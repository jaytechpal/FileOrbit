"""
Platform Configuration for 64-bit FileOrbit
Optimizes settings based on system architecture and capabilities
"""

import sys
import platform
import psutil


class PlatformConfig:
    """64-bit optimized platform configuration"""
    
    def __init__(self):
        self.is_64bit = self._check_64bit_system()
        self.system_memory = self._get_system_memory()
        self.cpu_count = psutil.cpu_count(logical=True)
        self.platform_name = platform.system().lower()
        self.architecture = platform.machine().lower()
        
    def _check_64bit_system(self) -> bool:
        """Verify we're running on a 64-bit system"""
        return sys.maxsize > 2**32
    
    def _get_system_memory(self) -> int:
        """Get total system memory in GB"""
        return psutil.virtual_memory().total // (1024**3)
    
    def get_optimal_buffer_size(self, file_size: int = 0) -> int:
        """Get optimal buffer size based on system capabilities and file size"""
        if not self.is_64bit:
            return 1024 * 1024  # 1MB for 32-bit fallback
        
        # Base buffer size on available memory and file size
        base_buffer = 4 * 1024 * 1024  # 4MB base for 64-bit
        
        if self.system_memory >= 16:  # 16GB+ RAM
            if file_size > 10 * 1024**3:  # Files > 10GB
                return 32 * 1024 * 1024  # 32MB buffer
            elif file_size > 1024**3:  # Files > 1GB
                return 16 * 1024 * 1024  # 16MB buffer
            else:
                return 8 * 1024 * 1024   # 8MB buffer
        elif self.system_memory >= 8:  # 8GB+ RAM
            if file_size > 1024**3:  # Files > 1GB
                return 8 * 1024 * 1024   # 8MB buffer
            else:
                return base_buffer       # 4MB buffer
        else:  # < 8GB RAM
            return base_buffer // 2      # 2MB buffer
    
    def get_max_concurrent_operations(self) -> int:
        """Get maximum concurrent file operations based on system"""
        if not self.is_64bit:
            return 2  # Conservative for 32-bit
        
        # Base on CPU cores but cap reasonable limits
        max_ops = min(self.cpu_count, 8)
        
        # Adjust based on available memory
        if self.system_memory < 8:
            max_ops = min(max_ops, 4)
        elif self.system_memory >= 16:
            max_ops = min(max_ops + 2, 12)
            
        return max(max_ops, 2)  # Minimum 2 operations
    
    def get_directory_scan_batch_size(self) -> int:
        """Get optimal batch size for directory scanning"""
        if not self.is_64bit:
            return 1000
        
        # Larger batches for 64-bit systems with more memory
        if self.system_memory >= 16:
            return 10000
        elif self.system_memory >= 8:
            return 5000
        else:
            return 2000
    
    def supports_memory_mapping(self) -> bool:
        """Check if memory mapping is recommended for large files"""
        return self.is_64bit and self.system_memory >= 8
    
    def get_cache_size_mb(self) -> int:
        """Get recommended cache size in MB"""
        if not self.is_64bit:
            return 50  # 50MB for 32-bit
        
        # Scale cache based on available memory
        if self.system_memory >= 32:
            return 500  # 500MB for high-end systems
        elif self.system_memory >= 16:
            return 250  # 250MB for mid-range
        elif self.system_memory >= 8:
            return 100  # 100MB for 8GB systems
        else:
            return 50   # 50MB for lower memory
    
    def get_platform_specific_settings(self) -> dict:
        """Get platform-specific optimization settings"""
        settings = {
            'is_64bit': self.is_64bit,
            'buffer_size': self.get_optimal_buffer_size(),
            'max_concurrent_ops': self.get_max_concurrent_operations(),
            'batch_size': self.get_directory_scan_batch_size(),
            'cache_size_mb': self.get_cache_size_mb(),
            'supports_memory_mapping': self.supports_memory_mapping(),
            'system_memory_gb': self.system_memory,
            'cpu_cores': self.cpu_count,
            'platform': self.platform_name,
            'architecture': self.architecture
        }
        
        # Platform-specific tweaks
        if self.platform_name == 'windows':
            settings.update({
                'use_win32_apis': True,
                'file_attributes': True,
                'junction_support': True,
            })
        elif self.platform_name == 'darwin':
            settings.update({
                'use_foundation_apis': True,
                'spotlight_integration': True,
                'extended_attributes': True,
            })
        elif self.platform_name == 'linux':
            settings.update({
                'use_native_dialogs': True,
                'desktop_integration': True,
                'extended_attributes': True,
            })
        
        return settings


# Global platform configuration instance
platform_config = PlatformConfig()


def get_platform_config() -> PlatformConfig:
    """Get the global platform configuration instance"""
    return platform_config


def log_system_info():
    """Log system information for debugging"""
    config = get_platform_config()
    settings = config.get_platform_specific_settings()
    
    print("=== FileOrbit 64-bit System Information ===")
    print(f"64-bit System: {settings['is_64bit']}")
    print(f"Platform: {settings['platform']} ({settings['architecture']})")
    print(f"System Memory: {settings['system_memory_gb']} GB")
    print(f"CPU Cores: {settings['cpu_cores']}")
    print(f"Optimal Buffer Size: {settings['buffer_size'] // 1024 // 1024} MB")
    print(f"Max Concurrent Operations: {settings['max_concurrent_ops']}")
    print(f"Directory Scan Batch Size: {settings['batch_size']}")
    print(f"Cache Size: {settings['cache_size_mb']} MB")
    print(f"Memory Mapping Support: {settings['supports_memory_mapping']}")
    print("=" * 45)


if __name__ == "__main__":
    log_system_info()
