"""
NavigationManager - Centralized navigation and tab management service

This service handles all navigation functionality including tab management,
history tracking, breadcrumb navigation, and bookmark management for the file manager.
"""

from pathlib import Path
from typing import List, Optional, Dict, Callable
from dataclasses import dataclass

from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QStyle
from PySide6.QtCore import QObject, Signal

from src.utils.logger import get_logger
from src.config.constants import UIConstants


@dataclass
class TabInfo:
    """Information about a tab."""
    widget: QWidget
    current_path: Path
    navigation_history: List[Path]
    history_index: int
    address_bar: QLineEdit
    back_button: QPushButton
    forward_button: QPushButton
    up_button: QPushButton


class NavigationManager(QObject):
    """
    Centralized navigation and tab management service.
    
    Handles:
    - Tab creation and management
    - Navigation history (back/forward)
    - Address bar navigation
    - Breadcrumb navigation
    - Bookmark management
    - Parent directory navigation
    """
    
    # Signals
    path_changed = Signal(str)  # emitted when current path changes
    tab_created = Signal(int)   # emitted when new tab is created
    tab_closed = Signal(int)    # emitted when tab is closed
    tab_switched = Signal(int)  # emitted when tab is switched
    navigation_changed = Signal(bool, bool)  # can_go_back, can_go_forward
    
    def __init__(self, tab_widget: QTabWidget):
        super().__init__()
        self.logger = get_logger(__name__)
        self.tab_widget = tab_widget
        
        # Tab management
        self._tabs: Dict[int, TabInfo] = {}
        self._current_tab_index = -1
        self._tab_counter = 0
        
        # Bookmarks
        self._bookmarks: List[Path] = []
        
        # Callbacks for tab content creation
        self._tab_content_factory: Optional[Callable[[Path], QWidget]] = None
        self._navigation_button_factory: Optional[Callable[[], tuple]] = None
        
        # Connect tab widget signals
        self._connect_tab_signals()
        
        self.logger.info("NavigationManager initialized successfully")
    
    def set_tab_content_factory(self, factory: Callable[[Path], QWidget]):
        """
        Set factory function for creating tab content.
        
        Args:
            factory: Function that takes a Path and returns a QWidget
        """
        self._tab_content_factory = factory
    
    def set_navigation_button_factory(self, factory: Callable[[], tuple]):
        """
        Set factory function for creating navigation buttons.
        
        Args:
            factory: Function that returns (back_btn, forward_btn, up_btn)
        """
        self._navigation_button_factory = factory
    
    def create_initial_tab(self, initial_path: Path) -> int:
        """
        Create the initial tab.
        
        Args:
            initial_path: Path to open in the first tab
            
        Returns:
            Tab index
        """
        return self.create_new_tab(initial_path)
    
    def create_new_tab(self, path: Optional[Path] = None) -> int:
        """
        Create a new tab.
        
        Args:
            path: Path to open in the new tab
            
        Returns:
            Tab index
        """
        target_path = path or self.get_current_path()
        if target_path is None:
            target_path = Path.home()
        
        try:
            # Create tab widget
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            tab_layout.setContentsMargins(2, 2, 2, 2)
            tab_layout.setSpacing(2)
            
            # Create address bar layout
            address_layout = QHBoxLayout()
            address_layout.setSpacing(2)
            
            # Create navigation buttons
            back_btn, forward_btn, up_btn = self._create_navigation_buttons()
            
            # Create address bar
            address_bar = QLineEdit()
            address_bar.setText(str(target_path))
            
            # Add to layout
            address_layout.addWidget(back_btn)
            address_layout.addWidget(forward_btn)
            address_layout.addWidget(up_btn)
            address_layout.addWidget(address_bar)
            tab_layout.addLayout(address_layout)
            
            # Create tab content
            if self._tab_content_factory:
                content_widget = self._tab_content_factory(target_path)
                tab_layout.addWidget(content_widget)
            
            # Create tab info
            tab_info = TabInfo(
                widget=tab_widget,
                current_path=target_path,
                navigation_history=[target_path],
                history_index=0,
                address_bar=address_bar,
                back_button=back_btn,
                forward_button=forward_btn,
                up_button=up_btn
            )
            
            # Add tab to widget
            tab_name = target_path.name if target_path.name else "Root"
            tab_index = self.tab_widget.addTab(tab_widget, tab_name)
            self.tab_widget.setCurrentIndex(tab_index)
            
            # Store tab info
            self._tabs[tab_index] = tab_info
            self._current_tab_index = tab_index
            
            # Connect button signals
            self._connect_navigation_buttons(tab_info)
            
            # Connect address bar
            address_bar.returnPressed.connect(lambda: self._navigate_to_address(tab_index))
            
            # Update navigation state
            self._update_navigation_buttons(tab_info)
            
            self.logger.info(f"Created new tab {tab_index} for path: {target_path}")
            self.tab_created.emit(tab_index)
            
            return tab_index
            
        except Exception as e:
            self.logger.error(f"Failed to create new tab: {e}")
            return -1
    
    def close_tab(self, tab_index: int) -> bool:
        """
        Close a tab.
        
        Args:
            tab_index: Index of tab to close
            
        Returns:
            True if tab was closed, False otherwise
        """
        if self.tab_widget.count() <= 1:
            self.logger.warning("Cannot close last tab")
            return False
        
        try:
            # Remove from our tracking
            if tab_index in self._tabs:
                del self._tabs[tab_index]
            
            # Remove from tab widget
            self.tab_widget.removeTab(tab_index)
            
            # Update current tab index
            if tab_index == self._current_tab_index:
                self._current_tab_index = self.tab_widget.currentIndex()
            
            self.logger.info(f"Closed tab {tab_index}")
            self.tab_closed.emit(tab_index)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to close tab {tab_index}: {e}")
            return False
    
    def navigate_to(self, path: Path, tab_index: Optional[int] = None) -> bool:
        """
        Navigate to a path in the specified tab.
        
        Args:
            path: Path to navigate to
            tab_index: Tab index (current tab if None)
            
        Returns:
            True if navigation succeeded
        """
        if tab_index is None:
            tab_index = self._current_tab_index
        
        if tab_index not in self._tabs:
            self.logger.error(f"Invalid tab index: {tab_index}")
            return False
        
        try:
            if not path.exists() or not path.is_dir():
                self.logger.warning(f"Invalid path: {path}")
                return False
            
            tab_info = self._tabs[tab_index]
            
            # Update navigation history
            self._add_to_history(tab_info, path)
            
            # Update tab info
            tab_info.current_path = path
            tab_info.address_bar.setText(str(path))
            
            # Update tab title
            tab_name = path.name if path.name else "Root"
            self.tab_widget.setTabText(tab_index, tab_name)
            
            # Update navigation buttons
            self._update_navigation_buttons(tab_info)
            
            # Emit signal if this is the current tab
            if tab_index == self._current_tab_index:
                self.path_changed.emit(str(path))
            
            self.logger.info(f"Navigated tab {tab_index} to: {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Navigation failed for tab {tab_index}: {e}")
            return False
    
    def go_back(self, tab_index: Optional[int] = None) -> bool:
        """
        Navigate back in history.
        
        Args:
            tab_index: Tab index (current tab if None)
            
        Returns:
            True if navigation succeeded
        """
        if tab_index is None:
            tab_index = self._current_tab_index
        
        if tab_index not in self._tabs:
            return False
        
        tab_info = self._tabs[tab_index]
        
        if tab_info.history_index > 0:
            tab_info.history_index -= 1
            path = tab_info.navigation_history[tab_info.history_index]
            return self._navigate_without_history(tab_info, path, tab_index)
        
        return False
    
    def go_forward(self, tab_index: Optional[int] = None) -> bool:
        """
        Navigate forward in history.
        
        Args:
            tab_index: Tab index (current tab if None)
            
        Returns:
            True if navigation succeeded
        """
        if tab_index is None:
            tab_index = self._current_tab_index
        
        if tab_index not in self._tabs:
            return False
        
        tab_info = self._tabs[tab_index]
        
        if tab_info.history_index < len(tab_info.navigation_history) - 1:
            tab_info.history_index += 1
            path = tab_info.navigation_history[tab_info.history_index]
            return self._navigate_without_history(tab_info, path, tab_index)
        
        return False
    
    def go_up(self, tab_index: Optional[int] = None) -> bool:
        """
        Navigate to parent directory.
        
        Args:
            tab_index: Tab index (current tab if None)
            
        Returns:
            True if navigation succeeded
        """
        if tab_index is None:
            tab_index = self._current_tab_index
        
        if tab_index not in self._tabs:
            return False
        
        tab_info = self._tabs[tab_index]
        parent_path = tab_info.current_path.parent
        
        if parent_path != tab_info.current_path:
            return self.navigate_to(parent_path, tab_index)
        
        return False
    
    def get_current_path(self) -> Optional[Path]:
        """
        Get current path of active tab.
        
        Returns:
            Current path or None
        """
        if self._current_tab_index in self._tabs:
            return self._tabs[self._current_tab_index].current_path
        return None
    
    def get_tab_path(self, tab_index: int) -> Optional[Path]:
        """
        Get path of specified tab.
        
        Args:
            tab_index: Tab index
            
        Returns:
            Tab path or None
        """
        if tab_index in self._tabs:
            return self._tabs[tab_index].current_path
        return None
    
    def get_tab_count(self) -> int:
        """Get number of tabs."""
        return self.tab_widget.count()
    
    def get_current_tab_index(self) -> int:
        """Get current tab index."""
        return self._current_tab_index
    
    def switch_to_tab(self, tab_index: int) -> bool:
        """
        Switch to specified tab.
        
        Args:
            tab_index: Tab index to switch to
            
        Returns:
            True if switch succeeded
        """
        if 0 <= tab_index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(tab_index)
            return True
        return False
    
    def add_bookmark(self, path: Path, name: Optional[str] = None):
        """
        Add a bookmark.
        
        Args:
            path: Path to bookmark
            name: Optional name for bookmark
        """
        if path not in self._bookmarks:
            self._bookmarks.append(path)
            self.logger.info(f"Added bookmark: {path}")
    
    def remove_bookmark(self, path: Path):
        """
        Remove a bookmark.
        
        Args:
            path: Path to remove from bookmarks
        """
        if path in self._bookmarks:
            self._bookmarks.remove(path)
            self.logger.info(f"Removed bookmark: {path}")
    
    def get_bookmarks(self) -> List[Path]:
        """
        Get all bookmarks.
        
        Returns:
            List of bookmark paths
        """
        return self._bookmarks.copy()
    
    def can_go_back(self, tab_index: Optional[int] = None) -> bool:
        """Check if can go back in history."""
        if tab_index is None:
            tab_index = self._current_tab_index
        
        if tab_index in self._tabs:
            return self._tabs[tab_index].history_index > 0
        return False
    
    def can_go_forward(self, tab_index: Optional[int] = None) -> bool:
        """Check if can go forward in history."""
        if tab_index is None:
            tab_index = self._current_tab_index
        
        if tab_index in self._tabs:
            tab_info = self._tabs[tab_index]
            return tab_info.history_index < len(tab_info.navigation_history) - 1
        return False
    
    # Private methods
    
    def _connect_tab_signals(self):
        """Connect tab widget signals."""
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
    
    def _connect_navigation_buttons(self, tab_info: TabInfo):
        """Connect navigation button signals for a tab."""
        tab_index = self._get_tab_index_by_widget(tab_info.widget)
        
        tab_info.back_button.clicked.connect(lambda: self.go_back(tab_index))
        tab_info.forward_button.clicked.connect(lambda: self.go_forward(tab_index))
        tab_info.up_button.clicked.connect(lambda: self.go_up(tab_index))
    
    def _create_navigation_buttons(self) -> tuple:
        """Create navigation buttons."""
        if self._navigation_button_factory:
            return self._navigation_button_factory()
        
        # Default button creation
        style = QStyle()
        
        back_btn = QPushButton()
        back_btn.setIcon(style.standardIcon(QStyle.SP_ArrowLeft))
        back_btn.setMaximumWidth(UIConstants.NAVIGATION_BUTTON_WIDTH)
        back_btn.setToolTip("Back")
        
        forward_btn = QPushButton()
        forward_btn.setIcon(style.standardIcon(QStyle.SP_ArrowRight))
        forward_btn.setMaximumWidth(UIConstants.NAVIGATION_BUTTON_WIDTH)
        forward_btn.setToolTip("Forward")
        
        up_btn = QPushButton()
        up_btn.setIcon(style.standardIcon(QStyle.SP_ArrowUp))
        up_btn.setMaximumWidth(UIConstants.NAVIGATION_BUTTON_WIDTH)
        up_btn.setToolTip("Up")
        
        return back_btn, forward_btn, up_btn
    
    def _add_to_history(self, tab_info: TabInfo, path: Path):
        """Add path to navigation history."""
        # Remove any forward history if we're navigating to a new path
        if tab_info.history_index < len(tab_info.navigation_history) - 1:
            tab_info.navigation_history = tab_info.navigation_history[:tab_info.history_index + 1]
        
        # Add new path to history (avoid duplicates of same path)
        if not tab_info.navigation_history or tab_info.navigation_history[-1] != path:
            tab_info.navigation_history.append(path)
            tab_info.history_index = len(tab_info.navigation_history) - 1
    
    def _navigate_without_history(self, tab_info: TabInfo, path: Path, tab_index: int) -> bool:
        """Navigate without modifying history (for back/forward)."""
        try:
            tab_info.current_path = path
            tab_info.address_bar.setText(str(path))
            
            # Update tab title
            tab_name = path.name if path.name else "Root"
            self.tab_widget.setTabText(tab_index, tab_name)
            
            # Update navigation buttons
            self._update_navigation_buttons(tab_info)
            
            # Emit signal if this is the current tab
            if tab_index == self._current_tab_index:
                self.path_changed.emit(str(path))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Navigation without history failed: {e}")
            return False
    
    def _update_navigation_buttons(self, tab_info: TabInfo):
        """Update navigation button states."""
        can_go_back = tab_info.history_index > 0
        can_go_forward = tab_info.history_index < len(tab_info.navigation_history) - 1
        
        tab_info.back_button.setEnabled(can_go_back)
        tab_info.forward_button.setEnabled(can_go_forward)
        
        # Emit navigation state change if this is current tab
        tab_index = self._get_tab_index_by_widget(tab_info.widget)
        if tab_index == self._current_tab_index:
            self.navigation_changed.emit(can_go_back, can_go_forward)
    
    def _navigate_to_address(self, tab_index: int):
        """Navigate to address bar path."""
        if tab_index not in self._tabs:
            return
        
        try:
            tab_info = self._tabs[tab_index]
            new_path = Path(tab_info.address_bar.text())
            self.navigate_to(new_path, tab_index)
        except Exception as e:
            self.logger.error(f"Invalid address bar path: {e}")
    
    def _on_tab_changed(self, index: int):
        """Handle tab change."""
        if index >= 0 and index in self._tabs:
            self._current_tab_index = index
            tab_info = self._tabs[index]
            
            # Update navigation button states
            self._update_navigation_buttons(tab_info)
            
            # Emit signals
            self.path_changed.emit(str(tab_info.current_path))
            self.tab_switched.emit(index)
    
    def _get_tab_index_by_widget(self, widget: QWidget) -> int:
        """Get tab index by widget."""
        for i in range(self.tab_widget.count()):
            if self.tab_widget.widget(i) == widget:
                return i
        return -1