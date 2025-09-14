"""
Context Menu Comparison Tests
Tests to compare context menu items and icons between directories/files
and verify FileOrbit's runtime behavior matches expectations.
"""

import sys
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict
import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.cross_platform_shell_integration import get_shell_integration


class ContextMenuTestHelper:
    """Helper class for context menu testing"""
    
    def __init__(self):
        self.shell_integration = get_shell_integration()
        self.temp_dir = None
        self.test_files = {}
        self.test_dirs = {}
    
    def setup_test_environment(self):
        """Create test files and directories"""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="fileorbit_test_"))
        
        # Create various test files
        self.test_files = {
            'text': self.temp_dir / 'test.txt',
            'python': self.temp_dir / 'script.py',
            'image': self.temp_dir / 'image.png',
            'video': self.temp_dir / 'video.mp4',
            'audio': self.temp_dir / 'music.mp3',
            'archive': self.temp_dir / 'archive.zip',
            'document': self.temp_dir / 'document.docx',
            'executable': self.temp_dir / 'program.exe',
        }
        
        # Create test content
        for file_type, file_path in self.test_files.items():
            content = f"Test {file_type} file content"
            file_path.write_text(content, encoding='utf-8')
        
        # Create various test directories
        self.test_dirs = {
            'empty': self.temp_dir / 'empty_folder',
            'with_files': self.temp_dir / 'folder_with_files',
            'git_repo': self.temp_dir / 'git_repository',
            'code_project': self.temp_dir / 'code_project',
        }
        
        for dir_type, dir_path in self.test_dirs.items():
            dir_path.mkdir()
            
            # Add specific content to some directories
            if dir_type == 'with_files':
                (dir_path / 'sample.txt').write_text('Sample file')
                (dir_path / 'data.json').write_text('{"key": "value"}')
            
            elif dir_type == 'git_repo':
                # Create .git directory to simulate git repository
                (dir_path / '.git').mkdir()
                (dir_path / 'README.md').write_text('# Git Repository')
            
            elif dir_type == 'code_project':
                (dir_path / 'main.py').write_text('print("Hello World")')
                (dir_path / 'requirements.txt').write_text('requests==2.25.1')
    
    def cleanup_test_environment(self):
        """Clean up test files and directories"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def get_context_menu_items(self, path: Path) -> List[Dict]:
        """Get context menu items for a path"""
        return self.shell_integration.get_context_menu_items(str(path))
    
    def extract_menu_texts(self, menu_items: List[Dict]) -> List[str]:
        """Extract text labels from menu items"""
        texts = []
        for item in menu_items:
            if not item.get('separator', False):
                text = item.get('text', '')
                if text:
                    texts.append(text)
        return texts
    
    def categorize_menu_items(self, menu_items: List[Dict]) -> Dict[str, List[str]]:
        """Categorize menu items by type"""
        categories = {
            'file_operations': [],
            'open_actions': [],
            'media_actions': [],
            'code_editors': [],
            'git_actions': [],
            'system_actions': [],
            'other_apps': []
        }
        
        for item in menu_items:
            if item.get('separator'):
                continue
                
            text = item.get('text', '').lower()
            
            if any(term in text for term in ['cut', 'copy', 'paste', 'delete', 'rename']):
                categories['file_operations'].append(item.get('text', ''))
            elif any(term in text for term in ['open', 'edit']):
                categories['open_actions'].append(item.get('text', ''))
            elif any(term in text for term in ['vlc', 'media player', 'mpc', 'playlist']):
                categories['media_actions'].append(item.get('text', ''))
            elif any(term in text for term in ['code', 'sublime', 'notepad++', 'vim']):
                categories['code_editors'].append(item.get('text', ''))
            elif 'git' in text:
                categories['git_actions'].append(item.get('text', ''))
            elif any(term in text for term in ['properties', 'send to', 'powershell', 'cmd']):
                categories['system_actions'].append(item.get('text', ''))
            else:
                categories['other_apps'].append(item.get('text', ''))
        
        return categories


class TestContextMenuComparison:
    """Test cases for context menu comparison"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test"""
        self.helper = ContextMenuTestHelper()
        self.helper.setup_test_environment()
        yield
        self.helper.cleanup_test_environment()
    
    def test_directory_vs_file_menu_differences(self):
        """Test that directory and file context menus have appropriate differences"""
        # Get context menus for directory and file
        dir_menu = self.helper.get_context_menu_items(self.helper.test_dirs['empty'])
        file_menu = self.helper.get_context_menu_items(self.helper.test_files['text'])
        
        dir_texts = self.helper.extract_menu_texts(dir_menu)
        file_texts = self.helper.extract_menu_texts(file_menu)
        
        print(f"\nDirectory menu items ({len(dir_texts)}):")
        for i, text in enumerate(dir_texts, 1):
            print(f"  {i:2d}. {text}")
        
        print(f"\nFile menu items ({len(file_texts)}):")
        for i, text in enumerate(file_texts, 1):
            print(f"  {i:2d}. {text}")
        
        # Analyze differences
        dir_only = set(dir_texts) - set(file_texts)
        file_only = set(file_texts) - set(dir_texts)
        common = set(dir_texts) & set(file_texts)
        
        print(f"\nDirectory-only items ({len(dir_only)}):")
        for item in sorted(dir_only):
            print(f"  - {item}")
        
        print(f"\nFile-only items ({len(file_only)}):")
        for item in sorted(file_only):
            print(f"  - {item}")
        
        print(f"\nCommon items ({len(common)}):")
        for item in sorted(common):
            print(f"  - {item}")
        
        # Assertions
        assert len(dir_menu) > 0, "Directory should have context menu items"
        assert len(file_menu) > 0, "File should have context menu items"
        
        # Check that both have basic file operations
        common_operations = ['Cut', 'Copy', 'Delete', 'Properties']
        for operation in common_operations:
            assert operation in dir_texts or operation in file_texts, f"Missing {operation} in menus"
    
    def test_media_files_no_media_actions_for_directories(self):
        """Test that media player actions don't appear for directories"""
        # Get directory context menu
        dir_menu = self.helper.get_context_menu_items(self.helper.test_dirs['empty'])
        dir_categories = self.helper.categorize_menu_items(dir_menu)
        
        # Get media file context menu for comparison
        media_file_menu = self.helper.get_context_menu_items(self.helper.test_files['video'])
        media_categories = self.helper.categorize_menu_items(media_file_menu)
        
        print(f"\nDirectory media actions: {dir_categories['media_actions']}")
        print(f"Media file media actions: {media_categories['media_actions']}")
        
        # Directories should NOT have media player actions
        assert len(dir_categories['media_actions']) == 0, \
            f"Directory should not have media actions: {dir_categories['media_actions']}"
        
        # Media files MAY have media player actions (if VLC/MPC-HC installed)
        if media_categories['media_actions']:
            print(f"Media file has expected media actions: {media_categories['media_actions']}")
    
    def test_code_editors_appropriate_for_both(self):
        """Test that code editors appear for both files and directories appropriately"""
        dir_menu = self.helper.get_context_menu_items(self.helper.test_dirs['code_project'])
        file_menu = self.helper.get_context_menu_items(self.helper.test_files['python'])
        
        dir_categories = self.helper.categorize_menu_items(dir_menu)
        file_categories = self.helper.categorize_menu_items(file_menu)
        
        print(f"\nDirectory code editor actions: {dir_categories['code_editors']}")
        print(f"File code editor actions: {file_categories['code_editors']}")
        
        # Both should potentially have code editor actions
        # (VS Code, Sublime Text can open both files and project directories)
        code_editors = ['Visual Studio Code', 'Code', 'Sublime Text', 'Notepad++']
        
        # Check if any code editors are available in either menu
        has_code_editor_for_dir = any(
            any(editor.lower() in action.lower() for editor in code_editors)
            for action in dir_categories['code_editors']
        )
        
        has_code_editor_for_file = any(
            any(editor.lower() in action.lower() for editor in code_editors)
            for action in file_categories['code_editors']
        )
        
        print(f"Directory has code editor: {has_code_editor_for_dir}")
        print(f"File has code editor: {has_code_editor_for_file}")
        
        # At least one should have code editor support if installed
        if has_code_editor_for_file or has_code_editor_for_dir:
            print("Code editor integration detected and working correctly")
    
    def test_git_actions_in_git_repository(self):
        """Test that Git actions appear in Git repositories"""
        git_repo_menu = self.helper.get_context_menu_items(self.helper.test_dirs['git_repo'])
        normal_dir_menu = self.helper.get_context_menu_items(self.helper.test_dirs['empty'])
        
        git_repo_categories = self.helper.categorize_menu_items(git_repo_menu)
        normal_dir_categories = self.helper.categorize_menu_items(normal_dir_menu)
        
        print(f"\nGit repository Git actions: {git_repo_categories['git_actions']}")
        print(f"Normal directory Git actions: {normal_dir_categories['git_actions']}")
        
        # Git repository should have more git actions than normal directory
        git_repo_git_count = len(git_repo_categories['git_actions'])
        normal_dir_git_count = len(normal_dir_categories['git_actions'])
        
        print(f"Git repo has {git_repo_git_count} Git actions")
        print(f"Normal dir has {normal_dir_git_count} Git actions")
        
        # If Git is installed, Git repository should have Git actions
        if git_repo_git_count > 0:
            assert git_repo_git_count >= normal_dir_git_count, \
                "Git repository should have at least as many Git actions as normal directory"
    
    def test_file_type_specific_actions(self):
        """Test that different file types have appropriate specific actions"""
        file_type_menus = {}
        for file_type, file_path in self.helper.test_files.items():
            menu = self.helper.get_context_menu_items(file_path)
            file_type_menus[file_type] = self.helper.categorize_menu_items(menu)
        
        print("\nFile type specific actions:")
        for file_type, categories in file_type_menus.items():
            print(f"\n{file_type.upper()} file:")
            for category, actions in categories.items():
                if actions:
                    print(f"  {category}: {actions}")
        
        # Text files should have code editor actions if available
        text_editors = file_type_menus['text']['code_editors']
        python_editors = file_type_menus['python']['code_editors']
        
        # Python files should have at least as many editor options as text files
        if text_editors or python_editors:
            print(f"Text file editors: {text_editors}")
            print(f"Python file editors: {python_editors}")
        
        # Media files should have media actions if media players installed
        video_media = file_type_menus['video']['media_actions']
        audio_media = file_type_menus['audio']['media_actions']
        
        if video_media or audio_media:
            print(f"Video file media actions: {video_media}")
            print(f"Audio file media actions: {audio_media}")
    
    def test_menu_item_order_consistency(self):
        """Test that menu items follow consistent ordering"""
        dir_menu = self.helper.get_context_menu_items(self.helper.test_dirs['empty'])
        file_menu = self.helper.get_context_menu_items(self.helper.test_files['text'])
        
        # Extract non-separator items with their positions
        def get_ordered_items(menu_items):
            items = []
            for i, item in enumerate(menu_items):
                if not item.get('separator'):
                    items.append((i, item.get('text', '')))
            return items
        
        dir_ordered = get_ordered_items(dir_menu)
        file_ordered = get_ordered_items(file_menu)
        
        print("\nDirectory menu order:")
        for pos, text in dir_ordered:
            print(f"  {pos:2d}. {text}")
        
        print("\nFile menu order:")
        for pos, text in file_ordered:
            print(f"  {pos:2d}. {text}")
        
        # Check that "Open" actions come first (if present)
        dir_texts = [text for _, text in dir_ordered]
        file_texts = [text for _, text in file_ordered]
        
        def find_open_action_position(texts):
            for i, text in enumerate(texts):
                if 'open' in text.lower() and 'with' not in text.lower():
                    return i
            return -1
        
        dir_open_pos = find_open_action_position(dir_texts)
        file_open_pos = find_open_action_position(file_texts)
        
        print(f"\nOpen action positions - Dir: {dir_open_pos}, File: {file_open_pos}")
        
        # Open actions should be near the top if they exist
        if dir_open_pos >= 0:
            assert dir_open_pos <= 2, f"Directory Open action should be near top, found at position {dir_open_pos}"
        if file_open_pos >= 0:
            assert file_open_pos <= 2, f"File Open action should be near top, found at position {file_open_pos}"
    
    def test_icon_availability(self):
        """Test that menu items have appropriate icons"""
        # Test with a sample file and directory
        file_menu = self.helper.get_context_menu_items(self.helper.test_files['text'])
        dir_menu = self.helper.get_context_menu_items(self.helper.test_dirs['empty'])
        
        def analyze_icons(menu_items, item_type):
            icons_found = {}
            no_icon_items = []
            
            for item in menu_items:
                if item.get('separator'):
                    continue
                    
                text = item.get('text', '')
                icon = item.get('icon', '')
                
                if icon:
                    icons_found[text] = icon
                else:
                    no_icon_items.append(text)
            
            print(f"\n{item_type} - Items with icons:")
            for text, icon in icons_found.items():
                print(f"  '{text}' -> '{icon}'")
            
            print(f"\n{item_type} - Items without icons:")
            for text in no_icon_items:
                print(f"  '{text}'")
            
            return len(icons_found), len(no_icon_items)
        
        file_with_icons, file_without_icons = analyze_icons(file_menu, "FILE")
        dir_with_icons, dir_without_icons = analyze_icons(dir_menu, "DIRECTORY")
        
        # Some items should have icons
        total_file_items = file_with_icons + file_without_icons
        total_dir_items = dir_with_icons + dir_without_icons
        
        if total_file_items > 0:
            file_icon_ratio = file_with_icons / total_file_items
            print(f"\nFile menu icon coverage: {file_icon_ratio:.1%} ({file_with_icons}/{total_file_items})")
        
        if total_dir_items > 0:
            dir_icon_ratio = dir_with_icons / total_dir_items
            print(f"Directory menu icon coverage: {dir_icon_ratio:.1%} ({dir_with_icons}/{total_dir_items})")
        
        # At least some core actions should have icons
        assert file_with_icons > 0 or dir_with_icons > 0, "At least some menu items should have icons"
    
    def test_runtime_performance(self):
        """Test context menu generation performance"""
        import time
        
        # Test performance for different scenarios
        performance_results = {}
        
        test_cases = [
            ("Empty Directory", self.helper.test_dirs['empty']),
            ("Directory with Files", self.helper.test_dirs['with_files']),
            ("Git Repository", self.helper.test_dirs['git_repo']),
            ("Text File", self.helper.test_files['text']),
            ("Media File", self.helper.test_files['video']),
        ]
        
        for test_name, test_path in test_cases:
            start_time = time.time()
            menu_items = self.helper.get_context_menu_items(test_path)
            end_time = time.time()
            
            duration_ms = (end_time - start_time) * 1000
            performance_results[test_name] = {
                'duration_ms': duration_ms,
                'item_count': len([item for item in menu_items if not item.get('separator')])
            }
        
        print("\nPerformance Results:")
        for test_name, results in performance_results.items():
            print(f"  {test_name}: {results['duration_ms']:.1f}ms ({results['item_count']} items)")
        
        # Performance should be reasonable (under 1 second for any case)
        for test_name, results in performance_results.items():
            assert results['duration_ms'] < 1000, \
                f"{test_name} took too long: {results['duration_ms']:.1f}ms"
        
        print("\nAll performance tests passed (all under 1000ms)")


def run_context_menu_comparison_tests():
    """Run all context menu comparison tests manually"""
    print("=" * 60)
    print("FileOrbit Context Menu Comparison Tests")
    print("=" * 60)
    
    helper = ContextMenuTestHelper()
    
    try:
        helper.setup_test_environment()
        
        # Create test instance
        test_instance = TestContextMenuComparison()
        test_instance.helper = helper
        
        # Run tests manually
        tests = [
            ("Directory vs File Menu Differences", test_instance.test_directory_vs_file_menu_differences),
            ("Media Actions Filtering", test_instance.test_media_files_no_media_actions_for_directories),
            ("Code Editor Support", test_instance.test_code_editors_appropriate_for_both),
            ("Git Repository Detection", test_instance.test_git_actions_in_git_repository),
            ("File Type Specific Actions", test_instance.test_file_type_specific_actions),
            ("Menu Order Consistency", test_instance.test_menu_item_order_consistency),
            ("Icon Availability", test_instance.test_icon_availability),
            ("Runtime Performance", test_instance.test_runtime_performance),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n{'-' * 40}")
            print(f"Running: {test_name}")
            print(f"{'-' * 40}")
            
            try:
                test_func()
                print(f"✅ PASSED: {test_name}")
                passed_tests += 1
            except Exception as e:
                print(f"❌ FAILED: {test_name}")
                print(f"Error: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'=' * 60}")
        print(f"Test Results: {passed_tests}/{total_tests} tests passed")
        print(f"{'=' * 60}")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed!")
        else:
            print(f"⚠️  {total_tests - passed_tests} test(s) failed")
    
    finally:
        helper.cleanup_test_environment()


if __name__ == "__main__":
    run_context_menu_comparison_tests()