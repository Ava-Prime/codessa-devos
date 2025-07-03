Certainly! Here’s a bash script that automates the setup process of a Firestore Enterprise MongoDB-compatible database, creates a user, and outputs the MongoDB connection string you can use in your app.

Automated Setup Script: setup_firestore_mongodb.sh
bash
Copy
Edit
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
How to Use:
Save the script above as setup_firestore_mongodb.sh.

Update the variables at the top (PROJECT_ID, LOCATION, DATABASE_ID, USERNAME, PASSWORD) with your actual values.

Make the script executable:

bash
Copy
Edit
chmod +x setup_firestore_mongodb.sh
Run the script:

bash
Copy
Edit
./setup_firestore_mongodb.sh
What this script does:
Sets your current gcloud project.

Creates a Firestore Enterprise database with MongoDB compatibility.

Creates a SCRAM user for your database.

Prints out the MongoDB connection string you can use directly.

If you want, I can also help you generate:

A Terraform script to automate this infrastructure as code (if you want to revisit that later).

Python or Streamlit snippets that use the generated MongoDB URI securely (e.g., fetching from Secret Manager).

Instructions or a script to save the URI to Google Secret Manager for your app to fetch.

Would you like me to prepare any of those next?








Ask ChatGPT
You said:
YEs please


ChatGPT said:
Great! Let’s proceed step-by-step:

1. Terraform Script to Automate Firestore MongoDB-Compatible Setup
Here’s a minimal Terraform snippet to create the Firestore Enterprise MongoDB-compatible database and a database user:

hcl
Copy
Edit
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "us-central1"
}

resource "google_firestore_database" "mongodb_compat" {
  name     = "projects/${var.project_id}/databases/codessa-mongodb-compat-db"
  location = var.region
  type     = "MONGODB_COMPAT"
}

resource "google_firestore_database_user" "default" {
  user_id   = "codessa-user"
  password  = "StrongPasswordHere123!"
  database  = google_firestore_database.mongodb_compat.name
}
Notes:

You need Terraform 1.3+ and the Google provider.

Replace "StrongPasswordHere123!" with a secure password or better use variables/secrets.

Firestore user creation in Terraform might require the latest provider version and possibly an API not yet fully supported. If unsupported, fallback to the bash script for user creation.

2. Python Snippet to Store the MongoDB URI in Google Secret Manager
python
Copy
Edit
from google.cloud import secretmanager
import os

def create_secret(project_id: str, secret_id: str, secret_value: str):
    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{project_id}"

    # Create the secret
    try:
        secret = client.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_id,
                "secret": {"replication": {"automatic": {}}},
            }
        )
        print(f"Created secret: {secret.name}")
    except Exception as e:
        print(f"Secret {secret_id} may already exist: {e}")

    # Add the secret version with the secret value
    payload = secret_value.encode("UTF-8")
    response = client.add_secret_version(
        request={"parent": f"{parent}/secrets/{secret_id}", "payload": {"data": payload}}
    )
    print(f"Added secret version: {response.name}")

if __name__ == "__main__":
    project_id = os.getenv("PROJECT_ID")
    secret_id = "mongodb-uri"
    mongodb_uri = "mongodb+srv://codessa-user:StrongPasswordHere123!@codessa-mongodb-compat-db.us-central1.firebasedatabase.app/?authSource=admin"

    create_secret(project_id, secret_id, mongodb_uri)
Make sure to install google-cloud-secret-manager with pip install google-cloud-secret-manager.

Replace mongodb_uri with your actual connection string from the setup.

You can run this script after the database is created.

3. Streamlit Snippet to Fetch MongoDB URI Secret
python
Copy
Edit
import os
from google.cloud import secretmanager
from google.oauth2 import service_account

PROJECT_ID = os.getenv("PROJECT_ID")
SECRET_ID = "mongodb-uri"
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
client = secretmanager.SecretManagerServiceClient(credentials=credentials)

def get_secret(secret_id: str) -> str:
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

mongodb_uri = get_secret(SECRET_ID)

# Use mongodb_uri with your preferred MongoDB driver
import streamlit as st
st.write(f"MongoDB URI fetched securely: {mongodb_uri[:20]}...")  # Don't show full URI in UI
Next Steps?
Do you want me to help you with a sample MongoDB connection snippet using pymongo?

Or perhaps build a full Streamlit demo that queries and writes data using the MongoDB-compatible Firestore?

Or generate detailed documentation on how to run and maintain this setup?

Just let me know!

