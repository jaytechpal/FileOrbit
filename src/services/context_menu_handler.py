"""
ContextMenuHandler - Cross-platform context menu management service

This service provides a unified interface for context menus across all platforms
while maintaining native look and behavior on Windows, macOS, and Linux.

Note: This is now a wrapper around CrossPlatformContextMenuHandler for
backwards compatibility.
"""

from pathlib import Path
from typing import List, Callable

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject, Signal

from src.utils.logger import get_logger
from src.services.icon_manager import IconManager
from src.services.cross_platform_context_menu import CrossPlatformContextMenuHandler

class ContextMenuHandler(QObject):
    """
    Cross-platform context menu management service.
    
    This is now a wrapper around CrossPlatformContextMenuHandler that provides
    backwards compatibility while enabling native behavior on all platforms.
    """
    
    # Signals
    action_triggered = Signal(str, list)  # action_name, file_paths
    
    def __init__(self, icon_manager: IconManager):
        super().__init__()
        self.logger = get_logger(__name__)
        
        # Use the cross-platform implementation
        self._cross_platform_handler = CrossPlatformContextMenuHandler(icon_manager)
        
        # Connect signals
        self._cross_platform_handler.action_triggered.connect(self.action_triggered)
        
        self.logger.info("ContextMenuHandler initialized with cross-platform support")
    
    def register_action_handler(self, action_name: str, handler: Callable):
        """
        Register a handler for a specific action.
        
        Args:
            action_name: Name of the action
            handler: Callable to handle the action
        """
        self._cross_platform_handler.register_action_handler(action_name, handler)
    
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
        return self._cross_platform_handler.show_file_context_menu(parent, position, selected_files)
    
    def show_empty_area_context_menu(self, parent: QWidget, position, current_path: Path = None) -> bool:
        """
        Show context menu for empty area using native platform behavior.
        
        Args:
            parent: Parent widget for the menu
            position: Position to show the menu
            current_path: Current directory path
            
        Returns:
            True if menu was shown, False otherwise
        """
        return self._cross_platform_handler.show_empty_area_context_menu(parent, position, current_path)
    
    def get_context_files(self) -> List[Path]:
        """
        Get currently selected context menu files.
        
        Returns:
            List of file paths
        """
        return self._cross_platform_handler.get_context_files()
    
    def clear_context(self):
        """Clear context menu state."""
        self._cross_platform_handler.clear_context()
    
    def supports_trash(self) -> bool:
        """
        Check if the current platform supports trash/recycle bin.
        
        Returns:
            True if trash is supported
        """
        return self._cross_platform_handler.supports_trash()
    
    def move_to_trash(self, file_paths: List[Path]) -> bool:
        """
        Move files to trash using platform-specific method.
        
        Args:
            file_paths: List of file paths to move to trash
            
        Returns:
            True if operation was successful
        """
        return self._cross_platform_handler.move_to_trash(file_paths)
    
    def show_file_properties(self, file_path: Path, parent: QWidget) -> bool:
        """
        Show platform-native file properties dialog.
        
        Args:
            file_path: File path to show properties for
            parent: Parent widget
            
        Returns:
            True if dialog was shown
        """
        return self._cross_platform_handler.show_file_properties(file_path, parent)