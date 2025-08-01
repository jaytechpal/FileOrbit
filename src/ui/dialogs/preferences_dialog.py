"""
Preferences Dialog
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel, QComboBox, QCheckBox, QPushButton, QSpinBox, QGroupBox
from PySide6.QtCore import Qt

from src.utils.logger import get_logger


class PreferencesDialog(QDialog):
    """Application preferences dialog"""
    
    def __init__(self, config=None, theme_service=None, parent=None):
        super().__init__(parent)
        self.config = config
        self.theme_service = theme_service
        self.logger = get_logger(__name__)
        
        self.setWindowTitle("Preferences")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Setup preferences UI"""
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self._create_appearance_tab()
        self._create_behavior_tab()
        self._create_file_operations_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._apply_settings)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)
        
        layout.addLayout(button_layout)
    
    def _create_appearance_tab(self):
        """Create appearance settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme group
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout(theme_group)
        
        self.theme_combo = QComboBox()
        if self.theme_service:
            themes = self.theme_service.get_available_themes()
            for theme_id, theme_name in themes.items():
                self.theme_combo.addItem(theme_name, theme_id)
        
        theme_layout.addWidget(QLabel("Theme:"))
        theme_layout.addWidget(self.theme_combo)
        
        layout.addWidget(theme_group)
        
        # Display group
        display_group = QGroupBox("Display")
        display_layout = QVBoxLayout(display_group)
        
        self.show_hidden_check = QCheckBox("Show hidden files")
        self.dual_pane_check = QCheckBox("Dual pane mode")
        
        display_layout.addWidget(self.show_hidden_check)
        display_layout.addWidget(self.dual_pane_check)
        
        layout.addWidget(display_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Appearance")
    
    def _create_behavior_tab(self):
        """Create behavior settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # File operations group
        ops_group = QGroupBox("File Operations")
        ops_layout = QVBoxLayout(ops_group)
        
        self.confirm_delete_check = QCheckBox("Confirm file deletion")
        self.auto_refresh_check = QCheckBox("Auto refresh directories")
        self.single_click_check = QCheckBox("Single click to open files")
        
        ops_layout.addWidget(self.confirm_delete_check)
        ops_layout.addWidget(self.auto_refresh_check)
        ops_layout.addWidget(self.single_click_check)
        
        layout.addWidget(ops_group)
        
        # Tabs group
        tabs_group = QGroupBox("Tabs")
        tabs_layout = QVBoxLayout(tabs_group)
        
        self.remember_tabs_check = QCheckBox("Remember tabs on startup")
        
        tabs_layout.addWidget(self.remember_tabs_check)
        
        layout.addWidget(tabs_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Behavior")
    
    def _create_file_operations_tab(self):
        """Create file operations settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Performance group
        perf_group = QGroupBox("Performance")
        perf_layout = QVBoxLayout(perf_group)
        
        # Buffer size
        buffer_layout = QHBoxLayout()
        buffer_layout.addWidget(QLabel("Copy buffer size (KB):"))
        
        self.buffer_size_spin = QSpinBox()
        self.buffer_size_spin.setRange(64, 8192)
        self.buffer_size_spin.setSuffix(" KB")
        
        buffer_layout.addWidget(self.buffer_size_spin)
        buffer_layout.addStretch()
        
        perf_layout.addLayout(buffer_layout)
        
        layout.addWidget(perf_group)
        
        # Safety group
        safety_group = QGroupBox("Safety")
        safety_layout = QVBoxLayout(safety_group)
        
        self.show_progress_check = QCheckBox("Show progress for file operations")
        self.verify_checksums_check = QCheckBox("Verify file checksums after copy")
        
        safety_layout.addWidget(self.show_progress_check)
        safety_layout.addWidget(self.verify_checksums_check)
        
        layout.addWidget(safety_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "File Operations")
    
    def _load_settings(self):
        """Load current settings into UI"""
        if not self.config:
            return
        
        # Appearance
        theme = self.config.get('appearance', 'theme', 'dark')
        index = self.theme_combo.findData(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        self.show_hidden_check.setChecked(self.config.get('appearance', 'show_hidden_files', False))
        self.dual_pane_check.setChecked(self.config.get('appearance', 'dual_pane_mode', True))
        
        # Behavior
        self.confirm_delete_check.setChecked(self.config.get('behavior', 'confirm_delete', True))
        self.auto_refresh_check.setChecked(self.config.get('behavior', 'auto_refresh', True))
        self.single_click_check.setChecked(self.config.get('behavior', 'single_click_open', False))
        self.remember_tabs_check.setChecked(self.config.get('behavior', 'remember_tabs', True))
        
        # File operations
        buffer_size = self.config.get('file_operations', 'copy_buffer_size', 1024 * 1024) // 1024
        self.buffer_size_spin.setValue(buffer_size)
        self.show_progress_check.setChecked(self.config.get('file_operations', 'show_progress', True))
        self.verify_checksums_check.setChecked(self.config.get('file_operations', 'verify_checksums', False))
    
    def _apply_settings(self):
        """Apply settings without closing dialog"""
        if not self.config:
            return
        
        # Appearance
        theme_data = self.theme_combo.currentData()
        if theme_data:
            self.config.set('appearance', 'theme', theme_data)
            if self.theme_service:
                self.theme_service.apply_theme(theme_data)
        
        self.config.set('appearance', 'show_hidden_files', self.show_hidden_check.isChecked())
        self.config.set('appearance', 'dual_pane_mode', self.dual_pane_check.isChecked())
        
        # Behavior
        self.config.set('behavior', 'confirm_delete', self.confirm_delete_check.isChecked())
        self.config.set('behavior', 'auto_refresh', self.auto_refresh_check.isChecked())
        self.config.set('behavior', 'single_click_open', self.single_click_check.isChecked())
        self.config.set('behavior', 'remember_tabs', self.remember_tabs_check.isChecked())
        
        # File operations
        buffer_size = self.buffer_size_spin.value() * 1024
        self.config.set('file_operations', 'copy_buffer_size', buffer_size)
        self.config.set('file_operations', 'show_progress', self.show_progress_check.isChecked())
        self.config.set('file_operations', 'verify_checksums', self.verify_checksums_check.isChecked())
        
        # Save config
        self.config.save()
    
    def accept(self):
        """Accept dialog and apply settings"""
        self._apply_settings()
        super().accept()
