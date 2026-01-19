@echo off
REM Simple Python checker that stays open

echo.
echo Checking Python installation...
echo.

where python
if %errorlevel% neq 0 (
    echo.
    echo Python NOT FOUND in PATH
    echo.
    echo You need to install Python first!
    echo See QUICKSTART.md for instructions
    echo.
) else (
    echo.
    echo Python FOUND! Version:
    python --version
    echo.
    echo Python location:
    where python
    echo.
)

echo.
echo Press any key to close...
pause > nul
