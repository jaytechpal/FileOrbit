"""
Cross-Platform Shell Integration Service
Provides unified shell operations across Windows, macOS, and Linux
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Any

from platform_config import get_platform_config
from src.utils.logger import get_logger
from src.utils.cross_platform_filesystem import get_cross_platform_fs

# Import platform-specific implementations
try:
    from src.utils.windows_shell_wrapper import WindowsShell
    HAS_WINDOWS_SHELL = True
except ImportError:
    HAS_WINDOWS_SHELL = False

try:
    from src.services.macos_shell_integration import MacOSShellIntegration
    HAS_MACOS_SHELL = True
except ImportError:
    HAS_MACOS_SHELL = False

try:
    from src.services.linux_shell_integration import LinuxShellIntegration
    HAS_LINUX_SHELL = True
except ImportError:
    HAS_LINUX_SHELL = False


class CrossPlatformShellIntegration:
    """Cross-platform shell integration service"""
    
    def __init__(self):
        self.config = get_platform_config()
        self.logger = get_logger(__name__)
        self.fs = get_cross_platform_fs()
        
        # Initialize platform-specific shell integration
        self.platform_shell = None
        
        if self.config.is_windows and HAS_WINDOWS_SHELL:
            try:
                self.platform_shell = WindowsShell()
            except Exception as e:
                self.logger.warning(f"Failed to initialize Windows shell: {e}")
                
        elif self.config.is_macos and HAS_MACOS_SHELL:
            try:
                self.platform_shell = MacOSShellIntegration()
            except Exception as e:
                self.logger.warning(f"Failed to initialize macOS shell: {e}")
                
        elif self.config.is_linux and HAS_LINUX_SHELL:
            try:
                self.platform_shell = LinuxShellIntegration()
            except Exception as e:
                self.logger.warning(f"Failed to initialize Linux shell: {e}")
    
    def open_file_with_default_app(self, file_path: str) -> bool:
        """Open file with default application"""
        try:
            # Try platform-specific implementation first
            if self.platform_shell and hasattr(self.platform_shell, 'open_with_default_app'):
                return self.platform_shell.open_with_default_app(file_path)
            
            # Fallback to cross-platform filesystem implementation
            return self.fs.open_file_with_default_app(file_path)
            
        except Exception as e:
            self.logger.error(f"Error opening file with default app: {e}")
            return False
    
    def open_file_properties(self, file_path: str) -> bool:
        """Open file properties dialog"""
        try:
            # Try platform-specific implementation first
            if self.platform_shell and hasattr(self.platform_shell, 'show_properties'):
                return self.platform_shell.show_properties(file_path)
            
            # Fallback to cross-platform filesystem implementation
            return self.fs.open_file_properties(file_path)
            
        except Exception as e:
            self.logger.error(f"Error opening file properties: {e}")
            return False
    
    def show_in_explorer(self, file_path: str) -> bool:
        """Show file in file manager/explorer"""
        try:
            file_path = str(Path(file_path).resolve())
            
            if self.config.is_windows:
                # Windows Explorer
                if self.platform_shell and hasattr(self.platform_shell, 'show_in_explorer'):
                    return self.platform_shell.show_in_explorer(file_path)
                else:
                    subprocess.run(['explorer', '/select,', file_path], check=True)
                    return True
                    
            elif self.config.is_macos:
                # macOS Finder
                if self.platform_shell and hasattr(self.platform_shell, 'reveal_in_finder'):
                    return self.platform_shell.reveal_in_finder(file_path)
                else:
                    subprocess.run(['open', '-R', file_path], check=True)
                    return True
                    
            else:  # Linux and others
                # Linux file managers
                if self.platform_shell and hasattr(self.platform_shell, 'show_in_file_manager'):
                    return self.platform_shell.show_in_file_manager(file_path)
                else:
                    return self._linux_show_in_file_manager(file_path)
            
        except Exception as e:
            self.logger.error(f"Error showing file in explorer: {e}")
            return False
    
    def _linux_show_in_file_manager(self, file_path: str) -> bool:
        """Show file in Linux file manager"""
        file_managers = [
            ('nautilus', ['nautilus', '--select', file_path]),
            ('dolphin', ['dolphin', '--select', file_path]),
            ('thunar', ['thunar', '--select', file_path]),
            ('pcmanfm', ['pcmanfm', '--select', file_path]),
            ('nemo', ['nemo', '--select', file_path]),
        ]
        
        for fm_name, cmd in file_managers:
            try:
                subprocess.run(cmd, check=True)
                return True
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        # Fallback: open parent directory
        try:
            parent_dir = str(Path(file_path).parent)
            subprocess.run(['xdg-open', parent_dir], check=True)
            return True
        except Exception:
            return False
    
    def move_to_trash(self, file_path: str) -> bool:
        """Move file to trash/recycle bin"""
        try:
            # Try platform-specific implementation first
            if self.platform_shell and hasattr(self.platform_shell, 'move_to_trash'):
                return self.platform_shell.move_to_trash(file_path)
            
            # Fallback to cross-platform filesystem implementation
            return self.fs.move_to_trash(file_path)
            
        except Exception as e:
            self.logger.error(f"Error moving file to trash: {e}")
            return False
    
    def create_shortcut(self, target_path: str, shortcut_path: str, 
                       description: str = "", working_dir: str = "") -> bool:
        """Create shortcut/link to file"""
        try:
            target_path = Path(target_path)
            shortcut_path = Path(shortcut_path)
            
            if self.config.is_windows:
                return self._create_windows_shortcut(target_path, shortcut_path, description, working_dir)
            elif self.config.is_macos:
                return self._create_macos_alias(target_path, shortcut_path)
            else:  # Linux
                return self._create_linux_link(target_path, shortcut_path, description)
                
        except Exception as e:
            self.logger.error(f"Error creating shortcut: {e}")
            return False
    
    def _create_windows_shortcut(self, target_path: Path, shortcut_path: Path, 
                               description: str, working_dir: str) -> bool:
        """Create Windows shortcut"""
        try:
            # Try platform-specific implementation first
            if self.platform_shell and hasattr(self.platform_shell, 'create_shortcut'):
                return self.platform_shell.create_shortcut(
                    str(target_path), str(shortcut_path), description, working_dir
                )
            
            # Fallback using win32com if available
            try:
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(str(shortcut_path))
                shortcut.Targetpath = str(target_path)
                shortcut.Description = description
                if working_dir:
                    shortcut.WorkingDirectory = working_dir
                shortcut.save()
                return True
            except ImportError:
                # Create using PowerShell as fallback
                ps_script = f'''
                $WshShell = New-Object -comObject WScript.Shell
                $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
                $Shortcut.TargetPath = "{target_path}"
                $Shortcut.Description = "{description}"
                $Shortcut.WorkingDirectory = "{working_dir or target_path.parent}"
                $Shortcut.Save()
                '''
                result = subprocess.run(['powershell', '-Command', ps_script], 
                                      capture_output=True, text=True)
                return result.returncode == 0
                
        except Exception as e:
            self.logger.debug(f"Windows shortcut creation failed: {e}")
            return False
    
    def _create_macos_alias(self, target_path: Path, shortcut_path: Path) -> bool:
        """Create macOS alias"""
        try:
            # Use AppleScript to create alias
            applescript = f'''
            tell application "Finder"
                make alias file to (POSIX file "{target_path}") at (POSIX file "{shortcut_path.parent}")
                set name of result to "{shortcut_path.stem}"
            end tell
            '''
            result = subprocess.run(['osascript', '-e', applescript], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            self.logger.debug(f"macOS alias creation failed: {e}")
            return False
    
    def _create_linux_link(self, target_path: Path, shortcut_path: Path, description: str) -> bool:
        """Create Linux desktop file or symbolic link"""
        try:
            if shortcut_path.suffix == '.desktop':
                # Create desktop file
                desktop_content = f'''[Desktop Entry]
Type=Application
Name={shortcut_path.stem}
Comment={description}
Exec={target_path}
Icon={target_path}
Terminal=false
Categories=Application;
'''
                shortcut_path.write_text(desktop_content)
                shortcut_path.chmod(0o755)
                return True
            else:
                # Create symbolic link
                shortcut_path.symlink_to(target_path)
                return True
        except Exception as e:
            self.logger.debug(f"Linux link creation failed: {e}")
            return False
    
    def get_file_associations(self, file_extension: str) -> List[Dict[str, str]]:
        """Get file associations for extension"""
        try:
            # Try platform-specific implementation first
            if self.platform_shell and hasattr(self.platform_shell, 'get_file_associations'):
                return self.platform_shell.get_file_associations(file_extension)
            
            # Fallback to cross-platform filesystem implementation
            return self.fs.get_file_associations(file_extension)
            
        except Exception as e:
            self.logger.error(f"Error getting file associations: {e}")
            return []
    
    def open_with_application(self, file_path: str, app_path: str) -> bool:
        """Open file with specific application"""
        try:
            file_path = str(Path(file_path).resolve())
            app_path = str(Path(app_path).resolve())
            
            if self.config.is_windows:
                # Windows: Use start command or direct execution
                if self.platform_shell and hasattr(self.platform_shell, 'open_with_app'):
                    return self.platform_shell.open_with_app(file_path, app_path)
                else:
                    subprocess.run([app_path, file_path], check=True)
                    return True
                    
            elif self.config.is_macos:
                # macOS: Use open command
                if app_path.endswith('.app'):
                    subprocess.run(['open', '-a', app_path, file_path], check=True)
                else:
                    subprocess.run([app_path, file_path], check=True)
                return True
                
            else:  # Linux
                # Linux: Direct execution
                subprocess.run([app_path, file_path], check=True)
                return True
                
        except Exception as e:
            self.logger.error(f"Error opening file with application: {e}")
            return False
    
    def open_properties_dialog(self, file_path: Path) -> bool:
        """Open properties dialog for file/folder"""
        try:
            # Try platform-specific implementation first
            if self.platform_shell and hasattr(self.platform_shell, 'show_properties'):
                return self.platform_shell.show_properties(str(file_path))
            
            # Fallback implementation
            if self.config.is_windows:
                # Windows: Use shell32 properties dialog
                subprocess.run(['rundll32.exe', 'shell32.dll,OpenAs_RunDLL', str(file_path)], check=True)
                return True
            elif self.config.is_macos:
                # macOS: Use Finder's Get Info
                subprocess.run(['open', '-R', str(file_path)], check=True)
                return True
            else:  # Linux
                # Linux: Try common file managers
                for cmd in ['nautilus', 'dolphin', 'thunar', 'pcmanfm']:
                    try:
                        subprocess.run([cmd, '--properties', str(file_path)], check=True)
                        return True
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                return False
                
        except Exception as e:
            self.logger.error(f"Error opening properties dialog: {e}")
            return False
    
    def get_shell_folders(self) -> Dict[str, str]:
        """Get shell special folders"""
        folders = {}
        
        try:
            if self.config.is_windows:
                # Windows special folders
                folders.update({
                    'Desktop': str(self.config.get_desktop_directory()),
                    'Documents': str(self.config.get_documents_directory()),
                    'Downloads': str(Path.home() / 'Downloads'),
                    'Pictures': str(Path.home() / 'Pictures'),
                    'Music': str(Path.home() / 'Music'),
                    'Videos': str(Path.home() / 'Videos'),
                    'AppData': str(Path.home() / 'AppData'),
                    'Program Files': 'C:\\Program Files',
                    'Program Files (x86)': 'C:\\Program Files (x86)',
                })
                
            elif self.config.is_macos:
                # macOS special folders
                home = Path.home()
                folders.update({
                    'Desktop': str(home / 'Desktop'),
                    'Documents': str(home / 'Documents'),
                    'Downloads': str(home / 'Downloads'),
                    'Pictures': str(home / 'Pictures'),
                    'Music': str(home / 'Music'),
                    'Movies': str(home / 'Movies'),
                    'Applications': '/Applications',
                    'Library': str(home / 'Library'),
                })
                
            else:  # Linux
                # Linux special folders
                home = Path.home()
                folders.update({
                    'Desktop': str(home / 'Desktop'),
                    'Documents': str(home / 'Documents'),
                    'Downloads': str(home / 'Downloads'),
                    'Pictures': str(home / 'Pictures'),
                    'Music': str(home / 'Music'),
                    'Videos': str(home / 'Videos'),
                    'Applications': '/usr/share/applications',
                    'Local Applications': str(home / '.local' / 'share' / 'applications'),
                })
                
        except Exception as e:
            self.logger.error(f"Error getting shell folders: {e}")
        
        return folders
    
    def is_shell_integration_available(self) -> bool:
        """Check if shell integration is available"""
        return self.platform_shell is not None
    
    def get_context_menu_items(self, file_path: str) -> List[Dict[str, Any]]:
        """Get context menu items for file"""
        try:
            # Try platform-specific implementation first
            if self.platform_shell and hasattr(self.platform_shell, 'get_context_menu_items'):
                return self.platform_shell.get_context_menu_items(file_path)
            
            # Fallback: basic context menu items
            return self._get_basic_context_menu_items(file_path)
            
        except Exception as e:
            self.logger.error(f"Error getting context menu items: {e}")
            return []
    
    def _get_basic_context_menu_items(self, file_path: str) -> List[Dict[str, Any]]:
        """Get basic context menu items"""
        items = []
        file_path_obj = Path(file_path)
        
        # Basic items available on all platforms
        items.extend([
            {
                'text': 'Open',
                'action': 'open_default',
                'enabled': file_path_obj.exists()
            },
            {
                'text': 'Show in Explorer' if self.config.is_windows else 
                        'Reveal in Finder' if self.config.is_macos else 
                        'Show in File Manager',
                'action': 'show_in_explorer',
                'enabled': file_path_obj.exists()
            },
            {
                'text': 'Properties',
                'action': 'properties',
                'enabled': file_path_obj.exists()
            },
            {
                'text': 'Move to Trash' if not self.config.is_windows else 'Move to Recycle Bin',
                'action': 'move_to_trash',
                'enabled': file_path_obj.exists()
            }
        ])
        
        return items
    
    def get_empty_area_context_menu(self) -> List[Dict[str, Any]]:
        """Get context menu items for empty area (background)"""
        try:
            # Try platform-specific implementation first
            if self.platform_shell and hasattr(self.platform_shell, 'get_empty_area_context_menu'):
                return self.platform_shell.get_empty_area_context_menu()
            
            # Fallback: basic empty area menu items
            return self._get_basic_empty_area_menu()
            
        except Exception as e:
            self.logger.error(f"Error getting empty area context menu: {e}")
            return []
    
    def _get_basic_empty_area_menu(self) -> List[Dict[str, Any]]:
        """Get basic empty area context menu items"""
        items = []
        
        # Basic items for empty area
        items.extend([
            {
                'text': 'Refresh',
                'action': 'refresh',
                'enabled': True
            },
            {'separator': True},
            {
                'text': 'New',
                'submenu': [
                    {
                        'text': 'Folder',
                        'action': 'new_folder',
                        'enabled': True
                    },
                    {
                        'text': 'Text Document',
                        'action': 'new_text_file',
                        'enabled': True
                    }
                ]
            },
            {'separator': True},
            {
                'text': 'Paste',
                'action': 'paste',
                'enabled': True  # Should check clipboard state
            }
        ])
        
        # Platform-specific items
        if self.config.is_windows:
            items.extend([
                {'separator': True},
                {
                    'text': 'Open Command Prompt here',
                    'action': 'open_cmd',
                    'enabled': True
                },
                {
                    'text': 'Open PowerShell here',
                    'action': 'open_powershell',
                    'enabled': True
                }
            ])
        elif self.config.is_macos:
            items.extend([
                {'separator': True},
                {
                    'text': 'Open Terminal here',
                    'action': 'open_terminal',
                    'enabled': True
                }
            ])
        else:  # Linux
            items.extend([
                {'separator': True},
                {
                    'text': 'Open Terminal here',
                    'action': 'open_terminal',
                    'enabled': True
                }
            ])
        
        return items


# Global instance
cross_platform_shell = CrossPlatformShellIntegration()


def get_shell_integration() -> CrossPlatformShellIntegration:
    """Get the global shell integration instance"""
    return cross_platform_shell