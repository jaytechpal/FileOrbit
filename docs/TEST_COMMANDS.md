# FileOrbit Test Commands - Quick Reference (Multi-Platform)

## Setup

### Windows
```powershell
# Navigate to project directory
cd "d:\DevWorks\FileOrbit"
```

### macOS/Linux
```bash
# Navigate to project directory
cd "/path/to/FileOrbit"  # Adjust to your actual path

# Activate virtual environment
source fileorbit-env/bin/activate
```

## Essential Test Commands

### 1. Quick Verification (Start Here)

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/test_basic.py -v
```

**macOS/Linux (Terminal):**
```bash
python -m pytest tests/test_basic.py -v
```

### 2. Unit Tests (Most Comprehensive)

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/unit/ -v
```

**macOS/Linux (Terminal):**
```bash
python -m pytest tests/unit/ -v
```

### 3. All Tests

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest -v
```

**macOS/Linux (Terminal):**
```bash
python -m pytest -v
```

### 4. Performance Tests with Benchmarking

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/performance/ --benchmark-only -v
```

**macOS/Linux (Terminal):**
```bash
python -m pytest tests/performance/ --benchmark-only -v
```

## Individual Test Files

### Platform Configuration Tests

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/unit/test_platform_config.py -v
```

**macOS/Linux (Terminal):**
```bash
python -m pytest tests/unit/test_platform_config.py -v
```

### File Service Tests

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/unit/test_file_service.py -v
```

**macOS/Linux (Terminal):**
```bash
python -m pytest tests/unit/test_file_service.py -v
```

### Sidebar Component Tests

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/unit/test_sidebar.py -v
```

**macOS/Linux (Terminal):**
```bash
python -m pytest tests/unit/test_sidebar.py -v
```

### Integration Tests

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/integration/ -v
```

**macOS/Linux (Terminal):**
```bash
python -m pytest tests/integration/ -v
```

### UI Tests

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/ui/ -v
```

**macOS/Linux (Terminal):**
```bash
python -m pytest tests/ui/ -v
```

## Test Categories by Markers

### Fast Tests Only

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest -m "not slow" -v
```

**macOS/Linux (Terminal):**
```bash
python -m pytest -m "not slow" -v
```

### Integration Tests Only

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest -m integration -v
```

**macOS/Linux (Terminal):**
```bash
python -m pytest -m integration -v
```

### UI Tests Only

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest -m ui -v
```

**macOS/Linux (Terminal):**
```bash
python -m pytest -m ui -v
```

### Performance Tests Only

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest -m performance -v
```

**macOS/Linux (Terminal):**
```bash
python -m pytest -m performance -v
```

## Environment Verification

### Check Python Version

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" --version
```

**macOS/Linux (Terminal):**
```bash
python --version
```

### Check Pytest Installation

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -c "import pytest; print('pytest version:', pytest.__version__)"
```

**macOS/Linux (Terminal):**
```bash
python -c "import pytest; print('pytest version:', pytest.__version__)"
```

### Check All Test Dependencies

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -c "import pytest, pytest_qt, pytest_benchmark; print('All test dependencies available')"
```

**macOS/Linux (Terminal):**
```bash
python -c "import pytest, pytest_qt, pytest_benchmark; print('All test dependencies available')"
```

## Troubleshooting

### Virtual Environment Issues

**Windows:**
```powershell
# Recreate virtual environment
python -m venv fileorbit-env
.\fileorbit-env\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
# Recreate virtual environment
python3 -m venv fileorbit-env
source fileorbit-env/bin/activate
pip install -r requirements.txt
```

### Platform-Specific Issues

**Linux (Headless Testing):**
```bash
# For CI environments without display
export QT_QPA_PLATFORM=offscreen
python -m pytest tests/ui/ -v
```

**macOS (Qt Dependencies):**
```bash
# Install Qt if needed
brew install qt6
```

**Linux (Qt Dependencies):**
```bash
# Ubuntu/Debian
sudo apt-get install qt6-base-dev python3-pyside6

# Fedora/RHEL
sudo dnf install qt6-qtbase-devel python3-pyside6
```

## Test Output Levels

### Minimal Output

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/unit/
```

**macOS/Linux (Terminal):**
```bash
python -m pytest tests/unit/
```

### Verbose Output (Recommended)

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/unit/ -v
```

**macOS/Linux (Terminal):**
```bash
python -m pytest tests/unit/ -v
```

### Short Traceback (Good for Development)

**Windows (PowerShell):**
```powershell
& "D:/DevWorks/FileOrbit/fileorbit-env/Scripts/python.exe" -m pytest tests/unit/ -v --tb=short
```

**macOS/Linux (Terminal):**
```bash
python -m pytest tests/unit/ -v --tb=short
```
