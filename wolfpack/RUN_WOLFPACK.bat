@echo off
SETLOCAL EnableDelayedExpansion

REM ========================================
REM Wolf Pack Trading System - Daily Runner
REM ========================================

REM Keep window open no matter what
if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )

echo.
echo ===============================================
echo   WOLF PACK TRADING SYSTEM
echo   Daily Data Collection and Analysis
echo ===============================================
echo.

REM Change to wolfpack directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

REM Create data directories if they don't exist
if not exist "data" mkdir data
if not exist "reports" mkdir reports

echo [1/6] Initializing database...
python wolfpack_db.py
if %errorlevel% neq 0 (
    echo ERROR: Database initialization failed!
    pause
    exit /b 1
)

echo.
echo [2/6] Updating forward returns...
python wolfpack_updater.py
if %errorlevel% neq 0 (
    echo WARNING: Forward return update had issues
)

echo.
echo [3/6] Recording today's data for 99 stocks...
python wolfpack_recorder.py
if %errorlevel% neq 0 (
    echo ERROR: Data recording failed!
    pause
    exit /b 1
)

echo.
echo [4/6] Investigating big moves...
python move_investigator.py
if %errorlevel% neq 0 (
    echo WARNING: Move investigation had issues
)

echo.
echo [5/6] Checking for alerts...
python alert_engine.py
if %errorlevel% neq 0 (
    echo WARNING: Alert engine had issues
)

echo.
echo [6/6] Generating daily report...
python wolfpack_daily_report.py
if %errorlevel% neq 0 (
    echo WARNING: Daily report had issues
)

echo.
echo ===============================================
echo   WOLF PACK SYSTEM COMPLETE
echo   Check reports/ folder for today's summary
echo ===============================================
echo.
echo.
echo Press any key to close this window...
pause > nul
