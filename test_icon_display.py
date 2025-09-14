"""
Test Icon Display and QIcon Properties
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_qicon_properties():
    """Test QIcon properties and display"""
    
    print("=" * 60)
    print("Testing QIcon Properties and Display")
    print("=" * 60)
    
    try:
        from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QWidget, QPushButton
        from PySide6.QtGui import QIcon, QAction
        from PySide6.QtCore import QSize
        
        # Create Qt application
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Test loading icons
        icon_dir = Path("d:/DevWorks/FileOrbit/resources/icons/extracted")
        
        test_icons = [
            icon_dir / "system_cut.png",
            icon_dir / "system_copy.png",
            icon_dir / "app_visual_studio_code.png",
        ]
        
        for icon_path in test_icons:
            print(f"\n🔍 Testing: {icon_path.name}")
            
            if not icon_path.exists():
                print(f"  ❌ File doesn't exist")
                continue
            
            # Load as QIcon
            icon = QIcon(str(icon_path))
            
            print(f"  Icon null: {icon.isNull()}")
            
            # Check available sizes
            available_sizes = icon.availableSizes()
            print(f"  Available sizes: {[f'{s.width()}x{s.height()}' for s in available_sizes]}")
            
            # Get actual pixmap
            pixmap = icon.pixmap(QSize(16, 16))
            print(f"  16x16 pixmap null: {pixmap.isNull()}")
            print(f"  16x16 pixmap size: {pixmap.width()}x{pixmap.height()}")
            
            pixmap32 = icon.pixmap(QSize(32, 32))
            print(f"  32x32 pixmap null: {pixmap32.isNull()}")
            print(f"  32x32 pixmap size: {pixmap32.width()}x{pixmap32.height()}")
        
        # Create a test window to see if icons display
        print(f"\n🖼️  Creating test window to check icon display...")
        
        window = QMainWindow()
        window.setWindowTitle("Icon Display Test")
        window.resize(400, 300)
        
        # Create central widget
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create test menu
        menubar = window.menuBar()
        test_menu = menubar.addMenu("Test Icons")
        
        for icon_path in test_icons:
            if icon_path.exists():
                icon = QIcon(str(icon_path))
                action = QAction(f"Test {icon_path.stem}", window)
                action.setIcon(icon)
                test_menu.addAction(action)
        
        # Create test buttons with icons
        for icon_path in test_icons:
            if icon_path.exists():
                icon = QIcon(str(icon_path))
                button = QPushButton(f"Button {icon_path.stem}")
                button.setIcon(icon)
                button.setIconSize(QSize(24, 24))  # Force icon size
                layout.addWidget(button)
        
        window.show()
        print(f"  Test window created. Check if icons are visible.")
        print(f"  Close the window to continue...")
        
        # Run event loop briefly to show the window
        app.processEvents()
        
        # Don't exit immediately - let user see the window
        import time
        time.sleep(3)  # Show for 3 seconds
        
        window.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_qicon_properties()