# Changelog

All notable changes to FileOrbit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Cross-Platform Compatibility (Latest)
- **Native Icons**: QFileIconProvider integration for platform-appropriate file and folder icons
- **Platform Fonts**: Automatic font selection (Segoe UI/Windows, SF Pro Display/macOS, Ubuntu/Linux)
- **Cross-Platform Config**: Platform-specific configuration directories (%APPDATA%, ~/.config)
- **Enhanced Sidebar**: Windows drive detection, macOS/Linux filesystem root navigation
- **File Permissions**: Cross-platform permission handling (Windows read-only, Unix octal)
- **Custom Widgets**: ActivatableTabWidget, ActivatableLineEdit, ActivatablePushButton classes
- **Debug System**: Comprehensive panel activation logging and tracking
- **Icon Fallbacks**: Enhanced fallback icons for common file types across platforms
- **Documentation**: Complete cross-platform compatibility guide

### Added - Previous Features
- Comprehensive documentation suite in `docs/` directory
- Installation guide with platform-specific instructions
- Troubleshooting guide with common issues and solutions
- UI components documentation with architecture details
- Development guide with coding standards and contributing guidelines
- Clean launch script (`run_clean.bat`) for cache management
- Emoji-based toolbar icons for cross-platform compatibility
- Active panel tracking system for correct navigation behavior
- Enhanced error handling and logging

### Changed
- **Configuration Paths**: Now use platform-appropriate directories instead of generic paths
- **Icon System**: Replaced basic icons with native system icons via QFileIconProvider
- **Font Selection**: Dynamic font selection based on platform instead of hardcoded Segoe UI
- **Sidebar Navigation**: Enhanced with platform-specific filesystem navigation
- **Panel Activation**: Complete rewrite with custom widget classes for reliable signal emission
- Improved README.md with better structure and cross-platform documentation
- Updated toolbar to use emoji icons instead of system icons
- Enhanced panel navigation to respect currently active panel
- Improved Qt6 compatibility by removing deprecated attributes
- Better virtual environment setup scripts

### Fixed
- **Critical**: Panel navigation now affects the correct (active) panel instead of always the left panel
- **Critical**: Toolbar navigation buttons now visible with emoji icons (← ↑ →)
- **Cross-Platform**: File permissions now handled appropriately on Windows vs Unix systems
- **Cross-Platform**: Configuration and log directories now follow platform conventions
- **Panel Focus**: Tab clicking now properly activates panels with custom widget signal emission
- **Icon Loading**: Improved fallback system for missing or unsupported icons
- **Critical**: Python bytecode cache no longer prevents code updates from taking effect
- Qt6 high DPI deprecation warnings removed
- JSON serialization errors with QByteArray objects
- Path object type conversion errors
- Virtual environment setup script reliability

### Technical Improvements
- Added proper signal-slot connections for panel activation
- Implemented base64 encoding for Qt objects in JSON serialization
- Added mousePressEvent handling for panel click detection
- Enhanced error handling for file operations
- Improved logging and debug capabilities

## [1.0.0] - 2024-12-XX

### Added
- Initial release of FileOrbit
- Dual-pane file manager interface
- Modern Qt6/PySide6 GUI
- File operations (copy, move, delete, rename)
- Multiple theme support (Dark, Light, Blue)
- Real-time file system monitoring
- Cross-platform support (Windows, macOS, Linux)
- Virtual environment setup scripts
- Basic configuration management
- Keyboard shortcuts
- Status bar with file information
- Sidebar navigation with drive access

### Core Features
- **Dual-Pane Interface**: Side-by-side file browsing inspired by OneCommander
- **Modern UI**: Clean, responsive interface with theme support
- **File Operations**: Multi-threaded copy/move/delete with progress tracking
- **Real-time Updates**: Automatic refresh when files change
- **Cross-Platform**: Native support for Windows, macOS, and Linux

### Technology Stack
- Python 3.8+ as core language
- PySide6 6.9.1+ for modern Qt6 GUI
- Watchdog for file system monitoring
- Pathlib for modern path handling
- QThread for non-blocking operations

## Development Notes

### Version 1.0.0 Focus Areas

#### User Interface
- Implemented OneCommander-inspired dual-pane layout
- Created modular component architecture
- Added comprehensive theme system
- Implemented keyboard shortcut system

#### File Operations
- Multi-threaded file operations for responsiveness
- Progress tracking for long operations
- Error handling and user feedback
- Batch operation support

#### Platform Support
- Windows: Native installation and execution
- macOS: Homebrew and native Python support
- Linux: Package manager integration

#### Performance
- Efficient directory scanning
- Lazy loading for large directories
- Memory-conscious resource management
- Real-time file system monitoring

### Recent Development Sprint (December 2024)

#### Issues Addressed
1. **UI Navigation Problems**:
   - Sidebar navigation always affected left panel
   - Missing toolbar navigation icons
   - Inconsistent panel activation feedback

2. **Technical Challenges**:
   - Python bytecode cache preventing updates
   - Qt6 compatibility warnings
   - JSON serialization of Qt objects
   - Path object type mismatches

3. **Setup and Installation**:
   - Virtual environment setup reliability
   - Cross-platform script compatibility
   - Dependency management

#### Solutions Implemented
1. **Active Panel Tracking**:
   ```python
   # Added panel_activated signal to FilePanel
   panel_activated = Signal(str)
   
   # MousePressEvent detection
   def mousePressEvent(self, event):
       super().mousePressEvent(event)
       self.panel_activated.emit(self.panel_id)
   
   # MainWindow coordination
   def _on_panel_activated(self, panel_id):
       self.active_panel = panel_id
   ```

2. **Emoji-Based Toolbar Icons**:
   ```python
   # Cross-platform compatible icons
   self.back_button.setText("← Back")
   self.forward_button.setText("Forward →") 
   self.up_button.setText("↑ Up")
   self.copy_button.setText("📄 Copy")
   self.move_button.setText("✂️ Move")
   self.delete_button.setText("🗑️ Delete")
   ```

3. **Cache Management System**:
   ```batch
   # run_clean.bat script
   @echo off
   echo Cleaning Python cache...
   for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
   del /s /q *.pyc
   python -B main.py
   ```

4. **Qt6 Compatibility**:
   ```python
   # Removed deprecated high DPI attributes
   # Qt6 handles high DPI automatically
   # app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  # Removed
   # app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)     # Removed
   ```

#### Testing and Validation
- Manual testing of panel navigation behavior
- Cross-platform script testing
- Cache clearing validation
- Theme switching verification
- File operation testing

#### Documentation Updates
- Created comprehensive troubleshooting guide
- Added UI component architecture documentation
- Developed installation guide for all platforms
- Written development guide with coding standards
- Updated README with proper structure and links

### Future Development Priorities

#### Short-term (Next Release)
- [ ] Tab support for multiple locations per panel
- [ ] Enhanced file preview capabilities
- [ ] Advanced search and filtering
- [ ] Improved keyboard navigation
- [ ] Plugin system foundation

#### Medium-term
- [ ] Network drive and remote file support
- [ ] Built-in archive handling (zip, tar, etc.)
- [ ] Integration with cloud storage services
- [ ] Advanced file synchronization
- [ ] Git integration features

#### Long-term
- [ ] Mobile companion application
- [ ] Terminal integration
- [ ] Advanced scripting capabilities
- [ ] Enterprise features and deployment
- [ ] Performance optimization for massive directories

### Quality Assurance

#### Testing Strategy
- Unit tests for core components
- Integration tests for file operations
- UI automation tests with pytest-qt
- Cross-platform compatibility testing
- Performance testing with large directories

#### Code Quality
- PEP 8 compliance with Black formatting
- Type hints with mypy validation
- Linting with flake8
- Documentation coverage
- Code review process

#### Release Process
1. Feature development and testing
2. Documentation updates
3. Version increment and changelog update
4. Cross-platform testing
5. Release candidate creation
6. Final testing and validation
7. Release deployment

### Community and Contributions

#### Contribution Guidelines
- Development environment setup documented
- Coding standards clearly defined
- Testing requirements specified
- Pull request process outlined
- Issue reporting templates provided

#### Community Building
- Comprehensive documentation for users and developers
- Clear troubleshooting resources
- Regular updates and communication
- Responsive issue handling
- Feature request consideration process

---

For detailed information about any release, please refer to the corresponding documentation in the `docs/` directory.
