"""
Test script to check available Qt standard icons and emoji rendering
"""
import sys
from pathlib import Path

# Add the source directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QToolBar, QPushButton, QHBoxLayout, QStyle
from PySide6.QtGui import QAction, QFont

def test_icons():
    app = QApplication(sys.argv)
    widget = QWidget()
    widget.setWindowTitle("Icon Test")
    widget.resize(800, 400)
    
    layout = QVBoxLayout(widget)
    
    # Test standard Qt icons
    toolbar = QToolBar()
    style = widget.style()
    
    # Test Qt standard icons with correct enum access
    standard_icons = [
        (QStyle.SP_ArrowLeft, "SP_ArrowLeft"),
        (QStyle.SP_ArrowRight, "SP_ArrowRight"), 
        (QStyle.SP_ArrowUp, "SP_ArrowUp"),
        (QStyle.SP_ArrowDown, "SP_ArrowDown"),
        (QStyle.SP_DirIcon, "SP_DirIcon"),
        (QStyle.SP_FileIcon, "SP_FileIcon"),
        (QStyle.SP_TrashIcon, "SP_TrashIcon"),
        (QStyle.SP_BrowserReload, "SP_BrowserReload"),
        (QStyle.SP_DialogCancelButton, "SP_DialogCancelButton"),
        (QStyle.SP_DialogApplyButton, "SP_DialogApplyButton")
    ]
    
    print("Testing Qt Standard Icons:")
    for icon_enum, name in standard_icons:
        try:
            icon = style.standardIcon(icon_enum)
            if not icon.isNull():
                action = QAction(name, toolbar)
                action.setIcon(icon)
                toolbar.addAction(action)
                print(f"✓ {name} - Available")
            else:
                print(f"✗ {name} - Null icon")
        except Exception as e:
            print(f"✗ {name} - Error: {e}")
    
    layout.addWidget(toolbar)
    
    # Test emoji rendering
    print("\nTesting Emoji Rendering:")
    emoji_layout = QHBoxLayout()
    emoji_widget = QWidget()
    emoji_widget.setLayout(emoji_layout)
    
    emojis = ["←", "→", "↑", "📄", "✂️", "🗑️", "📁", "🔄"]
    emoji_names = ["Back", "Forward", "Up", "Copy", "Move", "Delete", "New Folder", "Refresh"]
    
    for emoji, name in zip(emojis, emoji_names):
        button = QPushButton(f"{emoji} {name}")
        # Try different fonts for better emoji support
        font = QFont()
        font.setPointSize(12)
        button.setFont(font)
        emoji_layout.addWidget(button)
        print(f"Added emoji button: {emoji} {name}")
    
    layout.addWidget(emoji_widget)
    
    # Test text-only buttons
    print("\nTesting Text-Only Buttons:")
    text_layout = QHBoxLayout()
    text_widget = QWidget()
    text_widget.setLayout(text_layout)
    
    text_buttons = ["◄ Back", "► Forward", "▲ Up", "Copy", "Move", "Delete", "New Folder", "Refresh"]
    
    for text in text_buttons:
        button = QPushButton(text)
        text_layout.addWidget(button)
        print(f"Added text button: {text}")
    
    layout.addWidget(text_widget)
    
    print(f"\nWindow would be displayed. Available font families: {app.fontDatabase().families()[:5]}...")
    
    # Don't show the widget in testing, just return the info
    widget.close()

if __name__ == "__main__":
    test_icons()
