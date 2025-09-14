"""
Application Configuration Service - Manages custom application paths and user preferences
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from src.utils.logger import get_logger
from src.utils.error_handling import safe_execute


class ApplicationConfigService:
    """Manages custom application paths and configurations"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.logger = get_logger(__name__)
        
        # Default config directory
        if config_dir is None:
            config_dir = os.path.join(
                os.environ.get("APPDATA", ""), 
                "FileOrbit"
            )
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "application_paths.json"
        self.custom_apps = {}
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing configuration
        self._load_config()
    
    @safe_execute
    def add_custom_application(self, app_name: str, exe_path: str, display_name: str = "") -> bool:
        """Add a custom application path"""
        if not os.path.exists(exe_path):
            self.logger.warning(f"Executable not found: {exe_path}")
            return False
        
        if not display_name:
            display_name = os.path.splitext(os.path.basename(exe_path))[0].title()
        
        app_info = {
            "path": exe_path,
            "display_name": display_name,
            "added_date": self._get_current_timestamp(),
            "category": self._detect_category(exe_path, display_name)
        }
        
        self.custom_apps[app_name] = app_info
        self._save_config()
        
        self.logger.info(f"Added custom application: {app_name} -> {exe_path}")
        return True
    
    @safe_execute
    def remove_custom_application(self, app_name: str) -> bool:
        """Remove a custom application"""
        if app_name in self.custom_apps:
            del self.custom_apps[app_name]
            self._save_config()
            self.logger.info(f"Removed custom application: {app_name}")
            return True
        return False
    
    @safe_execute
    def get_custom_applications(self) -> Dict[str, Dict[str, str]]:
        """Get all custom applications"""
        return self.custom_apps.copy()
    
    @safe_execute
    def get_application_path(self, app_name: str) -> Optional[str]:
        """Get the path for a specific application"""
        app_info = self.custom_apps.get(app_name)
        if app_info:
            path = app_info.get("path")
            # Verify the path still exists
            if path and os.path.exists(path):
                return path
            else:
                self.logger.warning(f"Custom application path no longer exists: {path}")
                return None
        return None
    
    @safe_execute
    def update_application_path(self, app_name: str, new_path: str) -> bool:
        """Update the path for an existing custom application"""
        if app_name not in self.custom_apps:
            return False
        
        if not os.path.exists(new_path):
            self.logger.warning(f"New path does not exist: {new_path}")
            return False
        
        self.custom_apps[app_name]["path"] = new_path
        self.custom_apps[app_name]["updated_date"] = self._get_current_timestamp()
        self._save_config()
        
        self.logger.info(f"Updated application path: {app_name} -> {new_path}")
        return True
    
    @safe_execute
    def validate_custom_applications(self) -> Dict[str, bool]:
        """Validate all custom applications and return their status"""
        validation_results = {}
        apps_to_remove = []
        
        for app_name, app_info in self.custom_apps.items():
            path = app_info.get("path", "")
            exists = os.path.exists(path)
            validation_results[app_name] = exists
            
            if not exists:
                self.logger.warning(f"Custom application no longer exists: {app_name} -> {path}")
                # Optionally mark for removal or ask user
                # apps_to_remove.append(app_name)
        
        # Remove invalid applications if desired
        # for app_name in apps_to_remove:
        #     self.remove_custom_application(app_name)
        
        return validation_results
    
    @safe_execute
    def suggest_applications_in_directory(self, directory: str) -> List[Dict[str, str]]:
        """Suggest applications found in a directory"""
        suggestions = []
        
        if not os.path.exists(directory):
            return suggestions
        
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                
                if os.path.isfile(item_path) and item.lower().endswith('.exe'):
                    app_name = os.path.splitext(item)[0].lower()
                    display_name = os.path.splitext(item)[0].title()
                    
                    suggestion = {
                        "app_name": app_name,
                        "display_name": display_name,
                        "path": item_path,
                        "category": self._detect_category(item_path, display_name)
                    }
                    suggestions.append(suggestion)
        except (PermissionError, OSError) as e:
            self.logger.debug(f"Could not scan directory {directory}: {e}")
        
        return suggestions
    
    @safe_execute
    def import_applications_from_directory(self, directory: str) -> int:
        """Import all executables from a directory as custom applications"""
        suggestions = self.suggest_applications_in_directory(directory)
        imported_count = 0
        
        for suggestion in suggestions:
            app_name = suggestion["app_name"]
            
            # Don't import if already exists
            if app_name not in self.custom_apps:
                success = self.add_custom_application(
                    app_name,
                    suggestion["path"],
                    suggestion["display_name"]
                )
                if success:
                    imported_count += 1
        
        self.logger.info(f"Imported {imported_count} applications from {directory}")
        return imported_count
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.custom_apps = data.get("custom_applications", {})
                    self.logger.debug(f"Loaded {len(self.custom_apps)} custom applications")
            else:
                self.custom_apps = {}
        except (json.JSONDecodeError, OSError) as e:
            self.logger.error(f"Could not load application config: {e}")
            self.custom_apps = {}
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            config_data = {
                "version": "1.0",
                "custom_applications": self.custom_apps,
                "last_updated": self._get_current_timestamp()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
            self.logger.debug("Application configuration saved")
        except OSError as e:
            self.logger.error(f"Could not save application config: {e}")
    
    def _detect_category(self, exe_path: str, display_name: str) -> str:
        """Detect application category based on path and name"""
        exe_name = os.path.basename(exe_path).lower()
        path_lower = exe_path.lower()
        name_lower = display_name.lower()
        
        # Code editors
        if any(term in exe_name or term in name_lower for term in [
            "code", "visual studio", "sublime", "notepad++", "atom", "vim", "emacs"
        ]):
            return "editor"
        
        # Version control
        if any(term in exe_name or term in name_lower for term in [
            "git", "svn", "mercurial", "tortoise"
        ]):
            return "version_control"
        
        # Media players
        if any(term in exe_name or term in name_lower for term in [
            "vlc", "mpc", "media player", "winamp", "foobar", "potplayer"
        ]):
            return "media"
        
        # Compression tools
        if any(term in exe_name or term in name_lower for term in [
            "winrar", "7zip", "zip", "rar", "archive"
        ]):
            return "compression"
        
        # System tools
        if any(term in exe_name or term in path_lower for term in [
            "system32", "windows", "cmd", "powershell", "admin"
        ]):
            return "system"
        
        # Development tools
        if any(term in exe_name or term in name_lower for term in [
            "compiler", "debugger", "ide", "studio", "dev"
        ]):
            return "development"
        
        return "application"
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp as string"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    @safe_execute
    def export_config(self, export_path: str) -> bool:
        """Export configuration to a file"""
        try:
            export_data = {
                "version": "1.0",
                "export_date": self._get_current_timestamp(),
                "custom_applications": self.custom_apps
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration exported to {export_path}")
            return True
        except OSError as e:
            self.logger.error(f"Could not export configuration: {e}")
            return False
    
    @safe_execute
    def import_config(self, import_path: str, merge: bool = True) -> bool:
        """Import configuration from a file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_apps = data.get("custom_applications", {})
            
            if merge:
                # Merge with existing applications
                self.custom_apps.update(imported_apps)
            else:
                # Replace existing applications
                self.custom_apps = imported_apps
            
            self._save_config()
            self.logger.info(f"Configuration imported from {import_path}")
            return True
        except (json.JSONDecodeError, OSError) as e:
            self.logger.error(f"Could not import configuration: {e}")
            return False