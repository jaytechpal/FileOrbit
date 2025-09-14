"""
Integration tests for IconManager service

This module demonstrates integration testing patterns and provides
comprehensive tests for the IconManager service.
"""

from pathlib import Path
from unittest.mock import Mock, patch

from tests.test_framework import TestBase, integration_test, temp_directory
from src.services.icon_manager import IconManager


class TestIconManagerIntegration(TestBase):
    """Integration tests for IconManager."""
    
    def setup_method(self):
        """Set up test environment."""
        super().setup_method()
        self.icon_manager = IconManager()
    
    @integration_test
    def test_icon_manager_initialization(self):
        """Test IconManager initializes correctly."""
        assert self.icon_manager is not None
        assert self.icon_manager.icon_provider is not None
        assert self.icon_manager.platform is not None
    
    @integration_test
    def test_get_folder_icon(self):
        """Test getting folder icon."""
        # Act
        icon = self.icon_manager.get_folder_icon()
        
        # Assert
        assert icon is not None
        # Icon might be null on systems without proper icons, but should not raise
    
    @integration_test
    def test_get_fallback_icon_for_missing_file(self):
        """Test fallback icon for non-existent file."""
        # Arrange
        non_existent_path = Path("/non/existent/file.txt")
        
        # Act
        icon = self.icon_manager.get_fallback_icon(non_existent_path)
        
        # Assert
        assert icon is not None
    
    @integration_test
    def test_cache_functionality(self):
        """Test icon caching works correctly."""
        # Arrange
        test_path = Path.home()
        
        # Act - First call
        icon1 = self.icon_manager.get_file_icon(test_path)
        stats_after_first = self.icon_manager.get_cache_stats()
        
        # Act - Second call (should hit cache)
        icon2 = self.icon_manager.get_file_icon(test_path)
        stats_after_second = self.icon_manager.get_cache_stats()
        
        # Assert
        assert icon1 is not None
        assert icon2 is not None
        assert stats_after_second['cache_hits'] > stats_after_first['cache_hits']
    
    @integration_test
    def test_clear_cache(self):
        """Test cache clearing functionality."""
        # Arrange
        test_path = Path.home()
        self.icon_manager.get_file_icon(test_path)
        stats_before = self.icon_manager.get_cache_stats()
        
        # Act
        self.icon_manager.clear_cache()
        stats_after = self.icon_manager.get_cache_stats()
        
        # Assert
        assert stats_before['cache_size'] > 0
        assert stats_after['cache_size'] == 0
    
    @integration_test
    def test_context_menu_icon_with_empty_name(self):
        """Test context menu icon with empty name."""
        # Act
        icon = self.icon_manager.get_context_menu_icon("")
        
        # Assert
        # Should return empty icon for empty name
        assert icon is not None
    
    @integration_test
    def test_context_menu_icon_with_valid_name(self):
        """Test context menu icon with valid name."""
        # Act
        icon = self.icon_manager.get_context_menu_icon("test_app")
        
        # Assert
        assert icon is not None
    
    @integration_test 
    def test_get_exe_icon_with_nonexistent_file(self):
        """Test exe icon extraction with non-existent file."""
        # Act
        icon = self.icon_manager.get_exe_icon_with_index("/non/existent/app.exe", 0)
        
        # Assert
        # Should return empty icon for non-existent file
        assert icon is not None
    
    @integration_test
    def test_cache_stats_accuracy(self):
        """Test cache statistics are accurate."""
        # Arrange
        self.icon_manager.clear_cache()
        initial_stats = self.icon_manager.get_cache_stats()
        
        # Act - Generate some cache activity
        path1 = Path.home()
        path2 = Path.home().parent if Path.home().parent != Path.home() else Path.home()
        
        # First calls (cache misses)
        self.icon_manager.get_file_icon(path1)
        self.icon_manager.get_file_icon(path2)
        
        # Second calls (cache hits)
        self.icon_manager.get_file_icon(path1)
        self.icon_manager.get_file_icon(path2)
        
        final_stats = self.icon_manager.get_cache_stats()
        
        # Assert
        assert initial_stats['total_requests'] == 0
        assert final_stats['total_requests'] == 4
        assert final_stats['cache_hits'] >= 2  # At least 2 hits from repeated calls
        assert final_stats['cache_misses'] >= 2  # At least 2 misses from first calls
    
    @integration_test
    def test_multiple_icon_types(self):
        """Test getting multiple types of icons."""
        # Act - Get different types of icons
        folder_icon = self.icon_manager.get_folder_icon()
        parent_icon = self.icon_manager.get_parent_directory_icon()
        context_icon = self.icon_manager.get_context_menu_icon("test")
        
        # Assert - All should return valid icon objects
        assert folder_icon is not None
        assert parent_icon is not None
        assert context_icon is not None


class TestIconManagerWithMockedFileSystem(TestBase):
    """Test IconManager with mocked file system."""
    
    def setup_method(self):
        """Set up test environment."""
        super().setup_method()
        self.icon_manager = IconManager()
    
    @integration_test
    def test_file_icon_with_real_files(self):
        """Test file icon extraction with real test files."""
        with temp_directory() as temp_dir:
            # Create test files
            test_file = temp_dir / "test.txt"
            test_file.write_text("test content")
            
            test_dir = temp_dir / "test_folder"
            test_dir.mkdir()
            
            # Act
            file_icon = self.icon_manager.get_file_icon(test_file)
            dir_icon = self.icon_manager.get_file_icon(test_dir)
            
            # Assert
            assert file_icon is not None
            assert dir_icon is not None
    
    @integration_test
    @patch('src.services.icon_manager.QFileIconProvider')
    def test_icon_provider_failure_handling(self, mock_provider_class):
        """Test handling of icon provider failures."""
        # Arrange - Mock the provider to raise exceptions
        mock_provider = Mock()
        mock_provider.icon.side_effect = Exception("Icon provider error")
        mock_provider_class.return_value = mock_provider
        
        # Create new manager with mocked provider
        icon_manager = IconManager()
        
        # Act
        test_path = Path("/test/file.txt")
        icon = icon_manager.get_file_icon(test_path)
        
        # Assert - Should return fallback icon without raising
        assert icon is not None


class TestIconManagerPerformance(TestBase):
    """Performance tests for IconManager."""
    
    def setup_method(self):
        """Set up test environment."""
        super().setup_method()
        self.icon_manager = IconManager()
    
    @integration_test
    def test_cache_performance_with_many_files(self):
        """Test cache performance with many file requests."""
        import time
        
        # Arrange
        test_paths = [Path(f"/test/file_{i}.txt") for i in range(100)]
        
        # Act - First pass (cache misses)
        start_time = time.time()
        for path in test_paths:
            self.icon_manager.get_fallback_icon(path)
        first_pass_time = time.time() - start_time
        
        # Act - Second pass (cache hits)
        start_time = time.time()
        for path in test_paths:
            self.icon_manager.get_fallback_icon(path)
        second_pass_time = time.time() - start_time
        
        # Assert - Second pass should be significantly faster
        assert second_pass_time < first_pass_time
        
        # Check cache stats
        stats = self.icon_manager.get_cache_stats()
        assert stats['cache_hits'] >= 100
        assert stats['hit_rate'] > 50.0  # At least 50% hit rate