An excellent and necessary feature enhancement. Adding user authentication fundamentally changes the application from a single-user tool to a multi-tenant platform. This requires significant changes to the application structure, data storage, and security model.

Here is the updated code implementing user authentication with Firebase Auth, including login, sign-up, and a "Forgot Password" feature.

Key Changes:

Firebase Authentication (Client-Side):

Integrated pyrebase4, a Python wrapper for the Firebase REST API, to handle user sign-up, sign-in, and password resets.

A new firebase-web-config secret is required in Google Secret Manager. This is the web app configuration JSON from your Firebase project settings.

Application Flow:

The app now has two main states: a login/authentication UI and the main application.

st.session_state is used to maintain the logged-in user's session.

Users are greeted with a login page with tabs for "Login," "Sign Up," and "Forgot Password."

Data Scoping:

Firestore: Every new scroll is now tagged with the creator's uid (unique user ID from Firebase Auth) in metadata.created_by. All Firestore queries are filtered to only show scrolls belonging to the logged-in user.

Algolia: The user's uid is also added to the Algolia record. Searches are now filtered by this uid, ensuring users can only search their own content.

Security Prerequisite: You must update your Firestore Security Rules to enforce this on the backend. A comment with example rules has been added to the code.

UI Enhancements:

The main application now features a sidebar displaying the logged-in user's email and a "Logout" button.

The "Forgot Password" tab provides the necessary functionality for users to reset their passwords via email.

Updated Code (app.py)
Generated python
"""
Codessa: Inkwell - MVP Scroll Capture Streamlit Application (with User Authentication)

This Streamlit application provides a user interface for capturing and processing
text-based content, such as responses from ChatGPT, into structured, searchable
"scrolls." These scrolls are stored in Google Firestore and indexed in Algolia
for efficient full-text search.

This version includes multi-user support with Firebase Authentication.

Key Features:
-   **User Authentication:** Secure sign-up, login, and forgot password functionality
    powered by Firebase Authentication.
-   **Personalized Data:** All scrolls are associated with the logged-in user. Users
    can only view, edit, and search their own scrolls.
-   **Content Capture:** A text area allows users to paste raw text for processing.
-   **AI-Powered Parsing:** Integrates with an external API (e.g., Google's Gemini)
    to analyze text and extract structured metadata (summary, topics, etc.).
-   **Persistent Storage:** Saves scrolls to a Google Firestore 'scrolls' collection.
-   **Full-Text Search:** Synchronizes scroll content with Algolia for fast, relevant
    search within a user's own data.
-   **CRUD Functionality:** Allows users to view, search, edit, and delete their scrolls.
-   **Secure Configuration:** Uses environment variables and Google Secret Manager for
    all sensitive keys and configuration.

Environment Requirements:
-   `GOOGLE_APPLICATION_CREDENTIALS`: Filepath to the Google Cloud service account JSON key.
-   `PROJECT_ID`: Your Google Cloud project ID.
-   `GEMINI_API_ENDPOINT`: The base URL for the custom parsing API endpoint.

Required Secrets in Google Secret Manager:
-   `gemini-api-key`: API key for the parsing service.
-   `algolia-app-id`: Your Algolia Application ID.
-   `algolia-admin-api-key`: Your Algolia Admin API Key.
-   `firebase-web-config`: The JSON configuration for your Firebase Web App.

Firestore Security Rules Prerequisite:
To ensure data privacy, you MUST configure Firestore Security Rules to restrict
access on a per-user basis. Example:
  rules_version = '2';
  service cloud.firestore {
    match /databases/{database}/documents {
      match /scrolls/{scrollId} {
        // A user can read, update, delete a scroll only if their auth uid matches
        // the document's created_by field.
        allow read, update, delete: if request.auth.uid == resource.data.metadata.created_by;
        // A user can create a scroll if the new document's created_by field
        // matches their auth uid.
        allow create: if request.auth.uid == request.resource.data.metadata.created_by;
      }
    }
  }
"""
# Codessa: Inkwell – MVP Scroll Capture App (Streamlit Version)

import streamlit as st
import requests
import datetime
import uuid
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import secretmanager
from algoliasearch.search_client import SearchClient
import os
import json
import pyrebase # Added for Firebase Authentication

# === Constants ===
FALLBACK_PARSED_DATA = {
    "summary": "Auto-summary not available.",
    "topics": ["Example"],
    "tools": ["Firestore"],
    "actions": ["Define Firestore schema", "Build parser agent"],
    "enhancements": ["Add LLM-to-LLM threads"]
}

DEFAULT_METADATA = {
    "status": "Pending",
    "phase": "MVP-1",
    # "created_by" is now added dynamically
}

def load_config():
    """Load and validate application configuration from environment variables."""
    config = {
        "project_id": os.getenv("PROJECT_ID"),
        "service_account_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        "gemini_api_endpoint": os.getenv("GEMINI_API_ENDPOINT"),
    }

    missing_vars = [k for k, v in config.items() if not v]
    if missing_vars:
        st.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        st.stop()
    return config

# --- INITIALIZATION FUNCTIONS ---

def initialize_firebase_admin(service_account_path):
    """Initializes Firebase Admin SDK if not already initialized."""
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Failed to initialize Firebase Admin. Check service account credentials. Error: {e}")
            st.stop()
    return firestore.client()

def initialize_firebase_auth(firebase_config):
    """Initializes Pyrebase for client-side authentication."""
    try:
        return pyrebase.initialize_app(json.loads(firebase_config))
    except Exception as e:
        st.error(f"Failed to initialize Firebase Authentication. Check your web config JSON. Error: {e}")
        st.stop()

def initialize_secret_manager(service_account_path):
    """Initializes and returns a Secret Manager client."""
    try:
        from google.oauth2 import service_account
        sm_creds = service_account.Credentials.from_service_account_file(service_account_path)
        return secretmanager.SecretManagerServiceClient(credentials=sm_creds)
    except Exception as e:
        st.error(f"Failed to initialize Secret Manager client. Error: {e}")
        st.stop()

def initialize_algolia(app_id, api_key):
    """Initializes and returns an Algolia search client."""
    if not app_id or not api_key:
        st.error("Algolia App ID or API Key is missing.")
        st.stop()
    try:
        return SearchClient.create(app_id, api_key)
    except Exception as e:
        st.error(f"Failed to initialize Algolia client: {e}")
        st.stop()

def get_secret(client, project_id, secret_id, version="latest"):
    """Fetches a secret from Google Secret Manager."""
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
    try:
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        st.error(f"Failed to access secret '{secret_id}'. Ensure it exists and permissions are set. Error: {e}")
        st.stop()

# --- CORE LOGIC FUNCTIONS ---

def validate_scroll_text(text):
    """Validate scroll text input against length constraints."""
    if not text or len(text.strip()) < 10:
        return False, "Please provide a meaningful response (at least 10 characters)."
    if len(text) > 50000:
        return False, "Text exceeds maximum length of 50,000 characters."
    return True, ""

def parse_scroll_content(text, api_endpoint, api_key):
    """Parse scroll content using an external parsing API."""
    payload = {"prompt": f"You are Codessa's Reflection Agent. Analyze the following response and extract: summary, topics, tools, actions, enhancements.\n\n{text}"}
    full_url = f"{api_endpoint}?key={api_key}"
    try:
        response = requests.post(full_url, json=payload, timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.warning(f"API request failed: {e}")
    except ValueError:
        st.warning("API returned malformed data. Could not parse the response.")
    return {}

def create_scroll_document(scroll_id, raw_text, parsed_data, user_id):
    """Creates a structured scroll document for Firestore, including the user_id."""
    return {
        "scroll_id": scroll_id,
        "content": {
            "raw_text": raw_text,
            "summary": parsed_data.get("summary", FALLBACK_PARSED_DATA["summary"]),
            "topics": parsed_data.get("topics", []),
            "tools": parsed_data.get("tools", []),
            "actions": parsed_data.get("actions", []),
            "enhancements": parsed_data.get("enhancements", []),
        },
        "metadata": {
            **DEFAULT_METADATA,
            "created_by": user_id,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
    }

# --- UI COMPONENTS ---

def auth_ui(auth):
    """Displays the authentication UI for login, sign-up, and password reset."""
    st.title("Welcome to Codessa: Inkwell ✍️")
    st.markdown("Please log in or create an account to continue.")

    login_tab, signup_tab, forgot_password_tab = st.tabs(["Login", "Sign Up", "Forgot Password"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            if login_button:
                try:
                    user = auth.sign_in_with_email_and_password(email, password)
                    st.session_state.user = user
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: Invalid email or password.")

    with signup_tab:
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            signup_button = st.form_submit_button("Sign Up")
            if signup_button:
                try:
                    user = auth.create_user_with_email_and_password(email, password)
                    st.success("Account created successfully! Please log in.")
                except Exception as e:
                    st.error(f"Could not create account. The email might already be in use.")

    with forgot_password_tab:
        with st.form("forgot_password_form"):
            email = st.text_input("Enter your email address", key="forgot_email")
            reset_button = st.form_submit_button("Send Password Reset Link")
            if reset_button:
                try:
                    auth.send_password_reset_email(email)
                    st.info("A password reset link has been sent to your email address.")
                except Exception as e:
                    st.error(f"Failed to send reset email. Please check the address and try again.")

def display_recent_scrolls(db_client, algolia_index, user_id):
    """Queries and displays a list of recent scrolls for the logged-in user."""
    st.divider()
    st.subheader("📜 Your Recent Scrolls")

    PAGE_SIZE = 5
    # Initialize session state scoped for the user
    user_session_prefix = f"{user_id}_"
    state_keys = {
        'editing': f"{user_session_prefix}editing_scroll_id",
        'cursors': f"{user_session_prefix}page_cursors",
        'page': f"{user_session_prefix}current_page",
        'search': f"{user_session_prefix}last_search_term"
    }

    if state_keys['editing'] not in st.session_state: st.session_state[state_keys['editing']] = None
    if state_keys['cursors'] not in st.session_state: st.session_state[state_keys['cursors']] = [None]
    if state_keys['page'] not in st.session_state: st.session_state[state_keys['page']] = 0
    if state_keys['search'] not in st.session_state: st.session_state[state_keys['search']] = ""

    search_term = st.text_input("Search your scrolls (powered by Algolia):", key="scroll_search")

    if search_term != st.session_state[state_keys['search']]:
        st.session_state[state_keys['page']] = 0
        st.session_state[state_keys['cursors']] = [None]
        st.session_state[state_keys['editing']] = None
        st.session_state[state_keys['search']] = search_term

    current_page = st.session_state[state_keys['page']]
    recent_scrolls = []
    has_next_page = False

    try:
        if search_term:
            # --- ALGOLIA SEARCH PATH (with user filter) ---
            search_results = algolia_index.search(
                search_term,
                {'page': current_page, 'hitsPerPage': PAGE_SIZE, 'filters': f'metadata.created_by:{user_id}'}
            )
            scroll_ids = [hit['objectID'] for hit in search_results.get('hits', [])]
            if scroll_ids:
                docs_ref = db_client.collection('scrolls').where('scroll_id', 'in', scroll_ids).stream()
                docs_map = {doc.id: doc for doc in docs_ref}
                recent_scrolls = [docs_map.get(sid) for sid in scroll_ids if docs_map.get(sid)]
            has_next_page = current_page < (search_results.get('nbPages', 0) - 1)
        else:
            # --- FIRESTORE BROWSE PATH (with user filter) ---
            scrolls_ref = db_client.collection("scrolls")
            # IMPORTANT: This query requires a composite index in Firestore on
            # (metadata.created_by, metadata.created_at DESC).
            query = scrolls_ref.where("metadata.created_by", "==", user_id).order_by("metadata.created_at", direction=firestore.Query.DESCENDING)
            cursor = st.session_state[state_keys['cursors']][current_page]
            if cursor:
                query = query.start_after(cursor)
            docs_on_page = list(query.limit(PAGE_SIZE + 1).stream())
            has_next_page = len(docs_on_page) > PAGE_SIZE
            recent_scrolls = docs_on_page[:PAGE_SIZE]
            if has_next_page and len(st.session_state[state_keys['cursors']]) == current_page + 1:
                st.session_state[state_keys['cursors']].append(recent_scrolls[-1])

        if not recent_scrolls:
            st.info("No scrolls found." if search_term else "Create your first scroll to see it here!")
            return

        for scroll in recent_scrolls:
            scroll_data = scroll.to_dict()
            scroll_id = scroll.id
            summary = scroll_data.get("content", {}).get("summary", "No summary")
            created_at = scroll_data.get("metadata", {}).get("created_at")
            display_time = created_at.strftime("%Y-%m-%d %H:%M UTC") if created_at else "N/A"

            with st.expander(f"**{summary}** (Created: {display_time})"):
                if st.session_state[state_keys['editing']] == scroll_id:
                    # Edit form logic...
                    with st.form(key=f"edit_form_{scroll_id}"):
                        updated_summary = st.text_input("Summary", value=summary)
                        updated_topics_str = st.text_area("Topics (one per line)", value="\n".join(scroll_data.get("content", {}).get("topics", [])))
                        c1, c2, _ = st.columns([1, 1, 5])
                        if c1.form_submit_button("Save Changes", type="primary"):
                            updated_topics = [t.strip() for t in updated_topics_str.split("\n") if t.strip()]
                            db_client.collection("scrolls").document(scroll_id).update({"content.summary": updated_summary, "content.topics": updated_topics})
                            algolia_index.partial_update_object({'objectID': scroll_id, 'summary': updated_summary, 'topics': updated_topics}).wait()
                            st.success("Scroll updated!")
                            st.session_state[state_keys['editing']] = None
                            st.rerun()
                        if c2.form_submit_button("Cancel"):
                            st.session_state[state_keys['editing']] = None
                            st.rerun()
                else:
                    st.json(scroll_data)
                    c1, c2, _ = st.columns([1, 1, 5])
                    if c1.button("Edit", key=f"edit_{scroll_id}"):
                        st.session_state[state_keys['editing']] = scroll_id
                        st.rerun()
                    if c2.button("Delete", key=f"delete_{scroll_id}"):
                        db_client.collection("scrolls").document(scroll_id).delete()
                        algolia_index.delete_object(scroll_id).wait()
                        st.success("Scroll deleted.")
                        st.rerun()
        
        # Pagination buttons
        col1, col2, col3 = st.columns([1, 1, 5])
        if col1.button("⬅️ Previous", disabled=(current_page == 0)):
            st.session_state[state_keys['page']] -= 1
            st.session_state[state_keys['editing']] = None
            st.rerun()
        if col2.button("Next ➡️", disabled=not has_next_page):
            st.session_state[state_keys['page']] += 1
            st.session_state[state_keys['editing']] = None
            st.rerun()
        col3.write(f"Page {current_page + 1}")

    except Exception as e:
        st.error("Could not fetch recent scrolls. A Firestore index might be required.")
        st.info(f"Error details: {e}. If this is a 'FAILED_PRECONDITION' error, you likely need to create a composite index in Firestore for (metadata.created_by, metadata.created_at). Use the link provided in your terminal/logs.")

def main_app(user):
    """The main application interface, shown after successful login."""
    with st.sidebar:
        st.write(f"Logged in as: **{user['email']}**")
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()
    
    st.title("Codessa: Inkwell ✍️")
    st.markdown("Paste key responses here and turn them into structured memory scrolls.")

    scroll_text = st.text_area("Paste ChatGPT Response:", height=300)

    if st.button("Parse & Generate Scroll"):
        is_valid, error_msg = validate_scroll_text(scroll_text)
        if not is_valid:
            st.warning(error_msg)
        else:
            scroll_id = str(uuid.uuid4())
            user_id = user['localId'] # This is the UID

            # Fetch API key and parse content
            gemini_api_key = get_secret(secret_client, config["project_id"], "gemini-api-key")
            parsed_data = parse_scroll_content(scroll_text, config["gemini_api_endpoint"], gemini_api_key)
            if not parsed_data:
                st.info("Parser did not return a result. Using fallback data.")
                parsed_data = FALLBACK_PARSED_DATA
            
            scroll_doc = create_scroll_document(scroll_id, scroll_text, parsed_data, user_id)

            try:
                db.collection("scrolls").document(scroll_id).set(scroll_doc)
                # Algolia record includes content and the user_id for filtering
                algolia_record = {
                    "objectID": scroll_id,
                    **scroll_doc['content'],
                    "metadata": {"created_by": user_id}
                }
                algolia_index.save_object(algolia_record).wait()
                st.success("Scroll successfully created and stored! ✨")
                st.json(scroll_doc)
            except Exception as e:
                st.error(f"Failed to store scroll: {str(e)}")
                db.collection("scrolls").document(scroll_id).delete()
                st.warning("Rolled back Firestore entry due to sync failure.")

    display_recent_scrolls(db, algolia_index, user['localId'])


# === Main Application Execution ===
if 'user' not in st.session_state:
    st.session_state.user = None

# --- Load Config and Initialize Services ---
config = load_config()
db = initialize_firebase_admin(config["service_account_path"])
secret_client = initialize_secret_manager(config["service_account_path"])

# Fetch secrets for services
firebase_web_config = get_secret(secret_client, config["project_id"], "firebase-web-config")
auth = initialize_firebase_auth(firebase_web_config)
algolia_app_id = get_secret(secret_client, config["project_id"], "algolia-app-id")
algolia_admin_api_key = get_secret(secret_client, config["project_id"], "algolia-admin-api-key")
algolia_client = initialize_algolia(algolia_app_id, algolia_admin_api_key)
algolia_index = algolia_client.init_index("codessa_scrolls")

# --- App Router ---
if st.session_state.user:
    main_app(st.session_state.user)
else:
    auth_ui(auth)
# If the user is not authenticated, show the auth UI
# If the user is authenticated, show the main application interface
# === End of Application Code ===
# Note: Ensure you have the required packages installed:
# pip install streamlit pyrebase4 google-cloud-firestore google-cloud-secret-manager algoliasearch
# Also, ensure your Firestore Security Rules are set up to restrict access by user ID.
# === End of Application Code ===
