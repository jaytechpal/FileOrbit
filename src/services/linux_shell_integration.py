"""
Linux-specific shell integration and context menu implementation

Provides native Linux desktop environment integration supporting GNOME, KDE, XFCE
and other desktop environments with their respective file managers and conventions.
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import platform

from PySide6.QtWidgets import QWidget

from src.core.shell_integration_interfaces import IShellIntegrationProvider, IDesktopEnvironment
from src.utils.logger import get_logger


class LinuxDesktopEnvironment(IDesktopEnvironment):
    """
    Linux desktop environment detection and integration.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._desktop_env = self._detect_desktop_environment()
        self.logger.info(f"Detected desktop environment: {self._desktop_env}")
    
    def _detect_desktop_environment(self) -> str:
        """Detect the current desktop environment."""
        # Check environment variables
        desktop_session = os.environ.get('DESKTOP_SESSION', '').lower()
        xdg_current_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        
        # GNOME detection
        if 'gnome' in desktop_session or 'gnome' in xdg_current_desktop:
            return 'gnome'
        elif 'unity' in desktop_session or 'ubuntu' in desktop_session:
            return 'gnome'  # Unity uses GNOME components
        
        # KDE detection
        if 'kde' in desktop_session or 'kde' in xdg_current_desktop:
            return 'kde'
        elif 'plasma' in desktop_session or 'plasma' in xdg_current_desktop:
            return 'kde'
        
        # XFCE detection
        if 'xfce' in desktop_session or 'xfce' in xdg_current_desktop:
            return 'xfce'
        
        # MATE detection
        if 'mate' in desktop_session or 'mate' in xdg_current_desktop:
            return 'mate'
        
        # Cinnamon detection
        if 'cinnamon' in desktop_session or 'cinnamon' in xdg_current_desktop:
            return 'cinnamon'
        
        # LXQt detection
        if 'lxqt' in desktop_session or 'lxqt' in xdg_current_desktop:
            return 'lxqt'
        
        # LXDE detection
        if 'lxde' in desktop_session or 'lxde' in xdg_current_desktop:
            return 'lxde'
        
        # Check for running processes as fallback
        try:
            # Check for common desktop environment processes
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            processes = result.stdout.lower()
            
            if 'gnome-shell' in processes or 'gnome-session' in processes:
                return 'gnome'
            elif 'kwin' in processes or 'plasmashell' in processes:
                return 'kde'
            elif 'xfwm4' in processes or 'xfce4-panel' in processes:
                return 'xfce'
            elif 'mate-panel' in processes:
                return 'mate'
            elif 'cinnamon' in processes:
                return 'cinnamon'
        except Exception:
            pass
        
        return 'unknown'
    
    def get_desktop_environment(self) -> str:
        """Get the current desktop environment name."""
        return self._desktop_env
    
    def get_file_manager_command(self) -> str:
        """Get the command to open the default file manager."""
        if self._desktop_env == 'gnome':
            return 'nautilus'
        elif self._desktop_env == 'kde':
            return 'dolphin'
        elif self._desktop_env == 'xfce':
            return 'thunar'
        elif self._desktop_env == 'mate':
            return 'caja'
        elif self._desktop_env == 'cinnamon':
            return 'nemo'
        elif self._desktop_env == 'lxqt':
            return 'pcmanfm-qt'
        elif self._desktop_env == 'lxde':
            return 'pcmanfm'
        else:
            # Try to find any available file manager
            for fm in ['nautilus', 'dolphin', 'thunar', 'pcmanfm', 'nemo', 'caja']:
                if shutil.which(fm):
                    return fm
            return 'xdg-open'
    
    def get_terminal_command(self) -> str:
        """Get the command to open the default terminal."""
        if self._desktop_env == 'gnome':
            return 'gnome-terminal'
        elif self._desktop_env == 'kde':
            return 'konsole'
        elif self._desktop_env == 'xfce':
            return 'xfce4-terminal'
        elif self._desktop_env == 'mate':
            return 'mate-terminal'
        elif self._desktop_env == 'cinnamon':
            return 'gnome-terminal'
        elif self._desktop_env == 'lxqt':
            return 'qterminal'
        elif self._desktop_env == 'lxde':
            return 'lxterminal'
        else:
            # Try to find any available terminal
            for term in ['gnome-terminal', 'konsole', 'xfce4-terminal', 'xterm', 'rxvt']:
                if shutil.which(term):
                    return term
            return 'x-terminal-emulator'
    
    def supports_desktop_notifications(self) -> bool:
        """Check if desktop notifications are supported."""
        return shutil.which('notify-send') is not None


class LinuxShellIntegration(IShellIntegrationProvider):
    """
    Linux-specific shell integration supporting multiple desktop environments.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._verify_linux()
        
        self.desktop_env = LinuxDesktopEnvironment()
        self._mime_cache = {}
        self._app_cache = {}
        
        self.logger.info("LinuxShellIntegration initialized")
    
    def _verify_linux(self):
        """Verify we're running on Linux."""
        if platform.system() != 'Linux':
            raise RuntimeError("LinuxShellIntegration can only be used on Linux")
    
    def get_context_menu_actions(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """
        Get Linux-native context menu actions for selected files.
        """
        try:
            if not file_paths:
                return []
            
            actions = []
            first_file = file_paths[0]
            is_single_file = len(file_paths) == 1
            is_directory = first_file.is_dir()
            
            # Open / Open With
            if is_single_file:
                if is_directory:
                    actions.append({
                        "text": "Open",
                        "action": "open",
                        "icon": "folder_open",
                        "bold": True
                    })
                    # Custom action for FileOrbit
                    actions.append({
                        "text": "Open in New Tab",
                        "action": "open_in_new_tab",
                        "icon": "tab_new"
                    })
                else:
                    actions.append({
                        "text": "Open",
                        "action": "open",
                        "icon": "file_open",
                        "bold": True
                    })
                
                # Open With submenu
                open_with_apps = self._get_open_with_applications(first_file)
                if open_with_apps:
                    actions.append({
                        "text": "Open With",
                        "icon": "open_with",
                        "submenu": open_with_apps
                    })
                
                actions.append({"separator": True})
            
            # Edit actions
            actions.extend([
                {
                    "text": "Cut",
                    "action": "cut",
                    "icon": "cut",
                    "shortcut": "Ctrl+X"
                },
                {
                    "text": "Copy",
                    "action": "copy",
                    "icon": "copy",
                    "shortcut": "Ctrl+C"
                }
            ])
            
            actions.append({"separator": True})
            
            # Create Link (Linux equivalent of shortcut/alias)
            if is_single_file:
                actions.append({
                    "text": "Make Link",
                    "action": "make_link",
                    "icon": "link"
                })
            
            # Send To submenu (desktop environment specific)
            send_to_options = self._get_send_to_options()
            if send_to_options:
                actions.append({
                    "text": "Send To",
                    "icon": "send_to",
                    "submenu": send_to_options
                })
            
            actions.append({"separator": True})
            
            # Compress (Create Archive)
            if len(file_paths) == 1:
                name = first_file.stem
                actions.append({
                    "text": f"Compress \"{name}\"",
                    "action": "compress",
                    "icon": "archive"
                })
            elif len(file_paths) > 1:
                actions.append({
                    "text": f"Compress {len(file_paths)} Items",
                    "action": "compress",
                    "icon": "archive"
                })
            
            actions.append({"separator": True})
            
            # Move to Trash
            actions.append({
                "text": "Move to Trash",
                "action": "move_to_trash",
                "icon": "trash",
                "shortcut": "Delete"
            })
            
            actions.append({"separator": True})
            
            # Properties
            if is_single_file:
                actions.append({
                    "text": "Properties",
                    "action": "properties",
                    "icon": "properties",
                    "shortcut": "Alt+Enter"
                })
            else:
                actions.append({
                    "text": "Properties",
                    "action": "properties",
                    "icon": "properties"
                })
            
            return actions
            
        except Exception as e:
            self.logger.error(f"Failed to get context menu actions: {e}")
            return []
    
    def get_empty_area_context_menu(self, current_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        Get Linux context menu for empty area.
        """
        try:
            actions = []
            
            # Create Folder
            actions.append({
                "text": "Create Folder",
                "action": "new_folder",
                "icon": "folder_new",
                "shortcut": "Ctrl+Shift+N"
            })
            
            # Create Document submenu (if supported by desktop environment)
            create_options = self._get_create_document_options()
            if create_options:
                actions.append({
                    "text": "Create Document",
                    "icon": "document_new",
                    "submenu": create_options
                })
            
            actions.append({"separator": True})
            
            # Paste
            actions.append({
                "text": "Paste",
                "action": "paste",
                "icon": "paste",
                "shortcut": "Ctrl+V"
            })
            
            actions.append({"separator": True})
            
            # Sort By
            sort_options = [
                {"text": "Name", "action": "sort_by_name", "checkable": True},
                {"text": "Size", "action": "sort_by_size", "checkable": True},
                {"text": "Type", "action": "sort_by_type", "checkable": True},
                {"text": "Date Modified", "action": "sort_by_date_modified", "checkable": True}
            ]
            
            actions.append({
                "text": "Sort By",
                "icon": "sort",
                "submenu": sort_options
            })
            
            # View options (desktop environment specific)
            view_options = self._get_view_options()
            if view_options:
                actions.append({
                    "text": "View",
                    "icon": "view",
                    "submenu": view_options
                })
            
            actions.append({"separator": True})
            
            # Open Terminal Here
            actions.append({
                "text": "Open in Terminal",
                "action": "open_terminal",
                "icon": "terminal",
                "shortcut": "F4"
            })
            
            # Properties (folder properties)
            actions.append({
                "text": "Properties",
                "action": "folder_properties",
                "icon": "properties"
            })
            
            return actions
            
        except Exception as e:
            self.logger.error(f"Failed to get empty area context menu: {e}")
            return []
    
    def execute_action(self, action_name: str, file_paths: List[Path], **kwargs) -> bool:
        """
        Execute Linux-specific actions.
        """
        try:
            self.logger.debug(f"Executing Linux action: {action_name}")
            
            if action_name == "open":
                return self._open_files(file_paths)
            elif action_name == "open_in_new_tab":
                # This will be handled by the calling code
                return True
            elif action_name == "make_link" and file_paths:
                return self._make_link(file_paths[0])
            elif action_name == "compress":
                return self._compress_files(file_paths)
            elif action_name == "properties":
                return self._show_properties(file_paths)
            elif action_name == "new_folder":
                current_path = kwargs.get('current_path')
                return self._create_new_folder(current_path)
            elif action_name == "open_terminal":
                current_path = kwargs.get('current_path')
                return self._open_terminal(current_path)
            elif action_name.startswith("open_with_"):
                app_name = action_name.replace("open_with_", "")
                return self._open_with_application(file_paths, app_name)
            else:
                # Handle standard actions
                return self._execute_standard_action(action_name, file_paths, **kwargs)
                
        except Exception as e:
            self.logger.error(f"Failed to execute action {action_name}: {e}")
            return False
    
    def get_default_applications(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Get default applications for a file type on Linux using MIME types.
        """
        try:
            mime_type = self._get_mime_type(file_path)
            if not mime_type:
                return []
            
            if mime_type in self._app_cache:
                return self._app_cache[mime_type]
            
            apps = []
            
            try:
                # Use xdg-mime to get default application
                result = subprocess.run([
                    'xdg-mime', 'query', 'default', mime_type
                ], capture_output=True, text=True)
                
                if result.returncode == 0 and result.stdout.strip():
                    desktop_file = result.stdout.strip()
                    app_info = self._parse_desktop_file(desktop_file)
                    if app_info:
                        apps.append(app_info)
                
                # Get all applications that can handle this MIME type
                result = subprocess.run([
                    'grep', '-l', f'MimeType.*{mime_type}',
                    '/usr/share/applications/*.desktop'
                ], capture_output=True, text=True, shell=True)
                
                if result.returncode == 0:
                    for desktop_file_path in result.stdout.strip().split('\n'):
                        if desktop_file_path and desktop_file_path.endswith('.desktop'):
                            app_info = self._parse_desktop_file(Path(desktop_file_path).name)
                            if app_info and app_info not in apps:
                                apps.append(app_info)
                
            except subprocess.SubprocessError:
                # Fallback to common applications
                apps = self._get_fallback_applications(file_path)
            
            self._app_cache[mime_type] = apps
            return apps
            
        except Exception as e:
            self.logger.error(f"Failed to get default applications: {e}")
            return []
    
    def supports_trash(self) -> bool:
        """Linux supports trash via gvfs-trash or gio."""
        return shutil.which('gio') is not None or shutil.which('gvfs-trash') is not None
    
    def move_to_trash(self, file_paths: List[Path]) -> bool:
        """
        Move files to Linux trash using gio or gvfs-trash.
        """
        try:
            # Try gio first (newer)
            if shutil.which('gio'):
                for file_path in file_paths:
                    result = subprocess.run([
                        'gio', 'trash', str(file_path)
                    ], capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        self.logger.error(f"Failed to trash {file_path}: {result.stderr}")
                        return False
                return True
            
            # Fallback to gvfs-trash
            elif shutil.which('gvfs-trash'):
                for file_path in file_paths:
                    result = subprocess.run([
                        'gvfs-trash', str(file_path)
                    ], capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        self.logger.error(f"Failed to trash {file_path}: {result.stderr}")
                        return False
                return True
            
            else:
                self.logger.warning("No trash command available")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to move files to trash: {e}")
            return False
    
    def get_file_properties_dialog(self, file_path: Path, parent: QWidget) -> bool:
        """
        Show Linux file properties dialog using desktop environment tools.
        """
        try:
            desktop_env = self.desktop_env.get_desktop_environment()
            
            if desktop_env == 'gnome':
                # Use nautilus properties
                subprocess.Popen(['nautilus', '--properties', str(file_path)])
                return True
            elif desktop_env == 'kde':
                # Use dolphin or kde properties
                if shutil.which('dolphin'):
                    subprocess.Popen(['dolphin', '--properties', str(file_path)])
                    return True
            elif desktop_env == 'xfce':
                # Use thunar properties
                if shutil.which('thunar'):
                    subprocess.Popen(['thunar', '--properties', str(file_path)])
                    return True
            
            # Fallback - try to open with default file manager
            file_manager = self.desktop_env.get_file_manager_command()
            if shutil.which(file_manager):
                subprocess.Popen([file_manager, str(file_path.parent)])
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to show properties dialog: {e}")
            return False
    
    def _get_open_with_applications(self, file_path: Path) -> List[Dict[str, Any]]:
        """Get applications that can open the file."""
        apps = self.get_default_applications(file_path)
        
        # Add "Other Application..." option
        if apps:
            apps.append({"separator": True})
        apps.append({
            "text": "Other Application...",
            "action": "choose_application",
            "icon": "app_extension"
        })
        
        return apps
    
    def _get_send_to_options(self) -> List[Dict[str, Any]]:
        """Get Send To options based on desktop environment."""
        options = []
        
        # Email
        if shutil.which('thunderbird') or shutil.which('evolution'):
            options.append({
                "text": "Email",
                "action": "send_to_email",
                "icon": "mail"
            })
        
        # Desktop
        options.append({
            "text": "Desktop",
            "action": "send_to_desktop",
            "icon": "desktop"
        })
        
        # Removable devices (simplified)
        options.append({
            "text": "Removable Device",
            "action": "send_to_removable",
            "icon": "usb"
        })
        
        return options
    
    def _get_create_document_options(self) -> List[Dict[str, Any]]:
        """Get Create Document options."""
        return [
            {
                "text": "Empty File",
                "action": "create_empty_file",
                "icon": "document_new"
            },
            {
                "text": "Text Document",
                "action": "create_text_document",
                "icon": "text_document"
            }
        ]
    
    def _get_view_options(self) -> List[Dict[str, Any]]:
        """Get view options based on desktop environment."""
        return [
            {"text": "Icons", "action": "view_as_icons", "checkable": True},
            {"text": "List", "action": "view_as_list", "checkable": True},
            {"text": "Details", "action": "view_as_details", "checkable": True}
        ]
    
    def _get_mime_type(self, file_path: Path) -> Optional[str]:
        """Get MIME type for a file."""
        try:
            result = subprocess.run([
                'file', '--mime-type', '-b', str(file_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip()
            
        except subprocess.SubprocessError:
            pass
        
        # Fallback: guess from extension
        ext = file_path.suffix.lower()
        mime_mappings = {
            '.txt': 'text/plain',
            '.py': 'text/x-python',
            '.js': 'application/javascript',
            '.html': 'text/html',
            '.css': 'text/css',
            '.jpg': 'image/jpeg',
            '.png': 'image/png',
            '.mp4': 'video/mp4',
            '.mp3': 'audio/mpeg',
            '.pdf': 'application/pdf'
        }
        
        return mime_mappings.get(ext, 'application/octet-stream')
    
    def _parse_desktop_file(self, desktop_file: str) -> Optional[Dict[str, Any]]:
        """Parse a .desktop file to extract application information."""
        try:
            # Look for the desktop file in standard locations
            desktop_paths = [
                f'/usr/share/applications/{desktop_file}',
                f'{os.path.expanduser("~")}/.local/share/applications/{desktop_file}'
            ]
            
            for desktop_path in desktop_paths:
                if os.path.exists(desktop_path):
                    with open(desktop_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    name = None
                    icon = None
                    
                    for line in content.split('\n'):
                        if line.startswith('Name='):
                            name = line.split('=', 1)[1]
                        elif line.startswith('Icon='):
                            icon = line.split('=', 1)[1]
                    
                    if name:
                        return {
                            "name": name,
                            "path": desktop_file,
                            "icon": icon or "app_extension"
                        }
            
        except Exception as e:
            self.logger.warning(f"Failed to parse desktop file {desktop_file}: {e}")
        
        return None
    
    def _open_files(self, file_paths: List[Path]) -> bool:
        """Open files with default applications."""
        try:
            for file_path in file_paths:
                subprocess.Popen(['xdg-open', str(file_path)])
            return True
        except Exception as e:
            self.logger.error(f"Failed to open files: {e}")
            return False
    
    def _make_link(self, file_path: Path) -> bool:
        """Create a symbolic link."""
        try:
            link_path = file_path.parent / f"{file_path.name} (link)"
            os.symlink(file_path, link_path)
            return True
        except Exception as e:
            self.logger.error(f"Failed to make link: {e}")
            return False
    
    def _compress_files(self, file_paths: List[Path]) -> bool:
        """Compress files using available archiver."""
        try:
            if shutil.which('file-roller'):
                # GNOME Archive Manager
                subprocess.Popen(['file-roller', '--add'] + [str(p) for p in file_paths])
                return True
            elif shutil.which('ark'):
                # KDE Ark
                subprocess.Popen(['ark', '--add'] + [str(p) for p in file_paths])
                return True
            else:
                # Fallback to zip command
                if len(file_paths) == 1:
                    archive_name = f"{file_paths[0].stem}.zip"
                else:
                    archive_name = "archive.zip"
                
                archive_path = file_paths[0].parent / archive_name
                cmd = ['zip', '-r', str(archive_path)] + [str(p) for p in file_paths]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.returncode == 0
                
        except Exception as e:
            self.logger.error(f"Failed to compress files: {e}")
            return False
    
    def _show_properties(self, file_paths: List[Path]) -> bool:
        """Show properties dialog for files."""
        try:
            for file_path in file_paths:
                if not self.get_file_properties_dialog(file_path, None):
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Failed to show properties: {e}")
            return False
    
    def _create_new_folder(self, current_path: Optional[Path]) -> bool:
        """Create a new folder."""
        try:
            if not current_path:
                current_path = Path.home()
            
            new_folder = current_path / "New Folder"
            counter = 1
            while new_folder.exists():
                new_folder = current_path / f"New Folder {counter}"
                counter += 1
            
            new_folder.mkdir()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create new folder: {e}")
            return False
    
    def _open_terminal(self, current_path: Optional[Path]) -> bool:
        """Open terminal in current path."""
        try:
            terminal_cmd = self.desktop_env.get_terminal_command()
            if current_path and current_path.is_dir():
                subprocess.Popen([terminal_cmd], cwd=str(current_path))
            else:
                subprocess.Popen([terminal_cmd])
            return True
        except Exception as e:
            self.logger.error(f"Failed to open terminal: {e}")
            return False
    
    def _open_with_application(self, file_paths: List[Path], app_identifier: str) -> bool:
        """Open files with specific application."""
        try:
            if app_identifier.endswith('.desktop'):
                # Use gtk-launch for .desktop files
                for file_path in file_paths:
                    subprocess.Popen(['gtk-launch', app_identifier, str(file_path)])
            else:
                # Direct command
                for file_path in file_paths:
                    subprocess.Popen([app_identifier, str(file_path)])
            return True
        except Exception as e:
            self.logger.error(f"Failed to open with application: {e}")
            return False
    
    def _execute_standard_action(self, action_name: str, file_paths: List[Path], **kwargs) -> bool:
        """Execute standard actions (cut, copy, paste, etc.)."""
        # These will be handled by the main application
        return action_name in ['cut', 'copy', 'paste', 'delete', 'rename']
    
    def _get_fallback_applications(self, file_path: Path) -> List[Dict[str, Any]]:
        """Get fallback applications when system lookup fails."""
        apps = []
        ext = file_path.suffix.lower()
        
        if ext in ['.txt', '.md', '.py', '.js', '.html', '.css']:
            apps.extend([
                {"name": "Text Editor", "path": "gedit", "icon": "text-editor"},
                {"name": "Visual Studio Code", "path": "code", "icon": "app_extension"}
            ])
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            apps.extend([
                {"name": "Image Viewer", "path": "eog", "icon": "image-viewer"},
                {"name": "GIMP", "path": "gimp", "icon": "app_extension"}
            ])
        elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
            apps.extend([
                {"name": "Videos", "path": "totem", "icon": "video-player"},
                {"name": "VLC", "path": "vlc", "icon": "app_extension"}
            ])
        elif ext in ['.mp3', '.wav', '.flac', '.m4a']:
            apps.extend([
                {"name": "Music", "path": "rhythmbox", "icon": "music-player"},
                {"name": "VLC", "path": "vlc", "icon": "app_extension"}
            ])
        
        return apps