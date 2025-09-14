"""
Core application module
Main application class and initialization
"""

from PySide6.QtCore import QTimer

from src.ui.main_window import MainWindow
from src.config.settings import AppConfig
from src.utils.logger import get_logger
from src.services.file_service import FileService
from src.services.theme_service import ThemeService
from src.services.cross_platform_shell_integration import get_shell_integration
from src.utils.cross_platform_filesystem import get_cross_platform_fs
from platform_config import get_platform_config


class FileOrbitApplication:
    """Main application class with cross-platform support"""
    
    def __init__(self, platform_config=None):
        self.logger = get_logger(__name__)
        self.config = AppConfig()
        self.platform_config = platform_config or get_platform_config()
        self.main_window = None
        self.file_service = None
        self.theme_service = None
        self.shell_integration = None
        self.cross_platform_fs = None
        
        self._initialize_services()
        self._create_main_window()
        self._setup_auto_save()
    
    def _initialize_services(self):
        """Initialize application services"""
        self.file_service = FileService()
        self.theme_service = ThemeService()
        self.shell_integration = get_shell_integration()
        self.cross_platform_fs = get_cross_platform_fs()
        
        # Apply theme
        theme_name = self.config.get('appearance', 'theme', 'dark')
        self.theme_service.apply_theme(theme_name)
        
        # Log platform information
        self.logger.info(f"Platform: {self.platform_config.platform_name}")
        self.logger.info(f"Architecture: {self.platform_config.architecture}")
        self.logger.info(f"Shell integration available: {self.shell_integration.is_shell_integration_available()}")
    
    def _create_main_window(self):
        """Create and setup main window"""
        self.main_window = MainWindow(
            file_service=self.file_service,
            theme_service=self.theme_service,
            config=self.config
        )
        
        # Connect signals
        self.main_window.closing.connect(self._on_application_closing)
    
    def _setup_auto_save(self):
        """Setup auto-save timer for settings"""
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save_settings)
        self.auto_save_timer.start(30000)  # Save every 30 seconds
    
    def _auto_save_settings(self):
        """Auto-save application settings"""
        try:
            self.config.save()
        except Exception as e:
            self.logger.warning(f"Failed to auto-save settings: {e}")
    
    def _on_application_closing(self):
        """Handle application closing"""
        self.logger.info("Application closing...")
        self.config.save()
        
        # Stop services
        if self.file_service:
            self.file_service.stop_all_operations()
    
    def show(self):
        """Show the main window"""
        if self.main_window:
            self.main_window.show()
            self.main_window.restore_window_state()
    
    def get_main_window(self):
        """Get main window instance"""
        return self.main_window
