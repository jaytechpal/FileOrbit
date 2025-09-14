"""
Error handling framework for FileOrbit
Provides specific exception types and error handling decorators
"""

import functools
import logging
from typing import Any, Callable, Optional, Type
from pathlib import Path


class FileOrbitException(Exception):
    """Base exception for all FileOrbit-specific errors"""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None, error_code: Optional[str] = None):
        super().__init__(message)
        self.original_error = original_error
        self.error_code = error_code
        self.message = message
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class RegistryAccessError(FileOrbitException):
    """Registry access operation failed"""
    pass


class ShellIntegrationError(FileOrbitException):
    """Shell integration operation failed"""
    pass


class IconExtractionError(FileOrbitException):
    """Icon extraction operation failed"""
    pass


class FileOperationError(FileOrbitException):
    """File system operation failed"""
    pass


class ConfigurationError(FileOrbitException):
    """Configuration or setup error"""
    pass


class ValidationError(FileOrbitException):
    """Data validation error"""
    pass


class NetworkError(FileOrbitException):
    """Network operation error"""
    pass


# Error handling decorators

def handle_registry_operation(func: Callable) -> Callable:
    """Decorator for registry operations with specific error handling"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        
        try:
            return func(*args, **kwargs)
        except OSError as e:
            error_msg = f"Registry access failed in {func.__name__}: {e}"
            logger.error(error_msg)
            raise RegistryAccessError(error_msg, original_error=e, error_code="REG001")
        except PermissionError as e:
            error_msg = f"Registry permission denied in {func.__name__}: {e}"
            logger.error(error_msg)
            raise RegistryAccessError(error_msg, original_error=e, error_code="REG002")
        except Exception as e:
            error_msg = f"Unexpected registry error in {func.__name__}: {e}"
            logger.error(error_msg)
            raise RegistryAccessError(error_msg, original_error=e, error_code="REG999")
    
    return wrapper


def handle_shell_operation(func: Callable) -> Callable:
    """Decorator for shell operations with specific error handling"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            error_msg = f"Shell executable not found in {func.__name__}: {e}"
            logger.error(error_msg)
            raise ShellIntegrationError(error_msg, original_error=e, error_code="SHELL001")
        except PermissionError as e:
            error_msg = f"Shell permission denied in {func.__name__}: {e}"
            logger.error(error_msg)
            raise ShellIntegrationError(error_msg, original_error=e, error_code="SHELL002")
        except TimeoutError as e:
            error_msg = f"Shell operation timeout in {func.__name__}: {e}"
            logger.error(error_msg)
            raise ShellIntegrationError(error_msg, original_error=e, error_code="SHELL003")
        except Exception as e:
            error_msg = f"Unexpected shell error in {func.__name__}: {e}"
            logger.error(error_msg)
            raise ShellIntegrationError(error_msg, original_error=e, error_code="SHELL999")
    
    return wrapper


def handle_icon_operation(func: Callable) -> Callable:
    """Decorator for icon operations with specific error handling"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            error_msg = f"Icon file not found in {func.__name__}: {e}"
            logger.error(error_msg)
            raise IconExtractionError(error_msg, original_error=e, error_code="ICON001")
        except OSError as e:
            error_msg = f"Icon extraction OS error in {func.__name__}: {e}"
            logger.error(error_msg)
            raise IconExtractionError(error_msg, original_error=e, error_code="ICON002")
        except Exception as e:
            error_msg = f"Unexpected icon error in {func.__name__}: {e}"
            logger.error(error_msg)
            raise IconExtractionError(error_msg, original_error=e, error_code="ICON999")
    
    return wrapper


def handle_file_operation(func: Callable) -> Callable:
    """Decorator for file operations with specific error handling"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            error_msg = f"File not found in {func.__name__}: {e}"
            logger.error(error_msg)
            raise FileOperationError(error_msg, original_error=e, error_code="FILE001")
        except PermissionError as e:
            error_msg = f"File permission denied in {func.__name__}: {e}"
            logger.error(error_msg)
            raise FileOperationError(error_msg, original_error=e, error_code="FILE002")
        except OSError as e:
            error_msg = f"File system error in {func.__name__}: {e}"
            logger.error(error_msg)
            raise FileOperationError(error_msg, original_error=e, error_code="FILE003")
        except Exception as e:
            error_msg = f"Unexpected file error in {func.__name__}: {e}"
            logger.error(error_msg)
            raise FileOperationError(error_msg, original_error=e, error_code="FILE999")
    
    return wrapper


def safe_execute(func: Callable, default_return: Any = None, log_errors: bool = True) -> Callable:
    """
    Safe execution wrapper that catches all exceptions and returns default value
    Use sparingly and only when you're sure errors can be ignored
    """
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if log_errors:
                logger = logging.getLogger(func.__module__)
                logger.warning(f"Safe execution caught error in {func.__name__}: {e}")
            return default_return
    
    return wrapper


# Validation helpers

def validate_path(path: Path, must_exist: bool = True, must_be_file: bool = False, must_be_dir: bool = False) -> None:
    """Validate path with specific requirements"""
    if not isinstance(path, Path):
        raise ValidationError(f"Expected Path object, got {type(path)}", error_code="VAL001")
    
    if must_exist and not path.exists():
        raise ValidationError(f"Path does not exist: {path}", error_code="VAL002")
    
    if must_be_file and not path.is_file():
        raise ValidationError(f"Path is not a file: {path}", error_code="VAL003")
    
    if must_be_dir and not path.is_dir():
        raise ValidationError(f"Path is not a directory: {path}", error_code="VAL004")


def validate_not_empty(value: Any, name: str = "value") -> None:
    """Validate that value is not empty"""
    if not value:
        raise ValidationError(f"{name} cannot be empty", error_code="VAL005")
    
    if isinstance(value, str) and not value.strip():
        raise ValidationError(f"{name} cannot be empty or whitespace", error_code="VAL006")


def validate_type(value: Any, expected_type: Type, name: str = "value") -> None:
    """Validate value type"""
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"{name} must be of type {expected_type.__name__}, got {type(value).__name__}",
            error_code="VAL007"
        )


# Error reporting utilities

class ErrorReporter:
    """Utility class for error reporting and aggregation"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def add_error(self, error: Exception, context: str = ""):
        """Add an error to the report"""
        self.errors.append({
            'error': error,
            'context': context,
            'type': type(error).__name__,
            'message': str(error)
        })
    
    def add_warning(self, message: str, context: str = ""):
        """Add a warning to the report"""
        self.warnings.append({
            'message': message,
            'context': context
        })
    
    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings"""
        return len(self.warnings) > 0
    
    def get_summary(self) -> str:
        """Get a summary of all errors and warnings"""
        summary = []
        
        if self.errors:
            summary.append(f"Errors ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                context = f" in {error['context']}" if error['context'] else ""
                summary.append(f"  {i}. {error['type']}: {error['message']}{context}")
        
        if self.warnings:
            summary.append(f"Warnings ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                context = f" in {warning['context']}" if warning['context'] else ""
                summary.append(f"  {i}. {warning['message']}{context}")
        
        return "\n".join(summary) if summary else "No errors or warnings"
    
    def clear(self):
        """Clear all errors and warnings"""
        self.errors.clear()
        self.warnings.clear()


# Usage examples and best practices
"""
Usage Examples:

1. Using decorators:
   
   @handle_registry_operation
   def get_file_type(self, file_path: Path) -> Dict[str, str]:
       # Registry operation code here
       pass

2. Using validation:
   
   def process_file(self, file_path: Path) -> None:
       validate_path(file_path, must_exist=True, must_be_file=True)
       validate_not_empty(file_path.name, "filename")
       # Process file

3. Using ErrorReporter:
   
   reporter = ErrorReporter()
   
   for file_path in file_paths:
       try:
           process_file(file_path)
       except FileOperationError as e:
           reporter.add_error(e, f"processing {file_path}")
   
   if reporter.has_errors():
       logger.error(reporter.get_summary())

Best Practices:

1. Always use specific exception types instead of generic Exception
2. Include original error and error codes for better debugging
3. Log errors at the appropriate level (error for failures, warning for recoverable issues)
4. Use validation functions at entry points to catch issues early
5. Use ErrorReporter for batch operations where you want to collect all errors
6. Don't catch exceptions you can't handle meaningfully
7. Re-raise exceptions with additional context when appropriate
"""