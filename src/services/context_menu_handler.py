"""
ContextMenuHandler - Centralized context menu management service

This service handles all context menu creation, customization, and action handling
for the file manager. It integrates with shell extensions and provides consistent
menu behavior across the application.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Callable

from PySide6.QtWidgets import QMenu, QAction, QWidget
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon

from src.utils.logger import get_logger
from src.services.icon_manager import IconManager
from src.utils.windows_shell import WindowsShellIntegration


class ContextMenuHandler(QObject):
    """
    Centralized context menu management service.
    
    Handles:
    - File context menus
    - Empty area context menus 
    - Shell extension integration
    - Icon management for menu items
    - Action dispatching
    """
    
    # Signals
    action_triggered = Signal(str, list)  # action_name, file_paths
    
    def __init__(self, icon_manager: IconManager, shell_integration: WindowsShellIntegration):
        super().__init__()
        self.logger = get_logger(__name__)
        self.icon_manager = icon_manager
        self.shell_integration = shell_integration
        
        # Storage for context menu data
        self._context_menu_files: List[Path] = []
        self._context_menu_commands: Dict[str, str] = {}
        self._action_handlers: Dict[str, Callable] = {}
        
        self.logger.info("ContextMenuHandler initialized successfully")
    
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
        Show context menu for selected files.
        
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
            
            # Get Windows Explorer-style actions
            actions = self.shell_integration.get_context_menu_actions(selected_files)
            
            # Create and show menu
            menu = self._create_context_menu(actions, parent)
            if menu:
                menu.exec(position)
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to show file context menu: {e}")
        
        return False
    
    def show_empty_area_context_menu(self, parent: QWidget, position) -> bool:
        """
        Show context menu for empty area.
        
        Args:
            parent: Parent widget for the menu
            position: Position to show the menu
            
        Returns:
            True if menu was shown, False otherwise
        """
        try:
            # Clear file selection
            self._context_menu_files = []
            
            # Get empty area actions
            actions = self.shell_integration.get_empty_area_context_menu()
            
            # Create and show menu
            menu = self._create_context_menu(actions, parent)
            if menu:
                menu.exec(position)
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to show empty area context menu: {e}")
        
        return False
    
    def _create_context_menu(self, actions: List[Dict[str, Any]], parent: QWidget) -> Optional[QMenu]:
        """
        Create context menu from action definitions.
        
        Args:
            actions: List of action definitions
            parent: Parent widget for the menu
            
        Returns:
            QMenu instance or None if creation failed
        """
        if not actions:
            return None
        
        try:
            menu = QMenu(parent)
            
            for action_def in actions:
                self._add_menu_item(menu, action_def, parent)
            
            return menu
            
        except Exception as e:
            self.logger.error(f"Failed to create context menu: {e}")
            return None
    
    def _add_menu_item(self, menu: QMenu, action_def: Dict[str, Any], parent: QWidget):
        """
        Add a single menu item to the menu.
        
        Args:
            menu: Menu to add item to
            action_def: Action definition
            parent: Parent widget
        """
        try:
            if action_def.get("separator"):
                menu.addSeparator()
                return
            
            if action_def.get("submenu"):
                self._add_submenu(menu, action_def, parent)
                return
            
            # Regular menu item
            action = self._create_menu_action(action_def, parent)
            if action:
                menu.addAction(action)
                
        except Exception as e:
            self.logger.warning(f"Failed to add menu item: {e}")
    
    def _add_submenu(self, menu: QMenu, action_def: Dict[str, Any], parent: QWidget):
        """
        Add a submenu to the menu.
        
        Args:
            menu: Parent menu
            action_def: Submenu definition
            parent: Parent widget
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
                self._add_submenu_item(submenu, sub_action, parent)
            
            menu.addMenu(submenu)
            
        except Exception as e:
            self.logger.warning(f"Failed to add submenu: {e}")
    
    def _add_submenu_item(self, submenu: QMenu, sub_action: Dict[str, Any], parent: QWidget):
        """
        Add an item to a submenu.
        
        Args:
            submenu: Submenu to add item to
            sub_action: Submenu item definition
            parent: Parent widget
        """
        try:
            if sub_action.get("separator"):
                submenu.addSeparator()
                return
            
            # Handle different submenu item formats
            if "text" in sub_action:
                text = sub_action["text"]
                action_name = sub_action.get("action", "unknown_action")
            elif "name" in sub_action:
                text = sub_action["name"]
                if "action" in sub_action:
                    action_name = sub_action["action"]
                elif "path" in sub_action:
                    action_name = f"open_with_{sub_action['path']}"
                else:
                    action_name = "unknown_action"
            else:
                self.logger.warning(f"Invalid submenu item format: {sub_action}")
                return
            
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
                lambda checked, action=action_name: self._handle_context_action(action)
            )
            
            submenu.addAction(sub_item)
            
        except Exception as e:
            self.logger.warning(f"Failed to add submenu item: {e}")
    
    def _create_menu_action(self, action_def: Dict[str, Any], parent: QWidget) -> Optional[QAction]:
        """
        Create a menu action from definition.
        
        Args:
            action_def: Action definition
            parent: Parent widget
            
        Returns:
            QAction instance or None
        """
        try:
            action = QAction(action_def["text"], parent)
            
            # Set icon
            icon = self._get_menu_icon(action_def.get("icon"), action_def["text"])
            if icon and not icon.isNull():
                action.setIcon(icon)
            
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
                self._context_menu_commands[action_name] = action_def["command"]
            
            return action
            
        except Exception as e:
            self.logger.warning(f"Failed to create menu action: {e}")
            return None
    
    def _get_menu_icon(self, icon_name: Optional[str], text: str = "") -> QIcon:
        """
        Get icon for menu item.
        
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
        
        # Direct text analysis for common applications and actions
        icon_mapping = {
            # Applications
            "vlc": "vlc",
            "media player": "vlc", 
            "mpc": "mpc",
            "media player classic": "mpc",
            "git": "git",
            "visual studio code": "code",
            "vs code": "code",
            "code": "code",
            "sublime": "sublime",
            "notepad": "editor",
            "powershell": "powershell",
            "cmd": "cmd",
            "command": "cmd",
            
            # Actions
            "cut": "cut",
            "copy": "copy", 
            "paste": "paste",
            "delete": "delete",
            "rename": "rename",
            "properties": "properties",
            "open": "file_open",
            "open with": "open_with",
            "send to": "send_to",
            "new": "new",
            "folder": "folder",
            "refresh": "refresh",
            "search": "search",
            "find": "find",
        }
        
        # Check for direct matches
        for key, icon in icon_mapping.items():
            if key in text_lower:
                return icon
        
        # Check for specific patterns
        if "edit with" in text_lower or "edit" in text_lower:
            return "editor"
        elif "play with" in text_lower or "play" in text_lower:
            return "media"
        elif "view" in text_lower:
            return "view"
        elif "terminal" in text_lower or "shell" in text_lower:
            return "terminal"
        
        return "app_extension"
    
    def _handle_context_action(self, action_name: str):
        """
        Handle context menu action.
        
        Args:
            action_name: Name of the triggered action
        """
        try:
            self.logger.debug(f"Handling context action: {action_name}")
            
            # Check for registered custom handlers first
            if action_name in self._action_handlers:
                handler = self._action_handlers[action_name]
                handler(self._context_menu_files)
                return
            
            # Emit signal for external handling
            self.action_triggered.emit(action_name, [str(f) for f in self._context_menu_files])
            
            # Handle shell extension commands
            if action_name in self._context_menu_commands:
                command = self._context_menu_commands[action_name]
                self._execute_shell_command(command)
            
        except Exception as e:
            self.logger.error(f"Failed to handle context action {action_name}: {e}")
    
    def _execute_shell_command(self, command: str):
        """
        Execute shell extension command.
        
        Args:
            command: Command to execute
        """
        try:
            import subprocess
            
            # Replace file placeholders in command
            if self._context_menu_files:
                file_paths = [str(f) for f in self._context_menu_files]
                # Simple placeholder replacement - could be enhanced
                command = command.replace("%1", file_paths[0] if file_paths else "")
            
            # Execute command
            self.logger.info(f"Executing shell command: {command}")
            subprocess.Popen(command, shell=True)
            
        except Exception as e:
            self.logger.error(f"Failed to execute shell command {command}: {e}")
    
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
        self._context_menu_commands.clear()
        self.logger.debug("Context menu state cleared")