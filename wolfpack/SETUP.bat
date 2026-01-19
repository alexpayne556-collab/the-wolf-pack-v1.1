@echo off
SETLOCAL EnableDelayedExpansion

REM ========================================
REM Wolf Pack - One-Time Setup
REM ========================================

REM Keep window open no matter what
if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )

echo.
echo ===============================================
echo   WOLF PACK SYSTEM - SETUP
echo ===============================================
echo.

REM Check if Python is installed
echo [1/3] Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo PLEASE DO ONE OF THE FOLLOWING:
    echo.
    echo Option 1 - Install from Microsoft Store (EASIEST):
    echo   1. Press Windows key
    echo   2. Type "Microsoft Store"
    echo   3. Search for "Python 3.12"
    echo   4. Click "Get" or "Install"
    echo   5. Wait for installation
    echo   6. Run this script again
    echo.
    echo Option 2 - Install from python.org:
    echo   1. Go to: https://www.python.org/downloads/
    echo   2. Download Python 3.12 for Windows
    echo   3. Run installer
    echo   4. CHECK "Add Python to PATH" during install!
    echo   5. Run this script again
    echo.
    pause
    exit /b 1
)

python --version
echo Python found!
echo.

REM Check if pip works
echo [2/3] Checking pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip not found, trying to install...
    python -m ensurepip --default-pip
)

python -m pip --version
echo pip found!
echo.

REM Install dependencies
echo [3/3] Installing Python packages...
echo This may take 1-2 minutes...
echo.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install some packages!
    echo Try running: python -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ===============================================
echo   SETUP COMPLETE!
echo.
echo.
echo Press any key to close this window...
pause > nul
echo   Or just double-click RUN_WOLFPACK.bat
echo ===============================================
echo.

pause
