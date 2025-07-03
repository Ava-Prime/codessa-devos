"""
Codessa: Inkwell - MVP Scroll Capture Streamlit Application

This Streamlit application allows users to capture and parse ChatGPT responses into structured 'scrolls' 
stored in Firestore. Key features include:
- Text input for capturing responses
- Integration with a custom parsing API (e.g., Gemini, LLM) for response parsing
- Automatic generation of scroll metadata (summary, topics, tools, actions, enhancements)
- Unique scroll ID generation
- Firestore document storage

Environment Requirements:
- GOOGLE_APPLICATION_CREDENTIALS: Path to Firebase service account key
- PROJECT_ID: Your Google Cloud project ID
- GEMINI_API_ENDPOINT: Endpoint for Gemini API parsing

Note: Current implementation includes mock fallback for parsing when API call fails.
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
    "created_by": "Phoenix"
}


def load_config():
    """Load and validate application configuration"""
    config = {
        "project_id": os.getenv("PROJECT_ID"),
        "service_account_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        "gemini_api_endpoint": os.getenv("GEMINI_API_ENDPOINT"), # The base URL for the parser
    }
    
    missing_vars = [k for k, v in config.items() if not v]
    if missing_vars:
        st.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        st.stop()
    
    return config

def initialize_firebase(service_account_path):
    """Initializes Firebase Admin SDK if not already initialized."""
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error("Failed to initialize Firebase. Check service account credentials.")
            st.exception(e)
            st.stop()
    return firestore.client()

def initialize_secret_manager(service_account_path):
    """Initializes and returns a Secret Manager client using service account credentials."""
    try:
        # secretmanager library uses google-auth to find credentials, but we can be explicit
        from google.oauth2 import service_account
        sm_creds = service_account.Credentials.from_service_account_file(service_account_path)
        return secretmanager.SecretManagerServiceClient(credentials=sm_creds)
    except Exception as e:
        st.error("Failed to initialize Secret Manager client.")
        st.exception(e)
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
    """Fetches a secret from Google Secret Manager, handling errors gracefully."""
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
    try:
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        st.error(f"Failed to access secret '{secret_id}'. Please ensure it exists and the service account has permissions. Error: {e}")
        st.stop()


def validate_scroll_text(text):
    """Validate scroll text input"""
    if not text or len(text.strip()) < 10:
        return False, "Please provide a meaningful response (at least 10 characters)."
    if len(text) > 50000:
        return False, "Text exceeds maximum length of 50,000 characters."
    return True, ""

def parse_scroll_content(text, api_endpoint, api_key):
    """Parse scroll content using Gemini API with robust error handling."""
    payload = {
        "prompt": f"You are Codessa's Reflection Agent. Analyze the following response and extract: summary, topics, tools, actions, enhancements.\n\n{text}"
    }
    # Append the API key as a query parameter, as required by APIs like Google's GenAI
    full_url = f"{api_endpoint}?key={api_key}"
    try:
        response = requests.post(full_url, json=payload, timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.warning(f"API request failed: {str(e)}")
    except ValueError:
        st.warning("API returned malformed data. Could not parse the response.")
    return {}

def create_scroll_document(scroll_id, raw_text, parsed_data):
    """Creates a structured scroll document for Firestore."""
    topics = parsed_data.get("topics", [])
    tools = parsed_data.get("tools", [])

    return {
        "scroll_id": scroll_id,
        "content": {
            "raw_text": raw_text,
            "summary": parsed_data.get("summary", FALLBACK_PARSED_DATA["summary"]),
            "topics": topics,
            "tools": tools,
            "actions": parsed_data.get("actions", []),
            "enhancements": parsed_data.get("enhancements", []),
        },
        "metadata": {
            **DEFAULT_METADATA,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
    }

def display_recent_scrolls(db_client, algolia_index):
    """Queries and displays a paginated list of recent scrolls from Firestore."""
    st.divider()
    st.subheader("📜 Recent Scrolls")

    PAGE_SIZE = 5

    # Initialize session state for managing edit mode and pagination
    if 'editing_scroll_id' not in st.session_state:
        st.session_state.editing_scroll_id = None
    if 'page_cursors' not in st.session_state:
        st.session_state.page_cursors = [None]  # Cursors for start_after(). [None] is for page 0.
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    if 'last_search_term' not in st.session_state:
        st.session_state.last_search_term = ""

    search_term = st.text_input("Search scrolls (full-text search powered by Algolia):", key="scroll_search")

    # If search term changes, reset pagination to start from the beginning of the new results
    if search_term != st.session_state.last_search_term:
        st.session_state.current_page = 0
        st.session_state.page_cursors = [None]
        st.session_state.editing_scroll_id = None
        st.session_state.last_search_term = search_term

    recent_scrolls = []
    has_next_page = False

    try:
        if search_term:
            # --- ALGOLIA SEARCH PATH ---
            search_results = algolia_index.search(
                search_term,
                {'page': st.session_state.current_page, 'hitsPerPage': PAGE_SIZE}
            )
            scroll_ids = [hit['objectID'] for hit in search_results.get('hits', [])]

            if scroll_ids:
                # Fetch full docs from Firestore using the IDs from Algolia
                docs_ref = db_client.collection('scrolls').where('scroll_id', 'in', scroll_ids).stream()
                docs_map = {doc.id: doc for doc in docs_ref}
                # Re-order to match Algolia's relevance ranking
                recent_scrolls = [docs_map.get(sid) for sid in scroll_ids if docs_map.get(sid)]

            total_pages = search_results.get('nbPages', 0)
            has_next_page = st.session_state.current_page < (total_pages - 1)
        else:
            # --- FIRESTORE BROWSE PATH (existing logic) ---
            scrolls_ref = db_client.collection("scrolls")
            query = scrolls_ref.order_by("metadata.created_at", direction=firestore.Query.DESCENDING)
            cursor = st.session_state.page_cursors[st.session_state.current_page]
            if cursor:
                query = query.start_after(cursor)
            
            docs_on_page = list(query.limit(PAGE_SIZE + 1).stream())
            has_next_page = len(docs_on_page) > PAGE_SIZE
            recent_scrolls = docs_on_page[:PAGE_SIZE]

            if has_next_page and len(st.session_state.page_cursors) == st.session_state.current_page + 1:
                st.session_state.page_cursors.append(recent_scrolls[-1])

        if not recent_scrolls:
            if search_term:
                st.info(f"No scrolls found matching '{search_term}'.")
            else:
                st.info("No scrolls found on this page. Create one or check other pages.")
            return

        for scroll in recent_scrolls:
            scroll_data = scroll.to_dict()
            scroll_id = scroll.id
            summary = scroll_data.get("content", {}).get("summary", "No summary available")
            created_at = scroll_data.get("metadata", {}).get("created_at")
            display_time = created_at.strftime("%Y-%m-%d %H:%M UTC") if created_at else "N/A"

            with st.expander(f"**{summary}** (Created: {display_time})"):
                if st.session_state.editing_scroll_id == scroll_id:
                    with st.form(key=f"edit_form_{scroll_id}"):
                        updated_summary = st.text_input("Summary", value=summary)
                        current_topics = scroll_data.get("content", {}).get("topics", [])
                        updated_topics_str = st.text_area("Topics (one per line)", value="\n".join(current_topics))
                        
                        c1, c2, _ = st.columns([1, 1, 5])
                        if c1.form_submit_button("Save Changes", type="primary"):
                            updated_topics = [topic.strip() for topic in updated_topics_str.split("\n") if topic.strip()]
                            db_client.collection("scrolls").document(scroll_id).update({
                                "content.summary": updated_summary, "content.topics": updated_topics
                            })
                            algolia_index.partial_update_object({
                                'objectID': scroll_id, 'summary': updated_summary, 'topics': updated_topics
                            }).wait()
                            st.success("Scroll updated successfully!")
                            st.session_state.editing_scroll_id = None
                            st.rerun()
                        if c2.form_submit_button("Cancel"):
                            st.session_state.editing_scroll_id = None
                            st.rerun()
                else:
                    st.json(scroll_data)
                    c1, c2, _ = st.columns([1, 1, 5])
                    if c1.button("Edit", key=f"edit_{scroll_id}"):
                        st.session_state.editing_scroll_id = scroll_id
                        st.rerun()
                    if c2.button("Delete", key=f"delete_{scroll_id}"):
                        db_client.collection("scrolls").document(scroll_id).delete()
                        algolia_index.delete_object(scroll_id).wait()
                        st.success("Scroll deleted.")
                        st.rerun()

        # Pagination buttons
        col1, col2, col3 = st.columns([1, 1, 5])

        if col1.button("⬅️ Previous", disabled=(st.session_state.current_page == 0)):
            st.session_state.current_page -= 1
            st.session_state.editing_scroll_id = None # Reset edit state on navigation
            st.rerun()

        if col2.button("Next ➡️", disabled=not has_next_page):
            st.session_state.current_page += 1
            # The cursor for the next page is stored when we fetch the data
            st.session_state.editing_scroll_id = None # Reset edit state on navigation
            st.rerun()
        
        col3.write(f"Page {st.session_state.current_page + 1}")

    except Exception as e:
        st.error("Could not fetch recent scrolls. A Firestore index might be required.")
        st.info(f"Error details: {e}. If this is a 'FAILED_PRECONDITION' error, please create the required composite index using the link provided in the terminal or logs.")

# === Main Application Logic ===
config = load_config()
db = initialize_firebase(config["service_account_path"])
secret_client = initialize_secret_manager(config["service_account_path"])

# Fetch Algolia credentials and initialize client
algolia_app_id = get_secret(secret_client, config["project_id"], "algolia-app-id")
algolia_admin_api_key = get_secret(secret_client, config["project_id"], "algolia-admin-api-key")
algolia_client = initialize_algolia(algolia_app_id, algolia_admin_api_key)
algolia_index = algolia_client.init_index("codessa_scrolls")


st.title("Codessa: Inkwell ✍️")
st.markdown("Paste key responses here and turn them into structured memory scrolls.")

scroll_text = st.text_area("Paste ChatGPT Response:", height=300)

if st.button("Parse & Generate Scroll"):
    is_valid, error_msg = validate_scroll_text(scroll_text)
    if not is_valid:
        st.warning(error_msg)
    else:
        scroll_id = str(uuid.uuid4())

        # Fetch the Gemini API key from Secret Manager as per ADR-0005
        gemini_api_key = get_secret(secret_client, config["project_id"], "gemini-api-key")
        parsed_data = parse_scroll_content(scroll_text, config["gemini_api_endpoint"], gemini_api_key)
        if not parsed_data:
            st.info("Parser did not return a result. Using fallback data.")
            parsed_data = FALLBACK_PARSED_DATA
        
        scroll_doc = create_scroll_document(scroll_id, scroll_text, parsed_data)

        try:
            db.collection("scrolls").document(scroll_id).set(scroll_doc)
            # Sync to Algolia
            algolia_record = { "objectID": scroll_id, **scroll_doc['content'] }
            algolia_index.save_object(algolia_record).wait()
            st.success("Scroll successfully created and stored in Firestore & Algolia ✨")
        except Exception as e:
            st.error(f"Failed to store scroll: {str(e)}")
            # Attempt to clean up Firestore entry if Algolia sync fails
            db.collection("scrolls").document(scroll_id).delete()
            st.warning("Rolled back Firestore entry due to sync failure.")

        # Show parsed output
        st.subheader("Parsed Scroll Summary")
        # Note: firestore.SERVER_TIMESTAMP is a sentinel value. It will only be populated
        # with the actual server time after being written and read back from Firestore.
        st.json(scroll_doc)

# Display the list of recent scrolls on every app run
display_recent_scrolls(db, algolia_index)

# === Future: Embed this app in Notion via iframe or WebView ===
# Note: Notion does not support arbitrary iframes directly for security reasons.
# You may need to use tools like Notion Widget Wrappers, third-party embeds, or host
# the app externally (e.g., on Firebase Hosting or Streamlit Cloud) and link to it.
# Security Concerns:
# - Avoid exposing sensitive API keys or Firebase credentials in frontend JS.
# - Limit Firestore rules to read-only access or authenticated sessions if public.
# - Consider using a proxy endpoint to serve data safely.
# - Use appropriate Content Security Policy (CSP) headers and HTTPS for embedding.
