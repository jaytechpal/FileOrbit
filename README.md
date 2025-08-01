# FileOrbit - Modern File Manager

A sleek, modern dual-pane file manager built with Python and PySide6, inspired by OneCommander's elegant interface.

## Features

### Core Features
- **Dual-Pane Interface**: Side-by-side file browsing like OneCommander
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

- **Python 3.8+**: Core language
- **PySide6**: Modern Qt6 bindings for GUI
- **Pathlib**: Modern path handling
- **Watchdog**: File system monitoring
- **Threading**: QThread for non-blocking operations

## Installation

```bash
# Clone the repository
git clone https://github.com/youruser/FileOrbit.git
cd FileOrbit

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Format code
black src/

# Type checking
mypy src/
```

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

### Version 1.0 (Current)
- [x] Basic dual-pane interface
- [x] File operations (copy, move, delete)
- [x] Modern theming system
- [x] Configuration management
- [ ] Complete UI components
- [ ] File preview
- [ ] Search functionality

### Version 1.1
- [ ] Plugin system
- [ ] Archive support (zip, rar, 7z)
- [ ] Cloud storage integration
- [ ] Advanced search with filters
- [ ] File comparison tools

### Version 1.2
- [ ] FTP/SFTP support
- [ ] Image viewer
- [ ] Text editor integration
- [ ] Bookmark system
- [ ] Custom themes editor

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
