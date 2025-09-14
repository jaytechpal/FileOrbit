#!/usr/bin/env python3
"""Test context menu building to see why duplicates still exist"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path.cwd() / 'src'))

from utils.windows_shell import WindowsShellIntegration

def test_context_menu_building():
    shell = WindowsShellIntegration()
    
    # Test with video file (like in the screenshot)
    test_file = Path('test.mp4')
    test_file.touch()
    
    print('=== Context Menu Actions Building Test ===')
    actions = shell.get_context_menu_actions([test_file])
    
    print(f'Total actions: {len(actions)}')
    print()
    
    # Look for VS Code duplicates
    code_actions = []
    mpc_actions = []
    
    for i, action in enumerate(actions):
        text = action.get('text', '')
        
        if 'code' in text.lower():
            code_actions.append((i, action))
        if 'mpc' in text.lower():
            mpc_actions.append((i, action))
    
    print(f'VS Code related actions found: {len(code_actions)}')
    for i, (idx, action) in enumerate(code_actions):
        print(f'  {i+1}. [{idx}] "{action.get("text", "")}"')
        print(f'      Action: {action.get("action", "")}')
        print(f'      Icon: {action.get("icon", "")}')
        print()
    
    print(f'MPC-HC related actions found: {len(mpc_actions)}')
    for i, (idx, action) in enumerate(mpc_actions):
        print(f'  {i+1}. [{idx}] "{action.get("text", "")}"')
        print(f'      Action: {action.get("action", "")}')
        print(f'      Icon: {action.get("icon", "")}')
        print()
    
    # Show all third-party extensions
    print('All third-party related actions:')
    third_party_keywords = ['vlc', 'git', 'code', 'sublime', 'mpc', 'visual studio']
    
    for i, action in enumerate(actions):
        text = action.get('text', '').lower()
        if any(keyword in text for keyword in third_party_keywords):
            print(f'{i+1:2d}. "{action.get("text", "")}"')
            print(f'     Action: {action.get("action", "")}')
            print(f'     Icon: {action.get("icon", "")}')
            print()
    
    test_file.unlink()

if __name__ == '__main__':
    test_context_menu_building()