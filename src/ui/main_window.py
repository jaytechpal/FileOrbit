"""
Main Window UI - OneCommander-style dual pane file manager
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QMenuBar, QStatusBar, QToolBar, QTabWidget, QFrame
)
from PySide6.QtCore import Qt, Signal, QSettings, QSize
from PySide6.QtGui import QIcon, QAction, QKeySequence

from src.ui.components.file_panel import FilePanel
from src.ui.components.toolbar import ModernToolBar
from src.ui.components.statusbar import ModernStatusBar
from src.ui.components.sidebar import SideBar
from src.ui.components.command_palette import CommandPalette
from src.ui.dialogs.preferences_dialog import PreferencesDialog
from src.utils.logger import get_logger


class MainWindow(QMainWindow):
    """Main application window with dual-pane interface"""
    
    closing = Signal()
    
    def __init__(self, file_service=None, theme_service=None, config=None):
        super().__init__()
        self.file_service = file_service
        self.theme_service = theme_service
        self.config = config
        self.logger = get_logger(__name__)
        
        # Window properties
        self.setWindowTitle("FileOrbit - Modern File Manager")
        self.setMinimumSize(1000, 600)
        self.resize(1400, 800)
        
        # UI Components
        self.left_panel = None
        self.right_panel = None
        self.sidebar = None
        self.toolbar = None
        self.status_bar = None
        self.command_palette = None
        
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_shortcuts()
        self._connect_signals()
        
    def _setup_ui(self):
        """Setup the main UI layout"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = SideBar(self.file_service)
        
        # Create splitter for main content
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Create dual-pane layout
        pane_widget = QWidget()
        pane_layout = QHBoxLayout(pane_widget)
        pane_layout.setContentsMargins(5, 5, 5, 5)
        pane_layout.setSpacing(5)
        
        # Create dual panels
        self.left_panel = FilePanel(
            panel_id="left",
            file_service=self.file_service,
            config=self.config
        )
        
        self.right_panel = FilePanel(
            panel_id="right", 
            file_service=self.file_service,
            config=self.config
        )
        
        # Panel splitter
        panel_splitter = QSplitter(Qt.Horizontal)
        panel_splitter.addWidget(self.left_panel)
        panel_splitter.addWidget(self.right_panel)
        panel_splitter.setSizes([500, 500])  # Equal split
        
        pane_layout.addWidget(panel_splitter)
        
        # Add to main splitter
        main_splitter.addWidget(self.sidebar)
        main_splitter.addWidget(pane_widget)
        main_splitter.setSizes([200, 1200])  # Sidebar smaller
        
        main_layout.addWidget(main_splitter)
        
        # Setup toolbar
        self.toolbar = ModernToolBar(self.file_service)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        
        # Setup status bar
        self.status_bar = ModernStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Command palette (hidden by default)
        self.command_palette = CommandPalette(self)
        
    def _setup_menu_bar(self):
        """Setup application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_tab_action = QAction("&New Tab", self)
        new_tab_action.setShortcut(QKeySequence.AddTab)
        new_tab_action.triggered.connect(self._new_tab)
        file_menu.addAction(new_tab_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self._copy_files)
        edit_menu.addAction(copy_action)
        
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self._cut_files)
        edit_menu.addAction(cut_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self._paste_files)
        edit_menu.addAction(paste_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        toggle_sidebar_action = QAction("Toggle &Sidebar", self)
        toggle_sidebar_action.setShortcut(QKeySequence("F9"))
        toggle_sidebar_action.triggered.connect(self._toggle_sidebar)
        view_menu.addAction(toggle_sidebar_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        preferences_action = QAction("&Preferences", self)
        preferences_action.setShortcut(QKeySequence.Preferences)
        preferences_action.triggered.connect(self._show_preferences)
        tools_menu.addAction(preferences_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_shortcuts(self):
        """Setup global keyboard shortcuts"""
        # Command palette
        command_palette_shortcut = QAction(self)
        command_palette_shortcut.setShortcut(QKeySequence("Ctrl+Shift+P"))
        command_palette_shortcut.triggered.connect(self._show_command_palette)
        self.addAction(command_palette_shortcut)
        
        # Quick navigation
        focus_left_shortcut = QAction(self)
        focus_left_shortcut.setShortcut(QKeySequence("F1"))
        focus_left_shortcut.triggered.connect(lambda: self.left_panel.setFocus())
        self.addAction(focus_left_shortcut)
        
        focus_right_shortcut = QAction(self)
        focus_right_shortcut.setShortcut(QKeySequence("F2"))
        focus_right_shortcut.triggered.connect(lambda: self.right_panel.setFocus())
        self.addAction(focus_right_shortcut)
    
    def _connect_signals(self):
        """Connect component signals"""
        if self.sidebar:
            self.sidebar.location_changed.connect(self._on_sidebar_location_changed)
        
        if self.left_panel:
            self.left_panel.status_message.connect(self.status_bar.show_message)
            self.left_panel.selection_changed.connect(self._on_selection_changed)
        
        if self.right_panel:
            self.right_panel.status_message.connect(self.status_bar.show_message)
            self.right_panel.selection_changed.connect(self._on_selection_changed)
    
    # Event handlers
    def _new_tab(self):
        """Create new tab in active panel"""
        active_panel = self._get_active_panel()
        if active_panel:
            active_panel.new_tab()
    
    def _copy_files(self):
        """Copy selected files"""
        active_panel = self._get_active_panel()
        if active_panel:
            active_panel.copy_selection()
    
    def _cut_files(self):
        """Cut selected files"""
        active_panel = self._get_active_panel()
        if active_panel:
            active_panel.cut_selection()
    
    def _paste_files(self):
        """Paste files to active panel"""
        active_panel = self._get_active_panel()
        if active_panel:
            active_panel.paste()
    
    def _toggle_sidebar(self):
        """Toggle sidebar visibility"""
        if self.sidebar:
            self.sidebar.setVisible(not self.sidebar.isVisible())
    
    def _show_command_palette(self):
        """Show command palette"""
        if self.command_palette:
            self.command_palette.show_at_center()
    
    def _show_preferences(self):
        """Show preferences dialog"""
        dialog = PreferencesDialog(self.config, self.theme_service, self)
        dialog.exec()
    
    def _show_about(self):
        """Show about dialog"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "About FileOrbit",
            "FileOrbit v1.0.0\n\n"
            "Modern dual-pane file manager\n"
            "Built with Python and PySide6"
        )
    
    def _get_active_panel(self):
        """Get currently active panel"""
        if self.left_panel and self.left_panel.hasFocus():
            return self.left_panel
        elif self.right_panel and self.right_panel.hasFocus():
            return self.right_panel
        else:
            # Default to left panel
            return self.left_panel
    
    def _on_sidebar_location_changed(self, path):
        """Handle sidebar location change"""
        active_panel = self._get_active_panel()
        if active_panel:
            active_panel.navigate_to(path)
    
    def _on_selection_changed(self, selection_info):
        """Handle file selection change"""
        self.status_bar.update_selection_info(selection_info)
    
    # Window state management
    def save_window_state(self):
        """Save window state to settings"""
        if self.config:
            self.config.set('window', 'geometry', self.saveGeometry())
            self.config.set('window', 'state', self.saveState())
    
    def restore_window_state(self):
        """Restore window state from settings"""
        if self.config:
            geometry = self.config.get('window', 'geometry')
            state = self.config.get('window', 'state')
            
            if geometry:
                self.restoreGeometry(geometry)
            if state:
                self.restoreState(state)
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.save_window_state()
        self.closing.emit()
        event.accept()
