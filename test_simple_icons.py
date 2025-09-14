"""
Simple Icon Test - Test if PNG icons can be loaded by Qt
"""

import sys
from pathlib import Path

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QIcon
    
    def test_png_icons():
        """Test if extracted PNG icons can be loaded by Qt"""
        
        # Create minimal Qt application
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        print("=" * 50)
        print("Testing PNG Icon Loading")
        print("=" * 50)
        
        # Test icon directory
        icon_dir = Path("d:/DevWorks/FileOrbit/resources/icons/extracted")
        
        if not icon_dir.exists():
            print("❌ Icon directory not found!")
            return
        
        icon_files = list(icon_dir.glob("*.png"))
        print(f"Found {len(icon_files)} PNG files")
        
        success = 0
        total = 0
        
        # Test first 5 icons
        for icon_file in sorted(icon_files)[:5]:
            total += 1
            icon = QIcon(str(icon_file))
            
            if not icon.isNull():
                success += 1
                print(f"✅ {icon_file.name}")
            else:
                print(f"❌ {icon_file.name}")
        
        print(f"\nResult: {success}/{total} icons loaded successfully")
        
        # Test file path detection
        print(f"\nTesting file path detection:")
        test_paths = [
            str(icon_dir / "system_cut.png"),
            "system_cut.png",  # Not a full path
            "cut",  # Just name
        ]
        
        for path in test_paths:
            is_file_path = path.endswith('.png') and ('\\' in path or '/' in path)
            print(f"  '{path}' -> File path: {is_file_path}")
            
            if is_file_path:
                if Path(path).exists():
                    print(f"    File exists: ✅")
                else:
                    print(f"    File exists: ❌")
    
    if __name__ == "__main__":
        test_png_icons()
        
except ImportError as e:
    print(f"Could not import Qt modules: {e}")
    print("This test requires PySide6 to be installed")