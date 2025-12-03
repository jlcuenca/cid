# 📝 Terraform Configuration Guide

## Step 1: Configure Your GCP Project Settings

You need to create a `terraform.tfvars` file with your specific configuration. This file will contain your GCP project details and service configurations.

### Required Information

Before creating the file, gather the following information:

#### 1. **GCP Project ID** (Required)
Your Google Cloud Project ID where the infrastructure will be deployed.

**How to find it:**
```powershell
gcloud config get-value project
```

Or check in [GCP Console](https://console.cloud.google.com) → Project selector (top bar)

---

#### 2. **GCP Region** (Optional - Default: `us-central1`)
The region where your Cloud Functions and other resources will be deployed.

**Common options:**
- `us-central1` (Iowa, USA)
- `us-east1` (South Carolina, USA)
- `europe-west1` (Belgium)
- `asia-southeast1` (Singapore)

[Full list of regions](https://cloud.google.com/compute/docs/regions-zones)

---

#### 3. **Environment** (Optional - Default: `dev`)
Environment identifier for resource labeling.

**Options:** `dev`, `staging`, `prod`

---

#### 4. **Acreditta API URL** (Optional - Default: `https://api.acreditta.com/v1`)
The base URL for the Acreditta API.

Use default unless you have a custom Acreditta instance.

---

#### 5. **SIS Database Configuration** (Optional)
If you have a legacy SIS database to integrate:

- **SIS DB Host**: Database hostname (e.g., `sis-db.example.com`)
- **SIS DB Name**: Database name (e.g., `sis_production`)

**Note:** You can skip this initially and add it later when ready to integrate with SIS.

---

## Example Configuration

Here's what your `terraform.tfvars` file should look like:

```hcl
# GCP Project Configuration
project_id = "my-edu-project-12345"    # ← Replace with YOUR project ID
region     = "us-central1"              # ← Change if needed

# Environment
environment = "dev"                     # ← dev, staging, or prod

# Firestore
firestore_location = "us-central"       # ← Should match region

# Cloud Functions Configuration
function_runtime       = "python311"
function_memory        = "512Mi"
function_timeout       = 300
function_max_instances = 10
function_min_instances = 0

# External Services
acreditta_api_url = "https://api.acreditta.com/v1"  # ← Your Acreditta URL

# SIS Database (Legacy System) - Optional
sis_db_host = ""                        # ← Leave empty if not using SIS yet
sis_db_name = "sis_production"
```

---

## Next Steps

Once you have this information:

1. I'll create the `terraform.tfvars` file for you
2. We'll validate the configuration
3. Then proceed with `terraform init` and `terraform plan`

---

## Quick Start (If You Just Want to Test)

If you just want to test the infrastructure without SIS integration:

**Minimum required:**
- GCP Project ID

**Can use defaults for:**
- Region: `us-central1`
- Environment: `dev`
- Acreditta URL: `https://api.acreditta.com/v1`
- SIS Host: Leave empty (skip SIS integration)

---

## What Information Do You Have?

Please provide:
1. Your GCP Project ID
2. (Optional) Preferred region
3. (Optional) Acreditta API URL if different from default
4. (Optional) SIS database details if ready to integrate
