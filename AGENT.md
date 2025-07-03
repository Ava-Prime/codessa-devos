# AGENT.md: Codessa DevOS

This guide provides essential context for AI coding agents operating in this repository.

### 1. Build, Lint, & Test Commands

- **Install Dependencies**: `pip install -r requirements-dev.txt`
- **Run the App**: `streamlit run app.py`
- **Run All Linters/Formatters**: `pre-commit run --all-files`
- **Run All Tests**: `pytest`
- **Run a Single Test File**: `pytest path/to/your/test_file.py`
- **Run a Specific Test Function**: `pytest path/to/your/test_file.py::test_function_name`

### 2. Architecture & Core Components

- **Main Application**: `app.py` is the primary entry point, a Streamlit app with Firebase-based user authentication.
- **Data Storage**:
  - **Primary**: Google Firestore (`scrolls` collection) stores user-generated content.
  - **Search**: Algolia (`codessa_scrolls` index) provides full-text search capabilities.
- **Authentication**: User identity is managed by Firebase Authentication.
- **Configuration**: App configuration is loaded from environment variables. Secrets (API keys) are securely fetched from Google Secret Manager.
- **Infrastructure as Code (IaC)**: The `codessa-devos-terraform/` directory contains Terraform configurations for provisioning Google Cloud resources.

### 3. Code Style & Conventions

- **Formatting**: Code style is non-negotiable and enforced by `pre-commit` using **Black**, **isort**, and **Prettier**. Always run it before committing.
- **Naming**: Use `snake_case` for variables and functions, `PascalCase` for classes, and `UPPER_CASE` for constants.
- **Type Hints**: Type hints are strongly preferred for all function signatures. Use `mypy` (via pre-commit) to verify types.
- **Error Handling**: For user-facing errors in the Streamlit app, use `st.error()`. For debugging internal exceptions, use `st.exception(e)`.
- **Imports**: Follow the `isort` standard: standard library, then third-party, then local application imports.
