#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Complete deployment script for CCA infrastructure.

.DESCRIPTION
    This script orchestrates the complete deployment process:
    1. Prepares Cloud Functions with common module
    2. Initializes Terraform (if needed)
    3. Validates Terraform configuration
    4. Deploys infrastructure to GCP
    5. Provides next steps for secret configuration

.PARAMETER AutoApprove
    Skip Terraform approval prompt (use with caution)

.PARAMETER PlanOnly
    Only run terraform plan without applying changes

.EXAMPLE
    .\deploy.ps1
    
.EXAMPLE
    .\deploy.ps1 -PlanOnly
    
.EXAMPLE
    .\deploy.ps1 -AutoApprove
#>

param(
    [switch]$AutoApprove = $false,
    [switch]$PlanOnly = $false
)

$ErrorActionPreference = "Stop"

# Get directories
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ScriptsDir = Join-Path $ProjectRoot "scripts"
$TerraformDir = Join-Path $ProjectRoot "infrastructure" "terraform"

Write-Host "=== CCA Deployment Script ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Prepare functions
Write-Host "[1/5] Preparing Cloud Functions..." -ForegroundColor Yellow
$PrepareScript = Join-Path $ScriptsDir "prepare-functions.ps1"
& $PrepareScript -Clean
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Function preparation failed" -ForegroundColor Red
    exit 1
}

# Step 2: Check GCP authentication
Write-Host "[2/5] Checking GCP authentication..." -ForegroundColor Yellow
try {
    $account = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
    if ($account) {
        Write-Host "  ✓ Authenticated as: $account" -ForegroundColor Green
    }
    else {
        Write-Host "  ! Not authenticated. Please run: gcloud auth login" -ForegroundColor Yellow
        Write-Host "  ! And also run: gcloud auth application-default login" -ForegroundColor Yellow
        exit 1
    }
}
catch {
    Write-Host "  ! gcloud CLI not found or not configured" -ForegroundColor Yellow
    Write-Host "  ! Please install Google Cloud SDK and authenticate" -ForegroundColor Yellow
    exit 1
}

# Step 3: Initialize Terraform
Write-Host "[3/5] Initializing Terraform..." -ForegroundColor Yellow
Push-Location $TerraformDir
try {
    if (-not (Test-Path ".terraform")) {
        terraform init
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Terraform initialization failed" -ForegroundColor Red
            exit 1
        }
    }
    else {
        Write-Host "  ✓ Terraform already initialized" -ForegroundColor Green
    }
    
    # Step 4: Validate Terraform
    Write-Host "[4/5] Validating Terraform configuration..." -ForegroundColor Yellow
    terraform validate
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Terraform validation failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "  ✓ Configuration is valid" -ForegroundColor Green
    
    # Step 5: Plan/Apply
    if ($PlanOnly) {
        Write-Host "[5/5] Running Terraform plan..." -ForegroundColor Yellow
        terraform plan
    }
    else {
        Write-Host "[5/5] Deploying infrastructure..." -ForegroundColor Yellow
        if ($AutoApprove) {
            terraform apply -auto-approve
        }
        else {
            terraform apply
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "=== Deployment Complete! ===" -ForegroundColor Green
            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Cyan
            Write-Host "  1. Configure secrets:" -ForegroundColor Gray
            Write-Host "     .\scripts\update-secrets.ps1" -ForegroundColor White
            Write-Host ""
            Write-Host "  2. Initialize Firestore with sample rules:" -ForegroundColor Gray
            Write-Host "     .\scripts\init-firestore.ps1" -ForegroundColor White
            Write-Host ""
            Write-Host "  3. Test the workflow:" -ForegroundColor Gray
            Write-Host "     gcloud workflows execute cca-badge-issue-flow --location=us-central1 --data='{...}'" -ForegroundColor White
        }
    }
}
finally {
    Pop-Location
}
