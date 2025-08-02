# FileOrbit UI Components Documentation

## Overview

FileOrbit uses a modular UI architecture with reusable components built on PySide6/Qt6, optimized for 64-bit systems with intelligent memory management and performance scaling.

## Architecture

```
src/ui/
├── main_window.py          # Main application window with 64-bit optimizations
├── components/             # Reusable UI components
│   ├── file_panel.py      # Core dual-pane file browser with large file support
│   ├── toolbar.py         # Navigation and action toolbar
│   ├── statusbar.py       # Status information display with memory usage
│   ├── sidebar.py         # Quick access navigation with 64-bit drive detection
│   └── command_palette.py # Command palette interface
├── dialogs/               # Modal dialogs
│   └── preferences_dialog.py
└── themes/                # Theme management
```

## 64-bit Performance Features

### Memory Management
- **Dynamic Buffer Allocation**: Components automatically adjust memory usage based on system capabilities
- **Efficient Rendering**: Large directory listings optimized for 64-bit memory addressing
- **Resource Scaling**: UI responsiveness maintained during multi-GB file operations
- **Cache Management**: Intelligent caching with automatic cleanup based on available memory

### Platform Integration
- **Native APIs**: 64-bit Windows API integration for accurate system information
- **Cross-Platform Icons**: QFileIconProvider with 64-bit compatibility
- **Memory Profiling**: Built-in memory usage monitoring and optimization

## Core Components

### 1. MainWindow (main_window.py)

**Purpose**: Primary application window managing layout and component coordination.

**Key Features**:
- Dual-pane layout management
- Active panel tracking
- Window state persistence
- Theme application
- Keyboard shortcut handling

**Important Methods**:
```python
def _on_panel_activated(self, panel_id):
    """Track which panel is currently active"""
    self.active_panel = panel_id

def save_window_settings(self):
    """Persist window state and geometry"""
    # Converts QByteArray to base64 for JSON serialization

def apply_theme(self, theme_name):
    """Apply selected theme to all components"""
```

**Signals**:
- Window state changes
- Theme changes
- Panel activation

### 2. FilePanel (components/file_panel.py)

**Purpose**: Core file browsing component implementing the dual-pane interface.

**Key Features**:
- File system navigation
- File selection and multi-selection
- Panel activation detection
- File operations integration
- Real-time file system monitoring

**Important Methods**:
```python
def mousePressEvent(self, event):
    """Detect panel clicks for activation tracking"""
    super().mousePressEvent(event)
    self.panel_activated.emit(self.panel_id)

def navigate_to(self, path):
    """Navigate to specified directory"""
    # Handles path validation and updates

def refresh_view(self):
    """Refresh file listing"""
    # Updates view with current directory contents
```

**Signals**:
```python
panel_activated = Signal(str)    # Emitted when panel is clicked
directory_changed = Signal(str)  # Emitted when directory changes
selection_changed = Signal(list) # Emitted when file selection changes
```

**Properties**:
- `panel_id`: Unique identifier ("left" or "right")
- `current_path`: Current directory path
- `selected_files`: List of selected file paths

### 3. Toolbar (components/toolbar.py)

**Purpose**: Navigation and file operation controls.

**Key Features**:
- Navigation buttons (Back, Forward, Up)
- File operation buttons (Copy, Move, Delete, etc.)
- Emoji-based icons for cross-platform compatibility
- Keyboard shortcuts
- Action state management

**Button Configuration**:
```python
# Navigation buttons
"← Back"     # Navigate to previous directory
"Forward →"  # Navigate to next directory  
"↑ Up"       # Navigate to parent directory

# File operations
"📄 Copy"    # Copy selected files (Ctrl+C)
"✂️ Move"    # Move selected files (Ctrl+X)
"🗑️ Delete" # Delete selected files (Delete)
"📁 New"     # Create new folder (Ctrl+Shift+N)
"🔄 Refresh" # Refresh current view (F5)
"👁️ View"   # Toggle view mode (Ctrl+1/2/3)
```

**Important Methods**:
```python
def setup_navigation_buttons(self):
    """Configure navigation button actions"""

def setup_file_operation_buttons(self):
    """Configure file operation button actions"""

def update_button_states(self):
    """Enable/disable buttons based on context"""
```

### 4. Sidebar (components/sidebar.py)

**Purpose**: Quick access navigation and system information.

**Key Features**:
- Drive/volume listing
- Bookmarks and favorites
- Recent locations
- System shortcuts
- Active panel awareness

**Important Methods**:
```python
def on_item_clicked(self, item):
    """Handle sidebar navigation clicks"""
    # Routes navigation to currently active panel

def refresh_drives(self):
    """Update drive listing"""
    # Detects available drives/volumes

def add_bookmark(self, path, name):
    """Add location to bookmarks"""
```

**Integration**:
- Communicates with `MainWindow` to determine active panel
- Sends navigation requests to appropriate `FilePanel`
- Updates based on panel changes

### 5. StatusBar (components/statusbar.py)

**Purpose**: Display file selection and operation status information.

**Key Features**:
- Selection count and size
- Current operation progress
- Path information
- File system status

**Information Display**:
```python
def update_selection_info(self, files):
    """Update selection statistics"""
    # Shows: "X files selected (Y MB)"

def show_operation_progress(self, operation, progress):
    """Display operation progress"""
    # Shows: "Copying files... 45%"
```

### 6. Command Palette (components/command_palette.py)

**Purpose**: Quick command access interface (Ctrl+Shift+P).

**Key Features**:
- Fuzzy search for commands
- Recent command history
- Keyboard-driven interface
- Extensible command system

**Usage**:
- Press `Ctrl+Shift+P` to open
- Type to search commands
- Enter to execute
- Escape to close

## Component Communication

### Signal-Slot Connections

```python
# In MainWindow.__init__()

# Panel activation tracking
self.left_panel.panel_activated.connect(self._on_panel_activated)
self.right_panel.panel_activated.connect(self._on_panel_activated)

# Sidebar navigation
self.sidebar.navigate_requested.connect(self._handle_navigation)

# File operation feedback
self.toolbar.file_operation_requested.connect(self._handle_file_operation)

# Status updates
self.left_panel.selection_changed.connect(self.status_bar.update_selection_info)
self.right_panel.selection_changed.connect(self.status_bar.update_selection_info)
```

### Data Flow

1. **User Input** → Component (e.g., FilePanel click)
2. **Component** → Signal emission
3. **MainWindow** → Signal handling and coordination
4. **MainWindow** → Target component method call
5. **Target Component** → Action execution and UI update

## Theming System

### Theme Application

All components support theming through CSS stylesheets:

```python
def apply_theme(self, theme_css):
    """Apply theme stylesheet to component"""
    self.setStyleSheet(theme_css)
    # Cascade to child components
```

### Available Themes

- **Dark Theme**: Modern dark interface
- **Light Theme**: Traditional light interface  
- **Blue Theme**: Blue accent colors

### Custom Themes

Themes are defined in CSS format and can be extended:

```css
/* Example theme snippet */
QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
}

QPushButton {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    padding: 8px 16px;
    border-radius: 4px;
}
```

## Performance Considerations

### File System Operations

- Use `QThread` for blocking operations
- Implement progress reporting for long operations
- Cache directory listings when appropriate
- Debounce file system change events

### UI Responsiveness

- Lazy load large directory contents
- Use virtual scrolling for large file lists
- Implement incremental search
- Minimize unnecessary redraws

### Memory Management

- Clean up temporary resources
- Implement proper signal disconnection
- Use weak references where appropriate
- Monitor memory usage in development

## Testing UI Components

### Manual Testing Checklist

1. **Panel Activation**:
   - Click left panel → sidebar navigation affects left panel
   - Click right panel → sidebar navigation affects right panel
   - Visual feedback shows active panel

2. **Toolbar Functions**:
   - All buttons visible with emoji icons
   - Keyboard shortcuts work
   - Button states update correctly

3. **File Operations**:
   - Copy/paste between panels
   - Delete confirmation dialogs
   - Progress feedback for long operations

4. **Theme Switching**:
   - All components update consistently
   - No visual artifacts
   - Settings persist across sessions

### Automated Testing

```python
# Example component test
def test_panel_activation():
    panel = FilePanel("test_panel")
    with qtbot.waitSignal(panel.panel_activated) as blocker:
        qtbot.mouseClick(panel, Qt.LeftButton)
    assert blocker.args[0] == "test_panel"
```

## Extending Components

### Adding New Buttons

```python
# In toolbar.py
def add_custom_button(self, text, icon, callback, shortcut=None):
    """Add custom button to toolbar"""
    button = QPushButton(text)
    if shortcut:
        button.setShortcut(QKeySequence(shortcut))
    button.clicked.connect(callback)
    self.addWidget(button)
    return button
```

### Custom Dialogs

```python
# Create new dialog in ui/dialogs/
class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # Dialog setup code
        pass
```

### Component Guidelines

1. **Inherit from appropriate Qt base class**
2. **Implement proper signal/slot patterns**
3. **Support theming through stylesheets**
4. **Handle errors gracefully**
5. **Document public methods and signals**
6. **Follow naming conventions**
7. **Implement proper cleanup**
