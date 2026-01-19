@echo off
REM ========================================
REM Wolf Pack V2 - Log a Trade
REM Quick decision logging
REM ========================================

SETLOCAL EnableDelayedExpansion

REM Keep window open
if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )

echo.
echo ===============================================
echo   WOLF PACK V2 - DECISION LOGGER
echo ===============================================
echo.

cd /d "%~dp0"

python decision_logger.py

echo.
echo Press any key to close...
pause > nul
