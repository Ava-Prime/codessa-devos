# ADR 0002: Use Streamlit for the Codessa DevOS UI

- Status: Accepted
- Date: 2024-10-27
- Deciders: Phoenix
- Supersedes: None

## Context and Problem Statement

Codessa DevOS requires a user-friendly interface where developers can interact with the AI assistant, submit prompts, and visualize responses. The interface should be quick to prototype, easy to deploy, and capable of integrating with backend services such as Firestore and Vertex AI. The challenge is to balance speed of development with UX quality, integration ease, and long-term maintainability.

## Considered Options

1. Streamlit
2. React-based SPA (Next.js + FastAPI backend)
3. Dash by Plotly
4. Flask + Custom HTML/CSS

## Decision Outcome

Chosen Option: Streamlit

### Positive Consequences

- 🧪 Rapid Prototyping: Streamlit allows for quick iteration and hot-reloading, ideal for developing MVPs and internal tools.
- 🧠 AI-Native UX: Built with LLM-based workflows in mind. Text inputs, markdown rendering, and interaction widgets are perfect for Codessa’s conversational interface.
- 🔌 Integrated State: Easy integration with Python objects and GCP libraries without requiring REST APIs.
- 🌐 Low Friction Hosting: Can be deployed on Streamlit Community Cloud, GCP App Engine, or Docker.

### Negative Consequences

- 🧱 Limited UI Customization: Less control over the HTML/CSS layout compared to React or Flask.
- 📈 Less Scalable for Consumer Apps: Not optimal for massive-scale public-facing UIs.
- 🔄 Dependency on Python: Tight coupling between UI and Python backend might hinder separation of concerns long-term.

## Notes

If we outgrow Streamlit, we may revisit the decision and migrate to a Next.js + FastAPI architecture in Phase 2. For MVP-1, Streamlit is the fastest and cleanest option.

---
