# FileOrbit Virtual Environment Quick Reference

## Setup Commands

| Action | Windows PowerShell | Windows CMD | macOS/Linux |
|--------|-------------------|-------------|-------------|
| **Create venv** | `python -m venv fileorbit-env` | `python -m venv fileorbit-env` | `python3 -m venv fileorbit-env` |
| **Activate** | `.\fileorbit-env\Scripts\Activate.ps1` | `fileorbit-env\Scripts\activate.bat` | `source fileorbit-env/bin/activate` |
| **Deactivate** | `deactivate` | `deactivate` | `deactivate` |
| **Install deps** | `pip install -r requirements.txt` | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| **Run app** | `python main.py` | `python main.py` | `python main.py` |

## Automated Setup

| Platform | Command |
|----------|---------|
| **Windows PowerShell** | `.\setup_venv.ps1` |
| **Windows CMD** | `setup_venv.bat` |
| **macOS/Linux** | `chmod +x setup_venv.sh && ./setup_venv.sh` |

## Development Workflow

```bash
# 1. Activate environment
.\fileorbit-env\Scripts\Activate.ps1  # Windows PowerShell

# 2. Check activation (should show venv path)
where python

# 3. Work on your project
python main.py

# 4. Install new packages (if needed)
pip install package-name
pip freeze > requirements.txt

# 5. Deactivate when done
deactivate
```

## Troubleshooting

### PowerShell Execution Policy
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Virtual Environment Not Found
```bash
# Make sure you're in the right directory
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
