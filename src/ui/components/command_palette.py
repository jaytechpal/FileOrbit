"""
Command Palette Component - Quick action search
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
from PySide6.QtCore import Signal, Qt, QEvent
from PySide6.QtGui import QKeySequence

from src.utils.logger import get_logger


class CommandPalette(QWidget):
    """Command palette for quick actions"""
    
    command_executed = Signal(str)  # command_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFixedSize(400, 300)
        
        self.commands = self._get_available_commands()
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup command palette UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type a command...")
        self.search_input.textChanged.connect(self._filter_commands)
        self.search_input.returnPressed.connect(self._execute_selected_command)
        layout.addWidget(self.search_input)
        
        # Commands list
        self.commands_list = QListWidget()
        self.commands_list.itemDoubleClicked.connect(self._execute_selected_command)
        layout.addWidget(self.commands_list)
        
        # Populate initial commands
        self._populate_commands()
        
        # Style
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d30;
                border: 1px solid #464647;
                border-radius: 5px;
            }
            QLineEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #464647;
                padding: 5px;
                border-radius: 3px;
            }
            QListWidget {
                background-color: #252526;
                color: #ffffff;
                border: none;
                border-radius: 3px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #464647;
            }
            QListWidget::item:selected {
                background-color: #094771;
            }
        """)
    
    def _get_available_commands(self):
        """Get list of available commands"""
        return [
            ("copy", "Copy Files", "Copy selected files to clipboard"),
            ("cut", "Cut Files", "Cut selected files to clipboard"),
            ("paste", "Paste Files", "Paste files from clipboard"),
            ("delete", "Delete Files", "Delete selected files"),
            ("new_folder", "New Folder", "Create a new folder"),
            ("new_file", "New File", "Create a new file"),
            ("refresh", "Refresh", "Refresh current view"),
            ("go_home", "Go Home", "Navigate to home directory"),
            ("go_up", "Go Up", "Navigate to parent directory"),
            ("show_hidden", "Toggle Hidden Files", "Show/hide hidden files"),
            ("dual_pane", "Toggle Dual Pane", "Toggle dual pane mode"),
            ("focus_left", "Focus Left Panel", "Set focus to left panel"),
            ("focus_right", "Focus Right Panel", "Set focus to right panel"),
            ("new_tab", "New Tab", "Open new tab"),
            ("close_tab", "Close Tab", "Close current tab"),
            ("preferences", "Preferences", "Open preferences dialog"),
            ("about", "About", "Show about dialog"),
            ("exit", "Exit", "Exit application"),
        ]
    
    def _populate_commands(self, filter_text=""):
        """Populate commands list"""
        self.commands_list.clear()
        
        for command_id, name, description in self.commands:
            if not filter_text or filter_text.lower() in name.lower() or filter_text.lower() in description.lower():
                item = QListWidgetItem()
                item.setText(f"{name}\n{description}")
                item.setData(Qt.UserRole, command_id)
                self.commands_list.addItem(item)
        
        # Select first item
        if self.commands_list.count() > 0:
            self.commands_list.setCurrentRow(0)
    
    def _filter_commands(self, text):
        """Filter commands based on search text"""
        self._populate_commands(text)
    
    def _execute_selected_command(self):
        """Execute selected command"""
        current_item = self.commands_list.currentItem()
        if current_item:
            command_id = current_item.data(Qt.UserRole)
            self.command_executed.emit(command_id)
            self.hide()
    
    def show_at_center(self):
        """Show command palette at center of parent"""
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)
        
        self.show()
        self.search_input.clear()
        self.search_input.setFocus()
        self._populate_commands()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            self.hide()
        elif event.key() == Qt.Key_Up:
            current_row = self.commands_list.currentRow()
            if current_row > 0:
                self.commands_list.setCurrentRow(current_row - 1)
        elif event.key() == Qt.Key_Down:
            current_row = self.commands_list.currentRow()
            if current_row < self.commands_list.count() - 1:
                self.commands_list.setCurrentRow(current_row + 1)
        else:
            super().keyPressEvent(event)
