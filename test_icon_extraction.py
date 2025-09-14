"""
Test Icon Extraction from Windows Context Menu
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.cross_platform_shell_integration import get_shell_integration
from src.utils.windows_icon_extractor import get_icon_extractor


def test_icon_extraction():
    """Test extracting icons from Windows context menu items"""
    print("=" * 60)
    print("Windows Icon Extraction Test")
    print("=" * 60)
    
    # Create test environment
    temp_dir = Path(tempfile.mkdtemp(prefix="fileorbit_icon_extraction_"))
    
    try:
        # Create test files
        test_file = temp_dir / 'test.txt'
        test_dir = temp_dir / 'test_folder'
        
        test_file.write_text('Test content')
        test_dir.mkdir()
        
        # Get shell integration
        shell = get_shell_integration()
        icon_extractor = get_icon_extractor()
        
        print(f"Icon extractor available: {icon_extractor is not None}")
        print(f"Cache directory: {icon_extractor.cache_dir if icon_extractor else 'None'}")
        
        # Test system icon extraction
        print(f"\n{'-' * 40}")
        print("SYSTEM ICON EXTRACTION")
        print("-" * 40)
        
        if icon_extractor:
            system_icons = ['cut', 'copy', 'paste', 'delete', 'properties', 'folder_open', 'file_open']
            
            for icon_name in system_icons:
                print(f"Extracting system icon: {icon_name}")
                icon_path = icon_extractor.get_system_icon(icon_name)
                if icon_path:
                    print(f"  ✅ Extracted to: {icon_path}")
                else:
                    print("  ❌ Failed to extract")
        
        # Test context menu with icon extraction
        print(f"\n{'-' * 40}")
        print("CONTEXT MENU WITH ICON EXTRACTION")
        print("-" * 40)
        
        file_menu = shell.get_context_menu_items(str(test_file))
        
        print(f"File context menu ({len(file_menu)} items):")
        for i, item in enumerate(file_menu, 1):
            if item.get('separator'):
                print(f"  {i:2d}. --- SEPARATOR ---")
            else:
                text = item.get('text', 'NO_TEXT')
                icon = item.get('icon', 'NO_ICON')
                extracted_icon = item.get('extracted_icon', 'NONE')
                
                print(f"  {i:2d}. {text}")
                print(f"      Icon: {icon}")
                if extracted_icon != 'NONE':
                    print(f"      Extracted: {extracted_icon}")
        
        # Test application icon extraction
        print(f"\n{'-' * 40}")
        print("APPLICATION ICON EXTRACTION")
        print("-" * 40)
        
        if icon_extractor:
            test_apps = [
                'Visual Studio Code',
                'Sublime Text',
                'Notepad++',
                'VLC Media Player',
                'Git',
                'PowerShell'
            ]
            
            for app_name in test_apps:
                print(f"Extracting icon for: {app_name}")
                icon_path = icon_extractor.get_application_icon(app_name)
                if icon_path:
                    print(f"  ✅ Extracted to: {icon_path}")
                else:
                    print("  📝 Not found or not installed")
        
        # Test icon cache status
        print(f"\n{'-' * 40}")
        print("ICON CACHE STATUS")
        print("-" * 40)
        
        if icon_extractor and icon_extractor.cache_dir.exists():
            cache_files = list(icon_extractor.cache_dir.glob("*.png"))
            print(f"Cached icons: {len(cache_files)}")
            for cache_file in cache_files:
                size_kb = cache_file.stat().st_size / 1024
                print(f"  - {cache_file.name} ({size_kb:.1f} KB)")
        else:
            print("No icon cache found")
        
        # Summary
        print(f"\n{'=' * 60}")
        print("ICON EXTRACTION SUMMARY")
        print("=" * 60)
        
        if icon_extractor:
            cache_count = len(list(icon_extractor.cache_dir.glob("*.png"))) if icon_extractor.cache_dir.exists() else 0
            print("✅ Icon extractor initialized successfully")
            print(f"📁 Cache directory: {icon_extractor.cache_dir}")
            print(f"🖼️  Cached icons: {cache_count}")
            
            if cache_count > 0:
                print("🎉 Icon extraction working - icons cached successfully!")
            else:
                print("📝 No icons cached yet - may need PowerShell or system access")
        else:
            print("❌ Icon extractor not available")
    
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_icon_extraction_performance():
    """Test performance of icon extraction"""
    print(f"\n{'=' * 60}")
    print("ICON EXTRACTION PERFORMANCE TEST")
    print("=" * 60)
    
    import time
    
    icon_extractor = get_icon_extractor()
    if not icon_extractor:
        print("❌ Icon extractor not available")
        return
    
    # Test system icon extraction performance
    system_icons = ['cut', 'copy', 'paste', 'delete', 'properties']
    
    print("Testing system icon extraction performance:")
    total_time = 0
    success_count = 0
    
    for icon_name in system_icons:
        start_time = time.time()
        icon_path = icon_extractor.get_system_icon(icon_name)
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        total_time += duration_ms
        
        if icon_path:
            success_count += 1
            print(f"  ✅ {icon_name}: {duration_ms:.1f}ms")
        else:
            print(f"  ❌ {icon_name}: {duration_ms:.1f}ms (failed)")
    
    avg_time = total_time / len(system_icons)
    success_rate = success_count / len(system_icons) * 100
    
    print("\nPerformance Results:")
    print(f"  Average extraction time: {avg_time:.1f}ms")
    print(f"  Success rate: {success_rate:.1f}% ({success_count}/{len(system_icons)})")
    print(f"  Total time: {total_time:.1f}ms")
    
    if avg_time < 100:
        print("  ✅ Performance: Excellent (under 100ms)")
    elif avg_time < 500:
        print("  📝 Performance: Good (under 500ms)")
    else:
        print("  ⚠️  Performance: Slow (over 500ms)")


if __name__ == "__main__":
    test_icon_extraction()
    test_icon_extraction_performance()