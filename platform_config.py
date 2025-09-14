"""
Platform Configuration for Cross-Platform FileOrbit
Optimizes settings based on system architecture, platform, and capabilities
"""

import sys
import platform
import psutil
import os
from pathlib import Path


class PlatformConfig:
    """Cross-platform configuration with platform-specific optimizations"""
    
    def __init__(self):
        self.is_64bit = self._check_64bit_system()
        self.system_memory = self._get_system_memory()
        self.cpu_count = psutil.cpu_count(logical=True)
        self.platform_name = platform.system().lower()
        self.architecture = platform.machine().lower()
        self.os_version = platform.version()
        self.python_version = platform.python_version()
        
        # Platform-specific initialization
        self._init_platform_specifics()
        
    def _check_64bit_system(self) -> bool:
        """Verify we're running on a 64-bit system"""
        return sys.maxsize > 2**32
    
    def _get_system_memory(self) -> int:
        """Get total system memory in GB"""
        return psutil.virtual_memory().total // (1024**3)
    
    def _init_platform_specifics(self):
        """Initialize platform-specific attributes"""
        if self.platform_name == 'windows':
            self.is_windows = True
            self.is_macos = False
            self.is_linux = False
            self.path_separator = '\\'
            self.executable_extension = '.exe'
            self.supports_registry = True
            self.supports_shell_extensions = True
            self.supports_recycle_bin = True
            self.default_shell = 'cmd.exe'
            
        elif self.platform_name == 'darwin':  # macOS
            self.is_windows = False
            self.is_macos = True
            self.is_linux = False
            self.path_separator = '/'
            self.executable_extension = ''
            self.supports_registry = False
            self.supports_shell_extensions = True  # Via Finder extensions
            self.supports_recycle_bin = True  # Trash
            self.default_shell = '/bin/zsh'
            
        elif self.platform_name == 'linux':
            self.is_windows = False
            self.is_macos = False
            self.is_linux = True
            self.path_separator = '/'
            self.executable_extension = ''
            self.supports_registry = False
            self.supports_shell_extensions = True  # Via desktop environment
            self.supports_recycle_bin = True  # Trash
            self.default_shell = '/bin/bash'
            
        else:
            # Unknown platform - use POSIX defaults
            self.is_windows = False
            self.is_macos = False
            self.is_linux = False
            self.path_separator = '/'
            self.executable_extension = ''
            self.supports_registry = False
            self.supports_shell_extensions = False
            self.supports_recycle_bin = False
            self.default_shell = '/bin/sh'
    
    def get_optimal_buffer_size(self, file_size: int = 0) -> int:
        """Get optimal buffer size based on system capabilities and file size"""
        if not self.is_64bit:
            return 1024 * 1024  # 1MB for 32-bit fallback
        
        # Base buffer size on available memory and file size
        base_buffer = 4 * 1024 * 1024  # 4MB base for 64-bit
        
        if self.system_memory >= 16:  # 16GB+ RAM
            if file_size > 10 * 1024**3:  # Files > 10GB
                return 32 * 1024 * 1024  # 32MB buffer
            elif file_size > 1024**3:  # Files > 1GB
                return 16 * 1024 * 1024  # 16MB buffer
            else:
                return 8 * 1024 * 1024   # 8MB buffer
        elif self.system_memory >= 8:  # 8GB+ RAM
            if file_size > 1024**3:  # Files > 1GB
                return 8 * 1024 * 1024   # 8MB buffer
            else:
                return base_buffer       # 4MB buffer
        else:  # < 8GB RAM
            return base_buffer // 2      # 2MB buffer
    
    def get_max_concurrent_operations(self) -> int:
        """Get maximum concurrent file operations based on system"""
        if not self.is_64bit:
            return 2  # Conservative for 32-bit
        
        # Base on CPU cores but cap reasonable limits
        max_ops = min(self.cpu_count, 8)
        
        # Adjust based on available memory
        if self.system_memory < 8:
            max_ops = min(max_ops, 4)
        elif self.system_memory >= 16:
            max_ops = min(max_ops + 2, 12)
            
        return max(max_ops, 2)  # Minimum 2 operations
    
    def get_directory_scan_batch_size(self) -> int:
        """Get optimal batch size for directory scanning"""
        if not self.is_64bit:
            return 1000
        
        # Larger batches for 64-bit systems with more memory
        if self.system_memory >= 16:
            return 10000
        elif self.system_memory >= 8:
            return 5000
        else:
            return 2000
    
    def supports_memory_mapping(self) -> bool:
        """Check if memory mapping is recommended for large files"""
        return self.is_64bit and self.system_memory >= 8
    
    def get_cache_size_mb(self) -> int:
        """Get recommended cache size in MB"""
        if not self.is_64bit:
            return 50  # 50MB for 32-bit
        
        # Scale cache based on available memory
        if self.system_memory >= 32:
            return 500  # 500MB for high-end systems
        elif self.system_memory >= 16:
            return 250  # 250MB for mid-range
        elif self.system_memory >= 8:
            return 100  # 100MB for 8GB systems
        else:
            return 50   # 50MB for lower memory
    
    def get_platform_specific_settings(self) -> dict:
        """Get platform-specific optimization settings"""
        settings = {
            'is_64bit': self.is_64bit,
            'buffer_size': self.get_optimal_buffer_size(),
            'max_concurrent_ops': self.get_max_concurrent_operations(),
            'batch_size': self.get_directory_scan_batch_size(),
            'cache_size_mb': self.get_cache_size_mb(),
            'supports_memory_mapping': self.supports_memory_mapping(),
            'system_memory_gb': self.system_memory,
            'cpu_cores': self.cpu_count,
            'platform': self.platform_name,
            'architecture': self.architecture,
            'os_version': self.os_version,
            'python_version': self.python_version,
            'path_separator': self.path_separator,
            'executable_extension': self.executable_extension,
            'supports_registry': self.supports_registry,
            'supports_shell_extensions': self.supports_shell_extensions,
            'supports_recycle_bin': self.supports_recycle_bin,
            'default_shell': self.default_shell
        }
        
        # Platform-specific tweaks
        if self.is_windows:
            settings.update({
                'use_win32_apis': True,
                'file_attributes': True,
                'junction_support': True,
                'registry_support': True,
                'shell_integration': 'explorer',
                'context_menu_provider': 'windows',
                'icon_provider': 'win32',
                'file_watcher': 'windows',
                'trash_implementation': 'recycle_bin'
            })
        elif self.is_macos:
            settings.update({
                'use_foundation_apis': True,
                'spotlight_integration': True,
                'extended_attributes': True,
                'shell_integration': 'finder',
                'context_menu_provider': 'macos',
                'icon_provider': 'cocoa',
                'file_watcher': 'fsevents',
                'trash_implementation': 'trash',
                'quick_look_support': True,
                'applescript_support': True
            })
        elif self.is_linux:
            settings.update({
                'use_native_dialogs': True,
                'desktop_integration': True,
                'extended_attributes': True,
                'shell_integration': 'desktop_environment',
                'context_menu_provider': 'linux',
                'icon_provider': 'freedesktop',
                'file_watcher': 'inotify',
                'trash_implementation': 'freedesktop',
                'mime_type_support': True,
                'desktop_entry_support': True
            })
        else:
            settings.update({
                'shell_integration': 'basic',
                'context_menu_provider': 'fallback',
                'icon_provider': 'qt',
                'file_watcher': 'polling',
                'trash_implementation': 'delete'
            })
        
        return settings
    
    def get_config_directory(self) -> Path:
        """Get platform-appropriate configuration directory"""
        if self.is_windows:
            config_dir = Path(os.environ.get('APPDATA', '~')) / 'FileOrbit'
        elif self.is_macos:
            config_dir = Path.home() / 'Library' / 'Application Support' / 'FileOrbit'
        else:  # Linux and others
            config_dir = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'fileorbit'
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def get_data_directory(self) -> Path:
        """Get platform-appropriate data directory"""
        if self.is_windows:
            data_dir = Path(os.environ.get('LOCALAPPDATA', '~')) / 'FileOrbit'
        elif self.is_macos:
            data_dir = Path.home() / 'Library' / 'Application Support' / 'FileOrbit'
        else:  # Linux and others
            data_dir = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share')) / 'fileorbit'
        
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    def get_cache_directory(self) -> Path:
        """Get platform-appropriate cache directory"""
        if self.is_windows:
            cache_dir = Path(os.environ.get('LOCALAPPDATA', '~')) / 'FileOrbit' / 'Cache'
        elif self.is_macos:
            cache_dir = Path.home() / 'Library' / 'Caches' / 'FileOrbit'
        else:  # Linux and others
            cache_dir = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache')) / 'fileorbit'
        
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    def get_home_directory(self) -> Path:
        """Get user's home directory"""
        return Path.home()
    
    def get_desktop_directory(self) -> Path:
        """Get user's desktop directory"""
        if self.is_windows:
            import winreg
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                  r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
                    desktop_path, _ = winreg.QueryValueEx(key, "Desktop")
                    return Path(desktop_path)
            except Exception:
                pass
        
        # Fallback for all platforms
        desktop = Path.home() / 'Desktop'
        if not desktop.exists():
            desktop = Path.home()
        return desktop
    
    def get_documents_directory(self) -> Path:
        """Get user's documents directory"""
        if self.is_windows:
            import winreg
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                  r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
                    docs_path, _ = winreg.QueryValueEx(key, "Personal")
                    return Path(docs_path)
            except Exception:
                pass
        
        # Fallback for all platforms
        documents = Path.home() / 'Documents'
        if not documents.exists():
            documents = Path.home()
        return documents
    
    def get_system_drives(self) -> list:
        """Get list of system drives/mount points"""
        drives = []
        
        if self.is_windows:
            import string
            for letter in string.ascii_uppercase:
                drive_path = f"{letter}:\\"
                if os.path.exists(drive_path):
                    drives.append({
                        'path': drive_path,
                        'label': letter,
                        'type': 'drive'
                    })
        else:  # Unix-like systems
            # Add root filesystem
            drives.append({
                'path': '/',
                'label': 'Root',
                'type': 'filesystem'
            })
            
            # Add common mount points
            mount_points = ['/home', '/usr', '/var', '/tmp']
            if self.is_macos:
                mount_points.extend(['/Applications', '/System', '/Volumes'])
            else:  # Linux
                mount_points.extend(['/media', '/mnt'])
            
            for mount_point in mount_points:
                if os.path.exists(mount_point) and os.path.ismount(mount_point):
                    drives.append({
                        'path': mount_point,
                        'label': os.path.basename(mount_point) or mount_point,
                        'type': 'mount'
                    })
        
        return drives
    
    def supports_feature(self, feature: str) -> bool:
        """Check if a specific feature is supported on this platform"""
        feature_map = {
            'registry': self.supports_registry,
            'shell_extensions': self.supports_shell_extensions,
            'recycle_bin': self.supports_recycle_bin,
            'trash': self.supports_recycle_bin,
            'quick_look': self.is_macos,
            'applescript': self.is_macos,
            'spotlight': self.is_macos,
            'mime_types': not self.is_windows,
            'desktop_entries': self.is_linux,
            'extended_attributes': not self.is_windows or self.is_macos,
            'file_associations': True,  # All platforms support this in some form
            'context_menus': True,  # All platforms support this
            'file_watching': True,  # All platforms support this
            'notifications': True,  # All platforms support this
        }
        
        return feature_map.get(feature, False)

    @property
    def theme_colors(self) -> dict:
        """Get platform-appropriate theme colors"""
        return {
            'primary': '#4A90E2',
            'secondary': '#5BC0DE', 
            'success': '#5CB85C',
            'warning': '#F0AD4E',
            'danger': '#D9534F',
            'dark': '#2b2b2b',
            'light': '#f8f9fa',
            'background': '#2b2b2b' if self.is_macos else '#3c3c3c',
            'text': '#ffffff',
            'border': '#555555'
        }
    
    @property 
    def default_theme(self) -> str:
        """Get default theme name for platform"""
        return 'dark' if self.is_macos else 'dark'


# Global platform configuration instance
platform_config = PlatformConfig()


def get_platform_config() -> PlatformConfig:
    """Get the global platform configuration instance"""
    return platform_config


def log_system_info():
    """Log system information for debugging"""
    config = get_platform_config()
    settings = config.get_platform_specific_settings()
    
    print("=== FileOrbit Cross-Platform System Information ===")
    print(f"64-bit System: {settings['is_64bit']}")
    print(f"Platform: {settings['platform']} ({settings['architecture']})")
    print(f"OS Version: {settings['os_version']}")
    print(f"Python Version: {settings['python_version']}")
    print(f"System Memory: {settings['system_memory_gb']} GB")
    print(f"CPU Cores: {settings['cpu_cores']}")
    print(f"Path Separator: {settings['path_separator']}")
    print(f"Executable Extension: {settings['executable_extension']}")
    print(f"Shell Integration: {settings['shell_integration']}")
    print(f"Context Menu Provider: {settings['context_menu_provider']}")
    print(f"Icon Provider: {settings['icon_provider']}")
    print(f"File Watcher: {settings['file_watcher']}")
    print(f"Trash Implementation: {settings['trash_implementation']}")
    print(f"Optimal Buffer Size: {settings['buffer_size'] // 1024 // 1024} MB")
    print(f"Max Concurrent Operations: {settings['max_concurrent_ops']}")
    print(f"Directory Scan Batch Size: {settings['batch_size']}")
    print(f"Cache Size: {settings['cache_size_mb']} MB")
    print(f"Memory Mapping Support: {settings['supports_memory_mapping']}")
    print(f"Config Directory: {config.get_config_directory()}")
    print(f"Data Directory: {config.get_data_directory()}")
    print(f"Cache Directory: {config.get_cache_directory()}")
    print("=" * 55)


if __name__ == "__main__":
    log_system_info()
