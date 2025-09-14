"""
Context Menu Builder - Constructs context menus with proper ordering and formatting
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from src.utils.logger import get_logger
from src.config.constants import ShellConstants, FilterConstants
from src.utils.error_handling import safe_execute


class WindowsContextMenuBuilder:
    """Builds context menus with Windows Explorer-like behavior"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    @safe_execute
    def build_context_menu(self, 
                          file_path: Path, 
                          shell_extensions: List[Dict[str, str]],
                          add_custom_actions: bool = True) -> List[Dict[str, Any]]:
        """Build a complete context menu for a file/folder"""
        actions = []
        
        # Add default open actions first
        if add_custom_actions:
            actions.extend(self._get_default_actions(file_path))
        
        # Process and add shell extensions
        filtered_extensions = self._filter_extensions(shell_extensions)
        prioritized_extensions = self._prioritize_extensions(filtered_extensions)
        
        for extension in prioritized_extensions:
            action = self._extension_to_action(extension, file_path)
            if action:
                actions.append(action)
        
        # Add separators at appropriate positions
        actions = self._add_separators(actions)
        
        return actions
    
    def _get_default_actions(self, file_path: Path) -> List[Dict[str, Any]]:
        """Get default open actions for a file/folder"""
        actions = []
        
        if file_path.is_file():
            actions.append({
                "text": "Open",
                "action": "open",
                "command": f'"{file_path}"',
                "icon": "open",
                "priority": ShellConstants.PRIORITY_OPEN_ACTIONS
            })
            
            actions.append({
                "text": "Open with...",
                "action": "open_with", 
                "command": f'rundll32.exe shell32.dll,OpenAs_RunDLL "{file_path}"',
                "icon": "open_with",
                "priority": ShellConstants.PRIORITY_OPEN_ACTIONS + 1
            })
        else:
            actions.append({
                "text": "Open",
                "action": "open",
                "command": f'explorer.exe "{file_path}"',
                "icon": "folder",
                "priority": ShellConstants.PRIORITY_OPEN_ACTIONS
            })
        
        return actions
    
    def _filter_extensions(self, extensions: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Filter out unwanted or system-only extensions"""
        filtered = []
        
        for ext in extensions:
            text = ext.get("text", "").lower().strip()
            command = ext.get("command", "").lower()
            
            # Skip empty or invalid entries
            if not text or len(text) < FilterConstants.MIN_TEXT_LENGTH:
                continue
            
            # Skip system resource references that we want to filter
            if text.startswith('@'):
                # Check if it's in our system resource mappings
                resolved_text = self._resolve_system_resource(text)
                if not resolved_text:  # Empty means skip
                    continue
                ext["text"] = resolved_text
            
            # Skip unwanted patterns
            if any(pattern in text for pattern in FilterConstants.FILTER_PATTERNS):
                continue
            
            # Skip certain prefixes
            if any(text.startswith(prefix) for prefix in FilterConstants.FILTER_PREFIXES):
                continue
            
            # Skip if command contains certain unwanted applications
            if any(unwanted in command for unwanted in ['wsl.exe', 'ms-']):
                continue
            
            filtered.append(ext)
        
        return filtered
    
    def _prioritize_extensions(self, extensions: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Sort extensions by priority for proper menu ordering"""
        def get_priority(ext):
            return self._calculate_extension_priority(ext)
        
        return sorted(extensions, key=get_priority)
    
    def _calculate_extension_priority(self, extension: Dict[str, str]) -> int:
        """Calculate priority value for an extension"""
        text = extension.get("text", "").lower()
        action_type = extension.get("action", "").lower()
        
        # Check priority map for exact matches
        priority_map = self._get_priority_map()
        
        # Exact text match
        if text in priority_map:
            return priority_map[text]
        
        # Exact action match
        if action_type in priority_map:
            return priority_map[action_type]
        
        # Pattern matching for known application types
        for keyword, priority in priority_map.items():
            if keyword != "separator" and keyword in text:
                return priority
        
        # Check for priority application patterns
        if any(pattern in text for pattern in ShellConstants.PRIORITY_APP_PATTERNS):
            return ShellConstants.PRIORITY_CODE_EDITORS
        
        return ShellConstants.PRIORITY_DEFAULT
    
    def _get_priority_map(self) -> Dict[str, int]:
        """Get the priority mapping for different action types"""
        return {
            # Core Windows Explorer actions first
            "open": ShellConstants.PRIORITY_OPEN_ACTIONS,
            "open_with": ShellConstants.PRIORITY_OPEN_ACTIONS + 1,
            
            # Git operations
            "git": ShellConstants.PRIORITY_GIT_OPERATIONS,
            "open git gui here": ShellConstants.PRIORITY_GIT_OPERATIONS + 1,
            "open git bash here": ShellConstants.PRIORITY_GIT_OPERATIONS + 2,
            
            # Text editors
            "open with code": ShellConstants.PRIORITY_CODE_EDITORS,
            "open with sublime text": ShellConstants.PRIORITY_CODE_EDITORS + 1,
            "open powershell here": ShellConstants.PRIORITY_CODE_EDITORS + 2,
            
            # File operations
            "cut": ShellConstants.PRIORITY_FILE_OPERATIONS,
            "copy": ShellConstants.PRIORITY_FILE_OPERATIONS + 1,
            "create shortcut": ShellConstants.PRIORITY_FILE_OPERATIONS + 2,
            "delete": ShellConstants.PRIORITY_FILE_OPERATIONS + 3,
            "rename": ShellConstants.PRIORITY_FILE_OPERATIONS + 4,
            
            # Third-party applications
            "add to vlc media player's playlist": ShellConstants.PRIORITY_THIRD_PARTY_APPS,
            "find": ShellConstants.PRIORITY_THIRD_PARTY_APPS + 1,
            "send to": ShellConstants.PRIORITY_THIRD_PARTY_APPS + 2,
            "add to mpc-hc playlist": ShellConstants.PRIORITY_THIRD_PARTY_APPS + 3,
            
            # System actions
            "properties": ShellConstants.PRIORITY_SYSTEM_ACTIONS,
        }
    
    def _extension_to_action(self, extension: Dict[str, str], file_path: Path) -> Optional[Dict[str, Any]]:
        """Convert a shell extension to an action definition"""
        text = extension.get("text", "")
        command = extension.get("command", "")
        action = extension.get("action", "")
        
        if not text or not command:
            return None
        
        return {
            "text": text,
            "action": action,
            "command": command,
            "priority": self._calculate_extension_priority(extension),
            "registry_path": extension.get("registry_path", ""),
            "executable": self._extract_executable_from_command(command)
        }
    
    def _add_separators(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add separators at appropriate positions in the context menu"""
        if not actions:
            return actions
        
        result = []
        last_priority_group = None
        
        for action in actions:
            priority = action.get("priority", ShellConstants.PRIORITY_DEFAULT)
            current_group = self._get_priority_group(priority)
            
            # Add separator if we're moving to a new priority group
            if last_priority_group is not None and current_group != last_priority_group:
                result.append({
                    "separator": True,
                    "priority": priority - 1
                })
            
            result.append(action)
            last_priority_group = current_group
        
        return result
    
    def _get_priority_group(self, priority: int) -> str:
        """Get the priority group name for a given priority value"""
        if priority <= ShellConstants.PRIORITY_OPEN_ACTIONS + 10:
            return "open_actions"
        elif priority <= ShellConstants.PRIORITY_GIT_OPERATIONS + 10:
            return "git_operations"
        elif priority <= ShellConstants.PRIORITY_CODE_EDITORS + 10:
            return "code_editors"
        elif priority <= ShellConstants.PRIORITY_FILE_OPERATIONS + 50:
            return "file_operations"
        elif priority <= ShellConstants.PRIORITY_THIRD_PARTY_APPS + 100:
            return "third_party_apps"
        else:
            return "system_actions"
    
    def _resolve_system_resource(self, resource_ref: str) -> str:
        """Resolve system resource references like @shell32.dll,-8506"""
        return ShellConstants.SYSTEM_RESOURCE_MAPPINGS.get(resource_ref, resource_ref)
    
    def _extract_executable_from_command(self, command: str) -> Optional[str]:
        """Extract executable path from a command string"""
        if not command:
            return None
        
        # Handle quoted paths
        if command.startswith('"'):
            end_quote = command.find('"', 1)
            if end_quote != -1:
                return command[1:end_quote]
        
        # Simple space split for unquoted paths
        return command.split()[0] if command.split() else None