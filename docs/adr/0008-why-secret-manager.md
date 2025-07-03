# ADR 0008: Use Google Secret Manager for Credential Storage

- Status: Accepted
- Date: 2024-11-01
- Deciders: Phoenix

## Context and Problem Statement

Codessa DevOS requires secure storage of sensitive information such as:

- Gemini API Keys
- Service Account credentials (where applicable)
- Notion API tokens
- Other third-party API keys (e.g., GitHub, HuggingFace, Postmark, etc.)

These credentials must be securely accessed from deployed environments (e.g., Streamlit on Cloud Run or App Engine) while maintaining fine-grained access control and auditability. Hardcoding credentials or using environment variables alone is insufficient for production-grade systems.

## Considered Options

1. 🔐 Google Secret Manager
2. 📁 Environment variables (.env)
3. 🧠 Using a secrets.json file checked into the repo (insecure)
4. 🧰 AWS Secrets Manager / HashiCorp Vault (non-native to GCP)
5. 🗝️ Encrypted .env with manual decryption (adds complexity)

## Decision Outcome

Chosen Option: Google Secret Manager

### Positive Consequences

- ✅ Native to GCP — integrates cleanly with Firestore, Cloud Functions, and Vertex AI
- 🛡️ Supports IAM-based access control per secret
- 📜 Fully auditable (every access is logged)
- 🔄 Secrets can be updated dynamically without redeploying the app
- 🔑 Service accounts (e.g., codessa-devos-admin) can be granted fine-grained read-only access

### Negative Consequences

- 📈 Slight runtime latency when fetching secrets (cached after first access)
- ⚙️ Requires setup of IAM roles and permissions
- 🧪 Secrets are not automatically injected into environment variables (requires code)

## Notes

We use Google Secret Manager in the following ways:

- To store and retrieve the Gemini API Key using get_secret("gemini-api-key")
- To isolate project credentials between environments (dev, staging, production)
- To avoid ever committing secrets to GitHub

Example usage in code:

```python
def get_secret(secret_id: str) -> str:
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = secret_client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

This ensures secrets are stored securely, access is traceable, and deployments remain stateless and secure.

