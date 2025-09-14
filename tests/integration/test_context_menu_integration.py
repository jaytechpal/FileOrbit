"""
Integration tests for FileOrbit context menu functionality
Tests real context menu interactions and shell integration
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import patch

from src.ui.components.file_panel import FilePanel
from src.services.cross_platform_shell_integration import get_shell_integration


class TestContextMenuIntegration:
    """Integration tests for context menu functionality"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace with test files"""
        temp_path = Path(tempfile.mkdtemp())
        
        # Create test directory structure
        test_structure = {
            'documents': temp_path / 'Documents',
            'images': temp_path / 'Images',
            'scripts': temp_path / 'Scripts',
            'empty_folder': temp_path / 'EmptyFolder',
        }
        
        # Create directories
        for folder in test_structure.values():
            folder.mkdir(parents=True)
        
        # Create test files
        test_files = {
            'readme': temp_path / 'README.md',
            'python_script': test_structure['scripts'] / 'test.py',
            'text_file': test_structure['documents'] / 'notes.txt',
            'image_file': test_structure['images'] / 'photo.jpg',
            'config_file': temp_path / 'config.ini',
        }
        
        # Write content to test files
        test_files['readme'].write_text("# FileOrbit Test\nThis is a test README file.")
        test_files['python_script'].write_text("#!/usr/bin/env python3\nprint('Hello, World!')")
        test_files['text_file'].write_text("These are my notes.\nLine 2 of notes.")
        test_files['image_file'].write_bytes(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde')  # Minimal PNG header
        test_files['config_file'].write_text("[settings]\ntheme=dark\nlanguage=en")
        
        workspace = {
            'root': temp_path,
            'folders': test_structure,
            'files': test_files
        }
        
        yield workspace
        
        # Cleanup
        shutil.rmtree(temp_path, ignore_errors=True)
    
    @pytest.fixture
    def file_panel_with_workspace(self, qtbot, temp_workspace):
        """Create FilePanel with test workspace"""
        panel = FilePanel(panel_id="integration_test", file_service=None, config=None)
        panel.current_path = temp_workspace['root']
        panel._refresh_file_list()
        qtbot.addWidget(panel)
        return panel, temp_workspace


class TestRealContextMenuGeneration(TestContextMenuIntegration):
    """Test real context menu generation with shell integration"""
    
    def test_file_context_menu_real_shell_integration(self, file_panel_with_workspace):
        """Test real shell integration for file context menus"""
        panel, workspace = file_panel_with_workspace
        shell_integration = get_shell_integration()
        
        # Test context menu for Python file
        python_file = str(workspace['files']['python_script'])
        context_items = shell_integration.get_context_menu_items(python_file)
        
        # Should have basic context menu items
        assert len(context_items) > 0
        
        # Extract action texts for verification
        action_texts = []
        for item in context_items:
            if not item.get('separator'):
                action_texts.append(item.get('text', ''))
        
        # Should contain standard file operations
        assert any('open' in text.lower() for text in action_texts)
        assert any('cut' in text.lower() for text in action_texts)
        assert any('copy' in text.lower() for text in action_texts)
        assert any('delete' in text.lower() for text in action_texts)
        assert any('properties' in text.lower() or 'info' in text.lower() for text in action_texts)
    
    def test_directory_context_menu_real_shell_integration(self, file_panel_with_workspace):
        """Test real shell integration for directory context menus"""
        panel, workspace = file_panel_with_workspace
        shell_integration = get_shell_integration()
        
        # Test context menu for directory
        test_dir = str(workspace['folders']['documents'])
        context_items = shell_integration.get_context_menu_items(test_dir)
        
        # Should have basic context menu items
        assert len(context_items) > 0
        
        # Extract action texts for verification
        action_texts = []
        for item in context_items:
            if not item.get('separator'):
                action_texts.append(item.get('text', ''))
        
        # Should contain directory-specific operations
        assert any('open' in text.lower() for text in action_texts)
        
        # Check for "Open in new tab" specifically for directories
        has_new_tab = any('new tab' in text.lower() for text in action_texts)
        if not has_new_tab:
            # If not from shell integration, should be in fallback menu
            fallback_items = shell_integration._get_fallback_context_menu(test_dir) if hasattr(shell_integration, '_get_fallback_context_menu') else []
            fallback_texts = [item.get('text', '') for item in fallback_items if not item.get('separator')]
            has_new_tab = any('new tab' in text.lower() for text in fallback_texts)
        
        assert has_new_tab, "Directory context menu should include 'Open in new tab' option"
    
    def test_empty_area_context_menu_real_shell_integration(self, file_panel_with_workspace):
        """Test real shell integration for empty area context menus"""
        panel, workspace = file_panel_with_workspace
        shell_integration = get_shell_integration()
        
        # Test empty area context menu
        empty_context_items = shell_integration.get_empty_area_context_menu()
        
        # Should have basic empty area items
        assert len(empty_context_items) > 0
        
        # Extract action texts for verification
        action_texts = []
        for item in empty_context_items:
            if not item.get('separator'):
                action_texts.append(item.get('text', ''))
        
        # Should contain standard empty area operations
        assert any('refresh' in text.lower() for text in action_texts)
        assert any('new' in text.lower() or 'create' in text.lower() for text in action_texts)
        assert any('paste' in text.lower() for text in action_texts)


class TestContextMenuActionExecution(TestContextMenuIntegration):
    """Test context menu action execution"""
    
    def test_open_in_new_tab_execution(self, file_panel_with_workspace):
        """Test execution of 'Open in new tab' action"""
        panel, workspace = file_panel_with_workspace
        
        # Get initial tab count
        initial_tab_count = panel.tab_widget.count()
        
        # Set up context for directory
        test_dir = workspace['folders']['documents']
        panel._context_menu_files = [test_dir]
        
        # Execute "open in new tab" action
        panel._handle_context_action("open_new_tab")
        
        # Verify new tab was created
        assert panel.tab_widget.count() == initial_tab_count + 1
        
        # Verify new tab has correct path
        new_tab = panel.tab_widget.widget(panel.tab_widget.count() - 1)
        assert new_tab.current_path == test_dir
    
    def test_context_menu_copy_cut_actions(self, file_panel_with_workspace):
        """Test copy and cut actions from context menu"""
        panel, workspace = file_panel_with_workspace
        
        # Test file operations
        test_file = workspace['files']['text_file']
        panel._context_menu_files = [test_file]
        
        # Test copy action
        with patch.object(panel, 'copy_selection') as mock_copy:
            panel._handle_context_action("copy")
            mock_copy.assert_called_once()
        
        # Test cut action
        with patch.object(panel, 'cut_selection') as mock_cut:
            panel._handle_context_action("cut")
            mock_cut.assert_called_once()
    
    def test_context_menu_delete_action(self, file_panel_with_workspace):
        """Test delete action from context menu"""
        panel, workspace = file_panel_with_workspace
        
        # Create a temporary file for deletion test
        temp_file = workspace['root'] / 'temp_delete_test.txt'
        temp_file.write_text("This file will be deleted")
        
        # Set up context for file
        panel._context_menu_files = [temp_file]
        
        # Test delete action
        with patch.object(panel, 'delete_selection') as mock_delete:
            panel._handle_context_action("delete")
            mock_delete.assert_called_once()
    
    def test_context_menu_properties_action(self, file_panel_with_workspace):
        """Test properties action from context menu"""
        panel, workspace = file_panel_with_workspace
        
        # Test properties for file
        test_file = workspace['files']['config_file']
        panel._context_menu_files = [test_file]
        
        # Test properties action
        with patch.object(panel.shell_integration, 'open_properties_dialog') as mock_props:
            mock_props.return_value = True
            panel._handle_context_action("properties")
            mock_props.assert_called_once_with(test_file)


class TestContextMenuErrorHandling(TestContextMenuIntegration):
    """Test context menu error handling"""
    
    def test_context_menu_nonexistent_file(self, file_panel_with_workspace):
        """Test context menu handling for nonexistent files"""
        panel, workspace = file_panel_with_workspace
        
        # Create path to nonexistent file
        nonexistent_file = workspace['root'] / 'nonexistent.txt'
        
        # Test context menu creation doesn't crash
        shell_integration = get_shell_integration()
        try:
            context_items = shell_integration.get_context_menu_items(str(nonexistent_file))
            # Should return empty list or basic fallback menu
            assert isinstance(context_items, list)
        except Exception as e:
            pytest.fail(f"Context menu creation should not crash for nonexistent files: {e}")
    
    def test_context_menu_permission_error(self, file_panel_with_workspace):
        """Test context menu handling for permission errors"""
        panel, workspace = file_panel_with_workspace
        
        # Create a file and remove read permissions (on Unix systems)
        test_file = workspace['root'] / 'no_permission.txt'
        test_file.write_text("Test content")
        
        if os.name == 'posix':  # Unix/Linux/macOS
            test_file.chmod(0o000)  # Remove all permissions
        
        try:
            # Test context menu creation doesn't crash
            shell_integration = get_shell_integration()
            context_items = shell_integration.get_context_menu_items(str(test_file))
            assert isinstance(context_items, list)
        except Exception as e:
            pytest.fail(f"Context menu creation should handle permission errors gracefully: {e}")
        finally:
            if os.name == 'posix':
                test_file.chmod(0o644)  # Restore permissions for cleanup


class TestContextMenuUIIntegration(TestContextMenuIntegration):
    """Test context menu UI integration"""
    
    def test_context_menu_position(self, file_panel_with_workspace):
        """Test context menu positioning"""
        panel, workspace = file_panel_with_workspace
        
        # Create mock position
        from PySide6.QtCore import QPoint
        position = QPoint(100, 100)
        
        # Mock file list widget
        mock_item = type('MockItem', (), {
            'data': lambda self, role: str(workspace['files']['text_file'])
        })()
        
        # Test context menu doesn't crash on positioning
        try:
            panel._show_file_context_menu(position, [mock_item])
        except Exception as e:
            # Context menu might not show in test environment, but creation should not crash
            if "Cannot create QWidget" not in str(e) and "no application" not in str(e).lower():
                pytest.fail(f"Context menu creation should not crash: {e}")
    
    def test_context_menu_multiple_selection(self, file_panel_with_workspace):
        """Test context menu with multiple files selected"""
        panel, workspace = file_panel_with_workspace
        
        # Mock multiple selected items
        files = [workspace['files']['text_file'], workspace['files']['config_file']]
        mock_items = []
        for file_path in files:
            mock_item = type('MockItem', (), {
                'data': lambda self, role, path=file_path: str(path)
            })()
            mock_items.append(mock_item)
        
        # Set up multiple file context
        panel._context_menu_files = files
        
        # Test that actions work with multiple files
        with patch.object(panel, 'copy_selection') as mock_copy:
            panel._handle_context_action("copy")
            mock_copy.assert_called_once()


if __name__ == "__main__":
    # Run specific test when executed directly
    pytest.main([__file__])