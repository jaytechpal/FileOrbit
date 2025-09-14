"""
Cross-Platform File System Utilities
Provides unified file system operations across Windows, macOS, and Linux
"""

import os
import stat
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

try:
    import winreg
    HAS_WINREG = True
except ImportError:
    HAS_WINREG = False

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from platform_config import get_platform_config


class CrossPlatformFileSystem:
    """Cross-platform file system operations"""
    
    def __init__(self):
        self.config = get_platform_config()
        self.is_windows = self.config.is_windows
        self.is_macos = self.config.is_macos
        self.is_linux = self.config.is_linux
    
    def get_drives(self) -> List[Dict[str, Any]]:
        """Get list of available drives/mount points"""
        drives = []
        
        if self.is_windows:
            drives = self._get_windows_drives()
        elif self.is_macos:
            drives = self._get_macos_volumes()
        else:  # Linux and other Unix-like
            drives = self._get_linux_mounts()
        
        return drives
    
    def _get_windows_drives(self) -> List[Dict[str, Any]]:
        """Get Windows drives using cross-platform methods"""
        drives = []
        
        if HAS_PSUTIL:
            # Use psutil for cross-platform drive detection
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    drive_info = {
                        'path': partition.mountpoint,
                        'label': partition.mountpoint.rstrip('\\'),
                        'filesystem': partition.fstype or 'Unknown',
                        'type': self._get_drive_type(partition),
                        'total_space': usage.total,
                        'free_space': usage.free,
                        'used_space': usage.used,
                        'usage_percent': (usage.used / usage.total * 100) if usage.total > 0 else 0
                    }
                    drives.append(drive_info)
                except (PermissionError, OSError):
                    # Drive not accessible, skip it
                    continue
        else:
            # Fallback to simple drive detection
            import string
            for letter in string.ascii_uppercase:
                drive_path = f"{letter}:\\"
                if os.path.exists(drive_path):
                    try:
                        stat_info = os.statvfs(drive_path) if hasattr(os, 'statvfs') else None
                        drive_info = {
                            'path': drive_path,
                            'label': letter,
                            'filesystem': 'Unknown',
                            'type': 'drive',
                            'total_space': stat_info.f_frsize * stat_info.f_blocks if stat_info else 0,
                            'free_space': stat_info.f_frsize * stat_info.f_bavail if stat_info else 0,
                            'used_space': 0,
                            'usage_percent': 0
                        }
                        drives.append(drive_info)
                    except (PermissionError, OSError):
                        continue
        
        return drives
    
    def _get_macos_volumes(self) -> List[Dict[str, Any]]:
        """Get macOS volumes and mount points"""
        drives = []
        
        # Add root filesystem
        drives.append(self._get_mount_info('/', 'Macintosh HD'))
        
        # Check /Volumes for mounted drives
        volumes_path = Path('/Volumes')
        if volumes_path.exists():
            for volume in volumes_path.iterdir():
                if volume.is_dir() and not volume.name.startswith('.'):
                    drives.append(self._get_mount_info(str(volume), volume.name))
        
        return drives
    
    def _get_linux_mounts(self) -> List[Dict[str, Any]]:
        """Get Linux mount points"""
        drives = []
        
        # Add root filesystem
        drives.append(self._get_mount_info('/', 'Root'))
        
        # Check common mount points
        common_mounts = ['/home', '/media', '/mnt', '/opt', '/usr', '/var']
        for mount_point in common_mounts:
            if os.path.exists(mount_point) and os.path.ismount(mount_point):
                drives.append(self._get_mount_info(mount_point, os.path.basename(mount_point)))
        
        # Check /media and /mnt for user mounts
        for base_path in ['/media', '/mnt']:
            if os.path.exists(base_path):
                try:
                    for item in os.listdir(base_path):
                        item_path = os.path.join(base_path, item)
                        if os.path.ismount(item_path):
                            drives.append(self._get_mount_info(item_path, item))
                except PermissionError:
                    continue
        
        return drives
    
    def _get_mount_info(self, path: str, label: str) -> Dict[str, Any]:
        """Get mount point information"""
        try:
            if HAS_PSUTIL:
                usage = psutil.disk_usage(path)
                return {
                    'path': path,
                    'label': label,
                    'filesystem': 'Unknown',
                    'type': 'mount',
                    'total_space': usage.total,
                    'free_space': usage.free,
                    'used_space': usage.used,
                    'usage_percent': (usage.used / usage.total * 100) if usage.total > 0 else 0
                }
            else:
                stat_info = os.statvfs(path)
                total = stat_info.f_frsize * stat_info.f_blocks
                free = stat_info.f_frsize * stat_info.f_bavail
                used = total - free
                return {
                    'path': path,
                    'label': label,
                    'filesystem': 'Unknown',
                    'type': 'mount',
                    'total_space': total,
                    'free_space': free,
                    'used_space': used,
                    'usage_percent': (used / total * 100) if total > 0 else 0
                }
        except (OSError, PermissionError):
            return {
                'path': path,
                'label': label,
                'filesystem': 'Unknown',
                'type': 'mount',
                'total_space': 0,
                'free_space': 0,
                'used_space': 0,
                'usage_percent': 0
            }
    
    def _get_drive_type(self, partition) -> str:
        """Determine drive type from partition info"""
        if hasattr(partition, 'opts') and partition.opts:
            if 'removable' in partition.opts:
                return 'removable'
            elif 'network' in partition.opts:
                return 'network'
        
        # Check by filesystem type
        if partition.fstype in ['vfat', 'exfat', 'fat32']:
            return 'removable'
        elif partition.fstype in ['cifs', 'nfs', 'smb']:
            return 'network'
        else:
            return 'fixed'
    
    def get_file_associations(self, file_extension: str) -> List[Dict[str, str]]:
        """Get file associations for a given extension"""
        associations = []
        
        if self.is_windows and HAS_WINREG:
            associations = self._get_windows_file_associations(file_extension)
        elif self.is_macos:
            associations = self._get_macos_file_associations(file_extension)
        elif self.is_linux:
            associations = self._get_linux_file_associations(file_extension)
        
        return associations
    
    def _get_windows_file_associations(self, file_extension: str) -> List[Dict[str, str]]:
        """Get Windows file associations from registry"""
        associations = []
        
        try:
            # Get file type from extension
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, file_extension) as key:
                file_type, _ = winreg.QueryValueEx(key, "")
            
            # Get command from file type
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{file_type}\\shell\\open\\command") as key:
                command, _ = winreg.QueryValueEx(key, "")
                
                # Extract executable name
                app_name = "Unknown Application"
                if '"' in command:
                    exe_path = command.split('"')[1]
                    app_name = Path(exe_path).stem
                else:
                    exe_path = command.split()[0]
                    app_name = Path(exe_path).stem
                
                associations.append({
                    'name': app_name,
                    'command': command,
                    'is_default': True
                })
        except (WindowsError, FileNotFoundError, KeyError):
            pass
        
        return associations
    
    def _get_macos_file_associations(self, file_extension: str) -> List[Dict[str, str]]:
        """Get macOS file associations using Launch Services"""
        associations = []
        
        try:
            # Use lsregister to get file associations
            result = subprocess.run([
                '/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister',
                '-dump'
            ], capture_output=True, text=True, timeout=10)
            
            # Parse output for file extension associations
            # This is a simplified approach - full implementation would be more complex
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if file_extension in line and 'path:' in line:
                        parts = line.split('path:')
                        if len(parts) > 1:
                            app_path = parts[1].strip()
                            app_name = Path(app_path).name.replace('.app', '')
                            associations.append({
                                'name': app_name,
                                'command': app_path,
                                'is_default': True
                            })
                            break
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        
        return associations
    
    def _get_linux_file_associations(self, file_extension: str) -> List[Dict[str, str]]:
        """Get Linux file associations using xdg-mime"""
        associations = []
        
        try:
            # Get MIME type for extension
            result = subprocess.run([
                'xdg-mime', 'query', 'filetype', f'dummy{file_extension}'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                mime_type = result.stdout.strip()
                
                # Get default application for MIME type
                result = subprocess.run([
                    'xdg-mime', 'query', 'default', mime_type
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    desktop_file = result.stdout.strip()
                    app_name = desktop_file.replace('.desktop', '')
                    associations.append({
                        'name': app_name,
                        'command': 'xdg-open %f',
                        'is_default': True
                    })
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        
        return associations
    
    def open_file_with_default_app(self, file_path: str) -> bool:
        """Open file with default application"""
        try:
            file_path = str(Path(file_path).resolve())
            
            if self.is_windows:
                os.startfile(file_path)
            elif self.is_macos:
                subprocess.run(['open', file_path], check=True)
            else:  # Linux and others
                subprocess.run(['xdg-open', file_path], check=True)
            
            return True
        except (subprocess.SubprocessError, OSError):
            return False
    
    def open_file_properties(self, file_path: str) -> bool:
        """Open file properties dialog"""
        try:
            file_path = str(Path(file_path).resolve())
            
            if self.is_windows:
                subprocess.run(['explorer', '/select,', file_path], check=True)
            elif self.is_macos:
                subprocess.run(['open', '-R', file_path], check=True)
            else:  # Linux
                # Try different file managers
                file_managers = ['nautilus', 'dolphin', 'thunar', 'pcmanfm']
                for fm in file_managers:
                    try:
                        subprocess.run([fm, '--select', file_path], check=True)
                        return True
                    except (subprocess.SubprocessError, FileNotFoundError):
                        continue
                
                # Fallback to opening parent directory
                parent_dir = str(Path(file_path).parent)
                subprocess.run(['xdg-open', parent_dir], check=True)
            
            return True
        except (subprocess.SubprocessError, OSError):
            return False
    
    def move_to_trash(self, file_path: str) -> bool:
        """Move file to trash/recycle bin"""
        try:
            file_path = Path(file_path)
            
            if self.is_windows:
                # Use send2trash library if available, otherwise delete
                try:
                    import send2trash
                    send2trash.send2trash(str(file_path))
                    return True
                except ImportError:
                    return self._windows_recycle_bin(file_path)
            
            elif self.is_macos:
                # Move to Trash
                subprocess.run([
                    'osascript', '-e',
                    f'tell application "Finder" to delete POSIX file "{file_path}"'
                ], check=True)
                return True
            
            else:  # Linux
                # Use trash-cli if available
                try:
                    subprocess.run(['trash', str(file_path)], check=True)
                    return True
                except (subprocess.SubprocessError, FileNotFoundError):
                    return self._linux_trash(file_path)
        
        except (subprocess.SubprocessError, OSError):
            return False
    
    def _windows_recycle_bin(self, file_path: Path) -> bool:
        """Move to Windows recycle bin using shell operations"""
        try:
            # Try using shell operations
            import ctypes
            from ctypes import wintypes
            
            SHFileOperation = ctypes.windll.shell32.SHFileOperationW
            
            class SHFILEOPSTRUCT(ctypes.Structure):
                _fields_ = [
                    ("hwnd", wintypes.HWND),
                    ("wFunc", wintypes.UINT),
                    ("pFrom", wintypes.LPCWSTR),
                    ("pTo", wintypes.LPCWSTR),
                    ("fFlags", wintypes.USHORT),
                    ("fAnyOperationsAborted", wintypes.BOOL),
                    ("hNameMappings", wintypes.LPVOID),
                    ("lpszProgressTitle", wintypes.LPCWSTR),
                ]
            
            FO_DELETE = 3
            FOF_ALLOWUNDO = 64
            FOF_NOCONFIRMATION = 16
            
            file_op = SHFILEOPSTRUCT()
            file_op.wFunc = FO_DELETE
            file_op.pFrom = str(file_path) + '\0'
            file_op.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION
            
            result = SHFileOperation(ctypes.byref(file_op))
            return result == 0
        except Exception:
            return False
    
    def _linux_trash(self, file_path: Path) -> bool:
        """Move to Linux trash using freedesktop.org spec"""
        try:
            import time
            
            # Get trash directory
            if 'XDG_DATA_HOME' in os.environ:
                trash_dir = Path(os.environ['XDG_DATA_HOME']) / 'Trash'
            else:
                trash_dir = Path.home() / '.local' / 'share' / 'Trash'
            
            trash_files = trash_dir / 'files'
            trash_info = trash_dir / 'info'
            
            # Create trash directories
            trash_files.mkdir(parents=True, exist_ok=True)
            trash_info.mkdir(parents=True, exist_ok=True)
            
            # Generate unique name
            timestamp = int(time.time())
            base_name = file_path.name
            trash_name = f"{base_name}.{timestamp}"
            
            # Move file to trash
            trash_file_path = trash_files / trash_name
            shutil.move(str(file_path), str(trash_file_path))
            
            # Create info file
            info_content = f"""[Trash Info]
Path={file_path}
DeletionDate={datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}
"""
            info_file_path = trash_info / f"{trash_name}.trashinfo"
            info_file_path.write_text(info_content)
            
            return True
        except Exception:
            return False
    
    def get_file_type_icon(self, file_path: str) -> Optional[str]:
        """Get file type icon path"""
        # Platform-specific icon handling would go here
        # For now, return None to use Qt's default icon provider
        return None
    
    def get_file_description(self, file_path: str) -> str:
        """Get file type description"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        # Common file type descriptions
        descriptions = {
            '.txt': 'Text Document',
            '.pdf': 'PDF Document',
            '.doc': 'Microsoft Word Document',
            '.docx': 'Microsoft Word Document',
            '.xls': 'Microsoft Excel Spreadsheet',
            '.xlsx': 'Microsoft Excel Spreadsheet',
            '.ppt': 'Microsoft PowerPoint Presentation',
            '.pptx': 'Microsoft PowerPoint Presentation',
            '.jpg': 'JPEG Image',
            '.jpeg': 'JPEG Image',
            '.png': 'PNG Image',
            '.gif': 'GIF Image',
            '.bmp': 'Bitmap Image',
            '.mp3': 'MP3 Audio File',
            '.mp4': 'MP4 Video File',
            '.avi': 'AVI Video File',
            '.zip': 'ZIP Archive',
            '.rar': 'RAR Archive',
            '.py': 'Python Script',
            '.js': 'JavaScript File',
            '.html': 'HTML Document',
            '.css': 'CSS Stylesheet',
        }
        
        return descriptions.get(extension, f'{extension.upper()} File' if extension else 'File')
    
    def is_hidden_file(self, file_path: str) -> bool:
        """Check if file is hidden"""
        file_path = Path(file_path)
        
        if self.is_windows:
            # Check Windows hidden attribute
            try:
                attrs = os.stat(file_path).st_file_attributes
                return bool(attrs & stat.FILE_ATTRIBUTE_HIDDEN)
            except (AttributeError, OSError):
                # Fallback to name check
                return file_path.name.startswith('.')
        else:
            # Unix-like systems: files starting with . are hidden
            return file_path.name.startswith('.')
    
    def get_file_permissions(self, file_path: str) -> Dict[str, bool]:
        """Get file permissions"""
        try:
            file_stat = os.stat(file_path)
            mode = file_stat.st_mode
            
            return {
                'readable': bool(mode & stat.S_IRUSR),
                'writable': bool(mode & stat.S_IWUSR),
                'executable': bool(mode & stat.S_IXUSR),
                'owner_read': bool(mode & stat.S_IRUSR),
                'owner_write': bool(mode & stat.S_IWUSR),
                'owner_execute': bool(mode & stat.S_IXUSR),
                'group_read': bool(mode & stat.S_IRGRP),
                'group_write': bool(mode & stat.S_IWGRP),
                'group_execute': bool(mode & stat.S_IXGRP),
                'other_read': bool(mode & stat.S_IROTH),
                'other_write': bool(mode & stat.S_IWOTH),
                'other_execute': bool(mode & stat.S_IXOTH),
            }
        except OSError:
            return {
                'readable': False,
                'writable': False,
                'executable': False,
                'owner_read': False,
                'owner_write': False,
                'owner_execute': False,
                'group_read': False,
                'group_write': False,
                'group_execute': False,
                'other_read': False,
                'other_write': False,
                'other_execute': False,
            }


# Global cross-platform filesystem instance
cross_platform_fs = CrossPlatformFileSystem()


def get_cross_platform_fs() -> CrossPlatformFileSystem:
    """Get the global cross-platform filesystem instance"""
    return cross_platform_fs