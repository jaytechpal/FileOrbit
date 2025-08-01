# Setup script for FileOrbit Virtual Environment (Windows PowerShell)
# Run this script to automatically set up the development environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FileOrbit Virtual Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "Python is installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host

# Check execution policy
$executionPolicy = Get-ExecutionPolicy
if ($executionPolicy -eq "Restricted") {
    Write-Host "WARNING: PowerShell execution policy is Restricted" -ForegroundColor Yellow
    Write-Host "Setting execution policy for current user..." -ForegroundColor Yellow
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Write-Host "✓ Execution policy updated" -ForegroundColor Green
    Write-Host
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
try {
    python -m venv fileorbit-env
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create virtual environment"
    }
    Write-Host "✓ Virtual environment created successfully" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
try {
    & .\fileorbit-env\Scripts\Activate.ps1
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
try {
    python -m pip install --upgrade pip | Out-Null
    Write-Host "✓ pip upgraded successfully" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Failed to upgrade pip, continuing..." -ForegroundColor Yellow
}
Write-Host

# Install dependencies
Write-Host "Installing project dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install dependencies"
    }
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Write-Host "Please check requirements.txt and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host
Write-Host "To activate the virtual environment in the future:" -ForegroundColor White
Write-Host "  .\fileorbit-env\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host
Write-Host "To run FileOrbit:" -ForegroundColor White
Write-Host "  python main.py" -ForegroundColor Gray
Write-Host
Write-Host "To deactivate the virtual environment:" -ForegroundColor White
Write-Host "  deactivate" -ForegroundColor Gray
Write-Host
Write-Host "The virtual environment is currently active." -ForegroundColor Green
Write-Host "You can now run: python main.py" -ForegroundColor Yellow
Write-Host

Read-Host "Press Enter to continue"
