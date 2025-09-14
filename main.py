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

from src.core.application import FileOrbitApplication
from src.utils.logger import setup_logger
from platform_config import get_platform_config, log_system_info


def main():
    """Main application entry point"""
    # Get platform configuration
    platform_config = get_platform_config()
    
    # Check system compatibility and log warnings
    if not platform_config.is_64bit:
        print("WARNING: FileOrbit is optimized for 64-bit systems.")
        print("Some features may be limited on 32-bit systems.")
    
    # Create QApplication with cross-platform settings
    app = QApplication(sys.argv)
    app.setApplicationName("FileOrbit")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("FileOrbit Team")
    
    # Note: Qt6 automatically handles high DPI scaling, so no manual setup needed
    
    # Setup logging early
    logger = setup_logger()
    logger.info(f"Starting FileOrbit application on {platform_config.platform_name}")
    
    # Log comprehensive system information for debugging
    log_system_info()
    
    # Load application icon with cross-platform resource management
    from src.utils.cross_platform_resources import get_resource_manager
    
    resource_manager = get_resource_manager()
    app_icon = resource_manager.load_icon('app_icon')
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)
    else:
        logger.warning("Application icon not found, using system default")
    
    # Initialize application with cross-platform support
    try:
        file_orbit = FileOrbitApplication(platform_config)
        file_orbit.show()
        
        logger.info("FileOrbit started successfully")
        
        # Start event loop
        exit_code = app.exec()
        logger.info(f"Application exited with code: {exit_code}")
        sys.exit(exit_code)
        
    except ImportError as e:
        logger.error(f"Missing dependencies: {e}")
        print(f"Error: Missing required dependencies: {e}")
        print("Please ensure all required packages are installed.")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        print(f"Error: Failed to start FileOrbit: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
