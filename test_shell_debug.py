#!/usr/bin/env python3
"""Test script to debug shell integration issues"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path.cwd() / 'src'))

from utils.windows_shell import WindowsShellIntegration

def test_shell_extensions():
    shell = WindowsShellIntegration()
    
    # Test with video file (for MPC-HC)
    test_file = Path('test.mp4')
    test_file.touch()
    
    print('=== Shell Extensions for MP4 file ===')
    extensions = shell.get_shell_extensions_for_file(test_file)
    
    # Group by text to see duplicates
    text_counts = {}
    for ext in extensions:
        text = ext.get('text', 'N/A')
        if text not in text_counts:
            text_counts[text] = []
        text_counts[text].append(ext)
    
    print(f'Total extensions found: {len(extensions)}')
    print(f'Unique text entries: {len(text_counts)}')
    print()
    
    # Show duplicates
    duplicates_found = False
    for text, items in text_counts.items():
        if len(items) > 1:
            print(f'DUPLICATE: "{text}" appears {len(items)} times')
            for i, item in enumerate(items):
                command = item.get("command", "N/A")
                print(f'  {i+1}. Command: {command[:80]}...')
            print()
            duplicates_found = True
    
    if not duplicates_found:
        print("No duplicates found in text entries.")
        print()
    
    # Show all entries with focus on VS Code and MPC-HC
    print('All entries:')
    for i, ext in enumerate(extensions):
        text = ext.get('text', 'N/A')
        command = ext.get('command', 'N/A')
        name = ext.get('name', 'N/A')
        
        # Highlight VS Code and MPC-HC entries
        marker = ""
        if 'code' in text.lower() or 'code' in command.lower():
            marker = " [VS CODE]"
        elif 'mpc' in text.lower() or 'mpc' in command.lower():
            marker = " [MPC-HC]"
        
        print(f'{i+1:2d}. Text: "{text}"{marker}')
        if name != text:
            print(f'     Name: "{name}"')
        print(f'     Command: {command[:80]}...')
        print()
    
    test_file.unlink()

if __name__ == '__main__':
    test_shell_extensions()