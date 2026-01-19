@echo off
REM 🐺 FENRIR V2 - Quick Launch

echo.
echo ====================================
echo   🐺 FENRIR V2 - AI TRADING SECRETARY
echo ====================================
echo.
echo Quick Commands:
echo   python fenrir_secretary.py briefing    - Morning summary
echo   python fenrir_secretary.py risk        - Risk check
echo   python fenrir_secretary.py catalysts   - Upcoming events
echo   python fenrir_secretary.py eod         - End of day report
echo   python fenrir_secretary.py afterhours  - After-hours monitor
echo.
echo   python main.py chat                    - Full chat mode
echo   python main.py scan                    - Market scanner
echo   python main.py holdings                - Show positions
echo.
echo Starting chat mode...
echo.

cd /d "%~dp0"
python main.py chat

pause
