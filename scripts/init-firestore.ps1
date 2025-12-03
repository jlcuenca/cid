#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Initializes Firestore with sample badge issuance rules.

.DESCRIPTION
    Creates sample emission rules in Firestore for testing the CCA system.
    These rules define when badges should be issued based on course and score criteria.

.PARAMETER ProjectId
    GCP Project ID (defaults to value from terraform.tfvars)

.EXAMPLE
    .\init-firestore.ps1
    
.EXAMPLE
    .\init-firestore.ps1 -ProjectId "my-project-id"
#>

param(
    [string]$ProjectId = ""
)

$ErrorActionPreference = "Stop"

Write-Host "=== Firestore Initialization ===" -ForegroundColor Cyan
Write-Host ""

# Get project ID from terraform.tfvars if not provided
if (-not $ProjectId) {
    $TerraformDir = Join-Path (Split-Path -Parent $PSScriptRoot) "infrastructure" "terraform"
    $TfVarsFile = Join-Path $TerraformDir "terraform.tfvars"
    
    if (Test-Path $TfVarsFile) {
        $content = Get-Content $TfVarsFile
        $projectLine = $content | Where-Object { $_ -match 'project_id\s*=\s*"([^"]+)"' }
        if ($projectLine) {
            $ProjectId = $Matches[1]
            Write-Host "Using project ID from terraform.tfvars: $ProjectId" -ForegroundColor Gray
        }
    }
}

if (-not $ProjectId) {
    Write-Host "ERROR: Project ID not found. Please provide with -ProjectId parameter" -ForegroundColor Red
    exit 1
}

Write-Host "Creating sample rules in Firestore..." -ForegroundColor Yellow
Write-Host ""

# Sample Rule 1: Mathematics Excellence
Write-Host "Creating rule: Mathematics Excellence Badge" -ForegroundColor Cyan
$rule1 = @{
    course_id         = "MATH101"
    evaluation_id     = "final_exam"
    min_score         = 80
    badge_template_id = "math-excellence-2024"
    badge_title       = "Mathematics Excellence"
    active            = $true
    created_at        = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    updated_at        = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
} | ConvertTo-Json -Compress

gcloud firestore documents create `
    --project=$ProjectId `
    --collection=reglas_emision `
    --document-id=rule-math-excellence `
    --data=$rule1

Write-Host "  ✓ Created" -ForegroundColor Green

# Sample Rule 2: Computer Science Achievement
Write-Host "Creating rule: Computer Science Achievement Badge" -ForegroundColor Cyan
$rule2 = @{
    course_id         = "CS101"
    evaluation_id     = "final_project"
    min_score         = 85
    badge_template_id = "cs-achievement-2024"
    badge_title       = "Computer Science Achievement"
    active            = $true
    created_at        = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    updated_at        = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
} | ConvertTo-Json -Compress

gcloud firestore documents create `
    --project=$ProjectId `
    --collection=reglas_emision `
    --document-id=rule-cs-achievement `
    --data=$rule2

Write-Host "  ✓ Created" -ForegroundColor Green

# Sample Rule 3: General Course Completion (any evaluation)
Write-Host "Creating rule: Course Completion Badge" -ForegroundColor Cyan
$rule3 = @{
    course_id         = "GEN100"
    min_score         = 70
    badge_template_id = "course-completion-2024"
    badge_title       = "Course Completion"
    active            = $true
    created_at        = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    updated_at        = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
} | ConvertTo-Json -Compress

gcloud firestore documents create `
    --project=$ProjectId `
    --collection=reglas_emision `
    --document-id=rule-course-completion `
    --data=$rule3

Write-Host "  ✓ Created" -ForegroundColor Green

Write-Host ""
Write-Host "=== Firestore Initialization Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Sample rules created:" -ForegroundColor Cyan
Write-Host "  1. MATH101 final_exam (score ≥ 80) → Mathematics Excellence" -ForegroundColor Gray
Write-Host "  2. CS101 final_project (score ≥ 85) → Computer Science Achievement" -ForegroundColor Gray
Write-Host "  3. GEN100 any evaluation (score ≥ 70) → Course Completion" -ForegroundColor Gray
Write-Host ""
Write-Host "View rules:" -ForegroundColor Cyan
Write-Host "  gcloud firestore documents list --collection=reglas_emision --project=$ProjectId" -ForegroundColor White
