# 🐺 WOLF BRAIN 4 AM AUTO-SCANNER SETUP
# 
# This script sets up Windows Task Scheduler to run
# the Wolf Brain at 4 AM every weekday.
#
# RUN THIS ONCE AS ADMINISTRATOR to set up the schedule.

Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🐺 WOLF BRAIN 4 AM SCHEDULER SETUP                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

"@

$scriptPath = Join-Path $PSScriptRoot "wolf_brain_4am.bat"

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  This script needs to run as Administrator to create scheduled task." -ForegroundColor Yellow
    Write-Host "   Right-click PowerShell and 'Run as Administrator', then run this script again." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit
}

Write-Host "Creating scheduled task for 4 AM daily scan..." -ForegroundColor Cyan

# Create the scheduled task
$action = New-ScheduledTaskAction -Execute $scriptPath -Argument "auto"
$trigger = New-ScheduledTaskTrigger -Daily -At 4:00AM
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -WakeToRun

try {
    # Remove existing task if it exists
    Unregister-ScheduledTask -TaskName "WolfBrain4AM" -Confirm:$false -ErrorAction SilentlyContinue
    
    # Create new task
    Register-ScheduledTask -TaskName "WolfBrain4AM" -Action $action -Trigger $trigger -Settings $settings -Description "Wolf Brain 4 AM Premarket Scanner - Generates intel report for morning review"
    
    Write-Host ""
    Write-Host "✅ SUCCESS! Wolf Brain scheduled for 4 AM daily." -ForegroundColor Green
    Write-Host ""
    Write-Host "The brain will:" -ForegroundColor Cyan
    Write-Host "  • Wake up at 4:00 AM" -ForegroundColor White
    Write-Host "  • Scan ALL premarket gainers" -ForegroundColor White
    Write-Host "  • Classify RUNNERS vs FADERS" -ForegroundColor White
    Write-Host "  • Generate INTEL REPORT" -ForegroundColor White
    Write-Host "  • Save to: data\wolf_brain\LATEST_INTEL_REPORT.txt" -ForegroundColor White
    Write-Host ""
    Write-Host "When you wake up at 7 AM, just open the report!" -ForegroundColor Yellow
    Write-Host ""
    
} catch {
    Write-Host "❌ Failed to create task: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "To manually trigger the scan anytime:" -ForegroundColor Cyan
Write-Host "  python src\wolf_brain\autonomous_brain.py --report" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
