#!/usr/bin/env python3
"""Test MPC-HC icon extraction specifically"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path.cwd() / 'src'))

from utils.windows_shell import WindowsShellIntegration

def test_mpc_hc_extraction():
    shell = WindowsShellIntegration()
    
    # Test with video file
    test_file = Path('test.mp4')
    test_file.touch()
    
    print('=== MPC-HC Detection Test ===')
    extensions = shell.get_shell_extensions_for_file(test_file)
    
    # Find MPC-HC extensions
    mpc_extensions = []
    for ext in extensions:
        text = ext.get('text', '')
        if 'mpc' in text.lower():
            mpc_extensions.append(ext)
    
    print(f'Found {len(mpc_extensions)} MPC-HC extensions:')
    
    for i, ext in enumerate(mpc_extensions):
        print(f'\n{i+1}. Text: "{ext.get("text", "N/A")}"')
        print(f'   Command: {ext.get("command", "N/A")}')
        print(f'   Name: {ext.get("name", "N/A")}')
        print(f'   Icon: {ext.get("icon", "N/A")}')
        
        # Test executable extraction
        command = ext.get("command", "")
        if command:
            # Extract exe path like the file panel does
            if command.startswith('"'):
                end_quote = command.find('"', 1)
                if end_quote > 0:
                    exe_path = command[1:end_quote]
            else:
                parts = command.split(' ')
                exe_path = parts[0] if parts else ""
            
            print(f'   Extracted exe path: {exe_path}')
            
            # Check if file exists
            import os
            if exe_path and os.path.exists(exe_path):
                print(f'   ✅ Executable exists: {exe_path}')
            else:
                print(f'   ❌ Executable not found: {exe_path}')
    
    test_file.unlink()

if __name__ == '__main__':
    test_mpc_hc_extraction()