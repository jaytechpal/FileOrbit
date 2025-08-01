"""
Modern Toolbar Component
"""

from PySide6.QtWidgets import QToolBar, QToolButton, QWidget, QHBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon, QAction

from src.utils.logger import get_logger


class ModernToolBar(QToolBar):
    """Modern styled toolbar with file operation buttons"""
    
    # Signals
    copy_requested = Signal()
    move_requested = Signal()
    delete_requested = Signal()
    new_folder_requested = Signal()
    refresh_requested = Signal()
    
    def __init__(self, file_service=None):
        super().__init__()
        self.file_service = file_service
        self.logger = get_logger(__name__)
        
        self.setMovable(False)
        self.setFloatable(False)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        self._setup_actions()
    
    def _setup_actions(self):
        """Setup toolbar actions"""
        # Copy action
        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.setToolTip("Copy selected files")
        copy_action.triggered.connect(self.copy_requested.emit)
        self.addAction(copy_action)
        
        # Move action
        move_action = QAction("Move", self)
        move_action.setShortcut("Ctrl+X")
        move_action.setToolTip("Move selected files")
        move_action.triggered.connect(self.move_requested.emit)
        self.addAction(move_action)
        
        # Delete action
        delete_action = QAction("Delete", self)
        delete_action.setShortcut("Delete")
        delete_action.setToolTip("Delete selected files")
        delete_action.triggered.connect(self.delete_requested.emit)
        self.addAction(delete_action)
        
        self.addSeparator()
        
        # New folder action
        new_folder_action = QAction("New Folder", self)
        new_folder_action.setShortcut("Ctrl+Shift+N")
        new_folder_action.setToolTip("Create new folder")
        new_folder_action.triggered.connect(self.new_folder_requested.emit)
        self.addAction(new_folder_action)
        
        # Refresh action
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.setToolTip("Refresh current view")
        refresh_action.triggered.connect(self.refresh_requested.emit)
        self.addAction(refresh_action)
        
        # Add spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.addWidget(spacer)
        
        # View options on the right
        view_action = QAction("View", self)
        view_action.setToolTip("View options")
        self.addAction(view_action)
