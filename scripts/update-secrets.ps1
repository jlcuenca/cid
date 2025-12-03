# Deploy infrastructure
.\scripts\deploy.sh

# Update secrets
echo "Enter Acreditta API Key:"
$ACREDITTA_KEY = Read-Host -AsSecureString
$ACREDITTA_KEY_PLAIN = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($ACREDITTA_KEY))
echo $ACREDITTA_KEY_PLAIN | gcloud secrets versions add acreditta-api-key --data-file=-

echo "Enter SIS DB User:"
$SIS_USER = Read-Host
echo $SIS_USER | gcloud secrets versions add sis-db-user --data-file=-

echo "Enter SIS DB Password:"
$SIS_PASS = Read-Host -AsSecureString
$SIS_PASS_PLAIN = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($SIS_PASS))
echo $SIS_PASS_PLAIN | gcloud secrets versions add sis-db-pass --data-file=-

Write-Host "✅ Secrets updated successfully!"
