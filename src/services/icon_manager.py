"""
IconManager - Centralized icon handling and caching service

This service handles all icon extraction, caching, and management for the file manager.
It provides consistent icon handling across the application with intelligent caching.
"""

import sys
from pathlib import Path
from typing import Dict, Any

from PySide6.QtWidgets import QFileIconProvider, QStyle, QApplication
from PySide6.QtCore import QFileInfo, QObject, QTimer
from PySide6.QtGui import QIcon

from src.utils.logger import get_logger
from src.utils.error_handling import IconExtractionError, handle_icon_operation
from src.config.constants import IconConstants


class IconManager(QObject):
    """
    Centralized icon management service with caching and platform support.
    
    Provides consistent icon handling for:
    - File and folder icons
    - Application icons
    - System icons
    - Context menu icons
    - Executable icons with index support
    """
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        
        # Qt icon provider for native file icons
        self.icon_provider = QFileIconProvider()
        
        # Platform detection
        self.platform = sys.platform
        self.logger.info(f"IconManager initialized for platform: {self.platform}")
        
        # Icon cache for performance
        self._icon_cache: Dict[str, QIcon] = {}
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Cache cleanup timer
        self._cache_cleanup_timer = QTimer()
        self._cache_cleanup_timer.timeout.connect(self._cleanup_cache)
        self._cache_cleanup_timer.start(300000)  # 5 minutes
        
        self.logger.info("IconManager initialized successfully")
    
    def get_file_icon(self, file_path: Path) -> QIcon:
        """
        Get icon for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            QIcon for the file
        """
        cache_key = f"file:{str(file_path)}"
        
        if cache_key in self._icon_cache:
            self._cache_hits += 1
            return self._icon_cache[cache_key]
        
        self._cache_misses += 1
        
        try:
            icon = self._extract_file_icon(file_path)
            self._icon_cache[cache_key] = icon
            return icon
        except Exception as e:
            self.logger.warning(f"Failed to get icon for {file_path}: {e}")
            return self.get_fallback_icon(file_path)
    
    def get_folder_icon(self) -> QIcon:
        """
        Get standard folder icon.
        
        Returns:
            QIcon for folders
        """
        cache_key = "folder:standard"
        
        if cache_key in self._icon_cache:
            self._cache_hits += 1
            return self._icon_cache[cache_key]
        
        self._cache_misses += 1
        
        try:
            folder_icon = self.icon_provider.icon(QFileIconProvider.Folder)
            if folder_icon and not folder_icon.isNull():
                self._icon_cache[cache_key] = folder_icon
                return folder_icon
        except Exception as e:
            self.logger.warning(f"Failed to get folder icon: {e}")
        
        # Fallback to system folder icon
        return self._get_system_folder_icon()
    
    def get_parent_directory_icon(self) -> QIcon:
        """
        Get icon for parent directory (..) entry.
        
        Returns:
            QIcon for parent directory
        """
        cache_key = "folder:parent"
        
        if cache_key in self._icon_cache:
            self._cache_hits += 1
            return self._icon_cache[cache_key]
        
        self._cache_misses += 1
        
        try:
            # Try to get up arrow icon
            if QApplication.instance():
                style = QApplication.instance().style()
                if style:
                    icon = style.standardIcon(QStyle.SP_ArrowUp)
                    if icon and not icon.isNull():
                        self._icon_cache[cache_key] = icon
                        return icon
        except Exception as e:
            self.logger.warning(f"Failed to get parent directory icon: {e}")
        
        # Fallback to folder icon
        return self.get_folder_icon()
    
    def get_fallback_icon(self, file_path: Path) -> QIcon:
        """
        Get fallback icon for a file when normal icon extraction fails.
        
        Args:
            file_path: Path to the file
            
        Returns:
            QIcon fallback icon
        """
        cache_key = f"fallback:{file_path.suffix.lower()}"
        
        if cache_key in self._icon_cache:
            self._cache_hits += 1
            return self._icon_cache[cache_key]
        
        self._cache_misses += 1
        
        try:
            if file_path.is_dir():
                icon = self.get_folder_icon()
            else:
                # Use system default file icon
                if QApplication.instance():
                    style = QApplication.instance().style()
                    if style:
                        icon = style.standardIcon(QStyle.SP_FileIcon)
                        if icon and not icon.isNull():
                            self._icon_cache[cache_key] = icon
                            return icon
                
                # Final fallback
                icon = self.icon_provider.icon(QFileIconProvider.File)
            
            self._icon_cache[cache_key] = icon
            return icon
        except Exception as e:
            self.logger.error(f"Failed to get fallback icon for {file_path}: {e}")
            return QIcon()  # Return empty icon as last resort
    
    def get_context_menu_icon(self, icon_name: str) -> QIcon:
        """
        Get icon for context menu items.
        
        Args:
            icon_name: Name or path of the icon
            
        Returns:
            QIcon for context menu
        """
        if not icon_name:
            return QIcon()
        
        cache_key = f"context:{icon_name}"
        
        if cache_key in self._icon_cache:
            self._cache_hits += 1
            return self._icon_cache[cache_key]
        
        self._cache_misses += 1
        
        try:
            # Try different icon extraction methods
            icon = self._get_system_application_icon(icon_name)
            if icon and not icon.isNull():
                self._icon_cache[cache_key] = icon
                return icon
            
            # Try as file path
            icon = self._get_icon_from_path(icon_name)
            if icon and not icon.isNull():
                self._icon_cache[cache_key] = icon
                return icon
            
            # Try executable extraction
            icon = self._get_exe_icon(icon_name)
            if icon and not icon.isNull():
                self._icon_cache[cache_key] = icon
                return icon
                
        except Exception as e:
            self.logger.warning(f"Failed to get context menu icon for {icon_name}: {e}")
        
        return QIcon()
    
    def get_exe_icon_with_index(self, exe_path: str, icon_index: int = 0) -> QIcon:
        """
        Extract icon from executable at specific index.
        
        Args:
            exe_path: Path to executable
            icon_index: Icon index in the executable
            
        Returns:
            QIcon extracted from executable
        """
        cache_key = f"exe:{exe_path}:{icon_index}"
        
        if cache_key in self._icon_cache:
            self._cache_hits += 1
            return self._icon_cache[cache_key]
        
        self._cache_misses += 1
        
        try:
            icon = self._extract_exe_icon_with_index(exe_path, icon_index)
            if icon and not icon.isNull():
                self._icon_cache[cache_key] = icon
                return icon
        except Exception as e:
            self.logger.warning(f"Failed to extract icon from {exe_path} at index {icon_index}: {e}")
        
        return QIcon()
    
    def clear_cache(self):
        """Clear the icon cache."""
        old_size = len(self._icon_cache)
        self._icon_cache.clear()
        self.logger.info(f"Icon cache cleared. Removed {old_size} entries.")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_size": len(self._icon_cache),
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests
        }
    
    # Private implementation methods
    
    @handle_icon_operation
    def _extract_file_icon(self, file_path: Path) -> QIcon:
        """Extract icon for a file using platform-specific methods."""
        try:
            file_info = QFileInfo(str(file_path))
            icon = self.icon_provider.icon(file_info)
            
            if icon and not icon.isNull():
                return icon
            else:
                raise IconExtractionError(f"Icon provider returned null icon for {file_path}")
                
        except Exception as e:
            self.logger.warning(f"Standard icon extraction failed for {file_path}: {e}")
            raise IconExtractionError(f"Failed to extract icon for {file_path}") from e
    
    def _get_system_folder_icon(self) -> QIcon:
        """Get system folder icon as fallback."""
        try:
            if QApplication.instance():
                style = QApplication.instance().style()
                if style:
                    return style.standardIcon(QStyle.SP_DirIcon)
        except Exception as e:
            self.logger.warning(f"Failed to get system folder icon: {e}")
        
        return QIcon()
    
    def _get_system_application_icon(self, icon_name: str) -> QIcon:
        """Extract icon from system applications."""
        try:
            # Platform-specific implementation would go here
            # For now, return empty icon
            return QIcon()
        except Exception as e:
            self.logger.warning(f"Failed to get system application icon for {icon_name}: {e}")
            return QIcon()
    
    def _get_icon_from_path(self, icon_path: str) -> QIcon:
        """Load icon from file path."""
        try:
            if Path(icon_path).exists():
                return QIcon(icon_path)
        except Exception as e:
            self.logger.warning(f"Failed to load icon from path {icon_path}: {e}")
        
        return QIcon()
    
    def _get_exe_icon(self, exe_path: str) -> QIcon:
        """Extract icon from executable file."""
        try:
            return self._extract_exe_icon_with_index(exe_path, 0)
        except Exception as e:
            self.logger.warning(f"Failed to extract icon from executable {exe_path}: {e}")
            return QIcon()
    
    def _extract_exe_icon_with_index(self, exe_path: str, icon_index: int) -> QIcon:
        """Platform-specific executable icon extraction."""
        if self.platform == "win32":
            return self._extract_windows_exe_icon(exe_path, icon_index)
        else:
            # For non-Windows platforms, use file icon
            try:
                if Path(exe_path).exists():
                    return self.get_file_icon(Path(exe_path))
            except Exception as e:
                self.logger.warning(f"Failed to get file icon for {exe_path}: {e}")
        
        return QIcon()
    
    def _extract_windows_exe_icon(self, exe_path: str, icon_index: int) -> QIcon:
        """Extract icon from Windows executable using Windows API."""
        try:
            import win32gui
            
            # Extract icon handle
            large_icons, small_icons = win32gui.ExtractIconEx(exe_path, icon_index, 1)
            
            if large_icons:
                # Convert to QIcon
                icon_handle = large_icons[0]
                
                # For now, return empty icon - full implementation would need
                # proper bitmap to QPixmap conversion using GetIconInfo
                
                # Clean up
                win32gui.DestroyIcon(icon_handle)
                
                return QIcon()  # Placeholder - actual implementation needed
            
        except ImportError:
            self.logger.warning("Windows icon extraction requires pywin32")
        except Exception as e:
            self.logger.warning(f"Windows icon extraction failed for {exe_path}: {e}")
        
        return QIcon()
    
    def _cleanup_cache(self):
        """Periodic cache cleanup to prevent memory leaks."""
        if len(self._icon_cache) > IconConstants.MAX_CACHE_SIZE:
            # Remove oldest entries (simple FIFO for now)
            items_to_remove = len(self._icon_cache) - IconConstants.OPTIMAL_CACHE_SIZE
            keys_to_remove = list(self._icon_cache.keys())[:items_to_remove]
            
            for key in keys_to_remove:
                del self._icon_cache[key]
            
            self.logger.info(f"Icon cache cleaned up. Removed {items_to_remove} entries.")