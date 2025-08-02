"""
Core application module
Main application class and initialization
"""

from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCore import QSettings, QTimer
from PySide6.QtGui import QAction, QKeySequence

from src.ui.main_window import MainWindow
from src.config.settings import AppConfig
from src.utils.logger import get_logger
from src.services.file_service import FileService
from src.services.theme_service import ThemeService


class FileOrbitApplication:
    """Main application class with 64-bit optimizations"""
    
    def __init__(self, platform_config=None):
        self.logger = get_logger(__name__)
        self.config = AppConfig()
        self.platform_config = platform_config
        self.main_window = None
        self.file_service = None
        self.theme_service = None
        
        self._initialize_services()
        self._create_main_window()
        self._setup_auto_save()
    
    def _initialize_services(self):
        """Initialize application services"""
        self.file_service = FileService()
        self.theme_service = ThemeService()
        
        # Apply theme
        theme_name = self.config.get('appearance', 'theme', 'dark')
        self.theme_service.apply_theme(theme_name)
    
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
