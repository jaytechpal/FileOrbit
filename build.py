#!/usr/bin/env python3
"""
Build script for FileOrbit
Creates executable packages for different platforms
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def run_command(cmd, check=True):
    """Run a command and optionally check for errors"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result


def clean_build():
    """Clean previous build artifacts"""
    print("Cleaning previous builds...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name}")


def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    run_command("pip install -r requirements.txt")
    run_command("pip install pyinstaller")


def build_executable():
    """Build executable using PyInstaller optimized for 64-bit systems"""
    print("Building 64-bit executable...")
    
    # Common 64-bit optimization options
    base_cmd = [
        "pyinstaller",
        "--clean",  # Clean PyInstaller cache
        "--noconfirm",  # Replace output directory without confirmation
    ]
    
    # Determine platform-specific options
    if sys.platform == "win32":
        # Windows 64-bit specific
        cmd = base_cmd + [
            "--windowed",
            "--onefile", 
            "--name", "FileOrbit-x64",
            "--icon", "resources/icons/app_icon.ico",
            "--version-file", "version_info.txt",  # Will create this
            "--add-data", "resources;resources",
            "--exclude-module", "tkinter",  # Exclude unnecessary modules
            "--optimize", "2",  # Python optimization level
            "main.py"
        ]
    elif sys.platform == "darwin":
        # macOS 64-bit specific (Apple Silicon + Intel)
        cmd = base_cmd + [
            "--windowed",
            "--onefile",
            "--name", "FileOrbit-universal",
            "--icon", "resources/icons/app_icon.icns",
            "--add-data", "resources:resources",
            "--target-arch", "universal2",  # Support both Intel and Apple Silicon
            "--optimize", "2",
            "main.py"
        ]
    else:
        # Linux 64-bit specific
        cmd = base_cmd + [
            "--onefile",
            "--name", "FileOrbit-x64",
            "--add-data", "resources:resources",
            "--optimize", "2",
            "main.py"
        ]
    
    run_command(" ".join(cmd))


def create_installer():
    """Create platform-specific installer"""
    if sys.platform == "win32":
        print("Creating Windows installer...")
        # You could use NSIS or Inno Setup here
        print("Windows installer creation not implemented")
    elif sys.platform == "darwin":
        print("Creating macOS package...")
        # You could create a .dmg file here
        print("macOS package creation not implemented")
    else:
        print("Creating Linux package...")
        # You could create a .deb or .rpm package here
        print("Linux package creation not implemented")


def main():
    """Main build process"""
    print("FileOrbit Build Script")
    print("=" * 40)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    try:
        clean_build()
        install_dependencies()
        build_executable()
        
        print("\nBuild completed successfully!")
        print(f"Executable created in: {script_dir / 'dist'}")
        
        # Optional: Create installer
        create_installer_choice = input("\nCreate installer? (y/N): ").lower()
        if create_installer_choice == 'y':
            create_installer()
        
    except KeyboardInterrupt:
        print("\nBuild cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
