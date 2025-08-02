"""
Sidebar Component - Navigation panel
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, 
                               QHBoxLayout, QProgressBar, QFileIconProvider)
from PySide6.QtCore import Signal, Qt, QFileInfo
from PySide6.QtGui import QIcon, QPixmap, QPainter
from pathlib import Path
import os
import shutil
import sys

from src.utils.logger import get_logger

# Windows-specific imports for drive type detection
if os.name == 'nt':
    import ctypes
    
    # Windows drive type constants
    DRIVE_UNKNOWN = 0
    DRIVE_NO_ROOT_DIR = 1
    DRIVE_REMOVABLE = 2
    DRIVE_FIXED = 3
    DRIVE_REMOTE = 4
    DRIVE_CDROM = 5
    DRIVE_RAMDISK = 6


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
        """Get drive type using platform-appropriate methods"""
        if os.name == 'nt':  # Windows
            try:
                # Windows API drive type detection
                drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_path)
                drive_letter = drive_path[0].upper()
                
                # Additional check for network mapped drives
                try:
                    buffer_size = 256
                    buffer = ctypes.create_unicode_buffer(buffer_size)
                    result = ctypes.windll.mpr.WNetGetConnectionW(
                        drive_letter + ":", buffer, ctypes.byref(ctypes.c_ulong(buffer_size))
                    )
                    if result == 0:  # SUCCESS
                        return "network"  # It's a mapped network drive
                except Exception:
                    pass  # Not a network drive or error occurred
                
                # Heuristic for network drives that appear as fixed
                if drive_type == DRIVE_FIXED and drive_letter >= 'H':
                    return "network"
                        
                if drive_type == DRIVE_FIXED:
                    return "fixed"  # Hard drive
                elif drive_type == DRIVE_REMOTE:
                    return "network"  # Network drive
                elif drive_type == DRIVE_REMOVABLE:
                    return "removable"  # USB, floppy, etc.
                elif drive_type == DRIVE_CDROM:
                    return "cdrom"  # CD/DVD/Blu-ray
                elif drive_type == DRIVE_RAMDISK:
                    return "ramdisk"  # RAM disk
                else:
                    return "unknown"
            except Exception:
                return "fixed"  # Default fallback
                
        elif os.name == 'posix':  # Linux and macOS
            try:
                # Check mount points for drive type detection
                import subprocess
                
                # On macOS, check if it's in /Volumes (external/network drives)
                if sys.platform == 'darwin':  # macOS
                    if drive_path.startswith('/Volumes/'):
                        # Try to determine if it's network or removable
                        try:
                            result = subprocess.run(['mount'], capture_output=True, text=True)
                            mount_info = result.stdout
                            if drive_path in mount_info:
                                if any(fs_type in mount_info for fs_type in ['nfs', 'smb', 'cifs', 'afp']):
                                    return "network"
                                elif any(fs_type in mount_info for fs_type in ['msdos', 'exfat', 'ntfs']):
                                    return "removable"
                        except Exception:
                            pass
                        return "removable"  # Default for /Volumes
                    elif drive_path == '/':
                        return "fixed"  # Root filesystem
                    else:
                        return "fixed"  # Other paths
                        
                else:  # Linux
                    if drive_path == '/':
                        return "fixed"  # Root filesystem
                    elif drive_path.startswith('/media/') or drive_path.startswith('/mnt/'):
                        # Check if it's a network mount
                        try:
                            result = subprocess.run(['mount'], capture_output=True, text=True)
                            mount_info = result.stdout
                            if any(fs_type in mount_info for fs_type in ['nfs', 'smb', 'cifs']):
                                return "network"
                        except Exception:
                            pass
                        return "removable"  # Likely external drive
                    else:
                        return "fixed"  # Default
                        
            except Exception:
                return "fixed"  # Default fallback
        else:
            return "fixed"  # Default for unknown OS

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
                
                # Get drive identifier (letter on Windows, last part of path on Unix)
                if os.name == 'nt':
                    drive_identifier = self.drive_info['letter']
                else:
                    drive_identifier = os.path.basename(drive_path) or '/'
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
            if folder_path and os.path.exists(folder_path):
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
        drives = []
        
        if os.name == 'nt':  # Windows
            import string
            for letter in string.ascii_uppercase:
                drive_path = f"{letter}:\\"
                if os.path.exists(drive_path):
                    try:
                        # Get drive usage information
                        usage = shutil.disk_usage(drive_path)
                        total_gb = usage.total / (1024**3)
                        used_gb = (usage.total - usage.free) / (1024**3)
                        free_gb = usage.free / (1024**3)
                        
                        drives.append({
                            'letter': letter,
                            'path': drive_path,
                            'name': f"{letter}:",
                            'total_gb': total_gb,
                            'used_gb': used_gb,
                            'free_gb': free_gb,
                            'usage_percent': (used_gb / total_gb) * 100 if total_gb > 0 else 0
                        })
                    except (OSError, PermissionError):
                        # Drive exists but can't get usage info (e.g., CD drive)
                        drives.append({
                            'letter': letter,
                            'path': drive_path,
                            'name': f"{letter}:",
                            'total_gb': 0,
                            'used_gb': 0,
                            'free_gb': 0,
                            'usage_percent': 0
                        })
                        
        elif sys.platform == 'darwin':  # macOS
            # Add root filesystem
            try:
                usage = shutil.disk_usage('/')
                total_gb = usage.total / (1024**3)
                used_gb = (usage.total - usage.free) / (1024**3)
                free_gb = usage.free / (1024**3)
                
                drives.append({
                    'letter': '/',
                    'path': '/',
                    'name': 'Macintosh HD',
                    'total_gb': total_gb,
                    'used_gb': used_gb,
                    'free_gb': free_gb,
                    'usage_percent': (used_gb / total_gb) * 100 if total_gb > 0 else 0
                })
            except (OSError, PermissionError):
                pass
            
            # Add mounted volumes in /Volumes
            volumes_path = Path('/Volumes')
            if volumes_path.exists():
                for volume in volumes_path.iterdir():
                    if volume.is_dir() and volume.name != 'Macintosh HD':
                        try:
                            usage = shutil.disk_usage(str(volume))
                            total_gb = usage.total / (1024**3)
                            used_gb = (usage.total - usage.free) / (1024**3)
                            free_gb = usage.free / (1024**3)
                            
                            drives.append({
                                'letter': volume.name[:1].upper(),
                                'path': str(volume),
                                'name': volume.name,
                                'total_gb': total_gb,
                                'used_gb': used_gb,
                                'free_gb': free_gb,
                                'usage_percent': (used_gb / total_gb) * 100 if total_gb > 0 else 0
                            })
                        except (OSError, PermissionError):
                            # Volume not accessible
                            drives.append({
                                'letter': volume.name[:1].upper(),
                                'path': str(volume),
                                'name': volume.name,
                                'total_gb': 0,
                                'used_gb': 0,
                                'free_gb': 0,
                                'usage_percent': 0
                            })
                            
        else:  # Linux and other Unix-like
            # Add root filesystem
            try:
                usage = shutil.disk_usage('/')
                total_gb = usage.total / (1024**3)
                used_gb = (usage.total - usage.free) / (1024**3)
                free_gb = usage.free / (1024**3)
                
                drives.append({
                    'letter': '/',
                    'path': '/',
                    'name': 'Root',
                    'total_gb': total_gb,
                    'used_gb': used_gb,
                    'free_gb': free_gb,
                    'usage_percent': (used_gb / total_gb) * 100 if total_gb > 0 else 0
                })
            except (OSError, PermissionError):
                pass
            
            # Add common mount points
            mount_points = ['/media', '/mnt', '/home']
            for mount_base in mount_points:
                mount_path = Path(mount_base)
                if mount_path.exists():
                    for mount in mount_path.iterdir():
                        if mount.is_dir():
                            try:
                                usage = shutil.disk_usage(str(mount))
                                total_gb = usage.total / (1024**3)
                                used_gb = (usage.total - usage.free) / (1024**3)
                                free_gb = usage.free / (1024**3)
                                
                                # Skip if it's the same as root filesystem
                                if mount != Path('/'):
                                    drives.append({
                                        'letter': mount.name[:1].upper(),
                                        'path': str(mount),
                                        'name': mount.name,
                                        'total_gb': total_gb,
                                        'used_gb': used_gb,
                                        'free_gb': free_gb,
                                        'usage_percent': (used_gb / total_gb) * 100 if total_gb > 0 else 0
                                    })
                            except (OSError, PermissionError):
                                pass
                                
        return drives
    
    def _on_item_clicked(self, item, column):
        """Handle item click"""
        path = item.data(0, Qt.UserRole)
        if path:
            self.location_changed.emit(path)
