"""
Test Icon Auto-Generation
Verify that extracted icons are properly regenerated when missing
"""

import sys
import shutil
import tempfile
from pathlib import Path

# Add project root to path
sys.path.append('.')

from src.utils.windows_icon_extractor import get_icon_extractor
from src.utils.logger import get_logger


def test_icon_auto_generation():
    """Test that icons are automatically generated when missing"""
    
    logger = get_logger(__name__)
    print("🧪 TESTING ICON AUTO-GENERATION")
    print("="*50)
    
    # Get the icon extractor
    extractor = get_icon_extractor()
    cache_dir = extractor.cache_dir
    
    print(f"📁 Icon cache directory: {cache_dir}")
    
    # Create a backup of existing icons
    backup_dir = None
    if cache_dir.exists() and any(cache_dir.iterdir()):
        backup_dir = Path(tempfile.mkdtemp()) / "icon_backup"
        shutil.copytree(cache_dir, backup_dir)
        print(f"💾 Backed up existing icons to: {backup_dir}")
    
    try:
        # Test 1: Clear cache and verify it's empty
        print("\n🧹 Step 1: Clearing icon cache...")
        extractor.clear_icon_cache()
        
        icon_count = len(list(cache_dir.glob("*.png"))) if cache_dir.exists() else 0
        print(f"   Icons after clearing: {icon_count}")
        
        # Test 2: Request a system icon (should auto-generate)
        print("\n🎯 Step 2: Requesting system icon (should auto-generate)...")
        system_icon = extractor.get_system_icon("cut")
        
        if system_icon:
            print(f"   ✅ System icon generated: {system_icon}")
        else:
            print(f"   ❌ Failed to generate system icon")
        
        # Test 3: Check cache directory
        print("\n📊 Step 3: Checking cache directory...")
        if cache_dir.exists():
            png_files = list(cache_dir.glob("*.png"))
            print(f"   Generated PNG files: {len(png_files)}")
            for png_file in png_files[:5]:  # Show first 5
                print(f"      - {png_file.name}")
            if len(png_files) > 5:
                print(f"      ... and {len(png_files)-5} more")
        else:
            print("   ❌ Cache directory doesn't exist")
        
        # Test 4: Verify cached path lookup works
        print("\n🔍 Step 4: Testing cached path lookup...")
        cached_path = extractor.get_cached_icon_path("system_cut")
        if cached_path and Path(cached_path).exists():
            print(f"   ✅ Cached path found: {cached_path}")
        else:
            print(f"   ⚠️  Cached path not found for system_cut")
        
        # Test 5: Test multiple system icons
        print("\n🎨 Step 5: Testing multiple system icons...")
        test_icons = ["copy", "delete", "properties", "folder"]
        generated_count = 0
        
        for icon_name in test_icons:
            icon_path = extractor.get_system_icon(icon_name)
            if icon_path:
                generated_count += 1
                print(f"   ✅ {icon_name} -> {Path(icon_path).name}")
            else:
                print(f"   ❌ {icon_name} -> Failed")
        
        print(f"\n📈 Generated {generated_count}/{len(test_icons)} system icons")
        
        # Final verification
        final_count = len(list(cache_dir.glob("*.png"))) if cache_dir.exists() else 0
        print(f"\n🎉 FINAL RESULT: {final_count} icons in cache")
        
        if final_count > 0:
            print("✅ SUCCESS: Icon auto-generation is working!")
            print("   The extracted icons directory can safely be in .gitignore")
            print("   because icons will be automatically generated as needed.")
            return True
        else:
            print("❌ FAILURE: No icons were generated")
            return False
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ ERROR: {e}")
        return False
        
    finally:
        # Restore backup if we made one
        if backup_dir and backup_dir.exists():
            print(f"\n🔄 Restoring original icons from backup...")
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
            shutil.copytree(backup_dir, cache_dir)
            shutil.rmtree(backup_dir, ignore_errors=True)
            print("✅ Original icons restored")


if __name__ == "__main__":
    success = test_icon_auto_generation()
    
    print("\n" + "="*50)
    if success:
        print("🎯 CONCLUSION: resources/icons/extracted/ should be in .gitignore")
        print("   ✅ Icons are automatically generated")
        print("   ✅ No need to track in version control")
        print("   ✅ Reduces repository size")
        print("   ✅ Avoids copyright/licensing issues")
    else:
        print("⚠️  MANUAL VERIFICATION NEEDED")
        print("   Check if icon generation is working properly")
    print("="*50)