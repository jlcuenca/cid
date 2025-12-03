#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Prepares Cloud Functions for deployment by copying the common module.

.DESCRIPTION
    This script copies the common module into each Cloud Function directory
    to ensure all dependencies are included in the deployment package.
    It also cleans up any previous builds.

.EXAMPLE
    .\prepare-functions.ps1
#>

param(
    [switch]$Clean = $false
)

$ErrorActionPreference = "Stop"

# Get the project root directory
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$FunctionsDir = Join-Path $ProjectRoot "functions"
$CommonDir = Join-Path $FunctionsDir "common"
$BuildDir = Join-Path $ProjectRoot "build"

Write-Host "=== CCA Function Preparation ===" -ForegroundColor Cyan
Write-Host "Project Root: $ProjectRoot" -ForegroundColor Gray
Write-Host ""

# Function to copy common module
function Copy-CommonModule {
    param(
        [string]$FunctionName
    )
    
    $FunctionDir = Join-Path $FunctionsDir $FunctionName
    $TargetCommonDir = Join-Path $FunctionDir "common"
    
    Write-Host "Processing: $FunctionName" -ForegroundColor Yellow
    
    # Remove existing common directory if it exists
    if (Test-Path $TargetCommonDir) {
        Write-Host "  - Removing existing common module..." -ForegroundColor Gray
        Remove-Item -Path $TargetCommonDir -Recurse -Force
    }
    
    # Copy common module
    Write-Host "  - Copying common module..." -ForegroundColor Gray
    Copy-Item -Path $CommonDir -Destination $TargetCommonDir -Recurse -Force
    
    # Remove __pycache__ directories
    Get-ChildItem -Path $TargetCommonDir -Filter "__pycache__" -Recurse -Directory | 
    Remove-Item -Recurse -Force
    
    Write-Host "  ✓ Complete" -ForegroundColor Green
}

# Clean build directory if requested
if ($Clean) {
    Write-Host "Cleaning build directory..." -ForegroundColor Yellow
    if (Test-Path $BuildDir) {
        Remove-Item -Path $BuildDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $BuildDir -Force | Out-Null
    Write-Host "✓ Build directory cleaned" -ForegroundColor Green
    Write-Host ""
}

# Verify common module exists
if (-not (Test-Path $CommonDir)) {
    Write-Host "ERROR: Common module not found at: $CommonDir" -ForegroundColor Red
    exit 1
}

# List of Cloud Functions
$Functions = @("validate_rule", "call_acreditta", "update_sis")

# Process each function
foreach ($Function in $Functions) {
    $FunctionPath = Join-Path $FunctionsDir $Function
    
    if (-not (Test-Path $FunctionPath)) {
        Write-Host "WARNING: Function directory not found: $Function" -ForegroundColor Yellow
        continue
    }
    
    Copy-CommonModule -FunctionName $Function
}

Write-Host ""
Write-Host "=== Preparation Complete ===" -ForegroundColor Green
Write-Host "Functions are ready for deployment!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. cd infrastructure/terraform" -ForegroundColor Gray
Write-Host "  2. terraform init" -ForegroundColor Gray
Write-Host "  3. terraform plan" -ForegroundColor Gray
Write-Host "  4. terraform apply" -ForegroundColor Gray
