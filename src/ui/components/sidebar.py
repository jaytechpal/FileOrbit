"""
Sidebar Component - Navigation panel
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon
from pathlib import Path
import os

from src.utils.logger import get_logger


class SideBar(QWidget):
    """Sidebar with quick access to common locations"""
    
    location_changed = Signal(str)  # Emitted when user selects a location
    
    def __init__(self, file_service=None):
        super().__init__()
        self.file_service = file_service
        self.logger = get_logger(__name__)
        
        self.setMaximumWidth(250)
        self.setMinimumWidth(150)
        
        self._setup_ui()
        self._populate_locations()
    
    def _setup_ui(self):
        """Setup sidebar UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title = QLabel("Quick Access")
        title.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(title)
        
        # Tree widget for locations
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setRootIsDecorated(True)
        self.tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.tree)
    
    def _populate_locations(self):
        """Populate sidebar with common locations"""
        # Clear existing items
        self.tree.clear()
        
        # Add common locations
        locations = [
            ("Home", str(Path.home())),
            ("Desktop", str(Path.home() / "Desktop")),
            ("Documents", str(Path.home() / "Documents")),
            ("Downloads", str(Path.home() / "Downloads")),
            ("Pictures", str(Path.home() / "Pictures")),
            ("Music", str(Path.home() / "Music")),
            ("Videos", str(Path.home() / "Videos")),
        ]
        
        # Add system drives (Windows)
        if os.name == 'nt':
            drives_item = QTreeWidgetItem(self.tree, ["Drives"])
            drives_item.setExpanded(True)
            
            # Get available drives
            for drive in self._get_windows_drives():
                drive_item = QTreeWidgetItem(drives_item, [f"{drive}:\\"])
                drive_item.setData(0, Qt.UserRole, f"{drive}:\\")
        
        # Add common locations
        favorites_item = QTreeWidgetItem(self.tree, ["Favorites"])
        favorites_item.setExpanded(True)
        
        for name, path in locations:
            if Path(path).exists():
                item = QTreeWidgetItem(favorites_item, [name])
                item.setData(0, Qt.UserRole, path)
    
    def _get_windows_drives(self):
        """Get available Windows drives"""
        drives = []
        if os.name == 'nt':
            import string
            for letter in string.ascii_uppercase:
                drive_path = f"{letter}:\\"
                if os.path.exists(drive_path):
                    drives.append(letter)
        return drives
    
    def _on_item_clicked(self, item, column):
        """Handle item click"""
        path = item.data(0, Qt.UserRole)
        if path:
            self.location_changed.emit(path)
