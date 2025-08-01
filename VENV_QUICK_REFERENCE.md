# FileOrbit Virtual Environment Quick Reference

## Quick Setup Commands ⚡

| Action | Windows PowerShell | Windows CMD | macOS/Linux |
|--------|-------------------|-------------|-------------|
| **Create venv** | `python -m venv fileorbit-env` | `python -m venv fileorbit-env` | `python3 -m venv fileorbit-env` |
| **Activate** | `.\fileorbit-env\Scripts\Activate.ps1` | `fileorbit-env\Scripts\activate.bat` | `source fileorbit-env/bin/activate` |
| **Deactivate** | `deactivate` | `deactivate` | `deactivate` |
| **Install deps** | `pip install -r requirements.txt` | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| **Run app** | `python main.py` | `python main.py` | `python main.py` |

## Automated Setup Scripts ✅

### Recommended: Quick Setup
```batch
# Windows - Fastest method
.\setup_quick.bat

# This script:
# 1. Creates virtual environment
# 2. Activates environment  
# 3. Installs all dependencies
# 4. Launches FileOrbit
```

### Platform-Specific Scripts
| Platform | Command | Notes |
|----------|---------|-------|
| **Windows PowerShell** | `.\setup_venv.ps1` | May require execution policy change |
| **Windows CMD** | `setup_venv.bat` | Most reliable on Windows |
| **macOS/Linux** | `chmod +x setup_venv.sh && ./setup_venv.sh` | Requires executable permission |

## Development Workflow 🔄

### Daily Development Routine
```bash
# 1. Activate environment
.\fileorbit-env\Scripts\Activate.ps1  # Windows PowerShell
# OR
fileorbit-env\Scripts\activate.bat     # Windows CMD
# OR  
source fileorbit-env/bin/activate      # macOS/Linux

# 2. Verify activation (should show venv path)
where python                           # Windows
which python                           # macOS/Linux

# 3. Start development
python main.py

# 4. Install new packages (if needed)
pip install package-name
pip freeze > requirements.txt

# 5. Deactivate when done
deactivate
```

### Clean Development Launch
```batch
# Use clean launch to avoid cache issues
.\run_clean.bat

# This script:
# 1. Clears Python bytecode cache
# 2. Activates virtual environment
# 3. Runs with cache disabled (python -B)
```

## Troubleshooting 🛠️

### Common Issues and Solutions

#### PowerShell Execution Policy Error
**Error**: `execution of scripts is disabled on this system`
**Solution**:
```powershell
# Run as Administrator:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or use CMD instead:
setup_venv.bat
```

#### Virtual Environment Not Found
**Error**: `'fileorbit-env' is not recognized`
**Solution**:
```bash
# 1. Ensure you're in the FileOrbit directory
cd d:\DevWorks\FileOrbit

# 2. Check if venv exists
dir fileorbit-env    # Windows
ls fileorbit-env     # macOS/Linux

# 3. If missing, recreate:
python -m venv fileorbit-env
```

#### Python Not Found After Activation
**Issue**: Python still points to system installation
**Solution**:
```bash
# 1. Deactivate and reactivate
deactivate
.\fileorbit-env\Scripts\Activate.ps1

# 2. Verify path (should include fileorbit-env):
echo $env:PATH        # PowerShell
echo %PATH%           # CMD
echo $PATH            # macOS/Linux
```

#### Package Installation Fails
**Error**: Permission denied or access errors
**Solution**:
```bash
# 1. Ensure virtual environment is activated
# 2. Upgrade pip first:
python -m pip install --upgrade pip

# 3. Install with user flag if needed:
pip install --user -r requirements.txt

# 4. For Windows permission issues:
pip install --trusted-host pypi.org --trusted-host pypi.python.org -r requirements.txt
```

#### Module Not Found Errors
**Error**: `ModuleNotFoundError: No module named 'PySide6'`
**Solution**:
```bash
# 1. Verify environment is activated (prompt should show (fileorbit-env))
# 2. Reinstall dependencies:
pip install -r requirements.txt

# 3. Check installed packages:
pip list

# 4. If PySide6 missing specifically:
pip install PySide6>=6.9.1
```

### Code Changes Not Taking Effect
**Issue**: UI changes don't appear after editing code
**Solution**:
```bash
# Use clean launch to bypass Python cache:
.\run_clean.bat

# Or manually clear cache:
python -B main.py
```

## Environment Management Best Practices 📋

### Directory Structure Check
```
FileOrbit/
├── fileorbit-env/           # Virtual environment
│   ├── Scripts/            # Windows executables
│   │   ├── activate.bat    # CMD activation
│   │   ├── Activate.ps1    # PowerShell activation  
│   │   └── python.exe      # Python interpreter
│   └── Lib/                # Installed packages
├── main.py                 # Application entry
├── requirements.txt        # Dependencies
└── setup_quick.bat        # Quick setup script
```

### Dependency Management
```bash
# Update requirements.txt after installing new packages:
pip freeze > requirements.txt

# Install exact versions for reproducibility:
pip install -r requirements.txt

# Check for outdated packages:
pip list --outdated

# Upgrade specific package:
pip install --upgrade PySide6
```

### Virtual Environment Cleanup
```bash
# Remove virtual environment completely:
rmdir /s fileorbit-env      # Windows
rm -rf fileorbit-env        # macOS/Linux

# Recreate fresh environment:
python -m venv fileorbit-env
.\fileorbit-env\Scripts\activate
pip install -r requirements.txt
```

## Production Deployment 🚀

### Environment Export
```bash
# Export exact environment:
pip freeze > requirements-exact.txt

# Export only direct dependencies:
pip-autoremove --list > requirements-minimal.txt
```

### Cross-Platform Considerations
- **Windows**: Use `setup_quick.bat` for reliable setup
- **macOS**: May need `python3` instead of `python`
- **Linux**: Check distribution-specific Python packages
- **All Platforms**: Virtual environment recommended for consistency

## Quick Commands Cheat Sheet 📝

```bash
# Setup (first time)
.\setup_quick.bat                          # Windows automated
python -m venv fileorbit-env && activation # Manual

# Daily use
.\fileorbit-env\Scripts\activate           # Activate
python main.py                             # Run app
deactivate                                 # Deactivate

# Development
.\run_clean.bat                            # Clean launch
pip install package-name                   # Add package
pip freeze > requirements.txt              # Update deps

# Troubleshooting
pip list                                   # Check packages
where python                               # Check Python path
python --version                           # Check version
```

For detailed installation instructions, see **[docs/INSTALLATION.md](docs/INSTALLATION.md)**
cd d:\DevWorks\FileOrbit

# Try absolute path
d:\DevWorks\FileOrbit\fileorbit-env\Scripts\Activate.ps1
```

### Package Installation Issues
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install packages one by one
pip install PySide6
pip install watchdog
pip install psutil
```

## IDE Integration

### VS Code
- `Ctrl+Shift+P` → "Python: Select Interpreter"
- Choose: `./fileorbit-env/Scripts/python.exe`

### PyCharm
- File → Settings → Project → Python Interpreter
- Add → Existing Environment
- Browse to virtual environment Python executable

## Environment Status

Check if virtual environment is active:
```bash
# Should show virtual environment path
where python          # Windows
which python          # macOS/Linux

# Should show (fileorbit-env) in prompt
echo $VIRTUAL_ENV     # macOS/Linux
echo $env:VIRTUAL_ENV # Windows PowerShell
```
