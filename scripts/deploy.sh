#!/bin/bash

# CCA Infrastructure Deployment Script
# This script deploys the complete CCA infrastructure to GCP

set -e  # Exit on error

echo "🚀 CCA Infrastructure Deployment"
echo "================================="
echo ""

# Check prerequisites
command -v gcloud >/dev/null 2>&1 || { echo "❌ gcloud CLI is required but not installed. Aborting." >&2; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "❌ Terraform is required but not installed. Aborting." >&2; exit 1; }

# Get project ID
if [ -z "$GCP_PROJECT_ID" ]; then
    echo "Enter your GCP Project ID:"
    read GCP_PROJECT_ID
fi

echo "📋 Project ID: $GCP_PROJECT_ID"
echo ""

# Confirm deployment
echo "⚠️  This will deploy infrastructure to GCP project: $GCP_PROJECT_ID"
echo "Continue? (yes/no)"
read CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

# Set GCP project
echo "🔧 Setting GCP project..."
gcloud config set project $GCP_PROJECT_ID

# Navigate to Terraform directory
cd infrastructure/terraform

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    echo "⚠️  terraform.tfvars not found. Creating from example..."
    cp terraform.tfvars.example terraform.tfvars
    echo "📝 Please edit infrastructure/terraform/terraform.tfvars with your configuration."
    echo "Then run this script again."
    exit 1
fi

# Initialize Terraform
echo "📦 Initializing Terraform..."
terraform init

# Validate configuration
echo "✅ Validating Terraform configuration..."
terraform validate

# Plan deployment
echo "📊 Creating deployment plan..."
terraform plan -out=tfplan

# Confirm deployment
echo ""
echo "Review the plan above. Deploy infrastructure? (yes/no)"
read DEPLOY_CONFIRM

if [ "$DEPLOY_CONFIRM" != "yes" ]; then
    echo "Deployment cancelled."
    rm tfplan
    exit 0
fi

# Apply deployment
echo "🚀 Deploying infrastructure..."
terraform apply tfplan

# Clean up plan file
rm tfplan

echo ""
echo "✅ Infrastructure deployed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Update secrets with actual credentials:"
echo "   ./scripts/update-secrets.sh"
echo ""
echo "2. Initialize Firestore collections:"
echo "   ./scripts/init-firestore.sh"
echo ""
echo "3. Configure Moodle webhook to publish to Pub/Sub topic"
echo ""
echo "4. Test the workflow:"
echo "   ./scripts/test-workflow.sh"
