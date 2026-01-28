#!/bin/bash
# Wolf Brain 24/7 Launcher
# Run this to start the autonomous brain

# Set API Keys (fill these in!)
export APCA_API_KEY_ID="PKW2ON6GMKIUXKBC7L3GY4MJ2A"
export APCA_API_SECRET_KEY="9S25KmeAhaRPzXg4LFqcsh9YBuxQ3whzp5LavrPvSrTN"

# Finnhub (already working)
export FINNHUB_API_KEY="d5jddu1r01qh37ujsqrgd5jddu1r01qh37ujsqs0"

# NewsAPI (already working)
export NEWSAPI_KEY="e6f793dfd61f473786f69466f9313fe8"

# Navigate to src directory
cd "$(dirname "$0")/src"

# Start the autonomous brain
echo "Starting Wolf Brain 24/7..."
echo "Press Ctrl+C to stop"
python wolf_brain/autonomous_brain.py "$@"
