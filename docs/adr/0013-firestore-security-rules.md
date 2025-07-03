# ADR 0014: Firestore Security Rules for Codessa DevOS

- **Status:** Accepted  
- **Date:** 2025-07-03  
- **Deciders:** Phoenix  

## Context and Problem Statement

Codessa DevOS stores sensitive data such as user prompts, AI-generated responses, and agent metadata in Firestore. Securing this data against unauthorized access is critical, especially as the system may be accessed by multiple users, agents, or services.

We need a Firestore security rules strategy that enforces:

- Access only to authorized users or service accounts.  
- Data validation on write operations to maintain data integrity.  
- Separation of access between user scopes or roles if multi-user support is added later.  
- Restriction of administrative actions to trusted identities.  

## Considered Options

1. **Open Access (No Rules):** Simplifies development but exposes data to anyone with project access (not secure).  
2. **Role-Based Access Control (RBAC):** Define roles and enforce them via security rules to restrict read/write operations.  
3. **Custom Claims and Authentication:** Use Firebase Authentication with custom claims to enforce fine-grained access.  
4. **Service Account-Only Access:** Limit Firestore access only to server-side service accounts with IAM permissions, denying client direct access.  

## Decision Outcome

**Chosen option:** Combination of **Service Account-Only Access** for backend operations with **Firebase Authentication + RBAC** for potential user-facing components.

- Currently, the Streamlit app and backend services authenticate via Google service accounts with least privilege.  
- Firestore security rules deny all client access except via authenticated service accounts.  
- Future multi-user support will use Firebase Auth with custom claims to assign roles (e.g., user, admin), enforced in Firestore rules.

---

## Positive Consequences

- Strong data protection by default.  
- Minimized attack surface by denying direct client access.  
- Clear pathway to extend with user authentication and role-based access.  
- Aligns with GCP best practices and compliance needs.

## Negative Consequences

- Development and testing require service account credentials or emulators.  
- More complex ruleset needed for future multi-user scenarios.  
- Possible increased latency due to authentication layers.

---

## Example Firestore Rules Snippet

```firestore
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth.token.admin == true;
      // Or restrict to service account identities with specific claims
    }
  }
}

Future Considerations
Implement Firebase Authentication for user management.

Expand security rules with granular read/write permissions per collection/document.

Add logging and monitoring on Firestore access attempts.

Related Decisions
ADR 0012: Firestore Data Model

ADR 0013: Use Streamlit for UI

ADR 0001: Use Google Vertex AI
