# FileOrbit Code Refactoring Plan

## Executive Summary

This document outlines a comprehensive refactoring strategy for FileOrbit to improve code maintainability, readability, and extensibility for future feature development.

## Current Code Analysis

### Critical Issues Identified

#### 1. **Single Responsibility Principle Violations**
- **WindowsShellIntegration**: 1,413 lines, 20+ methods handling registry access, shell extensions, context menus, and file operations
- **FilePanel**: 1,992 lines combining UI management, icon handling, context menus, navigation, and file operations

#### 2. **Code Smells**
- **Magic Numbers**: 40+ hardcoded values (100ms delays, 400px dimensions, priority numbers)
- **Overly Broad Exception Handling**: 25+ `except Exception:` blocks without specific error types
- **Hardcoded Paths**: Registry paths, application paths scattered throughout code
- **Method Length**: Several methods exceed 50 lines (context menu building, icon extraction)

#### 3. **Architecture Issues**
- **Tight Coupling**: Direct dependencies between UI and Windows-specific code
- **No Dependency Injection**: Hard to test and extend
- **Missing Abstractions**: No interfaces for platform-specific implementations
- **Configuration Scattered**: Settings and constants mixed with business logic

## Refactoring Strategy

### Phase 1: Core Infrastructure (High Priority)

#### 1.1 Create Configuration Management System
```python
# src/config/constants.py
class UIConstants:
    REFRESH_DELAY_MS = 100
    MIN_DIALOG_WIDTH = 400
    MIN_DIALOG_HEIGHT = 300
    DEFAULT_WINDOW_WIDTH = 1400
    DEFAULT_WINDOW_HEIGHT = 800

class ShellConstants:
    PRIORITY_OPEN_ACTIONS = 1
    PRIORITY_FILE_OPERATIONS = 100
    PRIORITY_THIRD_PARTY_APPS = 200
    PRIORITY_SYSTEM_ACTIONS = 900

class PathConstants:
    COMMON_PROGRAM_PATHS = {
        "vlc": [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
        ],
        "sublime": [
            r"C:\Program Files\Sublime Text\sublime_text.exe",
            r"C:\Program Files (x86)\Sublime Text\sublime_text.exe"
        ]
    }
```

#### 1.2 Implement Error Handling Framework
```python
# src/utils/error_handling.py
class FileOrbitException(Exception):
    """Base exception for FileOrbit"""
    pass

class RegistryAccessError(FileOrbitException):
    """Registry access failed"""
    pass

class ShellIntegrationError(FileOrbitException):
    """Shell integration operation failed"""
    pass

class IconExtractionError(FileOrbitException):
    """Icon extraction failed"""
    pass

def handle_registry_operation(func):
    """Decorator for registry operations with specific error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OSError as e:
            logger.error(f"Registry access failed: {e}")
            raise RegistryAccessError(f"Cannot access registry: {e}")
        except Exception as e:
            logger.error(f"Unexpected registry error: {e}")
            raise RegistryAccessError(f"Registry operation failed: {e}")
    return wrapper
```

### Phase 2: Decompose WindowsShellIntegration (Medium Priority)

#### 2.1 Split into Specialized Classes
```python
# src/shell/interfaces.py
from abc import ABC, abstractmethod

class IShellExtensionProvider(ABC):
    @abstractmethod
    def get_extensions_for_file(self, file_path: Path) -> List[Dict[str, str]]:
        pass

class IRegistryReader(ABC):
    @abstractmethod
    def get_file_type_info(self, file_path: Path) -> Dict[str, str]:
        pass

class IContextMenuBuilder(ABC):
    @abstractmethod
    def build_context_menu(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        pass

# src/shell/registry_reader.py
class WindowsRegistryReader(IRegistryReader):
    """Handles all Windows registry operations"""
    
    @handle_registry_operation
    def get_file_type_info(self, file_path: Path) -> Dict[str, str]:
        # Implementation with specific error handling
        pass

    @handle_registry_operation
    def get_shell_extensions(self, extension: str) -> List[Dict[str, str]]:
        # Implementation
        pass

# src/shell/shell_extension_provider.py
class WindowsShellExtensionProvider(IShellExtensionProvider):
    """Provides shell extensions from registry and common applications"""
    
    def __init__(self, registry_reader: IRegistryReader, app_detector: IApplicationDetector):
        self.registry_reader = registry_reader
        self.app_detector = app_detector

# src/shell/context_menu_builder.py
class WindowsContextMenuBuilder(IContextMenuBuilder):
    """Builds Windows Explorer-style context menus"""
    
    def __init__(self, extension_provider: IShellExtensionProvider, prioritizer: IMenuPrioritizer):
        self.extension_provider = extension_provider
        self.prioritizer = prioritizer
```

#### 2.2 Create Application Detection Service
```python
# src/services/application_detector.py
class ApplicationDetector:
    """Detects installed applications and their capabilities"""
    
    def __init__(self, config: PathConstants):
        self.config = config
        self._app_cache = {}
    
    def find_application(self, app_name: str) -> Optional[Path]:
        """Find application executable by name"""
        if app_name in self._app_cache:
            return self._app_cache[app_name]
        
        paths = self.config.COMMON_PROGRAM_PATHS.get(app_name, [])
        for path in paths:
            if Path(path).exists():
                self._app_cache[app_name] = Path(path)
                return Path(path)
        
        return None
    
    def get_application_capabilities(self, app_path: Path) -> Dict[str, Any]:
        """Get application capabilities (file types, icon, etc.)"""
        pass
```

### Phase 3: Decompose FilePanel (Medium Priority)

#### 3.1 Extract Icon Management
```python
# src/ui/components/icon_manager.py
class IconManager:
    """Handles all icon-related operations"""
    
    def __init__(self, app_detector: ApplicationDetector, config: UIConstants):
        self.app_detector = app_detector
        self.config = config
        self._icon_cache = {}
    
    def get_application_icon(self, app_name: str) -> QIcon:
        """Get icon for application"""
        if app_name in self._icon_cache:
            return self._icon_cache[app_name]
        
        # Try system extraction
        app_path = self.app_detector.find_application(app_name)
        if app_path:
            icon = self._extract_exe_icon(app_path)
            if icon and not icon.isNull():
                self._icon_cache[app_name] = icon
                return icon
        
        # Fallback to system icons
        return self._get_fallback_icon(app_name)
    
    def get_file_icon(self, file_path: Path) -> QIcon:
        """Get icon for file"""
        pass
```

#### 3.2 Extract Context Menu Handling
```python
# src/ui/components/context_menu_handler.py
class ContextMenuHandler:
    """Handles context menu creation and actions"""
    
    def __init__(self, menu_builder: IContextMenuBuilder, icon_manager: IconManager):
        self.menu_builder = menu_builder
        self.icon_manager = icon_manager
    
    def create_file_context_menu(self, file_paths: List[Path], parent: QWidget) -> QMenu:
        """Create context menu for files"""
        actions = self.menu_builder.build_context_menu(file_paths)
        return self._build_qt_menu(actions, parent)
    
    def _build_qt_menu(self, actions: List[Dict[str, Any]], parent: QWidget) -> QMenu:
        """Convert action definitions to QMenu"""
        menu = QMenu(parent)
        
        for action_def in actions:
            if action_def.get("separator"):
                menu.addSeparator()
            else:
                action = self._create_menu_action(action_def, parent)
                menu.addAction(action)
        
        return menu
```

#### 3.3 Extract Navigation Management
```python
# src/ui/components/navigation_manager.py
class NavigationManager:
    """Handles navigation history and path management"""
    
    def __init__(self):
        self.history = []
        self.current_index = -1
    
    def navigate_to(self, path: Path) -> bool:
        """Navigate to path and update history"""
        if self._can_navigate_to(path):
            self._add_to_history(path)
            return True
        return False
    
    def can_go_back(self) -> bool:
        """Check if can go back"""
        return self.current_index > 0
    
    def can_go_forward(self) -> bool:
        """Check if can go forward"""
        return self.current_index < len(self.history) - 1
```

### Phase 4: Implement Dependency Injection (Low Priority)

#### 4.1 Create Service Container
```python
# src/core/container.py
class ServiceContainer:
    """Simple dependency injection container"""
    
    def __init__(self):
        self._services = {}
        self._singletons = {}
    
    def register(self, interface_type, implementation_type, singleton=False):
        """Register service implementation"""
        self._services[interface_type] = (implementation_type, singleton)
    
    def resolve(self, service_type):
        """Resolve service instance"""
        if service_type in self._singletons:
            return self._singletons[service_type]
        
        if service_type in self._services:
            impl_type, is_singleton = self._services[service_type]
            instance = impl_type()
            
            if is_singleton:
                self._singletons[service_type] = instance
            
            return instance
        
        raise ValueError(f"Service {service_type} not registered")

# src/core/bootstrap.py
def configure_services() -> ServiceContainer:
    """Configure all services"""
    container = ServiceContainer()
    
    # Register services
    container.register(IRegistryReader, WindowsRegistryReader, singleton=True)
    container.register(IShellExtensionProvider, WindowsShellExtensionProvider)
    container.register(IContextMenuBuilder, WindowsContextMenuBuilder)
    
    return container
```

### Phase 5: Testing Infrastructure (High Priority)

#### 5.1 Create Test Framework
```python
# tests/test_registry_reader.py
import pytest
from unittest.mock import Mock, patch
from src.shell.registry_reader import WindowsRegistryReader

class TestWindowsRegistryReader:
    def setup_method(self):
        self.registry_reader = WindowsRegistryReader()
    
    @patch('winreg.OpenKey')
    def test_get_file_type_info_success(self, mock_open_key):
        # Arrange
        mock_key = Mock()
        mock_open_key.return_value.__enter__.return_value = mock_key
        
        # Act & Assert
        result = self.registry_reader.get_file_type_info(Path("test.txt"))
        assert result["extension"] == ".txt"
    
    @patch('winreg.OpenKey', side_effect=OSError("Registry error"))
    def test_get_file_type_info_registry_error(self, mock_open_key):
        # Act & Assert
        with pytest.raises(RegistryAccessError):
            self.registry_reader.get_file_type_info(Path("test.txt"))
```

## Implementation Roadmap

### Week 1-2: Foundation
1. Create configuration management system
2. Implement error handling framework
3. Set up testing infrastructure
4. Create service interfaces

### Week 3-4: Shell Integration Refactoring
1. Split WindowsShellIntegration into specialized classes
2. Implement dependency injection for shell services
3. Create application detection service
4. Add comprehensive tests

### Week 5-6: UI Component Refactoring
1. Extract IconManager from FilePanel
2. Extract ContextMenuHandler from FilePanel
3. Extract NavigationManager from FilePanel
4. Refactor FilePanel to use new components

### Week 7-8: Integration and Testing
1. Integrate all new components
2. Comprehensive testing
3. Performance optimization
4. Documentation updates

## Benefits of Refactoring

### Immediate Benefits
- **Improved Maintainability**: Smaller, focused classes easier to understand and modify
- **Better Testability**: Isolated components can be unit tested effectively
- **Reduced Coupling**: Clear interfaces between components
- **Consistent Error Handling**: Specific exceptions for different error scenarios

### Long-term Benefits
- **Easier Feature Addition**: New shell extensions or UI components can be added with minimal impact
- **Platform Portability**: Abstract interfaces allow for macOS/Linux implementations
- **Plugin Architecture**: Foundation for plugin system in future versions
- **Better Performance**: Caching and lazy loading can be added to each component independently

## Risk Mitigation

### Backward Compatibility
- Maintain existing public APIs during transition
- Implement feature toggles for new vs old implementations
- Comprehensive regression testing

### Gradual Migration
- Refactor one component at a time
- Keep old implementation alongside new until fully tested
- Use adapter pattern to bridge old and new code

## Success Metrics

- **Code Metrics**: Reduce average class size from 1,000+ lines to <300 lines
- **Test Coverage**: Achieve >80% code coverage for core components
- **Cyclomatic Complexity**: Reduce average method complexity from 10+ to <5
- **Bug Reports**: Track reduction in shell integration and icon-related bugs
- **Development Velocity**: Measure time to implement new features before/after refactoring