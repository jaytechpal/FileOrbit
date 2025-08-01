# Virtual Environment Setup for FileOrbit

This guide will help you set up a Python virtual environment for the FileOrbit project.

## Why Use a Virtual Environment?

- **Isolated Dependencies**: Keep project dependencies separate from system Python
- **Version Control**: Manage specific package versions for the project
- **Clean Development**: Avoid conflicts with other Python projects
- **Reproducible Setup**: Ensure consistent environment across different machines

## Setup Instructions

### Option 1: Using venv (Recommended)

#### 1. Create Virtual Environment
```bash
# Navigate to project directory
cd d:\DevWorks\FileOrbit

# Create virtual environment
python -m venv fileorbit-env

# Alternative with specific Python version
python3.11 -m venv fileorbit-env
```

#### 2. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
# Activate
.\fileorbit-env\Scripts\Activate.ps1

# If execution policy prevents activation:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\fileorbit-env\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
# Activate
fileorbit-env\Scripts\activate.bat
```

**macOS/Linux:**
```bash
# Activate
source fileorbit-env/bin/activate
```

#### 3. Install Dependencies
```bash
# Ensure you're in the activated virtual environment
# You should see (fileorbit-env) in your prompt

# Upgrade pip
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

#### 4. Run FileOrbit
```bash
# Run the application
python main.py
```

#### 5. Deactivate Virtual Environment
```bash
# When done working
deactivate
```

### Option 2: Using conda

#### 1. Create Conda Environment
```bash
# Create environment with Python 3.11
conda create -n fileorbit python=3.11

# Activate environment
conda activate fileorbit
```

#### 2. Install Dependencies
```bash
# Install PySide6 via conda (recommended for Qt)
conda install -c conda-forge pyside6

# Install remaining dependencies via pip
pip install watchdog psutil send2trash pillow

# Or install all via pip
pip install -r requirements.txt
```

#### 3. Run FileOrbit
```bash
python main.py
```

## Development Workflow

### Daily Development Routine
1. **Activate environment**: `.\fileorbit-env\Scripts\Activate.ps1` (Windows)
2. **Work on project**: Edit code, run tests, etc.
3. **Run application**: `python main.py`
4. **Deactivate when done**: `deactivate`

### Adding New Dependencies
```bash
# Activate environment first
.\fileorbit-env\Scripts\Activate.ps1

# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### Setting up on New Machine
```bash
# Clone repository
git clone https://github.com/youruser/FileOrbit.git
cd FileOrbit

# Create virtual environment
python -m venv fileorbit-env

# Activate environment
.\fileorbit-env\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## IDE Integration

### VS Code Setup
1. **Open project in VS Code**
2. **Select Python interpreter**: 
   - Press `Ctrl+Shift+P`
   - Type "Python: Select Interpreter"
   - Choose the interpreter from your virtual environment:
     `d:\DevWorks\FileOrbit\fileorbit-env\Scripts\python.exe`

3. **VS Code will automatically activate the environment** when opening terminals

### PyCharm Setup
1. **Open project in PyCharm**
2. **Configure interpreter**:
   - File → Settings → Project → Python Interpreter
   - Add new interpreter → Existing environment
   - Select: `d:\DevWorks\FileOrbit\fileorbit-env\Scripts\python.exe`

## Troubleshooting

### Common Issues

#### PowerShell Execution Policy Error
```powershell
# Fix execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Virtual Environment Not Activating
```bash
# Ensure you're in the correct directory
cd d:\DevWorks\FileOrbit

# Try full path
d:\DevWorks\FileOrbit\fileorbit-env\Scripts\Activate.ps1
```

#### Package Installation Fails
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Try installing packages individually
pip install PySide6
pip install watchdog
# etc.
```

#### Qt/PySide6 Issues
```bash
# Uninstall and reinstall PySide6
pip uninstall PySide6
pip install PySide6

# Or use conda for better Qt integration
conda install -c conda-forge pyside6
```

## Environment Variables

You may want to set environment variables for development:

```bash
# Create .env file (optional)
echo "FILEORBIT_DEBUG=1" > .env
echo "FILEORBIT_LOG_LEVEL=DEBUG" >> .env
```

## Quick Reference

### Common Commands
```bash
# Create environment
python -m venv fileorbit-env

# Activate (Windows PowerShell)
.\fileorbit-env\Scripts\Activate.ps1

# Activate (Windows CMD)
fileorbit-env\Scripts\activate.bat

# Activate (macOS/Linux)
source fileorbit-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py

# Deactivate
deactivate

# Update requirements
pip freeze > requirements.txt
```

### Directory Structure with Virtual Environment
```
d:\DevWorks\FileOrbit\
├── fileorbit-env/          # Virtual environment (don't commit)
│   ├── Scripts/            # Windows executables
│   ├── Lib/               # Installed packages
│   └── pyvenv.cfg         # Environment config
├── src/                   # Your source code
├── main.py               # Application entry point
├── requirements.txt      # Dependencies
└── README.md            # Project documentation
```

## Next Steps

1. **Create the virtual environment** using the commands above
2. **Activate it** in your terminal
3. **Install dependencies** with `pip install -r requirements.txt`
4. **Configure your IDE** to use the virtual environment
5. **Run FileOrbit** with `python main.py`

The virtual environment will keep your FileOrbit development clean and isolated from other Python projects on your system.
