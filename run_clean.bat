@echo off
echo ========================================
echo FileOrbit - Clean Launch
echo ========================================
echo.

echo Cleaning Python cache...
if exist "src\__pycache__" rmdir /s /q "src\__pycache__"
for /d /r "src" %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
del /s /q "*.pyc" 2>nul

echo Activating virtual environment...
call fileorbit-env\Scripts\activate.bat

echo Starting FileOrbit with fresh cache...
python -B main.py

pause
