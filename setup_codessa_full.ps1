<#
.SYNOPSIS
    Sets up a Google Cloud service account with necessary permissions and configurations.

.DESCRIPTION
    This script performs the following tasks:
    - Enables required Google Cloud APIs
    - Creates a service account if it doesn't exist
    - Assigns specified IAM roles to the service account
    - Generates a service account key
    - Sets up environment variables and outputs configuration details

.PARAMETER ProjectId
    The Google Cloud project ID. Defaults to "codessa-devos-2025".

.PARAMETER SaName
    The service account name. Defaults to "codessa-devos-admin".

.PARAMETER KeyOutputFolder
    The folder where the service account key will be saved. 
    Defaults to the user's .gcloud/keys directory.

.NOTES
    Requires gcloud CLI to be installed and configured.
    Performs multiple Google Cloud configuration steps in a single script.

.EXAMPLE
    .\setup_codessa_full.ps1 -ProjectId "my-project" -SaName "my-admin-account"
#>
param (
    [string]$ProjectId = "codessa-devos-2025",
    [string]$SaName = "codessa-devos-admin",
    [string]$KeyOutputFolder = "$env:USERPROFILE\.gcloud\keys"
)

$SaEmail = "$SaName@$ProjectId.iam.gserviceaccount.com"

# Ensure gcloud is in your PATH
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Error "gcloud CLI not found. Please install and configure Google Cloud SDK first."
    exit 1
}

# Enable required APIs
Write-Host "Enabling required APIs..."
gcloud services enable `
    datastore.googleapis.com `
    cloudfunctions.googleapis.com `
    secretmanager.googleapis.com `
    aiplatform.googleapis.com `
    storage.googleapis.com `
    iam.googleapis.com `
    --project $ProjectId --quiet

# Check if service account exists
$saExists = $false
try {
    gcloud iam service-accounts describe $SaEmail --project $ProjectId | Out-Null
    $saExists = $true
    Write-Host "Service account $SaEmail already exists."
}
catch {
    Write-Host "Creating service account $SaEmail..."
    gcloud iam service-accounts create $SaName `
        --display-name "Codessa DevOS Admin" `
        --project $ProjectId --quiet
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

# Create keys folder if missing
if (-not (Test-Path -Path $KeyOutputFolder)) {
    Write-Host "Creating key output folder at $KeyOutputFolder"
    New-Item -ItemType Directory -Path $KeyOutputFolder | Out-Null
}

# Create a new service account key
Write-Host "Creating a new service account key..."
$keyFilePath = Join-Path $KeyOutputFolder "$SaName-key-$(Get-Date -Format 'yyyyMMddHHmmss').json"
gcloud iam service-accounts keys create $keyFilePath `
    --iam-account $SaEmail `
    --project $ProjectId --quiet

Write-Host "Service account key saved to: $keyFilePath"

# Set environment variable for current session
$env:GOOGLE_APPLICATION_CREDENTIALS = $keyFilePath
Write-Host "Set GOOGLE_APPLICATION_CREDENTIALS environment variable for this session."

Write-Host "Setup complete! You can now run your app with the configured service account."

# Output the service account email
Write-Host "Service Account Email: $SaEmail"

# Output the project ID
Write-Host "Project ID: $ProjectId"

# Output the roles assigned
Write-Host "Roles assigned:"
foreach ($role in $roles) {
    Write-Host "- $role"
}   
# Output the key file path
Write-Host "Key file path: $keyFilePath"
# Output the key output folder
Write-Host "Key output folder: $KeyOutputFolder"
# Output the GOOGLE_APPLICATION_CREDENTIALS environment variable
Write-Host "GOOGLE_APPLICATION_CREDENTIALS: $env:GOOGLE_APPLICATION_CREDENTIAL
ES"
# Output the current user
Write-Host "Current user: $env:USERNAME"
# Output the current date and time
Write-Host "Current date and time: $(Get-Date -Format 'yyyy-MM-dd HH
:mm:ss')"
# Output the PowerShell version
Write-Host "PowerShell version: $($PSVersionTable.PSVersion)"
# Output the gcloud version
Write-Host "gcloud version: $(gcloud --version)"
# Output the current working directory
Write-Host "Current working directory: $(Get-Location)"
# Output the system architecture
Write-Host "System architecture: $([System.Environment]::Is64BitOperatingSystem ?
    "64-bit" : "32-bit")"
# Output the OS version
Write-Host "OS version: $([System.Environment]::OSVersion.VersionString)"
# Output the .NET version
Write-Host ".NET version: $([System.Environment]::Version.ToString())"
# Output the PATH environment variable
Write-Host "PATH environment variable: $env:PATH"
# Output the user profile directory
Write-Host "User profile directory: $env:USERPROFILE"
# Output the home directory
Write-Host "Home directory: $env:HOMEDRIVE$env:HOMEP
ATH"
# Output the temporary directory
Write-Host "Temporary directory: $env:TEMP"
# Output the system drive
Write-Host "System drive: $env:SystemDrive"
# Output the system root
Write-Host "System root: $env:SystemRoot"
# Output the computer name
Write-Host "Computer name: $env:COMPUTERNAME"
# Output the user domain
Write-Host "User domain: $env:USERDOMAIN"
# Output the user name
Write-Host "User name: $env:USERNAME"
# Output the user SID
Write-Host "User SID: $([System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value)"
# Output the user profile SID
Write-Host "User profile SID: $([System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value)"
# Output the user profile path
Write-Host "User profile path: $env:USERPROFILE"
# Output the user profile environment variable
Write-Host "User profile environment variable: $env:USERPROFILE"

