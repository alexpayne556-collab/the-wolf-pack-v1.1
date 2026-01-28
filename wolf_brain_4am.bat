@echo off
REM ================================================
REM WOLF BRAIN 4 AM AUTO-START
REM 
REM This script starts the Wolf Brain at 4 AM
REM to scan for premarket gainers and generate
REM an intel report for you to review at 7 AM.
REM
REM HOW TO SET UP:
REM 1. Open Task Scheduler (search "Task Scheduler" in Windows)
REM 2. Click "Create Basic Task"
REM 3. Name: "Wolf Brain 4AM Scanner"
REM 4. Trigger: Daily at 4:00 AM
REM 5. Action: Start a program
REM 6. Program: Browse to this .bat file
REM 7. Done!
REM
REM Or use schtasks command below.
REM ================================================

echo.
echo ============================================
echo   WOLF BRAIN 4 AM AUTO-SCANNER
echo   %date% %time%
echo ============================================
echo.

REM Set API Keys
set APCA_API_KEY_ID=PKW2ON6GMKIUXKBC7L3GY4MJ2A
set APCA_API_SECRET_KEY=9S25KmeAhaRPzXg4LFqcsh9YBuxQ3whzp5LavrPvSrTN
set FINNHUB_API_KEY=d5jddu1r01qh37ujsqrgd5jddu1r01qh37ujsqs0
set NEWSAPI_KEY=e6f793dfd61f473786f69466f9313fe8

REM Navigate to wolf_brain
cd /d %~dp0src\wolf_brain

REM Run the scanner with intel report
python autonomous_brain.py --report

echo.
echo ============================================
echo   INTEL REPORT GENERATED!
echo   Check: data\wolf_brain\LATEST_INTEL_REPORT.txt
echo ============================================
echo.

REM Keep window open if run manually
if "%1"=="" pause
