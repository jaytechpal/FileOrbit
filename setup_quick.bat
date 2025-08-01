@echo off
echo ========================================
echo FileOrbit Virtual Environment Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python is installed
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv fileorbit-env
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully
echo.

REM Activate virtual environment
echo Activating virtual environment...
call fileorbit-env\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo Installing project dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Please check requirements.txt and try again
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To activate the virtual environment in the future:
echo   fileorbit-env\Scripts\activate.bat
echo.
echo To run FileOrbit:
echo   python main.py
echo.
echo To deactivate the virtual environment:
echo   deactivate
echo.
echo The virtual environment is currently active.
echo You can now run: python main.py
echo.
pause
