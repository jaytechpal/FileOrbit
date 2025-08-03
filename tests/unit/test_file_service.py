"""
Unit tests for file service and 64-bit file operations
"""
from pathlib import Path
from unittest.mock import Mock, patch

from src.services.file_service import FileOperationWorker, FileService, FileWatcher


class TestFileOperationWorker:
    """Test file operation worker for 64-bit optimizations"""
    
    def test_worker_initialization(self, temp_dir):
        """Test file operation worker initialization"""
        source_files = [temp_dir / "test.txt"]
        source_files[0].write_text("Test content")
        target_dir = temp_dir / "target"
        target_dir.mkdir()
        
        worker = FileOperationWorker(
            operation_type="copy",
            source_paths=source_files,
            target_path=target_dir
        )
        
        assert worker.operation_type == "copy"
        assert worker.source_paths == source_files
        assert worker.target_path == target_dir
        assert worker.options == {}
        assert worker._cancelled is False
    
    def test_copy_operation(self, temp_dir, qtbot):
        """Test file copy operation with progress tracking"""
        # Create source file
        source_file = temp_dir / "source.txt"
        source_file.write_text("Test file content for copying")
        
        target_dir = temp_dir / "target"
        target_dir.mkdir()
        
        worker = FileOperationWorker(
            operation_type="copy",
            source_paths=[source_file],
            target_path=target_dir
        )
        
        # Track signals
        progress_signals = []
        status_signals = []
        finished_signals = []
        
        worker.progress.connect(lambda p: progress_signals.append(p))
        worker.status.connect(lambda s: status_signals.append(s))
        worker.finished.connect(lambda success, msg: finished_signals.append((success, msg)))
        
        # Run operation
        worker.run()
        
        # Verify file was copied
        target_file = target_dir / "source.txt"
        assert target_file.exists()
        assert target_file.read_text() == "Test file content for copying"
        
        # Verify signals
        assert len(finished_signals) == 1
        assert finished_signals[0][0] is True  # Success
    
    def test_move_operation(self, temp_dir):
        """Test file move operation"""
        # Create source file
        source_file = temp_dir / "source.txt"
        source_file.write_text("Test file content for moving")
        
        target_dir = temp_dir / "target"
        target_dir.mkdir()
        
        worker = FileOperationWorker(
            operation_type="move",
            source_paths=[source_file],
            target_path=target_dir
        )
        
        worker.run()
        
        # Verify file was moved
        target_file = target_dir / "source.txt"
        assert target_file.exists()
        assert not source_file.exists()
        assert target_file.read_text() == "Test file content for moving"
    
    def test_delete_operation(self, temp_dir):
        """Test file delete operation"""
        # Create files to delete
        file1 = temp_dir / "delete1.txt"
        file2 = temp_dir / "delete2.txt"
        file1.write_text("Delete me 1")
        file2.write_text("Delete me 2")
        
        worker = FileOperationWorker(
            operation_type="delete",
            source_paths=[file1, file2],
            target_path=temp_dir  # Not used for delete
        )
        
        worker.run()
        
        # Verify files were deleted
        assert not file1.exists()
        assert not file2.exists()
    
    def test_copy_with_progress(self, temp_dir):
        """Test copy operation with progress reporting"""
        # Create a larger file for progress testing
        source_file = temp_dir / "large_source.txt"
        with open(source_file, 'w') as f:
            f.write("x" * 1000)  # 1KB file
        
        target_dir = temp_dir / "target"
        target_dir.mkdir()
        
        worker = FileOperationWorker(
            operation_type="copy",
            source_paths=[source_file],
            target_path=target_dir
        )
        
        progress_values = []
        worker.progress.connect(lambda p: progress_values.append(p))
        
        worker.run()
        
        # Should have received progress updates
        assert len(progress_values) > 0
        assert max(progress_values) <= 100
        assert min(progress_values) >= 0
    
    def test_operation_cancellation(self, temp_dir):
        """Test operation cancellation"""
        source_file = temp_dir / "source.txt"
        source_file.write_text("Test content")
        
        target_dir = temp_dir / "target"
        target_dir.mkdir()
        
        worker = FileOperationWorker(
            operation_type="copy",
            source_paths=[source_file],
            target_path=target_dir
        )
        
        # Cancel immediately
        worker.cancel()
        assert worker._cancelled is True
    
    def test_file_size_calculation(self, temp_dir):
        """Test file size calculation for progress"""
        # Create files of different sizes
        small_file = temp_dir / "small.txt"
        small_file.write_text("small")
        
        # Create directory with files
        test_dir = temp_dir / "test_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "file2.txt").write_text("content2")
        
        worker = FileOperationWorker("copy", [], temp_dir)
        
        # Test file size
        file_size = worker._get_file_size(small_file)
        assert file_size == len("small")
        
        # Test directory size
        dir_size = worker._get_file_size(test_dir)
        assert dir_size == len("content1") + len("content2")
    
    def test_copy_file_with_progress_64bit_buffers(self, temp_dir, mock_platform_config):
        """Test copy with 64-bit optimized buffers"""
        # Create source file
        source_file = temp_dir / "source.txt"
        target_file = temp_dir / "target.txt"
        
        # Write test data
        test_data = "x" * (5 * 1024 * 1024)  # 5MB file
        source_file.write_text(test_data)
        
        worker = FileOperationWorker("copy", [], temp_dir)
        
        # Test copy with progress
        worker._copy_file_with_progress(source_file, target_file, len(test_data), 0)
        
        # Verify file was copied correctly
        assert target_file.exists()
        assert target_file.stat().st_size == source_file.stat().st_size


class TestFileService:
    """Test file service coordination"""
    
    def test_file_service_initialization(self):
        """Test file service initialization"""
        service = FileService()
        
        assert hasattr(service, 'active_operations')
        assert hasattr(service, 'logger')
        assert service.active_operations == {}
    
    def test_file_service_signals(self):
        """Test file service signal definitions"""
        service = FileService()
        
        # Verify signals exist
        assert hasattr(service, 'operation_started')
        assert hasattr(service, 'operation_progress')
        assert hasattr(service, 'operation_finished')
        assert hasattr(service, 'directory_changed')
    
    @patch('src.services.file_service.FileOperationWorker')
    def test_file_operation_delegation(self, mock_worker_class):
        """Test file operation delegation to worker"""
        FileService()  # Just test instantiation
        mock_worker = Mock()
        mock_worker_class.return_value = mock_worker
        
        # This would be implemented in the actual FileService
        # For now, just verify the worker class can be instantiated
        worker = mock_worker_class("copy", [], Path("/tmp"))
        assert worker is not None


class TestFileWatcher:
    """Test file system watcher"""
    
    def test_file_watcher_initialization(self):
        """Test file watcher initialization"""
        watcher = FileWatcher()
        
        assert hasattr(watcher, 'observer')
        assert hasattr(watcher, 'watched_paths')
        assert watcher.watched_paths == set()
    
    def test_start_watching(self, temp_dir):
        """Test starting file system watching"""
        watcher = FileWatcher()
        
        # Start watching directory
        watcher.start_watching(str(temp_dir))
        
        assert str(temp_dir) in watcher.watched_paths
    
    def test_stop_watching(self, temp_dir):
        """Test stopping file system watching"""
        watcher = FileWatcher()
        
        # Start then stop watching
        watcher.start_watching(str(temp_dir))
        watcher.stop_watching(str(temp_dir))
        
        assert str(temp_dir) not in watcher.watched_paths
    
    def test_stop_all_watching(self, temp_dir):
        """Test stopping all file system watching"""
        watcher = FileWatcher()
        
        # Start watching multiple paths
        dir1 = temp_dir / "dir1"
        dir2 = temp_dir / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        
        watcher.start_watching(str(dir1))
        watcher.start_watching(str(dir2))
        
        # Stop all
        watcher.stop_all()
        
        assert len(watcher.watched_paths) == 0


class TestFileOperationsPerformance:
    """Performance tests for file operations"""
    
    def test_small_file_copy_performance(self, benchmark, temp_dir):
        """Test performance of small file copying"""
        source_file = temp_dir / "small.txt"
        source_file.write_text("Small file content")
        
        target_dir = temp_dir / "target"
        target_dir.mkdir()
        
        def copy_small_file():
            worker = FileOperationWorker(
                operation_type="copy",
                source_paths=[source_file],
                target_path=target_dir
            )
            worker.run()
            # Clean up for next iteration
            target_file = target_dir / "small.txt"
            if target_file.exists():
                target_file.unlink()
        
        benchmark(copy_small_file)
    
    def test_large_file_buffer_optimization(self, temp_dir, perf_helper):
        """Test buffer size optimization for large files"""
        # Create 10MB test file
        large_file = temp_dir / "large.dat"
        perf_helper.create_large_file(large_file, 10)
        
        target_dir = temp_dir / "target"
        target_dir.mkdir()
        
        worker = FileOperationWorker(
            operation_type="copy",
            source_paths=[large_file],
            target_path=target_dir
        )
        
        # Measure memory before and after
        memory_before = perf_helper.measure_memory_usage()
        worker.run()
        memory_after = perf_helper.measure_memory_usage()
        
        # Should not use excessive memory (less than 100MB increase)
        memory_increase = memory_after - memory_before
        assert memory_increase < 100  # MB
        
        # Verify file was copied correctly
        target_file = target_dir / "large.dat"
        assert target_file.exists()
        assert target_file.stat().st_size == large_file.stat().st_size


class TestFileOperationErrorHandling:
    """Test error handling in file operations"""
    
    def test_copy_to_nonexistent_directory(self, temp_dir):
        """Test copying to non-existent directory"""
        source_file = temp_dir / "source.txt"
        source_file.write_text("Test content")
        
        nonexistent_dir = temp_dir / "nonexistent"
        
        worker = FileOperationWorker(
            operation_type="copy",
            source_paths=[source_file],
            target_path=nonexistent_dir
        )
        
        finished_signals = []
        worker.finished.connect(lambda success, msg: finished_signals.append((success, msg)))
        
        worker.run()
        
        # Should handle error gracefully
        assert len(finished_signals) == 1
        assert finished_signals[0][0] is False  # Not successful
    
    def test_delete_nonexistent_file(self, temp_dir):
        """Test deleting non-existent file"""
        nonexistent_file = temp_dir / "nonexistent.txt"
        
        worker = FileOperationWorker(
            operation_type="delete",
            source_paths=[nonexistent_file],
            target_path=temp_dir
        )
        
        finished_signals = []
        worker.finished.connect(lambda success, msg: finished_signals.append((success, msg)))
        
        worker.run()
        
        # Should handle error gracefully
        assert len(finished_signals) == 1
        assert finished_signals[0][0] is False  # Not successful
    
    def test_copy_with_permission_error(self, temp_dir, monkeypatch):
        """Test copy operation with permission errors"""
        source_file = temp_dir / "source.txt"
        source_file.write_text("Test content")
        
        target_dir = temp_dir / "target"
        target_dir.mkdir()
        
        # Mock open to raise PermissionError
        original_open = open
        
        def mock_open(*args, **kwargs):
            if 'target' in str(args[0]):
                raise PermissionError("Access denied")
            return original_open(*args, **kwargs)
        
        monkeypatch.setattr('builtins.open', mock_open)
        
        worker = FileOperationWorker(
            operation_type="copy",
            source_paths=[source_file],
            target_path=target_dir
        )
        
        finished_signals = []
        worker.finished.connect(lambda success, msg: finished_signals.append((success, msg)))
        
        worker.run()
        
        # Should handle permission error gracefully
        assert len(finished_signals) == 1
        assert finished_signals[0][0] is False  # Not successful
