# setup_codessa_sa.ps1
param (
    [string]$ProjectId = "codessa-devos-2025",
    [string]$SaName = "codessa-devos-admin"
)

$SaEmail = "$SaName@$ProjectId.iam.gserviceaccount.com"

# Enable required APIs
Write-Host "Enabling required APIs..."
gcloud services enable `
    datastore.googleapis.com `
    cloudfunctions.googleapis.com `
    secretmanager.googleapis.com `
    aiplatform.googleapis.com `
    storage.googleapis.com `
    iam.googleapis.com `
    --project $ProjectId

# Check if service account exists
try {
    gcloud iam service-accounts describe $SaEmail --project $ProjectId | Out-Null
    Write-Host "Service account $SaEmail already exists."
}
catch {
    Write-Host "Creating service account $SaEmail..."
    gcloud iam service-accounts create $SaName `
        --display-name "Codessa DevOS Admin" `
        --project $ProjectId
}

# Assign roles
$roles = @(
    "roles/datastore.user",
    "roles/cloudfunctions.invoker",
    "roles/secretmanager.secretAccessor",
    "roles/aiplatform.user",
    "roles/storage.objectAdmin"
)

Write-Host "Assigning roles to service account..."
foreach ($role in $roles) {
    Write-Host "Assigning $role ..."
    gcloud projects add-iam-policy-binding $ProjectId `
        --member="serviceAccount:$SaEmail" `
        --role=$role `
        --quiet
}

Write-Host "Setup complete. Service account $SaEmail is ready with required permissions."

# Output the service account email
Write-Host "Service Account Email: $SaEmail"

# Output the project ID
Write-Host "Project ID: $ProjectId"

# Output the roles assigned
Write-Host "Roles assigned:"
foreach ($role in $roles) {
    Write-Host "- $role"
}
# End of setup_codessa_sa.ps1
# This script sets up a service account for Codessa DevOS with necessary permissions.
# It enables required APIs, checks if the service account exists, creates it if not,
# and assigns the necessary roles to the service account.
# Ensure you have the Google Cloud SDK installed and authenticated before running this script.
# Usage: .\setup_codessa_sa.ps1 -ProjectId "your-project-id"


