"""
Debug Context Menu Icon Display Issue
This test will help identify why extracted icons aren't showing in the UI
"""

import sys
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def debug_context_menu_icons():
    """Debug why icons aren't showing in the actual UI"""
    
    print("=" * 70)
    print("DEBUGGING CONTEXT MENU ICON DISPLAY ISSUE")
    print("=" * 70)
    
    # First, verify our backend is still working
    from src.services.cross_platform_shell_integration import get_shell_integration
    
    temp_dir = Path(tempfile.mkdtemp(prefix="debug_icons_"))
    test_file = temp_dir / 'test.txt'
    test_file.write_text('test')
    
    try:
        shell = get_shell_integration()
        menu_items = shell.get_context_menu_items(str(test_file))
        
        print("🔍 BACKEND ICON PATHS:")
        print("-" * 50)
        
        extracted_count = 0
        total_count = 0
        
        for item in menu_items:
            if item.get('separator'):
                continue
                
            text = item.get('text', '')
            icon = item.get('icon', '')
            
            if not text:
                continue
            
            total_count += 1
            is_extracted = icon and (icon.endswith('.png') and ('\\' in icon or '/' in icon))
            
            if is_extracted:
                extracted_count += 1
                icon_file = Path(icon)
                exists = "✅" if icon_file.exists() else "❌"
                print(f"  {exists} {text:<20} -> {icon_file.name}")
            else:
                print(f"  📝 {text:<20} -> {icon or 'NO_ICON'}")
        
        print(f"\nBackend Result: {extracted_count}/{total_count} items have extracted icons")
        
        # Now test the UI component loading
        print(f"\n🧪 UI COMPONENT TESTING:")
        print("-" * 50)
        
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import Qt
            
            # Ensure Qt app exists
            if not QApplication.instance():
                app = QApplication(sys.argv)
            
            from src.ui.components.file_panel import FilePanel
            
            # Create FilePanel
            panel = FilePanel("debug_panel")
            
            # Test the _get_context_menu_icon method with actual icon paths
            print("Testing _get_context_menu_icon method:")
            
            icon_tests = []
            for item in menu_items:
                if item.get('separator'):
                    continue
                    
                text = item.get('text', '')
                icon = item.get('icon', '')
                
                if text and icon:
                    icon_tests.append((text, icon))
            
            ui_success = 0
            ui_total = 0
            
            for text, icon_path in icon_tests[:8]:  # Test first 8
                ui_total += 1
                try:
                    qt_icon = panel._get_context_menu_icon(icon_path)
                    
                    if qt_icon.isNull():
                        print(f"  ❌ {text:<15} -> QIcon is NULL")
                    else:
                        ui_success += 1
                        if icon_path.endswith('.png'):
                            print(f"  ✅ {text:<15} -> PNG QIcon loaded")
                        else:
                            print(f"  📋 {text:<15} -> Fallback QIcon loaded")
                            
                except Exception as e:
                    print(f"  ❌ {text:<15} -> Error: {e}")
            
            print(f"\nUI Loading Result: {ui_success}/{ui_total} icons loaded as QIcon")
            
            # Test actual context menu creation
            print(f"\n🔧 CONTEXT MENU CREATION TEST:")
            print("-" * 50)
            
            try:
                context_menu = panel._create_context_menu(menu_items)
                actions = context_menu.actions()
                
                menu_icon_count = 0
                menu_total = 0
                
                for action in actions:
                    if action.isSeparator():
                        continue
                    
                    menu_total += 1
                    action_icon = action.icon()
                    action_text = action.text()
                    
                    if not action_icon.isNull():
                        menu_icon_count += 1
                        print(f"  ✅ {action_text:<15} -> Has QIcon")
                    else:
                        print(f"  ❌ {action_text:<15} -> No QIcon")
                
                print(f"\nContext Menu Result: {menu_icon_count}/{menu_total} actions have icons")
                
                # Summary and diagnosis
                print(f"\n🎯 DIAGNOSIS:")
                print("-" * 50)
                
                if extracted_count == 0:
                    print("❌ ISSUE: Backend not returning extracted icon paths")
                elif ui_success == 0:
                    print("❌ ISSUE: UI component can't load PNG files as QIcon")
                elif menu_icon_count == 0:
                    print("❌ ISSUE: Context menu creation not preserving icons")
                elif menu_icon_count < ui_success:
                    print("⚠️  ISSUE: Some icons lost during context menu creation")
                else:
                    print("✅ Icons should be working! Check for:")
                    print("   - Icon size/scaling issues")
                    print("   - Theme compatibility")
                    print("   - Qt style override")
                
            except Exception as e:
                print(f"❌ Context menu creation failed: {e}")
                import traceback
                traceback.print_exc()
                
        except ImportError as e:
            print(f"❌ Qt import failed: {e}")
        except Exception as e:
            print(f"❌ UI testing failed: {e}")
            import traceback
            traceback.print_exc()
    
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    debug_context_menu_icons()