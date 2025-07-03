# Codessa DevOS 🧠

An intelligent DevOps agent built with Streamlit, Google Cloud Platform (GCP), Vertex AI, Firestore, and Notion.

---

## Overview

Codessa DevOS is a comprehensive DevOps automation platform designed to streamline development workflows through intelligent agent-based orchestration. It integrates cloud services and AI technologies to provide secure, scalable, and extensible automation.

---

## Key Capabilities

- Secure API and credential management via GCP Secret Manager  
- Intelligent data access and tool coordination using Firestore  
- AI-powered reasoning leveraging Vertex AI  
- Optional workflow tracking and documentation with Notion API  
- Extensible architecture for custom DevOps automation

---

## Technology Stack

- **Streamlit**: Web interface for user interaction  
- **Google Cloud Platform**: Core infrastructure and services  
- **Vertex AI**: Large language model (LLM) powered reasoning  
- **Firestore**: Structured and persistent memory  
- **Secret Manager**: Secure storage of sensitive credentials  
- **Notion API**: Optional integration for reflections and syncing

---

## Architecture Overview

```plaintext
+-------------+      +------------------+      +------------------+
|  Streamlit  | <--> | Firestore (DB)   | <--> | Google Secret    |
|  Web UI     |      | Persistent Store |      | Manager (Secrets) |
+-------------+      +------------------+      +------------------+
       |                      |                       |
       |                      |                       |
       v                      v                       v
+--------------------------------------------------------------+
|                       Vertex AI (LLM)                        |
+--------------------------------------------------------------+
       |
       v
+----------------+
|  Notion API    |
| (Optional Sync)|
+----------------+
This diagram shows the main components and data flow.

Getting Started
Prerequisites
Google Cloud Project with the following APIs enabled:

Firestore

Vertex AI

Secret Manager

Cloud Functions (if applicable)

Cloud Storage (optional)

Service account JSON key with assigned roles:

roles/datastore.user

roles/aiplatform.user

roles/secretmanager.secretAccessor

Python 3.9 or higher installed

.env file configured with environment variables (see below)

Installation
Clone this repository:

bash
Copy
Edit
git clone https://github.com/Ava-Prime/codessa-devos.git
cd codessa-devos
Create and activate a Python virtual environment:

bash
Copy
Edit
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Configure environment variables:

Copy .env.example to .env

Edit .env to set:

dotenv
Copy
Edit
PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account.json
REGION=us-central1
NOTION_API_KEY=your-notion-integration-key (optional)
NOTION_DATABASE_ID=your-notion-database-id (optional)
Run the Streamlit app:

bash
Copy
Edit
streamlit run app.py
Installation Verification
After running the app, verify:

The Streamlit UI loads without errors.

Firestore collections like codessa-reflections are created upon submitting queries.

No authentication errors occur related to GCP credentials.

(Optional) If Notion is configured, check for synced pages or entries.

You can also run:

bash
Copy
Edit
gcloud auth list
gcloud firestore indexes composite list --project=your-gcp-project-id
to verify your GCP setup.

Usage Examples
Submitting a prompt
Enter your question or command into the text input on the Streamlit UI and submit. The app stores your query and the AI-generated response securely in Firestore.

Firestore Data Access
Firestore is used as the persistent backend to store prompts, responses, and "scrolls" (aggregated insights). You can query or manage this data programmatically or via the GCP console.

Notion Sync (Optional)
If configured, Codessa DevOS syncs insights and summaries into your Notion workspace for enhanced documentation and tracking.

Architecture Decision Records (ADR)
Why Streamlit?
Rapid prototyping and interactive UI capabilities tailored for data apps.

Why Google Cloud Platform?
Native integration with AI, serverless, and storage services optimized for scalable deployments.

Why Firestore for storage?
Flexible, schema-less, and real-time database suited for conversational data and state persistence.

Why Vertex AI?
Provides managed LLMs and AI tooling integrated within the GCP ecosystem, facilitating future enhancements.

Why Notion API?
Enables seamless documentation and knowledge management workflows for users.

Troubleshooting
Authentication errors
Ensure GOOGLE_APPLICATION_CREDENTIALS points to a valid service account JSON file with necessary IAM roles.

Firestore connection issues
Confirm Firestore API is enabled and Firestore database is initialized in Native mode.

Notion integration problems
Verify that the Notion API key and database ID are correct and the integration has appropriate permissions.

Environment variables not loading
Make sure to run your app in the directory containing the .env file and that python-dotenv is installed.

API rate limiting or quota exceeded
Monitor GCP quotas and apply for increases as necessary.

Security Considerations
Credential Management:
Use Google Secret Manager to store sensitive API keys and service account credentials securely.

IAM Principle of Least Privilege:
Assign minimal permissions to service accounts, limiting access to only required services.

Network Security:
Configure private IPs, VPC Service Controls, or firewall rules to restrict unauthorized access.

Data Encryption:
Leverage GCP default encryption at rest and in transit; consider customer-managed keys for sensitive data.

API Rate Limiting:
Implement client-side throttling or backend rate limits to avoid abuse or unexpected costs.

Audit Logging:
Enable Cloud Audit Logs to monitor access and modifications for compliance.

Contribution Guidelines
We welcome contributions! Please follow these guidelines to maintain quality and consistency:

Fork the repository and create a feature branch.

Follow PEP8 and run black formatter before commits.

Write clear, descriptive commit messages.

Include tests for new features or bug fixes.

Run tests locally using:

bash

pytest tests/
Submit pull requests with a detailed description of changes.

Report issues clearly with steps to reproduce.

Version Information
Python >= 3.9

Streamlit >= 1.20.0

google-cloud-firestore >= 2.7.0

google-cloud-secret-manager >= 2.7.0

google-cloud-aiplatform >= 1.18.0

python-dotenv >= 0.21.0

requests >= 2.28.0

License
MIT License

Contact
For questions or contributions, contact Phoenix at contact@codessa-devos.com.

Built with ❤️ by Phoenix for Codessa DevOS
---

