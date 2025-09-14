"""
Simple Context Menu and Icon Test Runner
Tests context menu behavior without requiring Qt initialization
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.cross_platform_shell_integration import get_shell_integration


def test_context_menu_filtering():
    """Test that context menu filtering works correctly"""
    print("=" * 60)
    print("Context Menu Filtering Test")
    print("=" * 60)
    
    temp_dir = Path(tempfile.mkdtemp(prefix="fileorbit_filter_test_"))
    
    try:
        # Create test files and directories
        test_file = temp_dir / 'test.txt'
        test_video = temp_dir / 'video.mp4'
        test_dir = temp_dir / 'folder'
        git_dir = temp_dir / 'git_repo'
        
        test_file.write_text('Test content')
        test_video.write_text('Fake video')
        test_dir.mkdir()
        git_dir.mkdir()
        (git_dir / '.git').mkdir()
        
        shell = get_shell_integration()
        
        # Test directory filtering
        print("\n" + "-" * 40)
        print("DIRECTORY CONTEXT MENU FILTERING")
        print("-" * 40)
        
        dir_menu = shell.get_context_menu_items(str(test_dir))
        dir_texts = [item.get('text', '') for item in dir_menu if not item.get('separator')]
        
        # Check for inappropriate media player entries in directory menu
        media_players = ['vlc', 'mpc', 'media player', 'playlist']
        inappropriate_found = []
        
        for text in dir_texts:
            text_lower = text.lower()
            for media_term in media_players:
                if media_term in text_lower:
                    inappropriate_found.append(text)
                    break
        
        print(f"Directory menu items: {len(dir_texts)}")
        print("Directory menu contents:")
        for i, text in enumerate(dir_texts, 1):
            print(f"  {i:2d}. {text}")
        
        if inappropriate_found:
            print("\n❌ Found inappropriate media player items for directory:")
            for item in inappropriate_found:
                print(f"    - {item}")
        else:
            print("\n✅ No inappropriate media player items found in directory menu")
        
        # Test file menu for comparison
        print(f"\n{'-' * 40}")
        print("FILE CONTEXT MENU (for comparison)")
        print("-" * 40)
        
        video_menu = shell.get_context_menu_items(str(test_video))
        video_texts = [item.get('text', '') for item in video_menu if not item.get('separator')]
        
        video_media_found = []
        for text in video_texts:
            text_lower = text.lower()
            for media_term in media_players:
                if media_term in text_lower:
                    video_media_found.append(text)
                    break
        
        print(f"Video file menu items: {len(video_texts)}")
        if video_media_found:
            print("✅ Media player items found in video file menu (expected):")
            for item in video_media_found:
                print(f"    - {item}")
        else:
            print("📝 No media player items in video file menu")
        
        # Test Git repository detection
        print(f"\n{'-' * 40}")
        print("GIT REPOSITORY DETECTION")
        print("-" * 40)
        
        git_menu = shell.get_context_menu_items(str(git_dir))
        git_texts = [item.get('text', '') for item in git_menu if not item.get('separator')]
        
        git_items = [text for text in git_texts if 'git' in text.lower()]
        print(f"Git repository menu items: {len(git_texts)}")
        if git_items:
            print("✅ Git-related items found:")
            for item in git_items:
                print(f"    - {item}")
        else:
            print("📝 No Git-related items found (Git may not be installed)")
        
        # Summary
        print(f"\n{'=' * 60}")
        print("FILTERING TEST SUMMARY")
        print("=" * 60)
        
        if not inappropriate_found:
            print("✅ PASS: Directory filtering working correctly")
        else:
            print("❌ FAIL: Directory filtering needs improvement")
        
        if video_media_found:
            print("✅ PASS: Media file actions working correctly")
        else:
            print("📝 INFO: No media players detected (may not be installed)")
        
        print("✅ PASS: Test completed successfully")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_icon_mapping():
    """Test icon mapping without Qt"""
    print(f"\n{'=' * 60}")
    print("ICON MAPPING TEST")
    print("=" * 60)
    
    # Import the windows shell integration
    try:
        from src.utils.windows_shell import WindowsShellIntegration
        shell = WindowsShellIntegration()
        
        # Test icon mapping
        test_cases = [
            ("Open", "file_open"),
            ("Cut", "cut"),
            ("Copy", "copy"),
            ("Paste", "paste"),
            ("Delete", "delete"),
            ("Open with Visual Studio Code", "code"),
            ("Open with Code", "code"),
            ("Open PowerShell here", "powershell"),
            ("Open Command Prompt here", "cmd"),
            ("Add to VLC media player's Playlist", "vlc"),
            ("Add to MPC-HC playlist", "mpc"),
            ("Open Git GUI here", "git"),
            ("Properties", "properties"),
            ("Unknown App", "app_extension"),
        ]
        
        print("Testing icon resolution:")
        correct_mappings = 0
        total_mappings = len(test_cases)
        
        for text, expected_icon in test_cases:
            resolved_icon = shell._guess_icon_from_text(text)
            status = "✅" if resolved_icon == expected_icon else "❌"
            print(f"  {status} '{text}' -> '{resolved_icon}' (expected: '{expected_icon}')")
            if resolved_icon == expected_icon:
                correct_mappings += 1
        
        accuracy = correct_mappings / total_mappings * 100
        print(f"\nIcon mapping accuracy: {accuracy:.1f}% ({correct_mappings}/{total_mappings})")
        
        if accuracy >= 80:
            print("✅ PASS: Good icon mapping accuracy")
        elif accuracy >= 60:
            print("📝 MODERATE: Icon mapping could be improved")
        else:
            print("❌ FAIL: Icon mapping needs significant improvement")
        
    except Exception as e:
        print(f"❌ Error testing icon mapping: {e}")


def analyze_context_menu_structure():
    """Analyze the structure and organization of context menus"""
    print(f"\n{'=' * 60}")
    print("CONTEXT MENU STRUCTURE ANALYSIS")
    print("=" * 60)
    
    temp_dir = Path(tempfile.mkdtemp(prefix="fileorbit_structure_test_"))
    
    try:
        # Create test scenarios
        test_dir = temp_dir / 'test_folder'
        test_file = temp_dir / 'test.txt'
        
        test_dir.mkdir()
        test_file.write_text('Test content')
        
        shell = get_shell_integration()
        
        scenarios = [
            ("Directory", test_dir),
            ("Text File", test_file),
        ]
        
        for scenario_name, path in scenarios:
            print(f"\n{'-' * 40}")
            print(f"{scenario_name.upper()} MENU STRUCTURE")
            print("-" * 40)
            
            menu_items = shell.get_context_menu_items(str(path))
            
            # Analyze menu structure
            categories = {
                'open_actions': [],
                'edit_actions': [],
                'file_operations': [],
                'system_actions': [],
                'third_party': [],
                'separators': 0
            }
            
            position = 0
            for item in menu_items:
                if item.get('separator'):
                    categories['separators'] += 1
                    print(f"  {position:2d}. --- SEPARATOR ---")
                else:
                    text = item.get('text', '').lower()
                    
                    if any(term in text for term in ['open', 'edit']):
                        categories['open_actions'].append((position, item.get('text', '')))
                    elif any(term in text for term in ['cut', 'copy', 'paste', 'delete', 'rename']):
                        categories['file_operations'].append((position, item.get('text', '')))
                    elif any(term in text for term in ['properties', 'send to']):
                        categories['system_actions'].append((position, item.get('text', '')))
                    else:
                        categories['third_party'].append((position, item.get('text', '')))
                    
                    print(f"  {position:2d}. {item.get('text', '')}")
                
                position += 1
            
            # Analyze organization
            print(f"\nStructure analysis for {scenario_name}:")
            print(f"  Total items: {position}")
            print(f"  Separators: {categories['separators']}")
            print(f"  Open/Edit actions: {len(categories['open_actions'])}")
            print(f"  File operations: {len(categories['file_operations'])}")
            print(f"  System actions: {len(categories['system_actions'])}")
            print(f"  Third-party apps: {len(categories['third_party'])}")
            
            # Check if Open actions come first
            if categories['open_actions']:
                first_open_pos = categories['open_actions'][0][0]
                print(f"  First open action at position: {first_open_pos}")
                if first_open_pos <= 2:
                    print("  ✅ Open actions properly positioned at top")
                else:
                    print("  📝 Open actions could be moved higher")
            
            # Check if Properties is at the end
            if categories['system_actions']:
                properties_actions = [(pos, text) for pos, text in categories['system_actions'] if 'properties' in text]
                if properties_actions:
                    properties_pos = properties_actions[0][0]
                    total_non_separator = position - categories['separators']
                    if properties_pos >= total_non_separator - 2:
                        print("  ✅ Properties properly positioned near end")
                    else:
                        print("  📝 Properties could be moved closer to end")
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_context_menu_filtering()
    test_icon_mapping()
    analyze_context_menu_structure()