# ADR 0005: Use Google Secret Manager for Secure Credential Access

- Status: Accepted
- Date: 2024-10-30
- Deciders: Phoenix
- Supersedes: None

## Context and Problem Statement

Codessa DevOS relies on sensitive credentials (e.g. Notion API keys, Gemini API keys, service tokens) to interact with external services. Hardcoding these secrets or storing them in plaintext environment variables (e.g. .env) exposes them to accidental leakage or source control. We need a secure, scalable, auditable solution for managing secrets.

Requirements:

- Programmatic access to secrets from deployed apps (via Vertex AI Functions, Streamlit, etc.)
- IAM-based access control per secret
- Auditing and versioning
- Rotation support

## Considered Options

1. 🔐 Google Secret Manager (GCP-native, managed, IAM-compatible)
2. 🗝️ Environment variables + .env files
3. 📦 HashiCorp Vault (powerful, self-hosted, complex)
4. 🔑 Firebase Remote Config (meant for app config, not secrets)
5. 📁 GCS bucket with encrypted JSON files

## Decision Outcome

Chosen Option: Google Secret Manager

### Positive Consequences

- ✅ GCP-native: Seamless integration with our existing infrastructure (IAM, Cloud Functions, Firestore)
- 🔐 Fine-grained IAM control: We can grant individual roles (like SecretAccessor) per secret or service account
- 🧾 Auditable: Access logs are automatically written to Cloud Audit Logs
- 🔁 Versioned secrets: Ability to rotate credentials with rollback
- 🔒 Secrets are encrypted at rest with Google-managed or customer-managed keys
- ⚙️ Fetch via API (gcloud, REST, or Python SDK)

### Negative Consequences

- 📊 API usage is billable at scale (after free tier)
- ⚠️ Requires setup and IAM roles (not plug-and-play for beginners)
- ⏱ Access time slightly slower than loading from memory or local file
- 📄 No built-in config interpolation (e.g., can't combine values into templates inside Secret Manager itself)

## Notes

In the Codessa DevOS stack, we access Secret Manager from:

- Streamlit frontend (via Python SDK + service account)
- Cloud Functions (via built-in IAM binding)
- Dev scripts using gcloud CLI

Secrets currently managed:

- gemini-api-key
- notion-api-key
- codessa-webhook-token
- github-deploy-key (planned)

Service account codessa-devos-admin@codessa-devos-2025 has the role roles/secretmanager.secretAccessor.

We will expand this pattern in future phases with customer-managed encryption keys and periodic automated secret rotation.

## Conclusion

Google Secret Manager is the definitive choice for Codessa DevOS. Its robust security features, native integration with our GCP environment, and auditable access controls directly address our core requirements. While there is a minor overhead in cost and setup, these are acceptable trade-offs for the significant gains in security posture and operational manageability. This decision establishes a secure foundation for handling all sensitive credentials as the project scales.
