# services/firestore_client.py

import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

class FirestoreClient:
    """
    A client for interacting with the Firestore database for Ava's Memory Cortex.
    """
    def __init__(self):
        """
        Initializes the Firestore client.
        Expects the GOOGLE_CLOUD_PROJECT environment variable to be set.
        """
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set.")
        
        # Initialize the Firestore DB client
        self.db = firestore.Client(project=self.project_id)
        print(f"✅ FirestoreClient initialized for project: {self.project_id}")

    # --- Generic CRUD Methods ---

    def add(self, collection_name: str, data: Dict[str, Any], doc_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Adds a new document to a specified collection.

        Args:
            collection_name: The name of the collection.
            data: A dictionary containing the data for the new document.
            doc_id: Optional. The ID for the document. If not provided, a UUID is generated.

        Returns:
            The full document data, including the ID and created_at timestamp.
        """
        doc_id = doc_id or str(uuid.uuid4())
        doc_ref = self.db.collection(collection_name).document(doc_id)
        
        # Add server timestamp and ID to the data
        data['created_at'] = firestore.SERVER_TIMESTAMP
        data['id'] = doc_id
        
        doc_ref.set(data)
        
        # To return the full data with the resolved timestamp, we get it back
        # Note: This adds a slight delay but ensures consistency.
        created_doc = doc_ref.get().to_dict()
        print(f"📄 Added document '{doc_id}' to collection '{collection_name}'.")
        return created_doc

    def get(self, collection_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a document from a collection by its ID.

        Args:
            collection_name: The name of the collection.
            doc_id: The ID of the document to retrieve.

        Returns:
            A dictionary representing the document, or None if not found.
        """
        doc_ref = self.db.collection(collection_name).document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            print(f"📄 Retrieved document '{doc_id}' from collection '{collection_name}'.")
            return doc.to_dict()
        else:
            print(f"⚠️ Document '{doc_id}' not found in collection '{collection_name}'.")
            return None

    def list(self, collection_name: str, filters: Optional[List[tuple]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Lists documents in a collection, with optional filtering.

        Args:
            collection_name: The name of the collection.
            filters: A list of tuples for filtering, e.g., [("status", "==", "active")].
            limit: The maximum number of documents to return.

        Returns:
            A list of dictionaries, where each dictionary is a document.
        """
        query = self.db.collection(collection_name)
        
        if filters:
            for f in filters:
                try:
                    field, op, value = f
                    query = query.where(filter=FieldFilter(field, op, value))
                except ValueError as e:
                    print(f"⚠️ Invalid filter provided: {f}. Error: {e}")
                    return []

        docs = query.limit(limit).stream()
        results = [doc.to_dict() for doc in docs]
        print(f"📄 Listed {len(results)} documents from collection '{collection_name}'.")
        return results

    # --- Collection-Specific Methods for SCROLLS ---

    def add_scroll(self, prompt: str, response: str, **kwargs) -> Dict[str, Any]:
        """
        Adds a new 'scroll' document.

        Args:
            prompt: The user prompt or event trigger.
            response: The assistant's response.
            **kwargs: Additional fields for the scroll document (e.g., summary, topics).

        Returns:
            The newly created scroll document as a dictionary.
        """
        scroll_data = {
            "prompt": prompt,
            "response": response,
            "summary": kwargs.get("summary", ""),
            "topics": kwargs.get("topics", []),
            "tools": kwargs.get("tools", []),
            "actions": kwargs.get("actions", []),
            "phase": kwargs.get("phase", "mvp-1"),
            "created_by": kwargs.get("created_by", "Phoenix"),
            "status": kwargs.get("status", "active"),
        }
        return self.add("scrolls", scroll_data)

    def get_scroll(self, scroll_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a scroll by its ID."""
        return self.get("scrolls", scroll_id)

    # --- Collection-Specific Methods for AGENTS ---
    
    def add_agent(self, name: str, role: str, description: str, **kwargs) -> Dict[str, Any]:
        """
        Adds a new 'agent' document. The document ID will be a slugified version of the name.

        Args:
            name: The agent's name (e.g., "Ava Prime").
            role: The agent's primary function (e.g., "reflection-engine").
            description: A summary of the agent's purpose.
            **kwargs: Additional fields for the agent document (e.g., tools, state).

        Returns:
            The newly created agent document as a dictionary.
        """
        # Create a URL-friendly slug from the name for the ID
        agent_id = name.lower().replace(" ", "-").replace("_", "-")

        agent_data = {
            "name": name,
            "description": description,
            "role": role,
            "tools": kwargs.get("tools", []),
            "state": kwargs.get("state", "active"),
            "metadata": kwargs.get("metadata", {}),
        }
        return self.add("agents", agent_data, doc_id=agent_id)

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an agent by its ID (slug)."""
        return self.get("agents", agent_id)

# Example usage (for testing purposes)
if __name__ == "__main__":
    # Ensure you have run 'gcloud auth application-default login'
    # and set 'GOOGLE_CLOUD_PROJECT'
    try:
        client = FirestoreClient()
        print("\n--- Testing FirestoreClient ---")
        
        # Test Agent Creation
        print("\n1. Testing Agent Creation...")
        ava_prime_data = {
            "name": "Ava Prime",
            "role": "core-consciousness",
            "description": "The primary instance of the Ava agent.",
            "tools": ["Gemini-1.5-Pro", "VertexAI-Search"],
            "metadata": {"version": "1.0.0"}
        }
        agent_doc = client.add_agent(**ava_prime_data)
        print("   ✅ Created Agent:", agent_doc.get('name'))
        
        retrieved_agent = client.get_agent(agent_doc['id'])
        assert retrieved_agent is not None
        assert retrieved_agent['name'] == "Ava Prime"
        print(f"   ✅ Retrieved Agent: {retrieved_agent['name']} with ID: {retrieved_agent['id']}")

        # Test Scroll Creation
        print("\n2. Testing Scroll Creation...")
        scroll_doc = client.add_scroll(
            prompt="What is the capital of France?",
            response="The capital of France is Paris.",
            topics=["geography", "trivia"],
            tools=["Gemini-1.5-Pro"],
            created_by="Phoenix-Test"
        )
        print("   ✅ Created Scroll with ID:", scroll_doc.get('id'))

        retrieved_scroll = client.get_scroll(scroll_doc['id'])
        assert retrieved_scroll is not None
        assert "Paris" in retrieved_scroll['response']
        print(f"   ✅ Retrieved Scroll prompt: '{retrieved_scroll['prompt']}'")

        # Test Listing
        print("\n3. Testing Listing Scrolls...")
        active_scrolls = client.list("scrolls", filters=[("status", "==", "active")], limit=5)
        print(f"   ✅ Found {len(active_scrolls)} active scrolls.")
        assert len(active_scrolls) > 0

        print("\n--- FirestoreClient tests passed! ---")

    except (ValueError, ImportError) as e:
        print(f"\n❌ Error: {e}")
        print("   Please ensure you have authenticated with Google Cloud CLI:")
        print("   gcloud auth application-default login")
        print("   And set the GOOGLE_CLOUD_PROJECT environment variable:")
        print("   export GOOGLE_CLOUD_PROJECT='your-gcp-project-id'")