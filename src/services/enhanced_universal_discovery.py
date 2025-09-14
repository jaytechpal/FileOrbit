"""
Enhanced Universal Application Discovery
Provides cross-platform application discovery with Windows registry integration
"""

from typing import Dict, List, Optional

from platform_config import get_platform_config
from src.utils.logger import get_logger
from src.services.cross_platform_app_discovery import get_application_discovery

# Import Windows-specific discovery if available
try:
    from src.services.universal_registry_discovery import UniversalRegistryDiscovery
    HAS_WINDOWS_REGISTRY = True
except ImportError:
    HAS_WINDOWS_REGISTRY = False


class EnhancedUniversalDiscovery:
    """Enhanced application discovery with cross-platform support"""
    
    def __init__(self):
        self.config = get_platform_config()
        self.logger = get_logger(__name__)
        self.cross_platform_discovery = get_application_discovery()
        
        # Initialize Windows registry discovery if available
        self.windows_registry_discovery = None
        if HAS_WINDOWS_REGISTRY and self.config.is_windows:
            try:
                self.windows_registry_discovery = UniversalRegistryDiscovery()
            except Exception as e:
                self.logger.warning(f"Failed to initialize Windows registry discovery: {e}")
    
    def discover_all_installed_applications(self) -> Dict[str, Dict[str, str]]:
        """Discover all installed applications across all platforms"""
        applications = {}
        
        try:
            # Use cross-platform discovery
            cross_platform_apps = self.cross_platform_discovery.discover_applications()
            
            # Convert to legacy format for compatibility
            for app_info in cross_platform_apps:
                app_key = app_info.name.lower().replace(' ', '_')
                applications[app_key] = {
                    'name': app_info.name,
                    'executable': app_info.executable,
                    'install_path': app_info.install_path or '',
                    'icon': app_info.icon or '',
                    'version': app_info.version or '',
                    'description': app_info.description or '',
                    'exists': app_info.exists,
                    'platform': app_info.platform,
                    'bundle_id': getattr(app_info, 'bundle_id', ''),
                    'desktop_file': getattr(app_info, 'desktop_file', ''),
                }
            
            # Add Windows registry discovery if available
            if self.windows_registry_discovery and self.config.is_windows:
                try:
                    registry_apps = self.windows_registry_discovery.discover_all_installed_applications()
                    # Merge with cross-platform results, preferring registry data
                    for app_key, app_data in registry_apps.items():
                        if app_key not in applications:
                            applications[app_key] = app_data
                        else:
                            # Merge data, preferring non-empty registry values
                            merged_data = applications[app_key].copy()
                            for key, value in app_data.items():
                                if value and (not merged_data.get(key) or key in ['executable', 'install_path']):
                                    merged_data[key] = value
                            applications[app_key] = merged_data
                except Exception as e:
                    self.logger.warning(f"Windows registry discovery failed: {e}")
            
            self.logger.info(f"Discovered {len(applications)} total applications")
            
        except Exception as e:
            self.logger.error(f"Error during enhanced application discovery: {e}")
        
        return applications
    
    def find_application_by_name(self, app_name: str) -> Optional[Dict[str, str]]:
        """Find application by name across all platforms"""
        # Try cross-platform discovery first
        app_info = self.cross_platform_discovery.find_application(app_name)
        if app_info:
            return {
                'name': app_info.name,
                'executable': app_info.executable,
                'install_path': app_info.install_path or '',
                'icon': app_info.icon or '',
                'version': app_info.version or '',
                'exists': app_info.exists,
                'platform': app_info.platform
            }
        
        # Fallback to Windows registry if available
        if self.windows_registry_discovery and self.config.is_windows:
            try:
                all_apps = self.windows_registry_discovery.discover_all_installed_applications()
                app_key = app_name.lower().replace(' ', '_')
                if app_key in all_apps:
                    return all_apps[app_key]
                
                # Try partial matching
                for key, app_data in all_apps.items():
                    if app_name.lower() in app_data.get('name', '').lower():
                        return app_data
            except Exception as e:
                self.logger.debug(f"Registry lookup failed: {e}")
        
        return None
    
    def get_applications_by_type(self, app_type: str) -> List[Dict[str, str]]:
        """Get applications by type"""
        try:
            app_infos = self.cross_platform_discovery.get_applications_by_type(app_type)
            return [
                {
                    'name': app_info.name,
                    'executable': app_info.executable,
                    'install_path': app_info.install_path or '',
                    'icon': app_info.icon or '',
                    'version': app_info.version or '',
                    'exists': app_info.exists,
                    'platform': app_info.platform
                }
                for app_info in app_infos
            ]
        except Exception as e:
            self.logger.error(f"Error getting applications by type: {e}")
            return []
    
    def discover_shell_extensions(self) -> Dict[str, Dict[str, str]]:
        """Discover shell extensions (Windows-specific)"""
        if self.windows_registry_discovery and self.config.is_windows:
            try:
                return self.windows_registry_discovery.discover_all_shell_extensions()
            except Exception as e:
                self.logger.error(f"Error discovering shell extensions: {e}")
        
        return {}
    
    def discover_context_menu_handlers(self) -> Dict[str, Dict[str, str]]:
        """Discover context menu handlers (Windows-specific)"""
        if self.windows_registry_discovery and self.config.is_windows:
            try:
                return self.windows_registry_discovery.discover_all_context_menu_handlers()
            except Exception as e:
                self.logger.error(f"Error discovering context menu handlers: {e}")
        
        return {}
    
    def refresh_cache(self):
        """Refresh all cached data"""
        try:
            # Refresh cross-platform cache
            self.cross_platform_discovery.cache_dirty = True
            self.cross_platform_discovery.discover_applications(force_refresh=True)
            
            # Refresh Windows registry cache if available
            if hasattr(self.windows_registry_discovery, '_applications_cache'):
                self.windows_registry_discovery._applications_cache = {}
                self.windows_registry_discovery._shell_extensions_cache = {}
                self.windows_registry_discovery._context_menus_cache = {}
                
        except Exception as e:
            self.logger.error(f"Error refreshing cache: {e}")
    
    def get_statistics(self) -> Dict[str, int]:
        """Get discovery statistics"""
        stats = {
            'total_applications': 0,
            'platform_applications': 0,
            'registry_applications': 0,
            'shell_extensions': 0,
            'context_handlers': 0
        }
        
        try:
            # Cross-platform stats
            cross_platform_apps = self.cross_platform_discovery.discover_applications()
            stats['platform_applications'] = len(cross_platform_apps)
            stats['total_applications'] = len(cross_platform_apps)
            
            # Windows registry stats
            if self.windows_registry_discovery and self.config.is_windows:
                try:
                    registry_apps = self.windows_registry_discovery.discover_all_installed_applications()
                    shell_extensions = self.windows_registry_discovery.discover_all_shell_extensions()
                    context_handlers = self.windows_registry_discovery.discover_all_context_menu_handlers()
                    
                    stats['registry_applications'] = len(registry_apps)
                    stats['shell_extensions'] = len(shell_extensions)
                    stats['context_handlers'] = len(context_handlers)
                    
                    # Total unique applications
                    all_apps = set(app_info.name.lower() for app_info in cross_platform_apps)
                    all_apps.update(app_data.get('name', '').lower() for app_data in registry_apps.values())
                    stats['total_applications'] = len(all_apps)
                    
                except Exception as e:
                    self.logger.debug(f"Error getting Windows stats: {e}")
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
        
        return stats


# Global instance
enhanced_discovery = EnhancedUniversalDiscovery()


def get_enhanced_discovery() -> EnhancedUniversalDiscovery:
    """Get the global enhanced discovery instance"""
    return enhanced_discovery