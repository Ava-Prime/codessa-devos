#!/bin/bash
#
# v2: Made idempotent, added error handling, and removed global config changes.

# Exit immediately if a command exits with a non-zero status.
# Treat unset variables as an error.
# The return value of a pipeline is the status of the last command to exit with a non-zero status.
set -euo pipefail

# -----------------------------
# Ava Prime GCP Service Account Setup
# -----------------------------

# --- CONFIGURATION ---
# Use the first script argument as Project ID, or default to the one provided.
PROJECT_ID="${1:-codessa-devos-464821}"
SA_NAME="ava-prime-agent"
SA_DISPLAY_NAME="Ava Prime Agent"
SA_DESCRIPTION="Agent Ava Prime's programmatic identity for Codessa DevOS"
SA_KEY_PATH="service-account/${SA_NAME}-key.json"
ROLES=(
  "roles/datastore.user"
  "roles/aiplatform.user"
  "roles/secretmanager.secretAccessor"
  "roles/logging.logWriter"
)
# --- END CONFIGURATION ---

SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "----------------------------------------------------"
echo "🚀 Starting Ava Prime Service Account Setup"
echo "   Project: ${PROJECT_ID}"
echo "   Service Account: ${SA_NAME}"
echo "----------------------------------------------------"
echo ""

# Check if project exists and user has access
echo "🔧 Verifying project access..."
if ! gcloud projects describe "$PROJECT_ID" --quiet > /dev/null; then
    echo "❌ Error: Project '${PROJECT_ID}' not found or you don't have permission to access it."
    exit 1
fi
echo "   Project access confirmed."
echo ""

# Create service account IF it doesn't exist
echo "📡 Checking for service account: ${SA_NAME}"
if gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT_ID}" > /dev/null 2>&1; then
  echo "   ✅ Service account already exists. Skipping creation."
else
  echo "   Creating service account: ${SA_NAME}"
  gcloud iam service-accounts create "${SA_NAME}" \
    --project="${PROJECT_ID}" \
    --display-name="${SA_DISPLAY_NAME}" \
    --description="${SA_DESCRIPTION}"
  echo "   Service account created successfully."
fi
echo ""

# Assign IAM roles (add-iam-policy-binding is idempotent)
echo "🔐 Assigning IAM roles to ${SA_EMAIL}"
for ROLE in "${ROLES[@]}"; do
  echo "   ➤ Ensuring role: ${ROLE}"
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="${ROLE}" \
    --condition=None > /dev/null # Suppress verbose output
done
echo "   All roles assigned."
echo ""

# Create service account key directory
mkdir -p "$(dirname "$SA_KEY_PATH")"

# Generate key IF it doesn't exist
echo "🔑 Checking for JSON key at: ${SA_KEY_PATH}"
if [ -f "${SA_KEY_PATH}" ]; then
    echo "   ✅ Key file already exists. Skipping creation."
else
    echo "   Generating new JSON key..."
    gcloud iam service-accounts keys create "${SA_KEY_PATH}" \
      --iam-account="${SA_EMAIL}" \
      --project="${PROJECT_ID}"
    echo "   Key file created."
fi
echo ""

# --- SUMMARY ---
echo "----------------------------------------------------"
echo "✅ Done! Ava Prime is configured."
echo "   Name:        ${SA_NAME}"
echo "   Email:       ${SA_EMAIL}"
echo "   Key File:    ${SA_KEY_PATH}"
echo "----------------------------------------------------"
echo ""
echo "📌 Update your .env with:"
echo "GOOGLE_APPLICATION_CREDENTIALS=${SA_KEY_PATH}"
echo "PROJECT_ID=${PROJECT_ID}"
echo "FIRESTORE_SERVICE_ACCOUNT=${SA_KEY_PATH}"
echo ""
echo "🧪 You can now test access using:"
echo "gcloud auth activate-service-account --key-file=${SA_KEY_PATH}"
echo ""
echo "🚀 Happy coding!"
echo "----------------------------------------------------"
# End of Ava Prime Service Account Setup
# This script sets up a service account for Ava Prime in GCP, ensuring idempotency  
# and proper error handling. It creates the service account, assigns necessary roles,
# and generates a key file if it doesn't already exist. The script is designed to be run
# multiple times without causing errors or duplicating resources.
# It also provides a summary of the actions taken and instructions for updating the .env file.
# This script is part of the Codessa DevOS project, which aims to create a comprehensive
# development environment for AI agents and consciousness systems.
# The script is designed to be run in a Unix-like environment with gcloud CLI installed.
# It uses strict error handling to ensure that any issues are caught early, and it provides
# clear output messages to guide the user through the setup process.
# The script is designed to be run multiple times without causing errors or duplicating resources.
# It also provides a summary of the actions taken and instructions for updating the .env file.
# This script is part of the Codessa DevOS project, which aims to create a comprehensive