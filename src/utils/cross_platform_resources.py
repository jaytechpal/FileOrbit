"""
Cross-Platform Resource Management
Provides unified resource loading across Windows, macOS, and Linux
"""

import os
from pathlib import Path
from typing import Optional
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QSize

from platform_config import get_platform_config
from src.utils.logger import get_logger


class CrossPlatformResourceManager:
    """Cross-platform resource management for icons, themes, and assets"""
    
    def __init__(self):
        self.config = get_platform_config()
        self.logger = get_logger(__name__)
        
        # Base resource directory
        self.base_path = Path(__file__).parent.parent.parent / "resources"
        
        # Platform-specific resource paths
        self.icon_paths = [
            self.base_path / "icons",
            self.base_path / "icons" / self.config.platform_name,
            self._get_system_icon_path(),
        ]
        
        # Supported icon formats by platform
        self.icon_extensions = self._get_supported_icon_extensions()
        
    def _get_system_icon_path(self) -> Optional[Path]:
        """Get platform-specific system icon path"""
        if self.config.is_windows:
            return Path(os.environ.get('WINDIR', 'C:\\Windows')) / "System32"
        elif self.config.is_macos:
            return Path("/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources")
        else:  # Linux
            # Common icon theme directories
            theme_dirs = [
                Path("/usr/share/icons/hicolor"),
                Path("/usr/share/pixmaps"),
                Path(f"{os.environ.get('HOME', '/home/user')}/.local/share/icons"),
            ]
            for theme_dir in theme_dirs:
                if theme_dir.exists():
                    return theme_dir
            return None
    
    def _get_supported_icon_extensions(self) -> list:
        """Get supported icon file extensions by platform"""
        common_formats = ['.png', '.svg', '.jpg', '.jpeg', '.bmp']
        
        if self.config.is_windows:
            return ['.ico'] + common_formats
        elif self.config.is_macos:
            return ['.icns'] + common_formats
        else:  # Linux
            return ['.svg', '.png'] + common_formats
    
    def load_icon(self, icon_name: str, size: QSize = None) -> QIcon:
        """Load icon with cross-platform fallbacks"""
        # Try different paths and extensions
        for path in self.icon_paths:
            if not path or not path.exists():
                continue
                
            for ext in self.icon_extensions:
                icon_file = path / f"{icon_name}{ext}"
                if icon_file.exists():
                    try:
                        icon = QIcon(str(icon_file))
                        if not icon.isNull():
                            if size:
                                return QIcon(icon.pixmap(size))
                            return icon
                    except Exception as e:
                        self.logger.debug(f"Failed to load icon {icon_file}: {e}")
        
        # Fallback: try system icon
        return self._get_system_icon(icon_name, size)
    
    def _get_system_icon(self, icon_name: str, size: QSize = None) -> QIcon:
        """Get system-provided icon"""
        try:
            if self.config.is_windows:
                return self._get_windows_system_icon(icon_name, size)
            elif self.config.is_macos:
                return self._get_macos_system_icon(icon_name, size)
            else:  # Linux
                return self._get_linux_system_icon(icon_name, size)
        except Exception as e:
            self.logger.debug(f"Failed to get system icon {icon_name}: {e}")
            return self._create_placeholder_icon(size)
    
    def _get_windows_system_icon(self, icon_name: str, size: QSize = None) -> QIcon:
        """Get Windows system icon"""
        from PySide6.QtWidgets import QApplication, QStyle
        
        # Map common icon names to Windows system icons
        system_icons = {
            'app_icon': QStyle.SP_ComputerIcon,
            'folder': QStyle.SP_DirIcon,
            'file': QStyle.SP_FileIcon,
            'drive': QStyle.SP_DriveHDIcon,
            'refresh': QStyle.SP_BrowserReload,
            'home': QStyle.SP_DirHomeIcon,
            'back': QStyle.SP_ArrowBack,
            'forward': QStyle.SP_ArrowForward,
            'up': QStyle.SP_ArrowUp,
        }
        
        if icon_name in system_icons:
            style = QApplication.style()
            return style.standardIcon(system_icons[icon_name])
        
        return self._create_placeholder_icon(size)
    
    def _get_macos_system_icon(self, icon_name: str, size: QSize = None) -> QIcon:
        """Get macOS system icon"""
        # macOS system icon mapping
        system_icons = {
            'app_icon': 'GenericApplicationIcon',
            'folder': 'GenericFolderIcon',
            'file': 'GenericDocumentIcon',
            'drive': 'GenericHardDisk',
        }
        
        if icon_name in system_icons:
            try:
                # Try to load from macOS system icons
                icon_path = f"/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/{system_icons[icon_name]}.icns"
                if Path(icon_path).exists():
                    return QIcon(icon_path)
            except Exception:
                pass
        
        return self._create_placeholder_icon(size)
    
    def _get_linux_system_icon(self, icon_name: str, size: QSize = None) -> QIcon:
        """Get Linux system icon using icon themes"""
        from PySide6.QtGui import QIcon
        
        # Try to use system icon theme
        theme_icons = {
            'app_icon': 'application-x-executable',
            'folder': 'folder',
            'file': 'text-x-generic',
            'drive': 'drive-harddisk',
            'refresh': 'view-refresh',
            'home': 'user-home',
            'back': 'go-previous',
            'forward': 'go-next',
            'up': 'go-up',
        }
        
        if icon_name in theme_icons:
            # Try system theme icon
            system_icon = QIcon.fromTheme(theme_icons[icon_name])
            if not system_icon.isNull():
                return system_icon
        
        return self._create_placeholder_icon(size)
    
    def _create_placeholder_icon(self, size: QSize = None) -> QIcon:
        """Create a simple placeholder icon"""
        if not size:
            size = QSize(32, 32)
        
        # Create a simple colored square as placeholder
        pixmap = QPixmap(size)
        pixmap.fill(self.config.theme_colors.get('primary', '#4A90E2'))
        return QIcon(pixmap)
    
    def get_resource_path(self, resource_type: str, filename: str) -> Optional[Path]:
        """Get cross-platform resource path"""
        resource_path = self.base_path / resource_type / filename
        
        if resource_path.exists():
            return resource_path
        
        # Try platform-specific path
        platform_path = self.base_path / resource_type / self.config.platform_name / filename
        if platform_path.exists():
            return platform_path
        
        return None
    
    def load_stylesheet(self, theme_name: str = None) -> str:
        """Load cross-platform stylesheet"""
        if not theme_name:
            theme_name = self.config.default_theme
        
        style_file = self.get_resource_path('styles', f"{theme_name}.qss")
        if style_file:
            try:
                return style_file.read_text(encoding='utf-8')
            except Exception as e:
                self.logger.error(f"Failed to load stylesheet {style_file}: {e}")
        
        # Fallback to basic dark theme
        return self._get_basic_dark_theme()
    
    def _get_basic_dark_theme(self) -> str:
        """Get basic dark theme as fallback"""
        return """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QListWidget {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #555555;
        }
        QListWidget::item:selected {
            background-color: #4A90E2;
        }
        """


# Global resource manager instance
_resource_manager = None

def get_resource_manager() -> CrossPlatformResourceManager:
    """Get singleton resource manager instance"""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = CrossPlatformResourceManager()
    return _resource_manager