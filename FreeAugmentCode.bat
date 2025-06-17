@echo off
title Free AugmentCode - GUI Launcher

echo ========================================
echo    Free AugmentCode - Starting GUI
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python 3.8+ to run Free AugmentCode.
    echo Download from: https://python.org
    echo.
    pause
    exit /b 1
)

REM Check if main files exist
if not exist "index.py" (
    echo ERROR: index.py not found!
    echo Please make sure you're in the Free AugmentCode directory.
    echo.
    pause
    exit /b 1
)

if not exist "gui.py" (
    echo ERROR: gui.py not found!
    echo Please make sure you have all Free AugmentCode files.
    echo.
    pause
    exit /b 1
)

echo Python found. Starting Free AugmentCode GUI...
echo.

REM Install dependencies if needed
echo Installing/checking dependencies...
python -m pip install -r requirements.txt >nul 2>&1

echo Starting GUI application...
echo.

REM Launch the GUI
python index.py --gui

echo.
echo Free AugmentCode GUI closed.
pause
