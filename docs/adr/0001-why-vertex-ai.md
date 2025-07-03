# ADR 0001: Use Google Vertex AI for the Core LLM Engine

- **Status:** Accepted  
- **Date:** 2023-10-27  
- **Deciders:** Phoenix

## Context and Problem Statement

Codessa DevOS is an intelligent agent that requires a powerful, scalable, and reliable Large Language Model (LLM) to perform its core reasoning, planning, and task execution functions. The choice of the LLM provider is a critical architectural decision that will impact performance, scalability, cost, security, and future development velocity. We need a solution that is more than just an API endpoint; we need a managed platform that integrates well with our existing GCP-based technology stack.

## Considered Options

1. **Google Vertex AI:** A fully managed AI platform on GCP, offering access to Google's first-party models (like Gemini, PaLM 2) and third-party models.  
2. **OpenAI API:** A popular, high-performance API providing access to models like GPT-4.  
3. **Self-Hosting an Open-Source Model (e.g., Llama 2):** Deploying an open-source model on a GCP Compute Engine or GKE cluster.

## Decision Outcome

**Chosen option:** Google Vertex AI, because it offers the tightest integration with our GCP infrastructure, a unified platform for MLOps, and robust enterprise-grade security and data governance.

### Positive Consequences

- **Seamless Integration:** Native integration with our other GCP services (Firestore, Secret Manager, IAM) simplifies authentication and data flow. Service accounts and IAM roles can be used directly, enhancing security.  
- **Scalability and Reliability:** As a managed service, Vertex AI handles all the underlying infrastructure, scaling, and maintenance, allowing us to focus on application logic.  
- **Security and Data Governance:** Data processed through Vertex AI within our GCP project benefits from Google Cloud's security posture, including VPC Service Controls, data residency controls, and a commitment that our data is not used to train their models.  
- **Future-Proofing:** The Vertex AI platform is a strategic focus for Google, ensuring continuous updates, access to new models (like Gemini), and a growing ecosystem of MLOps tools (e.g., Vertex AI Search, Agent Builder).

### Negative Consequences

- **Vendor Lock-in:** By building deeply on the Vertex AI platform, migrating to another cloud or AI provider in the future would require significant effort.  
- **Cost Management:** As a powerful managed service, costs can scale quickly. Careful monitoring and implementation of quotas and alerts are necessary to manage the budget effectively.  
- **Model Availability:** While the platform is robust, we are dependent on Google for access to the latest and greatest models, which may have a different release cadence than other providers like OpenAI.

---
