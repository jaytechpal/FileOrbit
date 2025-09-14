"""
Theme Service - Modern UI theme management
"""

from pathlib import Path
from typing import Dict, Any
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPalette, QColor

from src.utils.logger import get_logger


class ThemeService(QObject):
    """Service for managing application themes"""
    
    theme_changed = Signal(str)  # theme_name
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.current_theme = "dark"
        self.themes = self._load_themes()
    
    def _load_themes(self) -> Dict[str, Dict[str, Any]]:
        """Load theme definitions"""
        return {
            "dark": {
                "name": "Dark Theme",
                "colors": {
                    "primary": "#2b2b2b",
                    "secondary": "#3c3c3c", 
                    "accent": "#0078d4",
                    "background": "#1e1e1e",
                    "surface": "#252526",
                    "text": "#ffffff",
                    "text_secondary": "#cccccc",
                    "border": "#464647",
                    "hover": "#2a2d2e",
                    "selected": "#094771",
                    "error": "#f44747",
                    "warning": "#ffcc02",
                    "success": "#89d185"
                },
                "stylesheet": self._get_dark_stylesheet()
            },
            "light": {
                "name": "Light Theme", 
                "colors": {
                    "primary": "#ffffff",
                    "secondary": "#f8f8f8",
                    "accent": "#0078d4",
                    "background": "#ffffff",
                    "surface": "#f8f8f8",
                    "text": "#000000",
                    "text_secondary": "#666666",
                    "border": "#d0d0d0",
                    "hover": "#e5f3ff",
                    "selected": "#cce8ff",
                    "error": "#d13438",
                    "warning": "#f9ca24",
                    "success": "#2ecc71"
                },
                "stylesheet": self._get_light_stylesheet()
            },
            "blue": {
                "name": "Blue Theme",
                "colors": {
                    "primary": "#1e3a5f",
                    "secondary": "#2c5282",
                    "accent": "#4299e1",
                    "background": "#1a202c",
                    "surface": "#2d3748",
                    "text": "#ffffff",
                    "text_secondary": "#a0aec0",
                    "border": "#4a5568",
                    "hover": "#2c5282",
                    "selected": "#3182ce",
                    "error": "#f56565",
                    "warning": "#ed8936",
                    "success": "#48bb78"
                },
                "stylesheet": self._get_blue_stylesheet()
            }
        }
    
    def apply_theme(self, theme_name: str):
        """Apply theme to application"""
        if theme_name not in self.themes:
            self.logger.warning(f"Theme '{theme_name}' not found, using dark theme")
            theme_name = "dark"
        
        theme = self.themes[theme_name]
        app = QApplication.instance()
        
        if app:
            # Apply stylesheet
            app.setStyleSheet(theme["stylesheet"])
            
            # Set palette
            self._apply_palette(theme["colors"])
            
            self.current_theme = theme_name
            self.theme_changed.emit(theme_name)
            
            self.logger.info(f"Applied theme: {theme['name']}")
    
    def _apply_palette(self, colors: Dict[str, str]):
        """Apply color palette to application"""
        app = QApplication.instance()
        if not app:
            return
            
        palette = QPalette()
        
        # Window colors
        palette.setColor(QPalette.Window, QColor(colors["background"]))
        palette.setColor(QPalette.WindowText, QColor(colors["text"]))
        
        # Base colors
        palette.setColor(QPalette.Base, QColor(colors["surface"]))
        palette.setColor(QPalette.Text, QColor(colors["text"]))
        
        # Button colors
        palette.setColor(QPalette.Button, QColor(colors["secondary"]))
        palette.setColor(QPalette.ButtonText, QColor(colors["text"]))
        
        # Highlight colors
        palette.setColor(QPalette.Highlight, QColor(colors["selected"]))
        palette.setColor(QPalette.HighlightedText, QColor(colors["text"]))
        
        app.setPalette(palette)
    
    def get_color(self, color_name: str) -> str:
        """Get color value from current theme"""
        if self.current_theme in self.themes:
            return self.themes[self.current_theme]["colors"].get(color_name, "#ffffff")
        return "#ffffff"
    
    def get_available_themes(self) -> Dict[str, str]:
        """Get list of available themes"""
        return {name: theme["name"] for name, theme in self.themes.items()}
    
    def _get_dark_stylesheet(self) -> str:
        """Get dark theme stylesheet"""
        return """
        /* Main Window */
        QMainWindow {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        
        /* Menu Bar */
        QMenuBar {
            background-color: #2d2d30;
            color: #ffffff;
            border: none;
            padding: 2px;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
            border-radius: 3px;
        }
        
        QMenuBar::item:selected {
            background-color: #094771;
        }
        
        QMenu {
            background-color: #2d2d30;
            color: #ffffff;
            border: 1px solid #464647;
            padding: 2px;
        }
        
        QMenu::item {
            padding: 5px 20px;
            border-radius: 3px;
        }
        
        QMenu::item:selected {
            background-color: #094771;
        }
        
        QMenu::icon {
            padding-left: 4px;
            width: 16px;
            height: 16px;
        }
        
        /* Tool Bar */
        QToolBar {
            background-color: #2d2d30;
            border: none;
            spacing: 2px;
            padding: 4px;
        }
        
        QToolButton {
            background-color: transparent;
            border: none;
            padding: 4px;
            border-radius: 3px;
        }
        
        QToolButton:hover {
            background-color: #2a2d2e;
        }
        
        QToolButton:pressed {
            background-color: #094771;
        }
        
        /* Status Bar */
        QStatusBar {
            background-color: #007acc;
            color: #ffffff;
            border: none;
        }
        
        /* Splitter */
        QSplitter::handle {
            background-color: #464647;
        }
        
        QSplitter::handle:horizontal {
            width: 2px;
        }
        
        QSplitter::handle:vertical {
            height: 2px;
        }
        
        /* List Widget */
        QListWidget {
            background-color: #252526;
            color: #ffffff;
            border: 1px solid #464647;
            alternate-background-color: #2d2d30;
        }
        
        QListWidget::item {
            padding: 3px;
            border: none;
        }
        
        QListWidget::item:selected {
            background-color: #094771;
        }
        
        QListWidget::item:hover {
            background-color: #2a2d2e;
        }
        
        /* Tree Widget */
        QTreeWidget {
            background-color: #252526;
            color: #ffffff;
            border: 1px solid #464647;
            alternate-background-color: #2d2d30;
        }
        
        QTreeWidget::item {
            padding: 2px;
        }
        
        QTreeWidget::item:selected {
            background-color: #094771;
        }
        
        QTreeWidget::item:hover {
            background-color: #2a2d2e;
        }
        
        /* Tab Widget */
        QTabWidget::pane {
            border: 1px solid #464647;
            background-color: #252526;
        }
        
        QTabBar::tab {
            background-color: #2d2d30;
            color: #ffffff;
            padding: 5px 10px;
            border: 1px solid #464647;
            border-bottom: none;
        }
        
        QTabBar::tab:selected {
            background-color: #252526;
        }
        
        QTabBar::tab:hover {
            background-color: #2a2d2e;
        }
        
        /* Scroll Bar */
        QScrollBar:vertical {
            background-color: #2d2d30;
            width: 12px;
            border: none;
        }
        
        QScrollBar::handle:vertical {
            background-color: #464647;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #555555;
        }
        
        QScrollBar:horizontal {
            background-color: #2d2d30;
            height: 12px;
            border: none;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #464647;
            border-radius: 6px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #555555;
        }
        
        /* Line Edit */
        QLineEdit {
            background-color: #1e1e1e;
            color: #ffffff;
            border: 1px solid #464647;
            padding: 4px;
            border-radius: 3px;
        }
        
        QLineEdit:focus {
            border: 1px solid #0078d4;
        }
        
        /* Push Button */
        QPushButton {
            background-color: #0e639c;
            color: #ffffff;
            border: none;
            padding: 5px 15px;
            border-radius: 3px;
        }
        
        QPushButton:hover {
            background-color: #1177bb;
        }
        
        QPushButton:pressed {
            background-color: #094771;
        }
        """
    
    def _get_light_stylesheet(self) -> str:
        """Get light theme stylesheet"""
        return """
        /* Main Window */
        QMainWindow {
            background-color: #ffffff;
            color: #000000;
        }
        
        /* Menu Bar */
        QMenuBar {
            background-color: #f8f8f8;
            color: #000000;
            border: none;
            padding: 2px;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
            border-radius: 3px;
        }
        
        QMenuBar::item:selected {
            background-color: #cce8ff;
        }
        
        QMenu {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #d0d0d0;
            padding: 2px;
        }
        
        QMenu::item {
            padding: 5px 20px;
            border-radius: 3px;
        }
        
        QMenu::item:selected {
            background-color: #cce8ff;
        }
        
        /* Tool Bar */
        QToolBar {
            background-color: #f8f8f8;
            border: none;
            spacing: 2px;
            padding: 4px;
        }
        
        QToolButton {
            background-color: transparent;
            border: none;
            padding: 4px;
            border-radius: 3px;
        }
        
        QToolButton:hover {
            background-color: #e5f3ff;
        }
        
        QToolButton:pressed {
            background-color: #cce8ff;
        }
        
        /* Status Bar */
        QStatusBar {
            background-color: #0078d4;
            color: #ffffff;
            border: none;
        }
        
        /* List Widget */
        QListWidget {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #d0d0d0;
            alternate-background-color: #f8f8f8;
        }
        
        QListWidget::item {
            padding: 3px;
            border: none;
        }
        
        QListWidget::item:selected {
            background-color: #cce8ff;
        }
        
        QListWidget::item:hover {
            background-color: #e5f3ff;
        }
        
        /* Tree Widget */
        QTreeWidget {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #d0d0d0;
            alternate-background-color: #f8f8f8;
        }
        
        QTreeWidget::item {
            padding: 2px;
        }
        
        QTreeWidget::item:selected {
            background-color: #cce8ff;
        }
        
        QTreeWidget::item:hover {
            background-color: #e5f3ff;
        }
        """
    
    def _get_blue_stylesheet(self) -> str:
        """Get blue theme stylesheet"""
        return """
        /* Main Window */
        QMainWindow {
            background-color: #1a202c;
            color: #ffffff;
        }
        
        /* Menu Bar */
        QMenuBar {
            background-color: #2d3748;
            color: #ffffff;
            border: none;
            padding: 2px;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
            border-radius: 3px;
        }
        
        QMenuBar::item:selected {
            background-color: #3182ce;
        }
        
        /* Tool Bar */
        QToolBar {
            background-color: #2d3748;
            border: none;
            spacing: 2px;
            padding: 4px;
        }
        
        QToolButton {
            background-color: transparent;
            border: none;
            padding: 4px;
            border-radius: 3px;
        }
        
        QToolButton:hover {
            background-color: #2c5282;
        }
        
        QToolButton:pressed {
            background-color: #3182ce;
        }
        """
