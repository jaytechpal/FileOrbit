"""
Enhanced Application Discovery Service - Finds applications in any installation location
"""

import os
import winreg
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set
from src.utils.logger import get_logger
from src.config.constants import PathConstants, IconConstants
from src.utils.error_handling import safe_execute, RegistryAccessError


class EnhancedApplicationDiscovery:
    """Advanced application discovery that handles custom installation paths"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._discovery_cache = {}
        self._path_cache = {}
        self._registry_cache = {}
    
    @safe_execute
    def discover_application(self, app_name: str) -> Optional[Dict[str, str]]:
        """Discover an application using multiple detection methods"""
        if app_name in self._discovery_cache:
            return self._discovery_cache[app_name]
        
        # Get search patterns for this application
        patterns = PathConstants.APPLICATION_SEARCH_PATTERNS.get(app_name)
        if not patterns:
            self.logger.debug(f"No search patterns defined for {app_name}")
            return None
        
        # Try different discovery methods in order of reliability
        discovery_methods = [
            self._discover_via_registry,
            self._discover_via_uninstall_registry,
            self._discover_via_path_environment,
            self._discover_via_common_locations,
            self._discover_via_file_search
        ]
        
        for method in discovery_methods:
            result = method(app_name, patterns)
            if result:
                self.logger.info(f"Found {app_name} via {method.__name__}: {result['path']}")
                self._discovery_cache[app_name] = result
                return result
        
        self.logger.debug(f"Could not discover {app_name} in any location")
        return None
    
    @safe_execute
    def discover_all_applications(self) -> Dict[str, Dict[str, str]]:
        """Discover all configured applications"""
        results = {}
        
        for app_name in PathConstants.APPLICATION_SEARCH_PATTERNS.keys():
            app_info = self.discover_application(app_name)
            if app_info:
                results[app_name] = app_info
        
        return results
    
    def _discover_via_registry(self, app_name: str, patterns: Dict) -> Optional[Dict[str, str]]:
        """Discover application via its specific registry keys"""
        for registry_key in patterns.get("registry_keys", []):
            try:
                # Try HKEY_LOCAL_MACHINE first
                for root_key in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                    try:
                        with winreg.OpenKey(root_key, registry_key) as key:
                            # Look for InstallLocation or similar
                            location_keys = ["InstallLocation", "InstallDir", "Path", ""]
                            
                            for location_key in location_keys:
                                try:
                                    install_path, _ = winreg.QueryValueEx(key, location_key)
                                    if install_path and os.path.exists(install_path):
                                        # Find executable in installation directory
                                        exe_path = self._find_executable_in_directory(
                                            install_path, patterns["executable_names"]
                                        )
                                        if exe_path:
                                            return self._create_app_info(app_name, exe_path, "registry")
                                except FileNotFoundError:
                                    continue
                    except (FileNotFoundError, PermissionError):
                        continue
            except Exception as e:
                self.logger.debug(f"Registry search failed for {app_name}: {e}")
        
        return None
    
    def _discover_via_uninstall_registry(self, app_name: str, patterns: Dict) -> Optional[Dict[str, str]]:
        """Discover application via Windows uninstall registry"""
        uninstall_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        
        display_names = patterns.get("uninstall_display_names", [])
        
        for uninstall_path in uninstall_paths:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, uninstall_path) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                                    
                                    # Check if this matches our application
                                    if any(name.lower() in display_name.lower() for name in display_names):
                                        # Get installation location
                                        try:
                                            install_location, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                                            if install_location and os.path.exists(install_location):
                                                exe_path = self._find_executable_in_directory(
                                                    install_location, patterns["executable_names"]
                                                )
                                                if exe_path:
                                                    return self._create_app_info(app_name, exe_path, "uninstall_registry")
                                        except FileNotFoundError:
                                            pass
                                except FileNotFoundError:
                                    pass
                            i += 1
                        except OSError:
                            break
            except (PermissionError, FileNotFoundError):
                continue
        
        return None
    
    def _discover_via_path_environment(self, app_name: str, patterns: Dict) -> Optional[Dict[str, str]]:
        """Discover application via PATH environment variable"""
        for exe_name in patterns.get("executable_names", []):
            try:
                # Use 'where' command to find executable in PATH
                result = subprocess.run(
                    ["where", exe_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    exe_path = result.stdout.strip().split('\n')[0]
                    if os.path.exists(exe_path):
                        return self._create_app_info(app_name, exe_path, "path_environment")
            except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
                self.logger.debug(f"PATH search failed for {exe_name}: {e}")
        
        return None
    
    def _discover_via_common_locations(self, app_name: str, patterns: Dict) -> Optional[Dict[str, str]]:
        """Discover application in common installation directories"""
        username = os.environ.get("USERNAME", "")
        
        for base_dir_template in PathConstants.COMMON_PROGRAM_DIRECTORIES:
            # Handle username placeholder
            base_dir = base_dir_template.format(username=username)
            
            if not os.path.exists(base_dir):
                continue
            
            # Check each common path pattern
            for path_pattern in patterns.get("common_paths", []):
                search_dir = os.path.join(base_dir, path_pattern)
                
                if os.path.exists(search_dir):
                    exe_path = self._find_executable_in_directory(
                        search_dir, patterns["executable_names"]
                    )
                    if exe_path:
                        return self._create_app_info(app_name, exe_path, "common_locations")
        
        return None
    
    def _discover_via_file_search(self, app_name: str, patterns: Dict) -> Optional[Dict[str, str]]:
        """Discover application via filesystem search (last resort)"""
        # This is expensive, so we limit it to likely directories
        search_roots = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            f"C:\\Users\\{os.environ.get('USERNAME', '')}"
        ]
        
        for root_dir in search_roots:
            if not os.path.exists(root_dir):
                continue
            
            try:
                for exe_name in patterns.get("executable_names", []):
                    # Use a limited depth search to avoid performance issues
                    for dirpath, dirnames, filenames in os.walk(root_dir):
                        # Limit search depth
                        depth = dirpath.replace(root_dir, '').count(os.sep)
                        if depth > 3:
                            dirnames[:] = []  # Don't recurse deeper
                            continue
                        
                        if exe_name in filenames:
                            exe_path = os.path.join(dirpath, exe_name)
                            if os.path.exists(exe_path):
                                return self._create_app_info(app_name, exe_path, "file_search")
                        
                        # Skip certain directories to speed up search
                        dirnames[:] = [d for d in dirnames if not d.startswith('.') and 
                                     d.lower() not in ['windows', 'system32', 'syswow64']]
            except (PermissionError, OSError) as e:
                self.logger.debug(f"File search failed in {root_dir}: {e}")
        
        return None
    
    def _find_executable_in_directory(self, directory: str, executable_names: List[str]) -> Optional[str]:
        """Find any of the given executables in a directory"""
        if not os.path.exists(directory):
            return None
        
        try:
            for exe_name in executable_names:
                exe_path = os.path.join(directory, exe_name)
                if os.path.exists(exe_path):
                    return exe_path
            
            # Also check subdirectories
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    result = self._find_executable_in_directory(item_path, executable_names)
                    if result:
                        return result
        except (PermissionError, OSError):
            pass
        
        return None
    
    def _create_app_info(self, app_name: str, exe_path: str, discovery_method: str) -> Dict[str, str]:
        """Create application information dictionary"""
        return {
            "name": app_name,
            "path": exe_path,
            "directory": os.path.dirname(exe_path),
            "executable": os.path.basename(exe_path),
            "discovery_method": discovery_method,
            "exists": os.path.exists(exe_path),
            "version": self._get_file_version(exe_path)
        }
    
    def _get_file_version(self, exe_path: str) -> str:
        """Get file version if available"""
        try:
            import win32api
            info = win32api.GetFileVersionInfo(exe_path, "\\")
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
            return version
        except Exception:
            return "Unknown"
    
    @safe_execute
    def add_custom_application(self, app_name: str, exe_path: str) -> bool:
        """Add a custom application to the discovery cache"""
        if not os.path.exists(exe_path):
            return False
        
        app_info = self._create_app_info(app_name, exe_path, "custom")
        self._discovery_cache[app_name] = app_info
        
        self.logger.info(f"Added custom application: {app_name} at {exe_path}")
        return True
    
    @safe_execute
    def get_application_suggestions(self, partial_name: str) -> List[Dict[str, str]]:
        """Get application suggestions based on partial name"""
        suggestions = []
        
        # Search through discovered applications
        for app_name, app_info in self._discovery_cache.items():
            if partial_name.lower() in app_name.lower():
                suggestions.append(app_info)
        
        # Search through PATH for additional executables
        try:
            result = subprocess.run(
                ["where", f"*{partial_name}*"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line and os.path.exists(line):
                        app_name = os.path.splitext(os.path.basename(line))[0]
                        suggestions.append(self._create_app_info(app_name, line, "suggestion"))
        except Exception:
            pass
        
        return suggestions
    
    def clear_cache(self):
        """Clear all discovery caches"""
        self._discovery_cache.clear()
        self._path_cache.clear()
        self._registry_cache.clear()
        self.logger.debug("Application discovery cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "discovered_applications": len(self._discovery_cache),
            "path_cache_size": len(self._path_cache),
            "registry_cache_size": len(self._registry_cache)
        }