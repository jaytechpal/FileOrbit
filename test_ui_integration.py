"""
Test UI Icon Loading with Forced Logging
"""

import sys
from pathlib import Path
import tempfile
import logging

# Set up logging to see debug messages
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_ui_icon_integration():
    """Test the full UI icon integration with debug output"""
    
    print("=" * 60)
    print("Testing UI Icon Integration with Debug Logging")
    print("=" * 60)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QIcon
        
        # Create Qt application
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        # Import FileOrbit components
        from src.ui.components.file_panel import FilePanel
        from src.services.cross_platform_shell_integration import get_shell_integration
        from platform_config import get_platform_config
        
        # Create minimal components
        shell = get_shell_integration()
        platform = get_platform_config()
        
        # Create a temporary directory for testing
        temp_dir = Path(tempfile.mkdtemp(prefix="fileorbit_ui_test_"))
        test_file = temp_dir / 'test.txt'
        test_file.write_text('test')
        
        try:
            # Create settings stub
            class MockSettings:
                def get_value(self, key, default=None):
                    return default
                
                def set_value(self, key, value):
                    pass
            
            settings = MockSettings()
            
            # Create FilePanel instance
            panel = FilePanel(settings, shell, platform, temp_dir)
            
            # Test the _get_context_menu_icon method directly
            print("\n🧪 Testing _get_context_menu_icon method:")
            print("-" * 50)
            
            test_icons = [
                # File paths to extracted icons
                str(Path("d:/DevWorks/FileOrbit/resources/icons/extracted/system_cut.png")),
                str(Path("d:/DevWorks/FileOrbit/resources/icons/extracted/app_visual_studio_code.png")),
                # Fallback names
                "cut",
                "copy",
                "delete",
                "code",
            ]
            
            for icon_name in test_icons:
                print(f"\nTesting icon: {icon_name}")
                try:
                    result_icon = panel._get_context_menu_icon(icon_name)
                    
                    if result_icon.isNull():
                        print(f"  ❌ Returned null icon")
                    else:
                        if icon_name.endswith('.png') and ('\\' in icon_name or '/' in icon_name):
                            if Path(icon_name).exists():
                                print(f"  ✅ Loaded PNG file successfully")
                            else:
                                print(f"  ❌ PNG file doesn't exist")
                        else:
                            print(f"  📋 Loaded fallback icon successfully")
                
                except Exception as e:
                    print(f"  ❌ Error: {e}")
            
            # Test context menu creation
            print(f"\n🔧 Testing context menu creation:")
            print("-" * 50)
            
            # Get context menu items from shell
            menu_items = shell.get_context_menu_items(str(test_file))
            
            # Create context menu using FilePanel method
            menu = panel._create_context_menu(menu_items)
            
            # Check the actions in the menu
            actions = menu.actions()
            icon_count = 0
            total_count = 0
            
            for action in actions:
                if action.isSeparator():
                    continue
                
                total_count += 1
                icon = action.icon()
                
                if not icon.isNull():
                    icon_count += 1
                    print(f"  ✅ '{action.text()}' has icon")
                else:
                    print(f"  📝 '{action.text()}' no icon")
            
            print(f"\nContext menu: {icon_count}/{total_count} actions have icons")
            
            if icon_count > total_count * 0.5:
                print("🎉 SUCCESS: Most context menu items have icons!")
            else:
                print("⚠️  Issue: Many context menu items missing icons")
        
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_ui_icon_integration()