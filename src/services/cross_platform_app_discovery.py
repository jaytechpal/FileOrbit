"""
Cross-Platform Application Discovery Service
Provides unified application discovery across Windows, macOS, and Linux
"""

import os
import subprocess
import re
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

try:
    import winreg
    HAS_WINREG = True
except ImportError:
    HAS_WINREG = False

try:
    import plistlib
    HAS_PLISTLIB = True
except ImportError:
    HAS_PLISTLIB = False

from platform_config import get_platform_config
from src.utils.logger import get_logger


@dataclass
class ApplicationInfo:
    """Cross-platform application information"""
    name: str
    executable: str
    icon: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    install_path: Optional[str] = None
    bundle_id: Optional[str] = None  # macOS specific
    desktop_file: Optional[str] = None  # Linux specific
    exists: bool = False
    platform: str = ""


class CrossPlatformApplicationDiscovery:
    """Cross-platform application discovery service"""
    
    def __init__(self):
        self.config = get_platform_config()
        self.logger = get_logger(__name__)
        self.cache = {}
        self.cache_dirty = True
    
    def discover_applications(self, force_refresh: bool = False) -> List[ApplicationInfo]:
        """Discover all available applications on the system"""
        if not force_refresh and not self.cache_dirty and self.cache:
            return list(self.cache.values())
        
        self.logger.info("Starting cross-platform application discovery")
        applications = []
        
        try:
            if self.config.is_windows:
                applications.extend(self._discover_windows_applications())
            elif self.config.is_macos:
                applications.extend(self._discover_macos_applications())
            elif self.config.is_linux:
                applications.extend(self._discover_linux_applications())
            else:
                self.logger.warning("Unknown platform, using fallback discovery")
                applications.extend(self._discover_fallback_applications())
            
            # Update cache
            self.cache = {app.name.lower(): app for app in applications}
            self.cache_dirty = False
            
            self.logger.info(f"Discovered {len(applications)} applications")
            return applications
            
        except Exception as e:
            self.logger.error(f"Error during application discovery: {e}")
            return []
    
    def _discover_windows_applications(self) -> List[ApplicationInfo]:
        """Discover Windows applications using registry and common paths"""
        applications = []
        
        if not HAS_WINREG:
            self.logger.warning("Windows registry access not available")
            return self._discover_windows_fallback()
        
        # Registry locations to search
        registry_locations = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        
        for hkey, subkey in registry_locations:
            try:
                applications.extend(self._scan_windows_registry(hkey, subkey))
            except Exception as e:
                self.logger.debug(f"Error scanning registry {subkey}: {e}")
        
        # Add applications from common installation directories
        common_paths = [
            Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')),
            Path(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')),
            Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local')),
            Path.home() / 'AppData' / 'Local' / 'Programs',
        ]
        
        for path in common_paths:
            if path.exists():
                applications.extend(self._scan_windows_directory(path))
        
        return applications
    
    def _scan_windows_registry(self, hkey, subkey_path: str) -> List[ApplicationInfo]:
        """Scan Windows registry for installed applications"""
        applications = []
        
        try:
            with winreg.OpenKey(hkey, subkey_path) as key:
                i = 0
                while True:
                    try:
                        app_key_name = winreg.EnumKey(key, i)
                        app_info = self._get_windows_app_info(hkey, f"{subkey_path}\\{app_key_name}")
                        if app_info:
                            applications.append(app_info)
                        i += 1
                    except WindowsError:
                        break
        except Exception as e:
            self.logger.debug(f"Error scanning registry key {subkey_path}: {e}")
        
        return applications
    
    def _get_windows_app_info(self, hkey, app_key_path: str) -> Optional[ApplicationInfo]:
        """Get application info from Windows registry entry"""
        try:
            with winreg.OpenKey(hkey, app_key_path) as app_key:
                # Get application properties
                try:
                    display_name = winreg.QueryValueEx(app_key, "DisplayName")[0]
                except FileNotFoundError:
                    return None  # Skip entries without display name
                
                # Skip system components and updates
                if any(skip in display_name.lower() for skip in [
                    'microsoft visual c++', 'microsoft .net', 'update',
                    'redistributable', 'runtime', 'hotfix'
                ]):
                    return None
                
                executable = None
                install_path = None
                icon = None
                version = None
                
                # Try to get executable path
                try:
                    install_location = winreg.QueryValueEx(app_key, "InstallLocation")[0]
                    if install_location and Path(install_location).exists():
                        install_path = install_location
                        # Find main executable
                        executable = self._find_main_executable(install_location)
                except FileNotFoundError:
                    pass
                
                # Try to get executable from DisplayIcon
                try:
                    display_icon = winreg.QueryValueEx(app_key, "DisplayIcon")[0]
                    if display_icon and display_icon.endswith('.exe'):
                        icon_path = Path(display_icon)
                        if icon_path.exists():
                            executable = str(icon_path)
                            install_path = str(icon_path.parent)
                            icon = display_icon
                except FileNotFoundError:
                    pass
                
                # Try to get executable from UninstallString
                if not executable:
                    try:
                        uninstall_string = winreg.QueryValueEx(app_key, "UninstallString")[0]
                        # Extract executable from uninstall string
                        if '"' in uninstall_string:
                            exe_path = uninstall_string.split('"')[1]
                        else:
                            exe_path = uninstall_string.split()[0]
                        
                        exe_path = Path(exe_path)
                        if exe_path.exists() and exe_path.suffix.lower() == '.exe':
                            install_path = str(exe_path.parent)
                            # Look for main executable in the same directory
                            main_exe = self._find_main_executable(install_path)
                            if main_exe:
                                executable = main_exe
                    except (FileNotFoundError, IndexError):
                        pass
                
                # Get version
                try:
                    version = winreg.QueryValueEx(app_key, "DisplayVersion")[0]
                except FileNotFoundError:
                    pass
                
                if executable or install_path:
                    return ApplicationInfo(
                        name=display_name,
                        executable=executable or "",
                        icon=icon,
                        version=version,
                        install_path=install_path,
                        exists=bool(executable and Path(executable).exists()),
                        platform="windows"
                    )
                    
        except Exception as e:
            self.logger.debug(f"Error reading registry app info: {e}")
        
        return None
    
    def _scan_windows_directory(self, directory: Path) -> List[ApplicationInfo]:
        """Scan Windows directory for applications"""
        applications = []
        
        try:
            for item in directory.iterdir():
                if item.is_dir():
                    # Look for executable files in subdirectories
                    exe_files = list(item.glob("*.exe"))
                    for exe_file in exe_files:
                        if self._is_likely_main_executable(exe_file):
                            app_info = ApplicationInfo(
                                name=item.name,
                                executable=str(exe_file),
                                install_path=str(item),
                                exists=True,
                                platform="windows"
                            )
                            applications.append(app_info)
                            break  # Only take the first main executable per directory
        except PermissionError:
            pass
        
        return applications
    
    def _discover_windows_fallback(self) -> List[ApplicationInfo]:
        """Fallback Windows discovery when registry is not available"""
        applications = []
        
        # Scan common paths manually
        common_paths = [
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            str(Path.home() / "AppData" / "Local" / "Programs"),
        ]
        
        for path_str in common_paths:
            path = Path(path_str)
            if path.exists():
                applications.extend(self._scan_windows_directory(path))
        
        return applications
    
    def _discover_macos_applications(self) -> List[ApplicationInfo]:
        """Discover macOS applications from /Applications and user Applications"""
        applications = []
        
        # Standard application directories
        app_directories = [
            Path('/Applications'),
            Path('/System/Applications'),
            Path.home() / 'Applications',
        ]
        
        for app_dir in app_directories:
            if app_dir.exists():
                applications.extend(self._scan_macos_applications(app_dir))
        
        return applications
    
    def _scan_macos_applications(self, directory: Path) -> List[ApplicationInfo]:
        """Scan macOS application directory"""
        applications = []
        
        try:
            for item in directory.iterdir():
                if item.is_dir() and item.suffix == '.app':
                    app_info = self._get_macos_app_info(item)
                    if app_info:
                        applications.append(app_info)
        except PermissionError:
            pass
        
        return applications
    
    def _get_macos_app_info(self, app_bundle: Path) -> Optional[ApplicationInfo]:
        """Get application info from macOS app bundle"""
        try:
            # Read Info.plist
            info_plist_path = app_bundle / 'Contents' / 'Info.plist'
            if not info_plist_path.exists():
                return None
            
            if not HAS_PLISTLIB:
                # Fallback without plistlib
                return ApplicationInfo(
                    name=app_bundle.stem,
                    executable=str(app_bundle),
                    install_path=str(app_bundle),
                    exists=True,
                    platform="macos"
                )
            
            with open(info_plist_path, 'rb') as f:
                plist_data = plistlib.load(f)
            
            # Extract app information
            app_name = plist_data.get('CFBundleDisplayName') or plist_data.get('CFBundleName') or app_bundle.stem
            bundle_id = plist_data.get('CFBundleIdentifier', '')
            version = plist_data.get('CFBundleShortVersionString') or plist_data.get('CFBundleVersion', '')
            
            # Find executable
            executable_name = plist_data.get('CFBundleExecutable')
            executable_path = None
            if executable_name:
                executable_path = app_bundle / 'Contents' / 'MacOS' / executable_name
                if not executable_path.exists():
                    executable_path = None
            
            return ApplicationInfo(
                name=app_name,
                executable=str(executable_path) if executable_path else str(app_bundle),
                version=version,
                install_path=str(app_bundle),
                bundle_id=bundle_id,
                exists=True,
                platform="macos"
            )
            
        except Exception as e:
            self.logger.debug(f"Error reading macOS app info for {app_bundle}: {e}")
            return None
    
    def _discover_linux_applications(self) -> List[ApplicationInfo]:
        """Discover Linux applications from desktop files"""
        applications = []
        
        # Standard desktop file directories
        desktop_dirs = [
            Path('/usr/share/applications'),
            Path('/usr/local/share/applications'),
            Path.home() / '.local' / 'share' / 'applications',
        ]
        
        # Add XDG data directories
        xdg_data_dirs = os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':')
        for data_dir in xdg_data_dirs:
            desktop_dirs.append(Path(data_dir) / 'applications')
        
        for desktop_dir in desktop_dirs:
            if desktop_dir.exists():
                applications.extend(self._scan_linux_desktop_files(desktop_dir))
        
        return applications
    
    def _scan_linux_desktop_files(self, directory: Path) -> List[ApplicationInfo]:
        """Scan Linux desktop files directory"""
        applications = []
        
        try:
            for desktop_file in directory.glob('*.desktop'):
                app_info = self._get_linux_app_info(desktop_file)
                if app_info:
                    applications.append(app_info)
        except PermissionError:
            pass
        
        return applications
    
    def _get_linux_app_info(self, desktop_file: Path) -> Optional[ApplicationInfo]:
        """Get application info from Linux desktop file"""
        try:
            with open(desktop_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse desktop file
            name = self._extract_desktop_entry(content, 'Name')
            exec_line = self._extract_desktop_entry(content, 'Exec')
            icon = self._extract_desktop_entry(content, 'Icon')
            version = self._extract_desktop_entry(content, 'Version')
            comment = self._extract_desktop_entry(content, 'Comment')
            no_display = self._extract_desktop_entry(content, 'NoDisplay')
            
            # Skip hidden applications
            if no_display and no_display.lower() == 'true':
                return None
            
            if not name or not exec_line:
                return None
            
            # Parse executable from Exec line
            executable = self._parse_exec_line(exec_line)
            if not executable:
                return None
            
            # Find the actual executable path
            executable_path = self._find_executable_in_path(executable)
            
            return ApplicationInfo(
                name=name,
                executable=executable_path or executable,
                icon=icon,
                version=version,
                description=comment,
                desktop_file=str(desktop_file),
                exists=bool(executable_path),
                platform="linux"
            )
            
        except Exception as e:
            self.logger.debug(f"Error reading Linux desktop file {desktop_file}: {e}")
            return None
    
    def _extract_desktop_entry(self, content: str, key: str) -> Optional[str]:
        """Extract value from desktop file content"""
        pattern = rf'^{key}=(.*)$'
        match = re.search(pattern, content, re.MULTILINE)
        return match.group(1).strip() if match else None
    
    def _parse_exec_line(self, exec_line: str) -> Optional[str]:
        """Parse executable name from Exec line"""
        # Remove desktop file field codes (%f, %F, %u, %U, etc.)
        exec_clean = re.sub(r'%[a-zA-Z]', '', exec_line).strip()
        
        # Split by spaces and take first part (the executable)
        parts = exec_clean.split()
        if parts:
            return parts[0]
        return None
    
    def _find_executable_in_path(self, executable: str) -> Optional[str]:
        """Find executable in system PATH"""
        try:
            result = subprocess.run(['which', executable], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def _discover_fallback_applications(self) -> List[ApplicationInfo]:
        """Fallback discovery for unknown platforms"""
        applications = []
        
        # Try to find common applications in PATH
        common_apps = [
            'firefox', 'chrome', 'chromium', 'safari',
            'code', 'vim', 'emacs', 'nano',
            'git', 'python', 'node', 'java'
        ]
        
        for app_name in common_apps:
            executable_path = self._find_executable_in_path(app_name)
            if executable_path:
                applications.append(ApplicationInfo(
                    name=app_name.title(),
                    executable=executable_path,
                    exists=True,
                    platform="unknown"
                ))
        
        return applications
    
    def _find_main_executable(self, directory: str) -> Optional[str]:
        """Find the main executable in a directory"""
        directory_path = Path(directory)
        if not directory_path.exists():
            return None
        
        # Look for executable files
        exe_files = []
        for pattern in ['*.exe', '*']:
            exe_files.extend(directory_path.glob(pattern))
        
        # Filter actual executables
        executables = [f for f in exe_files if f.is_file() and self._is_executable(f)]
        
        if not executables:
            return None
        
        # Prefer main executables
        for exe in executables:
            if self._is_likely_main_executable(exe):
                return str(exe)
        
        # Return first executable if no main found
        return str(executables[0])
    
    def _is_executable(self, file_path: Path) -> bool:
        """Check if file is executable"""
        if self.config.is_windows:
            return file_path.suffix.lower() in ['.exe', '.bat', '.cmd']
        else:
            return os.access(file_path, os.X_OK)
    
    def _is_likely_main_executable(self, file_path: Path) -> bool:
        """Check if executable is likely the main application executable"""
        name = file_path.stem.lower()
        
        # Skip common non-main executables
        skip_patterns = [
            'uninstall', 'setup', 'install', 'update', 'config',
            'helper', 'launcher', 'crash', 'report', 'debug'
        ]
        
        if any(pattern in name for pattern in skip_patterns):
            return False
        
        # Prefer executables that match directory name
        parent_name = file_path.parent.name.lower()
        if name in parent_name or parent_name in name:
            return True
        
        return True
    
    def find_application(self, name: str) -> Optional[ApplicationInfo]:
        """Find specific application by name"""
        if self.cache_dirty:
            self.discover_applications()
        
        # Try exact match first
        app_key = name.lower()
        if app_key in self.cache:
            return self.cache[app_key]
        
        # Try partial match
        for cached_name, app_info in self.cache.items():
            if name.lower() in cached_name or cached_name in name.lower():
                return app_info
        
        return None
    
    def get_applications_by_type(self, app_type: str) -> List[ApplicationInfo]:
        """Get applications by type (e.g., 'browser', 'editor', 'media')"""
        if self.cache_dirty:
            self.discover_applications()
        
        type_keywords = {
            'browser': ['firefox', 'chrome', 'chromium', 'safari', 'edge', 'opera'],
            'editor': ['code', 'vim', 'emacs', 'nano', 'notepad', 'sublime', 'atom'],
            'media': ['vlc', 'media player', 'quicktime', 'windows media'],
            'office': ['word', 'excel', 'powerpoint', 'libreoffice', 'openoffice'],
            'development': ['visual studio', 'intellij', 'eclipse', 'xcode', 'git']
        }
        
        keywords = type_keywords.get(app_type.lower(), [])
        if not keywords:
            return []
        
        matching_apps = []
        for app_info in self.cache.values():
            app_name_lower = app_info.name.lower()
            if any(keyword in app_name_lower for keyword in keywords):
                matching_apps.append(app_info)
        
        return matching_apps


# Global instance
cross_platform_app_discovery = CrossPlatformApplicationDiscovery()


def get_application_discovery() -> CrossPlatformApplicationDiscovery:
    """Get the global application discovery instance"""
    return cross_platform_app_discovery