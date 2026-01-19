#!/usr/bin/env pwsh
# ========================================
# Wolf Pack Trading System - Daily Runner
# ========================================

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  WOLF PACK TRADING SYSTEM" -ForegroundColor Cyan
Write-Host "  Daily Data Collection and Analysis" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Python not found!" -ForegroundColor Red
    Write-Host "  Please install Python 3.10+ from python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create data directories if they don't exist
@('data', 'reports', 'data\investigations', 'data\cache') | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
        Write-Host "✓ Created directory: $_" -ForegroundColor Green
    }
}

Write-Host ""

# Function to run script with error handling
function Invoke-WolfPackScript {
    param(
        [string]$ScriptName,
        [string]$Description,
        [int]$StepNumber,
        [int]$TotalSteps,
        [bool]$CriticalStep = $false
    )
    
    Write-Host "[$StepNumber/$TotalSteps] $Description..." -ForegroundColor Cyan
    
    try {
        $output = python $ScriptName 2>&1
        Write-Host $output
        
        if ($LASTEXITCODE -ne 0 -and $CriticalStep) {
            Write-Host "✗ ERROR: $Description failed!" -ForegroundColor Red
            return $false
        } elseif ($LASTEXITCODE -ne 0) {
            Write-Host "⚠ WARNING: $Description had issues" -ForegroundColor Yellow
        } else {
            Write-Host "✓ $Description complete" -ForegroundColor Green
        }
    } catch {
        Write-Host "✗ ERROR: $_" -ForegroundColor Red
        if ($CriticalStep) {
            return $false
        }
    }
    
    Write-Host ""
    return $true
}

# Run the Wolf Pack system
$success = $true

$success = $success -and (Invoke-WolfPackScript -ScriptName "wolfpack_db.py" -Description "Initializing database" -StepNumber 1 -TotalSteps 6 -CriticalStep $true)
if (-not $success) {
    Read-Host "Press Enter to exit"
    exit 1
}

Invoke-WolfPackScript -ScriptName "wolfpack_updater.py" -Description "Updating forward returns" -StepNumber 2 -TotalSteps 6
Invoke-WolfPackScript -ScriptName "wolfpack_recorder.py" -Description "Recording today's data for 99 stocks" -StepNumber 3 -TotalSteps 6 -CriticalStep $true
Invoke-WolfPackScript -ScriptName "move_investigator.py" -Description "Investigating big moves" -StepNumber 4 -TotalSteps 6
Invoke-WolfPackScript -ScriptName "alert_engine.py" -Description "Checking for alerts" -StepNumber 5 -TotalSteps 6
Invoke-WolfPackScript -ScriptName "wolfpack_daily_report.py" -Description "Generating daily report" -StepNumber 6 -TotalSteps 6

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  WOLF PACK SYSTEM COMPLETE" -ForegroundColor Green
Write-Host "  Check reports/ folder for today's summary" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Keep window open
Read-Host "Press Enter to exit"
