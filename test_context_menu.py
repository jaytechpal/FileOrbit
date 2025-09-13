#!/usr/bin/env python3
"""
Quick test script to verify context menu functionality
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ui.components.file_panel import FilePanel
from src.services.file_service import FileService


def test_context_menu():
    """Test context menu functionality"""
    app = QApplication(sys.argv)
    
    # Create file service
    file_service = FileService()
    
    # Create file panel
    panel = FilePanel(
        panel_id="test",
        file_service=file_service
    )
    
    # Navigate to a directory with some files
    test_dir = Path.home()
    panel.navigate_to(test_dir)
    
    # Show the panel
    panel.show()
    panel.resize(800, 600)
    
    print("FilePanel is now open. Right-click on files/folders to test context menu.")
    print("Context menu should include:")
    print("- Copy, Cut, Paste")
    print("- Delete")
    print("- Rename (for single selection)")
    print("- Properties")
    print("- Open/Open with system default")
    print("- New Folder/New File (on empty area)")
    print("- Refresh")
    print("- Show/Hide hidden files")
    print("\nPress Ctrl+C to close.")
    
    # Auto-close after 30 seconds for testing
    QTimer.singleShot(30000, app.quit)
    
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\nTest completed.")
        app.quit()


if __name__ == "__main__":
    test_context_menu()