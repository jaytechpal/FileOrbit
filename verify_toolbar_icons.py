#!/usr/bin/env python3
"""
Quick verification script to check if toolbar icons are working properly.
This script will help us verify that the Qt standard icons are being loaded correctly.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from ui.components.toolbar import NavigationToolbar

def main():
    app = QApplication(sys.argv)
    
    # Create a test window
    window = QMainWindow()
    window.setWindowTitle("Toolbar Icon Verification")
    window.setGeometry(100, 100, 800, 200)
    
    # Create central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    # Create layout
    layout = QVBoxLayout(central_widget)
    
    # Create toolbar instance
    toolbar = NavigationToolbar()
    layout.addWidget(toolbar)
    
    # Show the window
    window.show()
    
    print("=== Toolbar Icon Verification ===")
    print("✓ Application started successfully")
    print("✓ Toolbar created with Qt standard icons")
    print("✓ Check the toolbar for Back (←), Forward (→), and Up (↑) icons")
    print("✓ Icons should be visible as arrow symbols")
    print("\nIf you can see the navigation arrows, the fix is successful!")
    print("Close this window when done verifying.")
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
