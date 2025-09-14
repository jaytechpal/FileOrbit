"""
Application Detector - Detects installed applications and their capabilities
"""

import os
import subprocess
from typing import Dict, Optional
from src.utils.logger import get_logger
from src.config.constants import PathConstants, ShellConstants
from src.utils.error_handling import safe_execute
from src.services.universal_registry_discovery import UniversalRegistryDiscovery


class ApplicationDetector:
    """Detects and analyzes installed applications"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._app_cache = {}
        self._availability_cache = {}
        self.universal_discovery = UniversalRegistryDiscovery()
    
    @safe_execute
    def detect_available_applications(self) -> Dict[str, str]:
        """Detect which applications are available on the system"""
        if self._availability_cache:
            return self._availability_cache
        
        # Use universal discovery for comprehensive detection
        discovered_apps = self.universal_discovery.discover_all_installed_applications()
        
        # Convert to the expected format (app_name -> path)
        available_apps = {}
        for app_name, app_info in discovered_apps.items():
            if app_info.get("exists", False) and app_info.get("executable_path"):
                available_apps[app_name] = app_info["executable_path"]
        
        # Fallback to legacy detection for any missing apps
        legacy_apps = self._legacy_detect_available_applications()
        for app_name, path in legacy_apps.items():
            if app_name not in available_apps:
                available_apps[app_name] = path
        
        self._availability_cache = available_apps
        return available_apps
    
    def _legacy_detect_available_applications(self) -> Dict[str, str]:
        """Legacy detection method as fallback"""
        available_apps = {}
        
        # Check if any of the old hardcoded paths still exist
        legacy_paths = {
            "vlc": [
                r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
            ],
            "git": [
                r"C:\Program Files\Git\cmd\git-gui.exe",
                r"C:\Program Files (x86)\Git\cmd\git-gui.exe",
            ],
            "mpc": [
                r"C:\Program Files\MPC-HC\mpc-hc64.exe",
                r"C:\Program Files (x86)\MPC-HC\mpc-hc.exe",
            ],
            "code": [
                r"C:\Program Files\Microsoft VS Code\Code.exe",
                r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
                r"C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            ],
            "sublime": [
                r"C:\Program Files\Sublime Text\sublime_text.exe",
                r"C:\Program Files (x86)\Sublime Text\sublime_text.exe",
            ],
            "powershell": [
                r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
                r"C:\Program Files\PowerShell\7\pwsh.exe",
                r"C:\Program Files (x86)\PowerShell\7\pwsh.exe",
            ],
        }
        
        for app_name, paths in legacy_paths.items():
            for path_template in paths:
                # Handle username placeholder
                if "{username}" in path_template:
                    username = os.environ.get("USERNAME", "")
                    path = path_template.format(username=username)
                else:
                    path = path_template
                
                if os.path.exists(path):
                    available_apps[app_name] = path
                    self.logger.debug(f"Found {app_name} at {path} (legacy detection)")
                    break
        
        return available_apps
    
    @safe_execute
    def get_application_executable(self, app_identifier: str) -> Optional[str]:
        """Get the executable path for an application"""
        available_apps = self.detect_available_applications()
        
        # Direct lookup
        if app_identifier in available_apps:
            return available_apps[app_identifier]
        
        # Check aliases
        for alias_key, aliases in ShellConstants.APP_ALIASES.items():
            if app_identifier.lower() in [alias.lower() for alias in aliases]:
                if alias_key in available_apps:
                    return available_apps[alias_key]
        
        # Try to find in PATH
        return self._find_in_path(app_identifier)
    
    @safe_execute
    def extract_executable_from_command(self, command: str) -> Optional[str]:
        """Extract the executable path from a shell command"""
        if not command:
            return None
        
        # Handle quoted paths
        if command.startswith('"'):
            end_quote = command.find('"', 1)
            if end_quote != -1:
                exe_path = command[1:end_quote]
            else:
                exe_path = command.split()[0]
        else:
            exe_path = command.split()[0]
        
        # Clean up common prefixes
        exe_path = exe_path.strip('\'"')
        
        # Expand environment variables
        exe_path = os.path.expandvars(exe_path)
        
        # Check if it exists
        if os.path.exists(exe_path):
            return exe_path
        
        # Try to find it in PATH
        return self._find_in_path(os.path.basename(exe_path))
    
    @safe_execute
    def get_application_info(self, exe_path: str) -> Dict[str, str]:
        """Get detailed information about an application"""
        if exe_path in self._app_cache:
            return self._app_cache[exe_path]
        
        info = {
            "path": exe_path,
            "name": os.path.basename(exe_path),
            "exists": os.path.exists(exe_path),
            "directory": os.path.dirname(exe_path)
        }
        
        if info["exists"]:
            try:
                # Try to get version info using Windows API
                info.update(self._get_file_version_info(exe_path))
            except Exception as e:
                self.logger.debug(f"Could not get version info for {exe_path}: {e}")
        
        self._app_cache[exe_path] = info
        return info
    
    @safe_execute
    def categorize_application(self, exe_path: str, display_text: str = "") -> str:
        """Categorize an application based on its path and name"""
        exe_name = os.path.basename(exe_path).lower()
        path_lower = exe_path.lower()
        text_lower = display_text.lower()
        
        # Code editors
        if any(term in exe_name or term in text_lower for term in [
            "code", "visual studio", "sublime", "notepad++", "atom", "vim"
        ]):
            return "editor"
        
        # Version control
        if any(term in exe_name or term in text_lower for term in [
            "git", "svn", "mercurial", "tortoise"
        ]):
            return "version_control"
        
        # Media players
        if any(term in exe_name or term in text_lower for term in [
            "vlc", "mpc", "media player", "winamp", "foobar"
        ]):
            return "media"
        
        # Compression tools
        if any(term in exe_name or term in text_lower for term in [
            "winrar", "7zip", "zip", "rar"
        ]):
            return "compression"
        
        # System tools
        if any(term in exe_name or term in path_lower for term in [
            "system32", "windows", "cmd", "powershell"
        ]):
            return "system"
        
        return "application"
    
    def _find_in_path(self, executable: str) -> Optional[str]:
        """Find an executable in the system PATH"""
        try:
            result = subprocess.run(
                ["where", executable],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                path = result.stdout.strip().split('\n')[0]
                if os.path.exists(path):
                    return path
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            self.logger.debug(f"Could not find {executable} in PATH: {e}")
        
        return None
    
    def _get_file_version_info(self, exe_path: str) -> Dict[str, str]:
        """Get file version information using Windows API"""
        import ctypes
        from ctypes import wintypes
        
        # This is a simplified version - in a full implementation,
        # you'd use the Windows Version Info API
        version_info = {}
        
        try:
            # Get file size for basic info
            stat = os.stat(exe_path)
            version_info["size"] = str(stat.st_size)
            version_info["modified"] = str(stat.st_mtime)
        except OSError as e:
            self.logger.debug(f"Could not get file stats for {exe_path}: {e}")
        
        return version_info
    
    def clear_cache(self):
        """Clear all application caches"""
        self._app_cache.clear()
        self._availability_cache.clear()
        self.logger.debug("Application detector cache cleared")
    
    @safe_execute
    def is_system_application(self, exe_path: str) -> bool:
        """Check if an application is a Windows system application"""
        path_lower = exe_path.lower()
        
        system_paths = [
            "c:\\windows\\system32",
            "c:\\windows\\syswow64", 
            "c:\\windows",
            "c:\\program files\\windows"
        ]
        
        return any(path_lower.startswith(sys_path) for sys_path in system_paths)