# Development Documentation

## FileOrbit Framework Structure

This document explains the comprehensive framework structure created for your modern file manager application.

## Project Overview

FileOrbit is a modern dual-pane file manager inspired by OneCommander, built with Python and PySide6. The framework provides a robust foundation for cross-platform desktop application development.

## Architecture

### Core Design Principles
- **Modular Architecture**: Clean separation of concerns
- **Modern UI**: OneCommander-inspired sleek interface
- **Threading**: QThread-based background operations
- **Cross-Platform**: Windows, macOS, and Linux support
- **Extensible**: Plugin-ready architecture

### Technology Stack
- **Python 3.8+**: Core language
- **PySide6**: Qt6 bindings for modern GUI
- **Pathlib**: Modern path handling
- **Watchdog**: File system monitoring
- **QThread**: Non-blocking file operations

## Folder Structure Explanation

```
FileOrbit/
├── main.py                     # Application entry point
├── setup.py                    # Package setup and distribution
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
│
├── src/                        # Source code root
│   ├── __init__.py            # Package marker
│   │
│   ├── core/                   # Core application logic
│   │   ├── __init__.py        # Package marker
│   │   └── application.py     # Main application class, services coordination
│   │
│   ├── ui/                     # User interface layer
│   │   ├── __init__.py        # Package marker
│   │   ├── main_window.py     # Main window with dual-pane layout
│   │   │
│   │   ├── components/        # Reusable UI components
│   │   │   ├── __init__.py    # Package marker
│   │   │   ├── file_panel.py  # Core dual-pane file browser
│   │   │   ├── toolbar.py     # Modern toolbar with actions
│   │   │   ├── statusbar.py   # Status bar with file info
│   │   │   ├── sidebar.py     # Quick access navigation
│   │   │   └── command_palette.py # Command palette (Ctrl+Shift+P)
│   │   │
│   │   ├── dialogs/           # Dialog windows
│   │   │   ├── __init__.py    # Package marker
│   │   │   └── preferences_dialog.py # Settings dialog
│   │   │
│   │   ├── widgets/           # Custom widgets (future expansion)
│   │   └── themes/            # Theme definitions (future expansion)
│   │
│   ├── services/              # Business logic services
│   │   ├── __init__.py        # Package marker
│   │   ├── file_service.py    # File operations with QThread
│   │   └── theme_service.py   # Theme management system
│   │
│   ├── models/                # Data models (future expansion)
│   │
│   ├── utils/                 # Utility functions
│   │   ├── __init__.py        # Package marker
│   │   └── logger.py          # Logging configuration
│   │
│   └── config/                # Configuration management
│       ├── __init__.py        # Package marker
│       └── settings.py        # App configuration and persistence
│
├── resources/                  # Static resources
│   ├── icons/                 # Application icons
│   └── styles/                # Additional stylesheets
│
├── tests/                     # Unit tests (future expansion)
└── docs/                      # Documentation (future expansion)
```

## Key Components and Their Purposes

### 1. **main.py**
- Application entry point
- QApplication setup with high DPI support
- Error handling and logging initialization
- Icon and metadata configuration

### 2. **src/core/application.py**
- Main application controller
- Service initialization and coordination
- Theme application
- Auto-save functionality
- Graceful shutdown handling

### 3. **src/ui/main_window.py**
- OneCommander-style main window
- Dual-pane file browser layout
- Menu bar with file operations
- Keyboard shortcuts
- Window state persistence
- Splitter management for resizable panes

### 4. **src/ui/components/**

#### **file_panel.py**
- Core dual-pane file browser component
- Tab support for multiple directories
- Drag & drop functionality
- Context menus
- File selection and navigation
- Real-time directory watching

#### **toolbar.py**
- Modern toolbar with file operation buttons
- Copy, move, delete, new folder actions
- Refresh and view options
- Icon-based interface

#### **statusbar.py**
- File selection information
- Progress tracking for operations
- Current path display
- Operation status messages

#### **sidebar.py**
- Quick access to common locations
- Favorites and bookmarks
- Drive/volume listing
- Navigation shortcuts

#### **command_palette.py**
- Quick action search (Ctrl+Shift+P)
- Fuzzy command matching
- Keyboard-driven interface
- Extensible command system

### 5. **src/services/**

#### **file_service.py**
- QThread-based file operations
- Copy, move, delete with progress tracking
- File system monitoring with Watchdog
- Background operation management
- File integrity verification
- Operation cancellation support

#### **theme_service.py**
- Modern theme system (Dark, Light, Blue)
- OneCommander-inspired styling
- Runtime theme switching
- Custom color palettes
- Comprehensive stylesheet management

### 6. **src/config/settings.py**
- JSON-based configuration persistence
- Cross-platform settings location
- Default configuration management
- Theme and behavior settings
- Window state persistence

### 7. **src/utils/logger.py**
- Comprehensive logging system
- File and console output
- Debug and production modes
- Module-specific loggers

## Features Implemented

### Core Features
✅ **Dual-Pane Interface**: Side-by-side file browsing  
✅ **Modern UI**: Clean, responsive interface with themes  
✅ **QThread Operations**: Non-blocking file operations  
✅ **Real-time Updates**: Watchdog-based file monitoring  
✅ **Configuration System**: Persistent settings management  
✅ **Theme System**: Multiple themes with runtime switching  

### File Operations
✅ **Copy/Move/Delete**: Multi-threaded operations  
✅ **Progress Tracking**: Real-time operation feedback  
✅ **Drag & Drop**: Intuitive file manipulation  
✅ **Context Menus**: Right-click file operations  
✅ **Tab Support**: Multiple directory tabs  

### User Interface
✅ **Modern Styling**: OneCommander-inspired design  
✅ **Keyboard Shortcuts**: Comprehensive hotkey support  
✅ **Command Palette**: Quick action access  
✅ **Status Information**: File selection and operation status  
✅ **Responsive Layout**: Resizable panes and components  

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python main.py
```

### 3. Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests (when implemented)
pytest tests/

# Format code
black src/

# Type checking
mypy src/
```

## Extensibility Points

### 1. **Themes** (`src/ui/themes/`)
- Add new color schemes
- Custom styling definitions
- Runtime theme creation

### 2. **Plugins** (Future)
- Plugin architecture ready
- Service-based extension points
- UI component extensibility

### 3. **File Operations** (`src/services/file_service.py`)
- Custom operation types
- Cloud storage integration
- Archive handling

### 4. **UI Components** (`src/ui/components/`)
- Additional panels and views
- Custom file viewers
- Enhanced navigation

## Building Executables

### Windows
```bash
pip install pyinstaller
pyinstaller --windowed --onefile --name FileOrbit main.py
```

### Cross-Platform Distribution
The framework supports packaging for Windows, macOS, and Linux using PyInstaller or similar tools.

## Next Steps

1. **Complete UI Components**: Implement remaining dialogs and widgets
2. **File Preview**: Add file preview capabilities
3. **Search Functionality**: Implement file search with filters
4. **Archive Support**: Add zip/rar/7z handling
5. **Cloud Integration**: Support for cloud storage services
6. **Plugin System**: Implement extensible plugin architecture

This framework provides a solid foundation for building a modern, professional file manager application that rivals commercial solutions like OneCommander.
