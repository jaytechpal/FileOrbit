#!/bin/bash
# Setup script for FileOrbit Virtual Environment (macOS/Linux)
# Run this script to automatically set up the development environment

echo "========================================"
echo "FileOrbit Virtual Environment Setup"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

echo "Python is installed:"
python3 --version
echo

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv fileorbit-env
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi
echo "✓ Virtual environment created successfully"
echo

# Activate virtual environment
echo "Activating virtual environment..."
source fileorbit-env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip
echo

# Install dependencies
echo "Installing project dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    echo "Please check requirements.txt and try again"
    exit 1
fi
echo "✓ Dependencies installed successfully"
echo

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo
echo "To activate the virtual environment in the future:"
echo "  source fileorbit-env/bin/activate"
echo
echo "To run FileOrbit:"
echo "  python main.py"
echo
echo "To deactivate the virtual environment:"
echo "  deactivate"
echo
echo "The virtual environment is currently active."
echo "You can now run: python main.py"
echo
