# ADR 0011: Why Streamlit for Rapid Developer UI

- **Status:** Accepted
- **Date:** 2025-07-03
- **Deciders:** Phoenix
- **Context:** Codessa DevOS Developer Environment

## Context and Problem Statement

Codessa DevOS requires a simple, lightweight user interface that allows developers and AI agents to interact with the system, view prompt/response histories, submit scrolls, and view auto-generated reflections in real time. This UI must support rapid prototyping, deployment with minimal ops overhead, and tight integration with Python-based backend logic.

We need a framework that is:

- Fast to develop with
- Easy to deploy
- Python-native
- Interactive, reactive, and accessible in-browser

## Considered Options

1. **Streamlit:** Python-based app framework for building interactive data tools and dashboards.
2. **Flask + HTML/CSS/JS:** Traditional micro web framework with custom frontend.
3. **FastAPI + React:** API-first approach with decoupled modern frontend.
4. **Jupyter Notebooks:** Inline development environment with display/render capabilities.
5. **Gradio:** Lightweight framework for AI model demos and interactive inputs.

## Decision Outcome

**Chosen option:** Streamlit

### Positive Consequences

- ✅ **Developer Velocity:** Extremely fast to iterate and prototype in pure Python with zero frontend boilerplate.
- ✅ **Built-in Components:** Streamlit provides widgets like text input, markdown rendering, code blocks, and charts out of the box.
- ✅ **No DevOps Burden:** Can be launched via `streamlit run` without needing to deploy and manage a full web server stack.
- ✅ **In-browser Access:** Ideal for quick web UI demos, internal tooling, and AI interaction sandboxes.
- ✅ **Extensible:** Plays nicely with Google Cloud, Python SDKs, and Notion API integrations.
- ✅ **Low Learning Curve:** No frontend development knowledge required.

### Negative Consequences

- ⚠️ **Not Suited for Production-Scale Frontends:** Streamlit is ideal for internal tooling, not for public-facing multi-user apps.
- ⚠️ **Limited UI Flexibility:** Custom CSS and layout control is limited compared to full-stack frameworks.
- ⚠️ **Session-Oriented State:** Managing long-lived app state or collaborative editing can be challenging.
- ⚠️ **Browser Dependency:** Users must run and access the app through a web browser.

---

## Related Decisions

- ADR 0001: Why Vertex AI for Core LLMs
- ADR 0010: Why Firestore for Structured Memory
