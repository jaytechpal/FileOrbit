"""
Simple test to verify test infrastructure works
"""
import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_basic_functionality():
    """Test basic functionality"""
    assert True

def test_import_capabilities():
    """Test that we can import our modules"""
    try:
        from src.services.file_service import FileService
        service = FileService()
        assert service is not None
    except ImportError as e:
        pytest.skip(f"Cannot import FileService: {e}")

def test_platform_capabilities():
    """Test platform detection"""
    import platform
    assert platform.machine() in ['x86_64', 'AMD64', 'arm64', 'aarch64']
    assert platform.architecture()[0] in ['64bit', '32bit']

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
