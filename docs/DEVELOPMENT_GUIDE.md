# FileOrbit Development Guide

## Development Environment Setup

### Prerequisites (64-bit Development)

1. **Python 3.8+ (64-bit)** with development headers - 32-bit Python not supported
2. **Git** for version control
3. **Code Editor** (VS Code recommended with Python extension)
4. **Qt6 Development Tools** (optional, for UI design)
5. **64-bit System** - Development requires x64 architecture

### System Requirements for Development
- **Architecture**: x64 (64-bit) development environment only
- **Memory**: 8GB+ RAM recommended for development (16GB+ for large file testing)
- **Python**: 64-bit Python 3.8+ installation
- **Dependencies**: All packages must be 64-bit compatible

### Initial Setup

```bash
# Clone repository
git clone https://github.com/jaypalweb/FileOrbit.git
cd FileOrbit

# Verify 64-bit Python installation
python -c "import sys; print('64-bit:', sys.maxsize > 2**32)"

# Create development environment
python -m venv fileorbit-dev
source fileorbit-dev/bin/activate  # Linux/macOS
fileorbit-dev\Scripts\activate      # Windows

# Install development dependencies (64-bit)
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Test 64-bit optimizations
python platform_config.py
```

### Development Dependencies

Create `requirements-dev.txt`:
```
pytest>=7.0.0
pytest-qt>=4.0.0
pytest-cov>=4.0.0
black>=22.0.0
flake8>=4.0.0
mypy>=0.950
pre-commit>=2.20.0
sphinx>=5.0.0
sphinx-rtd-theme>=1.0.0
memory_profiler>=0.60.0    # For 64-bit memory profiling
psutil>=5.9.0              # Required for platform detection
```

## Code Architecture

### Project Structure

```
FileOrbit/
├── src/                    # Source code
│   ├── core/              # Core application logic with 64-bit optimizations
│   ├── ui/                # User interface components
│   ├── services/          # Business logic services with memory management
│   ├── utils/             # Utility functions
│   └── config/            # Configuration management
├── platform_config.py     # 64-bit system optimization configuration
├── tests/                 # Test suite including 64-bit performance tests
├── docs/                  # Documentation
├── resources/             # Static resources
├── version_info.txt       # Windows 64-bit executable version info
├── AUDIT_REPORT_64BIT.md  # Comprehensive 64-bit compatibility audit
└── scripts/               # Build and utility scripts
```

### Design Patterns

FileOrbit follows these architectural patterns optimized for 64-bit systems:

1. **Model-View-Controller (MVC)**:
   - Models: Data structures and file system interaction with 64-bit support
   - Views: UI components and user interaction
   - Controllers: Business logic with memory-aware operations

2. **Signal-Slot Pattern**:
   - Qt's event-driven communication
   - Loose coupling between components
   - Asynchronous operation support with CPU core scaling

3. **Service Layer Pattern**:
   - Separation of business logic with 64-bit optimizations
   - Reusable service components with memory management
   - Dependency injection with platform configuration

4. **Observer Pattern**:
   - File system change monitoring
   - UI state synchronization
   - Event propagation with efficient batching

5. **Strategy Pattern** (64-bit Optimization):
   - Platform-specific optimization strategies
   - Dynamic buffer sizing algorithms
   - Memory allocation strategies based on system capabilities

## Coding Standards

### Python Style Guide

FileOrbit follows PEP 8 with these specific guidelines:

#### Import Organization
```python
# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import QWidget, QVBoxLayout

# Local imports
from src.core.application import FileOrbitApp
from src.services.file_service import FileService
```

#### Class Structure
```python
class ComponentName(BaseClass):
    """Component description.
    
    Detailed explanation of component purpose,
    usage, and important considerations.
    """
    
    # Class-level constants
    DEFAULT_VALUE = "default"
    
    # Signals (for Qt components)
    signal_name = Signal(str)
    
    def __init__(self, parent=None):
        """Initialize component."""
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
    
    def public_method(self, param: str) -> bool:
        """Public method with type hints and docstring."""
        return self._private_method(param)
    
    def _private_method(self, param: str) -> bool:
        """Private method (prefix with underscore)."""
        # Implementation details
        pass
    
    def _setup_ui(self):
        """Initialize UI components."""
        pass
    
    def _connect_signals(self):
        """Connect signals and slots."""
        pass
```

#### Naming Conventions
- **Classes**: PascalCase (`FilePanel`, `ToolbarComponent`)
- **Functions/Methods**: snake_case (`setup_ui`, `handle_click`)
- **Variables**: snake_case (`current_path`, `selected_files`)
- **Constants**: UPPER_SNAKE_CASE (`DEFAULT_THEME`, `MAX_FILE_SIZE`)
- **Private members**: Leading underscore (`_internal_state`)

#### Documentation
```python
def complex_function(param1: str, param2: int = 0) -> dict:
    """Brief function description.
    
    Detailed explanation of function behavior,
    parameters, and return value.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter with default
        
    Returns:
        Dictionary containing result data with keys:
        - 'status': Operation status string
        - 'data': Result data or None
        
    Raises:
        ValueError: When param1 is empty
        FileNotFoundError: When specified file doesn't exist
        
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result['status'])
        'success'
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    
    # Implementation here
    return {'status': 'success', 'data': None}
```

### Qt/PySide6 Best Practices

#### Signal-Slot Connections
```python
# Prefer new-style connections
self.button.clicked.connect(self.on_button_clicked)

# Avoid old-style connections
# self.connect(self.button, SIGNAL("clicked()"), self.on_button_clicked)

# Use lambda for simple parameter passing
self.button.clicked.connect(lambda: self.on_action("button1"))

# Disconnect signals properly in cleanup
def cleanup(self):
    self.button.clicked.disconnect()
```

#### Threading Guidelines
```python
class FileWorker(QThread):
    """Worker thread for file operations."""
    
    progress_updated = Signal(int)
    operation_completed = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, operation, files):
        super().__init__()
        self.operation = operation
        self.files = files
    
    def run(self):
        """Execute file operation in background thread."""
        try:
            for i, file in enumerate(self.files):
                # Perform operation
                progress = int((i + 1) / len(self.files) * 100)
                self.progress_updated.emit(progress)
            
            self.operation_completed.emit({'status': 'success'})
        except Exception as e:
            self.error_occurred.emit(str(e))
```

#### Resource Management
```python
class ComponentWithResources(QWidget):
    """Component that manages resources properly."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker_thread = None
        self.setup_ui()
    
    def start_background_operation(self):
        """Start background operation with proper cleanup."""
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
        
        self.worker_thread = FileWorker()
        self.worker_thread.finished.connect(self.on_operation_finished)
        self.worker_thread.start()
    
    def closeEvent(self, event):
        """Handle component close event."""
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
        super().closeEvent(event)
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/                  # Unit tests
│   ├── test_core/        # Core module tests
│   ├── test_ui/          # UI component tests
│   └── test_services/    # Service layer tests
├── integration/          # Integration tests
├── fixtures/             # Test data and fixtures
└── conftest.py          # Pytest configuration
```

### Unit Testing

```python
import pytest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from src.ui.components.file_panel import FilePanel

class TestFilePanel:
    """Test suite for FilePanel component."""
    
    @pytest.fixture
    def file_panel(self, qtbot):
        """Create FilePanel instance for testing."""
        panel = FilePanel("test_panel")
        qtbot.addWidget(panel)
        return panel
    
    def test_panel_activation_signal(self, qtbot, file_panel):
        """Test panel activation signal emission."""
        with qtbot.waitSignal(file_panel.panel_activated) as blocker:
            qtbot.mouseClick(file_panel, Qt.LeftButton)
        
        assert blocker.args[0] == "test_panel"
    
    def test_navigate_to_valid_path(self, file_panel, tmp_path):
        """Test navigation to valid directory."""
        file_panel.navigate_to(str(tmp_path))
        assert file_panel.current_path == tmp_path
    
    def test_navigate_to_invalid_path(self, file_panel):
        """Test navigation to invalid directory."""
        with pytest.raises(FileNotFoundError):
            file_panel.navigate_to("/nonexistent/path")
    
    @patch('src.services.file_service.FileService.get_directory_contents')
    def test_refresh_view(self, mock_get_contents, file_panel):
        """Test view refresh functionality."""
        mock_get_contents.return_value = ['file1.txt', 'file2.txt']
        file_panel.refresh_view()
        mock_get_contents.assert_called_once()
```

### Integration Testing

```python
class TestFileOperations:
    """Integration tests for file operations."""
    
    def test_copy_files_between_panels(self, qtbot, main_window, tmp_path):
        """Test copying files between left and right panels."""
        # Create test files
        source_file = tmp_path / "source.txt"
        source_file.write_text("test content")
        
        # Setup panels
        main_window.left_panel.navigate_to(str(tmp_path))
        main_window.right_panel.navigate_to(str(tmp_path / "destination"))
        
        # Select file and copy
        main_window.left_panel.select_file(str(source_file))
        main_window.toolbar.copy_button.click()
        
        # Verify operation
        dest_file = tmp_path / "destination" / "source.txt"
        assert dest_file.exists()
        assert dest_file.read_text() == "test content"
```

### Test Configuration

`conftest.py`:
```python
import pytest
import tempfile
import shutil
from pathlib import Path
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def temp_directory():
    """Create temporary directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_files(temp_directory):
    """Create sample files for testing."""
    files = []
    for i in range(5):
        file_path = temp_directory / f"test_file_{i}.txt"
        file_path.write_text(f"Content of file {i}")
        files.append(file_path)
    return files
```

## Debugging Guidelines

### Logging Setup

```python
import logging
from src.utils.logger import get_logger

# In each module
logger = get_logger(__name__)

class FilePanel(QWidget):
    def navigate_to(self, path):
        logger.debug(f"Navigating to: {path}")
        try:
            # Navigation logic
            logger.info(f"Successfully navigated to: {path}")
        except Exception as e:
            logger.error(f"Navigation failed: {e}", exc_info=True)
```

### Debug Mode

```python
# Enable debug mode with environment variable
import os
DEBUG = os.getenv('FILEORBIT_DEBUG', 'False').lower() == 'true'

if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)
    print("Debug mode enabled")
```

### Common Debugging Scenarios

#### Cache Issues
```bash
# Clear Python cache before debugging
python -B -c "import sys; print('Cache disabled')"

# Or set environment variable
export PYTHONDONTWRITEBYTECODE=1
```

#### Qt Signal Debugging
```python
# Enable Qt signal debugging
import os
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.events.debug=true'
```

#### Memory Debugging
```python
import tracemalloc

# Start memory tracing
tracemalloc.start()

# ... application code ...

# Get memory statistics
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
```

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

def profile_function():
    """Profile specific function performance."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Code to profile
    result = expensive_operation()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative').print_stats(10)
    
    return result
```

### UI Performance

1. **Lazy Loading**: Load directory contents incrementally
2. **Virtual Scrolling**: For large file lists
3. **Debouncing**: Reduce update frequency for rapid events
4. **Threading**: Move blocking operations to background threads

### Memory Management

```python
class MemoryEfficientComponent(QWidget):
    """Component with memory management best practices."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cached_data = {}
        self.max_cache_size = 1000
    
    def add_to_cache(self, key, value):
        """Add item to cache with size limit."""
        if len(self.cached_data) >= self.max_cache_size:
            # Remove oldest items
            oldest_keys = list(self.cached_data.keys())[:100]
            for key in oldest_keys:
                del self.cached_data[key]
        
        self.cached_data[key] = value
    
    def cleanup(self):
        """Clean up resources."""
        self.cached_data.clear()
```

## Contributing Guidelines

### Pull Request Process

1. **Fork Repository**: Create personal fork on GitHub
2. **Create Branch**: Use descriptive branch names (`feature/panel-navigation`, `fix/cache-issue`)
3. **Make Changes**: Follow coding standards and add tests
4. **Test Changes**: Run full test suite and manual testing
5. **Submit PR**: Include detailed description and link issues

### Commit Message Format

```
type(scope): brief description

Detailed explanation of changes made and why.
Include any breaking changes or migration notes.

Fixes #123
Closes #456
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation updated
- [ ] No performance regressions
- [ ] Error handling implemented
- [ ] Signals/slots properly connected
- [ ] Memory leaks checked

## Release Process

### Version Management

FileOrbit uses semantic versioning (SemVer):
- **Major**: Breaking changes
- **Minor**: New features, backwards compatible
- **Patch**: Bug fixes, backwards compatible

### Release Steps

1. **Update Version**: Increment version in `setup.py` and `__init__.py`
2. **Update Changelog**: Document changes in `CHANGELOG.md`
3. **Run Tests**: Full test suite with coverage report
4. **Build Package**: Create distribution packages
5. **Tag Release**: Create Git tag with version
6. **Deploy**: Upload to PyPI or distribution channels

### Continuous Integration

Example GitHub Actions workflow (`.github/workflows/ci.yml`):

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.8, 3.9, '3.10', 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

This comprehensive development guide provides the foundation for maintaining and extending FileOrbit while ensuring code quality and consistency.
