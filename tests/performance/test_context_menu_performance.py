"""
Performance tests for context menu functionality
Tests context menu creation speed, memory usage, and responsiveness
"""

import pytest
import time
import tempfile
from pathlib import Path

from src.ui.components.file_panel import FilePanel
from src.services.cross_platform_shell_integration import get_shell_integration


class TestContextMenuPerformance:
    """Performance tests for context menu functionality"""
    
    @pytest.fixture
    def large_context_menu_data(self):
        """Generate large context menu data for performance testing"""
        # Simulate Windows context menu with many shell extensions
        items = []
        
        # Add standard items
        standard_items = [
            {"text": "Open", "action": "open", "icon": "file_open", "bold": True},
            {"separator": True},
        ]
        items.extend(standard_items)
        
        # Add "Open with" submenu with many applications
        open_with_submenu = []
        applications = [
            "Notepad", "Visual Studio Code", "Sublime Text", "Atom", "Vim",
            "Emacs", "nano", "WordPad", "Microsoft Word", "LibreOffice Writer",
            "Paint", "GIMP", "Photoshop", "InkScape", "Blender",
            "VLC Media Player", "Windows Media Player", "foobar2000", "iTunes",
            "Chrome", "Firefox", "Edge", "Safari", "Opera"
        ]
        
        for app in applications:
            open_with_submenu.append({
                "text": app,
                "action": f"open_with_{app.lower().replace(' ', '_')}",
                "icon": "app_extension"
            })
        
        items.append({
            "text": "Open with",
            "icon": "open_with",
            "submenu": open_with_submenu
        })
        
        # Add separator and more items
        items.extend([
            {"separator": True},
            {"text": "Cut", "action": "cut", "icon": "cut", "shortcut": "Ctrl+X"},
            {"text": "Copy", "action": "copy", "icon": "copy", "shortcut": "Ctrl+C"},
            {"separator": True},
            {"text": "Delete", "action": "delete", "icon": "delete"},
            {"text": "Rename", "action": "rename", "icon": "rename"},
            {"separator": True},
        ])
        
        # Add Send To submenu with many destinations
        send_to_submenu = []
        destinations = [
            "Desktop (create shortcut)", "Documents", "Downloads", "Pictures",
            "Music", "Videos", "OneDrive", "Dropbox", "Google Drive",
            "USB Drive (E:)", "Network Drive (Z:)", "CD/DVD Drive",
            "Bluetooth Device", "Email Recipient", "Compressed (zipped) folder"
        ]
        
        for dest in destinations:
            send_to_submenu.append({
                "text": dest,
                "action": f"send_to_{dest.lower().replace(' ', '_').replace('(', '').replace(')', '')}",
                "icon": "send_to"
            })
        
        items.append({
            "text": "Send to",
            "icon": "send_to",
            "submenu": send_to_submenu
        })
        
        # Add more separators and items
        items.extend([
            {"separator": True},
            {"text": "Properties", "action": "properties", "icon": "properties"}
        ])
        
        return items
    
    def test_context_menu_creation_performance(self, qtbot, large_context_menu_data):
        """Test context menu creation performance with large menu"""
        panel = FilePanel(panel_id="perf_test", file_service=None, config=None)
        qtbot.addWidget(panel)
        
        # Measure context menu creation time
        start_time = time.time()
        menu = panel._create_context_menu(large_context_menu_data)
        creation_time = time.time() - start_time
        
        # Context menu creation should be fast (under 200ms even for large menus)
        assert creation_time < 0.2, f"Context menu creation took {creation_time:.3f}s, should be under 0.2s"
        
        # Verify all items were created
        actions = menu.actions()
        non_separator_actions = [a for a in actions if not a.isSeparator()]
        assert len(non_separator_actions) > 20, "Should have many menu items for performance test"
    
    def test_context_menu_icon_loading_performance(self, qtbot):
        """Test context menu icon loading performance"""
        panel = FilePanel(panel_id="icon_perf_test", file_service=None, config=None)
        qtbot.addWidget(panel)
        
        # Test icon loading for many different icon types
        icon_names = [
            "folder_open", "file_open", "cut", "copy", "paste", "delete",
            "rename", "properties", "refresh", "new", "vlc", "git", "code",
            "terminal", "powershell", "cmd", "media", "image", "text"
        ]
        
        # Measure icon loading time
        start_time = time.time()
        icons = []
        for icon_name in icon_names:
            icon = panel._get_context_menu_icon(icon_name)
            icons.append(icon)
        icon_loading_time = time.time() - start_time
        
        # Icon loading should be fast
        assert icon_loading_time < 0.1, f"Icon loading took {icon_loading_time:.3f}s, should be under 0.1s"
        
        # Verify icons were loaded (not all null)
        non_null_icons = [icon for icon in icons if not icon.isNull()]
        assert len(non_null_icons) > len(icon_names) * 0.5, "At least half of the icons should load successfully"
    
    def test_shell_integration_performance(self, qtbot):
        """Test shell integration performance for context menu items"""
        panel = FilePanel(panel_id="shell_perf_test", file_service=None, config=None)
        qtbot.addWidget(panel)
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(b"Test content for performance testing")
            test_file_path = tmp_file.name
        
        try:
            shell_integration = get_shell_integration()
            
            # Measure shell integration response time
            start_time = time.time()
            context_items = shell_integration.get_context_menu_items(test_file_path)
            shell_response_time = time.time() - start_time
            
            # Shell integration should respond quickly
            assert shell_response_time < 1.0, f"Shell integration took {shell_response_time:.3f}s, should be under 1.0s"
            
            # Should return some context menu items
            assert isinstance(context_items, list)
            
        finally:
            # Cleanup
            Path(test_file_path).unlink(missing_ok=True)
    
    def test_context_menu_memory_usage(self, qtbot, large_context_menu_data):
        """Test memory usage of context menu creation"""
        import gc
        
        panel = FilePanel(panel_id="memory_test", file_service=None, config=None)
        qtbot.addWidget(panel)
        
        # Force garbage collection and measure initial memory
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Create and destroy multiple context menus
        menus = []
        for _ in range(10):
            menu = panel._create_context_menu(large_context_menu_data)
            menus.append(menu)
        
        # Clear references
        menus.clear()
        
        # Force garbage collection and measure final memory
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Memory usage should not grow excessively
        object_increase = final_objects - initial_objects
        # Allow some increase but not excessive (less than 1000 new objects)
        assert object_increase < 1000, f"Memory usage increased by {object_increase} objects, should be minimal"
    
    def test_context_menu_responsiveness_under_load(self, qtbot):
        """Test context menu responsiveness under load"""
        panel = FilePanel(panel_id="load_test", file_service=None, config=None)
        qtbot.addWidget(panel)
        
        # Simulate heavy load by creating many context menus rapidly
        creation_times = []
        
        for i in range(20):  # Create 20 context menus
            # Create varying menu sizes
            menu_items = [
                {"text": f"Item {j}", "action": f"action_{j}", "icon": "file_open"}
                for j in range(i + 1)  # Growing menu size
            ]
            
            start_time = time.time()
            menu = panel._create_context_menu(menu_items)
            creation_time = time.time() - start_time
            creation_times.append(creation_time)
            
            # Clean up menu
            del menu
        
        # Check that performance doesn't degrade significantly
        average_time = sum(creation_times) / len(creation_times)
        max_time = max(creation_times)
        
        # Average creation time should be reasonable
        assert average_time < 0.05, f"Average creation time {average_time:.3f}s too slow"
        
        # Maximum creation time should not be excessive
        assert max_time < 0.1, f"Maximum creation time {max_time:.3f}s too slow"
        
        # Performance should be consistent (max time not much higher than average)
        assert max_time < average_time * 3, "Performance degradation detected under load"


class TestContextMenuScalability:
    """Test context menu scalability with different data sizes"""
    
    @pytest.mark.parametrize("item_count", [1, 10, 50, 100])
    def test_context_menu_scalability(self, qtbot, item_count):
        """Test context menu performance with different item counts"""
        panel = FilePanel(panel_id="scale_test", file_service=None, config=None)
        qtbot.addWidget(panel)
        
        # Generate menu items
        menu_items = [
            {"text": f"Item {i}", "action": f"action_{i}", "icon": "file_open"}
            for i in range(item_count)
        ]
        
        # Measure creation time
        start_time = time.time()
        menu = panel._create_context_menu(menu_items)
        creation_time = time.time() - start_time
        
        # Performance should scale reasonably (roughly linear)
        expected_max_time = item_count * 0.002  # 2ms per item
        assert creation_time < expected_max_time, \
            f"Creation time {creation_time:.3f}s too slow for {item_count} items"
        
        # Verify all items were created
        actions = menu.actions()
        assert len(actions) == item_count, f"Expected {item_count} actions, got {len(actions)}"
    
    @pytest.mark.parametrize("submenu_depth", [1, 2, 3, 4])
    def test_nested_submenu_performance(self, qtbot, submenu_depth):
        """Test performance with deeply nested submenus"""
        panel = FilePanel(panel_id="nested_test", file_service=None, config=None)
        qtbot.addWidget(panel)
        
        # Create nested menu structure
        def create_nested_menu(depth):
            if depth == 0:
                return {"text": "Leaf Item", "action": "leaf_action", "icon": "file_open"}
            return {
                "text": f"Submenu Level {depth}",
                "icon": "folder_open",
                "submenu": [create_nested_menu(depth - 1)]
            }
        
        menu_items = [create_nested_menu(submenu_depth)]
        
        # Measure creation time
        start_time = time.time()
        panel._create_context_menu(menu_items)
        creation_time = time.time() - start_time
        
        # Performance should not degrade significantly with nesting
        expected_max_time = submenu_depth * 0.01  # 10ms per level
        assert creation_time < expected_max_time, \
            f"Creation time {creation_time:.3f}s too slow for {submenu_depth} levels"


if __name__ == "__main__":
    # Run specific test when executed directly
    pytest.main([__file__])