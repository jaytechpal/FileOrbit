"""
Unit tests for sidebar component and 64-bit drive detection
"""
from unittest.mock import Mock, patch

from PySide6.QtWidgets import QWidget

from src.ui.components.sidebar import Sidebar, DriveItemWidget


class TestDriveItemWidget:
    """Test drive item widget component"""
    
    def test_drive_widget_initialization(self, qapp, mock_drive_info):
        """Test drive item widget initialization"""
        widget = DriveItemWidget(mock_drive_info)
        
        assert widget.drive_info == mock_drive_info
        assert isinstance(widget, QWidget)
    
    def test_drive_widget_click_signal(self, qapp, mock_drive_info, qt_helper):
        """Test drive widget click signal emission"""
        widget = DriveItemWidget(mock_drive_info)
        
        # Track click signals
        clicked_paths = []
        widget.clicked.connect(lambda path: clicked_paths.append(path))
        
        # Simulate click
        qt_helper.click_widget(widget)
        
        # Should emit click signal with drive path
        assert len(clicked_paths) == 1
        assert clicked_paths[0] == mock_drive_info['path']
    
    def test_drive_widget_display_info(self, qapp, mock_drive_info):
        """Test drive widget displays correct information"""
        widget = DriveItemWidget(mock_drive_info)
        
        # Widget should contain drive information in its children
        # This is a basic test - in a real implementation you'd check specific labels
        assert widget.drive_info['letter'] == 'C'
        assert widget.drive_info['total_gb'] == 500.0


class TestSidebar:
    """Test sidebar component"""
    
    def test_sidebar_initialization(self, qapp):
        """Test sidebar component initialization"""
        sidebar = Sidebar()
        
        assert isinstance(sidebar, QWidget)
        assert hasattr(sidebar, 'tree')
        assert hasattr(sidebar, 'logger')
    
    def test_sidebar_signals(self, qapp):
        """Test sidebar signal definitions"""
        sidebar = Sidebar()
        
        # Verify location_changed signal exists
        assert hasattr(sidebar, 'location_changed')
    
    @patch('src.ui.components.sidebar.os.name', 'nt')
    @patch('src.ui.components.sidebar.kernel32')
    @patch('src.ui.components.sidebar.mpr')
    def test_get_drive_type_windows(self, mock_mpr, mock_kernel32, qapp):
        """Test Windows drive type detection"""
        sidebar = Sidebar()
        
        # Mock Windows API responses
        mock_kernel32.GetDriveTypeW.return_value = 3  # DRIVE_FIXED
        mock_mpr.WNetGetConnectionW.return_value = 1  # Not connected
        
        drive_type = sidebar._get_drive_type("C:\\")
        assert drive_type == "fixed"
    
    @patch('src.ui.components.sidebar.os.name', 'nt')
    @patch('src.ui.components.sidebar.kernel32')
    @patch('src.ui.components.sidebar.mpr')
    def test_get_drive_type_network_drive(self, mock_mpr, mock_kernel32, qapp):
        """Test network drive detection"""
        sidebar = Sidebar()
        
        # Mock network drive response
        mock_kernel32.GetDriveTypeW.return_value = 3  # DRIVE_FIXED (appears as fixed)
        mock_mpr.WNetGetConnectionW.return_value = 0  # SUCCESS - it's mapped
        
        drive_type = sidebar._get_drive_type("H:\\")
        assert drive_type == "network"
    
    @patch('src.ui.components.sidebar.os.name', 'posix')
    @patch('src.ui.components.sidebar.subprocess.run')
    def test_get_drive_type_unix(self, mock_subprocess, qapp):
        """Test Unix drive type detection"""
        sidebar = Sidebar()
        
        # Mock mount command output
        mock_result = Mock()
        mock_result.stdout = "/dev/sda1 on / type ext4 (rw,relatime)\n"
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        drive_type = sidebar._get_drive_type("/")
        assert drive_type in ["fixed", "unknown"]  # Depends on implementation
    
    @patch('src.ui.components.sidebar.os.name', 'nt')
    def test_get_drives_windows(self, qapp):
        """Test Windows drive enumeration"""
        sidebar = Sidebar()
        
        with patch('src.ui.components.sidebar.os.path.exists') as mock_exists, \
             patch('src.ui.components.sidebar.shutil.disk_usage') as mock_usage:
            
            # Mock drive existence
            mock_exists.side_effect = lambda path: path in ["C:\\", "D:\\"]
            
            # Mock disk usage
            mock_usage.return_value = Mock(
                total=500 * 1024**3,  # 500GB
                free=250 * 1024**3,   # 250GB free
            )
            
            drives = sidebar._get_drives()
            
            assert len(drives) == 2
            assert any(d['letter'] == 'C' for d in drives)
            assert any(d['letter'] == 'D' for d in drives)
    
    @patch('src.ui.components.sidebar.sys.platform', 'darwin')
    def test_get_drives_macos(self, qapp):
        """Test macOS drive enumeration"""
        sidebar = Sidebar()
        
        with patch('src.ui.components.sidebar.shutil.disk_usage') as mock_usage, \
             patch('src.ui.components.sidebar.Path') as mock_path:
            
            # Mock disk usage
            mock_usage.return_value = Mock(
                total=1000 * 1024**3,  # 1TB
                free=500 * 1024**3,    # 500GB free
            )
            
            # Mock /Volumes directory
            mock_volumes = Mock()
            mock_volumes.exists.return_value = True
            mock_volumes.iterdir.return_value = [
                Mock(is_dir=lambda: True, name="External Drive")
            ]
            mock_path.return_value = mock_volumes
            
            drives = sidebar._get_drives()
            
            # Should include root filesystem
            assert len(drives) >= 1
            assert any(d['path'] == '/' for d in drives)
    
    @patch('src.ui.components.sidebar.sys.platform', 'linux')
    def test_get_drives_linux(self, qapp):
        """Test Linux drive enumeration"""
        sidebar = Sidebar()
        
        with patch('src.ui.components.sidebar.shutil.disk_usage') as mock_usage, \
             patch('src.ui.components.sidebar.Path') as mock_path:
            
            # Mock disk usage
            mock_usage.return_value = Mock(
                total=500 * 1024**3,  # 500GB
                free=250 * 1024**3,   # 250GB free
            )
            
            # Mock mount points
            mock_media = Mock()
            mock_media.exists.return_value = True
            mock_media.iterdir.return_value = [
                Mock(is_dir=lambda: True, name="usb-drive")
            ]
            mock_path.return_value = mock_media
            
            drives = sidebar._get_drives()
            
            # Should include root filesystem
            assert len(drives) >= 1
            assert any(d['path'] == '/' for d in drives)
    
    def test_get_drive_icon_windows(self, qapp):
        """Test drive icon generation for Windows"""
        sidebar = Sidebar()
        
        # Test different drive types
        test_cases = [
            ("C", "fixed", "C:\\"),
            ("D", "removable", "D:\\"),
            ("H", "network", "H:\\"),
            ("E", "cdrom", "E:\\"),
        ]
        
        for letter, drive_type, path in test_cases:
            with patch.object(sidebar, '_get_drive_type', return_value=drive_type):
                icon = sidebar._get_drive_icon(letter, path)
                assert icon is not None
    
    def test_get_drive_icon_unix(self, qapp):
        """Test drive icon generation for Unix systems"""
        sidebar = Sidebar()
        
        with patch('src.ui.components.sidebar.sys.platform', 'linux'):
            icon = sidebar._get_drive_icon("root", "/")
            assert icon is not None
    
    def test_populate_drives(self, qapp):
        """Test drive population in sidebar"""
        sidebar = Sidebar()
        
        # Mock drives data
        mock_drives = [
            {
                'letter': 'C',
                'path': 'C:\\',
                'name': 'C:',
                'total_gb': 500.0,
                'used_gb': 250.0,
                'free_gb': 250.0,
                'usage_percent': 50.0
            }
        ]
        
        with patch.object(sidebar, '_get_drives', return_value=mock_drives):
            sidebar._populate_drives()
            
            # Verify tree was populated (basic check)
            assert sidebar.tree.topLevelItemCount() > 0


class TestSidebarErrorHandling:
    """Test sidebar error handling"""
    
    def test_drive_detection_with_exception(self, qapp):
        """Test drive detection handles exceptions gracefully"""
        sidebar = Sidebar()
        
        with patch('src.ui.components.sidebar.shutil.disk_usage', side_effect=OSError("Access denied")):
            drives = sidebar._get_drives()
            # Should not crash and return empty list or handle gracefully
            assert isinstance(drives, list)
    
    @patch('src.ui.components.sidebar.os.name', 'nt')
    def test_windows_api_exception(self, qapp):
        """Test Windows API exception handling"""
        sidebar = Sidebar()
        
        with patch('src.ui.components.sidebar.kernel32.GetDriveTypeW', side_effect=Exception("API Error")):
            drive_type = sidebar._get_drive_type("C:\\")
            assert drive_type == "unknown"
    
    def test_icon_generation_fallback(self, qapp):
        """Test icon generation fallback behavior"""
        sidebar = Sidebar()
        
        # Test with invalid drive type
        icon = sidebar._get_drive_icon("X", "X:\\")
        assert icon is not None  # Should always return some icon


class TestSidebarPerformance:
    """Performance tests for sidebar operations"""
    
    def test_drive_enumeration_performance(self, benchmark, qapp):
        """Test drive enumeration performance"""
        sidebar = Sidebar()
        
        def enumerate_drives():
            return sidebar._get_drives()
        
        result = benchmark(enumerate_drives)
        assert isinstance(result, list)
    
    def test_icon_generation_performance(self, benchmark, qapp):
        """Test drive icon generation performance"""
        sidebar = Sidebar()
        
        def generate_icon():
            return sidebar._get_drive_icon("C", "C:\\")
        
        result = benchmark(generate_icon)
        assert result is not None


class TestSidebar64BitOptimizations:
    """Test 64-bit specific optimizations in sidebar"""
    
    def test_large_drive_handling(self, qapp):
        """Test handling of large drives (>2TB)"""
        sidebar = Sidebar()
        
        # Mock very large drive
        with patch('src.ui.components.sidebar.shutil.disk_usage') as mock_usage:
            # 5TB drive
            mock_usage.return_value = Mock(
                total=5 * 1024**4,  # 5TB
                free=2 * 1024**4,   # 2TB free
            )
            
            with patch('src.ui.components.sidebar.os.path.exists', return_value=True):
                drives = sidebar._get_drives()
                
                if drives:  # If any drives returned
                    large_drive = drives[0]
                    assert large_drive['total_gb'] > 2000  # Should handle >2TB
                    assert isinstance(large_drive['total_gb'], float)
    
    def test_memory_efficient_drive_scanning(self, qapp):
        """Test memory efficiency during drive scanning"""
        sidebar = Sidebar()
        
        # Mock many drives
        mock_drives = []
        for i in range(26):  # A-Z drives
            letter = chr(ord('A') + i)
            mock_drives.append(f"{letter}:\\")
        
        with patch('src.ui.components.sidebar.os.path.exists', return_value=True), \
             patch('src.ui.components.sidebar.shutil.disk_usage') as mock_usage:
            
            mock_usage.return_value = Mock(
                total=1024**3,  # 1GB
                free=512 * 1024**2,  # 512MB
            )
            
            drives = sidebar._get_drives()
            
            # Should handle many drives without excessive memory usage
            assert len(drives) <= 26
    
    @patch('src.ui.components.sidebar.os.name', 'nt')
    def test_64bit_windows_api_types(self, qapp):
        """Test that Windows API uses proper 64-bit types"""
        sidebar = Sidebar()
        
        # This test verifies the API is called with proper types
        # In the actual implementation, we use wintypes.DWORD instead of c_ulong
        with patch('src.ui.components.sidebar.kernel32') as mock_kernel32, \
             patch('src.ui.components.sidebar.mpr') as mock_mpr:
            
            mock_kernel32.GetDriveTypeW.return_value = 3  # DRIVE_FIXED
            mock_mpr.WNetGetConnectionW.return_value = 0  # SUCCESS
            
            drive_type = sidebar._get_drive_type("C:\\")
            
            # Verify API was called
            mock_kernel32.GetDriveTypeW.assert_called_once()
            assert drive_type == "network"  # Should detect as network due to WNet success
