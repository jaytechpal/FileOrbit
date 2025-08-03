# FileOrbit Testing Documentation

## Overview

FileOrbit now includes a comprehensive unit testing suite built with pytest. The tests cover all major functionality with a focus on 64-bit optimizations and cross-platform compatibility.

## Test Structure

```
tests/
├── conftest.py                     # Central test configuration and fixtures
├── test_basic.py                   # Basic functionality verification
├── pytest.ini                     # Pytest configuration
├── unit/                          # Unit tests for individual components
│   ├── test_platform_config.py   # Platform detection and 64-bit optimization tests
│   ├── test_file_service.py      # File operations and service tests
│   └── test_sidebar.py           # Sidebar UI component tests
├── integration/                   # Integration tests for component interactions
│   └── test_component_integration.py
├── ui/                           # UI-specific tests using pytest-qt
│   └── test_main_components.py
└── performance/                  # Performance and benchmarking tests
    └── test_performance.py
```

## Test Categories

### Unit Tests (`tests/unit/`)

**Platform Configuration Tests** (`test_platform_config.py`)
- 64-bit system detection and validation
- Memory scaling optimization
- Buffer size calculations
- Platform-specific settings
- Cross-platform compatibility
- Performance optimization validation

**File Service Tests** (`test_file_service.py`)
- File operations (copy, move, delete)
- Progress tracking and reporting
- Large file handling (>2GB)
- Error handling and recovery
- Concurrent operations
- Memory-efficient operations

**Sidebar Component Tests** (`test_sidebar.py`)
- Drive detection and enumeration
- Windows API integration (mocked)
- Cross-platform drive handling
- Large drive support (>2TB)
- UI component behavior
- Error handling

### Integration Tests (`tests/integration/`)

- Main window service integration
- File operation workflows
- Theme system integration
- Memory management across components
- Concurrent operation handling
- Error recovery scenarios

### UI Tests (`tests/ui/`)

- Main window functionality
- File panel interactions
- Keyboard navigation
- Theme application
- UI responsiveness
- Error display

### Performance Tests (`tests/performance/`)

- File operation performance
- Memory usage optimization
- Concurrent operation scaling
- Disk I/O performance
- UI responsiveness under load

## Test Dependencies

The testing suite requires the following packages:

```
pytest>=7.0.0           # Core testing framework
pytest-qt>=4.2.0        # Qt GUI testing support
pytest-benchmark>=4.0.0 # Performance benchmarking
pytest-asyncio>=0.21.0  # Async operation testing
```

## Key Test Fixtures

### Central Fixtures (`conftest.py`)

- **`qapp`**: QApplication fixture for Qt testing
- **`temp_dir`**: Temporary directory for file operations
- **`sample_files`**: Pre-created test files of various sizes
- **`mock_platform_config`**: Mock platform configuration
- **`qt_helper`**: Qt testing utilities
- **`performance_helper`**: Memory and performance monitoring

## Running Tests

### Setup (All Platforms)

#### Windows

1. **Navigate to FileOrbit Directory**:
   ```powershell
   cd "d:\DevWorks\FileOrbit"
   ```

2. **Activate Virtual Environment** (if not already activated):
   ```powershell
   # Windows PowerShell
   .\fileorbit-env\Scripts\Activate.ps1
   ```

3. **Verify Test Dependencies**:
   ```powershell
   & "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -c "import pytest; print('pytest ready')"
   ```

#### macOS

1. **Navigate to FileOrbit Directory**:
   ```bash
   cd "/path/to/FileOrbit"  # Adjust to your actual path
   ```

2. **Activate Virtual Environment**:
   ```bash
   # Bash/Zsh
   source fileorbit-env/bin/activate
   ```

3. **Verify Test Dependencies**:
   ```bash
   python -c "import pytest; print('pytest ready')"
   ```

#### Linux

1. **Navigate to FileOrbit Directory**:
   ```bash
   cd "/path/to/FileOrbit"  # Adjust to your actual path
   ```

2. **Activate Virtual Environment**:
   ```bash
   # Bash
   source fileorbit-env/bin/activate
   ```

3. **Verify Test Dependencies**:
   ```bash
   python -c "import pytest; print('pytest ready')"
   ```

### Basic Test Execution

#### Windows (PowerShell)

**Important**: Use the full Python path for the virtual environment in PowerShell:

```powershell
# Run all tests
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest -v

# Run with short traceback (recommended)
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest -v --tb=short

# Run specific test categories
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/unit/ -v                    # Unit tests only
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/integration/ -v             # Integration tests only
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/ui/ -v                      # UI tests only
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/performance/ -v             # Performance tests only

# Run specific test files
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/unit/test_platform_config.py -v
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/unit/test_file_service.py -v
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/unit/test_sidebar.py -v

# Run basic verification test
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/test_basic.py -v
```

#### macOS/Linux (Terminal)

**After activating the virtual environment**, you can use standard pytest commands:

```bash
# Run all tests
python -m pytest -v

# Run with short traceback (recommended)
python -m pytest -v --tb=short

# Run specific test categories
python -m pytest tests/unit/ -v                    # Unit tests only
python -m pytest tests/integration/ -v             # Integration tests only
python -m pytest tests/ui/ -v                      # UI tests only
python -m pytest tests/performance/ -v             # Performance tests only

# Run specific test files
python -m pytest tests/unit/test_platform_config.py -v
python -m pytest tests/unit/test_file_service.py -v
python -m pytest tests/unit/test_sidebar.py -v

# Run basic verification test
python -m pytest tests/test_basic.py -v
```

### Alternative: Using Activated Environment (All Platforms)

If you have successfully activated the virtual environment on any platform, you can use shorter commands:

```bash
# After successful activation, these commands work on all platforms:
python -m pytest                     # Run all tests
python -m pytest -v                  # Verbose output
python -m pytest tests/unit/ -v      # Unit tests only
python -m pytest tests/test_basic.py -v  # Basic verification
```

### Performance Testing

#### Windows (PowerShell)

```powershell
# Run performance tests with benchmarking
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/performance/ --benchmark-only -v

# Compare performance runs
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/performance/ --benchmark-compare -v

# Save benchmark results
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/performance/ --benchmark-save=baseline -v

# Run performance tests without benchmarking (faster)
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/performance/ -v
```

#### macOS/Linux (Terminal)

```bash
# Run performance tests with benchmarking
python -m pytest tests/performance/ --benchmark-only -v

# Compare performance runs
python -m pytest tests/performance/ --benchmark-compare -v

# Save benchmark results
python -m pytest tests/performance/ --benchmark-save=baseline -v

# Run performance tests without benchmarking (faster)
python -m pytest tests/performance/ -v
```

### Test Markers

Tests are marked with the following categories:

#### Windows (PowerShell)

```powershell
# Run only fast tests (skip slow integration tests)
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest -m "not slow" -v

# Run only integration tests
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest -m integration -v

# Run only UI tests
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest -m ui -v

# Run only performance tests
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest -m performance -v
```

#### macOS/Linux (Terminal)

```bash
# Run only fast tests (skip slow integration tests)
python -m pytest -m "not slow" -v

# Run only integration tests
python -m pytest -m integration -v

# Run only UI tests
python -m pytest -m ui -v

# Run only performance tests
python -m pytest -m performance -v
```

### Quick Test Commands Summary

#### Windows (PowerShell)

```powershell
# Most common commands for daily use:

# 1. Quick verification that tests work
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/test_basic.py -v

# 2. Run all unit tests (fastest, most comprehensive)
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/unit/ -v

# 3. Run all tests (comprehensive but slower)
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest -v

# 4. Run with performance benchmarking
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/performance/ --benchmark-only -v
```

#### macOS/Linux (Terminal)

```bash
# Most common commands for daily use:

# 1. Quick verification that tests work
python -m pytest tests/test_basic.py -v

# 2. Run all unit tests (fastest, most comprehensive)
python -m pytest tests/unit/ -v

# 3. Run all tests (comprehensive but slower)
python -m pytest -v

# 4. Run with performance benchmarking
python -m pytest tests/performance/ --benchmark-only -v
```

## 64-bit Specific Testing

### Platform Detection Tests
- Validates 64-bit system detection
- Tests architecture-specific optimizations
- Verifies memory scaling for 64-bit systems

### Memory Management Tests
- Large file handling (>2GB)
- Memory-efficient buffer calculations
- 64-bit address space utilization

### Performance Tests
- 64-bit optimized file operations
- Memory usage scaling
- Large drive support (>2TB)

## Cross-Platform Testing

The test suite includes comprehensive mocking to enable cross-platform testing:

- **Windows API Mocking**: Tests Windows-specific functionality on any platform
- **Drive Detection Simulation**: Tests drive enumeration across different filesystems
- **Platform-Specific Optimization Testing**: Validates optimizations for different operating systems

## Error Handling and Edge Cases

### File Operation Errors
- Permission denied scenarios
- Disk full conditions
- Network interruption handling
- Invalid path handling

### UI Error States
- Service failure recovery
- Invalid directory navigation
- Theme switching errors
- Large directory loading

### Memory and Performance Edge Cases
- Very large file operations (>10GB)
- Concurrent operation limits
- Memory pressure scenarios
- Disk I/O bottlenecks

## Test Coverage Areas

### Core Functionality
- ✅ File operations (copy, move, delete)
- ✅ Directory navigation
- ✅ Drive detection and enumeration
- ✅ File system monitoring
- ✅ Progress tracking

### 64-bit Optimizations
- ✅ Large file support (>2GB)
- ✅ Memory-efficient operations
- ✅ 64-bit architecture detection
- ✅ Optimized buffer sizing
- ✅ Large drive handling (>2TB)

### Cross-Platform Features
- ✅ Windows API integration
- ✅ macOS compatibility
- ✅ Linux compatibility
- ✅ Platform-specific optimizations

### UI Components
- ✅ Main window functionality
- ✅ File panels
- ✅ Sidebar drive listing
- ✅ Theme system
- ✅ Keyboard navigation

### Performance and Reliability
- ✅ Memory usage optimization
- ✅ Concurrent operations
- ✅ Error recovery
- ✅ Resource cleanup

## Continuous Integration

The test suite is designed to run in CI/CD environments:

- **Fast Execution**: Core tests complete in under 30 seconds
- **Isolated Tests**: No external dependencies or network requirements
- **Cross-Platform**: Runs on Windows, macOS, and Linux
- **Comprehensive Mocking**: Tests platform-specific functionality without platform dependencies

## Troubleshooting

### Common Issues and Solutions

#### 1. "No module named pytest" Error

**Problem**: Running `python -m pytest` gives module not found error.

**Windows Solution**:
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest
```

**macOS/Linux Solution**:
```bash
# Make sure virtual environment is activated
source fileorbit-env/bin/activate
python -m pytest
```

#### 2. Command Syntax Errors

**Windows PowerShell Problem**: Commands fail with "Unexpected token" errors.
**Solution**: Use the `&` operator before quoted paths in PowerShell:
```powershell
# Wrong
"D:/path/python.exe" -m pytest

# Correct
& "D:/path/python.exe" -m pytest
```

**macOS/Linux**: Standard bash syntax works:
```bash
python -m pytest
./fileorbit-env/bin/python -m pytest  # If activation fails
```

#### 3. Import Errors in Tests

**Problem**: Tests fail with "ModuleNotFoundError" for src modules.

**Windows Solution**:
```powershell
cd "d:\DevWorks\FileOrbit"
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest
```

**macOS/Linux Solution**:
```bash
cd "/path/to/FileOrbit"
python -m pytest
```

#### 4. Qt Application Errors

**Problem**: Tests fail with Qt application initialization errors.

**All Platforms Solution**: Run tests that use Qt fixtures (ui tests) one at a time if needed:

**Windows**:
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/ui/ -v -x
```

**macOS/Linux**:
```bash
python -m pytest tests/ui/ -v -x
```

#### 5. Virtual Environment Issues

**Problem**: Virtual environment activation fails or pytest not found.

**Windows Solution**:
```powershell
python -m venv fileorbit-env
.\fileorbit-env\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS/Linux Solution**:
```bash
python3 -m venv fileorbit-env
source fileorbit-env/bin/activate
pip install -r requirements.txt
```

#### 6. Platform-Specific Issues

**macOS**: If you encounter permission issues with Qt:
```bash
# Install Qt dependencies if needed
brew install qt6
# Or use conda
conda install qt
```

**Linux**: If you encounter display server issues:
```bash
# For headless testing (CI environments)
export QT_QPA_PLATFORM=offscreen
python -m pytest tests/ui/ -v

# Install Qt dependencies on Ubuntu/Debian
sudo apt-get install qt6-base-dev python3-pyside6

# Install Qt dependencies on Fedora/RHEL
sudo dnf install qt6-qtbase-devel python3-pyside6
```

**Windows**: If you encounter Windows API issues:
```powershell
# Ensure pywin32 is installed (should be automatic from requirements.txt)
pip install pywin32
```

### Verifying Test Environment

#### Windows

To verify everything is set up correctly:

```powershell
# 1. Check you're in the right directory
cd "d:\DevWorks\FileOrbit"

# 2. Verify Python path
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" --version

# 3. Check pytest installation
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -c "import pytest; print('pytest version:', pytest.__version__)"

# 4. Run basic verification test
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/test_basic.py -v

# 5. If basic test passes, run unit tests
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/unit/ -v
```

#### macOS/Linux

To verify everything is set up correctly:

```bash
# 1. Check you're in the right directory
cd "/path/to/FileOrbit"

# 2. Activate virtual environment
source fileorbit-env/bin/activate

# 3. Verify Python version
python --version

# 4. Check pytest installation
python -c "import pytest; print('pytest version:', pytest.__version__)"

# 5. Run basic verification test
python -m pytest tests/test_basic.py -v

# 6. If basic test passes, run unit tests
python -m pytest tests/unit/ -v
```

## Maintenance and Updates

### Adding New Tests

1. **Create test file** in appropriate directory (`unit/`, `integration/`, `ui/`, `performance/`)
2. **Import required fixtures** from `conftest.py`
3. **Use appropriate markers** for test categorization
4. **Follow naming conventions**: `test_*.py` files, `Test*` classes, `test_*` methods

### Mock Updates

When adding new platform-specific functionality:

1. **Update mock fixtures** in `conftest.py`
2. **Add corresponding tests** in appropriate test files
3. **Ensure cross-platform compatibility** through mocking

### Performance Baselines

Performance tests include benchmarking to track regressions:

1. **Establish baselines** with `--benchmark-save`
2. **Compare against baselines** with `--benchmark-compare`
3. **Update baselines** when intentional performance changes occur

## Test Configuration

### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    ui: marks tests as UI tests requiring Qt
    performance: marks tests as performance tests
```

This comprehensive testing suite ensures FileOrbit's reliability, performance, and cross-platform compatibility while maintaining focus on 64-bit optimizations and modern file management requirements.
