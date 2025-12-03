#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Local testing script for CCA Cloud Functions.

.DESCRIPTION
    Starts Cloud Functions locally using functions-framework for testing.
    Each function runs on a different port for isolated testing.

.PARAMETER Function
    Specific function to test: validate_rule, call_acreditta, update_sis, or all

.EXAMPLE
    .\test-local.ps1 -Function validate_rule
    
.EXAMPLE
    .\test-local.ps1 -Function all
#>

param(
    [ValidateSet("validate_rule", "call_acreditta", "update_sis", "all")]
    [string]$Function = "all"
)

$ErrorActionPreference = "Stop"

# Get directories
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$FunctionsDir = Join-Path $ProjectRoot "functions"
$TestsDir = Join-Path $ProjectRoot "tests"
$SampleDataFile = Join-Path $TestsDir "sample_data.json"

Write-Host "=== CCA Local Testing ===" -ForegroundColor Cyan
Write-Host ""

# Check if sample data exists
if (-not (Test-Path $SampleDataFile)) {
    Write-Host "ERROR: Sample data file not found: $SampleDataFile" -ForegroundColor Red
    exit 1
}

# Load sample data
$SampleData = Get-Content $SampleDataFile | ConvertFrom-Json

# Function configurations
$FunctionConfigs = @{
    validate_rule  = @{
        Port     = 8080
        Target   = "validate_rule"
        TestData = $SampleData.validation_request | ConvertTo-Json -Compress
    }
    call_acreditta = @{
        Port     = 8081
        Target   = "call_acreditta"
        TestData = $SampleData.badge_issue_request | ConvertTo-Json -Compress
    }
    update_sis     = @{
        Port     = 8082
        Target   = "update_sis"
        TestData = $SampleData.sis_update_request | ConvertTo-Json -Compress
    }
}

function Start-FunctionLocal {
    param(
        [string]$FunctionName
    )
    
    $Config = $FunctionConfigs[$FunctionName]
    $FunctionPath = Join-Path $FunctionsDir $FunctionName
    
    Write-Host "Starting $FunctionName on port $($Config.Port)..." -ForegroundColor Yellow
    Write-Host "  Directory: $FunctionPath" -ForegroundColor Gray
    Write-Host "  Target: $($Config.Target)" -ForegroundColor Gray
    Write-Host ""
    
    # Set environment variables
    $env:GCP_PROJECT_ID = "test-project"
    $env:ENVIRONMENT = "local"
    
    # Start function
    Push-Location $FunctionPath
    try {
        Write-Host "Run this command in a new terminal:" -ForegroundColor Cyan
        Write-Host "  cd $FunctionPath" -ForegroundColor White
        Write-Host "  functions-framework --target=$($Config.Target) --port=$($Config.Port) --debug" -ForegroundColor White
        Write-Host ""
        Write-Host "Test with curl:" -ForegroundColor Cyan
        Write-Host "  curl -X POST http://localhost:$($Config.Port) -H 'Content-Type: application/json' -d '$($Config.TestData)'" -ForegroundColor White
        Write-Host ""
    }
    finally {
        Pop-Location
    }
}

# Display instructions
if ($Function -eq "all") {
    Write-Host "To test all functions, open 3 separate terminals and run:" -ForegroundColor Cyan
    Write-Host ""
    
    foreach ($FuncName in $FunctionConfigs.Keys) {
        $Config = $FunctionConfigs[$FuncName]
        Write-Host "Terminal $($FunctionConfigs.Keys.IndexOf($FuncName) + 1): $FuncName" -ForegroundColor Yellow
        Write-Host "  cd $FunctionsDir\$FuncName" -ForegroundColor Gray
        Write-Host "  functions-framework --target=$($Config.Target) --port=$($Config.Port) --debug" -ForegroundColor White
        Write-Host ""
    }
    
    Write-Host "Then test each function:" -ForegroundColor Cyan
    Write-Host ""
    
    foreach ($FuncName in $FunctionConfigs.Keys) {
        $Config = $FunctionConfigs[$FuncName]
        Write-Host "$FuncName (port $($Config.Port)):" -ForegroundColor Yellow
        Write-Host "  curl -X POST http://localhost:$($Config.Port) -H 'Content-Type: application/json' -d '$($Config.TestData)'" -ForegroundColor White
        Write-Host ""
    }
}
else {
    Start-FunctionLocal -FunctionName $Function
}

Write-Host "=== Testing Guide ===" -ForegroundColor Green
Write-Host ""
Write-Host "Prerequisites:" -ForegroundColor Cyan
Write-Host "  1. Install functions-framework: pip install functions-framework" -ForegroundColor Gray
Write-Host "  2. Install dependencies: pip install -r requirements.txt" -ForegroundColor Gray
Write-Host ""
Write-Host "Note: For local testing, Secret Manager and Firestore calls will fail." -ForegroundColor Yellow
Write-Host "      You may need to mock these services or use emulators." -ForegroundColor Yellow
