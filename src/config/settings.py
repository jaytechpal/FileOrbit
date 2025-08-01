"""
Application configuration management
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from PySide6.QtCore import QSettings


class AppConfig:
    """Application configuration manager"""
    
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"
        self.qt_settings = QSettings("FileOrbit", "FileOrbit")
        
        # Default configuration
        self.defaults = {
            "appearance": {
                "theme": "dark",
                "font_family": "Segoe UI",
                "font_size": 10,
                "show_hidden_files": False,
                "dual_pane_mode": True
            },
            "behavior": {
                "confirm_delete": True,
                "auto_refresh": True,
                "remember_tabs": True,
                "single_click_open": False
            },
            "window": {
                "geometry": None,
                "state": None,
                "maximized": False
            },
            "panels": {
                "left_path": str(Path.home()),
                "right_path": str(Path.home()),
                "active_panel": "left"
            },
            "file_operations": {
                "copy_buffer_size": 1024 * 1024,  # 1MB
                "show_progress": True,
                "verify_checksums": False
            }
        }
        
        self.config = self._load_config()
    
    def _get_config_dir(self) -> Path:
        """Get application configuration directory"""
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', '')) / "FileOrbit"
        else:  # Linux/Mac
            config_dir = Path.home() / ".config" / "fileorbit"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # Merge with defaults
                config = self.defaults.copy()
                self._deep_merge(config, loaded_config)
                return config
                
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}")
        
        return self.defaults.copy()
    
    def _deep_merge(self, base_dict: Dict, update_dict: Dict):
        """Deep merge two dictionaries"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_merge(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        try:
            return self.config.get(section, {}).get(key, default)
        except (KeyError, AttributeError):
            return default
    
    def set(self, section: str, key: str, value: Any):
        """Set configuration value"""
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.config.get(section, {})
    
    def set_section(self, section: str, values: Dict[str, Any]):
        """Set entire configuration section"""
        self.config[section] = values
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.defaults.copy()
        self.save()
    
    def get_theme_settings(self) -> Dict[str, Any]:
        """Get theme-related settings"""
        return {
            "theme": self.get("appearance", "theme", "dark"),
            "font_family": self.get("appearance", "font_family", "Segoe UI"),
            "font_size": self.get("appearance", "font_size", 10)
        }
