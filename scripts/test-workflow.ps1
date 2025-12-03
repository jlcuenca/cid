# Test workflow execution
Write-Host "🧪 Testing CCA Workflow"
Write-Host "======================="
Write-Host ""

# Get project and region
$PROJECT_ID = gcloud config get-value project
$REGION = "us-central1"

Write-Host "📋 Project: $PROJECT_ID"
Write-Host "📍 Region: $REGION"
Write-Host ""

# Test data
$testEvent = @{
    data = @{
        student_id    = "TEST-12345"
        course_id     = "MATH101"
        evaluation_id = "final_exam"
        score         = 85
        timestamp     = (Get-Date).ToUniversalTime().ToString("o")
    }
} | ConvertTo-Json -Depth 3

Write-Host "📤 Test Event:"
Write-Host $testEvent
Write-Host ""

# Execute workflow
Write-Host "🚀 Executing workflow..."
$execution = gcloud workflows execute cca-badge-issue-flow `
    --location=$REGION `
    --data=$testEvent `
    --format=json | ConvertFrom-Json

$executionId = $execution.name.Split('/')[-1]

Write-Host "✅ Workflow execution started!"
Write-Host "📋 Execution ID: $executionId"
Write-Host ""

# Wait a bit for execution
Write-Host "⏳ Waiting for execution to complete..."
Start-Sleep -Seconds 5

# Get execution details
Write-Host "📊 Execution details:"
gcloud workflows executions describe $executionId `
    --workflow=cca-badge-issue-flow `
    --location=$REGION

Write-Host ""
Write-Host "📝 To view logs:"
Write-Host "gcloud logging read 'resource.type=workflows.googleapis.com/Workflow' --limit=50"
Write-Host ""
Write-Host "📊 To list all executions:"
Write-Host "gcloud workflows executions list cca-badge-issue-flow --location=$REGION"
