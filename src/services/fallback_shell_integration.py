"""
Fallback shell integration for unsupported platforms

Provides basic context menu functionality when platform-specific 
integrations are not available.
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import QWidget

from src.core.shell_integration_interfaces import IShellIntegrationProvider
from src.utils.logger import get_logger


class FallbackShellIntegration(IShellIntegrationProvider):
    """
    Fallback shell integration that provides basic functionality
    when platform-specific integrations are not available.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.logger.info("Using fallback shell integration")
    
    def get_context_menu_actions(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """
        Get basic context menu actions for selected files.
        """
        if not file_paths:
            return []
        
        actions = []
        first_file = file_paths[0]
        is_single_file = len(file_paths) == 1
        is_directory = first_file.is_dir()
        
        # Basic Open action
        if is_single_file:
            if is_directory:
                actions.append({
                    "text": "Open",
                    "action": "open",
                    "icon": "folder_open",
                    "bold": True
                })
                # Our custom action
                actions.append({
                    "text": "Open in New Tab",
                    "action": "open_in_new_tab",
                    "icon": "tab_new"
                })
            else:
                actions.append({
                    "text": "Open",
                    "action": "open",
                    "icon": "file_open",
                    "bold": True
                })
            
            actions.append({"separator": True})
        
        # Basic edit actions
        actions.extend([
            {
                "text": "Cut",
                "action": "cut",
                "icon": "cut"
            },
            {
                "text": "Copy",
                "action": "copy",
                "icon": "copy"
            }
        ])
        
        actions.append({"separator": True})
        
        # Delete action
        actions.append({
            "text": "Delete",
            "action": "delete",
            "icon": "delete"
        })
        
        actions.append({"separator": True})
        
        # Properties
        if is_single_file:
            actions.append({
                "text": "Properties",
                "action": "properties",
                "icon": "properties"
            })
        
        return actions
    
    def get_empty_area_context_menu(self, current_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        Get basic context menu for empty area.
        """
        return [
            {
                "text": "New Folder",
                "action": "new_folder",
                "icon": "folder_new"
            },
            {"separator": True},
            {
                "text": "Paste",
                "action": "paste",
                "icon": "paste"
            },
            {"separator": True},
            {
                "text": "Refresh",
                "action": "refresh",
                "icon": "refresh"
            }
        ]
    
    def execute_action(self, action_name: str, file_paths: List[Path], **kwargs) -> bool:
        """
        Execute basic actions.
        """
        try:
            if action_name == "open" and file_paths:
                # Try to open with system default
                for file_path in file_paths:
                    try:
                        # Try different commands based on what might be available
                        if subprocess.run(['xdg-open', str(file_path)]).returncode == 0:
                            continue
                    except FileNotFoundError:
                        try:
                            if subprocess.run(['open', str(file_path)]).returncode == 0:
                                continue
                        except FileNotFoundError:
                            try:
                                subprocess.run(['start', '', str(file_path)], shell=True)
                            except Exception:
                                self.logger.warning(f"Could not open {file_path}")
                return True
            
            elif action_name == "open_in_new_tab":
                # This will be handled by the main application
                return True
            
            elif action_name in ["cut", "copy", "paste", "delete", "rename", "new_folder", "refresh"]:
                # These will be handled by the main application
                return True
            
            else:
                self.logger.warning(f"Unsupported action: {action_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to execute action {action_name}: {e}")
            return False
    
    def get_default_applications(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Get basic default applications (empty for fallback).
        """
        return []
    
    def supports_trash(self) -> bool:
        """
        Fallback doesn't support trash.
        """
        return False
    
    def move_to_trash(self, file_paths: List[Path]) -> bool:
        """
        Fallback doesn't support trash.
        """
        return False
    
    def get_file_properties_dialog(self, file_path: Path, parent: QWidget) -> bool:
        """
        Fallback doesn't support properties dialog.
        """
        return False