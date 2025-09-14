"""
Windows Shell Extension Provider - Coordinates shell extension discovery and caching
"""

from pathlib import Path
from typing import List, Dict, Optional
from src.utils.logger import get_logger
from src.config.constants import CacheConstants, PerformanceConstants
from src.services.windows_registry_reader import WindowsRegistryReader
from src.services.application_detector import ApplicationDetector
from src.utils.error_handling import ShellIntegrationError, safe_execute


class WindowsShellExtensionProvider:
    """Provides shell extensions with intelligent caching and filtering"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.registry_reader = WindowsRegistryReader()
        self.app_detector = ApplicationDetector()
        
        # Caches
        self._extension_cache = {}
        self._system_extensions_cache = None
        self._cache_timestamps = {}
    
    @safe_execute
    def get_shell_extensions_for_file(self, file_path: Path) -> List[Dict[str, str]]:
        """Get all applicable shell extensions for a specific file"""
        if not file_path.exists():
            return []
        
        # Check cache first
        cache_key = f"file_{file_path.suffix.lower()}"
        if self._is_cache_valid(cache_key):
            return self._extension_cache[cache_key]
        
        extensions = []
        
        if file_path.is_file():
            # Get extensions for this file type
            file_extensions = self.registry_reader.get_shell_extensions_for_extension(
                file_path.suffix.lower()
            )
            extensions.extend(file_extensions)
        
        # Add common system extensions that apply to all files/folders
        system_extensions = self.get_system_extensions()
        extensions.extend(system_extensions)
        
        # Enhance with application information
        enhanced_extensions = self._enhance_with_app_info(extensions)
        
        # Cache the result
        self._extension_cache[cache_key] = enhanced_extensions
        self._cache_timestamps[cache_key] = self._get_current_time()
        
        return enhanced_extensions
    
    @safe_execute
    def get_system_extensions(self) -> List[Dict[str, str]]:
        """Get system-wide shell extensions that apply to all items"""
        if self._system_extensions_cache is not None:
            return self._system_extensions_cache
        
        extensions = []
        
        # Get extensions for common system items
        common_types = ["*", "Directory", "Folder", "AllFilesystemObjects"]
        
        for type_name in common_types:
            try:
                type_extensions = self.registry_reader.get_shell_extensions_for_extension(type_name)
                extensions.extend(type_extensions)
            except Exception as e:
                self.logger.debug(f"Could not get extensions for {type_name}: {e}")
        
        # Remove duplicates based on command
        unique_extensions = self._deduplicate_extensions(extensions)
        
        # Cache the result
        self._system_extensions_cache = unique_extensions
        
        return unique_extensions
    
    @safe_execute
    def get_specialized_extensions(self) -> List[Dict[str, str]]:
        """Get specialized extensions for specific file types"""
        cache_key = "specialized"
        if self._is_cache_valid(cache_key):
            return self._extension_cache[cache_key]
        
        extensions = []
        
        # Get extensions for common file types
        common_extensions = [".txt", ".exe", ".jpg", ".mp4", ".pdf", ".zip"]
        
        for ext in common_extensions:
            try:
                ext_extensions = self.registry_reader.get_shell_extensions_for_extension(ext)
                extensions.extend(ext_extensions)
            except Exception as e:
                self.logger.debug(f"Could not get extensions for {ext}: {e}")
        
        # Deduplicate and enhance
        unique_extensions = self._deduplicate_extensions(extensions)
        enhanced_extensions = self._enhance_with_app_info(unique_extensions)
        
        # Cache the result
        self._extension_cache[cache_key] = enhanced_extensions
        self._cache_timestamps[cache_key] = self._get_current_time()
        
        return enhanced_extensions
    
    def _enhance_with_app_info(self, extensions: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Enhance extensions with application information"""
        enhanced = []
        
        for ext in extensions:
            enhanced_ext = ext.copy()
            
            # Extract executable path from command
            command = ext.get("command", "")
            if command:
                executable = self.app_detector.extract_executable_from_command(command)
                if executable:
                    enhanced_ext["executable"] = executable
                    
                    # Get application info
                    app_info = self.app_detector.get_application_info(executable)
                    enhanced_ext["app_info"] = app_info
                    
                    # Categorize the application
                    category = self.app_detector.categorize_application(
                        executable, 
                        ext.get("text", "")
                    )
                    enhanced_ext["category"] = category
                    
                    # Check if it's a system application
                    enhanced_ext["is_system"] = self.app_detector.is_system_application(executable)
            
            enhanced.append(enhanced_ext)
        
        return enhanced
    
    def _deduplicate_extensions(self, extensions: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Remove duplicate extensions based on command and text"""
        seen = set()
        unique = []
        
        for ext in extensions:
            # Create a key for deduplication
            key = (
                ext.get("text", "").lower().strip(),
                ext.get("command", "").lower().strip(),
                ext.get("action", "").lower().strip()
            )
            
            if key not in seen and all(key):  # Ensure no empty values
                seen.add(key)
                unique.append(ext)
        
        return unique
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if a cache entry is still valid"""
        if cache_key not in self._extension_cache:
            return False
        
        if cache_key not in self._cache_timestamps:
            return False
        
        current_time = self._get_current_time()
        cache_time = self._cache_timestamps[cache_key]
        
        # Check if cache has expired
        if current_time - cache_time > CacheConstants.SHELL_EXTENSIONS_CACHE_TIMEOUT:
            self._invalidate_cache_entry(cache_key)
            return False
        
        return True
    
    def _invalidate_cache_entry(self, cache_key: str):
        """Invalidate a specific cache entry"""
        self._extension_cache.pop(cache_key, None)
        self._cache_timestamps.pop(cache_key, None)
    
    def _get_current_time(self) -> float:
        """Get current time for cache timestamping"""
        import time
        return time.time()
    
    @safe_execute
    def refresh_cache(self):
        """Refresh all cached data"""
        self.logger.info("Refreshing shell extensions cache")
        
        # Clear all caches
        self._extension_cache.clear()
        self._cache_timestamps.clear()
        self._system_extensions_cache = None
        
        # Clear component caches
        self.registry_reader.clear_cache()
        self.app_detector.clear_cache()
        
        self.logger.info("Shell extensions cache refreshed")
    
    @safe_execute
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics for monitoring"""
        return {
            "extension_cache_size": len(self._extension_cache),
            "cached_timestamps": len(self._cache_timestamps),
            "system_extensions_cached": 1 if self._system_extensions_cache else 0,
            "max_cache_size": CacheConstants.SHELL_EXTENSIONS_CACHE_SIZE
        }
    
    def validate_extension(self, extension: Dict[str, str]) -> bool:
        """Validate that an extension is properly formed and executable"""
        if not extension.get("text") or not extension.get("command"):
            return False
        
        # Check if the executable exists
        executable = extension.get("executable")
        if executable:
            return self.app_detector.get_application_info(executable).get("exists", False)
        
        # If no executable info, try to extract it
        command = extension.get("command", "")
        if command:
            extracted_exe = self.app_detector.extract_executable_from_command(command)
            if extracted_exe:
                return self.app_detector.get_application_info(extracted_exe).get("exists", False)
        
        return True  # Assume valid if we can't determine otherwise