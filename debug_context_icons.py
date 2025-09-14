"""
Debug Context Menu Icon Display
Check why extracted icons aren't showing in the actual UI
"""

import sys
from pathlib import Path
import tempfile

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def debug_context_menu_display():
    """Debug why context menu icons aren't displaying correctly"""
    
    print("=" * 60)
    print("DEBUGGING CONTEXT MENU ICON DISPLAY")
    print("=" * 60)
    
    try:
        from PySide6.QtWidgets import QApplication, QMenu
        from PySide6.QtGui import QIcon
        
        # Create Qt application
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        from src.ui.components.file_panel import FilePanel
        from src.services.cross_platform_shell_integration import get_shell_integration
        
        # Create temporary test file
        temp_dir = Path(tempfile.mkdtemp(prefix="fileorbit_debug_"))
        test_file = temp_dir / 'test.txt'
        test_file.write_text('test')
        
        try:
            shell = get_shell_integration()
            panel = FilePanel("debug_panel")
            
            # Get context menu items from shell
            print("🔍 Getting context menu items from shell...")
            menu_items = shell.get_context_menu_items(str(test_file))
            
            print(f"Found {len(menu_items)} menu items\n")
            
            # Analyze each menu item
            for i, item in enumerate(menu_items):
                if item.get('separator'):
                    print(f"{i+1:2d}. [SEPARATOR]")
                    continue
                
                text = item.get('text', 'NO_TEXT')
                icon_name = item.get('icon', 'NO_ICON')
                
                print(f"{i+1:2d}. '{text}'")
                print(f"     Icon name: {icon_name}")
                
                # Test icon loading
                if icon_name and icon_name != 'NO_ICON':
                    try:
                        # Test the FilePanel icon method
                        icon = panel._get_context_menu_icon(icon_name)
                        
                        if icon.isNull():
                            print(f"     ❌ Icon is NULL")
                        else:
                            print(f"     ✅ Icon loaded successfully")
                            
                            # Check if it's a file path
                            if icon_name.endswith('.png') and ('\\' in icon_name or '/' in icon_name):
                                if Path(icon_name).exists():
                                    print(f"     📁 PNG file exists: {Path(icon_name).name}")
                                else:
                                    print(f"     ❌ PNG file missing: {icon_name}")
                            else:
                                print(f"     📋 Using fallback icon")
                                
                    except Exception as e:
                        print(f"     ❌ Error loading icon: {e}")
                else:
                    print(f"     📝 No icon specified")
                
                print()
            
            # Test actual menu creation
            print("🔧 Testing actual QMenu creation...")
            menu = panel._create_context_menu(menu_items)
            
            actions = menu.actions()
            icon_success = 0
            icon_total = 0
            
            for action in actions:
                if action.isSeparator():
                    continue
                
                icon_total += 1
                icon = action.icon()
                
                if not icon.isNull():
                    icon_success += 1
                    print(f"✅ '{action.text()}' has icon")
                else:
                    print(f"❌ '{action.text()}' NO ICON")
            
            print(f"\nMenu creation result: {icon_success}/{icon_total} actions have icons")
            
            # Test specific PNG loading
            print(f"\n🧪 Testing specific PNG loading...")
            icon_dir = Path("d:/DevWorks/FileOrbit/resources/icons/extracted")
            
            test_png = icon_dir / "system_cut.png"
            if test_png.exists():
                direct_icon = QIcon(str(test_png))
                if direct_icon.isNull():
                    print(f"❌ Direct PNG loading failed: {test_png}")
                else:
                    print(f"✅ Direct PNG loading works: {test_png.name}")
                    
                    # Test via FilePanel method
                    panel_icon = panel._get_context_menu_icon(str(test_png))
                    if panel_icon.isNull():
                        print(f"❌ FilePanel method failed for same PNG")
                    else:
                        print(f"✅ FilePanel method works for same PNG")
            else:
                print(f"❌ Test PNG not found: {test_png}")
        
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_context_menu_display()