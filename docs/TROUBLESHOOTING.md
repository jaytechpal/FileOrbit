# FileOrbit Troubleshooting Guide

## Common Issues and Solutions

### 1. Python Cache Issues

**Problem**: Code changes not taking effect after editing source files.

**Symptoms**:
- UI changes don't appear after modifying components
- Bug fixes don't work despite correct code
- Application behavior doesn't match updated code

**Root Cause**: Python bytecode cache (`.pyc` files in `__pycache__` directories) prevents updated code from loading.

**Solutions**:

#### Option 1: Use Clean Launch Script (Recommended)
```batch
# Use the provided clean launch script
.\run_clean.bat
```

#### Option 2: Manual Cache Clearing
```powershell
# Clear all Python cache files
Get-ChildItem -Path . -Recurse -Name "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force

# Run with bytecode compilation disabled
python -B main.py
```

#### Option 3: Environment Variable
```batch
set PYTHONDONTWRITEBYTECODE=1
python main.py
```

### 2. Virtual Environment Issues

**Problem**: Module not found errors or dependency conflicts.

**Solutions**:

#### Quick Setup
```batch
# Use the quick setup script
.\setup_quick.bat
```

#### Manual Setup
```powershell
# Create virtual environment
python -m venv fileorbit-env

# Activate environment
.\fileorbit-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Qt/PySide6 Issues

#### High DPI Display Problems
**Symptoms**: Blurry or incorrectly sized UI elements.

**Solution**: Qt6 handles high DPI automatically. Remove deprecated attributes:
```python
# Remove these deprecated calls:
# app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
# app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
```

#### Missing Toolbar Icons
**Problem**: Navigation buttons not visible in toolbar.

**Solution**: Use emoji-based icons as fallback:
```python
# In toolbar.py
self.back_button.setText("← Back")
self.forward_button.setText("Forward →")
self.up_button.setText("↑ Up")
```

### 4. Panel Navigation Issues

**Problem**: Sidebar navigation always affects left panel instead of active panel.

**Solution**: Implement active panel tracking:
```python
# In FilePanel class
panel_activated = Signal(str)

def mousePressEvent(self, event):
    super().mousePressEvent(event)
    self.panel_activated.emit(self.panel_id)

# In MainWindow class
def _on_panel_activated(self, panel_id):
    self.active_panel = panel_id
```

### 5. JSON Serialization Errors

**Problem**: `Object of type QByteArray is not JSON serializable`

**Solution**: Convert Qt objects to serializable format:
```python
def save_settings(self):
    settings_data = {
        'window_state': base64.b64encode(self.saveState()).decode('utf-8'),
        'geometry': base64.b64encode(self.saveGeometry()).decode('utf-8'),
        # ... other settings
    }
```

### 6. File Path Type Errors

**Problem**: `TypeError: expected str, bytes or os.PathLike object, not 'QModelIndex'`

**Solution**: Ensure proper type conversion:
```python
from pathlib import Path

# Convert to Path object explicitly
path = Path(file_path) if not isinstance(file_path, Path) else file_path
```

## Development Best Practices

### 1. Cache Management
- Always test changes with clean cache
- Use `python -B` flag during development
- Clear cache before releases

### 2. Error Handling
- Implement proper exception handling for file operations
- Log errors with appropriate detail level
- Provide user-friendly error messages

### 3. Threading
- Use QThread for file operations
- Emit signals for UI updates from worker threads
- Handle thread cleanup properly

### 4. Testing
- Test with different file types and sizes
- Verify cross-platform compatibility
- Test error conditions and edge cases

## Getting Help

1. **Check Logs**: Look in the console output for error messages
2. **Clear Cache**: Try running with `run_clean.bat` first
3. **Environment**: Ensure virtual environment is activated
4. **Dependencies**: Verify all requirements are installed
5. **Qt Version**: Ensure PySide6 6.9.1+ is installed

## Useful Debug Commands

```powershell
# Check Python version
python --version

# Check PySide6 version
python -c "import PySide6; print(PySide6.__version__)"

# List installed packages
pip list

# Run with verbose output
python -v main.py

# Run with bytecode disabled
python -B main.py

# Check for import errors
python -c "from src.core.application import FileOrbitApp; print('Import successful')"
```
