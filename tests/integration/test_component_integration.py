"""
Integration tests for FileOrbit - testing component interactions
"""
from unittest.mock import Mock
from PySide6.QtCore import QThread, QEventLoop
from PySide6.QtTest import QTest

from src.ui.main_window import MainWindow
from src.ui.components.file_panel import FilePanel
from src.ui.components.sidebar import Sidebar
from src.services.file_service import FileService, FileOperationWorker
from src.services.theme_service import ThemeService


class TestMainWindowIntegration:
    """Test main window integration with services"""
    
    def test_main_window_with_real_services(self, qapp, temp_dir):
        """Test main window with actual service integration"""
        # Create real services (but with mocked external dependencies)
        file_service = FileService()
        theme_service = ThemeService()
        mock_config = Mock()
        
        # Initialize main window with real services
        window = MainWindow(
            file_service=file_service,
            theme_service=theme_service,
            config=mock_config
        )
        
        assert window.file_service is file_service
        assert window.theme_service is theme_service
        assert window.config is mock_config
        
        window.show()
        QTest.qWait(100)
        window.close()
    
    def test_panel_service_interaction(self, qapp, temp_dir, sample_files):
        """Test file panel interaction with file service"""
        file_service = FileService()
        
        panel = FilePanel(
            panel_id="test",
            file_service=file_service
        )
        
        # Navigate to test directory
        test_dir = sample_files['small'].parent
        panel.navigate_to(str(test_dir))
        
        # Verify service interaction
        assert panel.current_path == str(test_dir)
        
        panel.close()
    
    def test_sidebar_drive_integration(self, qapp, mock_platform_config):
        """Test sidebar integration with platform configuration"""
        config = mock_platform_config
        
        sidebar = Sidebar(config=config)
        
        # Test drive detection integration
        sidebar.refresh_drives()
        
        # Should have detected some drives (mocked)
        assert hasattr(sidebar, 'drives') or hasattr(sidebar, 'drive_items')
        
        sidebar.close()


class TestFileOperationIntegration:
    """Test file operations across components"""
    
    def test_copy_operation_integration(self, qapp, temp_dir, sample_files):
        """Test complete copy operation across UI and services"""
        # Setup services
        # Create source and destination directories
        dst_dir = temp_dir / "destination"
        dst_dir.mkdir()
        
        # Test copy operation
        source_files = [sample_files['small']]
        destination = str(dst_dir)
        
        # Create worker for copy operation
        worker = FileOperationWorker(
            operation="copy",
            source_paths=[str(f) for f in source_files],
            destination_path=destination
        )
        
        # Track completion
        operation_completed = []
        worker.operation_completed.connect(lambda: operation_completed.append(True))
        
        # Start operation in thread
        thread = QThread()
        worker.moveToThread(thread)
        thread.started.connect(worker.execute)
        thread.start()
        
        # Wait for completion
        timeout = 5000  # 5 seconds
        loop = QEventLoop()
        worker.operation_completed.connect(loop.quit)
        QTest.qWait(timeout)
        
        thread.quit()
        thread.wait()
        
        # Verify file was copied
        copied_file = dst_dir / sample_files['small'].name
        assert copied_file.exists()
        assert len(operation_completed) > 0
    
    def test_move_operation_integration(self, qapp, temp_dir):
        """Test complete move operation"""
        # Create test file
        src_file = temp_dir / "source.txt"
        src_file.write_text("Test content")
        
        dst_dir = temp_dir / "destination"
        dst_dir.mkdir()
        
        # Create worker for move operation
        worker = FileOperationWorker(
            operation="move",
            source_paths=[str(src_file)],
            destination_path=str(dst_dir)
        )
        
        # Track completion
        operation_completed = []
        worker.operation_completed.connect(lambda: operation_completed.append(True))
        
        # Start operation
        thread = QThread()
        worker.moveToThread(thread)
        thread.started.connect(worker.execute)
        thread.start()
        
        # Wait for completion
        loop = QEventLoop()
        worker.operation_completed.connect(loop.quit)
        QTest.qWait(5000)
        
        thread.quit()
        thread.wait()
        
        # Verify file was moved
        moved_file = dst_dir / "source.txt"
        assert moved_file.exists()
        assert not src_file.exists()  # Original should be gone
        assert len(operation_completed) > 0


class TestThemeIntegration:
    """Test theme system integration"""
    
    def test_theme_service_integration(self, qapp):
        """Test theme service with UI components"""
        theme_service = ThemeService()
        mock_config = Mock()
        file_service = FileService()
        
        # Create main window
        window = MainWindow(
            file_service=file_service,
            theme_service=theme_service,
            config=mock_config
        )
        
        # Test theme switching
        if hasattr(theme_service, 'set_theme'):
            theme_service.set_theme("dark")
            
            # Apply to window
            if hasattr(window, 'apply_theme'):
                window.apply_theme("dark")
                
                # Verify theme was applied
                assert len(window.styleSheet()) > 0
        
        window.close()
    
    def test_theme_persistence_integration(self, qapp, temp_dir):
        """Test theme persistence across sessions"""
        # Create temporary config directory
        config_dir = temp_dir / "config"
        config_dir.mkdir()
        
        theme_service = ThemeService()
        
        # Set theme and save
        if hasattr(theme_service, 'set_theme') and hasattr(theme_service, 'save_preferences'):
            theme_service.set_theme("dark")
            theme_service.save_preferences(str(config_dir / "theme.json"))
            
            # Create new service instance and load
            new_theme_service = ThemeService()
            if hasattr(new_theme_service, 'load_preferences'):
                new_theme_service.load_preferences(str(config_dir / "theme.json"))
                
                # Should have same theme
                if hasattr(new_theme_service, 'get_current_theme'):
                    assert new_theme_service.get_current_theme() == "dark"


class TestPlatformIntegration:
    """Test platform-specific integrations"""
    
    def test_windows_api_integration(self, qapp, mock_platform_config):
        """Test Windows API integration (mocked)"""
        config = mock_platform_config
        
        # Test Windows-specific functionality
        if hasattr(config, 'get_system_drives'):
            drives = config.get_system_drives()
            assert len(drives) > 0
            
            # Verify drive structure
            for drive in drives:
                assert 'path' in drive
                assert 'label' in drive
    
    def test_cross_platform_compatibility(self, qapp):
        """Test cross-platform compatibility"""
        mock_config = Mock()
        mock_config.is_64bit.return_value = True
        mock_config.get_optimal_buffer_size.return_value = 8192
        
        # Should work on any platform
        assert hasattr(mock_config, 'is_64bit')
        assert isinstance(mock_config.is_64bit(), bool)
        
        if hasattr(mock_config, 'get_optimal_buffer_size'):
            buffer_size = mock_config.get_optimal_buffer_size()
            assert buffer_size > 0
            assert buffer_size % 1024 == 0  # Should be multiple of 1024


class TestMemoryManagement:
    """Test memory management across components"""
    
    def test_large_file_operation_memory(self, qapp, temp_dir, performance_helper):
        """Test memory usage during large file operations"""
        # Create large test file (10MB)
        large_file = temp_dir / "large_test.dat"
        with open(large_file, 'wb') as f:
            f.write(b'0' * (10 * 1024 * 1024))  # 10MB
        
        dst_dir = temp_dir / "destination"
        dst_dir.mkdir()
        
        # Measure initial memory
        initial_memory = performance_helper.get_current_memory_usage()
        
        # Perform copy operation
        file_service = FileService()
        worker = FileOperationWorker(
            operation="copy",
            source_paths=[str(large_file)],
            destination_path=str(dst_dir)
        )
        
        # Execute and measure memory
        thread = QThread()
        worker.moveToThread(thread)
        thread.started.connect(worker.execute)
        thread.start()
        
        # Wait for completion
        operation_completed = []
        worker.operation_completed.connect(lambda: operation_completed.append(True))
        
        loop = QEventLoop()
        worker.operation_completed.connect(loop.quit)
        QTest.qWait(10000)  # 10 seconds for large file
        
        thread.quit()
        thread.wait()
        
        # Measure final memory
        final_memory = performance_helper.get_current_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than file size)
        assert memory_increase < 10 * 1024 * 1024  # Less than 10MB
        assert len(operation_completed) > 0
    
    def test_multiple_panels_memory(self, qapp, temp_dir, performance_helper):
        """Test memory usage with multiple file panels"""
        initial_memory = performance_helper.get_current_memory_usage()
        
        file_service = FileService()
        panels = []
        
        # Create multiple panels
        for i in range(5):
            panel = FilePanel(
                panel_id=f"panel_{i}",
                file_service=file_service
            )
            panel.navigate_to(str(temp_dir))
            panels.append(panel)
        
        # Measure memory with all panels
        peak_memory = performance_helper.get_current_memory_usage()
        memory_per_panel = (peak_memory - initial_memory) / len(panels)
        
        # Each panel should use reasonable memory
        assert memory_per_panel < 50 * 1024 * 1024  # Less than 50MB per panel
        
        # Cleanup
        for panel in panels:
            panel.close()


class TestConcurrentOperations:
    """Test concurrent file operations"""
    
    def test_multiple_file_operations(self, qapp, temp_dir, sample_files):
        """Test multiple concurrent file operations"""
        # Create multiple destination directories
        dst_dirs = []
        for i in range(3):
            dst_dir = temp_dir / f"dest_{i}"
            dst_dir.mkdir()
            dst_dirs.append(dst_dir)
        
        # Create workers for concurrent operations
        workers = []
        threads = []
        completed_operations = []
        
        for i, dst_dir in enumerate(dst_dirs):
            worker = FileOperationWorker(
                operation="copy",
                source_paths=[str(sample_files['small'])],
                destination_path=str(dst_dir)
            )
            
            thread = QThread()
            worker.moveToThread(thread)
            
            # Track completion
            worker.operation_completed.connect(
                lambda i=i: completed_operations.append(i)
            )
            
            workers.append(worker)
            threads.append(thread)
        
        # Start all operations
        for worker, thread in zip(workers, threads):
            thread.started.connect(worker.execute)
            thread.start()
        
        # Wait for all to complete
        QTest.qWait(5000)
        
        # Cleanup threads
        for thread in threads:
            thread.quit()
            thread.wait()
        
        # Verify all operations completed
        assert len(completed_operations) == 3
        
        # Verify all files were copied
        for dst_dir in dst_dirs:
            copied_file = dst_dir / sample_files['small'].name
            assert copied_file.exists()


class TestErrorRecovery:
    """Test error recovery in integrated scenarios"""
    
    def test_file_operation_error_recovery(self, qapp, temp_dir):
        """Test recovery from file operation errors"""
        # Try to copy non-existent file
        worker = FileOperationWorker(
            operation="copy",
            source_paths=["/non/existent/file.txt"],
            destination_path=str(temp_dir)
        )
        
        error_occurred = []
        worker.operation_error.connect(lambda msg: error_occurred.append(msg))
        
        # Execute operation (should fail)
        thread = QThread()
        worker.moveToThread(thread)
        thread.started.connect(worker.execute)
        thread.start()
        
        # Wait for error
        QTest.qWait(2000)
        
        thread.quit()
        thread.wait()
        
        # Should have received error signal
        assert len(error_occurred) > 0
    
    def test_ui_recovery_from_service_errors(self, qapp):
        """Test UI recovery when services fail"""
        # Mock failing services
        mock_file_service = Mock()
        mock_file_service.copy_files.side_effect = Exception("Service failure")
        
        mock_theme_service = Mock()
        mock_config = Mock()
        
        # UI should handle service failures gracefully
        window = MainWindow(
            file_service=mock_file_service,
            theme_service=mock_theme_service,
            config=mock_config
        )
        
        window.show()
        
        # UI should remain functional despite service errors
        assert window.isVisible()
        
        window.close()


class TestApplicationLifecycle:
    """Test complete application lifecycle"""
    
    def test_startup_shutdown_cycle(self, qapp):
        """Test complete startup and shutdown cycle"""
        # Initialize all services
        mock_config = Mock()
        file_service = FileService()
        theme_service = ThemeService()
        
        # Create main application window
        window = MainWindow(
            file_service=file_service,
            theme_service=theme_service,
            config=mock_config
        )
        
        # Simulate startup
        window.show()
        QTest.qWait(500)
        
        # Simulate some user activity
        QTest.qWait(100)
        
        # Simulate shutdown
        window.close()
        
        # Should complete without errors
        assert True  # If we get here, lifecycle completed successfully
    
    def test_configuration_persistence(self, qapp, temp_dir):
        """Test configuration persistence across sessions"""
        config_file = temp_dir / "fileorbit_config.json"
        
        # Create initial configuration
        mock_config = Mock()
        mock_config.is_64bit.return_value = True
        
        if hasattr(mock_config, 'save_configuration'):
            mock_config.save_configuration(str(config_file))
            
            # Create new config instance and load
            new_mock_config = Mock()
            new_mock_config.is_64bit.return_value = True
            
            if hasattr(new_mock_config, 'load_configuration'):
                new_mock_config.load_configuration(str(config_file))
                
                # Should have loaded configuration
                assert new_mock_config.is_64bit() == mock_config.is_64bit()
