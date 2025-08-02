# FileOrbit Cross-Platform Testing Checklist

## Platform Testing Status

### ✅ Windows 10/11 (Tested)
- [x] Application launches successfully
- [x] Native Segoe UI font renders correctly
- [x] Drive detection works (C:\, D:\, etc.)
- [x] Shell integration icons display properly
- [x] Configuration saves to %APPDATA%\FileOrbit\
- [x] Panel activation system functions correctly
- [x] File operations work with Windows permissions
- [x] Emoji toolbar icons display correctly

### 🔄 macOS (Ready for Testing)
**Requirements for Testing:**
- macOS 10.14+ (Mojave or later)
- Python 3.8+ installed
- Xcode Command Line Tools

**Features to Verify:**
- [ ] SF Pro Display font availability and rendering
- [ ] Finder-style file/folder icons via QFileIconProvider
- [ ] Filesystem root (/) navigation in sidebar
- [ ] /Applications directory detection
- [ ] Configuration saves to ~/.config/fileorbit/
- [ ] Panel activation works with trackpad/mouse
- [ ] File permissions display correctly (Unix octal)
- [ ] Application bundle creation (.app file)

**Test Commands:**
```bash
# Clone and setup
git clone https://github.com/jaypalweb/FileOrbit.git
cd FileOrbit
python3 -m venv fileorbit-env
source fileorbit-env/bin/activate
pip install -r requirements.txt
python main.py
```

### 🔄 Linux (Ready for Testing)
**Distributions to Test:**
- [ ] Ubuntu 20.04/22.04 LTS
- [ ] Fedora (latest)
- [ ] Arch Linux
- [ ] openSUSE

**Desktop Environments to Test:**
- [ ] GNOME (GTK-based)
- [ ] KDE Plasma (Qt-based)
- [ ] XFCE
- [ ] LXDE/LXQt

**Features to Verify:**
- [ ] Ubuntu font rendering (or system default fallback)
- [ ] Desktop environment icon integration
- [ ] Package file detection (.deb, .rpm, .AppImage)
- [ ] Filesystem root (/) navigation
- [ ] Configuration saves to ~/.config/fileorbit/
- [ ] Panel activation works with various input methods
- [ ] File permissions display (Unix octal format)
- [ ] Theme integration with desktop environment

**Test Commands:**
```bash
# Install dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# Install dependencies (Fedora)
sudo dnf install python3 python3-pip git

# Clone and setup
git clone https://github.com/jaypalweb/FileOrbit.git
cd FileOrbit
python3 -m venv fileorbit-env
source fileorbit-env/bin/activate
pip install -r requirements.txt
python main.py
```

## Feature Testing Matrix

### Core Functionality Tests

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| **Application Startup** | ✅ | 🔄 | 🔄 |
| **Dual-Pane Interface** | ✅ | 🔄 | 🔄 |
| **File Operations** | ✅ | 🔄 | 🔄 |
| **Panel Activation** | ✅ | 🔄 | 🔄 |
| **Sidebar Navigation** | ✅ | 🔄 | 🔄 |
| **Theme Switching** | ✅ | 🔄 | 🔄 |

### Platform-Specific Features

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| **Drive Detection** | ✅ C:\, D:\ | N/A | N/A |
| **Filesystem Root** | N/A | 🔄 / | 🔄 / |
| **Native Icons** | ✅ Shell | 🔄 Finder | 🔄 DE |
| **System Font** | ✅ Segoe UI | 🔄 SF Pro | 🔄 Ubuntu |
| **Config Path** | ✅ %APPDATA% | 🔄 ~/.config | 🔄 ~/.config |
| **Permissions** | ✅ Read-only | 🔄 Octal | 🔄 Octal |

### UI Component Tests

| Component | Windows | macOS | Linux |
|-----------|---------|-------|-------|
| **Toolbar Icons** | ✅ Emoji | 🔄 | 🔄 |
| **File List** | ✅ | 🔄 | 🔄 |
| **Status Bar** | ✅ | 🔄 | 🔄 |
| **Preferences Dialog** | ✅ | 🔄 | 🔄 |
| **Context Menus** | ✅ | 🔄 | 🔄 |

## Known Platform Considerations

### Windows Specific
- **Drive Letters**: C:\, D:\, E:\ etc. properly detected
- **Permissions**: Simplified to read-only detection
- **Fonts**: Segoe UI is standard system font
- **Icons**: Windows Shell integration through Qt

### macOS Specific
- **Case Sensitivity**: Default filesystem is case-insensitive
- **App Bundle**: May need .app bundle creation for distribution
- **Permissions**: Full Unix permissions support
- **Sandbox**: May need entitlements for file access

### Linux Specific
- **Package Managers**: Different package file types (.deb, .rpm, .tar.xz)
- **Desktop Environments**: Icon themes vary significantly
- **Font Availability**: Ubuntu font may not be installed everywhere
- **Permissions**: Full Unix permissions with ACL support

## Testing Procedures

### Manual Testing Steps

1. **Installation Test**
   ```bash
   # Verify Python version
   python --version
   
   # Setup virtual environment
   python -m venv fileorbit-test
   source fileorbit-test/bin/activate  # Linux/macOS
   fileorbit-test\Scripts\activate     # Windows
   
   # Install and run
   pip install -r requirements.txt
   python main.py
   ```

2. **Core Functionality Test**
   - Launch application
   - Switch between panels by clicking
   - Navigate using sidebar
   - Switch themes in preferences
   - Perform file operations (copy, move, delete)

3. **Platform-Specific Test**
   - Verify native icons display
   - Check font rendering
   - Test filesystem navigation
   - Verify configuration directory creation

### Automated Testing (Future)

```python
# Platform detection test
import sys
import platform

def test_platform_detection():
    assert sys.platform in ['win32', 'darwin', 'linux']
    assert platform.system() in ['Windows', 'Darwin', 'Linux']

def test_config_directory():
    from src.config.settings import AppConfig
    config = AppConfig()
    assert config.config_dir.exists()

def test_icon_provider():
    from PySide6.QtGui import QFileIconProvider
    provider = QFileIconProvider()
    # Test icon availability
```

## Reporting Issues

When reporting platform-specific issues, include:

1. **System Information**
   ```bash
   python --version
   pip list | grep PySide6
   uname -a  # Linux/macOS
   systeminfo  # Windows
   ```

2. **Error Details**
   - Full error traceback
   - Log file contents (fileorbit.log)
   - Steps to reproduce
   - Screenshots if UI-related

3. **Environment Details**
   - Desktop environment (Linux)
   - Display scaling settings
   - Font settings
   - Theme settings

## Success Criteria

FileOrbit is considered cross-platform ready when:

- [x] **Windows**: All features work with native Windows experience
- [ ] **macOS**: All features work with native macOS experience  
- [ ] **Linux**: All features work across major desktop environments
- [ ] **Documentation**: Platform-specific setup guides complete
- [ ] **Distribution**: Executable creation works on all platforms

## Next Steps

1. **macOS Testing**: Find macOS system for comprehensive testing
2. **Linux Testing**: Test across multiple distributions and DEs
3. **CI/CD Setup**: Automated testing on GitHub Actions
4. **Package Distribution**: Create platform-specific installers
5. **Documentation**: Platform-specific troubleshooting guides

---

**FileOrbit Cross-Platform Compatibility** - Bringing native file management to every platform.
