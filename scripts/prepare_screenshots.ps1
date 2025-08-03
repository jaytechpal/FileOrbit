# FileOrbit Screenshot Preparation Script
# This script sets up the environment for taking professional screenshots

Write-Host "FileOrbit Screenshot Preparation" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check if we're in the FileOrbit directory
if (-not (Test-Path "main.py")) {
    Write-Host "Error: Please run this script from the FileOrbit root directory" -ForegroundColor Red
    exit 1
}

# Create screenshots directory structure if it doesn't exist
Write-Host "`nCreating screenshot directories..." -ForegroundColor Yellow
$screenshotDirs = @(
    "docs\screenshots",
    "docs\screenshots\features",
    "docs\screenshots\themes", 
    "docs\screenshots\platforms"
)

foreach ($dir in $screenshotDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "Exists: $dir" -ForegroundColor Gray
    }
}

# Generate sample files for screenshots
Write-Host "`nGenerating sample files for realistic screenshots..." -ForegroundColor Yellow
if (Test-Path "scripts\generate_sample_files.py") {
    try {
        python scripts\generate_sample_files.py
        Write-Host "Sample files generated successfully!" -ForegroundColor Green
    } catch {
        Write-Host "Error generating sample files: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "You may need to install Python dependencies first:" -ForegroundColor Yellow
        Write-Host "pip install -r requirements.txt" -ForegroundColor Cyan
    }
} else {
    Write-Host "Sample file generator not found" -ForegroundColor Red
}

# Check if FileOrbit can run
Write-Host "`nChecking FileOrbit dependencies..." -ForegroundColor Yellow
try {
    python -c "import PySide6; print('PySide6 available')"
    Write-Host "✓ PySide6 is available" -ForegroundColor Green
} catch {
    Write-Host "✗ PySide6 not available - install with: pip install PySide6" -ForegroundColor Red
}

try {
    python -c "import pathlib; print('pathlib available')"
    Write-Host "✓ Required Python modules available" -ForegroundColor Green
} catch {
    Write-Host "✗ Missing required Python modules" -ForegroundColor Red
}

# Display next steps
Write-Host "`nScreenshot Preparation Complete!" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor White
Write-Host "1. Run FileOrbit: python main.py" -ForegroundColor Yellow
Write-Host "2. Navigate to Screenshots_Sample_Data folder" -ForegroundColor Yellow  
Write-Host "3. Follow the SCREENSHOT_GUIDE.md for detailed instructions" -ForegroundColor Yellow
Write-Host "4. Take screenshots according to the checklist" -ForegroundColor Yellow
Write-Host ""
Write-Host "Available Sample Data:" -ForegroundColor White
if (Test-Path "Screenshots_Sample_Data") {
    Write-Host "✓ Sample files created in: Screenshots_Sample_Data" -ForegroundColor Green
    Write-Host "  - Documents (PDFs, DOCs, etc.)" -ForegroundColor Gray
    Write-Host "  - Images (JPGs, PNGs, etc.)" -ForegroundColor Gray
    Write-Host "  - Videos (including large files for 64-bit demo)" -ForegroundColor Gray
    Write-Host "  - Development files (code, configs)" -ForegroundColor Gray
    Write-Host "  - Archives (ZIPs, 7z, etc.)" -ForegroundColor Gray
} else {
    Write-Host "✗ Sample files not created - check for errors above" -ForegroundColor Red
}
Write-Host ""
Write-Host "Screenshot Guidelines:" -ForegroundColor White
Write-Host "• Resolution: 1920x1080 minimum" -ForegroundColor Gray
Write-Host "• Format: PNG for UI, JPG for promotional" -ForegroundColor Gray
Write-Host "• Consistency: Use same window size across shots" -ForegroundColor Gray
Write-Host "• Content: Show realistic file operations" -ForegroundColor Gray
Write-Host ""
Write-Host "Documentation: docs\SCREENSHOT_GUIDE.md" -ForegroundColor Cyan
