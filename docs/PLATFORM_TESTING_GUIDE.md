# FileOrbit Multi-Platform Testing Guide

## Platform Differences Summary

FileOrbit is designed to run on Windows, macOS, and Linux. While the core functionality is identical across platforms, there are some differences in setup and execution commands.

## Quick Reference

### Virtual Environment Setup

| Platform | Create Environment | Activate Environment |
|----------|-------------------|---------------------|
| **Windows** | `python -m venv fileorbit-env` | `.\fileorbit-env\Scripts\Activate.ps1` |
| **macOS** | `python3 -m venv fileorbit-env` | `source fileorbit-env/bin/activate` |
| **Linux** | `python3 -m venv fileorbit-env` | `source fileorbit-env/bin/activate` |

### Test Execution Commands

| Test Type | Windows (PowerShell) | macOS/Linux (Terminal) |
|-----------|---------------------|------------------------|
| **Basic Test** | `& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/test_basic.py -v` | `python -m pytest tests/test_basic.py -v` |
| **Unit Tests** | `& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/unit/ -v` | `python -m pytest tests/unit/ -v` |
| **All Tests** | `& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest -v` | `python -m pytest -v` |
| **Performance** | `& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/performance/ --benchmark-only -v` | `python -m pytest tests/performance/ --benchmark-only -v` |

## Platform-Specific Considerations

### Windows
- **PowerShell Syntax**: Requires `&` operator before quoted paths
- **Virtual Environment Path**: `fileorbit-env/Scripts/python.exe`
- **Windows API**: Tests include Windows-specific functionality (mocked for cross-platform testing)
- **Dependencies**: `pywin32` for Windows API integration

### macOS
- **Python Version**: May need `python3` instead of `python`
- **Virtual Environment Path**: `fileorbit-env/bin/python`
- **Qt Dependencies**: May need `brew install qt6` for GUI testing
- **Permissions**: Some Qt operations may require additional permissions

### Linux
- **Python Version**: Usually `python3` for Python 3.x
- **Virtual Environment Path**: `fileorbit-env/bin/python`
- **Display Server**: May need `export QT_QPA_PLATFORM=offscreen` for headless testing
- **Qt Dependencies**: Package manager installation required:
  - Ubuntu/Debian: `sudo apt-get install qt6-base-dev python3-pyside6`
  - Fedora/RHEL: `sudo dnf install qt6-qtbase-devel python3-pyside6`

## Cross-Platform Testing Features

### Mocked Components
FileOrbit's test suite includes comprehensive mocking to ensure all functionality can be tested on any platform:

- **Windows API Mocking**: Windows-specific drive detection and system APIs
- **Platform Detection Simulation**: Tests different OS configurations
- **File System Mocking**: Simulates different filesystem types and limitations

### Consistent Test Results
All platforms should produce identical test results due to:
- **Standardized Test Data**: Tests use consistent sample files and directory structures
- **Mock Configuration**: Platform-specific functionality is mocked consistently
- **Cross-Platform Code Paths**: FileOrbit handles platform differences internally

## Best Practices by Platform

### Windows Development
1. Use PowerShell (not Command Prompt) for better Unicode support
2. Ensure virtual environment is created with the same Python version used for development
3. Use the full Python path in scripts to avoid activation issues

### macOS Development
1. Consider using `pyenv` for Python version management
2. Install Xcode Command Line Tools if encounter compilation issues
3. Use Homebrew for Qt dependencies when needed

### Linux Development
1. Use distribution package manager for system dependencies
2. Consider using virtual display server for headless CI/CD environments
3. Ensure proper permissions for Qt GUI testing

## Continuous Integration Considerations

### GitHub Actions Example
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: [3.8, 3.9, 3.10, 3.11]

steps:
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: ${{ matrix.python-version }}

- name: Install dependencies (Linux)
  if: runner.os == 'Linux'
  run: |
    sudo apt-get update
    sudo apt-get install qt6-base-dev
    export QT_QPA_PLATFORM=offscreen

- name: Install dependencies (macOS)
  if: runner.os == 'macOS'
  run: brew install qt6

- name: Run tests
  run: |
    python -m venv fileorbit-env
    source fileorbit-env/bin/activate  # Linux/macOS
    # .\fileorbit-env\Scripts\Activate.ps1  # Windows
    pip install -r requirements.txt
    python -m pytest tests/ -v
```

## Troubleshooting by Platform

### Common Windows Issues
- **PowerShell Execution Policy**: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Path Issues**: Use forward slashes in paths even on Windows
- **Unicode Issues**: Ensure PowerShell supports UTF-8

### Common macOS Issues
- **Python Version Conflicts**: Use `python3` explicitly
- **Qt Framework Issues**: Install Qt via Homebrew
- **Permission Issues**: May need to allow Python in Security & Privacy settings

### Common Linux Issues
- **Missing Qt Libraries**: Install development packages
- **Display Server Issues**: Use `QT_QPA_PLATFORM=offscreen` for headless environments
- **Permission Issues**: Ensure user has access to create files in test directories

## Performance Considerations

### Platform-Specific Performance
- **Windows**: May have different file I/O performance characteristics
- **macOS**: SSD vs HDD performance varies significantly
- **Linux**: Filesystem type (ext4, btrfs, etc.) affects performance

### Benchmarking Across Platforms
- Use `pytest-benchmark` for consistent performance measurement
- Account for platform-specific performance baselines
- Consider running performance tests multiple times for statistical validity

This guide ensures FileOrbit's testing suite works consistently across all supported platforms while accounting for platform-specific requirements and optimizations.
