"""
Testing Framework Foundation

This module provides base classes, utilities, and fixtures for the FileOrbit testing suite.
It includes mocking support, test data factories, and common test patterns.
"""

import sys
import tempfile
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch
from contextlib import contextmanager

import pytest
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtTest import QTest

from src.core.service_container import ServiceContainer
from src.core.interfaces import (
    IIconProvider, IContextMenuProvider, INavigationProvider,
    IShellIntegration, IApplicationDiscovery, IFileService
)


class TestBase:
    """Base class for all tests providing common functionality."""
    
    def setup_method(self):
        """Set up method called before each test."""
        self.temp_dir = None
        self.test_files = []
        self.mocks = {}
    
    def teardown_method(self):
        """Clean up method called after each test."""
        # Clean up temporary files
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Clean up test files
        for file_path in self.test_files:
            try:
                if Path(file_path).exists():
                    if Path(file_path).is_dir():
                        shutil.rmtree(file_path, ignore_errors=True)
                    else:
                        Path(file_path).unlink()
            except Exception:
                pass  # Ignore cleanup errors
    
    def create_temp_dir(self) -> Path:
        """Create a temporary directory for testing."""
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp(prefix="fileorbit_test_")
        return Path(self.temp_dir)
    
    def create_test_file(self, name: str, content: str = "", parent: Optional[Path] = None) -> Path:
        """Create a test file with optional content."""
        if parent is None:
            parent = self.create_temp_dir()
        
        file_path = parent / name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        self.test_files.append(str(file_path))
        return file_path
    
    def create_test_directory(self, name: str, parent: Optional[Path] = None) -> Path:
        """Create a test directory."""
        if parent is None:
            parent = self.create_temp_dir()
        
        dir_path = parent / name
        dir_path.mkdir(parents=True, exist_ok=True)
        self.test_files.append(str(dir_path))
        return dir_path
    
    def create_mock(self, name: str, spec: Optional[type] = None) -> Mock:
        """Create and store a mock object."""
        mock_obj = Mock(spec=spec) if spec else Mock()
        self.mocks[name] = mock_obj
        return mock_obj
    
    def get_mock(self, name: str) -> Mock:
        """Get a previously created mock object."""
        return self.mocks.get(name)


class QtTestBase(TestBase):
    """Base class for Qt-based tests."""
    
    @classmethod
    def setup_class(cls):
        """Set up QApplication for Qt tests."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setup_method(self):
        """Set up method for Qt tests."""
        super().setup_method()
        self.widgets = []
    
    def teardown_method(self):
        """Clean up method for Qt tests."""
        super().teardown_method()
        
        # Clean up widgets
        for widget in self.widgets:
            if widget:
                widget.close()
                widget.deleteLater()
        
        # Process events to ensure cleanup
        QTest.qWait(10)
    
    def create_widget(self, widget_class, *args, **kwargs) -> QWidget:
        """Create and track a widget for cleanup."""
        widget = widget_class(*args, **kwargs)
        self.widgets.append(widget)
        return widget
    
    def process_events(self, timeout: int = 100):
        """Process Qt events with timeout."""
        QTest.qWait(timeout)


class ServiceTestBase(TestBase):
    """Base class for service tests with dependency injection."""
    
    def setup_method(self):
        """Set up method for service tests."""
        super().setup_method()
        self.container = ServiceContainer()
        self.setup_container()
    
    def setup_container(self):
        """Override to set up service container with test dependencies."""
        pass
    
    def register_mock_service(self, interface_type: type, mock_name: Optional[str] = None) -> Mock:
        """Register a mock service in the container."""
        if mock_name is None:
            mock_name = f"mock_{interface_type.__name__}"
        
        mock_service = self.create_mock(mock_name, spec=interface_type)
        self.container.register_singleton(interface_type, mock_service)
        return mock_service


class MockFactory:
    """Factory for creating commonly used mocks."""
    
    @staticmethod
    def create_icon_provider() -> Mock:
        """Create a mock icon provider."""
        mock = Mock(spec=IIconProvider)
        mock.get_file_icon.return_value = Mock()
        mock.get_folder_icon.return_value = Mock()
        mock.get_context_menu_icon.return_value = Mock()
        mock.get_cache_stats.return_value = {
            'cache_size': 0, 'cache_hits': 0, 'cache_misses': 0,
            'hit_rate': 0.0, 'total_requests': 0
        }
        return mock
    
    @staticmethod
    def create_context_menu_provider() -> Mock:
        """Create a mock context menu provider."""
        mock = Mock(spec=IContextMenuProvider)
        mock.show_file_context_menu.return_value = True
        mock.show_empty_area_context_menu.return_value = True
        mock.get_context_files.return_value = []
        return mock
    
    @staticmethod
    def create_navigation_provider() -> Mock:
        """Create a mock navigation provider."""
        mock = Mock(spec=INavigationProvider)
        mock.create_new_tab.return_value = 0
        mock.navigate_to.return_value = True
        mock.go_back.return_value = True
        mock.go_forward.return_value = True
        mock.go_up.return_value = True
        mock.get_current_path.return_value = Path.home()
        mock.get_tab_count.return_value = 1
        mock.get_bookmarks.return_value = []
        return mock
    
    @staticmethod
    def create_shell_integration() -> Mock:
        """Create a mock shell integration."""
        mock = Mock(spec=IShellIntegration)
        mock.get_context_menu_actions.return_value = []
        mock.get_empty_area_context_menu.return_value = []
        mock.get_shell_extensions_for_file.return_value = []
        mock.execute_shell_command.return_value = True
        return mock
    
    @staticmethod
    def create_application_discovery() -> Mock:
        """Create a mock application discovery service."""
        mock = Mock(spec=IApplicationDiscovery)
        mock.discover_all_installed_applications.return_value = []
        mock.discover_applications_for_file_type.return_value = []
        mock.get_application_info.return_value = None
        return mock
    
    @staticmethod
    def create_file_service() -> Mock:
        """Create a mock file service."""
        mock = Mock(spec=IFileService)
        mock.copy_files.return_value = True
        mock.move_files.return_value = True
        mock.delete_files.return_value = True
        mock.create_folder.return_value = True
        mock.rename_file.return_value = True
        mock.get_file_info.return_value = {}
        return mock


class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_file_list(count: int = 5, base_path: Optional[Path] = None) -> List[Path]:
        """Create a list of test file paths."""
        if base_path is None:
            base_path = Path("/test")
        
        return [base_path / f"file_{i}.txt" for i in range(count)]
    
    @staticmethod
    def create_folder_list(count: int = 3, base_path: Optional[Path] = None) -> List[Path]:
        """Create a list of test folder paths."""
        if base_path is None:
            base_path = Path("/test")
        
        return [base_path / f"folder_{i}" for i in range(count)]
    
    @staticmethod
    def create_context_menu_actions() -> List[Dict[str, Any]]:
        """Create sample context menu actions."""
        return [
            {
                "text": "Open",
                "action": "open",
                "icon": "file_open",
                "bold": True
            },
            {
                "text": "Edit",
                "action": "edit",
                "icon": "editor"
            },
            {
                "separator": True
            },
            {
                "text": "Copy",
                "action": "copy",
                "icon": "copy",
                "shortcut": "Ctrl+C"
            },
            {
                "text": "Cut",
                "action": "cut",
                "icon": "cut",
                "shortcut": "Ctrl+X"
            }
        ]
    
    @staticmethod
    def create_application_info(name: str = "TestApp") -> Dict[str, Any]:
        """Create sample application information."""
        return {
            "name": name,
            "display_name": f"{name} Display Name",
            "path": f"C:\\Program Files\\{name}\\{name.lower()}.exe",
            "version": "1.0.0",
            "publisher": "Test Publisher",
            "icon_path": f"C:\\Program Files\\{name}\\{name.lower()}.exe,0"
        }


@contextmanager
def temp_directory():
    """Context manager for temporary directory."""
    temp_dir = tempfile.mkdtemp(prefix="fileorbit_test_")
    try:
        yield Path(temp_dir)
    finally:
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


@contextmanager
def mock_registry():
    """Context manager for mocking Windows registry operations."""
    with patch('winreg.OpenKey'), \
         patch('winreg.EnumKey'), \
         patch('winreg.EnumValue'), \
         patch('winreg.QueryValueEx'), \
         patch('winreg.CloseKey'):
        yield


@contextmanager
def mock_file_system():
    """Context manager for mocking file system operations."""
    with patch('pathlib.Path.exists'), \
         patch('pathlib.Path.is_file'), \
         patch('pathlib.Path.is_dir'), \
         patch('pathlib.Path.stat'), \
         patch('os.listdir'), \
         patch('os.path.exists'):
        yield


class TestFixtures:
    """Common test fixtures."""
    
    @staticmethod
    @pytest.fixture
    def temp_dir():
        """Fixture for temporary directory."""
        with temp_directory() as temp_path:
            yield temp_path
    
    @staticmethod
    @pytest.fixture
    def mock_container():
        """Fixture for mock service container."""
        container = ServiceContainer()
        yield container
        container.clear()
    
    @staticmethod
    @pytest.fixture
    def qt_app():
        """Fixture for Qt application."""
        if not QApplication.instance():
            app = QApplication(sys.argv)
            yield app
        else:
            yield QApplication.instance()


# Pytest markers for easy test categorization
def unit_test(func):
    """Mark a test as a unit test."""
    return pytest.mark.unit(func)


def integration_test(func):
    """Mark a test as an integration test."""
    return pytest.mark.integration(func)


def ui_test(func):
    """Mark a test as a UI test."""
    return pytest.mark.ui(func)


def slow_test(func):
    """Mark a test as slow."""
    return pytest.mark.slow(func)


def windows_only_test(func):
    """Mark a test as Windows-specific."""
    return pytest.mark.windows(func)


def performance_test(func):
    """Mark a test as a performance test."""
    return pytest.mark.performance(func)


# Custom assertions
def assert_path_exists(path: Path, message: str = ""):
    """Assert that a path exists."""
    assert path.exists(), f"Path does not exist: {path}. {message}"


def assert_path_not_exists(path: Path, message: str = ""):
    """Assert that a path does not exist."""
    assert not path.exists(), f"Path should not exist: {path}. {message}"


def assert_is_file(path: Path, message: str = ""):
    """Assert that a path is a file."""
    assert path.is_file(), f"Path is not a file: {path}. {message}"


def assert_is_directory(path: Path, message: str = ""):
    """Assert that a path is a directory."""
    assert path.is_dir(), f"Path is not a directory: {path}. {message}"


def assert_mock_called_with_path(mock_method: Mock, expected_path: Path):
    """Assert that a mock was called with a specific path."""
    mock_method.assert_called()
    actual_path = mock_method.call_args[0][0]
    assert Path(actual_path) == expected_path, f"Expected {expected_path}, got {actual_path}"