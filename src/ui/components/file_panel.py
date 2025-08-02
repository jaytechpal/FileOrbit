"""
File Panel - Core dual-pane component
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import sys

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QListWidget,
    QListWidgetItem, QLabel, QLineEdit, QPushButton, QSplitter,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QMenu, QMessageBox, QStyle,
    QFileIconProvider
)
from PySide6.QtCore import Qt, Signal, QTimer, QMimeData, QUrl, QFileInfo
from PySide6.QtGui import QIcon, QPixmap, QDrag, QAction

from src.utils.logger import get_logger


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
        
        # Create first tab
        self._create_new_tab()
        
        layout.addWidget(self.tab_widget)
    
    def _create_new_tab(self, path: Optional[Path] = None):
        """Create new tab"""
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
        
        # Address bar
        self.address_bar = ActivatableLineEdit()
        self.address_bar.setText(str(path or self.current_path))
        self.address_bar.returnPressed.connect(self._navigate_to_address)
        self.address_bar.clicked_for_activation.connect(self._on_child_widget_clicked)
        
        address_layout.addWidget(back_btn)
        address_layout.addWidget(forward_btn)
        address_layout.addWidget(up_btn)
        address_layout.addWidget(self.address_bar)
        
        tab_layout.addLayout(address_layout)
        
        # File list
        self.file_list_widget = FileListWidget()
        self.file_list_widget.files_dropped.connect(self._handle_files_dropped)
        self.file_list_widget.context_menu_requested.connect(self._show_file_context_menu)
        self.file_list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.file_list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.file_list_widget.clicked_for_activation.connect(self._on_child_widget_clicked)
        
        tab_layout.addWidget(self.file_list_widget)
        
        # Add tab
        tab_name = path.name if path else self.current_path.name or "Root"
        self.tab_widget.addTab(tab_widget, tab_name)
        self.tab_widget.setCurrentWidget(tab_widget)
        
        return tab_widget
    
    def _connect_signals(self):
        """Connect internal signals"""
        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        
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
        """Show context menu for files"""
        if not selected_items:
            return
        
        menu = QMenu(self)
        
        # Common actions
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_selection)
        menu.addAction(copy_action)
        
        cut_action = QAction("Cut", self)
        cut_action.triggered.connect(self.cut_selection)
        menu.addAction(cut_action)
        
        menu.addSeparator()
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_selection)
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        properties_action = QAction("Properties", self)
        properties_action.triggered.connect(self._show_properties)
        menu.addAction(properties_action)
        
        menu.exec(self.file_list_widget.mapToGlobal(position))
    
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
                self.current_path = path
                self.address_bar.setText(str(path))
                self._refresh_file_list()
                self.path_changed.emit(str(path))
                
                # Update tab title
                current_tab = self.tab_widget.currentIndex()
                tab_name = path.name or "Root"
                self.tab_widget.setTabText(current_tab, tab_name)
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
        if self.selected_files and self.file_service:
            # In a real implementation, you'd copy to system clipboard
            self.status_message.emit(f"Copied {len(self.selected_files)} items")
    
    def cut_selection(self):
        """Cut selected files to clipboard"""
        if self.selected_files and self.file_service:
            # In a real implementation, you'd cut to system clipboard
            self.status_message.emit(f"Cut {len(self.selected_files)} items")
    
    def paste(self):
        """Paste files from clipboard"""
        if self.file_service:
            # In a real implementation, you'd paste from system clipboard
            self.status_message.emit("Paste operation")
    
    def delete_selection(self):
        """Delete selected files"""
        if not self.selected_files:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete {len(self.selected_files)} items?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes and self.file_service:
            self.file_service.delete_files(self.selected_files)
    
    def _show_properties(self):
        """Show properties dialog for selected files"""
        if self.selected_files:
            # In a real implementation, you'd show a properties dialog
            self.status_message.emit("Properties dialog")
    
    def _on_child_widget_clicked(self):
        """Handle child widget click to activate panel"""
        self.logger.info(f"Child widget in panel {self.panel_id} clicked - emitting panel_activated signal")
        self.panel_activated.emit(self.panel_id)
    
    def mousePressEvent(self, event):
        """Handle mouse press to activate panel"""
        self.logger.info(f"Panel {self.panel_id} clicked - emitting panel_activated signal")
        self.panel_activated.emit(self.panel_id)
        super().mousePressEvent(event)
