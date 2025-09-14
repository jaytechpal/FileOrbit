"""
Cross-Platform Tests for FileOrbit
Tests platform-specific functionality across Windows, macOS, and Linux
"""

import unittest
import platform
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from platform_config import get_platform_config
from src.utils.cross_platform_filesystem import get_cross_platform_fs
from src.services.cross_platform_app_discovery import get_application_discovery


class TestCrossPlatformConfiguration(unittest.TestCase):
    """Test cross-platform configuration detection"""
    
    def setUp(self):
        self.config = get_platform_config()
    
    def test_platform_detection(self):
        """Test that platform is correctly detected"""
        system = platform.system().lower()
        
        if system == 'windows':
            self.assertTrue(self.config.is_windows)
            self.assertFalse(self.config.is_macos)
            self.assertFalse(self.config.is_linux)
        elif system == 'darwin':
            self.assertFalse(self.config.is_windows)
            self.assertTrue(self.config.is_macos)
            self.assertFalse(self.config.is_linux)
        elif system == 'linux':
            self.assertFalse(self.config.is_windows)
            self.assertFalse(self.config.is_macos)
            self.assertTrue(self.config.is_linux)
    
    def test_architecture_detection(self):
        """Test that architecture is correctly detected"""
        self.assertIn(self.config.architecture, ['amd64', 'arm64', 'x86'])
        
        # Test 64-bit detection
        if platform.machine().endswith('64'):
            self.assertTrue(self.config.is_64bit)
        else:
            self.assertFalse(self.config.is_64bit)
    
    def test_directory_structure(self):
        """Test platform-specific directory configuration"""
        config_dir = self.config.get_config_directory()
        data_dir = self.config.get_data_directory()
        cache_dir = self.config.get_cache_directory()
        
        # All directories should exist after calling getters
        self.assertTrue(config_dir.exists())
        self.assertTrue(data_dir.exists())
        self.assertTrue(cache_dir.exists())
        
        # Test platform-specific paths
        if self.config.is_windows:
            self.assertIn('AppData', str(config_dir))
        elif self.config.is_macos:
            self.assertIn('Library', str(config_dir))
        else:  # Linux
            self.assertTrue(str(config_dir).endswith('fileorbit') or '.config' in str(config_dir))
    
    def test_feature_support(self):
        """Test feature support detection"""
        # Test universal features
        self.assertTrue(self.config.supports_feature('file_associations'))
        self.assertTrue(self.config.supports_feature('context_menus'))
        self.assertTrue(self.config.supports_feature('file_watching'))
        
        # Test platform-specific features
        if self.config.is_windows:
            self.assertTrue(self.config.supports_feature('registry'))
            self.assertTrue(self.config.supports_feature('recycle_bin'))
        elif self.config.is_macos:
            self.assertTrue(self.config.supports_feature('quick_look'))
            self.assertTrue(self.config.supports_feature('applescript'))
        elif self.config.is_linux:
            self.assertTrue(self.config.supports_feature('desktop_entries'))
            self.assertTrue(self.config.supports_feature('mime_types'))
    
    def test_performance_settings(self):
        """Test performance-related configuration"""
        buffer_size = self.config.get_optimal_buffer_size()
        max_ops = self.config.get_max_concurrent_operations()
        batch_size = self.config.get_directory_scan_batch_size()
        cache_size = self.config.get_cache_size_mb()
        
        # Validate reasonable values
        self.assertGreater(buffer_size, 0)
        self.assertGreaterEqual(max_ops, 2)
        self.assertGreater(batch_size, 0)
        self.assertGreater(cache_size, 0)
        
        # Test 64-bit optimizations
        if self.config.is_64bit:
            self.assertGreaterEqual(max_ops, 2)
            self.assertGreaterEqual(batch_size, 1000)
    
    def test_theme_colors(self):
        """Test theme color configuration"""
        colors = self.config.theme_colors
        
        self.assertIsInstance(colors, dict)
        self.assertIn('primary', colors)
        self.assertIn('background', colors)
        self.assertIn('text', colors)
        
        # Validate color format (should be hex)
        for color_name, color_value in colors.items():
            self.assertIsInstance(color_value, str)
            if color_value.startswith('#'):
                self.assertEqual(len(color_value), 7)  # #RRGGBB format


class TestCrossPlatformFilesystem(unittest.TestCase):
    """Test cross-platform filesystem operations"""
    
    def setUp(self):
        self.fs = get_cross_platform_fs()
        self.config = get_platform_config()
    
    def test_drive_detection(self):
        """Test cross-platform drive detection"""
        drives = self.fs.get_drives()
        
        self.assertIsInstance(drives, list)
        self.assertGreater(len(drives), 0)
        
        # Test drive structure
        for drive in drives:
            self.assertIn('path', drive)
            self.assertIn('label', drive)
            self.assertIn('type', drive)
            
            # Validate drive path exists
            drive_path = Path(drive['path'])
            self.assertTrue(drive_path.exists())
        
        # Platform-specific validations
        if self.config.is_windows:
            # Windows should have drive letters
            drive_paths = [d['path'] for d in drives]
            self.assertTrue(any(':' in path for path in drive_paths))
        else:
            # Unix-like should have root
            drive_paths = [d['path'] for d in drives]
            self.assertIn('/', drive_paths)
    
    def test_file_operations(self):
        """Test basic file operation support"""
        # Test that filesystem utilities are available
        self.assertTrue(hasattr(self.fs, 'get_drives'))
        self.assertTrue(hasattr(self.fs, 'get_file_associations'))
        self.assertTrue(hasattr(self.fs, 'move_to_trash'))


class TestCrossPlatformAppDiscovery(unittest.TestCase):
    """Test cross-platform application discovery"""
    
    def setUp(self):
        self.app_discovery = get_application_discovery()
        self.config = get_platform_config()
    
    def test_app_discovery_initialization(self):
        """Test application discovery initialization"""
        self.assertIsNotNone(self.app_discovery)
        self.assertIsNotNone(self.app_discovery.config)
        
        # Test that platform detection is consistent
        self.assertEqual(self.app_discovery.config.platform_name, self.config.platform_name)
    
    def test_platform_specific_discovery(self):
        """Test platform-specific discovery methods"""
        if self.config.is_windows:
            self.assertTrue(hasattr(self.app_discovery, '_scan_windows_registry'))
        elif self.config.is_macos:
            self.assertTrue(hasattr(self.app_discovery, '_scan_macos_applications'))
        else:  # Linux
            self.assertTrue(hasattr(self.app_discovery, '_scan_linux_desktop_files'))


class TestCrossPlatformIntegration(unittest.TestCase):
    """Integration tests for cross-platform components"""
    
    def test_component_initialization(self):
        """Test that all cross-platform components can be initialized"""
        try:
            config = get_platform_config()
            fs = get_cross_platform_fs()
            app_discovery = get_application_discovery()
            
            # All components should initialize successfully
            self.assertIsNotNone(config)
            self.assertIsNotNone(fs)
            self.assertIsNotNone(app_discovery)
            
        except Exception as e:
            self.fail(f"Cross-platform component initialization failed: {e}")
    
    def test_platform_consistency(self):
        """Test that platform detection is consistent across components"""
        config = get_platform_config()
        
        # All components should report the same platform
        components = [
            get_cross_platform_fs(),
            get_application_discovery(),
        ]
        
        for component in components:
            if hasattr(component, 'config'):
                self.assertEqual(component.config.platform_name, config.platform_name)
                self.assertEqual(component.config.is_windows, config.is_windows)
                self.assertEqual(component.config.is_macos, config.is_macos)
                self.assertEqual(component.config.is_linux, config.is_linux)
    
    def test_cross_platform_settings(self):
        """Test cross-platform settings structure"""
        config = get_platform_config()
        settings = config.get_platform_specific_settings()
        
        # All platforms should have these settings
        required_settings = [
            'platform', 'architecture', 'is_64bit',
            'shell_integration', 'context_menu_provider',
            'icon_provider', 'file_watcher', 'trash_implementation'
        ]
        
        for setting in required_settings:
            self.assertIn(setting, settings)
            self.assertIsNotNone(settings[setting])


def run_cross_platform_tests():
    """Run all cross-platform tests"""
    # Create test suite
    test_classes = [
        TestCrossPlatformConfiguration,
        TestCrossPlatformFilesystem,
        TestCrossPlatformAppDiscovery,
        TestCrossPlatformIntegration
    ]
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 60)
    print("FileOrbit Cross-Platform Compatibility Tests")
    print("=" * 60)
    
    success = run_cross_platform_tests()
    
    if success:
        print("\n✅ All cross-platform tests passed!")
        print("FileOrbit is ready for Windows, macOS, and Linux deployment.")
    else:
        print("\n❌ Some cross-platform tests failed.")
        print("Review the test output above for issues to fix.")
    
    exit(0 if success else 1)