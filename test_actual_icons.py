"""
Test Context Menu Icons Actually Being Used
"""

import sys
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.cross_platform_shell_integration import get_shell_integration

def test_actual_context_menu_icons():
    """Test what icons are actually returned by the context menu"""
    
    print("=" * 60)
    print("Testing Actual Context Menu Icon Paths")
    print("=" * 60)
    
    temp_dir = Path(tempfile.mkdtemp(prefix="fileorbit_icon_test_"))
    
    try:
        # Create test files
        test_file = temp_dir / 'test.txt'
        test_dir = temp_dir / 'test_folder'
        
        test_file.write_text('Test content')
        test_dir.mkdir()
        
        shell = get_shell_integration()
        
        print("🔍 FILE CONTEXT MENU ICONS:")
        print("-" * 40)
        
        file_menu = shell.get_context_menu_items(str(test_file))
        
        extracted_icons = 0
        total_icons = 0
        
        for item in file_menu:
            if item.get('separator'):
                continue
                
            text = item.get('text', '')
            icon = item.get('icon', '')
            
            if not text:
                continue
            
            total_icons += 1
            
            # Check if it's an extracted icon (file path)
            is_extracted = icon and (icon.endswith('.png') and ('\\' in icon or '/' in icon))
            
            if is_extracted:
                extracted_icons += 1
                icon_name = Path(icon).name
                print(f"  ✅ {text:<20} -> {icon_name}")
            else:
                print(f"  📝 {text:<20} -> {icon or 'NO_ICON'}")
        
        print(f"\nFile menu: {extracted_icons}/{total_icons} items use extracted icons")
        
        print(f"\n🔍 DIRECTORY CONTEXT MENU ICONS:")
        print("-" * 40)
        
        dir_menu = shell.get_context_menu_items(str(test_dir))
        
        extracted_icons_dir = 0
        total_icons_dir = 0
        
        for item in dir_menu:
            if item.get('separator'):
                continue
                
            text = item.get('text', '')
            icon = item.get('icon', '')
            
            if not text:
                continue
            
            total_icons_dir += 1
            
            # Check if it's an extracted icon (file path)
            is_extracted = icon and (icon.endswith('.png') and ('\\' in icon or '/' in icon))
            
            if is_extracted:
                extracted_icons_dir += 1
                icon_name = Path(icon).name
                print(f"  ✅ {text:<20} -> {icon_name}")
            else:
                print(f"  📝 {text:<20} -> {icon or 'NO_ICON'}")
        
        print(f"\nDirectory menu: {extracted_icons_dir}/{total_icons_dir} items use extracted icons")
        
        # Overall summary
        total_extracted = extracted_icons + extracted_icons_dir
        total_all = total_icons + total_icons_dir
        percentage = (total_extracted / total_all * 100) if total_all > 0 else 0
        
        print(f"\n🎯 SUMMARY:")
        print(f"  Total extracted icons: {total_extracted}/{total_all} ({percentage:.1f}%)")
        
        if percentage >= 70:
            print("  🏆 EXCELLENT: Most items use extracted Windows icons!")
        elif percentage >= 50:
            print("  ✅ GOOD: Many items use extracted Windows icons!")
        elif percentage >= 25:
            print("  📈 MODERATE: Some items use extracted Windows icons")
        else:
            print("  📝 LOW: Few items use extracted Windows icons")
        
        # Test specific system icons that should be extracted
        print(f"\n🔧 SYSTEM ICON CHECK:")
        system_tests = ['Cut', 'Copy', 'Delete', 'Properties', 'Rename']
        
        for item in file_menu:
            text = item.get('text', '')
            icon = item.get('icon', '')
            
            if text in system_tests:
                is_extracted = icon and (icon.endswith('.png') and ('\\' in icon or '/' in icon))
                if is_extracted:
                    print(f"  ✅ {text} uses extracted icon: {Path(icon).name}")
                else:
                    print(f"  ❌ {text} uses fallback: {icon}")
    
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_actual_context_menu_icons()