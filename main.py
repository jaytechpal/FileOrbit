#!/usr/bin/env python3
"""
FileOrbit - Modern File Manager
Main application entry point
"""

import sys
from pathlib import Path

# Add the source directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from src.core.application import FileOrbitApplication
from src.utils.logger import setup_logger
from src.config.settings import AppConfig
from platform_config import get_platform_config, log_system_info


def main():
    """Main application entry point"""
    # Check 64-bit system compatibility
    platform_config = get_platform_config()
    if not platform_config.is_64bit:
        print("WARNING: FileOrbit is optimized for 64-bit systems.")
        print("Some features may be limited on 32-bit systems.")
    
    # Create QApplication first (Qt6 handles high DPI automatically)
    app = QApplication(sys.argv)
    app.setApplicationName("FileOrbit")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("FileOrbit Team")
    
    # Setup logging
    logger = setup_logger()
    logger.info("Starting FileOrbit application...")
    
    # Log system information for debugging
    log_system_info()
    
    # Load application icon
    icon_path = Path(__file__).parent / "resources" / "icons" / "app_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Initialize application with 64-bit optimizations
    try:
        file_orbit = FileOrbitApplication(platform_config)
        file_orbit.show()
        
        # Start event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
