"""
Icon Resolution Test for Context Menu Items
Tests icon detection and resolution for different context menu items
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.cross_platform_shell_integration import get_shell_integration


def test_icon_resolution():
    """Test icon resolution for different menu items"""
    print("=" * 60)
    print("FileOrbit Icon Resolution Test")
    print("=" * 60)
    
    # Create test environment
    temp_dir = Path(tempfile.mkdtemp(prefix="fileorbit_icon_test_"))
    
    try:
        # Create test files
        test_files = {
            'text': temp_dir / 'test.txt',
            'python': temp_dir / 'script.py', 
            'video': temp_dir / 'video.mp4',
            'image': temp_dir / 'image.png',
        }
        
        for file_type, file_path in test_files.items():
            file_path.write_text(f"Test {file_type} content")
        
        # Create test directory
        test_dir = temp_dir / 'test_folder'
        test_dir.mkdir()
        
        # Get shell integration
        shell = get_shell_integration()
        
        # Test directory context menu icons
        print("\n" + "-" * 40)
        print("DIRECTORY CONTEXT MENU ICONS")
        print("-" * 40)
        
        dir_menu = shell.get_context_menu_items(str(test_dir))
        analyze_menu_icons(dir_menu, "Directory")
        
        # Test file context menu icons
        for file_type, file_path in test_files.items():
            print(f"\n{'-' * 40}")
            print(f"{file_type.upper()} FILE CONTEXT MENU ICONS")
            print("-" * 40)
            
            file_menu = shell.get_context_menu_items(str(file_path))
            analyze_menu_icons(file_menu, f"{file_type} file")
        
        # Test icon resolution through FilePanel
        print(f"\n{'-' * 40}")
        print("FILEPANEL ICON RESOLUTION TEST")
        print("-" * 40)
        
        test_icon_resolution_methods()
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


def analyze_menu_icons(menu_items, item_type):
    """Analyze icons in a context menu"""
    icons_by_category = {
        'with_icon': [],
        'without_icon': [],
        'default_icons': [],
        'app_specific_icons': []
    }
    
    for item in menu_items:
        if item.get('separator'):
            continue
        
        text = item.get('text', '')
        icon = item.get('icon', '')
        action = item.get('action', '')
        
        if not text:
            continue
        
        if icon:
            icons_by_category['with_icon'].append((text, icon))
            
            # Categorize icon types
            if icon in ['file_open', 'folder_open', 'cut', 'copy', 'paste', 'delete', 'rename', 'properties']:
                icons_by_category['default_icons'].append((text, icon))
            else:
                icons_by_category['app_specific_icons'].append((text, icon))
        else:
            icons_by_category['without_icon'].append((text, action))
    
    # Print analysis
    print(f"{item_type} menu analysis:")
    print(f"  Total items: {len(icons_by_category['with_icon']) + len(icons_by_category['without_icon'])}")
    print(f"  With icons: {len(icons_by_category['with_icon'])}")
    print(f"  Without icons: {len(icons_by_category['without_icon'])}")
    
    if icons_by_category['with_icon']:
        print("\n  Items WITH icons:")
        for text, icon in icons_by_category['with_icon']:
            print(f"    '{text}' -> '{icon}'")
    
    if icons_by_category['without_icon']:
        print("\n  Items WITHOUT icons:")
        for text, action in icons_by_category['without_icon']:
            print(f"    '{text}' (action: {action})")
    
    # Check icon resolution quality
    total_items = len(icons_by_category['with_icon']) + len(icons_by_category['without_icon'])
    if total_items > 0:
        icon_coverage = len(icons_by_category['with_icon']) / total_items * 100
        print(f"\n  Icon coverage: {icon_coverage:.1f}%")
        
        if icon_coverage < 50:
            print("  ⚠️  Low icon coverage - consider adding more icon mappings")
        elif icon_coverage < 80:
            print("  📝 Moderate icon coverage - room for improvement")
        else:
            print("  ✅ Good icon coverage")


def test_icon_resolution_methods():
    """Test different icon resolution methods"""
    # Test common context menu text patterns
    test_cases = [
        # Standard Windows actions
        ("Open", "file_open"),
        ("Cut", "cut"),
        ("Copy", "copy"),
        ("Paste", "paste"),
        ("Delete", "delete"),
        ("Rename", "rename"),
        ("Properties", "properties"),
        
        # Code editors
        ("Open with Visual Studio Code", "code"),
        ("Open with Code", "code"),
        ("Open with Sublime Text", "editor"),
        ("Edit with Notepad++", "notepad"),
        
        # Development tools
        ("Open PowerShell here", "powershell"),
        ("Open Command Prompt here", "cmd"),
        ("Open Git Bash here", "git"),
        ("Open Git GUI here", "git"),
        
        # Media applications  
        ("Add to VLC media player's Playlist", "vlc"),
        ("Play with VLC media player", "vlc"),
        ("Add to MPC-HC playlist", "mpc"),
        
        # System actions
        ("Send to", "send_to"),
        ("Compressed (zipped) folder", "archive"),
        ("7-Zip", "archive"),
        
        # Unknown/custom applications
        ("Some Custom App", "app_extension"),
        ("Unknown Application", "app_extension"),
    ]
    
    print("Testing icon resolution for common context menu items:")
    print()
    
    # Import the icon resolution function
    try:
        from src.ui.components.file_panel import FilePanel
        # Create a dummy FilePanel instance to access the method
        panel = FilePanel(None)
        
        for text, expected_icon in test_cases:
            resolved_icon = panel._guess_icon_from_text(text)
            status = "✅" if resolved_icon == expected_icon else "❌"
            print(f"  {status} '{text}' -> '{resolved_icon}' (expected: '{expected_icon}')")
            
    except Exception as e:
        print(f"Error testing icon resolution: {e}")
        
        # Fallback: test the icon guessing logic directly from windows_shell
        try:
            from src.utils.windows_shell import WindowsShellIntegration
            shell = WindowsShellIntegration()
            
            print("Testing with WindowsShellIntegration._guess_icon_from_text:")
            for text, expected_icon in test_cases:
                resolved_icon = shell._guess_icon_from_text(text)
                status = "✅" if resolved_icon == expected_icon else "❌"
                print(f"  {status} '{text}' -> '{resolved_icon}' (expected: '{expected_icon}')")
                
        except Exception as e2:
            print(f"Error with fallback icon resolution test: {e2}")


def test_context_menu_runtime_comparison():
    """Test context menu generation in runtime vs expectations"""
    print(f"\n{'=' * 60}")
    print("RUNTIME CONTEXT MENU COMPARISON")
    print("=" * 60)
    
    temp_dir = Path(tempfile.mkdtemp(prefix="fileorbit_runtime_test_"))
    
    try:
        # Create test scenarios
        scenarios = {
            'empty_dir': temp_dir / 'empty',
            'code_project': temp_dir / 'project',
            'media_file': temp_dir / 'video.mp4',
            'text_file': temp_dir / 'readme.txt',
        }
        
        # Setup scenarios
        scenarios['empty_dir'].mkdir()
        
        scenarios['code_project'].mkdir()
        (scenarios['code_project'] / 'main.py').write_text('print("Hello")')
        (scenarios['code_project'] / '.git').mkdir()
        
        scenarios['media_file'].write_text('fake video content')
        scenarios['text_file'].write_text('This is a text file')
        
        shell = get_shell_integration()
        
        # Expected behaviors
        expectations = {
            'empty_dir': {
                'should_have': ['Open', 'Cut', 'Copy', 'Delete', 'Properties'],
                'should_not_have': ['VLC', 'media player', 'playlist'],
                'may_have': ['Code', 'PowerShell', 'Git']
            },
            'code_project': {
                'should_have': ['Open', 'Cut', 'Copy', 'Delete', 'Properties'],
                'should_not_have': ['VLC', 'media player', 'playlist'],  
                'may_have': ['Code', 'Git', 'PowerShell', 'Sublime']
            },
            'media_file': {
                'should_have': ['Open', 'Cut', 'Copy', 'Delete', 'Properties'],
                'should_not_have': [],  # Media files can have media player actions
                'may_have': ['VLC', 'media player', 'Code', 'Notepad']
            },
            'text_file': {
                'should_have': ['Open', 'Cut', 'Copy', 'Delete', 'Properties'],
                'should_not_have': [],  # Text files are versatile
                'may_have': ['Code', 'Notepad', 'Sublime', 'WordPad']
            }
        }
        
        # Test each scenario
        for scenario_name, scenario_path in scenarios.items():
            print(f"\n{'-' * 40}")
            print(f"Testing: {scenario_name.upper()}")
            print(f"Path: {scenario_path}")
            print("-" * 40)
            
            menu_items = shell.get_context_menu_items(str(scenario_path))
            menu_texts = [item.get('text', '') for item in menu_items if not item.get('separator')]
            
            expectation = expectations[scenario_name]
            
            print(f"Generated {len(menu_texts)} context menu items:")
            for i, text in enumerate(menu_texts, 1):
                print(f"  {i:2d}. {text}")
            
            # Check expectations
            print("\n📋 Expectation Analysis:")
            
            # Should have
            missing_required = []
            for required_item in expectation['should_have']:
                found = any(required_item.lower() in text.lower() for text in menu_texts)
                status = "✅" if found else "❌"
                print(f"  {status} Should have '{required_item}': {'Found' if found else 'MISSING'}")
                if not found:
                    missing_required.append(required_item)
            
            # Should not have  
            unwanted_found = []
            for unwanted_item in expectation['should_not_have']:
                found = any(unwanted_item.lower() in text.lower() for text in menu_texts)
                status = "❌" if found else "✅"
                print(f"  {status} Should NOT have '{unwanted_item}': {'FOUND' if found else 'Correctly absent'}")
                if found:
                    unwanted_found.append(unwanted_item)
            
            # May have (optional)
            optional_found = []
            for optional_item in expectation['may_have']:
                found = any(optional_item.lower() in text.lower() for text in menu_texts)
                status = "📝" if found else "⚪"
                print(f"  {status} May have '{optional_item}': {'Found' if found else 'Not found'}")
                if found:
                    optional_found.append(optional_item)
            
            # Summary
            print(f"\n📊 Summary for {scenario_name}:")
            print(f"  Required items missing: {len(missing_required)}")
            print(f"  Unwanted items found: {len(unwanted_found)}")
            print(f"  Optional items found: {len(optional_found)}")
            
            if missing_required:
                print(f"  ⚠️  Missing: {', '.join(missing_required)}")
            if unwanted_found:
                print(f"  ❌ Unwanted: {', '.join(unwanted_found)}")
            if optional_found:
                print(f"  ✨ Optional found: {', '.join(optional_found)}")
            
            if not missing_required and not unwanted_found:
                print("  🎉 All expectations met!")
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_icon_resolution()
    test_context_menu_runtime_comparison()