"""
Sidebar Component - Navigation panel
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, 
                               QHBoxLayout, QProgressBar, QFileIconProvider)
from PySide6.QtCore import Signal, Qt, QFileInfo
from PySide6.QtGui import QIcon, QPixmap, QPainter
from pathlib import Path
import os

from src.utils.logger import get_logger
from src.utils.cross_platform_filesystem import get_cross_platform_fs
from platform_config import get_platform_config


class DriveItemWidget(QWidget):
    """Custom widget for drive items with icon and progress bar"""
    
    clicked = Signal(str)  # Signal to emit when drive is clicked
    
    def __init__(self, drive_info, parent=None):
        super().__init__(parent)
        self.drive_info = drive_info
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the drive item UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 1, 2, 1)  # Reduced margins
        layout.setSpacing(0)  # No spacing between elements
        
        # Main row: Drive icon and label
        main_layout = QHBoxLayout()
        main_layout.setSpacing(4)  # Reduced spacing
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Drive icon - larger and more prominent
        icon_label = QLabel()
        icon_label.setFixedSize(24, 24)  # Larger icon size
        
        # Get appropriate drive icon based on drive type
        drive_icon = self._get_drive_icon()
        if drive_icon:
            icon_label.setPixmap(drive_icon.pixmap(24, 24))
        
        # Drive letter (bold)
        drive_letter = QLabel(f"{self.drive_info['letter']}:")
        drive_letter.setStyleSheet("color: #FFFFFF; font-size: 11px; font-weight: bold;")
        drive_letter.setFixedWidth(25)
        
        # Drive usage info (right-aligned)
        usage_text = f"{self.drive_info['used_gb']:.0f} / {self.drive_info['total_gb']:.0f} GB"
        usage_label = QLabel(usage_text)
        usage_label.setStyleSheet("color: #CCCCCC; font-size: 9px;")
        usage_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        main_layout.addWidget(icon_label)
        main_layout.addWidget(drive_letter)
        main_layout.addStretch()
        main_layout.addWidget(usage_label)
        
        # Progress bar for drive usage (full width, positioned below)
        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        progress_bar.setValue(int(self.drive_info['usage_percent']))
        progress_bar.setFixedHeight(2)  # Thinner progress bar
        progress_bar.setTextVisible(False)
        
        # Style the progress bar with color based on usage
        bar_color = "#0078D4"  # Default blue
        if self.drive_info['usage_percent'] > 90:
            bar_color = "#D13438"  # Red for high usage
        elif self.drive_info['usage_percent'] > 75:
            bar_color = "#FFB900"  # Yellow for medium-high usage
        
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: #3C3C3C;
                border-radius: 1px;
            }}
            QProgressBar::chunk {{
                background-color: {bar_color};
                border-radius: 1px;
            }}
        """)
        
        layout.addLayout(main_layout)
        layout.addWidget(progress_bar)
        
        # Set compact height
        self.setFixedHeight(26)
    
    def mousePressEvent(self, event):
        """Handle mouse press to emit drive click signal"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.drive_info['path'])
        super().mousePressEvent(event)
    
    def _get_drive_type(self, drive_path):
        """Get drive type using cross-platform methods"""
        # Use the drive info from our cross-platform filesystem
        if hasattr(self, 'drive_info') and 'type' in self.drive_info:
            return self.drive_info['type']
        
        # Fallback: determine type from path
        config = get_platform_config()
        
        if config.is_windows:
            if drive_path.endswith(':\\'):
                return "fixed"  # Default for Windows drives
        elif config.is_macos:
            if drive_path == '/':
                return "fixed"
            elif drive_path.startswith('/Volumes/'):
                return "removable"
        else:  # Linux
            if drive_path == '/':
                return "fixed"
            elif drive_path.startswith(('/media/', '/mnt/')):
                return "removable"
        
        return "fixed"  # Default fallback

    def _get_drive_icon(self):
        """Get appropriate icon for drive type using platform-appropriate shell icons"""
        try:
            drive_path = self.drive_info['path']
            drive_type = self._get_drive_type(drive_path)
            
            # Try to get the system icon first (works on all platforms)
            icon_provider = QFileIconProvider()
            file_info = QFileInfo(drive_path)
            system_icon = icon_provider.icon(file_info)
            
            # If we got a valid system icon, use it
            if not system_icon.isNull():
                return system_icon
            
            # Fallback: create cross-platform custom icons based on detected drive type
            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter()
            if not painter.begin(pixmap):
                return None
                
            try:
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                
                # Get drive identifier using Path instead of os.path
                drive_path_obj = Path(drive_path)
                config = get_platform_config()
                
                if config.is_windows:
                    drive_identifier = self.drive_info.get('letter', drive_path_obj.name)
                else:
                    drive_identifier = drive_path_obj.name or '/'
                    if len(drive_identifier) > 2:
                        drive_identifier = drive_identifier[:2]  # Truncate long names
                
                if drive_type == "fixed":
                    # Hard drive icon (blue/gray) - universal design
                    painter.setPen(Qt.GlobalColor.white)
                    painter.setBrush(Qt.GlobalColor.darkBlue)
                    painter.drawRect(2, 5, 20, 14)
                    painter.setBrush(Qt.GlobalColor.lightGray)
                    painter.drawRect(3, 7, 18, 3)
                    painter.drawRect(3, 11, 18, 3)
                    painter.drawRect(3, 15, 18, 2)
                    
                elif drive_type == "network":
                    # Network drive icon (green with network symbol) - universal design
                    painter.setPen(Qt.GlobalColor.white)
                    painter.setBrush(Qt.GlobalColor.darkGreen)
                    painter.drawRect(2, 5, 20, 14)
                    painter.setBrush(Qt.GlobalColor.yellow)
                    painter.drawRect(3, 7, 18, 3)
                    painter.drawRect(3, 11, 18, 3)
                    # Network connector symbol
                    painter.setBrush(Qt.GlobalColor.cyan)
                    painter.drawRect(1, 8, 3, 8)
                    painter.drawRect(22, 8, 2, 8)
                    
                elif drive_type == "removable":
                    # USB/removable drive icon (orange) - universal design
                    painter.setPen(Qt.GlobalColor.black)
                    painter.setBrush(Qt.GlobalColor.darkMagenta)
                    painter.drawRect(3, 8, 18, 10)
                    painter.setBrush(Qt.GlobalColor.yellow)
                    painter.drawRect(4, 9, 16, 8)
                    # USB connector
                    painter.drawRect(1, 12, 4, 3)
                    
                elif drive_type == "cdrom":
                    # CD/DVD icon (silver) - universal design
                    painter.setPen(Qt.GlobalColor.gray)
                    painter.setBrush(Qt.GlobalColor.lightGray)
                    painter.drawEllipse(3, 3, 18, 18)
                    painter.setBrush(Qt.GlobalColor.darkGray)
                    painter.drawEllipse(9, 9, 6, 6)
                    
                else:
                    # Unknown/default drive icon - universal design
                    painter.setPen(Qt.GlobalColor.lightGray)
                    painter.setBrush(Qt.GlobalColor.darkGray)
                    painter.drawRect(2, 6, 20, 12)
                    painter.setBrush(Qt.GlobalColor.lightGray)
                    painter.drawRect(3, 8, 18, 3)
                    painter.drawRect(3, 12, 18, 3)
                
                # Add drive identifier (letter on Windows, name on Unix)
                painter.setPen(Qt.GlobalColor.white)
                if len(drive_identifier) == 1:
                    painter.drawText(10, 16, drive_identifier)
                else:
                    painter.drawText(8, 16, drive_identifier)
                
            finally:
                painter.end()
                
            return QIcon(pixmap)
            
        except Exception:
            # If there's any error, return None
            return None


class SideBar(QWidget):
    """Sidebar with quick access to common locations"""
    
    location_changed = Signal(str)  # Emitted when user selects a location
    
    def __init__(self, file_service=None):
        super().__init__()
        self.file_service = file_service
        self.logger = get_logger(__name__)
        
        self.setMaximumWidth(220)  # Reduced from 250
        self.setMinimumWidth(180)  # Increased from 150 for better layout
        
        # Set sidebar background to match OneCommander's dark theme
        self.setStyleSheet("""
            SideBar {
                background-color: #2D2D30;
                border-right: 1px solid #3C3C3C;
            }
        """)
        
        self._setup_ui()
        self._populate_locations()

    def _get_folder_icon(self, folder_type, folder_path=None):
        """Get appropriate icon for folder type using Windows shell icons when possible"""
        try:
            # Try to get Windows shell icon first if path is provided
            if folder_path and Path(folder_path).exists():
                icon_provider = QFileIconProvider()
                file_info = QFileInfo(folder_path)
                system_icon = icon_provider.icon(file_info)
                
                # If we got a valid system icon, use it
                if not system_icon.isNull():
                    return system_icon
            
            # Fallback: Create custom icons for better visibility
            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter()
            if not painter.begin(pixmap):
                return None
                
            try:
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                
                if folder_type == 'home':
                    # Home folder - House icon (blue) - larger and more prominent
                    painter.setPen(Qt.GlobalColor.white)
                    painter.setBrush(Qt.GlobalColor.darkBlue)
                    # House shape - larger
                    painter.drawRect(3, 12, 18, 10)
                    # Roof - larger
                    painter.setBrush(Qt.GlobalColor.red)
                    painter.drawRect(1, 9, 22, 4)
                    # Door - larger
                    painter.setBrush(Qt.GlobalColor.darkYellow)
                    painter.drawRect(10, 16, 6, 6)
                    
                elif folder_type == 'documents':
                    # Documents folder - Document icon (green) - larger
                    painter.setPen(Qt.GlobalColor.white)
                    painter.setBrush(Qt.GlobalColor.darkGreen)
                    painter.drawRect(5, 2, 14, 20)
                    painter.setBrush(Qt.GlobalColor.lightGray)
                    painter.drawRect(7, 5, 10, 2)
                    painter.drawRect(7, 8, 10, 2)
                    painter.drawRect(7, 11, 10, 2)
                    painter.drawRect(7, 14, 8, 2)
                    
                elif folder_type == 'downloads':
                    # Downloads folder - Download arrow (purple/cyan) - larger
                    painter.setPen(Qt.GlobalColor.white)
                    painter.setBrush(Qt.GlobalColor.darkMagenta)
                    painter.drawRect(3, 2, 18, 15)
                    painter.setBrush(Qt.GlobalColor.cyan)
                    # Arrow pointing down - larger
                    painter.drawRect(10, 6, 4, 8)
                    painter.drawRect(7, 12, 10, 3)
                    painter.drawRect(8, 15, 8, 2)
                    
                elif folder_type == 'music':
                    # Music folder - Musical note (purple) - larger
                    painter.setPen(Qt.GlobalColor.white)
                    painter.setBrush(Qt.GlobalColor.darkMagenta)
                    painter.drawRect(3, 2, 18, 18)
                    painter.setBrush(Qt.GlobalColor.yellow)
                    # Musical note - larger
                    painter.drawRect(9, 7, 2, 8)
                    painter.drawRect(11, 7, 5, 2)
                    painter.drawRect(7, 13, 5, 3)
                    
                elif folder_type == 'pictures':
                    # Pictures folder - Image icon (cyan) - larger
                    painter.setPen(Qt.GlobalColor.white)
                    painter.setBrush(Qt.GlobalColor.darkCyan)
                    painter.drawRect(3, 3, 18, 15)
                    painter.setBrush(Qt.GlobalColor.yellow)
                    # Image representation - larger
                    painter.drawRect(6, 6, 4, 4)
                    painter.drawRect(5, 12, 6, 3)
                    painter.drawRect(12, 9, 6, 6)
                    
                elif folder_type == 'videos':
                    # Videos folder - Play button (red) - larger
                    painter.setPen(Qt.GlobalColor.white)
                    painter.setBrush(Qt.GlobalColor.darkRed)
                    painter.drawRect(3, 3, 18, 15)
                    painter.setBrush(Qt.GlobalColor.white)
                    # Play triangle - larger
                    painter.drawRect(9, 7, 2, 8)
                    painter.drawRect(11, 8, 2, 6)
                    painter.drawRect(13, 10, 2, 2)
                    
                else:
                    # Default folder icon (gray) - larger
                    painter.setPen(Qt.GlobalColor.white)
                    painter.setBrush(Qt.GlobalColor.darkGray)
                    painter.drawRect(3, 4, 18, 15)
                    painter.setBrush(Qt.GlobalColor.lightGray)
                    painter.drawRect(4, 7, 16, 10)
                
            finally:
                painter.end()
                
            return QIcon(pixmap)
            
        except Exception:
            return None
    
    def _setup_ui(self):
        """Setup sidebar UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title = QLabel("Quick Access")
        title.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                padding: 5px;
                color: #FFFFFF;
                font-size: 12px;
            }
        """)
        layout.addWidget(title)
        
        # Tree widget for locations
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setRootIsDecorated(True)
        self.tree.itemClicked.connect(self._on_item_clicked)
        
        # Style the tree widget to match OneCommander's look with minimal spacing
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #2D2D30;
                border: none;
                outline: none;
                font-size: 11px;
            }
            QTreeWidget::item {
                padding: 1px 2px;
                border: none;
                color: #CCCCCC;
                min-height: 26px;
                max-height: 26px;
            }
            QTreeWidget::item:selected {
                background-color: #3C3C3C;
                color: #FFFFFF;
            }
            QTreeWidget::item:hover {
                background-color: #383838;
                color: #FFFFFF;
            }
            QTreeWidget::branch {
                background-color: transparent;
            }
            QTreeWidget::branch:has-siblings:!adjoins-item {
                border-image: none;
                border: none;
            }
            QTreeWidget::branch:has-siblings:adjoins-item {
                border-image: none;
                border: none;
            }
            QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {
                border-image: none;
                border: none;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(none);
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                border-image: none;
                image: url(none);
            }
        """)
        
        layout.addWidget(self.tree)
    
    def _populate_locations(self):
        """Populate sidebar with common locations"""
        # Clear existing items
        self.tree.clear()
        
        # Add common locations that exist on all platforms
        locations = [
            ("Home", str(Path.home())),
        ]
        
        # Add platform-specific common directories
        common_dirs = ["Desktop", "Documents", "Downloads", "Pictures", "Music", "Videos"]
        for dir_name in common_dirs:
            dir_path = Path.home() / dir_name
            if dir_path.exists():
                locations.append((dir_name, str(dir_path)))
        
        # Add drives/mount points section (cross-platform)
        drives_item = QTreeWidgetItem(self.tree, ["Drives" if os.name == 'nt' else "Volumes"])
        drives_item.setExpanded(True)
        
        # Get available drives with usage information
        drives = self._get_drives()
        self.logger.info(f"Detected {len(drives)} drives: {[d['name'] for d in drives]}")
        for drive_info in drives:
            if drive_info['total_gb'] > 0:
                # Create tree item for the drive
                drive_item = QTreeWidgetItem(drives_item)
                drive_item.setData(0, Qt.UserRole, drive_info['path'])
                
                # Create custom widget for the drive
                drive_widget = DriveItemWidget(drive_info)
                drive_widget.clicked.connect(self.location_changed.emit)
                
                # Set the widget to the tree item
                self.tree.setItemWidget(drive_item, 0, drive_widget)
                
                # Set item height to accommodate the custom widget properly
                drive_item.setSizeHint(0, drive_widget.sizeHint())
            else:
                # For drives without size info (CD/DVD drives, etc.) - use simple text
                drive_text = f"{drive_info.get('name', drive_info.get('letter', 'Unknown'))}"
                drive_item = QTreeWidgetItem(drives_item, [drive_text])
                drive_item.setData(0, Qt.UserRole, drive_info['path'])
        
        # Add common locations
        favorites_item = QTreeWidgetItem(self.tree, ["Favorites"])
        favorites_item.setExpanded(True)
        
        # Define folder type mapping for icons
        folder_types = {
            "Home": "home",
            "Desktop": "desktop",
            "Documents": "documents", 
            "Downloads": "downloads",
            "Pictures": "pictures",
            "Music": "music",
            "Videos": "videos"
        }
        
        for name, path in locations:
            if Path(path).exists():
                item = QTreeWidgetItem(favorites_item, [name])
                item.setData(0, Qt.UserRole, path)
                
                # Add appropriate icon for the folder type
                folder_type = folder_types.get(name, "default")
                icon = self._get_folder_icon(folder_type, path)
                if icon:
                    item.setIcon(0, icon)
    
    def _get_drives(self):
        """Get available drives/mount points with usage information (cross-platform)"""
        fs = get_cross_platform_fs()
        raw_drives = fs.get_drives()
        
        drives = []
        for drive_info in raw_drives:
            # Convert from bytes to GB
            total_gb = drive_info['total_space'] / (1024**3) if drive_info['total_space'] > 0 else 0
            used_gb = drive_info['used_space'] / (1024**3) if drive_info['used_space'] > 0 else 0
            free_gb = drive_info['free_space'] / (1024**3) if drive_info['free_space'] > 0 else 0
            
            # Extract letter for display (first character of label or path)
            letter = drive_info['label'][:1] if drive_info['label'] else drive_info['path'][:1]
            
            drives.append({
                'letter': letter.upper(),
                'path': drive_info['path'],
                'name': drive_info['label'] or drive_info['path'],
                'type': drive_info['type'],
                'filesystem': drive_info.get('filesystem', 'Unknown'),
                'total_gb': total_gb,
                'used_gb': used_gb,
                'free_gb': free_gb,
                'usage_percent': drive_info['usage_percent']
            })
                    
        return drives
    
    def _on_item_clicked(self, item, column):
        """Handle item click"""
        path = item.data(0, Qt.UserRole)
        if path:
            self.location_changed.emit(path)
