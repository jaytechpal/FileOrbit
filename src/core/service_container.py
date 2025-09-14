"""
Service Container for Dependency Injection

This module provides a dependency injection container that manages service
registration, lifecycle, and resolution. It supports singleton and transient
services and enables plugin architecture and testability.
"""

from typing import Dict, Any, TypeVar, Type, Callable, List, Optional
import inspect
from threading import RLock

from src.utils.logger import get_logger
from src.core.interfaces import IServiceContainer


T = TypeVar('T')


class ServiceRegistration:
    """Represents a service registration."""
    
    def __init__(self, interface_type: Type, implementation: Any, 
                 lifecycle: str, factory: Optional[Callable] = None):
        self.interface_type = interface_type
        self.implementation = implementation
        self.lifecycle = lifecycle  # 'singleton' or 'transient'
        self.factory = factory
        self.instance = None  # For singleton caching


class ServiceContainer(IServiceContainer):
    """
    Dependency injection container with service registration and resolution.
    
    Features:
    - Singleton and transient service lifetimes
    - Automatic dependency resolution
    - Constructor injection
    - Service validation
    - Thread-safe operations
    - Plugin architecture support
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._services: Dict[Type, ServiceRegistration] = {}
        self._lock = RLock()
        self._resolution_stack: List[Type] = []  # For circular dependency detection
        
        # Register the container itself
        self.register_singleton(IServiceContainer, self)
        
        self.logger.info("ServiceContainer initialized")
    
    def register_singleton(self, interface_type: Type[T], implementation: Any):
        """
        Register a singleton service.
        
        Args:
            interface_type: The interface type
            implementation: The implementation instance or class
        """
        with self._lock:
            self._validate_registration(interface_type, implementation)
            
            registration = ServiceRegistration(
                interface_type=interface_type,
                implementation=implementation,
                lifecycle='singleton'
            )
            
            self._services[interface_type] = registration
            self.logger.debug(f"Registered singleton: {interface_type.__name__} -> {type(implementation).__name__}")
    
    def register_transient(self, interface_type: Type[T], implementation_factory: Callable[[], T]):
        """
        Register a transient service.
        
        Args:
            interface_type: The interface type
            implementation_factory: Factory function that creates instances
        """
        with self._lock:
            self._validate_factory(implementation_factory)
            
            registration = ServiceRegistration(
                interface_type=interface_type,
                implementation=None,
                lifecycle='transient',
                factory=implementation_factory
            )
            
            self._services[interface_type] = registration
            self.logger.debug(f"Registered transient: {interface_type.__name__}")
    
    def register_scoped(self, interface_type: Type[T], implementation_class: Type[T]):
        """
        Register a scoped service (creates new instance per resolution context).
        
        Args:
            interface_type: The interface type
            implementation_class: The implementation class
        """
        def factory():
            return self._create_instance(implementation_class)
        
        self.register_transient(interface_type, factory)
    
    def resolve(self, interface_type: Type[T]) -> T:
        """
        Resolve a service instance.
        
        Args:
            interface_type: The interface type to resolve
            
        Returns:
            Service instance
            
        Raises:
            ValueError: If service is not registered or circular dependency detected
        """
        with self._lock:
            # Check for circular dependencies
            if interface_type in self._resolution_stack:
                cycle = " -> ".join([t.__name__ for t in self._resolution_stack] + [interface_type.__name__])
                raise ValueError(f"Circular dependency detected: {cycle}")
            
            if interface_type not in self._services:
                raise ValueError(f"Service not registered: {interface_type.__name__}")
            
            registration = self._services[interface_type]
            
            try:
                self._resolution_stack.append(interface_type)
                
                if registration.lifecycle == 'singleton':
                    return self._resolve_singleton(registration)
                elif registration.lifecycle == 'transient':
                    return self._resolve_transient(registration)
                else:
                    raise ValueError(f"Unknown lifecycle: {registration.lifecycle}")
                    
            finally:
                self._resolution_stack.pop()
    
    def try_resolve(self, interface_type: Type[T]) -> Optional[T]:
        """
        Try to resolve a service instance without raising exceptions.
        
        Args:
            interface_type: The interface type to resolve
            
        Returns:
            Service instance or None if not registered
        """
        try:
            return self.resolve(interface_type)
        except Exception as e:
            self.logger.warning(f"Failed to resolve {interface_type.__name__}: {e}")
            return None
    
    def is_registered(self, interface_type: Type) -> bool:
        """
        Check if a service is registered.
        
        Args:
            interface_type: The interface type to check
            
        Returns:
            True if registered, False otherwise
        """
        with self._lock:
            return interface_type in self._services
    
    def get_registered_services(self) -> List[Type]:
        """
        Get list of registered service types.
        
        Returns:
            List of registered interface types
        """
        with self._lock:
            return list(self._services.keys())
    
    def unregister(self, interface_type: Type):
        """
        Unregister a service.
        
        Args:
            interface_type: The interface type to unregister
        """
        with self._lock:
            if interface_type in self._services:
                del self._services[interface_type]
                self.logger.debug(f"Unregistered service: {interface_type.__name__}")
    
    def clear(self):
        """Clear all registered services except the container itself."""
        with self._lock:
            # Keep the container registration
            container_reg = self._services.get(IServiceContainer)
            self._services.clear()
            if container_reg:
                self._services[IServiceContainer] = container_reg
            self.logger.info("Cleared all service registrations")
    
    def create_scope(self) -> 'ServiceContainer':
        """
        Create a new service container scope.
        
        Returns:
            New service container with copied registrations
        """
        scope = ServiceContainer()
        
        with self._lock:
            # Copy all registrations except singleton instances
            for interface_type, registration in self._services.items():
                if interface_type == IServiceContainer:
                    continue  # Don't copy container registration
                
                new_registration = ServiceRegistration(
                    interface_type=registration.interface_type,
                    implementation=registration.implementation,
                    lifecycle=registration.lifecycle,
                    factory=registration.factory
                )
                # Don't copy singleton instances - they'll be created fresh in the scope
                scope._services[interface_type] = new_registration
        
        self.logger.debug("Created new service container scope")
        return scope
    
    def get_service_info(self, interface_type: Type) -> Optional[Dict[str, Any]]:
        """
        Get information about a registered service.
        
        Args:
            interface_type: The interface type
            
        Returns:
            Service information dictionary or None
        """
        with self._lock:
            if interface_type not in self._services:
                return None
            
            registration = self._services[interface_type]
            return {
                'interface': interface_type.__name__,
                'implementation': type(registration.implementation).__name__ if registration.implementation else 'Factory',
                'lifecycle': registration.lifecycle,
                'has_instance': registration.instance is not None,
                'is_factory': registration.factory is not None
            }
    
    # Private methods
    
    def _validate_registration(self, interface_type: Type, implementation: Any):
        """Validate service registration."""
        if not interface_type:
            raise ValueError("Interface type cannot be None")
        
        if implementation is None:
            raise ValueError("Implementation cannot be None")
        
        # Check if implementation matches interface (basic check)
        if hasattr(interface_type, '__abstractmethods__'):
            # For abstract base classes, check if implementation implements the interface
            if inspect.isclass(implementation):
                if not issubclass(implementation, interface_type):
                    self.logger.warning(f"Implementation {implementation.__name__} does not inherit from {interface_type.__name__}")
            else:
                # For instances, check if they implement the interface methods
                missing_methods = []
                for method_name in interface_type.__abstractmethods__:
                    if not hasattr(implementation, method_name):
                        missing_methods.append(method_name)
                
                if missing_methods:
                    self.logger.warning(f"Implementation missing methods: {missing_methods}")
    
    def _validate_factory(self, factory: Callable):
        """Validate factory function."""
        if not callable(factory):
            raise ValueError("Factory must be callable")
    
    def _resolve_singleton(self, registration: ServiceRegistration):
        """Resolve a singleton service."""
        if registration.instance is None:
            if registration.factory:
                registration.instance = registration.factory()
            elif inspect.isclass(registration.implementation):
                registration.instance = self._create_instance(registration.implementation)
            else:
                registration.instance = registration.implementation
        
        return registration.instance
    
    def _resolve_transient(self, registration: ServiceRegistration):
        """Resolve a transient service."""
        if registration.factory:
            return registration.factory()
        elif inspect.isclass(registration.implementation):
            return self._create_instance(registration.implementation)
        else:
            return registration.implementation
    
    def _create_instance(self, class_type: Type):
        """Create an instance with dependency injection."""
        try:
            # Get constructor signature
            constructor = class_type.__init__
            sig = inspect.signature(constructor)
            
            # Resolve constructor parameters
            kwargs = {}
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                # Try to resolve parameter by type annotation
                if param.annotation != inspect.Parameter.empty:
                    param_type = param.annotation
                    if self.is_registered(param_type):
                        kwargs[param_name] = self.resolve(param_type)
                    elif param.default == inspect.Parameter.empty:
                        # Required parameter but not registered
                        self.logger.warning(f"Cannot resolve required parameter {param_name} of type {param_type}")
            
            # Create instance
            return class_type(**kwargs)
            
        except Exception as e:
            self.logger.error(f"Failed to create instance of {class_type.__name__}: {e}")
            # Fallback to parameterless constructor
            try:
                return class_type()
            except Exception as fallback_error:
                self.logger.error(f"Fallback constructor also failed: {fallback_error}")
                raise ValueError(f"Cannot create instance of {class_type.__name__}") from e