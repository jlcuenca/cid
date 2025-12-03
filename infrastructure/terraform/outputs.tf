output "pubsub_topic_name" {
  description = "Name of the Pub/Sub topic for Moodle events"
  value       = google_pubsub_topic.moodle_events.name
}

output "pubsub_topic_id" {
  description = "Full resource ID of the Pub/Sub topic"
  value       = google_pubsub_topic.moodle_events.id
}

output "workflow_name" {
  description = "Name of the Cloud Workflow"
  value       = google_workflows_workflow.cca_badge_issue_flow.name
}

output "workflow_id" {
  description = "Full resource ID of the Cloud Workflow"
  value       = google_workflows_workflow.cca_badge_issue_flow.id
}

output "validate_rule_function_url" {
  description = "URL of the validate_rule Cloud Function"
  value       = google_cloudfunctions2_function.validate_rule.service_config[0].uri
}

output "call_acreditta_function_url" {
  description = "URL of the call_acreditta Cloud Function"
  value       = google_cloudfunctions2_function.call_acreditta.service_config[0].uri
}

output "update_sis_function_url" {
  description = "URL of the update_sis Cloud Function"
  value       = google_cloudfunctions2_function.update_sis.service_config[0].uri
}

output "service_account_email" {
  description = "Email of the service account used by functions"
  value       = google_service_account.cca_functions.email
}

output "firestore_database_name" {
  description = "Name of the Firestore database"
  value       = google_firestore_database.cca_database.name
}

output "secret_ids" {
  description = "Map of secret names to their IDs"
  value = {
    acreditta_api_key = google_secret_manager_secret.acreditta_api_key.secret_id
    sis_db_user       = google_secret_manager_secret.sis_db_user.secret_id
    sis_db_pass       = google_secret_manager_secret.sis_db_pass.secret_id
  }
}

output "deployment_instructions" {
  description = "Next steps after Terraform deployment"
  value = <<-EOT
    
    ✅ Infrastructure deployed successfully!
    
    Next steps:
    
    1. Update secrets with actual credentials:
       gcloud secrets versions add ${google_secret_manager_secret.acreditta_api_key.secret_id} --data-file=- <<< "YOUR_ACREDITTA_API_KEY"
       gcloud secrets versions add ${google_secret_manager_secret.sis_db_user.secret_id} --data-file=- <<< "YOUR_SIS_DB_USER"
       gcloud secrets versions add ${google_secret_manager_secret.sis_db_pass.secret_id} --data-file=- <<< "YOUR_SIS_DB_PASS"
    
    2. Initialize Firestore collections:
       - Create 'reglas_emision' collection
       - Create 'registro_evento' collection
    
    3. Configure Moodle webhook to publish to:
       Topic: ${google_pubsub_topic.moodle_events.name}
       Project: ${var.project_id}
    
    4. Test the workflow:
       gcloud workflows execute ${google_workflows_workflow.cca_badge_issue_flow.name} --location=${var.region}
  EOT
}
