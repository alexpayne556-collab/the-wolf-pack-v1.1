@echo off
REM ========================================
REM Wolf Pack V2 - Pattern Analysis
REM See your trading edge
REM ========================================

SETLOCAL EnableDelayedExpansion

if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )

echo.
echo ===============================================
echo   WOLF PACK V2 - PATTERN LEARNER
echo   Your trading edge revealed
echo ===============================================
echo.

cd /d "%~dp0"

python pattern_learner.py

echo.
echo Press any key to close...
pause > nul
