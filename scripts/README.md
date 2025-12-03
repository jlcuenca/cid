# CCA Scripts Directory

This directory contains PowerShell scripts for building, deploying, and testing the CCA system.

## Scripts Overview

### 🔨 Build Scripts

#### `prepare-functions.ps1`
Prepares Cloud Functions for deployment by copying the common module into each function directory.

```powershell
.\prepare-functions.ps1
.\prepare-functions.ps1 -Clean  # Clean build directory first
```

#### `clean-functions.ps1`
Removes copied common modules and build artifacts. Use before committing changes.

```powershell
.\clean-functions.ps1
```

### 🚀 Deployment Scripts

#### `deploy.ps1`
Complete deployment orchestration script. Handles:
1. Function preparation
2. GCP authentication check
3. Terraform initialization
4. Infrastructure deployment

```powershell
.\deploy.ps1                # Interactive deployment
.\deploy.ps1 -PlanOnly      # Only show what will be deployed
.\deploy.ps1 -AutoApprove   # Skip approval prompts (use with caution)
```

#### `update-secrets.ps1`
Updates Secret Manager secrets with actual credentials.

```powershell
.\update-secrets.ps1
```

#### `init-firestore.ps1`
Initializes Firestore with sample badge issuance rules.

```powershell
.\init-firestore.ps1
.\init-firestore.ps1 -ProjectId "my-project-id"
```

### 🧪 Testing Scripts

#### `test-local.ps1`
Provides instructions for local function testing using functions-framework.

```powershell
.\test-local.ps1 -Function validate_rule
.\test-local.ps1 -Function all
```

## Typical Workflow

### First-Time Deployment

```powershell
# 1. Prepare functions
.\prepare-functions.ps1 -Clean

# 2. Deploy infrastructure
.\deploy.ps1

# 3. Configure secrets
.\update-secrets.ps1

# 4. Initialize Firestore
.\init-firestore.ps1

# 5. Clean up local build artifacts
.\clean-functions.ps1
```

### Local Development & Testing

```powershell
# 1. Test functions locally
.\test-local.ps1 -Function validate_rule

# 2. Make changes to code

# 3. Redeploy
.\prepare-functions.ps1
.\deploy.ps1
.\clean-functions.ps1
```

### Before Committing Changes

```powershell
# Clean up generated files
.\clean-functions.ps1
```

## Prerequisites

- **PowerShell**: Version 5.1 or later (PowerShell Core 7+ recommended)
- **Google Cloud SDK**: `gcloud` CLI installed and configured
- **Terraform**: Version 1.0 or later
- **Python**: 3.11+ with `functions-framework` for local testing

## Environment Setup

```powershell
# Authenticate with GCP
gcloud auth login
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Install Python dependencies
pip install -r ../requirements.txt
pip install functions-framework
```

## Notes

- All scripts use `$ErrorActionPreference = "Stop"` to fail fast on errors
- The `prepare-functions.ps1` script must be run before Terraform deployment
- Copied common modules are gitignored and should not be committed
- Build artifacts are stored in the `build/` directory (also gitignored)
