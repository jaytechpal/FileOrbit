# Test Configuration and Fixtures
import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from platform_config import PlatformConfig


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for Qt tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit - let pytest handle cleanup


@pytest.fixture
def temp_dir():
    """Create temporary directory for file operations tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_files(temp_dir):
    """Create sample files for testing"""
    files = {}
    
    # Small text file
    small_file = temp_dir / "small.txt"
    small_file.write_text("This is a small test file.")
    files['small'] = small_file
    
    # Medium file (1MB)
    medium_file = temp_dir / "medium.dat"
    with open(medium_file, 'wb') as f:
        f.write(b'0' * (1024 * 1024))  # 1MB
    files['medium'] = medium_file
    
    # Directory structure
    sub_dir = temp_dir / "subdir"
    sub_dir.mkdir()
    (sub_dir / "nested.txt").write_text("Nested file content")
    files['directory'] = sub_dir
    
    return files


@pytest.fixture
def mock_platform_config():
    """Mock platform configuration for testing"""
    config = Mock(spec=PlatformConfig)
    config.is_64bit = True
    config.system_memory = 16  # 16GB
    config.cpu_count = 8
    config.platform_name = 'windows'
    config.architecture = 'amd64'
    
    config.get_optimal_buffer_size.return_value = 4 * 1024 * 1024  # 4MB
    config.get_max_concurrent_operations.return_value = 6
    config.get_directory_scan_batch_size.return_value = 5000
    config.supports_memory_mapping.return_value = True
    config.get_cache_size_mb.return_value = 250
    
    config.get_platform_specific_settings.return_value = {
        'is_64bit': True,
        'buffer_size': 4 * 1024 * 1024,
        'max_concurrent_ops': 6,
        'batch_size': 5000,
        'cache_size_mb': 250,
        'supports_memory_mapping': True,
        'system_memory_gb': 16,
        'cpu_cores': 8,
        'platform': 'windows',
        'architecture': 'amd64',
        'use_win32_apis': True,
        'file_attributes': True,
        'junction_support': True,
    }
    
    return config


@pytest.fixture
def mock_drive_info():
    """Mock drive information for testing"""
    return {
        'letter': 'C',
        'path': 'C:\\',
        'name': 'C:',
        'total_gb': 500.0,
        'used_gb': 250.0,
        'free_gb': 250.0,
        'usage_percent': 50.0
    }


class QtTestHelper:
    """Helper class for Qt testing operations"""
    
    @staticmethod
    def click_widget(widget, button=Qt.LeftButton, delay=100):
        """Click a widget with optional delay"""
        QTest.mouseClick(widget, button)
        QTest.qWait(delay)
    
    @staticmethod
    def key_sequence(widget, key_sequence, delay=100):
        """Send key sequence to widget"""
        QTest.keySequence(widget, key_sequence)
        QTest.qWait(delay)
    
    @staticmethod
    def wait_for_signal(signal, timeout=5000):
        """Wait for a signal to be emitted"""
        import time
        start_time = time.time()
        received = []
        
        def slot(*args):
            received.extend(args)
        
        signal.connect(slot)
        
        while not received and (time.time() - start_time) * 1000 < timeout:
            QApplication.processEvents()
            time.sleep(0.01)
        
        return received


@pytest.fixture
def qt_helper():
    """Provide Qt testing helper"""
    return QtTestHelper


# Performance testing helpers
class PerformanceHelper:
    """Helper for performance testing"""
    
    @staticmethod
    def create_large_file(path, size_mb):
        """Create a large file for performance testing"""
        with open(path, 'wb') as f:
            chunk_size = 1024 * 1024  # 1MB chunks
            for _ in range(size_mb):
                f.write(b'0' * chunk_size)
    
    @staticmethod
    def measure_memory_usage():
        """Measure current memory usage"""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB


@pytest.fixture
def perf_helper():
    """Provide performance testing helper"""
    return PerformanceHelper


# Mock Windows API for cross-platform testing
@pytest.fixture
def mock_windows_api(monkeypatch):
    """Mock Windows API calls for testing on any platform"""
    if os.name != 'nt':
        # Mock Windows-specific modules
        mock_ctypes = MagicMock()
        mock_ctypes.windll.kernel32.GetDriveTypeW.return_value = 3  # DRIVE_FIXED
        mock_ctypes.windll.mpr.WNetGetConnectionW.return_value = 1  # Not connected
        
        monkeypatch.setattr('src.ui.components.sidebar.ctypes', mock_ctypes)
        
        # Mock wintypes
        mock_wintypes = MagicMock()
        mock_wintypes.DWORD = lambda x: x
        monkeypatch.setattr('src.ui.components.sidebar.wintypes', mock_wintypes)


# Test data generators
def generate_test_files(base_path, count=100):
    """Generate multiple test files"""
    files = []
    for i in range(count):
        file_path = base_path / f"test_file_{i:03d}.txt"
        file_path.write_text(f"Test file {i} content")
        files.append(file_path)
    return files


def generate_directory_structure(base_path, depth=3, files_per_dir=10):
    """Generate nested directory structure for testing"""
    def create_level(path, current_depth):
        if current_depth <= 0:
            return
        
        for i in range(files_per_dir):
            file_path = path / f"file_{current_depth}_{i}.txt"
            file_path.write_text(f"Content at depth {current_depth}, file {i}")
        
        for i in range(3):  # 3 subdirectories per level
            sub_path = path / f"subdir_{current_depth}_{i}"
            sub_path.mkdir()
            create_level(sub_path, current_depth - 1)
    
    create_level(base_path, depth)
