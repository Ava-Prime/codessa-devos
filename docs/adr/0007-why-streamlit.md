# ADR 0007: Use Streamlit for Developer Interface (Frontend)

- Status: Accepted
- Date: 2024-11-01
- Deciders: Phoenix

## Context and Problem Statement

Codessa DevOS requires a lightweight, fast, and intuitive frontend interface to:

- Collect user prompts and inputs
- Display LLM responses, summaries, and scrolls
- Serve as a hub for human-in-the-loop interactions with Codessa agents
- Bootstrap developer workflows without building a full frontend stack

We need something that allows rapid iteration, tight Python integration, and minimal deployment friction.

## Considered Options

1. 🚀 Streamlit (Python-native web UI)
2. 🧪 Gradio (popular for ML demos, less customizable for full apps)
3. 🧱 Flask or FastAPI + custom React frontend
4. 📊 Dash / Plotly Dash
5. 🧠 Jupyter notebooks (exploratory but not production-friendly)

## Decision Outcome

Chosen Option: Streamlit

### Positive Consequences

- ⚡ Fastest possible dev loop — changes reload in seconds
- 🐍 Python-native — no JavaScript, React, or frontend build pipeline required
- 🎨 Supports input widgets, layout, charts, markdown, code blocks out of the box
- 🌐 Hosted via streamlit.io, Streamlit Community Cloud, or GCP (App Engine, Cloud Run)
- 🤝 Tight integration with Google Cloud libraries (Firestore, Secret Manager)
- 📷 Easy to add screenshot/GIF demo for README and docs

### Negative Consequences

- 🎛️ Limited control over UI/UX customization compared to React/Next.js
- 🚫 Not ideal for multi-user or heavily stateful apps (can be mitigated)
- 🧪 Session-based model makes multi-agent conversations more complex (requires session_id, context tracking)
- 📦 Not a traditional frontend framework — may need to migrate for advanced use cases

## Notes

Streamlit is currently used to:

- Render the "Codessa DevOS" frontend
- Accept prompt input from users
- Display Gemini responses
- Write interaction logs to Firestore
- Bootstrap new developer-facing features (tool selection, scroll generation, etc.)

It serves as the Developer OS interface during the MVP and early-stage rollout.

Future Phases may include:

- Embedding inside Notion via iframe or App
- Migrating to custom React interface for multi-agent orchestration
- Adding WebSockets for real-time feedback

## Code Review
