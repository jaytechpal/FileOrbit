"""
Service Interfaces for Dependency Injection

This module defines all the interfaces that services must implement to enable
dependency injection, testability, and plugin architecture in the file manager.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QIcon


class IIconProvider(ABC):
    """Interface for icon management services."""
    
    @abstractmethod
    def get_file_icon(self, file_path: Path) -> QIcon:
        """Get icon for a file."""
        pass
    
    @abstractmethod
    def get_folder_icon(self) -> QIcon:
        """Get standard folder icon."""
        pass
    
    @abstractmethod
    def get_context_menu_icon(self, icon_name: str) -> QIcon:
        """Get icon for context menu items."""
        pass
    
    @abstractmethod
    def get_exe_icon_with_index(self, exe_path: str, icon_index: int = 0) -> QIcon:
        """Extract icon from executable at specific index."""
        pass
    
    @abstractmethod
    def clear_cache(self):
        """Clear the icon cache."""
        pass
    
    @abstractmethod
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass


class IContextMenuProvider(ABC):
    """Interface for context menu management services."""
    
    @abstractmethod
    def show_file_context_menu(self, parent: QWidget, position, selected_files: List[Path]) -> bool:
        """Show context menu for selected files."""
        pass
    
    @abstractmethod
    def show_empty_area_context_menu(self, parent: QWidget, position) -> bool:
        """Show context menu for empty area."""
        pass
    
    @abstractmethod
    def register_action_handler(self, action_name: str, handler: Callable):
        """Register a handler for a specific action."""
        pass
    
    @abstractmethod
    def get_context_files(self) -> List[Path]:
        """Get currently selected context menu files."""
        pass
    
    @abstractmethod
    def clear_context(self):
        """Clear context menu state."""
        pass


class INavigationProvider(ABC):
    """Interface for navigation and tab management services."""
    
    @abstractmethod
    def create_initial_tab(self, initial_path: Path) -> int:
        """Create the initial tab."""
        pass
    
    @abstractmethod
    def create_new_tab(self, path: Optional[Path] = None) -> int:
        """Create a new tab."""
        pass
    
    @abstractmethod
    def close_tab(self, tab_index: int) -> bool:
        """Close a tab."""
        pass
    
    @abstractmethod
    def navigate_to(self, path: Path, tab_index: Optional[int] = None) -> bool:
        """Navigate to a path in the specified tab."""
        pass
    
    @abstractmethod
    def go_back(self, tab_index: Optional[int] = None) -> bool:
        """Navigate back in history."""
        pass
    
    @abstractmethod
    def go_forward(self, tab_index: Optional[int] = None) -> bool:
        """Navigate forward in history."""
        pass
    
    @abstractmethod
    def go_up(self, tab_index: Optional[int] = None) -> bool:
        """Navigate to parent directory."""
        pass
    
    @abstractmethod
    def get_current_path(self) -> Optional[Path]:
        """Get current path of active tab."""
        pass
    
    @abstractmethod
    def get_tab_count(self) -> int:
        """Get number of tabs."""
        pass
    
    @abstractmethod
    def add_bookmark(self, path: Path, name: Optional[str] = None):
        """Add a bookmark."""
        pass
    
    @abstractmethod
    def get_bookmarks(self) -> List[Path]:
        """Get all bookmarks."""
        pass


class IShellIntegration(ABC):
    """Interface for shell integration services."""
    
    @abstractmethod
    def get_context_menu_actions(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """Get context menu actions for files."""
        pass
    
    @abstractmethod
    def get_empty_area_context_menu(self) -> List[Dict[str, Any]]:
        """Get context menu actions for empty area."""
        pass
    
    @abstractmethod
    def get_shell_extensions_for_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Get shell extensions for a file."""
        pass
    
    @abstractmethod
    def execute_shell_command(self, command: str, file_paths: List[Path]) -> bool:
        """Execute a shell command."""
        pass


class IApplicationDiscovery(ABC):
    """Interface for application discovery services."""
    
    @abstractmethod
    def discover_all_installed_applications(self) -> List[Dict[str, Any]]:
        """Discover all installed applications."""
        pass
    
    @abstractmethod
    def discover_applications_for_file_type(self, file_extension: str) -> List[Dict[str, Any]]:
        """Discover applications that can handle a file type."""
        pass
    
    @abstractmethod
    def get_application_info(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific application."""
        pass
    
    @abstractmethod
    def refresh_cache(self):
        """Refresh the application discovery cache."""
        pass


class IFileService(ABC):
    """Interface for file operation services."""
    
    @abstractmethod
    def copy_files(self, source_paths: List[Path], destination: Path) -> bool:
        """Copy files to destination."""
        pass
    
    @abstractmethod
    def move_files(self, source_paths: List[Path], destination: Path) -> bool:
        """Move files to destination."""
        pass
    
    @abstractmethod
    def delete_files(self, file_paths: List[Path]) -> bool:
        """Delete files."""
        pass
    
    @abstractmethod
    def create_folder(self, parent_path: Path, folder_name: str) -> bool:
        """Create a new folder."""
        pass
    
    @abstractmethod
    def rename_file(self, file_path: Path, new_name: str) -> bool:
        """Rename a file or folder."""
        pass
    
    @abstractmethod
    def get_file_info(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Get file information."""
        pass
    
    @abstractmethod
    def start_watching_directory(self, directory_path: str):
        """Start watching a directory for changes."""
        pass
    
    @abstractmethod
    def stop_watching_directory(self, directory_path: str):
        """Stop watching a directory for changes."""
        pass


class IConfigurationService(ABC):
    """Interface for configuration management services."""
    
    @abstractmethod
    def get_setting(self, key: str, default_value: Any = None) -> Any:
        """Get a configuration setting."""
        pass
    
    @abstractmethod
    def set_setting(self, key: str, value: Any):
        """Set a configuration setting."""
        pass
    
    @abstractmethod
    def get_section(self, section_name: str) -> Dict[str, Any]:
        """Get all settings in a section."""
        pass
    
    @abstractmethod
    def save_settings(self):
        """Save settings to persistent storage."""
        pass
    
    @abstractmethod
    def load_settings(self):
        """Load settings from persistent storage."""
        pass


class IThemeService(ABC):
    """Interface for theme management services."""
    
    @abstractmethod
    def get_current_theme(self) -> str:
        """Get the name of the current theme."""
        pass
    
    @abstractmethod
    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme."""
        pass
    
    @abstractmethod
    def get_available_themes(self) -> List[str]:
        """Get list of available themes."""
        pass
    
    @abstractmethod
    def get_theme_setting(self, setting_name: str) -> Any:
        """Get a theme-specific setting."""
        pass


class IPluginManager(ABC):
    """Interface for plugin management services."""
    
    @abstractmethod
    def load_plugins(self, plugin_directory: Path):
        """Load plugins from directory."""
        pass
    
    @abstractmethod
    def get_loaded_plugins(self) -> List[Dict[str, Any]]:
        """Get list of loaded plugins."""
        pass
    
    @abstractmethod
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        pass
    
    @abstractmethod
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        pass
    
    @abstractmethod
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a plugin."""
        pass


class ISearchService(ABC):
    """Interface for search services."""
    
    @abstractmethod
    def search_files(self, search_path: Path, pattern: str, include_hidden: bool = False) -> List[Path]:
        """Search for files matching pattern."""
        pass
    
    @abstractmethod
    def search_file_content(self, search_path: Path, content_pattern: str) -> List[Dict[str, Any]]:
        """Search for files containing text."""
        pass
    
    @abstractmethod
    def get_recent_searches(self) -> List[str]:
        """Get list of recent search patterns."""
        pass
    
    @abstractmethod
    def clear_search_history(self):
        """Clear search history."""
        pass


class ILoggingService(ABC):
    """Interface for logging services."""
    
    @abstractmethod
    def log_debug(self, message: str, **kwargs):
        """Log a debug message."""
        pass
    
    @abstractmethod
    def log_info(self, message: str, **kwargs):
        """Log an info message."""
        pass
    
    @abstractmethod
    def log_warning(self, message: str, **kwargs):
        """Log a warning message."""
        pass
    
    @abstractmethod
    def log_error(self, message: str, **kwargs):
        """Log an error message."""
        pass
    
    @abstractmethod
    def get_log_entries(self, level: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent log entries."""
        pass


class IServiceContainer(ABC):
    """Interface for dependency injection container."""
    
    @abstractmethod
    def register_singleton(self, interface_type: type, implementation: Any):
        """Register a singleton service."""
        pass
    
    @abstractmethod
    def register_transient(self, interface_type: type, implementation_factory: Callable):
        """Register a transient service."""
        pass
    
    @abstractmethod
    def resolve(self, interface_type: type) -> Any:
        """Resolve a service instance."""
        pass
    
    @abstractmethod
    def is_registered(self, interface_type: type) -> bool:
        """Check if a service is registered."""
        pass
    
    @abstractmethod
    def get_registered_services(self) -> List[type]:
        """Get list of registered service types."""
        pass