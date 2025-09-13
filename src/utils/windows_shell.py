"""
Windows Shell Integration - Native Windows Explorer functionality
"""

import os
import sys
import subprocess
import winreg
from pathlib import Path
from typing import List, Dict, Optional
from src.utils.logger import get_logger


class WindowsShellIntegration:
    """Windows shell integration for Explorer-like functionality"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.is_windows = sys.platform == "win32"
        
        # Cache for performance optimization
        self._file_type_cache = {}
        self._shell_extensions_cache = {}
        self._app_availability_cache = {}
        self._specialized_extensions_cache = None
        self._common_extensions_cache = None
    
    def get_file_type_info(self, file_path: Path) -> Dict[str, str]:
        """Get file type information from Windows registry"""
        if not self.is_windows or not file_path.is_file():
            return {}
        
        try:
            ext = file_path.suffix.lower()
            if not ext:
                return {"type": "File", "description": "File"}
            
            # Get file type from registry
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, ext) as key:
                file_type, _ = winreg.QueryValueEx(key, "")
            
            # Get description
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, file_type) as key:
                    description, _ = winreg.QueryValueEx(key, "")
            except Exception:
                description = f"{ext.upper()} File"
            
            return {
                "type": file_type,
                "description": description,
                "extension": ext
            }
        except Exception as e:
            self.logger.debug(f"Error getting file type info: {e}")
            return {"type": "File", "description": f"{file_path.suffix.upper()} File"}
    
    def get_default_program(self, file_path: Path) -> Optional[str]:
        """Get default program for file type"""
        if not self.is_windows or not file_path.is_file():
            return None
        
        try:
            ext = file_path.suffix.lower()
            if not ext:
                return None
            
            # Get file type
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, ext) as key:
                file_type, _ = winreg.QueryValueEx(key, "")
            
            # Get default command
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{file_type}\\shell\\open\\command") as key:
                command, _ = winreg.QueryValueEx(key, "")
            
            # Extract program name from command
            if command.startswith('"'):
                program = command.split('"')[1]
            else:
                program = command.split()[0]
            
            return Path(program).name if Path(program).exists() else None
        except Exception as e:
            self.logger.debug(f"Error getting default program: {e}")
            return None
    
    def get_open_with_programs(self, file_path: Path) -> List[Dict[str, str]]:
        """Get list of programs that can open this file type"""
        if not self.is_windows or not file_path.is_file():
            return []
        
        programs = []
        try:
            ext = file_path.suffix.lower()
            
            # Add common programs
            common_programs = [
                {"name": "Notepad", "path": "notepad.exe", "args": '"{}"'},
                {"name": "WordPad", "path": "write.exe", "args": '"{}"'},
            ]
            
            if ext in ['.txt', '.log', '.md', '.py', '.js', '.html', '.css', '.json', '.xml']:
                programs.extend(common_programs)
            
            # Try to get from registry OpenWithList
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{ext}\\OpenWithList") as key:
                    i = 0
                    while True:
                        try:
                            program = winreg.EnumKey(key, i)
                            programs.append({
                                "name": program,
                                "path": program,
                                "args": '"{}"'
                            })
                            i += 1
                        except WindowsError:
                            break
            except Exception:
                pass
            
        except Exception as e:
            self.logger.debug(f"Error getting open with programs: {e}")
        
        return programs
    
    def open_properties_dialog(self, file_path: Path) -> bool:
        """Open Windows properties dialog for file/folder"""
        if not self.is_windows:
            return False
        
        try:
            subprocess.run([
                "rundll32.exe", "shell32.dll,OpenAs_RunDLL", str(file_path)
            ], check=False)
            return True
        except Exception as e:
            self.logger.error(f"Error opening properties dialog: {e}")
            return False
    
    def show_in_explorer(self, file_path: Path) -> bool:
        """Show file/folder in Windows Explorer"""
        if not self.is_windows:
            return False
        
        try:
            if file_path.is_file():
                subprocess.run([
                    "explorer.exe", "/select,", str(file_path)
                ], check=False)
            else:
                subprocess.run([
                    "explorer.exe", str(file_path)
                ], check=False)
            return True
        except Exception as e:
            self.logger.error(f"Error showing in explorer: {e}")
            return False
    
    def send_to_recycle_bin(self, file_paths: List[Path]) -> bool:
        """Send files to Windows Recycle Bin"""
        if not self.is_windows:
            return False
        
        try:
            import win32file
            import win32con
            
            for file_path in file_paths:
                win32file.SetFileAttributes(str(file_path), win32con.FILE_ATTRIBUTE_NORMAL)
                # Use SHFileOperation to send to recycle bin
                # This is more complex, for now use simple delete
                os.remove(str(file_path)) if file_path.is_file() else os.rmdir(str(file_path))
            
            return True
        except Exception as e:
            self.logger.error(f"Error sending to recycle bin: {e}")
            return False
    
    def get_send_to_options(self) -> List[Dict[str, str]]:
        """Get Send To menu options"""
        if not self.is_windows:
            return []
        
        send_to_options = [
            {"name": "Desktop (create shortcut)", "action": "desktop_shortcut"},
            {"name": "Mail recipient", "action": "mail"},
            {"name": "Compressed (zipped) folder", "action": "zip"},
        ]
        
        # Add removable drives
        try:
            drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" 
                     if os.path.exists(f"{d}:\\")]
            for drive in drives:
                if os.path.getsize(drive) > 0:  # Check if removable
                    send_to_options.append({
                        "name": f"Removable Disk ({drive})",
                        "action": f"copy_to_{drive}"
                    })
        except Exception:
            pass
        
        return send_to_options
    
    def create_shortcut(self, target_path: Path, shortcut_path: Path) -> bool:
        """Create Windows shortcut"""
        if not self.is_windows:
            return False
        
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(target_path)
            shortcut.WorkingDirectory = str(target_path.parent)
            shortcut.save()
            return True
        except Exception as e:
            self.logger.error(f"Error creating shortcut: {e}")
            return False
    
    def open_command_prompt_here(self, folder_path: Path) -> bool:
        """Open Command Prompt in specified folder"""
        if not self.is_windows or not folder_path.is_dir():
            return False
        
        try:
            subprocess.Popen([
                "cmd.exe", "/k", f"cd /d {folder_path}"
            ], cwd=str(folder_path))
            return True
        except Exception as e:
            self.logger.error(f"Error opening command prompt: {e}")
            return False
    
    def open_powershell_here(self, folder_path: Path) -> bool:
        """Open PowerShell in specified folder"""
        if not self.is_windows or not folder_path.is_dir():
            return False
        
        try:
            subprocess.Popen([
                "powershell.exe", "-NoExit", "-Command", f"cd '{folder_path}'"
            ], cwd=str(folder_path))
            return True
        except Exception as e:
            self.logger.error(f"Error opening PowerShell: {e}")
            return False
    
    def copy_path_to_clipboard(self, file_path: Path) -> bool:
        """Copy file path to clipboard"""
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(str(file_path))
            win32clipboard.CloseClipboard()
            return True
        except Exception as e:
            self.logger.error(f"Error copying path to clipboard: {e}")
            return False
    
    def open_with_system(self, file_path: Path) -> bool:
        """Open file with system default application"""
        try:
            if sys.platform == "win32":
                import os
                os.startfile(str(file_path))
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", str(file_path)])
            else:  # Linux and others
                subprocess.run(["xdg-open", str(file_path)])
            return True
        except Exception as e:
            self.logger.error(f"Error opening file: {e}")
            return False
    
    def get_shell_extensions_for_file(self, file_path: Path) -> List[Dict[str, str]]:
        """Get shell context menu extensions for specific file type"""
        if not self.is_windows or not file_path.exists():
            return []
        
        # Use cache key based on file extension or directory
        cache_key = file_path.suffix.lower() if file_path.is_file() else "Directory"
        
        if cache_key in self._shell_extensions_cache:
            return self._shell_extensions_cache[cache_key]
        
        extensions = []
        try:
            # Get file extension
            ext = file_path.suffix.lower() if file_path.is_file() else "Directory"
            
            # Get shell extensions for this file type
            if file_path.is_file():
                extensions.extend(self._get_file_type_shell_extensions(ext))
            else:
                extensions.extend(self._get_directory_shell_extensions())
            
            # Get general shell extensions (work on all files) - limit to 3 for performance
            universal_extensions = self._get_universal_shell_extensions()
            extensions.extend(universal_extensions[:3])
            
            # Cache the result
            self._shell_extensions_cache[cache_key] = extensions
            
        except Exception as e:
            self.logger.debug(f"Error getting shell extensions: {e}")
        
        return extensions
    
    def _get_file_type_shell_extensions(self, ext: str) -> List[Dict[str, str]]:
        """Get shell extensions specific to file type"""
        extensions = []
        
        try:
            # Get the file type from extension
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, ext) as key:
                file_type, _ = winreg.QueryValueEx(key, "")
            
            # Check file type shell extensions
            shell_key_path = f"{file_type}\\shell"
            extensions.extend(self._scan_shell_key(shell_key_path))
            
            # Check extension-specific shell extensions
            ext_shell_path = f"{ext}\\shell"
            extensions.extend(self._scan_shell_key(ext_shell_path))
            
        except Exception as e:
            self.logger.debug(f"Error getting file type shell extensions for {ext}: {e}")
        
        return extensions
    
    def _get_directory_shell_extensions(self) -> List[Dict[str, str]]:
        """Get shell extensions for directories"""
        extensions = []
        
        try:
            # Directory shell extensions
            extensions.extend(self._scan_shell_key("Directory\\shell"))
            extensions.extend(self._scan_shell_key("Folder\\shell"))
            
        except Exception as e:
            self.logger.debug(f"Error getting directory shell extensions: {e}")
        
        return extensions
    
    def _get_universal_shell_extensions(self) -> List[Dict[str, str]]:
        """Get shell extensions that work on all files"""
        extensions = []
        
        try:
            # Universal shell extensions
            extensions.extend(self._scan_shell_key("*\\shell"))
            extensions.extend(self._scan_shell_key("AllFilesystemObjects\\shell"))
            
        except Exception as e:
            self.logger.debug(f"Error getting universal shell extensions: {e}")
        
        return extensions
    
    def _scan_shell_key(self, key_path: str) -> List[Dict[str, str]]:
        """Scan a shell registry key for context menu items"""
        extensions = []
        
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key_path) as shell_key:
                i = 0
                while True:
                    try:
                        # Get shell command name
                        cmd_name = winreg.EnumKey(shell_key, i)
                        
                        # Skip certain system commands to avoid duplicates
                        if cmd_name.lower() in ['open', 'edit', 'print', 'openas', 'runas']:
                            i += 1
                            continue
                        
                        # Get command details
                        cmd_details = self._get_shell_command_details(key_path, cmd_name)
                        if cmd_details:
                            extensions.append(cmd_details)
                        
                        i += 1
                    except WindowsError:
                        break
                        
        except Exception as e:
            self.logger.debug(f"Error scanning shell key {key_path}: {e}")
        
        return extensions
    
    def _get_shell_command_details(self, base_path: str, cmd_name: str) -> Optional[Dict[str, str]]:
        """Get details for a shell command"""
        try:
            cmd_path = f"{base_path}\\{cmd_name}"
            
            # Get display name
            display_name = cmd_name
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, cmd_path) as cmd_key:
                    display_name, _ = winreg.QueryValueEx(cmd_key, "")
            except Exception:
                # Try MUIVerb for localized names
                try:
                    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, cmd_path) as cmd_key:
                        display_name, _ = winreg.QueryValueEx(cmd_key, "MUIVerb")
                except Exception:
                    # Use command name as fallback
                    display_name = cmd_name.replace("_", " ").title()
            
            # Get command executable
            command = None
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{cmd_path}\\command") as command_key:
                    command, _ = winreg.QueryValueEx(command_key, "")
            except Exception:
                pass
            
            if not command:
                return None
            
            # Get icon if available
            icon = None
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, cmd_path) as cmd_key:
                    icon, _ = winreg.QueryValueEx(cmd_key, "Icon")
            except Exception:
                pass
                pass
            
            return {
                "name": display_name,
                "command": command,
                "registry_key": cmd_name,
                "icon": icon,
                "action": f"shell_extension_{cmd_name}"
            }
            
        except Exception as e:
            self.logger.debug(f"Error getting shell command details for {cmd_name}: {e}")
            return None
    
    def execute_shell_extension(self, file_path: Path, command: str) -> bool:
        """Execute a shell extension command"""
        if not self.is_windows:
            return False
        
        try:
            # Replace placeholders in command
            command = command.replace('"%1"', f'"{file_path}"')
            command = command.replace('%1', f'"{file_path}"')
            command = command.replace('"%V"', f'"{file_path.parent}"')
            command = command.replace('%V', f'"{file_path.parent}"')
            
            # Execute command
            subprocess.run(command, shell=True, check=False)
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing shell extension: {e}")
            return False
    
    def get_specialized_app_extensions(self, file_path: Path) -> List[Dict[str, str]]:
        """Get extensions for specialized applications like 7-Zip, WinRAR, etc."""
        extensions = []
        
        # 7-Zip extensions
        if self._is_7zip_installed():
            extensions.extend(self._get_7zip_extensions(file_path))
        
        # WinRAR extensions
        if self._is_winrar_installed():
            extensions.extend(self._get_winrar_extensions(file_path))
        
        # Git extensions (if in a git repository)
        if self._is_git_repository(file_path):
            extensions.extend(self._get_git_extensions(file_path))
            
        # Notepad++ extensions
        if self._is_notepadpp_installed():
            extensions.extend(self._get_notepadpp_extensions(file_path))
            
        # VS Code extensions
        if self._is_vscode_installed():
            extensions.extend(self._get_vscode_extensions(file_path))
            
        # Total Commander extensions
        if self._is_totalcmd_installed():
            extensions.extend(self._get_totalcmd_extensions(file_path))
        
        return extensions
    
    def _is_7zip_installed(self) -> bool:
        """Check if 7-Zip is installed"""
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "7-Zip.001"):
                return True
        except Exception:
            return False
    
    def _get_7zip_extensions(self, file_path: Path) -> List[Dict[str, str]]:
        """Get 7-Zip context menu extensions"""
        extensions = []
        
        if file_path.is_file():
            # Archive operations for files
            extensions.extend([
                {
                    "name": "7-Zip → Add to archive...",
                    "command": f'7z a "{file_path.stem}.7z" "{file_path}"',
                    "registry_key": "7zip_add_archive",
                    "icon": None,
                    "action": "7zip_add_archive"
                },
                {
                    "name": "7-Zip → Add to zip",
                    "command": f'7z a "{file_path.stem}.zip" "{file_path}"',
                    "registry_key": "7zip_add_zip",
                    "icon": None,
                    "action": "7zip_add_zip"
                }
            ])
            
            # Extract operations for archive files
            if file_path.suffix.lower() in ['.zip', '.7z', '.rar', '.tar', '.gz']:
                extensions.extend([
                    {
                        "name": "7-Zip → Extract here",
                        "command": f'7z x "{file_path}" -o"{file_path.parent}"',
                        "registry_key": "7zip_extract_here",
                        "icon": None,
                        "action": "7zip_extract_here"
                    },
                    {
                        "name": "7-Zip → Extract to folder",
                        "command": f'7z x "{file_path}" -o"{file_path.parent}/{file_path.stem}"',
                        "registry_key": "7zip_extract_folder",
                        "icon": None,
                        "action": "7zip_extract_folder"
                    }
                ])
        
        return extensions
    
    def _is_winrar_installed(self) -> bool:
        """Check if WinRAR is installed"""
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "WinRAR"):
                return True
        except Exception:
            return False
    
    def _get_winrar_extensions(self, file_path: Path) -> List[Dict[str, str]]:
        """Get WinRAR context menu extensions"""
        extensions = []
        
        if file_path.is_file():
            # Archive operations for files
            extensions.extend([
                {
                    "name": "WinRAR → Add to archive...",
                    "command": f'winrar a "{file_path.stem}.rar" "{file_path}"',
                    "registry_key": "winrar_add_archive",
                    "icon": None,
                    "action": "winrar_add_archive"
                },
                {
                    "name": "WinRAR → Add to .zip",
                    "command": f'winrar a -afzip "{file_path.stem}.zip" "{file_path}"',
                    "registry_key": "winrar_add_zip",
                    "icon": None,
                    "action": "winrar_add_zip"
                }
            ])
            
            # Extract operations for archive files
            if file_path.suffix.lower() in ['.rar', '.zip', '.7z', '.tar', '.gz']:
                extensions.extend([
                    {
                        "name": "WinRAR → Extract here",
                        "command": f'winrar x "{file_path}"',
                        "registry_key": "winrar_extract_here",
                        "icon": None,
                        "action": "winrar_extract_here"
                    },
                    {
                        "name": "WinRAR → Extract to folder",
                        "command": f'winrar x "{file_path}" "{file_path.parent}/{file_path.stem}\\"',
                        "registry_key": "winrar_extract_folder", 
                        "icon": None,
                        "action": "winrar_extract_folder"
                    }
                ])
        
        return extensions
    
    def _is_notepadpp_installed(self) -> bool:
        """Check if Notepad++ is installed"""
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "Notepad++_file"):
                return True
        except Exception:
            try:
                # Alternative check via registry
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   "SOFTWARE\\Notepad++"):
                    return True
            except Exception:
                return False
    
    def _get_notepadpp_extensions(self, file_path: Path) -> List[Dict[str, str]]:
        """Get Notepad++ context menu extensions"""
        extensions = []
        
        # Only add for text files
        text_extensions = {'.txt', '.log', '.ini', '.cfg', '.conf', '.py', '.js', 
                          '.html', '.css', '.xml', '.json', '.md', '.yml', '.yaml'}
        
        if file_path.is_file() and file_path.suffix.lower() in text_extensions:
            extensions.append({
                "name": "Edit with Notepad++",
                "command": f'notepad++ "{file_path}"',
                "registry_key": "notepadpp_edit",
                "icon": None,
                "action": "notepadpp_edit"
            })
        
        return extensions
    
    def _is_vscode_installed(self) -> bool:
        """Check if Visual Studio Code is installed"""
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "vscode"):
                return True
        except Exception:
            try:
                # Check in program files
                import os
                vscode_paths = [
                    "C:\\Program Files\\Microsoft VS Code\\Code.exe",
                    "C:\\Program Files (x86)\\Microsoft VS Code\\Code.exe",
                    os.path.expanduser("~\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
                ]
                for path in vscode_paths:
                    if os.path.exists(path):
                        return True
                return False
            except Exception:
                return False
    
    def _get_vscode_extensions(self, file_path: Path) -> List[Dict[str, str]]:
        """Get Visual Studio Code context menu extensions"""
        extensions = []
        
        if file_path.is_file():
            extensions.append({
                "name": "Open with Code",
                "command": f'code "{file_path}"',
                "registry_key": "vscode_open",
                "icon": None,
                "action": "vscode_open"
            })
        elif file_path.is_dir():
            extensions.append({
                "name": "Open with Code",
                "command": f'code "{file_path}"',
                "registry_key": "vscode_open_folder",
                "icon": None,
                "action": "vscode_open_folder"
            })
        
        return extensions
    
    def _is_totalcmd_installed(self) -> bool:
        """Check if Total Commander is installed"""
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "TOTALCMD"):
                return True
        except Exception:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                   "SOFTWARE\\Ghisler\\Total Commander"):
                    return True
            except Exception:
                return False
    
    def _get_totalcmd_extensions(self, file_path: Path) -> List[Dict[str, str]]:
        """Get Total Commander context menu extensions"""
        extensions = []
        
        if file_path.is_dir():
            extensions.append({
                "name": "Open in Total Commander",
                "command": f'totalcmd.exe /O /T "{file_path}"',
                "registry_key": "totalcmd_open",
                "icon": None,
                "action": "totalcmd_open"
            })
        
        return extensions
    
    def _is_git_repository(self, file_path: Path) -> bool:
        """Check if file is in a Git repository"""
        try:
            current_path = file_path if file_path.is_dir() else file_path.parent
            while current_path != current_path.parent:
                if (current_path / ".git").exists():
                    return True
                current_path = current_path.parent
            return False
        except Exception:
            return False
    
    def _get_git_extensions(self, file_path: Path) -> List[Dict[str, str]]:
        """Get Git context menu extensions"""
        extensions = []
        
        # Common Git operations
        extensions.extend([
            {
                "name": "Git → Commit changes",
                "command": f'git add "{file_path}" && git commit',
                "registry_key": "git_commit",
                "icon": None,
                "action": "git_commit"
            },
            {
                "name": "Git → Show log",
                "command": f'git log --follow "{file_path}"',
                "registry_key": "git_log",
                "icon": None,
                "action": "git_log"
            }
        ])
        
        return extensions
    
    def get_common_app_extensions(self) -> List[Dict[str, str]]:
        """Get common application extensions that might not be in registry"""
        if self._common_extensions_cache is not None:
            return self._common_extensions_cache
        
        common_apps = []
        
        # Check for common applications with more sophisticated detection
        app_checks = [
            {
                "name": "Open with Visual Studio Code",
                "executable": "code",
                "command": 'code "{}"',
                "icon": None,
                "check_paths": [
                    "C:\\Program Files\\Microsoft VS Code\\Code.exe",
                    "C:\\Program Files (x86)\\Microsoft VS Code\\Code.exe",
                    "%LOCALAPPDATA%\\Programs\\Microsoft VS Code\\Code.exe"
                ]
            },
            {
                "name": "Open with Notepad++",
                "executable": "notepad++", 
                "command": 'notepad++ "{}"',
                "icon": None,
                "check_paths": [
                    "C:\\Program Files\\Notepad++\\notepad++.exe",
                    "C:\\Program Files (x86)\\Notepad++\\notepad++.exe"
                ]
            },
            {
                "name": "Open Command Prompt here",
                "executable": "cmd",
                "command": 'cmd.exe /k "cd /d {}"',
                "icon": None,
                "check_paths": ["%SYSTEMROOT%\\System32\\cmd.exe"]
            },
            {
                "name": "Open PowerShell here",
                "executable": "powershell",
                "command": 'powershell.exe -NoExit -Command "Set-Location \\"{}\\\""',
                "icon": None,
                "check_paths": [
                    "%SYSTEMROOT%\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
                ]
            }
        ]
        
        for app in app_checks:
            if self._is_application_available(app):
                common_apps.append({
                    "name": app["name"],
                    "command": app["command"],
                    "registry_key": f"common_{app['executable']}",
                    "icon": app["icon"],
                    "action": f"common_app_{app['executable'].replace('.', '_')}"
                })
        
        # Cache the result
        self._common_extensions_cache = common_apps
        return common_apps
    
    def _is_application_available(self, app_info: Dict) -> bool:
        """Check if an application is available using multiple methods"""
        cache_key = app_info["executable"]
        
        if cache_key in self._app_availability_cache:
            return self._app_availability_cache[cache_key]
        
        import os
        available = False
        
        # Check specific paths first (faster than PATH check)
        for path in app_info.get("check_paths", []):
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path):
                available = True
                break
        
        if not available:
            # Try PATH as fallback (with timeout)
            try:
                subprocess.run([app_info["executable"], "--version"], 
                             capture_output=True, check=False, timeout=1)
                available = True
            except Exception:
                try:
                    subprocess.run([app_info["executable"]], 
                                 capture_output=True, check=False, timeout=0.5)
                    available = True
                except Exception:
                    available = False
        
        # Cache the result
        self._app_availability_cache[cache_key] = available
        return available
    
    def _is_executable_available(self, executable: str) -> bool:
        """Check if an executable is available in PATH (legacy method)"""
        try:
            subprocess.run([executable, "--version"], 
                         capture_output=True, check=False, timeout=2)
            return True
        except Exception:
            try:
                # Try without --version flag
                subprocess.run([executable], 
                             capture_output=True, check=False, timeout=1)
                return True
            except Exception:
                return False
    
    def get_context_menu_actions(self, file_paths: List[Path]) -> List[Dict[str, any]]:
        """Get Windows Explorer-style context menu actions including third-party extensions"""
        if not file_paths:
            return []
        
        is_single = len(file_paths) == 1
        file_path = file_paths[0] if is_single else None
        
        actions = []
        
        # Get shell extensions for the file(s)
        shell_extensions = []
        if is_single and file_path:
            shell_extensions = self.get_shell_extensions_for_file(file_path)
        
        # Add specialized app extensions
        specialized_extensions = []
        if is_single and file_path:
            specialized_extensions = self.get_specialized_app_extensions(file_path)
        
        # Add common app extensions
        common_extensions = self.get_common_app_extensions()
        
        # Combine all extensions
        all_extensions = shell_extensions + specialized_extensions + common_extensions
        
        # Open actions (single file/folder only)
        if is_single:
            if file_path.is_dir():
                actions.append({
                    "text": "Open",
                    "icon": "folder_open",
                    "action": "open",
                    "bold": True
                })
                actions.append({
                    "text": "Open in new tab",
                    "icon": "tab_new",
                    "action": "open_new_tab"
                })
            else:
                default_program = self.get_default_program(file_path)
                if default_program:
                    actions.append({
                        "text": f"Open with {default_program}",
                        "icon": "file_open",
                        "action": "open_default",
                        "bold": True
                    })
                else:
                    actions.append({
                        "text": "Open",
                        "icon": "file_open", 
                        "action": "open_default",
                        "bold": True
                    })
                actions.append({
                    "text": "Open in new tab",
                    "icon": "tab_new",
                    "action": "open_new_tab"
                })
            
            # Open with submenu
            open_with_programs = self.get_open_with_programs(file_path)
            if open_with_programs:
                actions.append({
                    "text": "Open with",
                    "icon": "open_with",
                    "submenu": open_with_programs,
                    "action": "open_with_submenu"
                })
            
            actions.append({"separator": True})
        
        # Send to (Windows specific)
        send_to_options = self.get_send_to_options()
        if send_to_options:
            actions.append({
                "text": "Send to",
                "icon": "send_to",
                "submenu": send_to_options,
                "action": "send_to_submenu"
            })
        
        # Cut, Copy, Paste
        actions.extend([
            {"separator": True},
            {
                "text": "Cut",
                "icon": "cut",
                "action": "cut",
                "shortcut": "Ctrl+X"
            },
            {
                "text": "Copy",
                "icon": "copy", 
                "action": "copy",
                "shortcut": "Ctrl+C"
            }
        ])
        
        # Create shortcut
        if is_single:
            actions.append({
                "text": "Create shortcut",
                "icon": "shortcut",
                "action": "create_shortcut"
            })
        
        # Delete
        actions.extend([
            {"separator": True},
            {
                "text": "Delete",
                "icon": "delete",
                "action": "delete",
                "shortcut": "Del"
            }
        ])
        
        # Rename (single item only)
        if is_single:
            actions.append({
                "text": "Rename",
                "icon": "rename",
                "action": "rename",
                "shortcut": "F2"
            })
        
        actions.append({"separator": True})
        
        # Add shell extensions from installed applications
        if all_extensions:
            for ext in all_extensions:
                actions.append({
                    "text": ext["name"],
                    "icon": "app_extension",
                    "action": ext["action"],
                    "command": ext["command"]
                })
            actions.append({"separator": True})
        
        # Properties
        actions.append({
            "text": "Properties",
            "icon": "properties",
            "action": "properties",
            "shortcut": "Alt+Enter"
        })
        
        return actions
    
    def get_empty_area_context_menu(self) -> List[Dict[str, any]]:
        """Get context menu for empty area (like Windows Explorer)"""
        actions = [
            {
                "text": "View",
                "icon": "view",
                "submenu": [
                    {"text": "Extra large icons", "action": "view_extra_large"},
                    {"text": "Large icons", "action": "view_large"},
                    {"text": "Medium icons", "action": "view_medium"},
                    {"text": "Small icons", "action": "view_small"},
                    {"separator": True},
                    {"text": "List", "action": "view_list"},
                    {"text": "Details", "action": "view_details"},
                    {"text": "Tiles", "action": "view_tiles"},
                    {"text": "Content", "action": "view_content"},
                ]
            },
            {
                "text": "Sort by",
                "icon": "sort",
                "submenu": [
                    {"text": "Name", "action": "sort_name"},
                    {"text": "Date modified", "action": "sort_date"},
                    {"text": "Type", "action": "sort_type"},
                    {"text": "Size", "action": "sort_size"},
                    {"separator": True},
                    {"text": "Ascending", "action": "sort_asc", "checkable": True},
                    {"text": "Descending", "action": "sort_desc", "checkable": True},
                ]
            },
            {
                "text": "Refresh",
                "icon": "refresh",
                "action": "refresh",
                "shortcut": "F5"
            },
            {"separator": True},
            {
                "text": "Paste",
                "icon": "paste",
                "action": "paste",
                "shortcut": "Ctrl+V"
            },
            {
                "text": "Paste shortcut",
                "icon": "paste_shortcut", 
                "action": "paste_shortcut"
            },
            {"separator": True},
            {
                "text": "New",
                "icon": "new",
                "submenu": [
                    {"text": "Folder", "action": "new_folder", "icon": "folder"},
                    {"separator": True},
                    {"text": "Text Document", "action": "new_text", "icon": "text"},
                    {"text": "Bitmap Image", "action": "new_bitmap", "icon": "image"},
                    {"text": "Rich Text Document", "action": "new_rtf", "icon": "rtf"},
                ]
            },
            {"separator": True},
            {
                "text": "Display settings",
                "icon": "display",
                "action": "display_settings"
            },
            {
                "text": "Personalize",
                "icon": "personalize",
                "action": "personalize"
            },
            {"separator": True},
            {
                "text": "Open Command Prompt here",
                "icon": "cmd",
                "action": "open_cmd"
            },
            {
                "text": "Open PowerShell here", 
                "icon": "powershell",
                "action": "open_powershell"
            }
        ]
        
        return actions