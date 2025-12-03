$ErrorActionPreference = "Stop"

# Get the project root directory
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$FunctionsDir = Join-Path $ProjectRoot "functions"
$BuildDir = Join-Path $ProjectRoot "build"

Write-Host "=== CCA Function Cleanup ===" -ForegroundColor Cyan
Write-Host ""

# List of Cloud Functions
$Functions = @("validate_rule", "call_acreditta", "update_sis")

# Clean each function
foreach ($Function in $Functions) {
    $FunctionDir = Join-Path $FunctionsDir $Function
    $CommonDir = Join-Path $FunctionDir "common"
    
    if (Test-Path $CommonDir) {
        Write-Host "Removing common module from: $Function" -ForegroundColor Yellow
        Remove-Item -Path $CommonDir -Recurse -Force
        Write-Host "  Removed" -ForegroundColor Green
    }
}

# Clean build directory
if (Test-Path $BuildDir) {
    Write-Host "Cleaning build directory..." -ForegroundColor Yellow
    Remove-Item -Path $BuildDir -Recurse -Force
    Write-Host "  Removed" -ForegroundColor Green
}

# Clean __pycache__ directories
Write-Host "Cleaning __pycache__ directories..." -ForegroundColor Yellow
$pycacheDirs = Get-ChildItem -Path $FunctionsDir -Filter "__pycache__" -Recurse -Directory
if ($pycacheDirs) {
    foreach ($dir in $pycacheDirs) {
        Remove-Item -Path $dir.FullName -Recurse -Force
    }
}
Write-Host "  Removed" -ForegroundColor Green

Write-Host ""
Write-Host "=== Cleanup Complete ===" -ForegroundColor Green
