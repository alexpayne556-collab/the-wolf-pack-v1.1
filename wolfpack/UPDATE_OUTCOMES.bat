@echo off
REM ========================================
REM Wolf Pack V2 - Daily Outcomes Update
REM Run once daily to update trading outcomes
REM ========================================

SETLOCAL EnableDelayedExpansion

if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )

echo.
echo ===============================================
echo   WOLF PACK V2 - OUTCOME TRACKER
echo   Updating Day 2, 3, 5, 10 results
echo ===============================================
echo.

cd /d "%~dp0"

python outcome_tracker.py

echo.
echo Press any key to close...
pause > nul
