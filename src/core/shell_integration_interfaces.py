"""
Platform-specific shell integration interfaces

Defines the contract for shell integration across different operating systems
while maintaining native behavior and appearance.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
from PySide6.QtWidgets import QWidget


class IShellIntegrationProvider(ABC):
    """
    Abstract base class for platform-specific shell integration.
    """
    
    @abstractmethod
    def get_context_menu_actions(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """
        Get context menu actions for selected files.
        
        Args:
            file_paths: List of selected file paths
            
        Returns:
            List of action dictionaries with platform-native actions
        """
        pass
    
    @abstractmethod
    def get_empty_area_context_menu(self, current_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        Get context menu actions for empty area.
        
        Args:
            current_path: Current directory path
            
        Returns:
            List of action dictionaries for empty area
        """
        pass
    
    @abstractmethod
    def execute_action(self, action_name: str, file_paths: List[Path], **kwargs) -> bool:
        """
        Execute a platform-specific action.
        
        Args:
            action_name: Name of the action to execute
            file_paths: List of file paths to operate on
            **kwargs: Additional action parameters
            
        Returns:
            True if action was executed successfully
        """
        pass
    
    @abstractmethod
    def get_default_applications(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Get default applications for a file type.
        
        Args:
            file_path: File path to get applications for
            
        Returns:
            List of application dictionaries
        """
        pass
    
    @abstractmethod
    def supports_trash(self) -> bool:
        """
        Check if platform supports trash/recycle bin.
        
        Returns:
            True if trash is supported
        """
        pass
    
    @abstractmethod
    def move_to_trash(self, file_paths: List[Path]) -> bool:
        """
        Move files to trash/recycle bin.
        
        Args:
            file_paths: List of file paths to move to trash
            
        Returns:
            True if operation was successful
        """
        pass
    
    @abstractmethod
    def get_file_properties_dialog(self, file_path: Path, parent: QWidget) -> bool:
        """
        Show platform-native file properties dialog.
        
        Args:
            file_path: File path to show properties for
            parent: Parent widget
            
        Returns:
            True if dialog was shown
        """
        pass


class IDesktopEnvironment(ABC):
    """
    Interface for desktop environment specific operations (mainly for Linux).
    """
    
    @abstractmethod
    def get_desktop_environment(self) -> str:
        """
        Get the current desktop environment name.
        
        Returns:
            Desktop environment identifier (gnome, kde, xfce, etc.)
        """
        pass
    
    @abstractmethod
    def get_file_manager_command(self) -> str:
        """
        Get the command to open the default file manager.
        
        Returns:
            Command string to launch file manager
        """
        pass
    
    @abstractmethod
    def get_terminal_command(self) -> str:
        """
        Get the command to open the default terminal.
        
        Returns:
            Command string to launch terminal
        """
        pass
    
    @abstractmethod
    def supports_desktop_notifications(self) -> bool:
        """
        Check if desktop notifications are supported.
        
        Returns:
            True if notifications are supported
        """
        pass


class IPlatformContextMenu(ABC):
    """
    Interface for platform-specific context menu implementation.
    """
    
    @abstractmethod
    def create_context_menu(self, parent: QWidget, file_paths: List[Path]) -> Optional[object]:
        """
        Create platform-native context menu.
        
        Args:
            parent: Parent widget
            file_paths: List of file paths
            
        Returns:
            Platform-specific menu object or None
        """
        pass
    
    @abstractmethod
    def add_custom_action(self, menu: object, text: str, icon: str, callback) -> None:
        """
        Add custom action to platform menu.
        
        Args:
            menu: Platform-specific menu object
            text: Action text
            icon: Icon name or path
            callback: Action callback function
        """
        pass
    
    @abstractmethod
    def show_menu(self, menu: object, position) -> None:
        """
        Show the platform-specific menu.
        
        Args:
            menu: Platform-specific menu object
            position: Position to show menu at
        """
        pass