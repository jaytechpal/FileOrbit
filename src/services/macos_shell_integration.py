"""
macOS-specific shell integration and context menu implementation

Provides native macOS Finder integration using Cocoa APIs and NSMenu
for authentic macOS context menu behavior.
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import platform

from PySide6.QtWidgets import QWidget

from src.core.shell_integration_interfaces import IShellIntegrationProvider
from src.utils.logger import get_logger


class MacOSShellIntegration(IShellIntegrationProvider):
    """
    macOS-specific shell integration using Finder and system APIs.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._verify_macos()
        
        # Cache for application discovery
        self._app_cache = {}
        self._default_apps_cache = {}
        
        self.logger.info("MacOSShellIntegration initialized")
    
    def _verify_macos(self):
        """Verify we're running on macOS."""
        if platform.system() != 'Darwin':
            raise RuntimeError("MacOSShellIntegration can only be used on macOS")
    
    def get_context_menu_actions(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """
        Get macOS-native context menu actions for selected files.
        """
        try:
            if not file_paths:
                return []
            
            actions = []
            first_file = file_paths[0]
            is_single_file = len(file_paths) == 1
            is_directory = first_file.is_dir()
            
            # Quick Look (macOS-specific)
            if is_single_file and not is_directory:
                actions.append({
                    "text": "Quick Look",
                    "action": "quick_look",
                    "icon": "quicklook",
                    "shortcut": "Space"
                })
                actions.append({"separator": True})
            
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
                    "shortcut": "Cmd+X"
                },
                {
                    "text": "Copy",
                    "action": "copy", 
                    "icon": "copy",
                    "shortcut": "Cmd+C"
                }
            ])
            
            actions.append({"separator": True})
            
            # Duplicate (macOS-specific)
            if is_single_file:
                actions.append({
                    "text": "Duplicate",
                    "action": "duplicate",
                    "icon": "duplicate",
                    "shortcut": "Cmd+D"
                })
            
            # Make Alias (macOS equivalent of shortcut)
            if is_single_file:
                actions.append({
                    "text": "Make Alias",
                    "action": "make_alias",
                    "icon": "alias"
                })
            
            actions.append({"separator": True})
            
            # Share (macOS-specific)
            if len(file_paths) <= 10:  # Limit sharing to reasonable number
                share_options = self._get_share_options()
                if share_options:
                    actions.append({
                        "text": "Share",
                        "icon": "share",
                        "submenu": share_options
                    })
            
            # Compress (Archive Utility)
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
                "shortcut": "Cmd+Delete"
            })
            
            actions.append({"separator": True})
            
            # Get Info (macOS Properties)
            if is_single_file:
                actions.append({
                    "text": "Get Info",
                    "action": "get_info",
                    "icon": "info",
                    "shortcut": "Cmd+I"
                })
            else:
                actions.append({
                    "text": "Get Info",
                    "action": "get_info",
                    "icon": "info"
                })
            
            return actions
            
        except Exception as e:
            self.logger.error(f"Failed to get context menu actions: {e}")
            return []
    
    def get_empty_area_context_menu(self, current_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        Get macOS context menu for empty area.
        """
        try:
            actions = []
            
            # New Folder
            actions.append({
                "text": "New Folder",
                "action": "new_folder", 
                "icon": "folder_new",
                "shortcut": "Shift+Cmd+N"
            })
            
            actions.append({"separator": True})
            
            # Paste
            actions.append({
                "text": "Paste",
                "action": "paste",
                "icon": "paste",
                "shortcut": "Cmd+V"
            })
            
            actions.append({"separator": True})
            
            # View Options (macOS-specific)
            view_options = [
                {
                    "text": "as Icons",
                    "action": "view_as_icons",
                    "checkable": True
                },
                {
                    "text": "as List", 
                    "action": "view_as_list",
                    "checkable": True
                },
                {
                    "text": "as Columns",
                    "action": "view_as_columns", 
                    "checkable": True
                },
                {
                    "text": "as Gallery",
                    "action": "view_as_gallery",
                    "checkable": True
                }
            ]
            
            actions.append({
                "text": "View",
                "icon": "view",
                "submenu": view_options
            })
            
            # Sort By
            sort_options = [
                {"text": "Name", "action": "sort_by_name", "checkable": True},
                {"text": "Kind", "action": "sort_by_kind", "checkable": True},
                {"text": "Date Modified", "action": "sort_by_date_modified", "checkable": True},
                {"text": "Date Created", "action": "sort_by_date_created", "checkable": True},
                {"text": "Size", "action": "sort_by_size", "checkable": True},
                {"text": "Tags", "action": "sort_by_tags", "checkable": True}
            ]
            
            actions.append({
                "text": "Sort By",
                "icon": "sort",
                "submenu": sort_options
            })
            
            actions.append({"separator": True})
            
            # Show View Options
            actions.append({
                "text": "Show View Options",
                "action": "show_view_options",
                "icon": "preferences",
                "shortcut": "Cmd+J"
            })
            
            return actions
            
        except Exception as e:
            self.logger.error(f"Failed to get empty area context menu: {e}")
            return []
    
    def execute_action(self, action_name: str, file_paths: List[Path], **kwargs) -> bool:
        """
        Execute macOS-specific actions.
        """
        try:
            self.logger.debug(f"Executing macOS action: {action_name}")
            
            if action_name == "quick_look" and file_paths:
                return self._quick_look(file_paths[0])
            elif action_name == "open":
                return self._open_files(file_paths)
            elif action_name == "open_in_new_tab":
                # This will be handled by the calling code
                return True
            elif action_name == "duplicate" and file_paths:
                return self._duplicate_file(file_paths[0])
            elif action_name == "make_alias" and file_paths:
                return self._make_alias(file_paths[0])
            elif action_name == "compress":
                return self._compress_files(file_paths)
            elif action_name == "get_info":
                return self._show_get_info(file_paths)
            elif action_name == "new_folder":
                current_path = kwargs.get('current_path')
                return self._create_new_folder(current_path)
            elif action_name.startswith("open_with_"):
                app_path = action_name.replace("open_with_", "")
                return self._open_with_application(file_paths, app_path)
            else:
                # Handle standard actions (cut, copy, paste, etc.)
                return self._execute_standard_action(action_name, file_paths, **kwargs)
                
        except Exception as e:
            self.logger.error(f"Failed to execute action {action_name}: {e}")
            return False
    
    def get_default_applications(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Get default applications for a file type on macOS.
        """
        try:
            if file_path.suffix in self._default_apps_cache:
                return self._default_apps_cache[file_path.suffix]
            
            apps = []
            
            # Use Launch Services to get default applications
            # This is a simplified version - full implementation would use PyObjC
            try:
                import subprocess
                result = subprocess.run([
                    'duti', '-l', file_path.suffix[1:] if file_path.suffix else 'public.data'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if '\t' in line:
                            bundle_id, uti = line.split('\t', 1)
                            app_name = self._get_app_name_from_bundle_id(bundle_id)
                            if app_name:
                                apps.append({
                                    "name": app_name,
                                    "path": bundle_id,
                                    "icon": "app_extension"
                                })
            except (subprocess.SubprocessError, FileNotFoundError):
                # Fallback to common applications
                apps = self._get_fallback_applications(file_path)
            
            self._default_apps_cache[file_path.suffix] = apps
            return apps
            
        except Exception as e:
            self.logger.error(f"Failed to get default applications: {e}")
            return []
    
    def supports_trash(self) -> bool:
        """macOS supports Trash."""
        return True
    
    def move_to_trash(self, file_paths: List[Path]) -> bool:
        """
        Move files to macOS Trash using osascript.
        """
        try:
            for file_path in file_paths:
                script = f'''
                tell application "Finder"
                    move POSIX file "{file_path}" to trash
                end tell
                '''
                
                result = subprocess.run([
                    'osascript', '-e', script
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.logger.error(f"Failed to move {file_path} to trash: {result.stderr}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to move files to trash: {e}")
            return False
    
    def get_file_properties_dialog(self, file_path: Path, parent: QWidget) -> bool:
        """
        Show macOS Get Info dialog.
        """
        try:
            script = f'''
            tell application "Finder"
                open information window of (POSIX file "{file_path}" as alias)
            end tell
            '''
            
            result = subprocess.run([
                'osascript', '-e', script
            ], capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Failed to show Get Info dialog: {e}")
            return False
    
    def _get_open_with_applications(self, file_path: Path) -> List[Dict[str, Any]]:
        """Get applications that can open the file."""
        apps = self.get_default_applications(file_path)
        
        # Add "Other..." option
        apps.append({
            "separator": True
        })
        apps.append({
            "text": "Other...",
            "action": "choose_application",
            "icon": "app_extension"
        })
        
        return apps
    
    def _get_share_options(self) -> List[Dict[str, Any]]:
        """Get macOS sharing options."""
        return [
            {
                "text": "AirDrop",
                "action": "share_airdrop",
                "icon": "airdrop"
            },
            {
                "text": "Mail",
                "action": "share_mail", 
                "icon": "mail"
            },
            {
                "text": "Messages",
                "action": "share_messages",
                "icon": "messages"
            },
            {
                "separator": True
            },
            {
                "text": "More...",
                "action": "share_more",
                "icon": "share"
            }
        ]
    
    def _quick_look(self, file_path: Path) -> bool:
        """Show Quick Look preview."""
        try:
            subprocess.Popen(['qlmanage', '-p', str(file_path)])
            return True
        except Exception as e:
            self.logger.error(f"Failed to show Quick Look: {e}")
            return False
    
    def _open_files(self, file_paths: List[Path]) -> bool:
        """Open files with default applications."""
        try:
            for file_path in file_paths:
                subprocess.Popen(['open', str(file_path)])
            return True
        except Exception as e:
            self.logger.error(f"Failed to open files: {e}")
            return False
    
    def _duplicate_file(self, file_path: Path) -> bool:
        """Duplicate a file (macOS-style)."""
        try:
            script = f'''
            tell application "Finder"
                duplicate (POSIX file "{file_path}" as alias)
            end tell
            '''
            
            result = subprocess.run([
                'osascript', '-e', script
            ], capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Failed to duplicate file: {e}")
            return False
    
    def _make_alias(self, file_path: Path) -> bool:
        """Create an alias (macOS shortcut)."""
        try:
            script = f'''
            tell application "Finder"
                make alias file to (POSIX file "{file_path}" as alias) at (container of (POSIX file "{file_path}" as alias))
            end tell
            '''
            
            result = subprocess.run([
                'osascript', '-e', script
            ], capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Failed to make alias: {e}")
            return False
    
    def _compress_files(self, file_paths: List[Path]) -> bool:
        """Compress files using Archive Utility."""
        try:
            # Create zip archive using ditto (macOS built-in)
            if len(file_paths) == 1:
                archive_name = f"{file_paths[0].stem}.zip"
            else:
                archive_name = "Archive.zip"
            
            archive_path = file_paths[0].parent / archive_name
            
            # Use ditto to create zip archive
            cmd = ['ditto', '-c', '-k', '--sequesterRsrc', '--keepParent']
            cmd.extend([str(p) for p in file_paths])
            cmd.append(str(archive_path))
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Failed to compress files: {e}")
            return False
    
    def _show_get_info(self, file_paths: List[Path]) -> bool:
        """Show Get Info dialog for files."""
        try:
            for file_path in file_paths:
                if not self.get_file_properties_dialog(file_path, None):
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Failed to show Get Info: {e}")
            return False
    
    def _create_new_folder(self, current_path: Optional[Path]) -> bool:
        """Create a new folder."""
        try:
            if not current_path:
                current_path = Path.home()
            
            script = f'''
            tell application "Finder"
                make new folder at (POSIX file "{current_path}" as alias)
            end tell
            '''
            
            result = subprocess.run([
                'osascript', '-e', script
            ], capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Failed to create new folder: {e}")
            return False
    
    def _open_with_application(self, file_paths: List[Path], app_identifier: str) -> bool:
        """Open files with specific application."""
        try:
            for file_path in file_paths:
                subprocess.Popen(['open', '-a', app_identifier, str(file_path)])
            return True
        except Exception as e:
            self.logger.error(f"Failed to open with application: {e}")
            return False
    
    def _execute_standard_action(self, action_name: str, file_paths: List[Path], **kwargs) -> bool:
        """Execute standard actions (cut, copy, paste, etc.)."""
        # These will be handled by the main application
        # Return True to indicate the action is supported
        return action_name in ['cut', 'copy', 'paste', 'delete', 'rename']
    
    def _get_app_name_from_bundle_id(self, bundle_id: str) -> Optional[str]:
        """Get application name from bundle identifier."""
        try:
            # This is a simplified implementation
            # Full implementation would use PyObjC to query Launch Services
            app_mappings = {
                'com.apple.TextEdit': 'TextEdit',
                'com.apple.Preview': 'Preview',
                'com.apple.Safari': 'Safari',
                'com.apple.QuickTimePlayerX': 'QuickTime Player',
                'com.apple.finder': 'Finder',
                'com.microsoft.VSCode': 'Visual Studio Code',
                'com.sublimetext.4': 'Sublime Text',
                'com.adobe.Photoshop': 'Adobe Photoshop'
            }
            
            return app_mappings.get(bundle_id, bundle_id.split('.')[-1].title())
            
        except Exception:
            return None
    
    def _get_fallback_applications(self, file_path: Path) -> List[Dict[str, Any]]:
        """Get fallback applications when system lookup fails."""
        apps = []
        
        # Common applications by file extension
        ext = file_path.suffix.lower()
        
        if ext in ['.txt', '.md', '.py', '.js', '.html', '.css']:
            apps.extend([
                {"name": "TextEdit", "path": "com.apple.TextEdit", "icon": "app_extension"},
                {"name": "Visual Studio Code", "path": "com.microsoft.VSCode", "icon": "app_extension"}
            ])
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            apps.extend([
                {"name": "Preview", "path": "com.apple.Preview", "icon": "app_extension"},
                {"name": "Photos", "path": "com.apple.Photos", "icon": "app_extension"}
            ])
        elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
            apps.extend([
                {"name": "QuickTime Player", "path": "com.apple.QuickTimePlayerX", "icon": "app_extension"},
                {"name": "VLC", "path": "org.videolan.vlc", "icon": "app_extension"}
            ])
        elif ext in ['.mp3', '.wav', '.flac', '.m4a']:
            apps.extend([
                {"name": "Music", "path": "com.apple.Music", "icon": "app_extension"},
                {"name": "QuickTime Player", "path": "com.apple.QuickTimePlayerX", "icon": "app_extension"}
            ])
        
        return apps