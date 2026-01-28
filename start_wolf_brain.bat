@echo off
REM Wolf Brain 24/7 Launcher
REM Run this to start the autonomous brain

REM Set API Keys (fill these in!)
set APCA_API_KEY_ID=PKW2ON6GMKIUXKBC7L3GY4MJ2A
set APCA_API_SECRET_KEY=9S25KmeAhaRPzXg4LFqcsh9YBuxQ3whzp5LavrPvSrTN

REM Finnhub (already working)
set FINNHUB_API_KEY=d5jddu1r01qh37ujsqrgd5jddu1r01qh37ujsqs0

REM NewsAPI (already working)
set NEWSAPI_KEY=e6f793dfd61f473786f69466f9313fe8

REM Navigate to src directory
cd /d %~dp0src

REM Start the autonomous brain
echo Starting Wolf Brain 24/7...
echo Press Ctrl+C to stop
python wolf_brain\autonomous_brain.py %*
