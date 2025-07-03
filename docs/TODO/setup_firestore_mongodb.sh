#!/bin/bash

# Exit on any failure
set -e

# ----------- CONFIGURATION -----------

# TODO: Update these variables before running
PROJECT_ID="your-gcp-project-id"
LOCATION="us-central1"  # Change if needed
DATABASE_ID="codessa-mongodb-compat-db"
USERNAME="codessa-user"
PASSWORD="StrongPasswordHere123!"

# ------------------------------------

echo "Starting Firestore MongoDB-Compatible database setup..."

echo "1. Setting gcloud project to $PROJECT_ID"
gcloud config set project "$PROJECT_ID"

echo "2. Creating Firestore Enterprise MongoDB-compatible database..."
gcloud firestore databases create "$DATABASE_ID" \
  --location="$LOCATION" \
  --type="mongodb_compat" \
  --project="$PROJECT_ID"

echo "3. Creating Firestore database user with SCRAM authentication..."
gcloud firestore databases users create "$USERNAME" \
  --password="$PASSWORD" \
  --database="$DATABASE_ID" \
  --project="$PROJECT_ID"

MONGODB_URI="mongodb+srv://${USERNAME}:${PASSWORD}@${DATABASE_ID}.${LOCATION}.firebasedatabase.app/?authSource=admin"

echo ""
echo "✅ Firestore MongoDB-Compatible database and user created successfully!"
echo ""
echo "MongoDB Connection URI:"
echo "$MONGODB_URI"
echo ""
echo "Use this URI in your application to connect via MongoDB drivers."
echo ""
echo "Remember to secure your credentials! Consider storing the URI in Google Secret Manager."
echo "You can also use the Firestore Emulator for local development."
echo "For more information, refer to the Firestore documentation."
echo ""
echo "Setup complete!"
# End of script
echo "You can now use the MongoDB-compatible Firestore database in your application."
echo "To connect, use the provided MongoDB URI in your application code."
echo "For more details, refer to the Firestore documentation."
echo "Thank you for using this setup script!"
echo "Exiting setup script."
exit 0
# End of script
echo "Script completed successfully."
echo "You can now use the MongoDB-compatible Firestore database in your application."
echo "To connect, use the provided MongoDB URI in your application code."
echo "For more details, refer to the Firestore documentation."
echo "Thank you for using this setup script!"
echo "Exiting setup script."
exit 0
# End of script
echo "Script completed successfully."
echo "You can now use the MongoDB-compatible Firestore database in your application."