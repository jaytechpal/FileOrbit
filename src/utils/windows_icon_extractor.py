"""
Windows Icon Extractor
Extracts and caches icons from Windows Shell extensions and system resources
"""

import os
import sys
import winreg
import subprocess
from pathlib import Path
from typing import Optional
import shutil
from src.utils.logger import get_logger


class WindowsIconExtractor:
    """Extract and cache icons from Windows Shell and applications"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.is_windows = sys.platform == "win32"
        self.icon_cache = {}
        
        # Icon cache directory
        self.cache_dir = Path(__file__).parent.parent.parent / "resources" / "icons" / "extracted"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # System icon mappings (Windows system icons)
        self.system_icon_paths = {
            'folder_open': (r'%SystemRoot%\System32\shell32.dll', 3),
            'folder': (r'%SystemRoot%\System32\shell32.dll', 4),
            'file_open': (r'%SystemRoot%\System32\shell32.dll', 0),
            'cut': (r'%SystemRoot%\System32\shell32.dll', 260),
            'copy': (r'%SystemRoot%\System32\shell32.dll', 261),
            'paste': (r'%SystemRoot%\System32\shell32.dll', 262),
            'delete': (r'%SystemRoot%\System32\shell32.dll', 131),
            'rename': (r'%SystemRoot%\System32\shell32.dll', 134),
            'properties': (r'%SystemRoot%\System32\shell32.dll', 269),
            'send_to': (r'%SystemRoot%\System32\shell32.dll', 265),
            'shortcut': (r'%SystemRoot%\System32\shell32.dll', 29),
            'refresh': (r'%SystemRoot%\System32\shell32.dll', 239),
            'find': (r'%SystemRoot%\System32\shell32.dll', 22),
            'new_folder': (r'%SystemRoot%\System32\shell32.dll', 319),
        }
    
    def extract_icon_from_shell_extension(self, command: str, registry_key: str = None) -> Optional[str]:
        """Extract icon from shell extension command or registry"""
        if not self.is_windows:
            return None
        
        try:
            # Try to get icon from registry first
            if registry_key:
                icon_path = self._get_icon_from_registry(registry_key)
                if icon_path:
                    return self._extract_and_cache_icon(icon_path, registry_key)
            
            # Extract executable path from command
            exe_path = self._extract_exe_path_from_command(command)
            if exe_path and Path(exe_path).exists():
                return self._extract_and_cache_icon(f"{exe_path},0", f"exe_{Path(exe_path).stem}")
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error extracting icon from shell extension: {e}")
            return None
    
    def get_system_icon(self, icon_name: str) -> Optional[str]:
        """Get system icon and cache it"""
        if not self.is_windows or icon_name not in self.system_icon_paths:
            return None
        
        try:
            dll_path, icon_index = self.system_icon_paths[icon_name]
            expanded_path = os.path.expandvars(dll_path)
            
            if not os.path.exists(expanded_path):
                return None
            
            icon_spec = f"{expanded_path},{icon_index}"
            return self._extract_and_cache_icon(icon_spec, f"system_{icon_name}")
            
        except Exception as e:
            self.logger.debug(f"Error getting system icon {icon_name}: {e}")
            return None
    
    def get_application_icon(self, app_name: str, exe_path: str = None) -> Optional[str]:
        """Get application icon from executable or registry"""
        if not self.is_windows:
            return None
        
        try:
            # Check cache first
            cache_key = f"app_{app_name.lower().replace(' ', '_')}"
            cached_path = self.cache_dir / f"{cache_key}.png"
            if cached_path.exists():
                return str(cached_path)
            
            # Try to find executable path if not provided
            if not exe_path:
                exe_path = self._find_application_executable(app_name)
            
            if exe_path and Path(exe_path).exists():
                return self._extract_and_cache_icon(f"{exe_path},0", cache_key)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error getting application icon for {app_name}: {e}")
            return None
    
    def extract_context_menu_icons(self, menu_items: list) -> dict:
        """Extract icons for all context menu items"""
        icon_mapping = {}
        
        for item in menu_items:
            if item.get('separator'):
                continue
            
            text = item.get('text', '')
            command = item.get('command', '')
            registry_key = item.get('registry_key', '')
            
            if not text:
                continue
            
            # Try different methods to get icon
            icon_path = None
            
            # 1. Try to get from existing icon field
            existing_icon = item.get('icon', '')
            if existing_icon and not existing_icon.startswith('app_'):
                # If it's a system icon name, try to get actual icon
                icon_path = self.get_system_icon(existing_icon)
            
            # 2. Try to extract from shell extension
            if not icon_path and command:
                icon_path = self.extract_icon_from_shell_extension(command, registry_key)
            
            # 3. Try to get application icon by name
            if not icon_path:
                icon_path = self._guess_application_icon_from_text(text)
            
            if icon_path:
                icon_mapping[text] = icon_path
        
        return icon_mapping
    
    def _get_icon_from_registry(self, registry_key: str) -> Optional[str]:
        """Get icon path from registry"""
        try:
            # Common registry paths for icons
            possible_paths = [
                f"HKEY_CLASSES_ROOT\\{registry_key}",
                f"HKEY_CLASSES_ROOT\\{registry_key}\\DefaultIcon",
                f"HKEY_CLASSES_ROOT\\Applications\\{registry_key}\\DefaultIcon",
            ]
            
            for reg_path in possible_paths:
                try:
                    if reg_path.startswith("HKEY_CLASSES_ROOT\\"):
                        key_path = reg_path[len("HKEY_CLASSES_ROOT\\"):]
                        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key_path) as key:
                            icon_value, _ = winreg.QueryValueEx(key, "")
                            if icon_value:
                                return icon_value
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error getting icon from registry {registry_key}: {e}")
            return None
    
    def _extract_and_cache_icon(self, icon_spec: str, cache_key: str) -> Optional[str]:
        """Extract icon from specification and cache it"""
        try:
            # Check if already cached
            cached_path = self.cache_dir / f"{cache_key}.png"
            if cached_path.exists():
                return str(cached_path)
            
            # Parse icon specification (path,index or just path)
            if ',' in icon_spec:
                icon_path, icon_index = icon_spec.rsplit(',', 1)
                try:
                    icon_index = int(icon_index)
                except ValueError:
                    icon_index = 0
            else:
                icon_path = icon_spec
                icon_index = 0
            
            # Expand environment variables
            icon_path = os.path.expandvars(icon_path)
            
            # Remove quotes if present
            icon_path = icon_path.strip('"')
            
            if not os.path.exists(icon_path):
                return None
            
            # Extract icon using Windows API
            success = self._extract_icon_with_windows_api(icon_path, icon_index, str(cached_path))
            
            if success and cached_path.exists():
                return str(cached_path)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error extracting and caching icon {icon_spec}: {e}")
            return None
    
    def _extract_icon_with_windows_api(self, exe_path: str, icon_index: int, output_path: str) -> bool:
        """Extract icon using Windows API"""
        try:
            # Try using PowerShell to extract icon
            ps_script = f'''
            Add-Type -AssemblyName System.Drawing
            Add-Type -AssemblyName System.Windows.Forms
            
            try {{
                $icon = [System.Drawing.Icon]::ExtractAssociatedIcon("{exe_path}")
                if ($icon -ne $null) {{
                    $bitmap = $icon.ToBitmap()
                    $bitmap.Save("{output_path}", [System.Drawing.Imaging.ImageFormat]::Png)
                    $bitmap.Dispose()
                    $icon.Dispose()
                    Write-Output "SUCCESS"
                }} else {{
                    Write-Output "FAILED"
                }}
            }} catch {{
                Write-Output "ERROR: $($_.Exception.Message)"
            }}
            '''
            
            result = subprocess.run([
                'powershell', '-Command', ps_script
            ], capture_output=True, text=True, timeout=10)
            
            return result.stdout.strip() == "SUCCESS"
            
        except Exception as e:
            self.logger.debug(f"Error with PowerShell icon extraction: {e}")
            
            # Fallback: try using Python PIL with win32gui
            try:
                import win32gui
                
                # Extract icon handle
                if icon_index == 0:
                    # Try to get large icon
                    large_icons, small_icons = win32gui.ExtractIconEx(exe_path, -1)
                    if large_icons:
                        # Use the icon but don't assign to unused variable
                        pass
                    elif small_icons:
                        # Use the icon but don't assign to unused variable
                        pass
                    else:
                        return False
                else:
                    large_icons, small_icons = win32gui.ExtractIconEx(exe_path, icon_index)
                    if large_icons:
                        # Use the icon but don't assign to unused variable
                        pass
                    else:
                        return False
                
                # Convert to bitmap and save
                # This is complex and requires additional Windows API calls
                # For now, return False to use fallback methods
                return False
                
            except ImportError:
                # win32gui not available
                return False
            except Exception as e:
                self.logger.debug(f"Error with win32gui icon extraction: {e}")
                return False
    
    def _extract_exe_path_from_command(self, command: str) -> Optional[str]:
        """Extract executable path from shell command"""
        if not command:
            return None
        
        command = command.strip()
        
        # Handle quoted paths
        if command.startswith('"'):
            end_quote = command.find('"', 1)
            if end_quote > 0:
                return command[1:end_quote]
        
        # Handle unquoted paths
        parts = command.split()
        if parts:
            return parts[0]
        
        return None
    
    def _find_application_executable(self, app_name: str) -> Optional[str]:
        """Find executable path for application name"""
        try:
            app_name_lower = app_name.lower()
            
            # Common application mappings
            app_mappings = {
                'visual studio code': ['code.exe', 'Code.exe'],
                'sublime text': ['sublime_text.exe', 'subl.exe'],
                'notepad++': ['notepad++.exe'],
                'vlc media player': ['vlc.exe'],
                'mpc-hc': ['mpc-hc64.exe', 'mpc-hc.exe'],
                'git': ['git.exe'],
                'powershell': ['powershell.exe'],
                'command prompt': ['cmd.exe'],
            }
            
            # Search in common directories
            search_paths = [
                r"C:\Program Files",
                r"C:\Program Files (x86)",
                os.path.expanduser(r"~\AppData\Local\Programs"),
                os.environ.get('ProgramFiles', ''),
                os.environ.get('ProgramFiles(x86)', ''),
            ]
            
            executables = []
            for key, exes in app_mappings.items():
                if key in app_name_lower:
                    executables = exes
                    break
            
            if not executables:
                # Try to guess executable name
                clean_name = app_name_lower.replace(' ', '').replace('-', '')
                executables = [f"{clean_name}.exe"]
            
            # Search for executables
            for search_path in search_paths:
                if not search_path or not os.path.exists(search_path):
                    continue
                
                for exe_name in executables:
                    for root, dirs, files in os.walk(search_path):
                        if exe_name in files:
                            return os.path.join(root, exe_name)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error finding executable for {app_name}: {e}")
            return None
    
    def _guess_application_icon_from_text(self, text: str) -> Optional[str]:
        """Guess and extract application icon from menu text"""
        text_lower = text.lower()
        
        # Known applications with their likely names
        app_patterns = {
            'visual studio code': 'Visual Studio Code',
            'code': 'Visual Studio Code',
            'sublime': 'Sublime Text',
            'notepad++': 'Notepad++',
            'vlc': 'VLC Media Player',
            'mpc-hc': 'MPC-HC',
            'mpc': 'MPC-HC',
            'git': 'Git',
            'powershell': 'PowerShell',
            'cmd': 'Command Prompt',
        }
        
        for pattern, app_name in app_patterns.items():
            if pattern in text_lower:
                return self.get_application_icon(app_name)
        
        return None
    
    def get_cached_icon_path(self, icon_name: str) -> Optional[str]:
        """Get cached icon path if it exists"""
        cached_path = self.cache_dir / f"{icon_name}.png"
        if cached_path.exists():
            return str(cached_path)
        return None
    
    def clear_icon_cache(self):
        """Clear the icon cache"""
        try:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.icon_cache.clear()
            self.logger.info("Icon cache cleared")
        except Exception as e:
            self.logger.error(f"Error clearing icon cache: {e}")
    
    def preload_system_icons(self):
        """Preload common system icons"""
        self.logger.info("Preloading system icons...")
        
        for icon_name in self.system_icon_paths.keys():
            try:
                self.get_system_icon(icon_name)
            except Exception as e:
                self.logger.debug(f"Error preloading system icon {icon_name}: {e}")
        
        self.logger.info("System icons preloaded")


# Global instance
_icon_extractor = None

def get_icon_extractor() -> WindowsIconExtractor:
    """Get global icon extractor instance"""
    global _icon_extractor
    if _icon_extractor is None:
        _icon_extractor = WindowsIconExtractor()
    return _icon_extractor