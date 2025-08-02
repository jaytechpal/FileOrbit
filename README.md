# FileOrbit - Modern Cross-Platform File Manager

A sleek, modern dual-pane file manager built with Python and PySide6, inspired by OneCommander's elegant interface. FileOrbit provides a native experience across Windows, macOS, and Linux with platform-specific optimizations.

## Features

### Core Features
- **Dual-Pane Interface**: Side-by-side file browsing like OneCommander
- **Cross-Platform Native**: Optimized for Windows, macOS, and Linux with platform-specific icons and fonts
- **Modern UI**: Clean, responsive interface with multiple themes
- **Fast File Operations**: Multi-threaded copy/move/delete operations
- **Real-time Updates**: Automatic refresh when files change
- **Panel Focus System**: Advanced panel activation tracking with comprehensive debugging

### File Operations
- Copy, move, delete files and folders
- Progress tracking for long operations
- Background operations with QThread
- File integrity verification
- Batch operations support
- Cross-platform permission handling

### User Interface
- Dark, Light, and Blue themes
- Platform-appropriate fonts (Segoe UI, SF Pro Display, Ubuntu)
- Native system icons via QFileIconProvider
- Customizable layouts and keyboard shortcuts
- Command palette (Ctrl+Shift+P)
- Status bar with selection info
- Enhanced sidebar with platform-specific navigation

### Cross-Platform Features
- **Windows**: Drive detection (C:\, D:\, etc.), shell integration icons
- **macOS**: Filesystem root navigation, Finder-style icons, SF Pro font
- **Linux**: Desktop environment icons, package file detection (.deb, .rpm, .AppImage)
- **All Platforms**: User directories, native look and feel

## Technology Stack

- **Python 3.8+**: Core language with cross-platform compatibility
- **PySide6**: Modern Qt6 bindings for native GUI
- **QFileIconProvider**: Platform-specific native system icons
- **Pathlib**: Cross-platform path handling
- **Watchdog**: File system monitoring
- **Threading**: QThread for non-blocking operations

## Performance

FileOrbit is optimized for:
- **Large Directories**: Efficient handling of thousands of files
- **Real-time Updates**: File system monitoring with minimal overhead
- **Memory Usage**: Careful resource management and cleanup
- **Cross-Platform**: Native performance on Windows, macOS, and Linux

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **OneCommander** - Inspiration for the elegant dual-pane interface
- **Qt/PySide6** - Robust cross-platform GUI framework
- **Python Community** - Excellent ecosystem and libraries
- **Contributors** - Everyone who has contributed code, bug reports, and feedback

---

**FileOrbit** - Making file management modern, efficient, and enjoyable.y-side file browsing like OneCommander
- **Modern UI**: Clean, responsive interface with multiple themes
- **Fast File Operations**: Multi-threaded copy/move/delete operations
- **Real-time Updates**: Automatic refresh when files change
- **Cross-Platform**: Windows, macOS, and Linux support

### File Operations
- Copy, move, delete files and folders
- Progress tracking for long operations
- Background operations with QThread
- File integrity verification
- Batch operations support

### User Interface
- Dark, Light, and Blue themes
- Customizable layouts
- Keyboard shortcuts
- Command palette (Ctrl+Shift+P)
- Status bar with selection info
- Sidebar with quick access

### Advanced Features
- File watching with automatic updates
- Configurable settings
- Tab support
- Search functionality
- File preview
- Custom file associations

## Technology Stack

- **Python 3.8+**: Core language with cross-platform compatibility
- **PySide6**: Modern Qt6 bindings for native GUI
- **QFileIconProvider**: Platform-specific native system icons
- **Pathlib**: Cross-platform path handling
- **Watchdog**: File system monitoring
- **Threading**: QThread for non-blocking operations

## Recent Improvements and Status

### ✅ Cross-Platform Compatibility (Latest)
- **Native Icons**: QFileIconProvider integration for platform-appropriate file/folder icons
- **Platform Fonts**: Automatic font selection (Segoe UI on Windows, SF Pro Display on macOS, Ubuntu on Linux)
- **Configuration**: Platform-specific config directories (%APPDATA% on Windows, ~/.config on Unix)
- **Sidebar Navigation**: Windows drives detection, macOS/Linux filesystem root navigation
- **File Permissions**: Cross-platform permission handling (Windows read-only detection, Unix octal)

### ✅ Panel System Enhancements
- **Focus Tracking**: Advanced panel activation system with comprehensive debug logging
- **Custom Widgets**: ActivatableTabWidget, ActivatableLineEdit, ActivatablePushButton classes
- **Signal Integration**: All UI elements properly emit panel activation signals
- **Sidebar Integration**: Navigation correctly affects the currently active panel

### ✅ UI and Technical Improvements
- **Toolbar Icons**: Emoji-based navigation icons (← Back, Forward →, ↑ Up)
- **Icon System**: Enhanced fallback icons for common file types across platforms
- **Error Handling**: Improved cross-platform error reporting and path handling
- **Documentation**: Comprehensive cross-platform compatibility guide

## Documentation

### 📖 User Documentation
- **[Installation Guide](docs/INSTALLATION.md)** - Complete setup instructions for all platforms
- **[Cross-Platform Guide](CROSS_PLATFORM_COMPATIBILITY.md)** - Platform-specific features and compatibility
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

### 🔧 Developer Documentation
- **[Development Guide](docs/DEVELOPMENT_GUIDE.md)** - Contributing and development setup
- **[UI Components](docs/UI_COMPONENTS.md)** - Component architecture and APIs

## Quick Start

### Installation

The fastest way to get FileOrbit running:

**Windows:**
```batch
# Run the quick setup script
.\setup_quick.bat

# Launch FileOrbit
.\run_fileorbit.bat
```

**For detailed installation instructions, see [Installation Guide](docs/INSTALLATION.md)**

### First Launch

**Windows (PowerShell):**
```powershell
# Run the automated setup script
.\setup_venv.ps1
```

**Windows (Command Prompt):**
```cmd
# Run the automated setup script
setup_venv.bat
```

**macOS/Linux:**
```bash
# Make script executable and run
chmod +x setup_venv.sh
./setup_venv.sh
```

### Manual Setup

```bash
# Clone the repository
git clone https://github.com/youruser/FileOrbit.git
cd FileOrbit

# Create virtual environment
python -m venv fileorbit-env

# Activate virtual environment
# Windows PowerShell:
.\fileorbit-env\Scripts\Activate.ps1
# Windows CMD:
fileorbit-env\Scripts\activate.bat
# macOS/Linux:
source fileorbit-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Development Setup

### Virtual Environment (Recommended)

**Automated Setup:**
```powershell
# Windows PowerShell (Recommended)
.\setup_venv.ps1

# Windows Command Prompt
setup_venv.bat

# macOS/Linux
chmod +x setup_venv.sh && ./setup_venv.sh
```

**Manual Setup:**
```bash
# Create and activate virtual environment
python -m venv fileorbit-env

# Activate (choose your platform)
.\fileorbit-env\Scripts\Activate.ps1  # Windows PowerShell
fileorbit-env\Scripts\activate.bat    # Windows CMD
source fileorbit-env/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Format code
black src/

# Type checking
mypy src/
```

### IDE Configuration

**VS Code:**
1. Open project folder
2. Press `Ctrl+Shift+P` → "Python: Select Interpreter"
3. Choose: `./fileorbit-env/Scripts/python.exe` (Windows) or `./fileorbit-env/bin/python` (macOS/Linux)

**PyCharm:**
1. File → Settings → Project → Python Interpreter
2. Add new interpreter → Existing environment
3. Select the Python executable from your virtual environment

For detailed virtual environment setup, see [VIRTUAL_ENV_SETUP.md](VIRTUAL_ENV_SETUP.md)

## Project Structure

```
FileOrbit/
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
├── README.md              # Project documentation
├── src/                   # Source code
│   ├── core/             # Core application logic
│   │   └── application.py # Main application class
│   ├── ui/               # User interface
│   │   ├── main_window.py # Main window
│   │   ├── components/   # UI components
│   │   ├── dialogs/     # Dialog windows
│   │   ├── widgets/     # Custom widgets
│   │   └── themes/      # Theme definitions
│   ├── services/        # Business logic services
│   │   ├── file_service.py    # File operations
│   │   └── theme_service.py   # Theme management
│   ├── models/          # Data models
│   ├── utils/           # Utility functions
│   │   └── logger.py    # Logging setup
│   └── config/          # Configuration
│       └── settings.py  # Settings management
├── resources/           # Static resources
│   ├── icons/          # Application icons
│   └── styles/         # Additional stylesheets
├── tests/              # Unit tests
└── docs/               # Documentation
```

## Building Executables

### Windows
```bash
pip install pyinstaller
pyinstaller --windowed --onefile --name FileOrbit main.py
```

### macOS
```bash
pip install pyinstaller
pyinstaller --windowed --onefile --name FileOrbit main.py
```

### Linux
```bash
pip install pyinstaller
pyinstaller --onefile --name FileOrbit main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

### Version 1.0 (Current - Major Progress)
- [x] Dual-pane interface with panel activation system
- [x] File operations (copy, move, delete) with multi-threading
- [x] Modern theming system (Dark, Light, Blue)
- [x] Cross-platform compatibility (Windows, macOS, Linux)
- [x] Native system icons and platform-specific fonts
- [x] Configuration management with platform-appropriate paths
- [x] Enhanced sidebar navigation with filesystem support
- [x] Comprehensive panel focus tracking and debugging
- [ ] File preview panel
- [ ] Advanced search functionality
- [ ] Tab support for multiple locations

### Version 1.1 (Planned)
- [ ] Plugin system architecture
- [ ] Archive support (zip, rar, 7z, tar)
- [ ] Cloud storage integration (Google Drive, Dropbox, OneDrive)
- [ ] Advanced search with filters and regex
- [ ] File comparison tools and diff viewer
- [ ] Network drive and remote filesystem support

### Version 1.2 (Future)
- [ ] FTP/SFTP/SSH integration
- [ ] Built-in image viewer with basic editing
- [ ] Text editor integration
- [ ] Bookmark system for frequently accessed locations
- [ ] Custom theme editor and sharing
- [ ] Terminal integration

## Screenshots

[Screenshots will be added once UI is complete]

## Acknowledgments

- Inspired by OneCommander's beautiful interface
- Built with Qt6 and PySide6
- Icons from various open-source icon sets
- GUI Framework: PySide6
- File System: pathlib, os, shutil, watchdog
- Threads: QThread ( later QRunnable )
- Packaging: PyInstaller
