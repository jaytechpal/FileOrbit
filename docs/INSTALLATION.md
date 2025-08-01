# FileOrbit Setup and Installation Guide

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk Space**: 500MB for application and dependencies

## Installation Methods

### Method 1: Quick Setup (Recommended)

The fastest way to get FileOrbit running:

**Windows:**
```batch
# Clone or download FileOrbit
git clone https://github.com/jaypalweb/FileOrbit.git
cd FileOrbit

# Run quick setup script
.\setup_quick.bat

# Launch application
.\run_fileorbit.bat
```

**Linux/macOS:**
```bash
# Clone or download FileOrbit
git clone https://github.com/jaypalweb/FileOrbit.git
cd FileOrbit

# Run setup script
chmod +x setup_venv.sh
./setup_venv.sh

# Activate environment and run
source fileorbit-env/bin/activate
python main.py
```

### Method 2: Manual Setup

For more control over the installation process:

#### Step 1: Create Virtual Environment
```bash
# Create virtual environment
python -m venv fileorbit-env

# Activate environment
# Windows:
fileorbit-env\Scripts\activate
# Linux/macOS:
source fileorbit-env/bin/activate
```

#### Step 2: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
pip list
```

#### Step 3: Run Application
```bash
python main.py
```

### Method 3: Development Setup

For developers who want to contribute or modify FileOrbit:

#### Step 1: Development Dependencies
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-qt black flake8 mypy
```

#### Step 2: Development Tools
```bash
# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# Run code formatting
black src/

# Run linting
flake8 src/

# Run type checking
mypy src/
```

## Virtual Environment Management

### Creating Environments

FileOrbit uses virtual environments to isolate dependencies:

```bash
# Standard virtual environment
python -m venv fileorbit-env

# With specific Python version
python3.9 -m venv fileorbit-env

# Using conda (alternative)
conda create -n fileorbit python=3.9
conda activate fileorbit
```

### Activating Environments

**Windows:**
```batch
# Command Prompt
fileorbit-env\Scripts\activate.bat

# PowerShell
fileorbit-env\Scripts\Activate.ps1

# Git Bash
source fileorbit-env/Scripts/activate
```

**Linux/macOS:**
```bash
source fileorbit-env/bin/activate
```

### Deactivating Environments
```bash
deactivate
```

### Environment Troubleshooting

**Issue**: "Scripts execution is disabled on this system"
```powershell
# Solution (run as Administrator):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Issue**: Virtual environment not found
```bash
# Recreate environment:
python -m venv fileorbit-env --clear
```

## Dependency Management

### Core Dependencies

FileOrbit requires these essential packages:

```
PySide6>=6.9.1          # Qt6 GUI framework
watchdog>=2.1.0         # File system monitoring
pathlib                 # Path handling (built-in)
threading               # Threading support (built-in)
json                    # Configuration storage (built-in)
logging                 # Application logging (built-in)
```

### Development Dependencies

Additional packages for development:

```
pytest>=7.0.0           # Testing framework
pytest-qt>=4.0.0        # Qt testing support
black>=22.0.0           # Code formatting
flake8>=4.0.0           # Code linting
mypy>=0.950             # Type checking
```

### Updating Dependencies

```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade PySide6

# Check outdated packages
pip list --outdated
```

## Platform-Specific Setup

### Windows Setup

#### Prerequisites
```batch
# Install Python from python.org
# Ensure Python is in PATH
python --version

# Install Git (optional, for cloning)
# Download from git-scm.com
```

#### Common Issues
1. **PowerShell Execution Policy**:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Long Path Support**:
   - Enable in Windows 10 Settings or Group Policy
   - Or use Git Bash for setup

3. **Visual C++ Redistributable**:
   - Required for some Python packages
   - Download from Microsoft

### macOS Setup

#### Prerequisites
```bash
# Install Homebrew (recommended)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python via Homebrew
brew install python

# Or use pyenv for version management
brew install pyenv
pyenv install 3.9.16
pyenv global 3.9.16
```

#### Common Issues
1. **Xcode Command Line Tools**:
   ```bash
   xcode-select --install
   ```

2. **Permission Issues**:
   ```bash
   # Use --user flag for pip installations
   pip install --user -r requirements.txt
   ```

### Linux Setup

#### Ubuntu/Debian
```bash
# Update package manager
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip python3-venv

# Install development headers (for some packages)
sudo apt install python3-dev

# Install Qt dependencies
sudo apt install qt6-base-dev
```

#### CentOS/RHEL/Fedora
```bash
# Install Python and pip
sudo dnf install python3 python3-pip

# Install development tools
sudo dnf groupinstall "Development Tools"
sudo dnf install python3-devel

# Install Qt dependencies
sudo dnf install qt6-qtbase-devel
```

## Configuration

### First Run Setup

1. **Launch Application**: Run `python main.py` or use batch scripts
2. **Initial Configuration**: Choose preferences in Settings
3. **Theme Selection**: Select preferred theme (Dark/Light/Blue)
4. **Panel Layout**: Configure dual-pane layout preferences

### Settings Storage

FileOrbit stores settings in platform-appropriate locations:

**Windows**: `%APPDATA%\FileOrbit\settings.json`
**macOS**: `~/Library/Application Support/FileOrbit/settings.json`
**Linux**: `~/.config/FileOrbit/settings.json`

### Backup and Restore

```bash
# Backup settings
cp ~/.config/FileOrbit/settings.json ~/fileorbit-backup.json

# Restore settings
cp ~/fileorbit-backup.json ~/.config/FileOrbit/settings.json
```

## Performance Optimization

### System Tuning

1. **Increase File Handle Limits** (Linux/macOS):
   ```bash
   ulimit -n 4096
   ```

2. **Disable Real-time Antivirus Scanning** of FileOrbit directory (Windows)

3. **SSD Optimization**: Enable TRIM and optimize file system

### Application Tuning

1. **Large Directories**: Adjust refresh intervals in settings
2. **Network Drives**: Disable file watching for remote locations
3. **Memory Usage**: Monitor with Task Manager/Activity Monitor

## Troubleshooting Installation

### Common Errors and Solutions

**Error**: `ModuleNotFoundError: No module named 'PySide6'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Error**: `Permission denied`
```bash
# Solution: Use virtual environment
python -m venv fileorbit-env
source fileorbit-env/bin/activate  # Linux/macOS
fileorbit-env\Scripts\activate      # Windows
```

**Error**: `Qt platform plugin could not be initialized`
```bash
# Solution: Install Qt platform plugins
pip uninstall PySide6
pip install PySide6
```

**Error**: Application won't start
```bash
# Solution: Check Python version and dependencies
python --version  # Should be 3.8+
pip check         # Verify dependencies
```

### Getting Help

1. **Check System Requirements**: Ensure Python 3.8+ is installed
2. **Verify Dependencies**: Run `pip check` to verify installations
3. **Check Logs**: Look for error messages in console output
4. **Clean Installation**: Remove virtual environment and recreate
5. **Platform Forums**: Check Python and Qt documentation

### Logs and Debugging

Enable debug mode for detailed logging:

```bash
# Set environment variable for debug output
export FILEORBIT_DEBUG=1  # Linux/macOS
set FILEORBIT_DEBUG=1     # Windows

# Run with verbose Python output
python -v main.py

# Check application logs
# Windows: %APPDATA%\FileOrbit\logs\
# macOS: ~/Library/Logs/FileOrbit/
# Linux: ~/.local/share/FileOrbit/logs/
```

## Next Steps

After successful installation:

1. **Read User Guide**: Familiarize yourself with features
2. **Customize Settings**: Configure preferences and themes
3. **Set Bookmarks**: Add frequently used directories
4. **Learn Shortcuts**: Review keyboard shortcuts
5. **Explore Features**: Try file operations and advanced features

For development contributions, see `DEVELOPMENT.md` for additional setup requirements and coding guidelines.
