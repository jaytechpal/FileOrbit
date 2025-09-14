"""
Windows Registry Reader - Handles all Windows registry operations
"""

import winreg
from pathlib import Path
from typing import Dict, Optional, List
from src.utils.logger import get_logger
from src.config.constants import ShellConstants
from src.utils.error_handling import RegistryAccessError, safe_execute


class WindowsRegistryReader:
    """Handles all Windows registry read operations"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._cache = {}
    
    @safe_execute
    def get_file_type_info(self, file_path: Path) -> Dict[str, str]:
        """Get file type information from Windows registry"""
        if not file_path.is_file():
            return {}
        
        suffix = file_path.suffix.lower()
        if suffix in self._cache:
            return self._cache[suffix]
        
        try:
            # Get file type from extension
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, suffix) as key:
                file_type, _ = winreg.QueryValueEx(key, "")
                
            # Get file type description
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, file_type) as key:
                description, _ = winreg.QueryValueEx(key, "")
                
            result = {
                "type": file_type,
                "description": description,
                "extension": suffix
            }
            
            self._cache[suffix] = result
            return result
            
        except (FileNotFoundError, PermissionError, OSError) as e:
            self.logger.debug(f"Could not get file type info for {suffix}: {e}")
            raise RegistryAccessError(f"Failed to read file type info for {suffix}") from e
    
    @safe_execute
    def get_shell_extensions_for_extension(self, extension: str) -> List[Dict[str, str]]:
        """Get shell extensions for a specific file extension"""
        extensions = []
        
        try:
            # Get file type from extension
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, extension) as key:
                try:
                    file_type, _ = winreg.QueryValueEx(key, "")
                except FileNotFoundError:
                    return extensions
            
            # Get shell extensions for this file type
            shell_path = f"{file_type}\\shell"
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, shell_path) as shell_key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(shell_key, i)
                            extension_info = self._get_shell_extension_info(shell_path, subkey_name)
                            if extension_info:
                                extensions.append(extension_info)
                            i += 1
                        except OSError:
                            break
            except FileNotFoundError:
                self.logger.debug(f"No shell extensions found for {extension}")
                
        except (PermissionError, OSError) as e:
            self.logger.debug(f"Could not read shell extensions for {extension}: {e}")
            raise RegistryAccessError(f"Failed to read shell extensions for {extension}") from e
            
        return extensions
    
    @safe_execute
    def get_all_shell_extensions(self) -> List[Dict[str, str]]:
        """Get all available shell extensions from registry"""
        extensions = []
        
        try:
            # Enumerate all file types
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "") as root_key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(root_key, i)
                        
                        # Check if this is a file type (has shell extensions)
                        if subkey_name.startswith('.'):
                            ext_extensions = self.get_shell_extensions_for_extension(subkey_name)
                            extensions.extend(ext_extensions)
                        
                        i += 1
                    except OSError:
                        break
                        
        except (PermissionError, OSError) as e:
            self.logger.error(f"Could not enumerate shell extensions: {e}")
            raise RegistryAccessError("Failed to read shell extensions from registry") from e
            
        return extensions
    
    def _get_shell_extension_info(self, shell_path: str, subkey_name: str) -> Optional[Dict[str, str]]:
        """Get information about a specific shell extension"""
        try:
            extension_path = f"{shell_path}\\{subkey_name}"
            
            # Get display text
            display_text = subkey_name
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, extension_path) as ext_key:
                    display_text, _ = winreg.QueryValueEx(ext_key, "")
            except FileNotFoundError:
                pass
            
            # Get command
            command_path = f"{extension_path}\\command"
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, command_path) as cmd_key:
                    command, _ = winreg.QueryValueEx(cmd_key, "")
                    
                    return {
                        "text": display_text,
                        "command": command,
                        "action": subkey_name,
                        "registry_path": extension_path
                    }
            except FileNotFoundError:
                self.logger.debug(f"No command found for shell extension: {extension_path}")
                return None
                
        except (PermissionError, OSError) as e:
            self.logger.debug(f"Could not read shell extension {subkey_name}: {e}")
            return None
    
    @safe_execute
    def check_application_installed(self, app_name: str) -> bool:
        """Check if an application is installed by checking registry"""
        search_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        
        for search_path in search_paths:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, search_path) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                                    if app_name.lower() in display_name.lower():
                                        return True
                                except FileNotFoundError:
                                    pass
                            i += 1
                        except OSError:
                            break
            except (PermissionError, OSError) as e:
                self.logger.debug(f"Could not check installed applications in {search_path}: {e}")
                continue
                
        return False
    
    def clear_cache(self):
        """Clear the registry cache"""
        self._cache.clear()
        self.logger.debug("Registry cache cleared")