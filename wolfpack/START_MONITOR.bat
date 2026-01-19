@echo off
REM ========================================
REM Wolf Pack V2 - Real-Time Monitor
REM Runs during market hours (9:30 AM - 4:00 PM ET)
REM ========================================

SETLOCAL EnableDelayedExpansion

REM Keep window open no matter what
if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )

echo.
echo ===============================================
echo   WOLF PACK V2 - REAL-TIME MONITOR
echo   Detecting moves and fetching catalysts
echo   Alert threshold: ±3.0%%
echo ===============================================
echo.

cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo Starting real-time monitor...
echo.
echo 🐺 This will run continuously during market hours
echo 🐺 Press Ctrl+C to stop
echo.

python realtime_monitor.py

pause
