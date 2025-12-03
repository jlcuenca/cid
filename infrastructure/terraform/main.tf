terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "cloudfunctions.googleapis.com",
    "workflows.googleapis.com",
    "pubsub.googleapis.com",
    "secretmanager.googleapis.com",
    "firestore.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudscheduler.googleapis.com",
  ])
  
  service            = each.key
  disable_on_destroy = false
}

# Service Account for Cloud Functions
resource "google_service_account" "cca_functions" {
  account_id   = "cca-functions-sa"
  display_name = "CCA Cloud Functions Service Account"
  description  = "Service account for CCA Cloud Functions execution"
}

# Pub/Sub Topic for Moodle Events
resource "google_pubsub_topic" "moodle_events" {
  name = "moodle-evaluation-events"
  
  labels = {
    environment = var.environment
    component   = "cca"
  }
  
  depends_on = [google_project_service.required_apis]
}

# Firestore Database (Native Mode)
resource "google_firestore_database" "cca_database" {
  name        = "(default)"
  location_id = var.firestore_location
  type        = "FIRESTORE_NATIVE"
  
  depends_on = [google_project_service.required_apis]
}

# Secret Manager Secrets
resource "google_secret_manager_secret" "acreditta_api_key" {
  secret_id = "acreditta-api-key"
  
  replication {
    auto {}
  }
  
  labels = {
    environment = var.environment
    component   = "cca"
  }
  
  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret" "sis_db_user" {
  secret_id = "sis-db-user"
  
  replication {
    auto {}
  }
  
  labels = {
    environment = var.environment
    component   = "cca"
  }
  
  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret" "sis_db_pass" {
  secret_id = "sis-db-pass"
  
  replication {
    auto {}
  }
  
  labels = {
    environment = var.environment
    component   = "cca"
  }
  
  depends_on = [google_project_service.required_apis]
}

# Secret versions with placeholder values
resource "google_secret_manager_secret_version" "acreditta_api_key_v1" {
  secret      = google_secret_manager_secret.acreditta_api_key.id
  secret_data = "PLACEHOLDER_UPDATE_AFTER_DEPLOYMENT"
}

resource "google_secret_manager_secret_version" "sis_db_user_v1" {
  secret      = google_secret_manager_secret.sis_db_user.id
  secret_data = "PLACEHOLDER_UPDATE_AFTER_DEPLOYMENT"
}

resource "google_secret_manager_secret_version" "sis_db_pass_v1" {
  secret      = google_secret_manager_secret.sis_db_pass.id
  secret_data = "PLACEHOLDER_UPDATE_AFTER_DEPLOYMENT"
}

# IAM bindings for secrets
resource "google_secret_manager_secret_iam_member" "acreditta_key_access" {
  secret_id = google_secret_manager_secret.acreditta_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cca_functions.email}"
}

resource "google_secret_manager_secret_iam_member" "sis_user_access" {
  secret_id = google_secret_manager_secret.sis_db_user.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cca_functions.email}"
}

resource "google_secret_manager_secret_iam_member" "sis_pass_access" {
  secret_id = google_secret_manager_secret.sis_db_pass.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cca_functions.email}"
}

# Cloud Storage bucket for function source code
resource "google_storage_bucket" "function_source" {
  name     = "${var.project_id}-cca-functions"
  location = var.region
  
  uniform_bucket_level_access = true
  
  labels = {
    environment = var.environment
    component   = "cca"
  }
}

# Archive source code for functions
data "archive_file" "validate_rule_source" {
  type        = "zip"
  source_dir  = "${path.module}/../../functions/validate_rule"
  output_path = "${path.module}/../../build/validate_rule.zip"
}

data "archive_file" "call_acreditta_source" {
  type        = "zip"
  source_dir  = "${path.module}/../../functions/call_acreditta"
  output_path = "${path.module}/../../build/call_acreditta.zip"
}

data "archive_file" "update_sis_source" {
  type        = "zip"
  source_dir  = "${path.module}/../../functions/update_sis"
  output_path = "${path.module}/../../build/update_sis.zip"
}

# Upload function source to Cloud Storage
resource "google_storage_bucket_object" "validate_rule_source" {
  name   = "validate_rule-${data.archive_file.validate_rule_source.output_md5}.zip"
  bucket = google_storage_bucket.function_source.name
  source = data.archive_file.validate_rule_source.output_path
}

resource "google_storage_bucket_object" "call_acreditta_source" {
  name   = "call_acreditta-${data.archive_file.call_acreditta_source.output_md5}.zip"
  bucket = google_storage_bucket.function_source.name
  source = data.archive_file.call_acreditta_source.output_path
}

resource "google_storage_bucket_object" "update_sis_source" {
  name   = "update_sis-${data.archive_file.update_sis_source.output_md5}.zip"
  bucket = google_storage_bucket.function_source.name
  source = data.archive_file.update_sis_source.output_path
}

# Cloud Function 1: Validate Rule
resource "google_cloudfunctions2_function" "validate_rule" {
  name        = "cca-validate-rule"
  location    = var.region
  description = "Validates badge issuance rules from Firestore"
  
  build_config {
    runtime     = var.function_runtime
    entry_point = "validate_rule"
    
    source {
      storage_source {
        bucket = google_storage_bucket.function_source.name
        object = google_storage_bucket_object.validate_rule_source.name
      }
    }
  }
  
  service_config {
    max_instance_count    = var.function_max_instances
    min_instance_count    = var.function_min_instances
    available_memory      = var.function_memory
    timeout_seconds       = var.function_timeout
    service_account_email = google_service_account.cca_functions.email
    
    environment_variables = {
      GCP_PROJECT_ID = var.project_id
      ENVIRONMENT    = var.environment
    }
  }
  
  labels = {
    environment = var.environment
    component   = "cca"
    function    = "validate-rule"
  }
  
  depends_on = [google_project_service.required_apis]
}

# Cloud Function 2: Call Acreditta
resource "google_cloudfunctions2_function" "call_acreditta" {
  name        = "cca-call-acreditta"
  location    = var.region
  description = "Calls Acreditta API to issue digital badges"
  
  build_config {
    runtime     = var.function_runtime
    entry_point = "call_acreditta"
    
    source {
      storage_source {
        bucket = google_storage_bucket.function_source.name
        object = google_storage_bucket_object.call_acreditta_source.name
      }
    }
  }
  
  service_config {
    max_instance_count    = var.function_max_instances
    min_instance_count    = var.function_min_instances
    available_memory      = var.function_memory
    timeout_seconds       = var.function_timeout
    service_account_email = google_service_account.cca_functions.email
    
    environment_variables = {
      GCP_PROJECT_ID       = var.project_id
      ENVIRONMENT          = var.environment
      ACREDITTA_API_URL    = var.acreditta_api_url
      ACREDITTA_SECRET_ID  = google_secret_manager_secret.acreditta_api_key.secret_id
    }
  }
  
  labels = {
    environment = var.environment
    component   = "cca"
    function    = "call-acreditta"
  }
  
  depends_on = [google_project_service.required_apis]
}

# Cloud Function 3: Update SIS
resource "google_cloudfunctions2_function" "update_sis" {
  name        = "cca-update-sis"
  location    = var.region
  description = "Updates SIS database and logs audit events"
  
  build_config {
    runtime     = var.function_runtime
    entry_point = "update_sis"
    
    source {
      storage_source {
        bucket = google_storage_bucket.function_source.name
        object = google_storage_bucket_object.update_sis_source.name
      }
    }
  }
  
  service_config {
    max_instance_count    = var.function_max_instances
    min_instance_count    = var.function_min_instances
    available_memory      = var.function_memory
    timeout_seconds       = var.function_timeout
    service_account_email = google_service_account.cca_functions.email
    
    environment_variables = {
      GCP_PROJECT_ID      = var.project_id
      ENVIRONMENT         = var.environment
      SIS_DB_HOST         = var.sis_db_host
      SIS_DB_NAME         = var.sis_db_name
      SIS_USER_SECRET_ID  = google_secret_manager_secret.sis_db_user.secret_id
      SIS_PASS_SECRET_ID  = google_secret_manager_secret.sis_db_pass.secret_id
    }
  }
  
  labels = {
    environment = var.environment
    component   = "cca"
    function    = "update-sis"
  }
  
  depends_on = [google_project_service.required_apis]
}

# IAM permissions for functions
resource "google_project_iam_member" "functions_firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.cca_functions.email}"
}

resource "google_project_iam_member" "functions_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.cca_functions.email}"
}

# Cloud Workflow
resource "google_workflows_workflow" "cca_badge_issue_flow" {
  name            = "cca-badge-issue-flow"
  region          = var.region
  description     = "Orchestrates badge issuance: VALIDATE → EMIT → NOTIFY"
  service_account = google_service_account.cca_functions.email
  
  source_contents = templatefile("${path.module}/workflow.yaml", {
    validate_rule_url  = google_cloudfunctions2_function.validate_rule.service_config[0].uri
    call_acreditta_url = google_cloudfunctions2_function.call_acreditta.service_config[0].uri
    update_sis_url     = google_cloudfunctions2_function.update_sis.service_config[0].uri
  })
  
  labels = {
    environment = var.environment
    component   = "cca"
  }
  
  depends_on = [
    google_project_service.required_apis,
    google_cloudfunctions2_function.validate_rule,
    google_cloudfunctions2_function.call_acreditta,
    google_cloudfunctions2_function.update_sis
  ]
}

# Pub/Sub subscription to trigger workflow
resource "google_pubsub_subscription" "workflow_trigger" {
  name  = "moodle-events-workflow-trigger"
  topic = google_pubsub_topic.moodle_events.name
  
  push_config {
    push_endpoint = "https://workflowexecutions.googleapis.com/v1/${google_workflows_workflow.cca_badge_issue_flow.id}/executions"
    
    oidc_token {
      service_account_email = google_service_account.cca_functions.email
    }
  }
  
  ack_deadline_seconds = 600
  
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
  
  labels = {
    environment = var.environment
    component   = "cca"
  }
}

# IAM for workflow invocation
resource "google_project_iam_member" "workflow_invoker" {
  project = var.project_id
  role    = "roles/workflows.invoker"
  member  = "serviceAccount:${google_service_account.cca_functions.email}"
}

resource "google_cloudfunctions2_function_iam_member" "validate_rule_invoker" {
  project        = google_cloudfunctions2_function.validate_rule.project
  location       = google_cloudfunctions2_function.validate_rule.location
  cloud_function = google_cloudfunctions2_function.validate_rule.name
  role           = "roles/cloudfunctions.invoker"
  member         = "serviceAccount:${google_service_account.cca_functions.email}"
}

resource "google_cloudfunctions2_function_iam_member" "call_acreditta_invoker" {
  project        = google_cloudfunctions2_function.call_acreditta.project
  location       = google_cloudfunctions2_function.call_acreditta.location
  cloud_function = google_cloudfunctions2_function.call_acreditta.name
  role           = "roles/cloudfunctions.invoker"
  member         = "serviceAccount:${google_service_account.cca_functions.email}"
}

resource "google_cloudfunctions2_function_iam_member" "update_sis_invoker" {
  project        = google_cloudfunctions2_function.update_sis.project
  location       = google_cloudfunctions2_function.update_sis.location
  cloud_function = google_cloudfunctions2_function.update_sis.name
  role           = "roles/cloudfunctions.invoker"
  member         = "serviceAccount:${google_service_account.cca_functions.email}"
}
