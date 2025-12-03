# CCA Test Data

This directory contains sample test data for local and integration testing of the CCA system.

## Files

### `sample_data.json`
Contains sample payloads for testing each Cloud Function:

- **validation_request**: Test data for `validate_rule` function
- **badge_issue_request**: Test data for `call_acreditta` function
- **sis_update_request**: Test data for `update_sis` function
- **workflow_event**: Test data for the complete workflow

## Usage

### Local Function Testing

```bash
# Test validate_rule
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d @sample_data.json | jq '.validation_request'

# Test call_acreditta
curl -X POST http://localhost:8081 \
  -H "Content-Type: application/json" \
  -d @sample_data.json | jq '.badge_issue_request'

# Test update_sis
curl -X POST http://localhost:8082 \
  -H "Content-Type: application/json" \
  -d @sample_data.json | jq '.sis_update_request'
```

### Workflow Testing

```bash
# Execute workflow with sample data
gcloud workflows execute cca-badge-issue-flow \
  --location=us-central1 \
  --data='{"data":{"student_id":"12345","course_id":"MATH101","evaluation_id":"final_exam","score":85,"timestamp":"2025-12-03T12:00:00Z"}}'
```

## Customizing Test Data

Edit `sample_data.json` to test different scenarios:

- Change `score` values to test rule matching thresholds
- Modify `course_id` and `evaluation_id` to test different rules
- Update `student_id` to test with different students
