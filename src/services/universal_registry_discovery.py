"""
Universal Registry Discovery Service - Automatically discovers all applications and context menu entries
"""

import os
import winreg
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from src.utils.logger import get_logger
from src.config.constants import PathConstants, ShellConstants
from src.utils.error_handling import safe_execute, RegistryAccessError


class UniversalRegistryDiscovery:
    """Universal discovery of all applications and shell extensions from Windows registry"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._applications_cache = {}
        self._shell_extensions_cache = {}
        self._context_menus_cache = {}
        self._cache_timestamp = None
    
    @safe_execute
    def discover_all_installed_applications(self) -> Dict[str, Dict[str, str]]:
        """Discover ALL installed applications from Windows registry"""
        if self._applications_cache and self._is_cache_valid():
            return self._applications_cache
        
        applications = {}
        
        # Method 1: Scan Windows Uninstall Registry
        uninstall_apps = self._scan_uninstall_registry()
        applications.update(uninstall_apps)
        
        # Method 2: Scan App Paths Registry
        app_paths = self._scan_app_paths_registry()
        applications.update(app_paths)
        
        # Method 3: Scan Classes Registry for Applications
        class_apps = self._scan_classes_applications()
        applications.update(class_apps)
        
        # Method 4: Scan for shell extensions with executables
        shell_apps = self._extract_apps_from_shell_extensions()
        applications.update(shell_apps)
        
        # Cache the results
        self._applications_cache = applications
        self._update_cache_timestamp()
        
        self.logger.info(f"Discovered {len(applications)} applications from registry")
        return applications
    
    @safe_execute
    def discover_all_context_menu_entries(self) -> Dict[str, List[Dict[str, str]]]:
        """Discover ALL context menu entries for different file types"""
        if self._context_menus_cache and self._is_cache_valid():
            return self._context_menus_cache
        
        context_menus = {}
        
        # Scan all file extensions and their shell commands
        file_type_menus = self._scan_file_type_shell_commands()
        context_menus.update(file_type_menus)
        
        # Scan system-wide shell extensions
        system_menus = self._scan_system_shell_extensions()
        context_menus["*"] = system_menus  # Universal context menu entries
        
        # Cache the results
        self._context_menus_cache = context_menus
        self._update_cache_timestamp()
        
        total_entries = sum(len(entries) for entries in context_menus.values())
        self.logger.info(f"Discovered {total_entries} context menu entries across {len(context_menus)} file types")
        return context_menus
    
    def _scan_uninstall_registry(self) -> Dict[str, Dict[str, str]]:
        """Scan Windows uninstall registry for all installed programs"""
        applications = {}
        
        for uninstall_path in PathConstants.REGISTRY_DISCOVERY_PATHS["uninstall_programs"]:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, uninstall_path) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            app_info = self._extract_app_info_from_uninstall_entry(uninstall_path, subkey_name)
                            if app_info:
                                app_id = app_info.get("name", subkey_name).lower().replace(" ", "_")
                                applications[app_id] = app_info
                            i += 1
                        except OSError:
                            break
            except (FileNotFoundError, PermissionError) as e:
                self.logger.debug(f"Could not access uninstall registry {uninstall_path}: {e}")
        
        return applications
    
    def _extract_app_info_from_uninstall_entry(self, base_path: str, subkey_name: str) -> Optional[Dict[str, str]]:
        """Extract application information from an uninstall registry entry"""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{base_path}\\{subkey_name}") as subkey:
                app_info = {"registry_key": f"{base_path}\\{subkey_name}"}
                
                # Get basic application information
                registry_values = {
                    "DisplayName": "name",
                    "DisplayVersion": "version", 
                    "Publisher": "publisher",
                    "InstallLocation": "install_path",
                    "DisplayIcon": "icon_path",
                    "UninstallString": "uninstall_command"
                }
                
                for reg_name, info_key in registry_values.items():
                    try:
                        value, _ = winreg.QueryValueEx(subkey, reg_name)
                        if value:
                            app_info[info_key] = str(value).strip()
                    except FileNotFoundError:
                        continue
                
                # Must have at least a display name
                if "name" not in app_info:
                    return None
                
                # Try to find the main executable
                executable_path = self._find_main_executable(app_info)
                if executable_path:
                    app_info["executable_path"] = executable_path
                    app_info["exists"] = os.path.exists(executable_path)
                
                app_info["discovery_method"] = "uninstall_registry"
                return app_info
                
        except (PermissionError, OSError) as e:
            self.logger.debug(f"Could not read uninstall entry {subkey_name}: {e}")
            return None
    
    def _scan_app_paths_registry(self) -> Dict[str, Dict[str, str]]:
        """Scan App Paths registry for registered applications"""
        applications = {}
        
        for app_paths_key in PathConstants.REGISTRY_DISCOVERY_PATHS["application_paths"]:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, app_paths_key) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            app_info = self._extract_app_info_from_app_paths(app_paths_key, subkey_name)
                            if app_info:
                                app_id = os.path.splitext(subkey_name)[0].lower()
                                applications[app_id] = app_info
                            i += 1
                        except OSError:
                            break
            except (FileNotFoundError, PermissionError) as e:
                self.logger.debug(f"Could not access app paths registry {app_paths_key}: {e}")
        
        return applications
    
    def _extract_app_info_from_app_paths(self, base_path: str, subkey_name: str) -> Optional[Dict[str, str]]:
        """Extract application info from App Paths registry"""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{base_path}\\{subkey_name}") as subkey:
                app_info = {
                    "name": os.path.splitext(subkey_name)[0],
                    "registry_key": f"{base_path}\\{subkey_name}",
                    "discovery_method": "app_paths_registry"
                }
                
                # Get default value (executable path)
                try:
                    executable_path, _ = winreg.QueryValueEx(subkey, "")
                    if executable_path and os.path.exists(executable_path):
                        app_info["executable_path"] = executable_path
                        app_info["exists"] = True
                        app_info["install_path"] = os.path.dirname(executable_path)
                    else:
                        app_info["exists"] = False
                except FileNotFoundError:
                    return None
                
                # Get additional information
                try:
                    path_value, _ = winreg.QueryValueEx(subkey, "Path")
                    if path_value:
                        app_info["additional_paths"] = path_value
                except FileNotFoundError:
                    pass
                
                return app_info
                
        except (PermissionError, OSError) as e:
            self.logger.debug(f"Could not read app paths entry {subkey_name}: {e}")
            return None
    
    def _scan_classes_applications(self) -> Dict[str, Dict[str, str]]:
        """Scan HKEY_CLASSES_ROOT\\Applications for registered applications"""
        applications = {}
        
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "Applications") as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        if subkey_name.lower().endswith('.exe'):
                            app_info = self._extract_app_info_from_classes_application(subkey_name)
                            if app_info:
                                app_id = os.path.splitext(subkey_name)[0].lower()
                                applications[app_id] = app_info
                        i += 1
                    except OSError:
                        break
        except (FileNotFoundError, PermissionError) as e:
            self.logger.debug(f"Could not access Classes\\Applications registry: {e}")
        
        return applications
    
    def _extract_app_info_from_classes_application(self, app_exe_name: str) -> Optional[Dict[str, str]]:
        """Extract application info from Classes\\Applications registry"""
        try:
            app_info = {
                "name": os.path.splitext(app_exe_name)[0],
                "executable_name": app_exe_name,
                "discovery_method": "classes_applications"
            }
            
            # Try to find the executable in common locations
            executable_path = self._find_executable_by_name(app_exe_name)
            if executable_path:
                app_info["executable_path"] = executable_path
                app_info["exists"] = True
                app_info["install_path"] = os.path.dirname(executable_path)
            else:
                app_info["exists"] = False
            
            return app_info
            
        except Exception as e:
            self.logger.debug(f"Could not process classes application {app_exe_name}: {e}")
            return None
    
    def _scan_file_type_shell_commands(self) -> Dict[str, List[Dict[str, str]]]:
        """Scan all file type shell commands"""
        file_type_menus = {}
        
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "") as root_key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(root_key, i)
                        
                        # Process file extensions and progids
                        if subkey_name.startswith('.') or not subkey_name.startswith('CLSID'):
                            shell_commands = self._extract_shell_commands_for_type(subkey_name)
                            if shell_commands:
                                file_type_menus[subkey_name] = shell_commands
                        
                        i += 1
                        
                        # Limit to prevent excessive scanning
                        if i > 5000:  # Reasonable limit
                            break
                            
                    except OSError:
                        break
        except (FileNotFoundError, PermissionError) as e:
            self.logger.debug(f"Could not scan file type shell commands: {e}")
        
        return file_type_menus
    
    def _extract_shell_commands_for_type(self, file_type: str) -> List[Dict[str, str]]:
        """Extract shell commands for a specific file type"""
        commands = []
        
        # Check direct shell commands
        shell_path = f"{file_type}\\shell"
        commands.extend(self._scan_shell_commands_in_path(shell_path))
        
        # Check if this is a file extension that references a progid
        if file_type.startswith('.'):
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, file_type) as key:
                    try:
                        progid, _ = winreg.QueryValueEx(key, "")
                        if progid:
                            progid_shell_path = f"{progid}\\shell"
                            commands.extend(self._scan_shell_commands_in_path(progid_shell_path))
                    except FileNotFoundError:
                        pass
            except (FileNotFoundError, PermissionError):
                pass
        
        return commands
    
    def _scan_shell_commands_in_path(self, shell_path: str) -> List[Dict[str, str]]:
        """Scan shell commands in a specific registry path"""
        commands = []
        
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, shell_path) as shell_key:
                i = 0
                while True:
                    try:
                        command_name = winreg.EnumKey(shell_key, i)
                        command_info = self._extract_shell_command_info(shell_path, command_name)
                        if command_info:
                            commands.append(command_info)
                        i += 1
                    except OSError:
                        break
        except (FileNotFoundError, PermissionError):
            pass
        
        return commands
    
    def _extract_shell_command_info(self, shell_path: str, command_name: str) -> Optional[Dict[str, str]]:
        """Extract information about a shell command"""
        try:
            command_path = f"{shell_path}\\{command_name}"
            command_info = {
                "action": command_name,
                "registry_path": command_path
            }
            
            # Get display text
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, command_path) as cmd_key:
                    try:
                        display_text, _ = winreg.QueryValueEx(cmd_key, "")
                        command_info["text"] = display_text if display_text else command_name
                    except FileNotFoundError:
                        command_info["text"] = command_name
                        
                    # Get MUI verb if available
                    try:
                        mui_verb, _ = winreg.QueryValueEx(cmd_key, "MUIVerb")
                        if mui_verb:
                            command_info["mui_verb"] = mui_verb
                    except FileNotFoundError:
                        pass
            except (FileNotFoundError, PermissionError):
                command_info["text"] = command_name
            
            # Get command string
            command_subpath = f"{command_path}\\command"
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, command_subpath) as cmd_key:
                    try:
                        command_string, _ = winreg.QueryValueEx(cmd_key, "")
                        if command_string:
                            command_info["command"] = command_string
                            
                            # Extract executable from command
                            executable = self._extract_executable_from_command(command_string)
                            if executable:
                                command_info["executable"] = executable
                                command_info["executable_exists"] = os.path.exists(executable)
                        else:
                            return None
                    except FileNotFoundError:
                        return None
            except (FileNotFoundError, PermissionError):
                return None
            
            return command_info
            
        except Exception as e:
            self.logger.debug(f"Could not extract shell command info for {command_name}: {e}")
            return None
    
    def _scan_system_shell_extensions(self) -> List[Dict[str, str]]:
        """Scan system-wide shell extensions"""
        extensions = []
        
        system_paths = [
            "*\\shell",
            "Directory\\shell",
            "Folder\\shell", 
            "AllFilesystemObjects\\shell"
        ]
        
        for path in system_paths:
            extensions.extend(self._scan_shell_commands_in_path(path))
        
        return extensions
    
    def _extract_apps_from_shell_extensions(self) -> Dict[str, Dict[str, str]]:
        """Extract application information from shell extension commands"""
        applications = {}
        
        # Get all context menu entries
        context_menus = self.discover_all_context_menu_entries()
        
        for file_type, commands in context_menus.items():
            for command in commands:
                executable = command.get("executable")
                if executable and os.path.exists(executable):
                    app_name = os.path.splitext(os.path.basename(executable))[0].lower()
                    
                    if app_name not in applications:
                        applications[app_name] = {
                            "name": app_name,
                            "executable_path": executable,
                            "install_path": os.path.dirname(executable),
                            "discovery_method": "shell_extension",
                            "exists": True,
                            "context_menu_actions": []
                        }
                    
                    # Add this context menu action to the app
                    applications[app_name]["context_menu_actions"].append({
                        "action": command.get("action"),
                        "text": command.get("text"),
                        "file_type": file_type
                    })
        
        return applications
    
    def _find_main_executable(self, app_info: Dict[str, str]) -> Optional[str]:
        """Find the main executable for an application"""
        # Check install location first
        install_path = app_info.get("install_path")
        if install_path and os.path.exists(install_path):
            executable = self._find_executable_in_directory(install_path)
            if executable:
                return executable
        
        # Check icon path (often points to executable)
        icon_path = app_info.get("icon_path")
        if icon_path and icon_path.lower().endswith('.exe') and os.path.exists(icon_path):
            return icon_path
        
        # Parse uninstall string
        uninstall_command = app_info.get("uninstall_command")
        if uninstall_command:
            executable = self._extract_executable_from_command(uninstall_command)
            if executable and os.path.exists(executable):
                # Look for main exe in same directory
                main_exe = self._find_executable_in_directory(os.path.dirname(executable))
                if main_exe:
                    return main_exe
        
        return None
    
    def _find_executable_in_directory(self, directory: str) -> Optional[str]:
        """Find the most likely main executable in a directory"""
        if not os.path.exists(directory):
            return None
        
        try:
            exe_files = [f for f in os.listdir(directory) if f.lower().endswith('.exe')]
            
            if not exe_files:
                return None
            
            # Prioritize certain executable names
            priority_patterns = ['setup', 'install', 'uninstall', 'uninst']
            main_exes = [f for f in exe_files if not any(p in f.lower() for p in priority_patterns)]
            
            if main_exes:
                # Return the first non-installer executable
                return os.path.join(directory, main_exes[0])
            elif exe_files:
                # Fallback to any executable
                return os.path.join(directory, exe_files[0])
        
        except (PermissionError, OSError):
            pass
        
        return None
    
    def _find_executable_by_name(self, exe_name: str) -> Optional[str]:
        """Find an executable by name in common locations"""
        # Search in PATH first
        import subprocess
        try:
            result = subprocess.run(
                ["where", exe_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                path = result.stdout.strip().split('\n')[0]
                if os.path.exists(path):
                    return path
        except Exception:
            pass
        
        # Search in common directories
        username = os.environ.get("USERNAME", "")
        for base_dir_template in PathConstants.GENERIC_SEARCH_DIRECTORIES:
            base_dir = base_dir_template.format(username=username)
            if os.path.exists(base_dir):
                # Simple search in subdirectories
                for root, dirs, files in os.walk(base_dir):
                    if exe_name.lower() in [f.lower() for f in files]:
                        return os.path.join(root, exe_name)
                    # Limit search depth
                    if root.replace(base_dir, '').count(os.sep) > 2:
                        dirs[:] = []
        
        return None
    
    def _extract_executable_from_command(self, command: str) -> Optional[str]:
        """Extract executable path from a command string"""
        if not command:
            return None
        
        # Handle quoted paths
        if command.startswith('"'):
            end_quote = command.find('"', 1)
            if end_quote != -1:
                exe_path = command[1:end_quote]
            else:
                exe_path = command.split()[0] if command.split() else ""
        else:
            exe_path = command.split()[0] if command.split() else ""
        
        # Clean up and expand variables
        exe_path = exe_path.strip('\'"')
        exe_path = os.path.expandvars(exe_path)
        
        # Check if it exists
        if exe_path and os.path.exists(exe_path):
            return exe_path
        
        return None
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid (1 hour expiration)"""
        if not self._cache_timestamp:
            return False
        
        import time
        return (time.time() - self._cache_timestamp) < 3600  # 1 hour
    
    def _update_cache_timestamp(self):
        """Update cache timestamp"""
        import time
        self._cache_timestamp = time.time()
    
    @safe_execute
    def clear_cache(self):
        """Clear all caches"""
        self._applications_cache.clear()
        self._shell_extensions_cache.clear()
        self._context_menus_cache.clear()
        self._cache_timestamp = None
        self.logger.debug("Universal registry discovery cache cleared")
    
    @safe_execute
    def get_discovery_stats(self) -> Dict[str, int]:
        """Get discovery statistics"""
        return {
            "total_applications": len(self._applications_cache),
            "total_context_menu_types": len(self._context_menus_cache),
            "total_context_menu_entries": sum(len(entries) for entries in self._context_menus_cache.values()),
            "cache_valid": self._is_cache_valid()
        }