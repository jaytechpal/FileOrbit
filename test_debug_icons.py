"""
Debug Icon Mapping Test
Debug why system icons aren't being mapped correctly
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.windows_icon_extractor import get_icon_extractor


def debug_icon_mapping():
    """Debug icon mapping for system commands"""
    print("=" * 60)
    print("DEBUG: Icon Mapping Analysis")
    print("=" * 60)
    
    icon_extractor = get_icon_extractor()
    
    if not icon_extractor:
        print("❌ No icon extractor available")
        return
    
    # Test system icon mappings
    system_tests = [
        ('cut', 'system_cut'),
        ('copy', 'system_copy'),
        ('paste', 'system_paste'),
        ('delete', 'system_delete'),
        ('rename', 'system_rename'),
        ('properties', 'system_properties'),
        ('send to', 'system_send_to'),
        ('shortcut', 'system_shortcut'),
        ('open', 'system_file_open'),
        ('folder', 'system_folder_open'),
    ]
    
    print("\n🔍 SYSTEM ICON MAPPING TEST:")
    print("-" * 40)
    
    for text, expected_icon in system_tests:
        cached_path = icon_extractor.get_cached_icon_path(expected_icon)
        
        if cached_path:
            print(f"✅ '{text}' -> {expected_icon}.png -> {Path(cached_path).name}")
        else:
            print(f"❌ '{text}' -> {expected_icon}.png -> NOT FOUND")
    
    # List all cached icons
    print("\n📂 CACHED ICONS:")
    print("-" * 40)
    
    if icon_extractor.cache_dir.exists():
        cached_files = list(icon_extractor.cache_dir.glob("*.png"))
        
        system_icons = [f for f in cached_files if f.name.startswith('system_')]
        app_icons = [f for f in cached_files if f.name.startswith('app_')]
        exe_icons = [f for f in cached_files if f.name.startswith('exe_')]
        
        print(f"System icons ({len(system_icons)}):")
        for icon in sorted(system_icons):
            print(f"  📋 {icon.name}")
        
        print(f"\nApplication icons ({len(app_icons)}):")
        for icon in sorted(app_icons):
            print(f"  🎯 {icon.name}")
        
        print(f"\nExecutable icons ({len(exe_icons)}):")
        for icon in sorted(exe_icons):
            print(f"  📁 {icon.name}")
        
        print(f"\nTotal cached icons: {len(cached_files)}")
    
    # Test the _get_extracted_icon_for_text method directly
    print("\n🧪 DIRECT METHOD TEST:")
    print("-" * 40)
    
    from src.utils.windows_shell import WindowsShellIntegration
    
    shell = WindowsShellIntegration()
    
    test_texts = ['Cut', 'Copy', 'Paste', 'Delete', 'Properties', 'Open with Code', 'Git GUI']
    
    for text in test_texts:
        extracted_icon = shell._get_extracted_icon_for_text(text.lower())
        
        if extracted_icon:
            icon_name = Path(extracted_icon).name
            print(f"✅ '{text}' -> {icon_name}")
        else:
            print(f"❌ '{text}' -> NO EXTRACTED ICON")


if __name__ == "__main__":
    debug_icon_mapping()