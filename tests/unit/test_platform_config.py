"""
Unit tests for platform configuration and 64-bit optimizations
"""
import sys
import platform
from unittest.mock import patch

from platform_config import PlatformConfig, get_platform_config


class TestPlatformConfig:
    """Test platform configuration and 64-bit detection"""
    
    def test_64bit_detection(self):
        """Test 64-bit system detection"""
        config = PlatformConfig()
        
        # Should detect 64-bit on modern systems
        expected_64bit = sys.maxsize > 2**32
        assert config.is_64bit == expected_64bit
    
    def test_system_memory_detection(self):
        """Test system memory detection"""
        config = PlatformConfig()
        
        # Should return reasonable memory amount (> 0)
        assert config.system_memory > 0
        assert isinstance(config.system_memory, int)
    
    def test_cpu_count_detection(self):
        """Test CPU core count detection"""
        config = PlatformConfig()
        
        # Should return reasonable CPU count
        assert config.cpu_count > 0
        assert config.cpu_count <= 128  # Reasonable upper bound
    
    def test_platform_detection(self):
        """Test platform name detection"""
        config = PlatformConfig()
        
        expected_platform = platform.system().lower()
        assert config.platform_name == expected_platform
        assert config.architecture.lower() in ['amd64', 'x86_64', 'arm64', 'aarch64']
    
    @patch('psutil.virtual_memory')
    def test_buffer_size_calculation_small_system(self, mock_memory):
        """Test buffer size calculation for small memory systems"""
        # Mock 4GB system
        mock_memory.return_value.total = 4 * 1024**3
        
        config = PlatformConfig()
        
        # Small file buffer
        buffer_size = config.get_optimal_buffer_size(100 * 1024)  # 100KB file
        assert buffer_size == 2 * 1024 * 1024  # 2MB for small systems
    
    @patch('psutil.virtual_memory')
    def test_buffer_size_calculation_large_system(self, mock_memory):
        """Test buffer size calculation for large memory systems"""
        # Mock 32GB system
        mock_memory.return_value.total = 32 * 1024**3
        
        config = PlatformConfig()
        
        # Large file buffer
        buffer_size = config.get_optimal_buffer_size(10 * 1024**3)  # 10GB file
        assert buffer_size == 32 * 1024 * 1024  # 32MB for large files on high-memory systems
    
    @patch('psutil.virtual_memory')
    @patch('psutil.cpu_count')
    def test_concurrent_operations_scaling(self, mock_cpu, mock_memory):
        """Test concurrent operations scaling based on system specs"""
        mock_cpu.return_value = 8  # 8 CPU cores
        mock_memory.return_value.total = 16 * 1024**3  # 16GB
        
        config = PlatformConfig()
        max_ops = config.get_max_concurrent_operations()
        
        # Should scale with CPU cores but be reasonable
        assert 2 <= max_ops <= 12
        assert max_ops <= 8 + 2  # CPU cores + some buffer
    
    def test_memory_mapping_support(self):
        """Test memory mapping support detection"""
        config = PlatformConfig()
        
        # Should be True for 64-bit systems with sufficient memory
        if config.is_64bit and config.system_memory >= 8:
            assert config.supports_memory_mapping() is True
        else:
            assert config.supports_memory_mapping() is False
    
    @patch('psutil.virtual_memory')
    def test_cache_size_calculation(self, mock_memory):
        """Test cache size calculation based on memory"""
        # Test different memory configurations
        test_cases = [
            (4 * 1024**3, 50),    # 4GB -> 50MB cache
            (8 * 1024**3, 100),   # 8GB -> 100MB cache
            (16 * 1024**3, 250),  # 16GB -> 250MB cache
            (32 * 1024**3, 500),  # 32GB -> 500MB cache
        ]
        
        for memory_bytes, expected_cache_mb in test_cases:
            mock_memory.return_value.total = memory_bytes
            config = PlatformConfig()
            
            cache_size = config.get_cache_size_mb()
            assert cache_size == expected_cache_mb
    
    def test_platform_specific_settings_windows(self):
        """Test Windows-specific settings"""
        with patch('platform.system', return_value='Windows'):
            config = PlatformConfig()
            settings = config.get_platform_specific_settings()
            
            assert settings['platform'] == 'windows'
            assert 'use_win32_apis' in settings
            assert 'file_attributes' in settings
            assert 'junction_support' in settings
    
    def test_platform_specific_settings_macos(self):
        """Test macOS-specific settings"""
        with patch('platform.system', return_value='Darwin'):
            config = PlatformConfig()
            settings = config.get_platform_specific_settings()
            
            assert settings['platform'] == 'darwin'
            assert 'use_foundation_apis' in settings
            assert 'spotlight_integration' in settings
            assert 'extended_attributes' in settings
    
    def test_platform_specific_settings_linux(self):
        """Test Linux-specific settings"""
        with patch('platform.system', return_value='Linux'):
            config = PlatformConfig()
            settings = config.get_platform_specific_settings()
            
            assert settings['platform'] == 'linux'
            assert 'use_native_dialogs' in settings
            assert 'desktop_integration' in settings
            assert 'extended_attributes' in settings
    
    def test_directory_scan_batch_size(self):
        """Test directory scan batch size calculation"""
        config = PlatformConfig()
        batch_size = config.get_directory_scan_batch_size()
        
        if config.is_64bit:
            assert batch_size >= 2000
            assert batch_size <= 10000
        else:
            assert batch_size == 1000
    
    def test_global_config_instance(self):
        """Test global configuration instance"""
        config1 = get_platform_config()
        config2 = get_platform_config()
        
        # Should return the same instance
        assert config1 is config2
        assert isinstance(config1, PlatformConfig)


class TestPlatformConfigPerformance:
    """Performance tests for platform configuration"""
    
    def test_config_initialization_speed(self, benchmark):
        """Test platform config initialization performance"""
        def create_config():
            return PlatformConfig()
        
        result = benchmark(create_config)
        assert isinstance(result, PlatformConfig)
    
    def test_settings_generation_speed(self, benchmark):
        """Test platform settings generation performance"""
        config = PlatformConfig()
        
        def get_settings():
            return config.get_platform_specific_settings()
        
        result = benchmark(get_settings)
        assert isinstance(result, dict)
        assert 'is_64bit' in result


class TestPlatformConfigEdgeCases:
    """Test edge cases and error conditions"""
    
    @patch('sys.maxsize', 2**31 - 1)  # Simulate 32-bit system
    def test_32bit_system_detection(self):
        """Test behavior on 32-bit systems"""
        config = PlatformConfig()
        assert config.is_64bit is False
        
        # Should use conservative settings
        buffer_size = config.get_optimal_buffer_size()
        assert buffer_size == 1024 * 1024  # 1MB
        
        max_ops = config.get_max_concurrent_operations()
        assert max_ops == 2  # Conservative for 32-bit
    
    @patch('psutil.virtual_memory')
    def test_low_memory_system(self, mock_memory):
        """Test behavior on very low memory systems"""
        # Mock 2GB system
        mock_memory.return_value.total = 2 * 1024**3
        
        config = PlatformConfig()
        
        # Should handle gracefully
        cache_size = config.get_cache_size_mb()
        assert cache_size >= 50  # Minimum cache
        
        max_ops = config.get_max_concurrent_operations()
        assert max_ops >= 2  # Minimum operations
    
    @patch('psutil.cpu_count')
    def test_single_core_system(self, mock_cpu):
        """Test behavior on single-core systems"""
        mock_cpu.return_value = 1
        
        config = PlatformConfig()
        max_ops = config.get_max_concurrent_operations()
        
        # Should still allow at least 2 operations
        assert max_ops >= 2
    
    @patch('platform.system')
    def test_unknown_platform(self, mock_platform):
        """Test behavior on unknown platforms"""
        mock_platform.return_value = 'UnknownOS'
        
        config = PlatformConfig()
        settings = config.get_platform_specific_settings()
        
        # Should have basic settings
        assert 'is_64bit' in settings
        assert 'platform' in settings
        assert settings['platform'] == 'unknownos'
