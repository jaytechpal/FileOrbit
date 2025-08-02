"""
File Service - Core file operations with threading support
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from PySide6.QtCore import QObject, QThread, Signal, QMutex, QTimer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from src.utils.logger import get_logger


class FileOperationWorker(QThread):
    """Worker thread for file operations"""
    
    progress = Signal(int)  # Progress percentage
    status = Signal(str)    # Status message
    finished = Signal(bool, str)  # Success, message
    file_processed = Signal(str)  # Current file being processed
    
    def __init__(self, operation_type: str, source_paths: List[Path], 
                 target_path: Path, options: Dict[str, Any] = None):
        super().__init__()
        self.operation_type = operation_type
        self.source_paths = source_paths
        self.target_path = target_path
        self.options = options or {}
        self.logger = get_logger(__name__)
        self._cancelled = False
        
    def run(self):
        """Execute file operation"""
        try:
            if self.operation_type == "copy":
                self._copy_files()
            elif self.operation_type == "move":
                self._move_files()
            elif self.operation_type == "delete":
                self._delete_files()
            else:
                self.finished.emit(False, f"Unknown operation: {self.operation_type}")
                return
                
            if not self._cancelled:
                self.finished.emit(True, f"{self.operation_type.title()} completed successfully")
                
        except Exception as e:
            self.logger.error(f"File operation failed: {e}")
            self.finished.emit(False, str(e))
    
    def cancel(self):
        """Cancel the operation"""
        self._cancelled = True
    
    def _copy_files(self):
        """Copy files to target directory"""
        total_size = sum(self._get_file_size(path) for path in self.source_paths)
        copied_size = 0
        
        for source_path in self.source_paths:
            if self._cancelled:
                break
                
            target_file = self.target_path / source_path.name
            self.file_processed.emit(str(source_path))
            
            if source_path.is_file():
                self._copy_file_with_progress(source_path, target_file, total_size, copied_size)
                copied_size += source_path.stat().st_size
            elif source_path.is_dir():
                shutil.copytree(source_path, target_file, dirs_exist_ok=True)
                copied_size += self._get_file_size(source_path)
            
            progress = int((copied_size / total_size) * 100) if total_size > 0 else 100
            self.progress.emit(progress)
    
    def _move_files(self):
        """Move files to target directory"""
        total_files = len(self.source_paths)
        
        for i, source_path in enumerate(self.source_paths):
            if self._cancelled:
                break
                
            target_file = self.target_path / source_path.name
            self.file_processed.emit(str(source_path))
            
            shutil.move(str(source_path), str(target_file))
            
            progress = int(((i + 1) / total_files) * 100)
            self.progress.emit(progress)
    
    def _delete_files(self):
        """Delete files"""
        total_files = len(self.source_paths)
        
        for i, source_path in enumerate(self.source_paths):
            if self._cancelled:
                break
                
            self.file_processed.emit(str(source_path))
            
            if source_path.is_file():
                source_path.unlink()
            elif source_path.is_dir():
                shutil.rmtree(source_path)
            
            progress = int(((i + 1) / total_files) * 100)
            self.progress.emit(progress)
    
    def _copy_file_with_progress(self, source: Path, target: Path, total_size: int, copied_so_far: int):
        """Copy single file with progress reporting"""
        buffer_size = 1024 * 1024  # 1MB buffer
        
        with open(source, 'rb') as src, open(target, 'wb') as dst:
            while True:
                if self._cancelled:
                    break
                    
                chunk = src.read(buffer_size)
                if not chunk:
                    break
                    
                dst.write(chunk)
                copied_so_far += len(chunk)
                
                if total_size > 0:
                    progress = int((copied_so_far / total_size) * 100)
                    self.progress.emit(progress)
    
    def _get_file_size(self, path: Path) -> int:
        """Get total size of file or directory"""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        return 0


class FileWatcher(QObject, FileSystemEventHandler):
    """File system watcher for real-time updates"""
    
    file_changed = Signal(str, str)  # path, event_type
    
    def __init__(self):
        QObject.__init__(self)
        FileSystemEventHandler.__init__(self)
        self.observer = Observer()
        self.watched_paths = set()
        self.logger = get_logger(__name__)
    
    def start_watching(self, path: str):
        """Start watching a directory"""
        if path not in self.watched_paths:
            self.observer.schedule(self, path, recursive=False)
            self.watched_paths.add(path)
            
            if not self.observer.is_alive():
                self.observer.start()
    
    def stop_watching(self, path: str):
        """Stop watching a directory"""
        if path in self.watched_paths:
            self.watched_paths.remove(path)
            # Note: watchdog doesn't have easy way to remove specific path
            # In production, you might want to restart observer
    
    def stop_all(self):
        """Stop all watching"""
        self.observer.stop()
        self.observer.join()
        self.watched_paths.clear()
    
    def on_any_event(self, event):
        """Handle file system events"""
        if not event.is_directory:
            event_type = event.event_type
            file_path = event.src_path
            self.file_changed.emit(file_path, event_type)


class FileService(QObject):
    """Main file service for all file operations"""
    
    operation_started = Signal(str)  # operation_id
    operation_progress = Signal(str, int)  # operation_id, progress
    operation_finished = Signal(str, bool, str)  # operation_id, success, message
    directory_changed = Signal(str)  # path
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.active_operations = {}
        self.file_watcher = FileWatcher()
        self.operation_counter = 0
        self.mutex = QMutex()
        
        # Connect file watcher
        self.file_watcher.file_changed.connect(self._on_file_changed)
    
    def copy_files(self, source_paths: List[Path], target_path: Path, 
                   options: Dict[str, Any] = None) -> str:
        """Start copy operation"""
        return self._start_operation("copy", source_paths, target_path, options)
    
    def move_files(self, source_paths: List[Path], target_path: Path,
                   options: Dict[str, Any] = None) -> str:
        """Start move operation"""
        return self._start_operation("move", source_paths, target_path, options)
    
    def delete_files(self, source_paths: List[Path], 
                     options: Dict[str, Any] = None) -> str:
        """Start delete operation"""
        return self._start_operation("delete", source_paths, Path(), options)
    
    def _start_operation(self, operation_type: str, source_paths: List[Path],
                        target_path: Path, options: Dict[str, Any] = None) -> str:
        """Start file operation in worker thread"""
        self.mutex.lock()
        try:
            self.operation_counter += 1
            operation_id = f"{operation_type}_{self.operation_counter}"
            
            worker = FileOperationWorker(operation_type, source_paths, target_path, options)
            
            # Connect signals
            worker.progress.connect(lambda p: self.operation_progress.emit(operation_id, p))
            worker.finished.connect(lambda s, m: self._on_operation_finished(operation_id, s, m))
            
            self.active_operations[operation_id] = worker
            worker.start()
            
            self.operation_started.emit(operation_id)
            return operation_id
            
        finally:
            self.mutex.unlock()
    
    def cancel_operation(self, operation_id: str):
        """Cancel active operation"""
        if operation_id in self.active_operations:
            self.active_operations[operation_id].cancel()
    
    def _on_operation_finished(self, operation_id: str, success: bool, message: str):
        """Handle operation completion"""
        self.operation_finished.emit(operation_id, success, message)
        
        # Clean up
        if operation_id in self.active_operations:
            worker = self.active_operations[operation_id]
            worker.wait()  # Wait for thread to finish
            del self.active_operations[operation_id]
    
    def start_watching_directory(self, path: str):
        """Start watching directory for changes"""
        self.file_watcher.start_watching(path)
    
    def stop_watching_directory(self, path: str):
        """Stop watching directory"""
        self.file_watcher.stop_watching(path)
    
    def _on_file_changed(self, file_path: str, event_type: str):
        """Handle file system change"""
        directory = str(Path(file_path).parent)
        self.directory_changed.emit(directory)
    
    def get_file_info(self, path: Path) -> Dict[str, Any]:
        """Get detailed file information"""
        try:
            stat = path.stat()
            
            # Handle permissions cross-platform
            if os.name == 'nt':  # Windows
                # Windows doesn't use Unix-style permissions
                permissions = "---"  # Placeholder
                # Check if read-only
                if stat.st_mode & 0o200 == 0:  # No write permission
                    permissions = "r--"
                else:
                    permissions = "rw-"
            else:  # Unix-like systems (macOS, Linux)
                permissions = oct(stat.st_mode)[-3:]
            
            return {
                "name": path.name,
                "path": str(path),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "created": datetime.fromtimestamp(stat.st_ctime),
                "is_directory": path.is_dir(),
                "is_file": path.is_file(),
                "permissions": permissions,
                "extension": path.suffix.lower() if path.is_file() else ""
            }
        except (OSError, IOError) as e:
            self.logger.error(f"Error getting file info for {path}: {e}")
            return {}
    
    def calculate_checksum(self, file_path: Path, algorithm: str = "md5") -> str:
        """Calculate file checksum"""
        hash_obj = hashlib.new(algorithm)
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except (OSError, IOError) as e:
            self.logger.error(f"Error calculating checksum for {file_path}: {e}")
            return ""
    
    def stop_all_operations(self):
        """Stop all active operations"""
        for operation_id in list(self.active_operations.keys()):
            self.cancel_operation(operation_id)
        
        self.file_watcher.stop_all()
