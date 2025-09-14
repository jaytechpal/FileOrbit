"""
Windows Shell Compatibility Wrapper
Provides compatibility layer between existing WindowsShellIntegration and new cross-platform interface
"""

from pathlib import Path
from typing import List, Dict, Any

from src.utils.windows_shell import WindowsShellIntegration
from src.utils.logger import get_logger


class WindowsShell:
    """Windows shell integration wrapper for cross-platform compatibility"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.windows_shell = WindowsShellIntegration()
    
    def open_with_default_app(self, file_path: str) -> bool:
        """Open file with default application"""
        try:
            return self.windows_shell.open_with_system(Path(file_path))
        except Exception as e:
            self.logger.error(f"Error opening file with default app: {e}")
            return False
    
    def show_properties(self, file_path: str) -> bool:
        """Open file properties dialog"""
        try:
            return self.windows_shell.open_properties_dialog(Path(file_path))
        except Exception as e:
            self.logger.error(f"Error opening file properties: {e}")
            return False
    
    def show_in_explorer(self, file_path: str) -> bool:
        """Show file in Windows Explorer"""
        try:
            return self.windows_shell.show_in_explorer(Path(file_path))
        except Exception as e:
            self.logger.error(f"Error showing file in explorer: {e}")
            return False
    
    def move_to_trash(self, file_path: str) -> bool:
        """Move file to Recycle Bin"""
        try:
            return self.windows_shell.send_to_recycle_bin([Path(file_path)])
        except Exception as e:
            self.logger.error(f"Error moving file to trash: {e}")
            return False
    
    def create_shortcut(self, target_path: str, shortcut_path: str, 
                       description: str = "", working_dir: str = "") -> bool:
        """Create Windows shortcut"""
        try:
            return self.windows_shell.create_shortcut(Path(target_path), Path(shortcut_path))
        except Exception as e:
            self.logger.error(f"Error creating shortcut: {e}")
            return False
    
    def get_file_associations(self, file_extension: str) -> List[Dict[str, str]]:
        """Get file associations for extension"""
        try:
            # Create a dummy file path with the extension
            dummy_path = Path(f"dummy.{file_extension}")
            return self.windows_shell.get_open_with_programs(dummy_path)
        except Exception as e:
            self.logger.error(f"Error getting file associations: {e}")
            return []
    
    def open_with_app(self, file_path: str, app_path: str) -> bool:
        """Open file with specific application"""
        try:
            import subprocess
            result = subprocess.run([app_path, file_path], 
                                  capture_output=True, text=True, check=True)
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Error opening file with app: {e}")
            return False
    
    def get_context_menu_items(self, file_path: str) -> List[Dict[str, Any]]:
        """Get Windows context menu items"""
        try:
            # Get the comprehensive Windows context menu from the original implementation
            return self.windows_shell.get_context_menu_actions([Path(file_path)])
        except Exception as e:
            self.logger.error(f"Error getting context menu items: {e}")
            # Return basic fallback context menu
            return self._get_fallback_context_menu(file_path)
    
    def _get_fallback_context_menu(self, file_path: str) -> List[Dict[str, Any]]:
        """Get fallback context menu when Windows shell extensions fail"""
        try:
            file_path_obj = Path(file_path)
            actions = []
            
            if file_path_obj.is_dir():
                # Directory context menu
                actions.extend([
                    {
                        "text": "Open",
                        "icon": "folder_open",
                        "action": "open",
                        "bold": True
                    },
                    {
                        "text": "Open in new tab",
                        "icon": "tab_new", 
                        "action": "open_new_tab"
                    },
                    {"separator": True},
                    {
                        "text": "Cut",
                        "icon": "cut",
                        "action": "cut"
                    },
                    {
                        "text": "Copy",
                        "icon": "copy", 
                        "action": "copy"
                    },
                    {"separator": True},
                    {
                        "text": "Delete",
                        "icon": "delete",
                        "action": "delete"
                    },
                    {
                        "text": "Rename",
                        "icon": "rename",
                        "action": "rename"
                    },
                    {"separator": True},
                    {
                        "text": "Properties",
                        "icon": "properties",
                        "action": "properties"
                    }
                ])
            else:
                # File context menu
                default_program = self.windows_shell.get_default_program(file_path_obj)
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
                
                # Add Open With submenu
                open_with_programs = self.windows_shell.get_open_with_programs(file_path_obj)
                if open_with_programs:
                    actions.append({
                        "text": "Open with",
                        "icon": "app_extension",
                        "submenu": [
                            {
                                "text": program.get("name", "Unknown"),
                                "icon": program.get("icon", "app_extension"),
                                "action": f"open_with_{program.get('path', '')}",
                                "path": program.get("path", "")
                            } for program in open_with_programs[:10]  # Limit to 10 programs
                        ]
                    })
                
                actions.extend([
                    {"separator": True},
                    {
                        "text": "Cut",
                        "icon": "cut",
                        "action": "cut"
                    },
                    {
                        "text": "Copy",
                        "icon": "copy",
                        "action": "copy"
                    },
                    {"separator": True},
                    {
                        "text": "Delete", 
                        "icon": "delete",
                        "action": "delete"
                    },
                    {
                        "text": "Rename",
                        "icon": "rename", 
                        "action": "rename"
                    },
                    {"separator": True},
                    {
                        "text": "Properties",
                        "icon": "properties",
                        "action": "properties"
                    }
                ])
            
            return actions
            
        except Exception as e:
            self.logger.error(f"Error getting fallback context menu: {e}")
            return []
    
    def open_command_prompt_here(self, folder_path: str) -> bool:
        """Open Command Prompt at folder"""
        try:
            return self.windows_shell.open_command_prompt_here(Path(folder_path))
        except Exception as e:
            self.logger.error(f"Error opening command prompt: {e}")
            return False
    
    def open_powershell_here(self, folder_path: str) -> bool:
        """Open PowerShell at folder"""
        try:
            return self.windows_shell.open_powershell_here(Path(folder_path))
        except Exception as e:
            self.logger.error(f"Error opening PowerShell: {e}")
            return False
    
    def copy_path_to_clipboard(self, file_path: str) -> bool:
        """Copy file path to clipboard"""
        try:
            return self.windows_shell.copy_path_to_clipboard(Path(file_path))
        except Exception as e:
            self.logger.error(f"Error copying path to clipboard: {e}")
            return False
    
    def get_send_to_options(self) -> List[Dict[str, str]]:
        """Get Send To menu options"""
        try:
            return self.windows_shell.get_send_to_options()
        except Exception as e:
            self.logger.error(f"Error getting send to options: {e}")
            return []
    
    def execute_shell_extension(self, file_path: str, command: str) -> bool:
        """Execute shell extension command"""
        try:
            return self.windows_shell.execute_shell_extension(Path(file_path), command)
        except Exception as e:
            self.logger.error(f"Error executing shell extension: {e}")
            return False
    
    def get_file_type_info(self, file_path: str) -> Dict[str, str]:
        """Get file type information"""
        try:
            return self.windows_shell.get_file_type_info(Path(file_path))
        except Exception as e:
            self.logger.error(f"Error getting file type info: {e}")
            return {}
    
    def get_default_program(self, file_path: str) -> str:
        """Get default program for file"""
        try:
            result = self.windows_shell.get_default_program(Path(file_path))
            return result or ""
        except Exception as e:
            self.logger.error(f"Error getting default program: {e}")
            return ""
    
    def get_empty_area_context_menu(self) -> List[Dict[str, Any]]:
        """Get Windows context menu items for empty area (background)"""
        try:
            # Use the comprehensive Windows empty area context menu
            return self.windows_shell.get_empty_area_context_menu()
        except Exception as e:
            self.logger.error(f"Error getting empty area context menu: {e}")
            return self._get_fallback_empty_area_menu()
    
    def _get_fallback_empty_area_menu(self) -> List[Dict[str, Any]]:
        """Get fallback empty area menu when Windows shell fails"""
        return [
            {
                'text': 'Refresh',
                'action': 'refresh',
                'enabled': True
            },
            {'separator': True},
            {
                'text': 'New',
                'submenu': [
                    {
                        'text': 'Folder',
                        'action': 'new_folder',
                        'enabled': True
                    },
                    {
                        'text': 'Text Document',
                        'action': 'new_text_file',
                        'enabled': True
                    }
                ]
            },
            {'separator': True},
            {
                'text': 'Paste',
                'action': 'paste',
                'enabled': True
            },
            {'separator': True},
            {
                'text': 'Properties',
                'action': 'folder_properties',
                'enabled': True
            }
        ]