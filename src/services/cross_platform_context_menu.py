"""
Cross-platform context menu handler

Provides unified context menu functionality that automatically uses the appropriate
platform-specific implementation while maintaining native look and behavior.
"""

import platform
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable

from PySide6.QtWidgets import QMenu, QAction, QWidget
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon

from src.utils.logger import get_logger
from src.services.icon_manager import IconManager
from src.core.shell_integration_interfaces import IShellIntegrationProvider

# Platform-specific imports
try:
    if platform.system() == 'Windows':
        from src.utils.windows_shell import WindowsShellIntegration
    elif platform.system() == 'Darwin':
        from src.services.macos_shell_integration import MacOSShellIntegration
    elif platform.system() == 'Linux':
        from src.services.linux_shell_integration import LinuxShellIntegration
except ImportError as e:
    # Handle missing platform-specific modules gracefully
    platform_system = platform.system()
    print(f"Warning: Could not import shell integration for {platform_system}: {e}")
    # We'll create a fallback implementation if needed


class CrossPlatformContextMenuHandler(QObject):
    """
    Cross-platform context menu handler that provides native behavior on each platform.
    
    Features:
    - Native OS integration on Windows, macOS, and Linux
    - Consistent API across platforms
    - Custom "Open in new tab" action for directories
    - Platform-specific icons and shortcuts
    """
    
    # Signals
    action_triggered = Signal(str, list)  # action_name, file_paths
    
    def __init__(self, icon_manager: IconManager):
        super().__init__()
        self.logger = get_logger(__name__)
        self.icon_manager = icon_manager
        
        # Initialize platform-specific shell integration
        self.shell_integration = self._create_shell_integration()
        
        # Storage for context menu data
        self._context_menu_files: List[Path] = []
        self._action_handlers: Dict[str, Callable] = {}
        
        self.logger.info(f"CrossPlatformContextMenuHandler initialized for {platform.system()}")
    
    def _create_shell_integration(self) -> IShellIntegrationProvider:
        """Create the appropriate shell integration for the current platform."""
        system = platform.system()
        
        try:
            if system == 'Windows':
                return WindowsShellIntegration()
            elif system == 'Darwin':
                return MacOSShellIntegration()
            elif system == 'Linux':
                return LinuxShellIntegration()
            else:
                raise RuntimeError(f"Unsupported platform: {system}")
        except (ImportError, NameError) as e:
            self.logger.warning(f"Failed to create platform-specific shell integration: {e}")
            # Return a fallback implementation
            return self._create_fallback_shell_integration()
    
    def _create_fallback_shell_integration(self) -> IShellIntegrationProvider:
        """Create a basic fallback shell integration."""
        from src.services.fallback_shell_integration import FallbackShellIntegration
        return FallbackShellIntegration()
    
    def register_action_handler(self, action_name: str, handler: Callable):
        """
        Register a handler for a specific action.
        
        Args:
            action_name: Name of the action
            handler: Callable to handle the action
        """
        self._action_handlers[action_name] = handler
        self.logger.debug(f"Registered handler for action: {action_name}")
    
    def show_file_context_menu(self, parent: QWidget, position, selected_files: List[Path]) -> bool:
        """
        Show context menu for selected files using native platform behavior.
        
        Args:
            parent: Parent widget for the menu
            position: Position to show the menu
            selected_files: List of selected file paths
            
        Returns:
            True if menu was shown, False otherwise
        """
        if not selected_files:
            return self.show_empty_area_context_menu(parent, position)
        
        try:
            # Store selected files for action handling
            self._context_menu_files = selected_files
            
            # Get platform-native actions
            actions = self.shell_integration.get_context_menu_actions(selected_files)
            
            # Add our custom "Open in new tab" for directories if not already present
            actions = self._enhance_actions_with_custom_options(actions, selected_files)
            
            # Create and show menu
            menu = self._create_context_menu(actions, parent)
            if menu:
                menu.exec(position)
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to show file context menu: {e}")
        
        return False
    
    def show_empty_area_context_menu(self, parent: QWidget, position, current_path: Optional[Path] = None) -> bool:
        """
        Show context menu for empty area using native platform behavior.
        
        Args:
            parent: Parent widget for the menu
            position: Position to show the menu
            current_path: Current directory path
            
        Returns:
            True if menu was shown, False otherwise
        """
        try:
            # Clear file selection
            self._context_menu_files = []
            
            # Get platform-native empty area actions
            actions = self.shell_integration.get_empty_area_context_menu(current_path)
            
            # Create and show menu
            menu = self._create_context_menu(actions, parent, current_path=current_path)
            if menu:
                menu.exec(position)
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to show empty area context menu: {e}")
        
        return False
    
    def _enhance_actions_with_custom_options(self, actions: List[Dict[str, Any]], selected_files: List[Path]) -> List[Dict[str, Any]]:
        """
        Enhance platform actions with our custom options.
        
        Args:
            actions: Platform-native actions
            selected_files: Selected file paths
            
        Returns:
            Enhanced action list
        """
        if not actions or not selected_files:
            return actions
        
        # Check if we need to add "Open in new tab" for directories
        has_single_directory = len(selected_files) == 1 and selected_files[0].is_dir()
        
        if has_single_directory:
            # Check if "Open in new tab" already exists
            has_open_in_new_tab = any(
                action.get('action') == 'open_in_new_tab' 
                for action in actions
            )
            
            if not has_open_in_new_tab:
                # Find the "Open" action and add "Open in new tab" after it
                for i, action in enumerate(actions):
                    if action.get('action') == 'open' and action.get('bold'):
                        # Insert "Open in new tab" after the main "Open" action
                        new_action = {
                            "text": "Open in New Tab",
                            "action": "open_in_new_tab",
                            "icon": "tab_new"
                        }
                        actions.insert(i + 1, new_action)
                        break
        
        return actions
    
    def _create_context_menu(self, actions: List[Dict[str, Any]], parent: QWidget, **kwargs) -> Optional[QMenu]:
        """
        Create context menu from action definitions.
        
        Args:
            actions: List of action definitions
            parent: Parent widget for the menu
            **kwargs: Additional context (current_path, etc.)
            
        Returns:
            QMenu instance or None if creation failed
        """
        if not actions:
            return None
        
        try:
            menu = QMenu(parent)
            
            for action_def in actions:
                self._add_menu_item(menu, action_def, parent, **kwargs)
            
            return menu
            
        except Exception as e:
            self.logger.error(f"Failed to create context menu: {e}")
            return None
    
    def _add_menu_item(self, menu: QMenu, action_def: Dict[str, Any], parent: QWidget, **kwargs):
        """
        Add a single menu item to the menu.
        
        Args:
            menu: Menu to add item to
            action_def: Action definition
            parent: Parent widget
            **kwargs: Additional context
        """
        try:
            if action_def.get("separator"):
                menu.addSeparator()
                return
            
            if action_def.get("submenu"):
                self._add_submenu(menu, action_def, parent, **kwargs)
                return
            
            # Regular menu item
            action = self._create_menu_action(action_def, parent, **kwargs)
            if action:
                menu.addAction(action)
                
        except Exception as e:
            self.logger.warning(f"Failed to add menu item: {e}")
    
    def _add_submenu(self, menu: QMenu, action_def: Dict[str, Any], parent: QWidget, **kwargs):
        """
        Add a submenu to the menu.
        
        Args:
            menu: Parent menu
            action_def: Submenu definition
            parent: Parent widget
            **kwargs: Additional context
        """
        try:
            submenu = QMenu(action_def["text"], parent)
            
            # Set submenu icon
            if action_def.get("icon"):
                icon = self._get_menu_icon(action_def["icon"])
                if icon and not icon.isNull():
                    submenu.setIcon(icon)
            
            # Add submenu items
            for sub_action in action_def["submenu"]:
                self._add_submenu_item(submenu, sub_action, parent, **kwargs)
            
            menu.addMenu(submenu)
            
        except Exception as e:
            self.logger.warning(f"Failed to add submenu: {e}")
    
    def _add_submenu_item(self, submenu: QMenu, sub_action: Dict[str, Any], parent: QWidget, **kwargs):
        """
        Add an item to a submenu.
        
        Args:
            submenu: Submenu to add item to
            sub_action: Submenu item definition
            parent: Parent widget
            **kwargs: Additional context
        """
        try:
            if sub_action.get("separator"):
                submenu.addSeparator()
                return
            
            # Handle different submenu item formats
            text = sub_action.get("text") or sub_action.get("name", "Unknown")
            action_name = sub_action.get("action", "unknown_action")
            
            if "path" in sub_action and action_name == "unknown_action":
                action_name = f"open_with_{sub_action['path']}"
            
            # Create action
            sub_item = QAction(text, parent)
            
            # Set icon
            icon = self._get_submenu_item_icon(sub_action)
            if icon and not icon.isNull():
                sub_item.setIcon(icon)
            
            # Set checkable if needed
            if sub_action.get("checkable"):
                sub_item.setCheckable(True)
            
            # Connect action
            sub_item.triggered.connect(
                lambda checked, action=action_name, kwargs=kwargs: self._handle_context_action(action, **kwargs)
            )
            
            submenu.addAction(sub_item)
            
        except Exception as e:
            self.logger.warning(f"Failed to add submenu item: {e}")
    
    def _create_menu_action(self, action_def: Dict[str, Any], parent: QWidget, **kwargs) -> Optional[QAction]:
        """
        Create a menu action from definition.
        
        Args:
            action_def: Action definition
            parent: Parent widget
            **kwargs: Additional context
            
        Returns:
            QAction instance or None
        """
        try:
            action = QAction(action_def["text"], parent)
            
            # Set icon
            icon = self._get_menu_icon(action_def.get("icon"), action_def["text"])
            if icon and not icon.isNull():
                action.setIcon(icon)
            
            # Set shortcut (platform-aware)
            if action_def.get("shortcut"):
                shortcut = self._adapt_shortcut_for_platform(action_def["shortcut"])
                action.setShortcut(shortcut)
            
            # Set bold for default action
            if action_def.get("bold"):
                font = action.font()
                font.setBold(True)
                action.setFont(font)
            
            # Connect action
            action_name = action_def["action"]
            action.triggered.connect(
                lambda checked, act=action_name, kwargs=kwargs: self._handle_context_action(act, **kwargs)
            )
            
            return action
            
        except Exception as e:
            self.logger.warning(f"Failed to create menu action: {e}")
            return None
    
    def _get_menu_icon(self, icon_name: Optional[str], text: str = "") -> QIcon:
        """
        Get icon for menu item with intelligent fallback.
        
        Args:
            icon_name: Provided icon name
            text: Menu text for intelligent icon detection
            
        Returns:
            QIcon for the menu item
        """
        # Use provided icon or guess from text
        if icon_name and icon_name != "app_extension":
            return self.icon_manager.get_context_menu_icon(icon_name)
        else:
            # Intelligently guess icon from text
            guessed_icon = self._get_icon_from_text(text)
            return self.icon_manager.get_context_menu_icon(guessed_icon)
    
    def _get_submenu_item_icon(self, sub_action: Dict[str, Any]) -> QIcon:
        """
        Get icon for submenu item.
        
        Args:
            sub_action: Submenu action definition
            
        Returns:
            QIcon for the submenu item
        """
        if sub_action.get("icon") and sub_action["icon"] != "app_extension":
            return self.icon_manager.get_context_menu_icon(sub_action["icon"])
        else:
            # Guess from text
            text = sub_action.get("text") or sub_action.get("name", "")
            guessed_icon = self._get_icon_from_text(text)
            return self.icon_manager.get_context_menu_icon(guessed_icon)
    
    def _get_icon_from_text(self, text: str) -> str:
        """
        Intelligently guess icon name from menu text.
        
        Args:
            text: Menu text to analyze
            
        Returns:
            Guessed icon name
        """
        if not text:
            return "app_extension"
        
        text_lower = text.lower()
        
        # Platform-aware icon mapping
        icon_mapping = {
            # Actions
            "cut": "cut",
            "copy": "copy",
            "paste": "paste",
            "delete": "delete",
            "rename": "rename",
            "open": "file_open",
            "open with": "open_with",
            "send to": "send_to",
            "share": "share",
            "compress": "archive",
            "extract": "extract",
            "new folder": "folder_new",
            "create folder": "folder_new",
            "new": "new",
            "folder": "folder",
            "refresh": "refresh",
            "search": "search",
            "find": "find",
            "sort": "sort",
            "view": "view",
            
            # Platform-specific
            "properties": "properties",
            "get info": "info",
            "quick look": "quicklook",
            "duplicate": "duplicate",
            "make alias": "alias",
            "make link": "link",
            "move to trash": "trash",
            "open in terminal": "terminal",
            "open terminal": "terminal",
            
            # Applications
            "text editor": "editor",
            "image viewer": "image_viewer",
            "video player": "media",
            "music": "media",
            "mail": "mail",
            "email": "mail",
            "messages": "messages",
            "airdrop": "airdrop",
        }
        
        # Check for direct matches
        for key, icon in icon_mapping.items():
            if key in text_lower:
                return icon
        
        # Check for specific patterns
        if "edit" in text_lower:
            return "editor"
        elif "play" in text_lower or "media" in text_lower:
            return "media"
        elif "view" in text_lower:
            return "view"
        elif "terminal" in text_lower or "shell" in text_lower or "command" in text_lower:
            return "terminal"
        elif "browser" in text_lower or "web" in text_lower:
            return "browser"
        
        return "app_extension"
    
    def _adapt_shortcut_for_platform(self, shortcut: str) -> str:
        """
        Adapt keyboard shortcuts for the current platform.
        
        Args:
            shortcut: Original shortcut string
            
        Returns:
            Platform-adapted shortcut string
        """
        system = platform.system()
        
        if system == 'Darwin':  # macOS
            # Convert Ctrl to Cmd on macOS
            shortcut = shortcut.replace('Ctrl+', 'Cmd+')
            shortcut = shortcut.replace('Alt+', 'Opt+')
        elif system == 'Linux':
            # Linux typically uses Ctrl, no changes needed
            pass
        # Windows uses Ctrl by default
        
        return shortcut
    
    def _handle_context_action(self, action_name: str, **kwargs):
        """
        Handle context menu action using platform-specific or custom handlers.
        
        Args:
            action_name: Name of the triggered action
            **kwargs: Additional context (current_path, etc.)
        """
        try:
            self.logger.debug(f"Handling context action: {action_name}")
            
            # Check for registered custom handlers first
            if action_name in self._action_handlers:
                handler = self._action_handlers[action_name]
                handler(self._context_menu_files)
                return
            
            # Handle our custom actions
            if action_name == "open_in_new_tab":
                # Emit signal for the main application to handle
                self.action_triggered.emit(action_name, [str(f) for f in self._context_menu_files])
                return
            
            # Try platform-specific handler
            success = self.shell_integration.execute_action(
                action_name, 
                self._context_menu_files, 
                **kwargs
            )
            
            if success:
                # Emit signal for any additional handling needed
                self.action_triggered.emit(action_name, [str(f) for f in self._context_menu_files])
            else:
                self.logger.warning(f"Failed to execute platform action: {action_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to handle context action {action_name}: {e}")
    
    def get_context_files(self) -> List[Path]:
        """
        Get currently selected context menu files.
        
        Returns:
            List of file paths
        """
        return self._context_menu_files.copy()
    
    def clear_context(self):
        """Clear context menu state."""
        self._context_menu_files.clear()
        self.logger.debug("Context menu state cleared")
    
    def supports_trash(self) -> bool:
        """
        Check if the current platform supports trash/recycle bin.
        
        Returns:
            True if trash is supported
        """
        return self.shell_integration.supports_trash()
    
    def move_to_trash(self, file_paths: List[Path]) -> bool:
        """
        Move files to trash using platform-specific method.
        
        Args:
            file_paths: List of file paths to move to trash
            
        Returns:
            True if operation was successful
        """
        return self.shell_integration.move_to_trash(file_paths)
    
    def show_file_properties(self, file_path: Path, parent: QWidget) -> bool:
        """
        Show platform-native file properties dialog.
        
        Args:
            file_path: File path to show properties for
            parent: Parent widget
            
        Returns:
            True if dialog was shown
        """
        return self.shell_integration.get_file_properties_dialog(file_path, parent)