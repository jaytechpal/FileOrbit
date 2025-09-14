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
            
            # Remove duplicates based on text (keep first occurrence)
            seen_texts = set()
            unique_extensions = []
            for ext_item in extensions:
                text = ext_item.get("text", "").strip()
                # Skip if we've seen this exact text before
                if text and text not in seen_texts:
                    seen_texts.add(text)
                    unique_extensions.append(ext_item)
                elif not text:  # Keep items without text
                    unique_extensions.append(ext_item)
            
            extensions = unique_extensions
            
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
            
            # Filter out system resource references
            if self._is_system_resource_reference(display_name):
                # Try to resolve or skip if it's a system reference
                display_name = self._resolve_system_resource(display_name) or cmd_name.replace("_", " ").title()
            
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
                # If no icon in command key, try to extract from executable
                if command:
                    exe_path = self._extract_exe_path_from_command(command)
                    if exe_path and os.path.exists(exe_path):
                        icon = f"{exe_path},0"  # Default icon index
            
            return {
                "name": display_name,
                "text": display_name,  # Add text field for consistency
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
                    "text": app["name"],  # Add text field for consistency
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
        
        # Advanced deduplication - handle text variations and normalize
        seen_items = set()
        unique_extensions = []
        
        for ext in all_extensions:
            text = ext.get("text", "").strip()
            command = ext.get("command", "").strip()
            
            if not text:  # Skip items without text
                continue
            
            # Filter out unwanted entries that don't appear in Windows Explorer
            if self._should_filter_out_entry(text, command):
                continue
                
            # Normalize text for comparison (remove &, extra spaces, case)
            normalized_text = text.replace("&", "").replace("  ", " ").strip().lower()
            
            # Create multiple comparison keys for better duplicate detection
            keys_to_check = [
                normalized_text,  # Basic normalized text
                normalized_text.replace("with ", ""),  # Remove "with"
                normalized_text.replace("open ", ""),  # Remove "open"
                normalized_text.replace("visual studio ", ""),  # Handle VS Code variations
            ]
            
            # Special handling for common variations
            if "visual studio code" in normalized_text or "code" in normalized_text:
                keys_to_check.extend([
                    "code",
                    "visual studio code",
                    "open with code",
                    "open with visual studio code"
                ])
            
            # Check if any of the keys have been seen
            is_duplicate = False
            for key in keys_to_check:
                if key in seen_items:
                    is_duplicate = True
                    break
            
            # Also check for command-based duplicates (same executable)
            if command:
                exe_path = self._extract_exe_path_from_command(command)
                if exe_path:
                    exe_key = f"exe:{exe_path.lower()}"
                    if exe_key in seen_items:
                        is_duplicate = True
                    else:
                        seen_items.add(exe_key)
            
            if not is_duplicate:
                # Add all normalized keys to seen set
                for key in keys_to_check:
                    if key:  # Only add non-empty keys
                        seen_items.add(key)
                unique_extensions.append(ext)
        
        all_extensions = unique_extensions
        
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
                    
            # Add Open With submenu for files
            open_with_programs = self.get_open_with_programs(file_path)
            if open_with_programs:
                actions.append({
                    "text": "Open with",
                    "icon": "open_with",
                    "submenu": open_with_programs
                })
                
            # Add shell extensions right after Open actions (like Windows Explorer)
            # Filter to only show the most relevant ones in top level
            priority_extensions = []
            for ext in all_extensions:
                text = ext.get("text", "").lower()
                # Only add high-priority extensions to top level
                if any(priority_text in text for priority_text in [
                    "git gui", "git bash", "open with code", "open with sublime", 
                    "open powershell", "cmd", "command prompt"
                ]):
                    priority_extensions.append(ext)
            
            # Add priority extensions
            for ext in priority_extensions:
                action_def = {
                    "text": ext.get("text", ext.get("name", "Unknown")),
                    "action": ext.get("action", "shell_extension"),
                    "command": ext.get("command", "")
                }
                
                # Only set icon for certain applications, let others be auto-detected
                text_lower = ext.get("text", "").lower()
                if "git" in text_lower:
                    action_def["icon"] = "git"
                elif "vlc" in text_lower:
                    action_def["icon"] = "vlc"
                elif "mpc" in text_lower:
                    action_def["icon"] = "mpc"
                # For Sublime and PowerShell, don't set icon - let file panel guess
                # This ensures they use the working icon resolution path
                
                actions.append(action_def)
                    
            # Add separator
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
        
        # Add shell extensions from installed applications (exclude priority ones already shown)
        if all_extensions:
            priority_texts = ["git gui", "git bash", "open with code", "open with sublime", 
                            "open powershell", "cmd", "command prompt"]
            
            remaining_extensions = []
            for ext in all_extensions:
                text = ext.get("text", "").lower()
                # Skip extensions we already showed at the top
                if not any(priority_text in text for priority_text in priority_texts):
                    remaining_extensions.append(ext)
            
            if remaining_extensions:
                for ext in remaining_extensions:
                    actions.append({
                        "text": ext.get("text", ext.get("name", "Unknown")),
                        "icon": self._guess_icon_from_text(ext.get("text", "")),
                        "action": ext.get("action", "shell_extension"),
                        "command": ext.get("command", "")
                    })
                actions.append({"separator": True})
        
        # Properties
        actions.append({
            "text": "Properties",
            "icon": "properties",
            "action": "properties",
            "shortcut": "Alt+Enter"
        })
        
        # Sort and prioritize like Windows Explorer
        actions = self._prioritize_like_windows_explorer(actions)
        
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
    
    def _extract_exe_path_from_command(self, command: str) -> str:
        """Extract executable path from shell command"""
        if not command:
            return ""
        
        command = command.strip()
        if command.startswith('"'):
            # Find the closing quote
            end_quote = command.find('"', 1)
            if end_quote > 0:
                return command[1:end_quote]
        else:
            # Take the first part before any space
            parts = command.split(' ')
            return parts[0] if parts else ""
        
        return ""
    
    def _is_system_resource_reference(self, text: str) -> bool:
        """Check if text is a system resource reference like @shell32.dll,-8506"""
        if not text:
            return False
        return text.startswith('@') and ('.dll,' in text or '.exe,' in text)
    
    def _resolve_system_resource(self, resource_ref: str) -> str:
        """Resolve system resource reference to actual text"""
        try:
            # Common system resource mappings
            resource_mappings = {
                '@shell32.dll,-8506': 'Find',
                '@shell32.dll,-8508': 'Find',
                '@wsl.exe,-2': '',  # Skip WSL entries completely
                '@shell32.dll,-30315': 'Send to',
                '@shell32.dll,-31374': 'Copy',
                '@shell32.dll,-31375': 'Cut',
                # Add more system resources that should be filtered
                '@shell32.dll,-10210': '',  # Skip
                '@shell32.dll,-10211': '',  # Skip
                '@shell32.dll,-31233': '',  # Skip
            }
            
            # Check for direct mapping
            if resource_ref in resource_mappings:
                return resource_mappings[resource_ref]
            
            # If no mapping found, return empty to skip this item
            return ''
            
        except Exception:
            return ''
    
    def _should_filter_out_entry(self, text: str, command: str) -> bool:
        """Filter out entries that don't appear in Windows Explorer context menu"""
        if not text:
            return True
            
        text_lower = text.lower()
        command_lower = command.lower() if command else ""
        
        # Filter out WSL entries
        if 'wsl' in text_lower or 'wsl.exe' in command_lower:
            return True
            
        # Filter out Windows Subsystem entries
        if 'windows subsystem' in text_lower:
            return True
            
        # Filter out Microsoft Store entries that don't appear in Explorer
        if 'microsoft store' in text_lower:
            return True
            
        # Filter out some development tools that clutter the menu
        if any(term in text_lower for term in ['debugger', 'profiler', 'analyzer']):
            return True
            
        # Filter out system internal commands
        if text_lower.startswith('@') or text_lower.startswith('ms-'):
            return True
            
        # Filter out empty or very short entries
        if len(text.strip()) < 2:
            return True
            
        return False
    
    def _prioritize_like_windows_explorer(self, actions: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """Sort and prioritize context menu actions like Windows Explorer"""
        
        # Define priority order (lower numbers = higher priority)
        priority_map = {
            # Core Windows Explorer actions first (exactly like Windows)
            "open": 1,
            "open_with": 2,
            
            # Git operations (appear early in Windows Explorer)
            "git": 10,
            "open git gui here": 11,
            "open git bash here": 12,
            
            # Text editors
            "open with code": 20,
            "open with sublime text": 21,
            "open powershell here": 22,
            
            # First separator after open/edit actions
            "separator_1": 50,
            
            # File operations (Windows Explorer order)
            "cut": 100,
            "copy": 101,
            "create shortcut": 102,
            "delete": 103,
            "rename": 104,
            
            # Second separator after basic file operations  
            "separator_2": 150,
            
            # Third-party media applications
            "add to vlc media player's playlist": 200,
            "find": 201,
            "send to": 202,
            "add to mpc-hc playlist": 203,
            
            # Final separator before properties
            "separator_3": 800,
            
            # System actions last (like Windows Explorer)
            "properties": 900,
        }
        
        def get_action_priority(action):
            """Get priority for an action"""
            if action.get("separator"):
                # Count separators to assign them properly
                return 50 + (len([a for a in actions[:actions.index(action)] if a.get("separator")]) * 200)
                
            text = action.get("text", "").lower()
            action_type = action.get("action", "").lower()
            
            # Check for exact text matches first
            if text in priority_map:
                return priority_map[text]
                
            # Check for exact action matches
            if action_type in priority_map:
                return priority_map[action_type]
                
            # Check text for known patterns
            for keyword, priority in priority_map.items():
                if keyword in text and keyword != "separator":
                    return priority
                    
            # Default priority for unknown actions (put in middle)
            return 400
            
        # Sort by priority
        sorted_actions = sorted(actions, key=get_action_priority)
        
        return sorted_actions
    
    def _guess_icon_from_text(self, text: str) -> str:
        """Guess appropriate icon name from extension text"""
        if not text:
            return "app_extension"
            
        text_lower = text.lower()
        
        # Git operations
        if "git" in text_lower:
            return "git"
        
        # Code editors
        if "code" in text_lower or "visual studio" in text_lower:
            return "code"
        
        # Sublime Text specifically
        if "sublime" in text_lower:
            return "editor"
        
        # PowerShell/Command Prompt  
        if "powershell" in text_lower:
            return "powershell"
        elif "cmd" in text_lower or "command prompt" in text_lower:
            return "cmd"
        
        # VLC Media Player
        if "vlc" in text_lower:
            return "vlc"
            
        # MPC-HC
        if "mpc" in text_lower:
            return "mpc"
        
        # Default fallback
        return "app_extension"