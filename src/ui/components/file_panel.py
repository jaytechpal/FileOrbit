"""
File Panel - Core dual-pane component
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import sys
import subprocess

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QListWidget,
    QListWidgetItem, QLineEdit, QPushButton,
    QMenu, QMessageBox, QStyle,
    QFileIconProvider
)
from PySide6.QtCore import Qt, Signal, QTimer, QFileInfo
from PySide6.QtGui import QIcon, QAction

from src.utils.logger import get_logger
from src.utils.windows_shell import WindowsShellIntegration


class ActivatableTabWidget(QTabWidget):
    """Tab widget that emits activation signal when clicked"""
    clicked_for_activation = Signal()
    
    def mousePressEvent(self, event):
        self.clicked_for_activation.emit()
        super().mousePressEvent(event)


class ActivatableLineEdit(QLineEdit):
    """Line edit that emits activation signal when clicked or focused"""
    clicked_for_activation = Signal()
    
    def mousePressEvent(self, event):
        self.clicked_for_activation.emit()
        super().mousePressEvent(event)
        
    def focusInEvent(self, event):
        self.clicked_for_activation.emit()
        super().focusInEvent(event)


class ActivatablePushButton(QPushButton):
    """Push button that emits activation signal when clicked"""
    clicked_for_activation = Signal()
    
    def mousePressEvent(self, event):
        self.clicked_for_activation.emit()
        super().mousePressEvent(event)


class FileListWidget(QListWidget):
    """Custom list widget for file display"""
    
    files_dropped = Signal(list)  # List of file paths
    context_menu_requested = Signal(object, object)  # position, selected_items
    clicked_for_activation = Signal()  # Emitted when widget is clicked for panel activation
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QListWidget.ExtendedSelection)
        self.setAlternatingRowColors(True)
        
        # Connect context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    def mousePressEvent(self, event):
        """Handle mouse press to activate parent panel"""
        self.clicked_for_activation.emit()
        super().mousePressEvent(event)
    
    def dragEnterEvent(self, event):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)
    
    def dropEvent(self, event):
        """Handle drop event"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_paths = [url.toLocalFile() for url in urls]
            self.files_dropped.emit(file_paths)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)
    
    def _show_context_menu(self, position):
        """Show context menu"""
        selected_items = self.selectedItems()
        self.context_menu_requested.emit(position, selected_items)


class FilePanel(QWidget):
    """File panel with tabs and file list"""
    
    # Class variables for clipboard simulation
    _clipboard_files = []
    _clipboard_operation = None
    
    # Signals
    path_changed = Signal(str)
    selection_changed = Signal(dict)
    status_message = Signal(str)
    file_activated = Signal(str)
    panel_activated = Signal(str)  # Emitted when this panel becomes active
    
    def __init__(self, panel_id: str, file_service=None, config=None):
        super().__init__()
        self.panel_id = panel_id
        self.file_service = file_service
        self.config = config
        self.logger = get_logger(__name__)
        
        # Windows shell integration
        self.shell_integration = WindowsShellIntegration()
        
        # Current state
        self.current_path = Path.home()
        self.file_list = []
        self.selected_files = []
        
        # UI components
        self.tab_widget = None
        self.address_bar = None
        self.file_list_widget = None
        self.path_buttons = []
        
        # Icon provider for native file icons
        self.icon_provider = QFileIconProvider()
        
        # Detect platform for platform-specific icon handling
        self.platform = sys.platform
        self.logger.info(f"Platform detected: {self.platform} - Using platform-appropriate icons")
        
        self._setup_ui()
        self._connect_signals()
        self._refresh_file_list()
    
    def _setup_ui(self):
        """Setup panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Tab widget for multiple tabs
        self.tab_widget = ActivatableTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.clicked_for_activation.connect(self._on_child_widget_clicked)
        # Also connect to tab bar clicks directly
        self.tab_widget.tabBarClicked.connect(lambda index: self._on_child_widget_clicked())
        
        # Set initial styling
        self._update_active_state(False)
        
        # Create first tab
        self._create_new_tab()
        
        # Initialize navigation for first tab if needed
        first_tab = self.tab_widget.widget(0)
        if first_tab and not hasattr(first_tab, 'navigation_history'):
            first_tab.navigation_history = [self.current_path]
            first_tab.history_index = 0
            self._update_navigation_buttons(first_tab)
        
        layout.addWidget(self.tab_widget)
    
    def _create_new_tab(self, path: Optional[Path] = None):
        """Create new tab"""
        target_path = path or self.current_path
        
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(2, 2, 2, 2)
        tab_layout.setSpacing(2)
        
        # Address bar layout
        address_layout = QHBoxLayout()
        address_layout.setSpacing(2)
        
        # Get style for standard icons
        style = self.style()
        
        # Back/Forward buttons with Qt standard icons
        back_btn = ActivatablePushButton()
        back_btn.setIcon(style.standardIcon(QStyle.SP_ArrowLeft))
        back_btn.setMaximumWidth(30)
        back_btn.setToolTip("Back")
        back_btn.clicked_for_activation.connect(self._on_child_widget_clicked)
        
        forward_btn = ActivatablePushButton()
        forward_btn.setIcon(style.standardIcon(QStyle.SP_ArrowRight))
        forward_btn.setMaximumWidth(30)
        forward_btn.setToolTip("Forward")
        forward_btn.clicked_for_activation.connect(self._on_child_widget_clicked)
        
        up_btn = ActivatablePushButton()
        up_btn.setIcon(style.standardIcon(QStyle.SP_ArrowUp))
        up_btn.setMaximumWidth(30)
        up_btn.setToolTip("Up")
        up_btn.clicked.connect(self._go_up)
        up_btn.clicked_for_activation.connect(self._on_child_widget_clicked)
        
        # Address bar - set to target path
        address_bar = ActivatableLineEdit()
        address_bar.setText(str(target_path))
        address_bar.returnPressed.connect(self._navigate_to_address)
        address_bar.clicked_for_activation.connect(self._on_child_widget_clicked)
        
        address_layout.addWidget(back_btn)
        address_layout.addWidget(forward_btn)
        address_layout.addWidget(up_btn)
        address_layout.addWidget(address_bar)
        
        tab_layout.addLayout(address_layout)
        
        # File list
        file_list_widget = FileListWidget()
        file_list_widget.files_dropped.connect(self._handle_files_dropped)
        file_list_widget.context_menu_requested.connect(self._show_file_context_menu)
        file_list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        file_list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        file_list_widget.clicked_for_activation.connect(self._on_child_widget_clicked)
        
        tab_layout.addWidget(file_list_widget)
        
        # Store references in the tab widget for later access
        tab_widget.address_bar = address_bar
        tab_widget.file_list_widget = file_list_widget
        tab_widget.up_btn = up_btn
        tab_widget.back_btn = back_btn
        tab_widget.forward_btn = forward_btn
        tab_widget.current_path = target_path
        
        # Initialize navigation history for this tab
        tab_widget.navigation_history = [target_path]
        tab_widget.history_index = 0
        
        # Connect back/forward buttons for this tab
        # Note: These buttons are new instances, so no need to disconnect
        back_btn.clicked.connect(lambda: self._go_back(tab_widget))
        forward_btn.clicked.connect(lambda: self._go_forward(tab_widget))
        
        # Update button states
        self._update_navigation_buttons(tab_widget)
        
        # Add tab
        tab_name = target_path.name if target_path.name else "Root"
        tab_index = self.tab_widget.addTab(tab_widget, tab_name)
        self.tab_widget.setCurrentIndex(tab_index)
        
        # Update current references to the new tab
        self.address_bar = address_bar
        self.file_list_widget = file_list_widget
        self.current_path = target_path
        
        # Load files for the new tab
        self._refresh_file_list()
        
        return tab_widget
    
    def _on_tab_changed(self, index):
        """Handle tab switching"""
        if index >= 0:
            current_tab = self.tab_widget.widget(index)
            if current_tab and hasattr(current_tab, 'address_bar'):
                # Update current references to the active tab
                self.address_bar = current_tab.address_bar
                self.file_list_widget = current_tab.file_list_widget
                self.current_path = current_tab.current_path
                
                # Update navigation button states for the new tab
                self._update_navigation_buttons(current_tab)
                
                # Emit path changed signal
                self.path_changed.emit(str(self.current_path))
    
    def _connect_signals(self):
        """Connect internal signals"""
        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        if self.file_service:
            self.file_service.directory_changed.connect(self._on_directory_changed)
    
    def _refresh_file_list(self):
        """Refresh file list for current path"""
        try:
            if not self.current_path.exists():
                self.status_message.emit("Path does not exist")
                return
            
            # Clear current list
            self.file_list_widget.clear()
            self.file_list = []
            
            # Add parent directory entry
            if self.current_path.parent != self.current_path:
                parent_item = QListWidgetItem("..")
                parent_item.setData(Qt.UserRole, str(self.current_path.parent))
                parent_item.setIcon(self._get_parent_directory_icon())
                self.file_list_widget.addItem(parent_item)
            
            # Get directory contents
            try:
                items = list(self.current_path.iterdir())
                # Sort: directories first, then files
                items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
                
                for item_path in items:
                    if self._should_show_file(item_path):
                        self._add_file_item(item_path)
                
                self.file_list = items
                self.status_message.emit(f"{len(items)} items")
                
            except PermissionError:
                self.status_message.emit("Permission denied")
            except OSError as e:
                self.status_message.emit(f"Error: {e}")
                
        except Exception as e:
            self.logger.error(f"Error refreshing file list: {e}")
            self.status_message.emit(f"Error: {e}")
    
    def _add_file_item(self, file_path: Path):
        """Add file item to list"""
        item = QListWidgetItem()
        item.setText(file_path.name)
        item.setData(Qt.UserRole, str(file_path))
        
        # Set icon
        if file_path.is_dir():
            item.setIcon(self._get_folder_icon())
        else:
            item.setIcon(self._get_file_icon(file_path))
        
        # Set tooltip with file info
        if self.file_service:
            file_info = self.file_service.get_file_info(file_path)
            if file_info:
                tooltip = self._create_file_tooltip(file_info)
                item.setToolTip(tooltip)
        
        self.file_list_widget.addItem(item)
    
    def _should_show_file(self, file_path: Path) -> bool:
        """Check if file should be shown"""
        # Check hidden files setting
        show_hidden = self.config.get('appearance', 'show_hidden_files', False) if self.config else False
        
        if not show_hidden and file_path.name.startswith('.'):
            return False
        
        return True
    
    def _get_folder_icon(self) -> QIcon:
        """Get platform-appropriate folder icon"""
        # QFileIconProvider works well across all platforms and respects system themes
        folder_info = QFileInfo()
        folder_info.setFile(".")  # Current directory
        folder_icon = self.icon_provider.icon(QFileIconProvider.Folder)
        
        # If QFileIconProvider doesn't work, fall back to Qt standard icons
        if folder_icon.isNull():
            return self.style().standardIcon(QStyle.SP_DirIcon)
        return folder_icon
    
    def _get_file_icon(self, file_path: Path) -> QIcon:
        """Get platform-appropriate file icon based on file type"""
        try:
            # Use QFileIconProvider which respects system file associations
            # This works on Windows (shell icons), macOS (Finder icons), and Linux (desktop environment icons)
            file_info = QFileInfo(str(file_path))
            icon = self.icon_provider.icon(file_info)
            
            # Enhanced fallback system based on file extension
            if icon.isNull():
                icon = self._get_fallback_icon(file_path)
            
            return icon
        except Exception as e:
            self.logger.warning(f"Error getting icon for {file_path}: {e}")
            # Final fallback to generic file icon
            return self.style().standardIcon(QStyle.SP_FileIcon)
    
    def _get_fallback_icon(self, file_path: Path) -> QIcon:
        """Get fallback icons for common file types across platforms"""
        extension = file_path.suffix.lower()
        
        # Common file type mappings that work well across platforms
        if extension in ['.txt', '.log', '.md', '.readme']:
            return self.style().standardIcon(QStyle.SP_FileIcon)
        elif extension in ['.pdf']:
            return self.style().standardIcon(QStyle.SP_FileIcon)
        elif extension in ['.exe', '.app', '.deb', '.rpm', '.dmg']:
            return self.style().standardIcon(QStyle.SP_ComputerIcon)
        elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']:
            return self.style().standardIcon(QStyle.SP_FileIcon)
        elif extension in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
            return self.style().standardIcon(QStyle.SP_MediaVolume)
        elif extension in ['.mp4', '.avi', '.mkv', '.mov', '.wmv']:
            return self.style().standardIcon(QStyle.SP_MediaPlay)
        elif extension in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']:
            return self.style().standardIcon(QStyle.SP_DirIcon)  # Archive as folder-like
        else:
            return self.style().standardIcon(QStyle.SP_FileIcon)
    
    def _get_parent_directory_icon(self) -> QIcon:
        """Get platform-appropriate parent directory icon"""
        # Try to get a native "up" or "parent" icon
        if self.platform == "darwin":  # macOS
            # macOS Finder uses a specific up arrow
            return self.style().standardIcon(QStyle.SP_ArrowUp)
        elif self.platform.startswith("linux"):  # Linux
            # Linux desktop environments often use a folder with arrow
            return self.style().standardIcon(QStyle.SP_FileDialogToParent)
        else:  # Windows and others
            return self.style().standardIcon(QStyle.SP_FileDialogToParent)
    
    def _create_file_tooltip(self, file_info: Dict[str, Any]) -> str:
        """Create tooltip text for file"""
        lines = [
            f"Name: {file_info.get('name', 'Unknown')}",
            f"Size: {self._format_file_size(file_info.get('size', 0))}",
            f"Modified: {file_info.get('modified', 'Unknown')}",
            f"Type: {'Directory' if file_info.get('is_directory') else 'File'}"
        ]
        return "\n".join(lines)
    
    def _format_file_size(self, size: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def _format_datetime(self, timestamp: float) -> str:
        """Format timestamp to readable date/time string"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    # Event handlers
    def _navigate_to_address(self):
        """Navigate to address bar path"""
        try:
            new_path = Path(self.address_bar.text())
            self.navigate_to(new_path)
        except Exception as e:
            self.status_message.emit(f"Invalid path: {e}")
    
    def _go_up(self):
        """Navigate to parent directory"""
        if self.current_path.parent != self.current_path:
            self.navigate_to(self.current_path.parent)
    
    def _go_back(self, tab_widget=None):
        """Navigate back in history"""
        if tab_widget is None:
            tab_widget = self.tab_widget.currentWidget()
        
        if tab_widget and hasattr(tab_widget, 'navigation_history'):
            if tab_widget.history_index > 0:
                tab_widget.history_index -= 1
                path = tab_widget.navigation_history[tab_widget.history_index]
                self._navigate_to_path_without_history(path, tab_widget)
                self._update_navigation_buttons(tab_widget)
    
    def _go_forward(self, tab_widget=None):
        """Navigate forward in history"""
        if tab_widget is None:
            tab_widget = self.tab_widget.currentWidget()
        
        if tab_widget and hasattr(tab_widget, 'navigation_history'):
            if tab_widget.history_index < len(tab_widget.navigation_history) - 1:
                tab_widget.history_index += 1
                path = tab_widget.navigation_history[tab_widget.history_index]
                self._navigate_to_path_without_history(path, tab_widget)
                self._update_navigation_buttons(tab_widget)
    
    def _update_navigation_buttons(self, tab_widget):
        """Update back/forward button states"""
        if not tab_widget or not hasattr(tab_widget, 'navigation_history'):
            return
        
        # Update back button
        can_go_back = tab_widget.history_index > 0
        tab_widget.back_btn.setEnabled(can_go_back)
        
        # Update forward button
        can_go_forward = tab_widget.history_index < len(tab_widget.navigation_history) - 1
        tab_widget.forward_btn.setEnabled(can_go_forward)
    
    def _navigate_to_path_without_history(self, path: Path, tab_widget):
        """Navigate to path without adding to history (used for back/forward)"""
        try:
            if path.exists() and path.is_dir():
                # Update current path and UI for the specific tab
                tab_widget.current_path = path
                tab_widget.address_bar.setText(str(path))
                
                # If this is the current tab, update global references
                if tab_widget == self.tab_widget.currentWidget():
                    self.current_path = path
                    self.address_bar = tab_widget.address_bar
                    self.file_list_widget = tab_widget.file_list_widget
                    self._refresh_file_list()
                    self.path_changed.emit(str(path))
                
                # Update tab title
                tab_index = self.tab_widget.indexOf(tab_widget)
                if tab_index >= 0:
                    tab_name = path.name or "Root"
                    self.tab_widget.setTabText(tab_index, tab_name)
                
                # Start watching directory
                if self.file_service and tab_widget == self.tab_widget.currentWidget():
                    self.file_service.start_watching_directory(str(path))
                    
        except Exception as e:
            self.logger.error(f"Error navigating to {path}: {e}")
    
    def _on_item_double_clicked(self, item):
        """Handle item double click"""
        file_path = Path(item.data(Qt.UserRole))
        
        if file_path.is_dir():
            self.navigate_to(file_path)
        else:
            self.file_activated.emit(str(file_path))
    
    def _on_selection_changed(self):
        """Handle selection change"""
        selected_items = self.file_list_widget.selectedItems()
        self.selected_files = [Path(item.data(Qt.UserRole)) for item in selected_items]
        
        # Emit selection info
        selection_info = {
            'count': len(self.selected_files),
            'total_size': sum(f.stat().st_size for f in self.selected_files if f.is_file()),
            'files': len([f for f in self.selected_files if f.is_file()]),
            'folders': len([f for f in self.selected_files if f.is_dir()])
        }
        self.selection_changed.emit(selection_info)
    
    def _handle_files_dropped(self, file_paths: List[str]):
        """Handle files dropped on panel"""
        if self.file_service:
            source_paths = [Path(p) for p in file_paths]
            self.file_service.copy_files(source_paths, self.current_path)
    
    def _show_file_context_menu(self, position, selected_items):
        """Show Windows Explorer-style context menu for files"""
        if not selected_items:
            # Show context menu for empty area
            self._show_empty_area_context_menu(position)
            return
        
        # Get selected file paths
        selected_paths = [Path(item.data(Qt.UserRole)) for item in selected_items]
        
        # Get Windows Explorer-style actions
        actions = self.shell_integration.get_context_menu_actions(selected_paths)
        
        # Create menu
        menu = self._create_context_menu(actions)
        
        # Store selected paths for action handling
        self._context_menu_files = selected_paths
        
        # Show context menu
        menu.exec(self.file_list_widget.mapToGlobal(position))
    
    def _show_empty_area_context_menu(self, position):
        """Show Windows Explorer-style context menu for empty area"""
        # Get empty area actions
        actions = self.shell_integration.get_empty_area_context_menu()
        
        # Create menu
        menu = self._create_context_menu(actions)
        
        # Show context menu
        menu.exec(self.file_list_widget.mapToGlobal(position))
    
    def _create_context_menu(self, actions: List[Dict[str, any]]) -> QMenu:
        """Create context menu from action definitions"""
        menu = QMenu(self)
        
        for i, action_def in enumerate(actions):
            if action_def.get("separator"):
                menu.addSeparator()
            elif action_def.get("submenu"):
                submenu = QMenu(action_def["text"], self)
                if action_def.get("icon"):
                    submenu.setIcon(self._get_context_menu_icon(action_def["icon"]))
                
                # Add submenu items
                for sub_action in action_def["submenu"]:
                    if sub_action.get("separator"):
                        submenu.addSeparator()
                    elif isinstance(sub_action, dict) and "text" in sub_action:
                        sub_item = QAction(sub_action["text"], self)
                        if sub_action.get("icon") and sub_action["icon"] != "app_extension":
                            sub_item.setIcon(self._get_context_menu_icon(sub_action["icon"]))
                        else:
                            # Intelligently guess icon from action text
                            guessed_icon = self._get_icon_from_text(sub_action["text"])
                            sub_item.setIcon(self._get_context_menu_icon(guessed_icon))
                        if sub_action.get("checkable"):
                            sub_item.setCheckable(True)
                        if sub_action.get("action"):
                            sub_item.triggered.connect(
                                lambda checked, action=sub_action["action"]: self._handle_context_action(action)
                            )
                        submenu.addAction(sub_item)
                    elif isinstance(sub_action, dict) and "name" in sub_action:
                        # Handle different submenu item format (like open with programs)
                        sub_item = QAction(sub_action["name"], self)
                        # Intelligently guess icon from name
                        guessed_icon = self._get_icon_from_text(sub_action["name"])
                        sub_item.setIcon(self._get_context_menu_icon(guessed_icon))
                        if "action" in sub_action:
                            action_name = sub_action["action"]
                        elif "path" in sub_action:
                            action_name = f"open_with_{sub_action['path']}"
                        else:
                            action_name = "unknown_action"
                        
                        sub_item.triggered.connect(
                            lambda checked, action=action_name: self._handle_context_action(action)
                        )
                        submenu.addAction(sub_item)
                
                menu.addMenu(submenu)
            else:
                action = QAction(action_def["text"], self)
                
                # Set icon - use provided icon or intelligently guess from text
                if action_def.get("icon") and action_def["icon"] != "app_extension":
                    # Use the provided specific icon
                    action.setIcon(self._get_context_menu_icon(action_def["icon"]))
                else:
                    # Either no icon or generic app_extension - use intelligent detection
                    guessed_icon = self._get_icon_from_text(action_def["text"])
                    action.setIcon(self._get_context_menu_icon(guessed_icon))
                
                # Set shortcut
                if action_def.get("shortcut"):
                    action.setShortcut(action_def["shortcut"])
                
                # Set bold for default action
                if action_def.get("bold"):
                    font = action.font()
                    font.setBold(True)
                    action.setFont(font)
                
                # Connect action
                action_name = action_def["action"]
                action.triggered.connect(
                    lambda checked, act=action_name: self._handle_context_action(act)
                )
                
                # Store command if available (for shell extensions)
                if action_def.get("command"):
                    if not hasattr(self, '_context_menu_commands'):
                        self._context_menu_commands = {}
                    self._context_menu_commands[action_name] = action_def["command"]
                
                menu.addAction(action)
        
        return menu
    
    def _get_context_menu_icon(self, icon_name: str) -> QIcon:
        """Get icon for context menu item"""
        if not icon_name:
            return QIcon()  # Return empty icon for None/empty strings
        
        self.logger.debug(f"Getting context menu icon for: {icon_name}")
        
        # Try to get actual application icons from the system first
        actual_icon = self._get_system_application_icon(icon_name)
        if actual_icon and not actual_icon.isNull():
            self.logger.debug(f"Successfully got system icon for {icon_name}")
            return actual_icon
        
        self.logger.debug(f"System icon failed for {icon_name}, using fallback")
        
        # Fallback to our enhanced icon mapping with distinctive icons
        icon_map = {
            # Standard file operations
            "folder_open": QStyle.SP_DirOpenIcon,
            "file_open": QStyle.SP_FileIcon,
            "tab_new": QStyle.SP_FileDialogNewFolder,
            "open_with": QStyle.SP_ComputerIcon,
            "send_to": QStyle.SP_DriveHDIcon,
            
            # Edit operations with more distinctive icons
            "cut": QStyle.SP_DialogDiscardButton,
            "copy": QStyle.SP_DialogSaveButton,
            "paste": QStyle.SP_DialogOkButton,
            "paste_shortcut": QStyle.SP_ArrowRight,
            "shortcut": QStyle.SP_ArrowRight,
            "delete": QStyle.SP_TrashIcon,  # Proper delete icon
            "rename": QStyle.SP_FileDialogDetailedView,
            
            # View and navigation
            "properties": QStyle.SP_ComputerIcon,
            "view": QStyle.SP_FileDialogListView,
            "sort": QStyle.SP_ArrowUp,
            "refresh": QStyle.SP_BrowserReload,
            "new": QStyle.SP_FileDialogNewFolder,
            
            # File types
            "folder": QStyle.SP_DirIcon,
            "text": QStyle.SP_FileIcon,
            "image": QStyle.SP_FileIcon,
            "rtf": QStyle.SP_FileIcon,
            
            # System and applications with more distinctive icons
            "display": QStyle.SP_ComputerIcon,
            "personalize": QStyle.SP_ComputerIcon,
            
            # Third-party applications - using more distinctive system icons
            "vlc": QStyle.SP_MediaPlay,  # VLC - media play icon (triangle)
            "mpc": QStyle.SP_MediaVolume,  # MPC-HC - volume/media icon
            "git": QStyle.SP_DriveNetIcon,  # Git - network drive icon
            "find": QStyle.SP_FileDialogDetailedView,  # Find - magnifying glass style
            "search": QStyle.SP_FileDialogDetailedView,  # Search icon
            "media": QStyle.SP_MediaPlay,  # Media players - play button
            "code": QStyle.SP_CommandLink,  # Code editors - distinctive link icon  
            "editor": QStyle.SP_DialogSaveButton,  # Text editors - save/document icon
            "terminal": QStyle.SP_MessageBoxCritical,  # Terminal - warning/system icon
            "cmd": QStyle.SP_MessageBoxInformation,  # Command prompt - info icon
            "powershell": QStyle.SP_DialogApplyButton,  # PowerShell - apply/action icon (more distinctive)
            
            # Generic third-party app fallback
            "app_extension": QStyle.SP_DialogApplyButton,  # More distinctive than computer icon
        }
        
        # Get the standard Qt icon as fallback
        standard_icon = icon_map.get(icon_name, QStyle.SP_FileIcon)
        icon = self.style().standardIcon(standard_icon)
        
        # Special handling for delete operations
        if icon_name == "delete":
            trash_icon = self.style().standardIcon(QStyle.SP_TrashIcon)
            if not trash_icon.isNull():
                return trash_icon
            return self.style().standardIcon(QStyle.SP_DialogDiscardButton)
        
        # Force icon to be visible by ensuring it has content
        if icon.isNull():
            icon = self.style().standardIcon(QStyle.SP_FileIcon)
        
        return icon

    def _get_system_application_icon(self, icon_name: str) -> QIcon:
        """Get actual application icon from Windows system"""
        import os
        
        try:
            self.logger.debug(f"Attempting to get system icon for: {icon_name}")
            
            # First try direct application lookup for common applications
            app_paths = self._get_common_app_paths()
            
            # Match icon name to application path with better matching
            for app_name, app_path in app_paths.items():
                if (icon_name.lower() == app_name.lower() or 
                    icon_name.lower() in app_name.lower() or 
                    app_name.lower() in icon_name.lower()):
                    
                    self.logger.debug(f"Found matching app: {app_name} -> {app_path}")
                    if os.path.exists(app_path):
                        icon = self._get_exe_icon(app_path)
                        if icon and not icon.isNull():
                            self.logger.debug(f"Successfully extracted {icon_name} icon from {app_path}")
                            return icon
                        else:
                            self.logger.debug(f"Failed to extract icon from {app_path}")
                    else:
                        self.logger.debug(f"App path does not exist: {app_path}")
            
            self.logger.debug(f"No direct app match found for {icon_name}")
            
            # Fallback to shell extension lookup
            if hasattr(self, 'selected_files') and self.selected_files:
                test_file = self.selected_files[0]
            else:
                # Create a temporary file for testing
                test_file = self.current_path / "test.txt"
                test_created = False
                if not test_file.exists():
                    test_file.touch()
                    test_created = True
                
                try:
                    # Get shell extensions for this file type
                    shell_extensions = self.shell_integration.get_shell_extensions_for_file(test_file)
                    
                    # Look for matching applications
                    for ext in shell_extensions:
                        command = ext.get("command", "")
                        text = ext.get("text", "").lower()
                        icon_path = ext.get("icon", "")
                        if self._text_matches_icon_name(text, icon_name):
                            # First try to use registry-provided icon path
                            if icon_path:
                                icon = self._get_icon_from_path(icon_path)
                                if icon and not icon.isNull():
                                    self.logger.debug(f"Successfully extracted {icon_name} icon from registry path {icon_path}")
                                    return icon
                            
                            # Fallback to executable icon extraction
                            exe_path = self._extract_exe_path_from_command(command)
                            self.logger.debug(f"Matched {icon_name} by text: exe_path='{exe_path}'")
                            if exe_path and os.path.exists(exe_path):
                                icon = self._get_exe_icon(exe_path)
                                if icon and not icon.isNull():
                                    self.logger.debug(f"Successfully extracted {icon_name} icon from {exe_path}")
                                    return icon
                        
                        # Also try direct command matching for common apps
                        if command:
                            if ("vlc" in command.lower() and icon_name == "vlc") or \
                               ("mpc-hc" in command.lower() and icon_name == "mpc") or \
                               ("mpc" in command.lower() and icon_name == "mpc") or \
                               ("git" in command.lower() and icon_name == "git") or \
                               ("code" in command.lower() and icon_name == "code") or \
                               ("sublime" in command.lower() and icon_name == "sublime"):
                                exe_path = self._extract_exe_path_from_command(command)
                                self.logger.debug(f"Matched {icon_name} by command: exe_path='{exe_path}'")
                                if exe_path and os.path.exists(exe_path):
                                    icon = self._get_exe_icon(exe_path)
                                    if icon and not icon.isNull():
                                        self.logger.debug(f"Successfully extracted {icon_name} icon from command {exe_path}")
                                        return icon
                finally:
                    if test_created and test_file.exists():
                        test_file.unlink()
            
            # Fallback: Try common application paths
            app_paths = self._get_common_app_paths(icon_name)
            for app_path in app_paths:
                if os.path.exists(app_path):
                    icon = self._get_exe_icon(app_path)
                    if icon and not icon.isNull():
                        return icon
                        
        except Exception as e:
            self.logger.debug(f"Error getting system icon for {icon_name}: {e}")
        
        return QIcon()  # Return empty icon if we can't get system icon

    def _text_matches_icon_name(self, text: str, icon_name: str) -> bool:
        """Check if text content matches our icon name"""
        if not text or not icon_name:
            return False
            
        text_lower = text.lower()
        
        # Direct matches
        if icon_name == "vlc" and ("vlc" in text_lower or "media player" in text_lower):
            return True
        elif icon_name == "git" and "git" in text_lower:
            return True
        elif icon_name == "code" and ("code" in text_lower or "visual studio" in text_lower):
            return True
        elif icon_name == "sublime" and "sublime" in text_lower:
            return True
        elif icon_name == "find" and ("find" in text_lower or "search" in text_lower):
            return True
        elif icon_name == "mpc" and ("mpc-hc" in text_lower or "mpc" in text_lower or "media player classic" in text_lower):
            return True
            
        return False

    def _get_icon_from_path(self, icon_path: str) -> QIcon:
        """Extract icon from registry icon path (e.g., 'path.exe,0')"""
        import os
        
        if not icon_path:
            return QIcon()
        
        try:
            # Handle format like "C:\path\file.exe,0"
            if ',' in icon_path:
                exe_path, icon_index = icon_path.split(',', 1)
                exe_path = exe_path.strip().strip('"')
                icon_index = int(icon_index.strip())
            else:
                exe_path = icon_path.strip().strip('"')
                icon_index = 0
            
            # Check if executable exists
            if os.path.exists(exe_path):
                # Try to extract icon using Windows API with icon index
                icon = self._get_exe_icon_with_index(exe_path, icon_index)
                if icon and not icon.isNull():
                    return icon
                
                # Fallback to regular exe icon extraction
                return self._get_exe_icon(exe_path)
                
        except Exception as e:
            self.logger.debug(f"Error extracting icon from path {icon_path}: {e}")
        
        return QIcon()

    def _get_exe_icon_with_index(self, exe_path: str, icon_index: int = 0) -> QIcon:
        """Extract specific icon from executable by index"""
        try:
            # Use Windows shell32 API to extract icon by index
            import ctypes
            from ctypes import wintypes
            
            # Load shell32.dll
            shell32 = ctypes.windll.shell32
            
            # Get icon handle
            SHGFI_ICON = 0x100
            SHGFI_LARGEICON = 0x0
            
            class SHFILEINFO(ctypes.Structure):
                _fields_ = [
                    ("hIcon", wintypes.HANDLE),
                    ("iIcon", ctypes.c_int),
                    ("dwAttributes", wintypes.DWORD),
                    ("szDisplayName", ctypes.c_wchar * 260),
                    ("szTypeName", ctypes.c_wchar * 80)
                ]
            
            shfileinfo = SHFILEINFO()
            
            # Get file icon
            ret = shell32.SHGetFileInfoW(
                exe_path,
                0,
                ctypes.byref(shfileinfo),
                ctypes.sizeof(shfileinfo),
                SHGFI_ICON | SHGFI_LARGEICON
            )
            
            if ret:
                # Convert to QIcon using Qt's fromWinHICON
                from PySide6.QtGui import QIcon
                icon = QIcon.fromWinHICON(shfileinfo.hIcon)
                
                # Clean up the icon handle
                ctypes.windll.user32.DestroyIcon(shfileinfo.hIcon)
                
                if not icon.isNull():
                    return icon
                    
        except Exception as e:
            self.logger.debug(f"Failed to extract icon with index from {exe_path}: {e}")
            
        return QIcon()

    def _get_exe_icon(self, exe_path: str) -> QIcon:
        """Extract icon from executable file using Windows API"""
        import os
        try:
            # Try using Qt's QFileIconProvider first
            from PySide6.QtWidgets import QFileIconProvider
            from PySide6.QtCore import QFileInfo
            
            if os.path.exists(exe_path):
                provider = QFileIconProvider()
                file_info = QFileInfo(exe_path)
                icon = provider.icon(file_info)
                if not icon.isNull():
                    return icon
                    
            # Fallback: Try to use Windows shell32 API through Python
            import ctypes
            from ctypes import wintypes
            
            # Load shell32.dll
            shell32 = ctypes.windll.shell32
            
            # Get icon handle
            SHGFI_ICON = 0x100
            SHGFI_LARGEICON = 0x0
            
            class SHFILEINFO(ctypes.Structure):
                _fields_ = [
                    ("hIcon", wintypes.HANDLE),
                    ("iIcon", ctypes.c_int),
                    ("dwAttributes", wintypes.DWORD),
                    ("szDisplayName", ctypes.c_wchar * 260),
                    ("szTypeName", ctypes.c_wchar * 80)
                ]
            
            shfileinfo = SHFILEINFO()
            
            # Get file icon
            ret = shell32.SHGetFileInfoW(
                exe_path,
                0,
                ctypes.byref(shfileinfo),
                ctypes.sizeof(shfileinfo),
                SHGFI_ICON | SHGFI_LARGEICON
            )
            
            if ret:
                # Convert to QIcon using Qt's fromWinHICON
                from PySide6.QtGui import QIcon
                icon = QIcon.fromWinHICON(shfileinfo.hIcon)
                
                # Clean up the icon handle
                ctypes.windll.user32.DestroyIcon(shfileinfo.hIcon)
                
                if not icon.isNull():
                    return icon
                    
        except Exception as e:
            self.logger.debug(f"Failed to extract icon from {exe_path}: {e}")
            
        return QIcon()

    def _extract_exe_path_from_command(self, command: str) -> str:
        """Extract executable path from shell command"""
        if not command:
            return ""
        
        # Remove quotes and extract the executable part
        command = command.strip()
        
        # Handle quoted paths
        if command.startswith('"'):
            # Find the closing quote
            end_quote = command.find('"', 1)
            if end_quote > 0:
                exe_path = command[1:end_quote]
                self.logger.debug(f"Extracted quoted path: {exe_path}")
                return exe_path
        else:
            # Take the first part before any space
            parts = command.split(' ')
            exe_path = parts[0] if parts else ""
            self.logger.debug(f"Extracted unquoted path: {exe_path}")
            return exe_path
        
        return ""

    def _command_matches_icon(self, command: str, icon_name: str) -> bool:
        """Check if a command matches the icon type we're looking for"""
        command_lower = command.lower()
        
        if icon_name == "vlc":
            return "vlc" in command_lower
        elif icon_name == "git":
            return "git" in command_lower
        elif icon_name == "code":
            return "code" in command_lower or "vscode" in command_lower
        elif icon_name == "editor":
            return "sublime" in command_lower or "notepad" in command_lower
        elif icon_name == "cmd":
            return "cmd" in command_lower
        elif icon_name == "powershell":
            return "powershell" in command_lower
        elif icon_name == "terminal":
            return "bash" in command_lower or "sh.exe" in command_lower
        
        return False

    def _get_common_app_paths(self, icon_name: str) -> list:
        """Get common installation paths for applications"""
        import os
        paths = []
        
        username = os.environ.get('USERNAME', '')
        
        if icon_name == "vlc":
            paths.extend([
                r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
            ])
        elif icon_name == "git":
            paths.extend([
                r"C:\Program Files\Git\cmd\git-gui.exe",
                r"C:\Program Files\Git\git-bash.exe"
            ])
        elif icon_name == "code":
            paths.extend([
                rf"C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
                r"C:\Program Files\Microsoft VS Code\Code.exe",
                r"C:\Program Files (x86)\Microsoft VS Code\Code.exe"
            ])
        elif icon_name == "editor":
            paths.extend([
                r"C:\Program Files\Sublime Text\sublime_text.exe",
                r"C:\Program Files (x86)\Sublime Text\sublime_text.exe"
            ])
        elif icon_name == "cmd":
            paths.append(r"C:\Windows\System32\cmd.exe")
        elif icon_name == "mpc":
            paths.extend([
                r"C:\Program Files\MPC-HC\mpc-hc64.exe",
                r"C:\Program Files (x86)\MPC-HC\mpc-hc.exe",
                r"C:\Program Files\K-Lite Codec Pack\MPC-HC64\mpc-hc64.exe",
                r"C:\Program Files (x86)\K-Lite Codec Pack\MPC-HC\mpc-hc.exe",
                r"C:\Program Files\MPC-HC\mpc-hc.exe",
                rf"C:\Users\{username}\AppData\Local\Programs\MPC-HC\mpc-hc.exe"
            ])
        elif icon_name == "powershell":
            paths.extend([
                r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
                r"C:\Program Files\PowerShell\7\pwsh.exe"
            ])
        
        return paths
    
    def _get_icon_from_text(self, text: str) -> str:
        """Get appropriate icon name based on action text"""
        if not text:
            return "app_extension"
        
        text_lower = text.lower()
        
        # VLC media player
        if "vlc" in text_lower or "media player" in text_lower:
            return "vlc"
        
        # MPC-HC media player
        if "mpc-hc" in text_lower or "mpc" in text_lower or "media player classic" in text_lower:
            return "mpc"
        
        # Git operations
        if "git" in text_lower:
            return "git"
        
        # Find/Search operations
        if "find" in text_lower or "search" in text_lower:
            return "find"
        
        # Delete operations
        if "delete" in text_lower or "remove" in text_lower:
            return "delete"
        
        # Code editors
        if "code" in text_lower or "visual studio" in text_lower:
            return "code"
        
        # Sublime Text specifically
        if "sublime" in text_lower:
            return "editor"
        
        # Command Prompt specifically  
        if "command prompt" in text_lower or "cmd" in text_lower:
            return "cmd"
        
        # PowerShell specifically
        if "powershell" in text_lower:
            return "powershell"
        
        # Text editors
        if "notepad" in text_lower or "editor" in text_lower:
            return "editor"
        
        # Terminal/Command line
        if "command" in text_lower or "powershell" in text_lower or "bash" in text_lower:
            return "terminal"
        
        # Media applications
        if "mpc-hc" in text_lower or "mpc hc" in text_lower:
            return "mpc"
        elif "play" in text_lower or "mpc" in text_lower:
            return "mpc"
        elif "vlc" in text_lower or "media player" in text_lower:
            return "vlc"
        
        # Default fallback
        return "app_extension"
    
    def _handle_context_action(self, action_name: str):
        """Handle context menu action"""
        try:
            # Get selected files if available
            files = getattr(self, '_context_menu_files', [])
            
            # File/folder actions
            if action_name == "open" or action_name == "open_default":
                if files and len(files) == 1:
                    file_path = files[0]
                    if file_path.is_dir():
                        self.navigate_to(file_path)
                    else:
                        self.shell_integration.open_with_system(file_path)
            
            elif action_name == "open_new_tab":
                if files and len(files) == 1:
                    file_path = files[0]
                    if file_path.is_dir():
                        self._create_new_tab(file_path)
                    else:
                        # For files, open the parent directory in new tab and select the file
                        parent_dir = file_path.parent
                        self._create_new_tab(parent_dir)
            
            elif action_name.startswith("open_with_"):
                program = action_name.replace("open_with_", "")
                if files and len(files) == 1:
                    self._open_with_program(files[0], program)
            
            elif action_name == "cut":
                self.cut_selection()
            
            elif action_name == "copy":
                self.copy_selection()
            
            elif action_name == "paste":
                self.paste()
            
            elif action_name == "delete":
                self.delete_selection()
            
            elif action_name == "rename":
                self._rename_selection()
            
            elif action_name == "properties":
                if files:
                    # Try Windows properties dialog first
                    if not self.shell_integration.open_properties_dialog(files[0]):
                        self._show_properties()
            
            elif action_name == "create_shortcut":
                if files and len(files) == 1:
                    self._create_shortcut(files[0])
            
            # Send to actions
            elif action_name.startswith("send_to_"):
                self._handle_send_to_action(action_name, files)
            
            # View actions
            elif action_name.startswith("view_"):
                self._handle_view_action(action_name)
            
            # Sort actions
            elif action_name.startswith("sort_"):
                self._handle_sort_action(action_name)
            
            # New actions
            elif action_name == "new_folder":
                self._create_new_folder()
            elif action_name == "new_text":
                self._create_new_file("New Text Document.txt")
            elif action_name == "new_bitmap":
                self._create_new_file("New Bitmap Image.bmp")
            elif action_name == "new_rtf":
                self._create_new_file("New Rich Text Document.rtf")
            
            # Refresh
            elif action_name == "refresh":
                self._refresh_file_list()
            
            # Command/PowerShell
            elif action_name == "open_cmd":
                self.shell_integration.open_command_prompt_here(self.current_path)
            elif action_name == "open_powershell":
                self.shell_integration.open_powershell_here(self.current_path)
            
            # System actions
            elif action_name == "display_settings":
                subprocess.run(["ms-settings:display"], shell=True)
            elif action_name == "personalize":
                subprocess.run(["ms-settings:personalization"], shell=True)
            
            # Handle shell extensions from third-party applications
            elif action_name.startswith("shell_extension_") or action_name.startswith("common_app_"):
                self._handle_shell_extension(action_name, files)
            
            else:
                self.status_message.emit(f"Action not implemented: {action_name}")
                
        except Exception as e:
            self.logger.error(f"Error handling context action {action_name}: {e}")
            self.status_message.emit(f"Error: {e}")
    
    def _open_with_program(self, file_path: Path, program: str):
        """Open file with specific program"""
        try:
            import subprocess
            subprocess.run([program, str(file_path)], check=False)
            self.status_message.emit(f"Opened {file_path.name} with {program}")
        except Exception as e:
            self.logger.error(f"Error opening with {program}: {e}")
            self.status_message.emit(f"Failed to open with {program}")
    
    def _create_shortcut(self, target_path: Path):
        """Create shortcut to file/folder"""
        try:
            shortcut_path = self.current_path / f"{target_path.name} - Shortcut.lnk"
            if self.shell_integration.create_shortcut(target_path, shortcut_path):
                self.status_message.emit(f"Created shortcut to {target_path.name}")
                self._refresh_file_list()
            else:
                self.status_message.emit("Failed to create shortcut")
        except Exception as e:
            self.logger.error(f"Error creating shortcut: {e}")
            self.status_message.emit("Failed to create shortcut")
    
    def _handle_send_to_action(self, action_name: str, files: List[Path]):
        """Handle Send To actions"""
        if not files:
            return
        
        if action_name == "send_to_desktop_shortcut":
            desktop = Path.home() / "Desktop"
            for file_path in files:
                shortcut_path = desktop / f"{file_path.name} - Shortcut.lnk"
                self.shell_integration.create_shortcut(file_path, shortcut_path)
            self.status_message.emit(f"Created shortcuts on desktop for {len(files)} items")
        
        elif action_name == "send_to_mail":
            # Open default mail client with files as attachments
            try:
                import subprocess
                file_args = [str(f) for f in files]
                subprocess.run(["mailto:", *file_args], shell=True)
            except Exception:
                self.status_message.emit("Mail client not available")
        
        elif action_name == "send_to_zip":
            self._create_zip_archive(files)
        
        else:
            self.status_message.emit(f"Send to action not implemented: {action_name}")
    
    def _create_zip_archive(self, files: List[Path]):
        """Create ZIP archive of selected files"""
        try:
            import zipfile
            from PySide6.QtWidgets import QInputDialog
            
            archive_name, ok = QInputDialog.getText(
                self, "Create Archive", "Archive name:", 
                text="Archive.zip"
            )
            
            if ok and archive_name:
                archive_path = self.current_path / archive_name
                if not archive_path.suffix:
                    archive_path = archive_path.with_suffix(".zip")
                
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for file_path in files:
                        if file_path.is_file():
                            zf.write(file_path, file_path.name)
                        elif file_path.is_dir():
                            for item in file_path.rglob('*'):
                                if item.is_file():
                                    zf.write(item, item.relative_to(file_path.parent))
                
                self.status_message.emit(f"Created archive: {archive_name}")
                self._refresh_file_list()
        except Exception as e:
            self.logger.error(f"Error creating ZIP archive: {e}")
            self.status_message.emit("Failed to create archive")
    
    def _handle_shell_extension(self, action_name: str, files: List[Path]):
        """Handle shell extension actions from third-party applications"""
        if not files:
            return
        
        try:
            # Get the file for the action
            file_path = files[0]  # Most shell extensions work on single files
            
            # Get the shell extensions for this file
            shell_extensions = self.shell_integration.get_shell_extensions_for_file(file_path)
            common_extensions = self.shell_integration.get_common_app_extensions()
            all_extensions = shell_extensions + common_extensions
            
            # Find the matching extension
            matching_extension = None
            for ext in all_extensions:
                if ext["action"] == action_name:
                    matching_extension = ext
                    break
            
            if matching_extension:
                # Execute the shell extension command
                success = self.shell_integration.execute_shell_extension(
                    file_path, matching_extension["command"]
                )
                
                if success:
                    self.status_message.emit(f"Executed: {matching_extension['name']}")
                else:
                    self.status_message.emit(f"Failed to execute: {matching_extension['name']}")
            else:
                self.status_message.emit(f"Shell extension not found: {action_name}")
                
        except Exception as e:
            self.logger.error(f"Error handling shell extension {action_name}: {e}")
            self.status_message.emit(f"Error: {e}")
    
    def _handle_view_action(self, action_name: str):
        """Handle view mode actions"""
        view_modes = {
            "view_extra_large": "Extra Large Icons",
            "view_large": "Large Icons", 
            "view_medium": "Medium Icons",
            "view_small": "Small Icons",
            "view_list": "List",
            "view_details": "Details",
            "view_tiles": "Tiles",
            "view_content": "Content"
        }
        
        mode = view_modes.get(action_name, "Unknown")
        self.status_message.emit(f"View mode: {mode}")
        # TODO: Implement actual view mode changes
    
    def _handle_sort_action(self, action_name: str):
        """Handle sort actions"""
        sort_options = {
            "sort_name": "Name",
            "sort_date": "Date Modified",
            "sort_type": "Type", 
            "sort_size": "Size",
            "sort_asc": "Ascending",
            "sort_desc": "Descending"
        }
        
        option = sort_options.get(action_name, "Unknown")
        self.status_message.emit(f"Sort by: {option}")
        # TODO: Implement actual sorting
    
    def _close_tab(self, index: int):
        """Close tab"""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
    
    def _on_directory_changed(self, path: str):
        """Handle directory change notification"""
        if Path(path) == self.current_path:
            QTimer.singleShot(100, self._refresh_file_list)  # Small delay to avoid rapid updates
    
    # Public interface
    def navigate_to(self, path: Path):
        """Navigate to specified path"""
        self.logger.info(f"Panel {self.panel_id} navigate_to called with path: {path}")
        try:
            if path.exists() and path.is_dir():
                self.logger.info(f"Panel {self.panel_id} navigating from {self.current_path} to {path}")
                
                # Update current tab's navigation history
                current_tab = self.tab_widget.currentWidget()
                if current_tab and hasattr(current_tab, 'navigation_history'):
                    # Remove any forward history if we're navigating to a new path
                    if current_tab.history_index < len(current_tab.navigation_history) - 1:
                        current_tab.navigation_history = current_tab.navigation_history[:current_tab.history_index + 1]
                    
                    # Add new path to history (avoid duplicates of same path)
                    if not current_tab.navigation_history or current_tab.navigation_history[-1] != path:
                        current_tab.navigation_history.append(path)
                        current_tab.history_index = len(current_tab.navigation_history) - 1
                    
                    # Update navigation buttons
                    self._update_navigation_buttons(current_tab)
                
                self.current_path = path
                self.address_bar.setText(str(path))
                
                # Update current tab's stored path
                if current_tab and hasattr(current_tab, 'current_path'):
                    current_tab.current_path = path
                
                self._refresh_file_list()
                self.path_changed.emit(str(path))
                
                # Update tab title
                current_tab_index = self.tab_widget.currentIndex()
                tab_name = path.name or "Root"
                self.tab_widget.setTabText(current_tab_index, tab_name)
                self.logger.info(f"Panel {self.panel_id} navigation completed successfully to {path}")
                
                # Start watching directory
                if self.file_service:
                    self.file_service.start_watching_directory(str(path))
                    
            else:
                self.status_message.emit("Invalid or inaccessible path")
                
        except Exception as e:
            self.logger.error(f"Error navigating to {path}: {e}")
            self.status_message.emit(f"Error: {e}")
    
    def new_tab(self, path: Optional[Path] = None):
        """Create new tab"""
        self._create_new_tab(path or self.current_path)
    
    def copy_selection(self):
        """Copy selected files to clipboard"""
        if not self.selected_files:
            return
            
        try:
            # Store file paths in a class variable for clipboard simulation
            # In a real implementation, you'd use system clipboard
            FilePanel._clipboard_files = [str(path) for path in self.selected_files]
            FilePanel._clipboard_operation = "copy"
            
            file_count = len(self.selected_files)
            self.status_message.emit(f"Copied {file_count} item{'s' if file_count != 1 else ''}")
        except Exception as e:
            self.logger.error(f"Error copying files: {e}")
            self.status_message.emit(f"Copy failed: {e}")
    
    def cut_selection(self):
        """Cut selected files to clipboard"""
        if not self.selected_files:
            return
            
        try:
            # Store file paths in a class variable for clipboard simulation
            FilePanel._clipboard_files = [str(path) for path in self.selected_files]
            FilePanel._clipboard_operation = "cut"
            
            file_count = len(self.selected_files)
            self.status_message.emit(f"Cut {file_count} item{'s' if file_count != 1 else ''}")
        except Exception as e:
            self.logger.error(f"Error cutting files: {e}")
            self.status_message.emit(f"Cut failed: {e}")
    
    def paste(self):
        """Paste files from clipboard"""
        if not hasattr(FilePanel, '_clipboard_files') or not FilePanel._clipboard_files:
            self.status_message.emit("Nothing to paste")
            return
            
        try:
            source_paths = [Path(path) for path in FilePanel._clipboard_files]
            operation = getattr(FilePanel, '_clipboard_operation', 'copy')
            
            if self.file_service:
                if operation == "copy":
                    self.file_service.copy_files(source_paths, self.current_path)
                    self.status_message.emit(f"Copying {len(source_paths)} items...")
                elif operation == "cut":
                    self.file_service.move_files(source_paths, self.current_path)
                    self.status_message.emit(f"Moving {len(source_paths)} items...")
                    # Clear clipboard after cut operation
                    FilePanel._clipboard_files = []
                    FilePanel._clipboard_operation = None
            else:
                self.status_message.emit("File service not available")
        except Exception as e:
            self.logger.error(f"Error pasting files: {e}")
            self.status_message.emit(f"Paste failed: {e}")
    
    def delete_selection(self):
        """Delete selected files"""
        if not self.selected_files:
            return
        
        file_count = len(self.selected_files)
        file_names = ", ".join([path.name for path in self.selected_files[:3]])
        if file_count > 3:
            file_names += f" and {file_count - 3} more"
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete:\n{file_names}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.file_service:
                    self.file_service.delete_files(self.selected_files)
                    self.status_message.emit(f"Deleting {file_count} items...")
                else:
                    # Fallback for when service is not available
                    for file_path in self.selected_files:
                        if file_path.is_file():
                            file_path.unlink()
                        elif file_path.is_dir():
                            import shutil
                            shutil.rmtree(file_path)
                    self.status_message.emit(f"Deleted {file_count} items")
                    self._refresh_file_list()
            except Exception as e:
                self.logger.error(f"Error deleting files: {e}")
                self.status_message.emit(f"Delete failed: {e}")
    
    def _clipboard_has_files(self) -> bool:
        """Check if clipboard has files"""
        return hasattr(FilePanel, '_clipboard_files') and bool(FilePanel._clipboard_files)
    
    def _open_with_system(self, file_path: Path):
        """Open file with system default application"""
        try:
            import subprocess
            import sys
            
            if sys.platform == "win32":
                import os
                os.startfile(str(file_path))
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", str(file_path)])
            else:  # Linux and others
                subprocess.run(["xdg-open", str(file_path)])
                
            self.status_message.emit(f"Opened {file_path.name}")
        except Exception as e:
            self.logger.error(f"Error opening file: {e}")
            self.status_message.emit(f"Failed to open {file_path.name}")
    
    def _rename_selection(self):
        """Rename selected file/folder"""
        if not self.selected_files or len(self.selected_files) != 1:
            return
            
        old_path = self.selected_files[0]
        
        from PySide6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(
            self,
            "Rename",
            "New name:",
            text=old_path.name
        )
        
        if ok and new_name and new_name != old_path.name:
            try:
                new_path = old_path.parent / new_name
                old_path.rename(new_path)
                self.status_message.emit(f"Renamed to {new_name}")
                self._refresh_file_list()
            except Exception as e:
                self.logger.error(f"Error renaming file: {e}")
                self.status_message.emit(f"Rename failed: {e}")
    
    def _calculate_checksum(self):
        """Calculate checksum for selected file"""
        if not self.selected_files or len(self.selected_files) != 1:
            return
            
        file_path = self.selected_files[0]
        if not file_path.is_file():
            return
            
        if self.file_service:
            try:
                checksum = self.file_service.calculate_checksum(file_path)
                if checksum:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self,
                        "File Checksum",
                        f"MD5: {checksum}\n\nFile: {file_path.name}"
                    )
                else:
                    self.status_message.emit("Failed to calculate checksum")
            except Exception as e:
                self.logger.error(f"Error calculating checksum: {e}")
                self.status_message.emit("Checksum calculation failed")
    
    def _calculate_folder_size(self):
        """Calculate total size of selected folder"""
        if not self.selected_files or len(self.selected_files) != 1:
            return
            
        folder_path = self.selected_files[0]
        if not folder_path.is_dir():
            return
            
        try:
            total_size = 0
            file_count = 0
            
            for item in folder_path.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
                    file_count += 1
            
            size_str = self._format_file_size(total_size)
            
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Folder Size",
                f"Folder: {folder_path.name}\n"
                f"Total Size: {size_str}\n"
                f"Files: {file_count}"
            )
        except Exception as e:
            self.logger.error(f"Error calculating folder size: {e}")
            self.status_message.emit("Folder size calculation failed")
    
    def _create_new_folder(self):
        """Create new folder in current directory"""
        from PySide6.QtWidgets import QInputDialog
        
        folder_name, ok = QInputDialog.getText(
            self,
            "New Folder",
            "Folder name:",
            text="New Folder"
        )
        
        if ok and folder_name:
            try:
                new_folder = self.current_path / folder_name
                new_folder.mkdir(exist_ok=True)
                self.status_message.emit(f"Created folder: {folder_name}")
                self._refresh_file_list()
            except Exception as e:
                self.logger.error(f"Error creating folder: {e}")
                self.status_message.emit(f"Failed to create folder: {e}")
    
    def _create_new_file(self, filename: str = None):
        """Create new file in current directory"""
        from PySide6.QtWidgets import QInputDialog
        
        if not filename:
            filename = "new_file.txt"
        
        file_name, ok = QInputDialog.getText(
            self,
            "New File",
            "File name:",
            text=filename
        )
        
        if ok and file_name:
            try:
                new_file = self.current_path / file_name
                new_file.touch()
                self.status_message.emit(f"Created file: {file_name}")
                self._refresh_file_list()
            except Exception as e:
                self.logger.error(f"Error creating file: {e}")
                self.status_message.emit(f"Failed to create file: {e}")
    
    def _toggle_hidden_files(self):
        """Toggle showing hidden files"""
        if self.config:
            current_setting = self.config.get('appearance', 'show_hidden_files', False)
            new_setting = not current_setting
            self.config.set('appearance', 'show_hidden_files', new_setting)
            self.status_message.emit(f"Hidden files: {'shown' if new_setting else 'hidden'}")
            self._refresh_file_list()
    
    def _show_properties(self):
        """Show properties dialog for selected files"""
        if not self.selected_files:
            return
            
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Properties")
        dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        if len(self.selected_files) == 1:
            # Single file/folder properties
            file_path = self.selected_files[0]
            
            try:
                stat = file_path.stat()
                
                info_text = f"""Name: {file_path.name}
Location: {file_path.parent}
Type: {'Directory' if file_path.is_dir() else 'File'}
Size: {self._format_file_size(stat.st_size)}
Created: {self._format_datetime(stat.st_ctime)}
Modified: {self._format_datetime(stat.st_mtime)}
Accessed: {self._format_datetime(stat.st_atime)}"""
                
                if file_path.is_file():
                    info_text += f"\nExtension: {file_path.suffix}"
                    
            except Exception as e:
                info_text = f"Error reading file properties: {e}"
        else:
            # Multiple files/folders properties
            total_size = 0
            file_count = 0
            folder_count = 0
            
            for file_path in self.selected_files:
                try:
                    if file_path.is_file():
                        file_count += 1
                        total_size += file_path.stat().st_size
                    elif file_path.is_dir():
                        folder_count += 1
                        # Calculate folder size
                        for item in file_path.rglob('*'):
                            if item.is_file():
                                total_size += item.stat().st_size
                except Exception:
                    pass
            
            info_text = f"""Selected Items: {len(self.selected_files)}
Files: {file_count}
Folders: {folder_count}
Total Size: {self._format_file_size(total_size)}"""
        
        text_edit = QTextEdit()
        text_edit.setPlainText(info_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def _on_child_widget_clicked(self):
        """Handle child widget click to activate panel"""
        self.logger.info(f"Child widget in panel {self.panel_id} clicked - emitting panel_activated signal")
        self.panel_activated.emit(self.panel_id)
    
    def _update_active_state(self, is_active: bool):
        """Update visual state to show if panel is active"""
        if is_active:
            # Active panel: Very subtle blue top border like VS Code
            self.tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #3c3c3c;
                    border-top: 2px solid #007ACC;
                    background-color: transparent;
                }
                QTabWidget::tab-bar {
                    alignment: left;
                }
                QTabBar::tab {
                    background-color: transparent;
                    padding: 8px 12px;
                    margin-right: 1px;
                    border: none;
                    font-weight: 500;
                    color: #CCCCCC;
                    min-width: 60px;
                }
                QTabBar::tab:selected {
                    background-color: transparent;
                    font-weight: 500;
                    color: #FFFFFF;
                    border: none;  /* Remove all borders first */
                    border-top: 1px solid #4A90E2;  /* Only top horizontal line */
                    border-radius: 3px 3px 0px 0px;  /* Rounded top corners only */
                }
                QTabBar::tab:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: #FFFFFF;
                }
            """)
            self.logger.info(f"Panel {self.panel_id} set to ACTIVE state (subtle blue top border)")
        else:
            # Inactive panel: No special border, readable text
            self.tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #3c3c3c;
                    border-top: 2px solid #3c3c3c;
                    background-color: transparent;
                }
                QTabWidget::tab-bar {
                    alignment: left;
                }
                QTabBar::tab {
                    background-color: transparent;
                    padding: 8px 12px;
                    margin-right: 1px;
                    border: none;
                    font-weight: normal;
                    color: #CCCCCC;
                    min-width: 60px;
                }
                QTabBar::tab:selected {
                    background-color: transparent;
                    font-weight: normal;
                    color: #CCCCCC;
                    border: none;  /* Remove all borders first */
                    border-top: 1px solid transparent;  /* Same border space as active, but transparent */
                    border-radius: 3px 3px 0px 0px;  /* Same border radius as active */
                }
                QTabBar::tab:hover {
                    background-color: rgba(255, 255, 255, 0.05);
                    color: #FFFFFF;
                }
            """)
            self.logger.info(f"Panel {self.panel_id} set to INACTIVE state (normal border, readable text)")
    
    def set_active(self, active: bool):
        """Set panel active state - called from main window"""
        self._update_active_state(active)
    
    def mousePressEvent(self, event):
        """Handle mouse press to activate panel"""
        self.logger.info(f"Panel {self.panel_id} clicked - emitting panel_activated signal")
        self.panel_activated.emit(self.panel_id)
        super().mousePressEvent(event)
    
    def _get_common_app_paths(self) -> Dict[str, str]:
        """Get paths to common applications for icon extraction"""
        import os
        
        app_paths = {}
        
        # VLC Media Player
        vlc_paths = [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
        ]
        for path in vlc_paths:
            if os.path.exists(path):
                app_paths["vlc"] = path
                break
        
        # Git GUI
        git_paths = [
            r"C:\Program Files\Git\cmd\git-gui.exe",
            r"C:\Program Files (x86)\Git\cmd\git-gui.exe",
        ]
        for path in git_paths:
            if os.path.exists(path):
                app_paths["git"] = path
                break
                
        # MPC-HC
        mpc_paths = [
            r"C:\Program Files\MPC-HC\mpc-hc64.exe",
            r"C:\Program Files (x86)\MPC-HC\mpc-hc.exe",
        ]
        for path in mpc_paths:
            if os.path.exists(path):
                app_paths["mpc"] = path
                app_paths["mpc-hc"] = path  # Also map to full name
                app_paths["media"] = path   # Also map to media for fallback
                break
        
        # Visual Studio Code
        code_paths = [
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
            r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe".format(os.environ.get('USERNAME', '')),
        ]
        for path in code_paths:
            if os.path.exists(path):
                app_paths["code"] = path
                break
        
        # Sublime Text
        sublime_paths = [
            r"C:\Program Files\Sublime Text\sublime_text.exe",
            r"C:\Program Files (x86)\Sublime Text\sublime_text.exe",
        ]
        for path in sublime_paths:
            if os.path.exists(path):
                app_paths["sublime"] = path
                app_paths["editor"] = path  # Also map to "editor"
                break
        
        # PowerShell
        powershell_paths = [
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            r"C:\Program Files\PowerShell\7\pwsh.exe",  # PowerShell 7
            r"C:\Program Files (x86)\PowerShell\7\pwsh.exe",
        ]
        for path in powershell_paths:
            if os.path.exists(path):
                app_paths["powershell"] = path
                break
        
        return app_paths
