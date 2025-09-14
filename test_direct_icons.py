"""
Direct Icon Method Test
Test the _get_context_menu_icon method directly
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_icon_method_directly():
    """Test the _get_context_menu_icon method directly"""
    
    print("=" * 50)
    print("Testing Icon Method Directly")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        
        # Create Qt application
        if not QApplication.instance():
            QApplication(sys.argv)
        
        # Import FilePanel
        from src.ui.components.file_panel import FilePanel
        
        # Create FilePanel with correct constructor
        panel = FilePanel("test_panel")
        
        # Test extracted icon paths
        icon_dir = Path("d:/DevWorks/FileOrbit/resources/icons/extracted")
        
        test_cases = [
            # Extracted system icons
            (str(icon_dir / "system_cut.png"), "System Cut Icon"),
            (str(icon_dir / "system_copy.png"), "System Copy Icon"),
            (str(icon_dir / "system_delete.png"), "System Delete Icon"),
            (str(icon_dir / "app_visual_studio_code.png"), "VS Code App Icon"),
            # Fallback names
            ("cut", "Cut Fallback"),
            ("copy", "Copy Fallback"),
            ("unknown", "Unknown Fallback"),
        ]
        
        success_count = 0
        total_count = len(test_cases)
        
        for icon_path, description in test_cases:
            try:
                icon = panel._get_context_menu_icon(icon_path)
                
                if icon.isNull():
                    print(f"❌ {description}: Null icon returned")
                else:
                    success_count += 1
                    if icon_path.endswith('.png'):
                        if Path(icon_path).exists():
                            print(f"✅ {description}: PNG loaded successfully")
                        else:
                            print(f"⚠️  {description}: PNG path doesn't exist")
                    else:
                        print(f"📋 {description}: Fallback icon loaded")
                        
            except Exception as e:
                print(f"❌ {description}: Error - {e}")
        
        print(f"\nResults: {success_count}/{total_count} icons loaded successfully")
        
        if success_count == total_count:
            print("🎉 All icons loaded successfully!")
        elif success_count >= total_count * 0.8:
            print("✅ Most icons loaded successfully!")
        else:
            print("⚠️  Some issues with icon loading")
        
        # Check if PNG files actually exist
        print(f"\n📁 Checking PNG files:")
        png_files = list(icon_dir.glob("*.png"))
        print(f"   Found {len(png_files)} PNG files in cache")
        
        for png_file in sorted(png_files)[:5]:  # Show first 5
            print(f"   📄 {png_file.name}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_icon_method_directly()