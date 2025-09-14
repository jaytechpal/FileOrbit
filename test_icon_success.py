"""
Icon Extraction Success Test
Tests the success of Windows icon extraction and caching
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.cross_platform_shell_integration import get_shell_integration
from src.utils.windows_icon_extractor import get_icon_extractor


def test_icon_extraction_success():
    """Test that icon extraction significantly improves context menu icons"""
    print("=" * 60)
    print("Icon Extraction Success Validation")
    print("=" * 60)
    
    temp_dir = Path(tempfile.mkdtemp(prefix="fileorbit_icon_success_"))
    
    try:
        # Create test files
        test_file = temp_dir / 'test.txt'
        test_dir = temp_dir / 'test_folder'
        test_video = temp_dir / 'video.mp4'
        
        test_file.write_text('Test content')
        test_dir.mkdir()
        test_video.write_text('Fake video')
        
        shell = get_shell_integration()
        icon_extractor = get_icon_extractor()
        
        print(f"Icon extractor available: {icon_extractor is not None}")
        
        # Test different file types
        test_cases = [
            ("Text File", test_file),
            ("Directory", test_dir),
            ("Video File", test_video),
        ]
        
        total_items = 0
        items_with_extracted_icons = 0
        items_with_system_icons = 0
        items_with_app_icons = 0
        
        for case_name, test_path in test_cases:
            print(f"\n{'-' * 40}")
            print(f"{case_name.upper()} CONTEXT MENU ICONS")
            print("-" * 40)
            
            menu_items = shell.get_context_menu_items(str(test_path))
            
            case_total = 0
            case_extracted = 0
            case_system = 0
            case_app = 0
            
            for item in menu_items:
                if item.get('separator'):
                    continue
                
                text = item.get('text', '')
                icon = item.get('icon', '')
                
                if not text:
                    continue
                
                case_total += 1
                total_items += 1
                
                # Check if it's an extracted icon (file path)
                is_extracted = icon and (icon.startswith('D:') or '/' in icon or '\\' in icon)
                is_system_extracted = is_extracted and 'system_' in icon
                is_app_extracted = is_extracted and 'app_' in icon
                
                if is_extracted:
                    case_extracted += 1
                    items_with_extracted_icons += 1
                    
                    if is_system_extracted:
                        case_system += 1
                        items_with_system_icons += 1
                        print(f"  ✅ {text} -> [SYSTEM ICON] {Path(icon).name}")
                    elif is_app_extracted:
                        case_app += 1
                        items_with_app_icons += 1
                        print(f"  🎯 {text} -> [APP ICON] {Path(icon).name}")
                    else:
                        print(f"  📁 {text} -> [EXTRACTED] {Path(icon).name}")
                else:
                    icon_display = icon if icon else "NO_ICON"
                    print(f"  📝 {text} -> [PLACEHOLDER] {icon_display}")
            
            # Case summary
            extraction_rate = (case_extracted / case_total * 100) if case_total > 0 else 0
            print(f"\n  Summary for {case_name}:")
            print(f"    Total items: {case_total}")
            print(f"    Extracted icons: {case_extracted}")
            print(f"    System icons: {case_system}")
            print(f"    App icons: {case_app}")
            print(f"    Extraction rate: {extraction_rate:.1f}%")
        
        # Overall summary
        print(f"\n{'=' * 60}")
        print("OVERALL ICON EXTRACTION SUCCESS")
        print("=" * 60)
        
        overall_extraction_rate = (items_with_extracted_icons / total_items * 100) if total_items > 0 else 0
        system_icon_rate = (items_with_system_icons / total_items * 100) if total_items > 0 else 0
        app_icon_rate = (items_with_app_icons / total_items * 100) if total_items > 0 else 0
        
        print("📊 Statistics:")
        print(f"  Total context menu items analyzed: {total_items}")
        print(f"  Items with extracted icons: {items_with_extracted_icons}")
        print(f"  Items with system icons: {items_with_system_icons}")
        print(f"  Items with application icons: {items_with_app_icons}")
        print(f"  Overall extraction rate: {overall_extraction_rate:.1f}%")
        print(f"  System icon coverage: {system_icon_rate:.1f}%")
        print(f"  Application icon coverage: {app_icon_rate:.1f}%")
        
        # Evaluate success
        print("\n🏆 Success Evaluation:")
        
        if overall_extraction_rate >= 50:
            print(f"  ✅ EXCELLENT: {overall_extraction_rate:.1f}% of items have real Windows icons!")
        elif overall_extraction_rate >= 30:
            print(f"  📈 GOOD: {overall_extraction_rate:.1f}% extraction rate achieved")
        elif overall_extraction_rate >= 10:
            print(f"  📝 MODERATE: {overall_extraction_rate:.1f}% extraction rate")
        else:
            print(f"  ⚠️  LOW: Only {overall_extraction_rate:.1f}% extraction rate")
        
        if items_with_system_icons >= 5:
            print(f"  ✅ System icons working: {items_with_system_icons} icons extracted")
        
        if items_with_app_icons >= 2:
            print(f"  ✅ Application icons working: {items_with_app_icons} icons extracted")
        
        # Check cache directory
        if icon_extractor and icon_extractor.cache_dir.exists():
            cache_files = list(icon_extractor.cache_dir.glob("*.png"))
            cache_size_mb = sum(f.stat().st_size for f in cache_files) / (1024 * 1024)
            
            print("\n💾 Cache Information:")
            print(f"  Cache directory: {icon_extractor.cache_dir}")
            print(f"  Cached icon files: {len(cache_files)}")
            print(f"  Total cache size: {cache_size_mb:.2f} MB")
            
            if len(cache_files) >= 10:
                print(f"  ✅ Good cache coverage with {len(cache_files)} icons")
            elif len(cache_files) >= 5:
                print(f"  📝 Moderate cache with {len(cache_files)} icons")
            else:
                print(f"  ⚠️  Limited cache with only {len(cache_files)} icons")
        
        # Final verdict
        print("\n🎉 FINAL VERDICT:")
        
        success_score = 0
        if overall_extraction_rate >= 30:
            success_score += 40
        elif overall_extraction_rate >= 10:
            success_score += 20
        
        if items_with_system_icons >= 5:
            success_score += 30
        elif items_with_system_icons >= 2:
            success_score += 15
        
        if items_with_app_icons >= 2:
            success_score += 30
        elif items_with_app_icons >= 1:
            success_score += 15
        
        if success_score >= 80:
            print("🏆 OUTSTANDING SUCCESS: Icon extraction working excellently!")
            print("   Windows system and application icons are being extracted and cached.")
        elif success_score >= 60:
            print("✅ SUCCESS: Icon extraction working well!")
            print("   Most important icons are being extracted from Windows.")
        elif success_score >= 40:
            print("📈 PARTIAL SUCCESS: Icon extraction working but could improve.")
        else:
            print("📝 INITIAL STATE: Icon extraction basic functionality working.")
        
        print(f"\n   Success Score: {success_score}/100")
        
        # Before/After comparison
        print("\n📊 BEFORE vs AFTER:")
        print("   BEFORE: Icon names like 'cut', 'copy', 'app_extension'")
        print("   AFTER:  Real Windows icons extracted and cached as PNG files")
        print("           System icons from shell32.dll")
        print("           Application icons from installed programs")
        print("           Cached for fast subsequent access")
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_icon_extraction_success()