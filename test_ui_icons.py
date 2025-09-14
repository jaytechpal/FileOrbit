"""
Test Extracted Icon Loading in UI
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

def test_icon_loading():
    """Test if extracted icons can be loaded as QIcon objects"""
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    print("=" * 60)
    print("Testing Extracted Icon Loading in Qt")
    print("=" * 60)
    
    # Test icon directory
    icon_dir = Path("d:/DevWorks/FileOrbit/resources/icons/extracted")
    
    if not icon_dir.exists():
        print("❌ Icon directory not found!")
        return
    
    icon_files = list(icon_dir.glob("*.png"))
    print(f"Found {len(icon_files)} PNG icon files")
    
    successful_loads = 0
    failed_loads = 0
    
    for icon_file in sorted(icon_files)[:10]:  # Test first 10 icons
        icon = QIcon(str(icon_file))
        
        if not icon.isNull():
            successful_loads += 1
            print(f"✅ {icon_file.name} -> Loaded successfully")
        else:
            failed_loads += 1
            print(f"❌ {icon_file.name} -> Failed to load")
    
    print("\n📊 Results:")
    print(f"  Successfully loaded: {successful_loads}")
    print(f"  Failed to load: {failed_loads}")
    print(f"  Success rate: {successful_loads / (successful_loads + failed_loads) * 100:.1f}%")
    
    # Test the _get_context_menu_icon method
    print("\n🧪 Testing Context Menu Icon Method:")
    
    # Import the file panel to test the method
    try:
        from src.ui.components.file_panel import FilePanel
        from src.config.app_settings import AppSettings
        from src.services.cross_platform_shell_integration import get_shell_integration
        from platform_config import get_platform_config
        
        # Create minimal components for testing
        settings = AppSettings()
        shell = get_shell_integration()
        platform = get_platform_config()
        
        # Create a FilePanel instance
        panel = FilePanel(settings, shell, platform, Path.cwd())
        
        # Test loading extracted icons through the UI method
        test_icons = [
            str(icon_dir / "system_cut.png"),
            str(icon_dir / "system_copy.png"),
            str(icon_dir / "app_visual_studio_code.png"),
            "cut",  # fallback test
            "copy", # fallback test
        ]
        
        for test_icon in test_icons:
            try:
                result_icon = panel._get_context_menu_icon(test_icon)
                if not result_icon.isNull():
                    if test_icon.endswith('.png'):
                        print(f"✅ UI Method: {Path(test_icon).name} -> PNG icon loaded")
                    else:
                        print(f"📋 UI Method: {test_icon} -> Fallback icon loaded")
                else:
                    print(f"❌ UI Method: {test_icon} -> Failed")
            except Exception as e:
                print(f"❌ UI Method: {test_icon} -> Error: {e}")
        
    except Exception as e:
        print(f"❌ Could not test UI method: {e}")
    
    print("\n🎉 Test completed!")


if __name__ == "__main__":
    test_icon_loading()