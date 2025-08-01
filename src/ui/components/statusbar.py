"""
Modern Status Bar Component
"""

from PySide6.QtWidgets import QStatusBar, QLabel, QProgressBar, QHBoxLayout, QWidget
from PySide6.QtCore import Signal, QTimer
from PySide6.QtGui import QFont

from src.utils.logger import get_logger


class ModernStatusBar(QStatusBar):
    """Modern status bar with file information and progress"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        
        # Status widgets
        self.status_label = QLabel("Ready")
        self.selection_label = QLabel("")
        self.progress_bar = QProgressBar()
        self.path_label = QLabel("")
        
        self._setup_ui()
        self._setup_timer()
    
    def _setup_ui(self):
        """Setup status bar UI"""
        # Add permanent widgets (right side)
        self.addPermanentWidget(self.selection_label, 0)
        self.addPermanentWidget(self.path_label, 1)
        
        # Add temporary widget (left side)
        self.addWidget(self.status_label, 1)
        
        # Setup progress bar (hidden by default)
        self.progress_bar.setVisible(False)
        self.addWidget(self.progress_bar, 0)
        
        # Style
        font = QFont()
        font.setPointSize(9)
        self.setFont(font)
    
    def _setup_timer(self):
        """Setup timer for clearing temporary messages"""
        self.clear_timer = QTimer()
        self.clear_timer.timeout.connect(self._clear_temporary_message)
        self.clear_timer.setSingleShot(True)
    
    def show_message(self, message: str, timeout: int = 3000):
        """Show temporary status message"""
        self.status_label.setText(message)
        if timeout > 0:
            self.clear_timer.start(timeout)
    
    def _clear_temporary_message(self):
        """Clear temporary message"""
        self.status_label.setText("Ready")
    
    def update_selection_info(self, selection_info: dict):
        """Update selection information"""
        count = selection_info.get('count', 0)
        total_size = selection_info.get('total_size', 0)
        files = selection_info.get('files', 0)
        folders = selection_info.get('folders', 0)
        
        if count == 0:
            self.selection_label.setText("")
        else:
            size_str = self._format_size(total_size)
            self.selection_label.setText(f"{count} items ({files} files, {folders} folders) - {size_str}")
    
    def update_path_info(self, path: str, item_count: int = 0):
        """Update current path information"""
        if item_count > 0:
            self.path_label.setText(f"{path} ({item_count} items)")
        else:
            self.path_label.setText(path)
    
    def show_progress(self, visible: bool = True):
        """Show/hide progress bar"""
        self.progress_bar.setVisible(visible)
    
    def update_progress(self, value: int, text: str = ""):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        if text:
            self.show_message(text, 0)  # No timeout for progress messages
    
    def _format_size(self, size: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
