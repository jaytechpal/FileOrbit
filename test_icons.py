"""
Test script to check available Qt standard icons
"""
import sys
from pathlib import Path

# Add the source directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QToolBar
from PySide6.QtGui import QAction

def test_icons():
    app = QApplication(sys.argv)
    widget = QWidget()
    
    toolbar = QToolBar()
    
    # Try different standard icons
    icon_names = [
        'SP_ArrowLeft', 'SP_ArrowRight', 'SP_ArrowUp', 'SP_ArrowDown',
        'SP_DialogDiscardButton', 'SP_DialogApplyButton', 'SP_DialogCancelButton',
        'SP_DirHomeIcon', 'SP_DirOpenIcon', 'SP_DirClosedIcon', 'SP_DirIcon',
        'SP_FileIcon', 'SP_TrashIcon', 'SP_BrowserReload',
        'SP_MediaPlay', 'SP_MediaStop', 'SP_MediaPause',
        'SP_CommandLink', 'SP_VistaShield'
    ]
    
    for icon_name in icon_names:
        try:
            if hasattr(toolbar.style(), icon_name):
                icon_enum = getattr(toolbar.style(), icon_name)
                icon = toolbar.style().standardIcon(icon_enum)
                print(f"✓ {icon_name} - Available")
            else:
                print(f"✗ {icon_name} - Not available")
        except Exception as e:
            print(f"✗ {icon_name} - Error: {e}")

if __name__ == "__main__":
    test_icons()
