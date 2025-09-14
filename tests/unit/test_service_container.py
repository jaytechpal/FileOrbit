"""
Unit tests for the ServiceContainer

This module demonstrates the testing framework and provides comprehensive
tests for the dependency injection container.
"""

import pytest
from unittest.mock import Mock

from tests.test_framework import TestBase, unit_test
from src.core.service_container import ServiceContainer
from src.core.interfaces import IIconProvider, IContextMenuProvider


class TestServiceContainer(TestBase):
    """Test cases for ServiceContainer."""
    
    def setup_method(self):
        """Set up test environment."""
        super().setup_method()
        self.container = ServiceContainer()
    
    @unit_test
    def test_container_initialization(self):
        """Test container initializes correctly."""
        assert self.container is not None
        assert self.container.is_registered(type(self.container))
    
    @unit_test
    def test_register_singleton_service(self):
        """Test registering a singleton service."""
        # Arrange
        mock_service = Mock(spec=IIconProvider)
        
        # Act
        self.container.register_singleton(IIconProvider, mock_service)
        
        # Assert
        assert self.container.is_registered(IIconProvider)
        resolved_service = self.container.resolve(IIconProvider)
        assert resolved_service is mock_service
    
    @unit_test
    def test_register_transient_service(self):
        """Test registering a transient service."""
        # Arrange
        def factory():
            return Mock(spec=IContextMenuProvider)
        
        # Act
        self.container.register_transient(IContextMenuProvider, factory)
        
        # Assert
        assert self.container.is_registered(IContextMenuProvider)
        service1 = self.container.resolve(IContextMenuProvider)
        service2 = self.container.resolve(IContextMenuProvider)
        
        # Transient services should be different instances
        assert service1 is not service2
    
    @unit_test
    def test_singleton_returns_same_instance(self):
        """Test singleton services return same instance."""
        # Arrange
        mock_service = Mock(spec=IIconProvider)
        self.container.register_singleton(IIconProvider, mock_service)
        
        # Act
        service1 = self.container.resolve(IIconProvider)
        service2 = self.container.resolve(IIconProvider)
        
        # Assert
        assert service1 is service2
        assert service1 is mock_service
    
    @unit_test
    def test_resolve_unregistered_service_raises_error(self):
        """Test resolving unregistered service raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Service not registered"):
            self.container.resolve(IIconProvider)
    
    @unit_test
    def test_try_resolve_unregistered_service_returns_none(self):
        """Test try_resolve returns None for unregistered service."""
        # Act
        result = self.container.try_resolve(IIconProvider)
        
        # Assert
        assert result is None
    
    @unit_test
    def test_unregister_service(self):
        """Test unregistering a service."""
        # Arrange
        mock_service = Mock(spec=IIconProvider)
        self.container.register_singleton(IIconProvider, mock_service)
        assert self.container.is_registered(IIconProvider)
        
        # Act
        self.container.unregister(IIconProvider)
        
        # Assert
        assert not self.container.is_registered(IIconProvider)
    
    @unit_test
    def test_get_registered_services(self):
        """Test getting list of registered services."""
        # Arrange
        mock_icon_service = Mock(spec=IIconProvider)
        mock_menu_service = Mock(spec=IContextMenuProvider)
        
        initial_count = len(self.container.get_registered_services())
        
        # Act
        self.container.register_singleton(IIconProvider, mock_icon_service)
        self.container.register_singleton(IContextMenuProvider, mock_menu_service)
        
        # Assert
        services = self.container.get_registered_services()
        assert len(services) == initial_count + 2
        assert IIconProvider in services
        assert IContextMenuProvider in services
    
    @unit_test
    def test_clear_services(self):
        """Test clearing all services."""
        # Arrange
        mock_service = Mock(spec=IIconProvider)
        self.container.register_singleton(IIconProvider, mock_service)
        
        # Act
        self.container.clear()
        
        # Assert
        # Should only have the container itself registered
        services = self.container.get_registered_services()
        assert len(services) == 1
        assert not self.container.is_registered(IIconProvider)
    
    @unit_test
    def test_get_service_info(self):
        """Test getting service information."""
        # Arrange
        mock_service = Mock(spec=IIconProvider)
        self.container.register_singleton(IIconProvider, mock_service)
        
        # Act
        info = self.container.get_service_info(IIconProvider)
        
        # Assert
        assert info is not None
        assert info['interface'] == 'IIconProvider'
        assert info['lifecycle'] == 'singleton'
        assert 'implementation' in info
    
    @unit_test
    def test_create_scope(self):
        """Test creating a service container scope."""
        # Arrange
        mock_service = Mock(spec=IIconProvider)
        self.container.register_singleton(IIconProvider, mock_service)
        
        # Act
        scope = self.container.create_scope()
        
        # Assert
        assert scope is not self.container
        assert scope.is_registered(IIconProvider)
        
        # Services in scope should be independent
        scope_service = scope.resolve(IIconProvider)
        original_service = self.container.resolve(IIconProvider)
        
        # Different instances due to scope separation
        assert scope_service is not original_service


class MockService:
    """Mock service class for testing class-based registration."""
    
    def __init__(self, dependency: IIconProvider = None):
        self.dependency = dependency


class TestServiceContainerDependencyInjection(TestBase):
    """Test dependency injection capabilities."""
    
    def setup_method(self):
        """Set up test environment."""
        super().setup_method()
        self.container = ServiceContainer()
    
    @unit_test
    def test_register_class_with_dependency_injection(self):
        """Test registering a class with automatic dependency injection."""
        # Arrange
        mock_dependency = Mock(spec=IIconProvider)
        self.container.register_singleton(IIconProvider, mock_dependency)
        
        # Act
        self.container.register_scoped(MockService, MockService)
        service = self.container.resolve(MockService)
        
        # Assert
        assert service is not None
        assert isinstance(service, MockService)
        assert service.dependency is mock_dependency
    
    @unit_test
    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies."""
        # This test would require setting up classes with circular dependencies
        # For now, we'll test the basic mechanism
        
        # Create a factory that tries to resolve the same service
        def circular_factory():
            return self.container.resolve(IIconProvider)
        
        # Register the service with circular dependency
        self.container.register_transient(IIconProvider, circular_factory)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Circular dependency detected"):
            self.container.resolve(IIconProvider)