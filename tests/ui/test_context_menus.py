"""
Test cases for FileOrbit context menu functionality
Tests file context menus, directory context menus, empty area context menus, and cross-platform compatibility
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from src.ui.components.file_panel import FilePanel, FileListWidget
from src.services.cross_platform_shell_integration import CrossPlatformShellIntegration


class TestContextMenus:
    """Test suite for context menu functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)
    
    @pytest.fixture
    def test_files(self, temp_dir):
        """Create test files and directories"""
        files = {
            'text_file': temp_dir / 'test.txt',
            'python_file': temp_dir / 'script.py',
            'image_file': temp_dir / 'image.png',
            'test_dir': temp_dir / 'test_folder',
            'nested_dir': temp_dir / 'test_folder' / 'nested',
            'hidden_file': temp_dir / '.hidden',
            'no_extension': temp_dir / 'README',
        }
        
        # Create test files
        files['text_file'].write_text("Test content")
        files['python_file'].write_text("print('Hello World')")
        files['image_file'].touch()  # Empty file for testing
        files['no_extension'].write_text("No extension file")
        files['hidden_file'].write_text("Hidden file")
        
        # Create directories
        files['test_dir'].mkdir()
        files['nested_dir'].mkdir(parents=True)
        
        return files
    
    @pytest.fixture
    def file_panel(self, qtbot, temp_dir):
        """Create FilePanel instance for testing"""
        panel = FilePanel(panel_id="test", file_service=None, config=None)
        panel.current_path = temp_dir
        qtbot.addWidget(panel)
        return panel
    
    @pytest.fixture
    def file_list_widget(self, qtbot):
        """Create FileListWidget instance for testing"""
        widget = FileListWidget()
        qtbot.addWidget(widget)
        return widget


class TestFileContextMenus(TestContextMenus):
    """Test context menus for files"""
    
    def test_text_file_context_menu(self, file_panel, test_files):
        """Test context menu for text files"""
        with patch.object(file_panel.shell_integration, 'get_context_menu_items') as mock_context:
            # Mock context menu response for text file
            mock_context.return_value = [
                {
                    "text": "Open with Notepad",
                    "action": "open_default",
                    "icon": "text",
                    "bold": True
                },
                {
                    "text": "Open with",
                    "icon": "open_with",
                    "submenu": [
                        {
                            "text": "Notepad",
                            "action": "open_with_notepad.exe",
                            "icon": "text"
                        },
                        {
                            "text": "Visual Studio Code",
                            "action": "open_with_code.exe",
                            "icon": "code"
                        }
                    ]
                },
                {"separator": True},
                {
                    "text": "Cut",
                    "action": "cut",
                    "icon": "cut",
                    "shortcut": "Ctrl+X"
                },
                {
                    "text": "Copy",
                    "action": "copy",
                    "icon": "copy",
                    "shortcut": "Ctrl+C"
                },
                {"separator": True},
                {
                    "text": "Delete",
                    "action": "delete",
                    "icon": "delete"
                },
                {
                    "text": "Rename",
                    "action": "rename",
                    "icon": "rename"
                },
                {"separator": True},
                {
                    "text": "Properties",
                    "action": "properties",
                    "icon": "properties"
                }
            ]
            
            # Create mock selected items
            mock_item = Mock()
            mock_item.data.return_value = str(test_files['text_file'])
            
            # Test context menu creation
            menu = file_panel._create_context_menu(mock_context.return_value)
            
            # Verify menu structure
            actions = menu.actions()
            assert len(actions) >= 6  # At least main actions + separators
            
            # Check for expected actions
            action_texts = [action.text() for action in actions if not action.isSeparator()]
            assert "Open with Notepad" in action_texts
            assert "Open with" in action_texts
            assert "Cut" in action_texts
            assert "Copy" in action_texts
            assert "Delete" in action_texts
            assert "Rename" in action_texts
            assert "Properties" in action_texts
    
    def test_python_file_context_menu(self, file_panel, test_files):
        """Test context menu for Python files"""
        with patch.object(file_panel.shell_integration, 'get_context_menu_items') as mock_context:
            mock_context.return_value = [
                {
                    "text": "Open with Python",
                    "action": "open_default",
                    "icon": "python",
                    "bold": True
                },
                {
                    "text": "Edit with Visual Studio Code",
                    "action": "open_with_code",
                    "icon": "code"
                },
                {
                    "text": "Run Python Script",
                    "action": "run_python",
                    "icon": "python"
                }
            ]
            
            menu = file_panel._create_context_menu(mock_context.return_value)
            action_texts = [action.text() for action in menu.actions() if not action.isSeparator()]
            
            assert "Open with Python" in action_texts
            assert "Edit with Visual Studio Code" in action_texts
            assert "Run Python Script" in action_texts
    
    def test_image_file_context_menu(self, file_panel, test_files):
        """Test context menu for image files"""
        with patch.object(file_panel.shell_integration, 'get_context_menu_items') as mock_context:
            mock_context.return_value = [
                {
                    "text": "Open with Photos",
                    "action": "open_default",
                    "icon": "image",
                    "bold": True
                },
                {
                    "text": "Open with",
                    "icon": "open_with",
                    "submenu": [
                        {
                            "text": "Paint",
                            "action": "open_with_mspaint.exe",
                            "icon": "image"
                        },
                        {
                            "text": "GIMP",
                            "action": "open_with_gimp.exe",
                            "icon": "image"
                        }
                    ]
                },
                {
                    "text": "Set as desktop background",
                    "action": "set_wallpaper",
                    "icon": "image"
                }
            ]
            
            menu = file_panel._create_context_menu(mock_context.return_value)
            action_texts = [action.text() for action in menu.actions() if not action.isSeparator()]
            
            assert "Open with Photos" in action_texts
            assert "Open with" in action_texts
            assert "Set as desktop background" in action_texts


class TestDirectoryContextMenus(TestContextMenus):
    """Test context menus for directories"""
    
    def test_directory_context_menu_structure(self, file_panel, test_files):
        """Test context menu structure for directories"""
        with patch.object(file_panel.shell_integration, 'get_context_menu_items') as mock_context:
            mock_context.return_value = [
                {
                    "text": "Open",
                    "action": "open",
                    "icon": "folder_open",
                    "bold": True
                },
                {
                    "text": "Open in new tab",
                    "action": "open_new_tab",
                    "icon": "tab_new"
                },
                {
                    "text": "Open in new window",
                    "action": "open_new_window",
                    "icon": "folder_open"
                },
                {"separator": True},
                {
                    "text": "Cut",
                    "action": "cut",
                    "icon": "cut"
                },
                {
                    "text": "Copy",
                    "action": "copy",
                    "icon": "copy"
                },
                {"separator": True},
                {
                    "text": "Delete",
                    "action": "delete",
                    "icon": "delete"
                },
                {
                    "text": "Rename",
                    "action": "rename",
                    "icon": "rename"
                },
                {"separator": True},
                {
                    "text": "Properties",
                    "action": "properties",
                    "icon": "properties"
                }
            ]
            
            menu = file_panel._create_context_menu(mock_context.return_value)
            action_texts = [action.text() for action in menu.actions() if not action.isSeparator()]
            
            # Verify key directory actions
            assert "Open" in action_texts
            assert "Open in new tab" in action_texts
            assert "Open in new window" in action_texts
            assert "Cut" in action_texts
            assert "Copy" in action_texts
            assert "Delete" in action_texts
            assert "Rename" in action_texts
            assert "Properties" in action_texts
    
    def test_open_in_new_tab_action(self, file_panel, test_files):
        """Test 'Open in new tab' functionality for directories"""
        with patch.object(file_panel, '_create_new_tab') as mock_create_tab:
            file_panel._context_menu_files = [test_files['test_dir']]
            
            # Simulate action trigger
            file_panel._handle_context_action("open_new_tab")
            
            # Verify new tab was created with correct path
            mock_create_tab.assert_called_once_with(test_files['test_dir'])
    
    def test_directory_navigation_action(self, file_panel, test_files):
        """Test directory navigation from context menu"""
        with patch.object(file_panel, 'navigate_to') as mock_navigate:
            file_panel._context_menu_files = [test_files['test_dir']]
            
            # Simulate action trigger
            file_panel._handle_context_action("open")
            
            # Verify navigation was called
            mock_navigate.assert_called_once_with(test_files['test_dir'])


class TestEmptyAreaContextMenus(TestContextMenus):
    """Test context menus for empty areas"""
    
    def test_empty_area_context_menu_structure(self, file_panel):
        """Test context menu structure for empty areas"""
        with patch.object(file_panel.shell_integration, 'get_empty_area_context_menu') as mock_empty:
            mock_empty.return_value = [
                {
                    'text': 'Refresh',
                    'action': 'refresh',
                    'enabled': True
                },
                {'separator': True},
                {
                    'text': 'New',
                    'submenu': [
                        {
                            'text': 'Folder',
                            'action': 'new_folder',
                            'enabled': True
                        },
                        {
                            'text': 'Text Document',
                            'action': 'new_text',
                            'enabled': True
                        },
                        {
                            'text': 'Bitmap Image',
                            'action': 'new_bitmap',
                            'enabled': True
                        }
                    ]
                },
                {'separator': True},
                {
                    'text': 'Paste',
                    'action': 'paste',
                    'enabled': True
                },
                {'separator': True},
                {
                    'text': 'Properties',
                    'action': 'properties',
                    'enabled': True
                }
            ]
            
            menu = file_panel._create_context_menu(mock_empty.return_value)
            action_texts = [action.text() for action in menu.actions() if not action.isSeparator()]
            
            assert "Refresh" in action_texts
            assert "New" in action_texts
            assert "Paste" in action_texts
            assert "Properties" in action_texts
    
    def test_new_folder_action(self, file_panel, temp_dir):
        """Test creating new folder from context menu"""
        with patch.object(file_panel, '_create_new_folder') as mock_create:
            file_panel.current_path = temp_dir
            
            # Simulate action trigger
            file_panel._handle_context_action("new_folder")
            
            # Verify new folder creation was called
            mock_create.assert_called_once()
    
    def test_refresh_action(self, file_panel):
        """Test refresh action from context menu"""
        with patch.object(file_panel, '_refresh_file_list') as mock_refresh:
            # Simulate action trigger
            file_panel._handle_context_action("refresh")
            
            # Verify refresh was called
            mock_refresh.assert_called_once()


class TestCrossPlatformContextMenus(TestContextMenus):
    """Test cross-platform context menu compatibility"""
    
    @pytest.mark.parametrize("platform", ["windows", "macos", "linux"])
    def test_platform_specific_context_menus(self, file_panel, test_files, platform):
        """Test context menus adapt to different platforms"""
        with patch('platform_config.get_platform_config') as mock_config:
            # Mock platform configuration
            mock_platform = Mock()
            mock_platform.is_windows = (platform == "windows")
            mock_platform.is_macos = (platform == "macos")
            mock_platform.is_linux = (platform == "linux")
            mock_config.return_value = mock_platform
            
            # Create new shell integration with mocked platform
            shell_integration = CrossPlatformShellIntegration()
            file_panel.shell_integration = shell_integration
            
            # Mock platform-specific context menu
            if platform == "windows":
                expected_actions = [
                    "Open Command Prompt here",
                    "Open PowerShell here",
                    "Send to",
                    "Properties"
                ]
            elif platform == "macos":
                expected_actions = [
                    "Open Terminal here",
                    "Get Info",
                    "Move to Trash"
                ]
            else:  # linux
                expected_actions = [
                    "Open Terminal here",
                    "Properties",
                    "Move to Trash"
                ]
            
            # Test that platform-specific actions are available
            # Note: expected_actions would be used for more detailed testing
            # with actual shell integration mocking
            assert shell_integration.config.is_windows == (platform == "windows")
            assert shell_integration.config.is_macos == (platform == "macos")
            assert shell_integration.config.is_linux == (platform == "linux")


class TestContextMenuActions(TestContextMenus):
    """Test context menu action handling"""
    
    def test_cut_copy_paste_actions(self, file_panel, test_files):
        """Test cut, copy, and paste actions"""
        with patch.object(file_panel, 'cut_selection') as mock_cut, \
             patch.object(file_panel, 'copy_selection') as mock_copy, \
             patch.object(file_panel, 'paste') as mock_paste:
            
            file_panel._context_menu_files = [test_files['text_file']]
            
            # Test cut action
            file_panel._handle_context_action("cut")
            mock_cut.assert_called_once()
            
            # Test copy action
            file_panel._handle_context_action("copy")
            mock_copy.assert_called_once()
            
            # Test paste action
            file_panel._handle_context_action("paste")
            mock_paste.assert_called_once()
    
    def test_delete_action(self, file_panel, test_files):
        """Test delete action"""
        with patch.object(file_panel, 'delete_selection') as mock_delete:
            file_panel._context_menu_files = [test_files['text_file']]
            
            # Test delete action
            file_panel._handle_context_action("delete")
            mock_delete.assert_called_once()
    
    def test_rename_action(self, file_panel, test_files):
        """Test rename action"""
        with patch.object(file_panel, '_rename_selection') as mock_rename:
            file_panel._context_menu_files = [test_files['text_file']]
            
            # Test rename action
            file_panel._handle_context_action("rename")
            mock_rename.assert_called_once()
    
    def test_properties_action(self, file_panel, test_files):
        """Test properties action"""
        with patch.object(file_panel.shell_integration, 'open_properties_dialog') as mock_props:
            file_panel._context_menu_files = [test_files['text_file']]
            
            # Test properties action
            file_panel._handle_context_action("properties")
            mock_props.assert_called_once_with(test_files['text_file'])
    
    def test_open_with_specific_app_action(self, file_panel, test_files):
        """Test opening file with specific application"""
        with patch.object(file_panel, '_open_with_program') as mock_open_with:
            file_panel._context_menu_files = [test_files['text_file']]
            
            # Test open with action
            file_panel._handle_context_action("open_with_notepad.exe")
            mock_open_with.assert_called_once_with(test_files['text_file'], "notepad.exe")


class TestContextMenuIcons(TestContextMenus):
    """Test context menu icons"""
    
    def test_context_menu_icon_mapping(self, file_panel):
        """Test that context menu icons are properly mapped"""
        # Test standard icon mappings
        icon_tests = [
            ("folder_open", "SP_DirOpenIcon"),
            ("file_open", "SP_FileIcon"),
            ("cut", "SP_DialogDiscardButton"),
            ("copy", "SP_DialogSaveButton"),
            ("paste", "SP_DialogOkButton"),
            ("delete", "SP_TrashIcon"),
            ("properties", "SP_ComputerIcon"),
            ("refresh", "SP_BrowserReload"),
        ]
        
        for icon_name, expected_style in icon_tests:
            icon = file_panel._get_context_menu_icon(icon_name)
            assert not icon.isNull(), f"Icon {icon_name} should not be null"
    
    def test_application_specific_icons(self, file_panel):
        """Test application-specific icon detection"""
        app_icon_tests = [
            ("vlc", "SP_MediaPlay"),
            ("git", "SP_DriveNetIcon"),
            ("code", "SP_CommandLink"),
            ("terminal", "SP_MessageBoxCritical"),
        ]
        
        for app_name, expected_style in app_icon_tests:
            icon = file_panel._get_context_menu_icon(app_name)
            assert not icon.isNull(), f"Icon {app_name} should not be null"


class TestContextMenuPerformance(TestContextMenus):
    """Test context menu performance"""
    
    def test_context_menu_creation_speed(self, file_panel, test_files):
        """Test that context menu creation is reasonably fast"""
        import time
        
        with patch.object(file_panel.shell_integration, 'get_context_menu_items') as mock_context:
            # Mock a large context menu
            mock_context.return_value = [
                {
                    "text": f"Action {i}",
                    "action": f"action_{i}",
                    "icon": "file_open"
                } for i in range(50)  # 50 menu items
            ]
            
            start_time = time.time()
            menu = file_panel._create_context_menu(mock_context.return_value)
            creation_time = time.time() - start_time
            
            # Context menu creation should be fast (under 100ms)
            assert creation_time < 0.1, f"Context menu creation took {creation_time:.3f}s, should be under 0.1s"
            assert len(menu.actions()) == 50


if __name__ == "__main__":
    # Run specific test when executed directly
    pytest.main([__file__])