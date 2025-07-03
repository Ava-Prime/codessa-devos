#!/bin/bash
set -e

PROJECT_ID="codessa-devos-2025"
SA_NAME="codessa-devos-admin"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \
  datastore.googleapis.com \
  cloudfunctions.googleapis.com \
  secretmanager.googleapis.com \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  iam.googleapis.com \
  --project "$PROJECT_ID"

# Check if service account exists
if gcloud iam service-accounts describe "$SA_EMAIL" --project "$PROJECT_ID" >/dev/null 2>&1; then
  echo "Service account $SA_EMAIL already exists."
else
  echo "Creating service account $SA_EMAIL..."
  gcloud iam service-accounts create "$SA_NAME" \
    --display-name "Codessa DevOS Admin" \
    --project "$PROJECT_ID"
fi

# Assign roles
declare -a ROLES=(
  "roles/datastore.user"
  "roles/cloudfunctions.invoker"
  "roles/secretmanager.secretAccessor"
  "roles/aiplatform.user"
  "roles/storage.objectAdmin"
)

echo "Assigning roles to service account..."
for ROLE in "${ROLES[@]}"; do
  echo "Assigning $ROLE ..."
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="$ROLE" \
    --quiet
done

echo "All done! Service account $SA_EMAIL is ready with required permissions."
# Output service account email
echo "Service Account Email: $SA_EMAIL"

# Output project ID
echo "Project ID: $PROJECT_ID"

# Output roles assigned
echo "Roles assigned:"
for ROLE in "${ROLES[@]}"; do
  echo "- $ROLE"
done

# Output instructions for next steps
echo "Next steps:"
echo "1. Use the service account email ($SA_EMAIL) in your application."
echo "2. Ensure your application is configured to use this service account for authentication."
echo "3. If you need to add more roles in the future, you can use the command:"
echo "   gcloud projects add-iam-policy-binding $PROJECT_ID --member=serviceAccount:$SA_EMAIL --role=<ROLE_NAME>"
echo "4. For more information, refer to the Google Cloud documentation on IAM roles and service accounts."
echo "5. If you need to delete the service account in the future, you can use the command:"
echo "   gcloud iam service-accounts delete $SA_EMAIL --project=$PROJECT_ID"
echo "6. To view the service account details, you can use the command:"
echo "   gcloud iam service-accounts describe $SA_EMAIL --project=$PROJECT_ID"
echo "7. To list all service accounts in the project, you can use the command:"
echo "   gcloud iam service-accounts list --project=$PROJECT_ID"
echo "8. To view the IAM policy for the project, you can use the command:"
echo "   gcloud projects get-iam-policy $PROJECT_ID"