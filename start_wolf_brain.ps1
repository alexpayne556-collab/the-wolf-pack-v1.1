# Wolf Brain 24/7 Launcher - PowerShell Version
# 
# USAGE:
#   .\start_wolf_brain.ps1                    # Normal 24/7 mode
#   .\start_wolf_brain.ps1 --background       # Run hidden 24/7
#   .\start_wolf_brain.ps1 --scan             # Force 4AM scan NOW
#   .\start_wolf_brain.ps1 --analyze AQST     # Deep analysis of ticker
#   .\start_wolf_brain.ps1 --dry-run          # No real trades
#   .\start_wolf_brain.ps1 --once             # Run one cycle and exit

Write-Host @"
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     🐺 WOLF BRAIN 24/7 LAUNCHER                              ║
    ║                                                              ║
    ║     EQUIPPED WITH:                                           ║
    ║     • 4AM Premarket Scanner                                  ║
    ║     • FDA Calendar Intelligence                              ║
    ║     • Runner vs Fader Classification                         ║
    ║     • Biotech Formula Detection                              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
"@

# Set API Keys
$env:APCA_API_KEY_ID = "PKW2ON6GMKIUXKBC7L3GY4MJ2A"
$env:APCA_API_SECRET_KEY = "9S25KmeAhaRPzXg4LFqcsh9YBuxQ3whzp5LavrPvSrTN"
$env:FINNHUB_API_KEY = "d5jddu1r01qh37ujsqrgd5jddu1r01qh37ujsqs0"
$env:NEWSAPI_KEY = "e6f793dfd61f473786f69466f9313fe8"

# Navigate to src
Set-Location $PSScriptRoot\src

# Check for --background flag first
if ($args -contains "--background") {
    Write-Host "Starting in BACKGROUND mode (24/7)..."
    Write-Host "Logs at: data\wolf_brain\"
    
    # Remove --background from args and pass rest
    $otherArgs = $args | Where-Object { $_ -ne "--background" }
    $argString = $otherArgs -join " "
    
    Start-Process python -ArgumentList "wolf_brain\autonomous_brain.py $argString" -WindowStyle Hidden
    Write-Host "✅ Wolf Brain running in background!"
} else {
    # Show mode based on args
    if ($args -contains "--scan") {
        Write-Host "Mode: 4AM PREMARKET SCAN" -ForegroundColor Green
    } elseif ($args -contains "--analyze") {
        Write-Host "Mode: DEEP ANALYSIS" -ForegroundColor Cyan
    } elseif ($args -contains "--dry-run") {
        Write-Host "Mode: DRY RUN (no trades)" -ForegroundColor Yellow
    } else {
        Write-Host "Mode: 24/7 AUTONOMOUS" -ForegroundColor Green
    }
    
    Write-Host "Press Ctrl+C to stop"
    Write-Host ""
    
    # Pass any arguments through
    $argString = $args -join " "
    python wolf_brain\autonomous_brain.py $argString
}
