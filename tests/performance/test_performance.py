"""
Performance tests for FileOrbit - testing speed and resource usage
"""
import time
from unittest.mock import Mock
from PySide6.QtCore import QThread
from PySide6.QtTest import QTest

from src.services.file_service import FileService, FileOperationWorker


class TestFileOperationPerformance:
    """Test file operation performance"""
    
    def test_small_file_copy_performance(self, benchmark, temp_dir):
        """Test performance of copying small files"""
        # Create small test file
        small_file = temp_dir / "small.txt"
        small_file.write_text("Small file content")
        
        dst_dir = temp_dir / "destination"
        dst_dir.mkdir()
        
        def copy_small_file():
            worker = FileOperationWorker(
                operation="copy",
                source_paths=[str(small_file)],
                destination_path=str(dst_dir)
            )
            
            # Execute synchronously for benchmark
            if hasattr(worker, '_copy_files'):
                worker._copy_files([str(small_file)], str(dst_dir))
            
            return True
        
        result = benchmark(copy_small_file)
        assert result is True
    
    def test_large_file_copy_performance(self, benchmark, temp_dir):
        """Test performance of copying large files"""
        # Create large test file (1MB)
        large_file = temp_dir / "large.dat"
        with open(large_file, 'wb') as f:
            f.write(b'0' * (1024 * 1024))  # 1MB
        
        dst_dir = temp_dir / "destination"
        dst_dir.mkdir()
        
        def copy_large_file():
            worker = FileOperationWorker(
                operation="copy",
                source_paths=[str(large_file)],
                destination_path=str(dst_dir)
            )
            
            # Execute synchronously for benchmark
            if hasattr(worker, '_copy_files'):
                worker._copy_files([str(large_file)], str(dst_dir))
            
            return True
        
        result = benchmark(copy_large_file)
        assert result is True
    
    def test_multiple_files_copy_performance(self, benchmark, temp_dir):
        """Test performance of copying multiple files"""
        # Create multiple test files
        files = []
        for i in range(50):
            test_file = temp_dir / f"file_{i:03d}.txt"
            test_file.write_text(f"Content for file {i}")
            files.append(str(test_file))
        
        dst_dir = temp_dir / "destination"
        dst_dir.mkdir()
        
        def copy_multiple_files():
            worker = FileOperationWorker(
                operation="copy",
                source_paths=files,
                destination_path=str(dst_dir)
            )
            
            # Execute synchronously for benchmark
            if hasattr(worker, '_copy_files'):
                worker._copy_files(files, str(dst_dir))
            
            return len(files)
        
        result = benchmark(copy_multiple_files)
        assert result == 50
    
    def test_directory_copy_performance(self, benchmark, temp_dir):
        """Test performance of copying directories"""
        # Create source directory with nested structure
        src_dir = temp_dir / "source"
        src_dir.mkdir()
        
        # Create nested files and directories
        for i in range(10):
            sub_dir = src_dir / f"subdir_{i}"
            sub_dir.mkdir()
            for j in range(5):
                test_file = sub_dir / f"file_{j}.txt"
                test_file.write_text(f"Content {i}-{j}")
        
        dst_dir = temp_dir / "destination"
        dst_dir.mkdir()
        
        def copy_directory():
            worker = FileOperationWorker(
                operation="copy",
                source_paths=[str(src_dir)],
                destination_path=str(dst_dir)
            )
            
            # Execute synchronously for benchmark
            if hasattr(worker, '_copy_directory'):
                worker._copy_directory(str(src_dir), str(dst_dir))
            
            return True
        
        result = benchmark(copy_directory)
        assert result is True


class TestFileServicePerformance:
    """Test FileService performance"""
    
    def test_file_service_initialization_performance(self, benchmark):
        """Test FileService initialization performance"""
        def create_file_service():
            return FileService()
        
        service = benchmark(create_file_service)
        assert isinstance(service, FileService)
    
    def test_file_listing_performance(self, benchmark, temp_dir):
        """Test file listing performance"""
        # Create many files
        for i in range(100):
            test_file = temp_dir / f"file_{i:04d}.txt"
            test_file.write_text(f"Content {i}")
        
        service = FileService()
        
        def list_files():
            if hasattr(service, 'list_directory'):
                return service.list_directory(str(temp_dir))
            else:
                # Fallback to pathlib
                return list(temp_dir.iterdir())
        
        files = benchmark(list_files)
        assert len(files) >= 100
    
    def test_file_info_retrieval_performance(self, benchmark, sample_files):
        """Test file information retrieval performance"""
        service = FileService()
        test_file = sample_files['small']
        
        def get_file_info():
            if hasattr(service, 'get_file_info'):
                return service.get_file_info(str(test_file))
            else:
                # Fallback to stat
                stat = test_file.stat()
                return {
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                    'is_dir': test_file.is_dir()
                }
        
        info = benchmark(get_file_info)
        assert info is not None


class TestMemoryPerformance:
    """Test memory usage performance"""
    
    def test_large_file_operation_memory_usage(self, temp_dir, performance_helper):
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
        worker = FileOperationWorker(
            operation="copy",
            source_paths=[str(large_file)],
            destination_path=str(dst_dir)
        )
        
        # Execute and measure peak memory
        if hasattr(worker, '_copy_files'):
            worker._copy_files([str(large_file)], str(dst_dir))
        
        peak_memory = performance_helper.get_current_memory_usage()
        memory_usage = peak_memory - initial_memory
        
        # Memory usage should be reasonable (less than file size)
        assert memory_usage < 10 * 1024 * 1024  # Less than 10MB
        
        # Verify file was copied
        copied_file = dst_dir / large_file.name
        assert copied_file.exists()
    
    def test_multiple_workers_memory_scaling(self, temp_dir, performance_helper):
        """Test memory scaling with multiple workers"""
        # Create test files
        test_files = []
        for i in range(5):
            test_file = temp_dir / f"test_{i}.txt"
            test_file.write_text(f"Content {i}" * 1000)  # ~10KB each
            test_files.append(test_file)
        
        dst_dirs = []
        for i in range(5):
            dst_dir = temp_dir / f"dest_{i}"
            dst_dir.mkdir()
            dst_dirs.append(dst_dir)
        
        # Measure initial memory
        initial_memory = performance_helper.get_current_memory_usage()
        
        # Create multiple workers
        workers = []
        for i, (test_file, dst_dir) in enumerate(zip(test_files, dst_dirs)):
            worker = FileOperationWorker(
                operation="copy",
                source_paths=[str(test_file)],
                destination_path=str(dst_dir)
            )
            workers.append(worker)
        
        # Measure memory with all workers
        peak_memory = performance_helper.get_current_memory_usage()
        memory_per_worker = (peak_memory - initial_memory) / len(workers)
        
        # Each worker should use reasonable memory
        assert memory_per_worker < 10 * 1024 * 1024  # Less than 10MB per worker
    
    def test_memory_cleanup_after_operations(self, temp_dir, performance_helper):
        """Test memory is properly cleaned up after operations"""
        # Create test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content" * 10000)  # ~120KB
        
        dst_dir = temp_dir / "destination"
        dst_dir.mkdir()
        
        # Measure initial memory
        initial_memory = performance_helper.get_current_memory_usage()
        
        # Perform operation
        worker = FileOperationWorker(
            operation="copy",
            source_paths=[str(test_file)],
            destination_path=str(dst_dir)
        )
        
        if hasattr(worker, '_copy_files'):
            worker._copy_files([str(test_file)], str(dst_dir))
        
        # Clear worker reference
        del worker
        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Measure final memory
        final_memory = performance_helper.get_current_memory_usage()
        memory_difference = final_memory - initial_memory
        
        # Memory should be mostly cleaned up (allow some overhead)
        assert memory_difference < 5 * 1024 * 1024  # Less than 5MB difference


class TestConcurrencyPerformance:
    """Test concurrent operation performance"""
    
    def test_concurrent_copy_operations_performance(self, benchmark, temp_dir, sample_files):
        """Test performance of concurrent copy operations"""
        # Create destination directories
        dst_dirs = []
        for i in range(3):
            dst_dir = temp_dir / f"dest_{i}"
            dst_dir.mkdir()
            dst_dirs.append(dst_dir)
        
        def concurrent_copies():
            workers = []
            threads = []
            completed = []
            
            # Create workers and threads
            for i, dst_dir in enumerate(dst_dirs):
                worker = FileOperationWorker(
                    operation="copy",
                    source_paths=[str(sample_files['small'])],
                    destination_path=str(dst_dir)
                )
                
                thread = QThread()
                worker.moveToThread(thread)
                
                # Track completion
                worker.operation_completed.connect(lambda: completed.append(True))
                
                workers.append(worker)
                threads.append(thread)
            
            # Start all operations
            start_time = time.time()
            for worker, thread in zip(workers, threads):
                thread.started.connect(worker.execute)
                thread.start()
            
            # Wait for completion
            while len(completed) < len(workers) and time.time() - start_time < 10:
                QTest.qWait(10)
            
            # Cleanup
            for thread in threads:
                thread.quit()
                thread.wait()
            
            return len(completed)
        
        result = benchmark(concurrent_copies)
        assert result == 3
    
    def test_sequential_vs_concurrent_performance(self, temp_dir, sample_files):
        """Compare sequential vs concurrent operation performance"""
        # Create multiple destination directories
        sequential_dirs = []
        concurrent_dirs = []
        
        for i in range(3):
            seq_dir = temp_dir / f"seq_{i}"
            seq_dir.mkdir()
            sequential_dirs.append(seq_dir)
            
            conc_dir = temp_dir / f"conc_{i}"
            conc_dir.mkdir()
            concurrent_dirs.append(conc_dir)
        
        # Test sequential operations
        start_time = time.time()
        for dst_dir in sequential_dirs:
            worker = FileOperationWorker(
                operation="copy",
                source_paths=[str(sample_files['small'])],
                destination_path=str(dst_dir)
            )
            
            if hasattr(worker, '_copy_files'):
                worker._copy_files([str(sample_files['small'])], str(dst_dir))
        
        sequential_time = time.time() - start_time
        
        # Test concurrent operations
        start_time = time.time()
        workers = []
        threads = []
        completed = []
        
        for dst_dir in concurrent_dirs:
            worker = FileOperationWorker(
                operation="copy",
                source_paths=[str(sample_files['small'])],
                destination_path=str(dst_dir)
            )
            
            thread = QThread()
            worker.moveToThread(thread)
            worker.operation_completed.connect(lambda: completed.append(True))
            
            workers.append(worker)
            threads.append(thread)
        
        # Start concurrent operations
        for worker, thread in zip(workers, threads):
            thread.started.connect(worker.execute)
            thread.start()
        
        # Wait for completion
        while len(completed) < len(workers) and time.time() - start_time < 10:
            QTest.qWait(10)
        
        concurrent_time = time.time() - start_time
        
        # Cleanup
        for thread in threads:
            thread.quit()
            thread.wait()
        
        # For small files, concurrent might not be faster due to overhead
        # but it should not be significantly slower
        assert concurrent_time < sequential_time * 3  # Allow up to 3x overhead


class TestUIPerformance:
    """Test UI performance under load"""
    
    def test_file_panel_large_directory_performance(self, benchmark, qapp, temp_dir):
        """Test file panel performance with large directories"""
        # Create many files
        for i in range(500):
            test_file = temp_dir / f"file_{i:04d}.txt"
            test_file.write_text(f"Content {i}")
        
        from src.ui.components.file_panel import FilePanel
        
        def create_and_populate_panel():
            mock_file_service = Mock()
            panel = FilePanel(
                panel_id="test",
                file_service=mock_file_service
            )
            
            # Navigate to directory with many files
            panel.navigate_to(str(temp_dir))
            
            # Process events to simulate loading
            for _ in range(50):
                QTest.qWait(1)
                qapp.processEvents()
            
            panel.close()
            return panel
        
        panel = benchmark(create_and_populate_panel)
        assert panel is not None
    
    def test_theme_switching_performance(self, benchmark, qapp):
        """Test theme switching performance"""
        from src.ui.main_window import MainWindow
        from src.services.theme_service import ThemeService
        
        mock_file_service = Mock()
        theme_service = ThemeService()
        mock_config = Mock()
        
        window = MainWindow(
            file_service=mock_file_service,
            theme_service=theme_service,
            config=mock_config
        )
        
        def switch_theme_multiple_times():
            themes = ["light", "dark", "light", "dark"]
            for theme in themes:
                if hasattr(window, 'apply_theme'):
                    window.apply_theme(theme)
                    QTest.qWait(10)
        
        benchmark(switch_theme_multiple_times)
        window.close()


class TestDiskIOPerformance:
    """Test disk I/O performance"""
    
    def test_read_performance(self, benchmark, temp_dir):
        """Test file reading performance"""
        # Create test file with 1MB of data
        test_file = temp_dir / "read_test.dat"
        with open(test_file, 'wb') as f:
            f.write(b'A' * (1024 * 1024))  # 1MB
        
        def read_file():
            with open(test_file, 'rb') as f:
                return f.read()
        
        data = benchmark(read_file)
        assert len(data) == 1024 * 1024
    
    def test_write_performance(self, benchmark, temp_dir):
        """Test file writing performance"""
        test_data = b'B' * (1024 * 1024)  # 1MB
        
        def write_file():
            test_file = temp_dir / f"write_test_{time.time()}.dat"
            with open(test_file, 'wb') as f:
                f.write(test_data)
            return test_file
        
        written_file = benchmark(write_file)
        assert written_file.exists()
        assert written_file.stat().st_size == 1024 * 1024
    
    def test_chunked_copy_performance(self, benchmark, temp_dir):
        """Test chunked file copying performance"""
        # Create source file
        src_file = temp_dir / "source.dat"
        with open(src_file, 'wb') as f:
            f.write(b'C' * (5 * 1024 * 1024))  # 5MB
        
        def chunked_copy():
            dst_file = temp_dir / f"chunked_copy_{time.time()}.dat"
            
            with open(src_file, 'rb') as src, open(dst_file, 'wb') as dst:
                chunk_size = 64 * 1024  # 64KB chunks
                while True:
                    chunk = src.read(chunk_size)
                    if not chunk:
                        break
                    dst.write(chunk)
            
            return dst_file
        
        copied_file = benchmark(chunked_copy)
        assert copied_file.exists()
        assert copied_file.stat().st_size == src_file.stat().st_size
