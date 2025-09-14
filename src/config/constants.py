"""
Configuration constants for FileOrbit
Centralizes all magic numbers and configuration values
"""

class UIConstants:
    """UI-related constants"""
    # Timing
    REFRESH_DELAY_MS = 100
    STATUS_MESSAGE_TIMEOUT_MS = 2000
    
    # Dimensions
    MIN_DIALOG_WIDTH = 400
    MIN_DIALOG_HEIGHT = 300
    MIN_WINDOW_WIDTH = 1000
    MIN_WINDOW_HEIGHT = 600
    DEFAULT_WINDOW_WIDTH = 1400
    DEFAULT_WINDOW_HEIGHT = 800
    
    # Preferences dialog
    PREFERENCES_DIALOG_WIDTH = 500
    PREFERENCES_DIALOG_HEIGHT = 400
    
    # Splitter sizes
    PANEL_SPLITTER_LEFT = 500
    PANEL_SPLITTER_RIGHT = 500
    SIDEBAR_WIDTH = 200
    MAIN_CONTENT_WIDTH = 1200
    
    # Button dimensions
    NAVIGATION_BUTTON_WIDTH = 30
    
    # Padding and margins
    TAB_PADDING_HORIZONTAL = 12
    TAB_PADDING_VERTICAL = 8
    BUTTON_PADDING_HORIZONTAL = 8
    BUTTON_PADDING_VERTICAL = 4
    
    # Font weights
    FONT_WEIGHT_NORMAL = 400
    FONT_WEIGHT_MEDIUM = 500
    FONT_WEIGHT_BOLD = 600
    
    # File size units
    BYTES_PER_KB = 1024.0


class ShellConstants:
    """Shell integration constants"""
    # Priority levels for context menu ordering
    PRIORITY_OPEN_ACTIONS = 1
    PRIORITY_GIT_OPERATIONS = 10
    PRIORITY_CODE_EDITORS = 20
    PRIORITY_FIRST_SEPARATOR = 50
    PRIORITY_FILE_OPERATIONS = 100
    PRIORITY_SECOND_SEPARATOR = 150
    PRIORITY_THIRD_PARTY_APPS = 200
    PRIORITY_FINAL_SEPARATOR = 800
    PRIORITY_SYSTEM_ACTIONS = 900
    PRIORITY_DEFAULT = 400
    
    # Separator spacing calculation
    SEPARATOR_SPACING = 200
    
    # Registry paths
    REGISTRY_CLASSES_ROOT = r"HKEY_CLASSES_ROOT"
    SHELL_EXTENSIONS_PATH = r"shell"
    COMMAND_PATH = r"command"
    
    # System resource mappings
    SYSTEM_RESOURCE_MAPPINGS = {
        '@shell32.dll,-8506': 'Find',
        '@shell32.dll,-8508': 'Find',
        '@wsl.exe,-2': '',  # Skip WSL entries completely
        '@shell32.dll,-30315': 'Send to',
        '@shell32.dll,-31374': 'Copy',
        '@shell32.dll,-31375': 'Cut',
        '@shell32.dll,-10210': '',  # Skip
        '@shell32.dll,-10211': '',  # Skip
        '@shell32.dll,-31233': '',  # Skip
    }
    
    # Priority application text patterns
    PRIORITY_APP_PATTERNS = [
        "git gui", "git bash", "open with code", "open with sublime", 
        "open powershell", "cmd", "command prompt"
    ]


class PathConstants:
    """File system path constants for generic discovery"""
    
    # Registry paths for automatic discovery
    REGISTRY_DISCOVERY_PATHS = {
        "uninstall_programs": [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ],
        "shell_extensions": [
            r"*\shell",
            r"Directory\shell", 
            r"Folder\shell",
            r"AllFilesystemObjects\shell",
            r"SystemFileAssociations\*\shell"
        ],
        "file_associations": [
            r"Applications",
            r"SystemFileAssociations"
        ],
        "application_paths": [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths"
        ]
    }
    
    # Generic search directories for filesystem scanning
    GENERIC_SEARCH_DIRECTORIES = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        r"C:\Users\{username}\AppData\Local\Programs",
        r"C:\Users\{username}\AppData\Roaming",
        r"C:\ProgramData",
        r"C:\Tools",
        r"C:\Apps",
        r"D:\Programs",
        r"D:\Tools",
        r"D:\Apps"
    ]
    
    # System directories
    WINDOWS_SYSTEM32 = r"C:\Windows\System32"
    WINDOWS_SYSWOW64 = r"C:\Windows\SysWOW64"
    
    # Registry value names to check for executable paths
    EXECUTABLE_PATH_VALUE_NAMES = [
        "",  # Default value
        "InstallLocation",
        "InstallDir", 
        "InstallPath",
        "Path",
        "ApplicationPath",
        "ExePath",
        "UninstallString",
        "DisplayIcon"
    ]
    
    # File extensions to consider as executables
    EXECUTABLE_EXTENSIONS = [".exe", ".bat", ".cmd", ".com", ".msi"]


class IconConstants:
    """Icon-related constants"""
    # Windows API constants
    SHGFI_ICON = 0x100
    SHGFI_LARGEICON = 0x0
    SHGFI_SMALLICON = 0x1
    ICON_BUFFER_SIZE = 80
    
    # Default icon indices
    DEFAULT_ICON_INDEX = 0
    
    # Cache configuration
    MAX_CACHE_SIZE = 1000
    OPTIMAL_CACHE_SIZE = 750
    CACHE_CLEANUP_INTERVAL = 300000  # 5 minutes in milliseconds
    
    # Application aliases for icon detection
    APP_ALIASES = {
        "sublime": ["editor", "sublime text"],
        "mpc": ["mpc-hc", "media", "media player classic"],
        "vlc": ["vlc media player", "videolan"],
        "git": ["git gui", "git bash"],
        "code": ["visual studio code", "vs code"],
        "powershell": ["windows powershell", "pwsh"],
    }


class FilterConstants:
    """Filtering constants for shell extensions"""
    # Text patterns to filter out
    FILTER_PATTERNS = [
        'wsl', 'windows subsystem', 'microsoft store',
        'debugger', 'profiler', 'analyzer'
    ]
    
    # Prefixes to filter out
    FILTER_PREFIXES = ['@', 'ms-']
    
    # Minimum text length
    MIN_TEXT_LENGTH = 2


class LoggingConstants:
    """Logging configuration constants"""
    # Log levels
    DEBUG_LEVEL = "DEBUG"
    INFO_LEVEL = "INFO"
    WARNING_LEVEL = "WARNING"
    ERROR_LEVEL = "ERROR"
    
    # Log format
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # File encoding
    LOG_FILE_ENCODING = 'utf-8'


class CacheConstants:
    """Caching configuration"""
    # Cache sizes
    ICON_CACHE_SIZE = 100
    SHELL_EXTENSIONS_CACHE_SIZE = 50
    APP_DETECTION_CACHE_SIZE = 20
    
    # Cache timeouts (in seconds)
    ICON_CACHE_TIMEOUT = 3600  # 1 hour
    SHELL_EXTENSIONS_CACHE_TIMEOUT = 1800  # 30 minutes
    APP_DETECTION_CACHE_TIMEOUT = 7200  # 2 hours


class PerformanceConstants:
    """Performance-related constants"""
    # Thread pool sizes
    ICON_EXTRACTION_THREADS = 4
    FILE_OPERATION_THREADS = 2
    
    # Batch sizes
    FILE_LIST_BATCH_SIZE = 1000
    ICON_EXTRACTION_BATCH_SIZE = 50
    
    # Timeouts
    SHELL_COMMAND_TIMEOUT_MS = 5000
    ICON_EXTRACTION_TIMEOUT_MS = 2000