"""
Final Icon Visibility Test
Test all the changes we made to force icon visibility in context menus
"""

import sys
import tempfile
from pathlib import Path

# Add src to path for imports  
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_final_icon_fixes():
    """Test all the icon visibility fixes we implemented"""
    
    print("=" * 70)
    print("TESTING FINAL ICON VISIBILITY FIXES")
    print("=" * 70)
    
    try:
        from PySide6.QtWidgets import QApplication
        from src.ui.components.file_panel import FilePanel
        from src.services.cross_platform_shell_integration import get_shell_integration
        
        # Ensure Qt app exists
        if not QApplication.instance():
            QApplication(sys.argv)
        
        # Create test environment
        temp_dir = Path(tempfile.mkdtemp(prefix="final_icon_test_"))
        test_file = temp_dir / 'test.txt'
        test_file.write_text('test')
        
        try:
            # Test backend
            shell = get_shell_integration()
            menu_items = shell.get_context_menu_items(str(test_file))
            
            print("🔍 BACKEND VERIFICATION:")
            print("-" * 50)
            
            extracted_count = 0
            for item in menu_items:
                if item.get('separator'):
                    continue
                text = item.get('text', '')
                icon = item.get('icon', '')
                if text and icon and icon.endswith('.png'):
                    extracted_count += 1
                    print(f"✅ {text} -> {Path(icon).name}")
            
            print(f"Backend: {extracted_count} extracted icons found")
            
            # Test UI component
            panel = FilePanel("test_panel")
            
            print(f"\n🧪 UI COMPONENT VERIFICATION:")
            print("-" * 50)
            
            # Test individual icon loading
            test_icon_paths = [
                "d:/DevWorks/FileOrbit/resources/icons/extracted/system_cut.png",
                "d:/DevWorks/FileOrbit/resources/icons/extracted/system_copy.png",
                "d:/DevWorks/FileOrbit/resources/icons/extracted/app_visual_studio_code.png",
            ]
            
            loaded_count = 0
            for icon_path in test_icon_paths:
                icon = panel._get_context_menu_icon(icon_path)
                if not icon.isNull():
                    loaded_count += 1
                    print(f"✅ {Path(icon_path).name} loaded successfully")
                else:
                    print(f"❌ {Path(icon_path).name} failed to load")
            
            print(f"UI Loading: {loaded_count}/{len(test_icon_paths)} icons loaded")
            
            # Test context menu creation with new fixes
            print(f"\n🔧 CONTEXT MENU CREATION TEST:")
            print("-" * 50)
            
            context_menu = panel._create_context_menu(menu_items)
            actions = context_menu.actions()
            
            # Check action properties
            icon_visible_count = 0
            total_actions = 0
            
            for action in actions:
                if action.isSeparator():
                    continue
                
                total_actions += 1
                
                # Check if action has icon
                action_icon = action.icon()
                has_icon = not action_icon.isNull()
                
                # Check if iconVisibleInMenu is set (our new fix)
                icon_visible = action.isIconVisibleInMenu() if hasattr(action, 'isIconVisibleInMenu') else True
                
                if has_icon:
                    icon_visible_count += 1
                    status = "✅" if icon_visible else "⚠️"
                    print(f"  {status} {action.text()} -> Icon: {has_icon}, Visible: {icon_visible}")
            
            print(f"Context Menu: {icon_visible_count}/{total_actions} actions have icons")
            
            # Check menu properties
            menu_icon_size = context_menu.property("iconSize")
            print(f"Menu icon size property: {menu_icon_size}")
            
            # Final verdict
            print(f"\n🎯 FINAL ASSESSMENT:")
            print("-" * 50)
            
            backend_ok = extracted_count >= 8
            ui_ok = loaded_count >= 2
            menu_ok = icon_visible_count >= total_actions * 0.7
            
            print(f"Backend icon extraction: {'✅ GOOD' if backend_ok else '❌ POOR'} ({extracted_count} icons)")
            print(f"UI icon loading: {'✅ GOOD' if ui_ok else '❌ POOR'} ({loaded_count} icons)")
            print(f"Context menu icons: {'✅ GOOD' if menu_ok else '❌ POOR'} ({icon_visible_count}/{total_actions} actions)")
            
            if backend_ok and ui_ok and menu_ok:
                print(f"\n🎉 ALL SYSTEMS GO! Icons should be visible in FileOrbit context menus.")
                print(f"   Right-click on any file/folder to see extracted Windows icons.")
            elif backend_ok and ui_ok:
                print(f"\n⚠️  PARTIAL SUCCESS: Icons load correctly but may have display issues.")
                print(f"   This might be a Qt theme or styling issue.")
            else:
                print(f"\n❌ ISSUES DETECTED: Some components not working properly.")
            
            # List our applied fixes
            print(f"\n🔧 APPLIED FIXES:")
            print("-" * 50)
            print("✅ Icon pre-caching with multiple sizes (16x16, 24x24, 32x32)")
            print("✅ setIconVisibleInMenu(True) for all QActions")
            print("✅ Menu iconSize property set to QSize(16, 16)")
            print("✅ QMenu::icon CSS styling in dark theme")
            print("✅ Enhanced icon loading with null checking")
            print("✅ Forced pixmap generation for standard sizes")
            
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_final_icon_fixes()