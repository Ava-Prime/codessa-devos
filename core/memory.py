# core/memory.py

from google.cloud import firestore
from typing import List, Dict, Optional

db = firestore.Client()

# === Memory Cortex: CREATE ===
def create_scroll(agent_id: str, prompt: str, response: str, metadata: Optional[dict] = None) -> str:
    doc_ref = db.collection("scrolls").document()
    data = {
        "agent_id": agent_id,
        "prompt": prompt,
        "response": response,
        "metadata": metadata or {},
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
        "phase": "MVP-1",
        "status": "active"
    }
    doc_ref.set(data)
    return doc_ref.id

# === Memory Cortex: RETRIEVE ===
def get_scrolls(agent_id: str, limit: int = 10) -> List[Dict]:
    query = (
        db.collection("scrolls")
        .where("agent_id", "==", agent_id)
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
    )
    return [doc.to_dict() | {"id": doc.id} for doc in query.stream()]

# === Memory Cortex: REFLECT ===
def reflect_scrolls(agent_id: str, limit: int = 10) -> str:
    scrolls = get_scrolls(agent_id, limit)
    concatenated = "\n\n".join([f"Prompt: {s['prompt']}\nResponse: {s['response']}" for s in scrolls])
    # Placeholder: Replace this with a call to Vertex AI or Gemini
    reflection = f"Ava reflected on {len(scrolls)} memories:\n\n{concatenated}"
    return reflection

# === Memory Cortex: UPDATE === 
def update_scroll(scroll_id: str, updated_data: dict) -> None:
    doc_ref = db.collection("scrolls").document(scroll_id)
    doc_ref.update(updated_data)
    return
# === Memory Cortex: DELETE ===
def delete_scroll(scroll_id: str) -> None:
    doc_ref = db.collection("scrolls").document(scroll_id)
    doc_ref.delete()
    return
# === Memory Cortex: LIST ALL ===
def list_all_scrolls() -> List[Dict]:
    query = db.collection("scrolls").order_by("created_at", direction=firestore.Query.DESCENDING)
    return [doc.to_dict() | {"id": doc.id} for doc in query.stream()]
# === Memory Cortex: GET BY ID ===
def get_scroll_by_id(scroll_id: str) -> Dict:
    doc_ref = db.collection("scrolls").document(scroll_id)
    doc = doc_ref.get()
    doc_dict = doc.to_dict()
    if doc.exists and doc_dict is not None:
        return doc_dict | {"id": doc.id}
    else:
        return {}
# === Memory Cortex: GET BY AGENT ID ===
def get_scrolls_by_agent_id(agent_id: str) -> List[Dict]:
    query = db.collection("scrolls").where("agent_id", "==", agent_id)
    return [doc.to_dict() | {"id": doc.id} for doc in query.stream()]
# === Memory Cortex: GET BY PHASE ===
def get_scrolls_by_phase(phase: str) -> List[Dict]:
    query = db.collection("scrolls").where("phase", "==", phase)
    return [doc.to_dict() | {"id": doc.id} for doc in query.stream()]   
# === Memory Cortex: GET BY STATUS ===
def get_scrolls_by_status(status: str) -> List[Dict]:
    query = db.collection("scrolls").where("status", "==", status)
    return [doc.to_dict() | {"id": doc.id} for doc in query.stream()]
# === Memory Cortex: GET BY AGENT ID AND PHASE ===
def get_scrolls_by_agent_id_and_phase(agent_id: str, phase: str) -> List[Dict]:
    query = (
        db.collection("scrolls")
        .where("agent_id", "==", agent_id)
        .where("phase", "==", phase)
    )
    return [doc.to_dict() | {"id": doc.id} for doc in query.stream()]
# === Memory Cortex: GET BY AGENT ID AND STATUS ===
# def get_scrolls_by_agent_id_and_status(agent_id: str, status: str) ->
def get_scrolls_by_agent_id_and_status(agent_id: str, status: str) -> List[Dict]:
    query = (
        db.collection("scrolls")
        .where("agent_id", "==", agent_id)
        .where("status", "==", status)
    )
    return [doc.to_dict() | {"id": doc.id} for doc in query.stream()]
def get_scrolls_by_phase_and_status(phase: str, status: str) -> List[Dict]:
    query = (
        db.collection("scrolls")
        .where("phase", "==", phase)
        .where("status", "==", status)
    )
    return [doc.to_dict() | {"id": doc.id} for doc in query.stream()]
# === Memory Cortex: GET BY AGENT ID, PHASE, AND STATUS ===
def get_scrolls_by_agent_id_phase_and_status(agent_id: str, phase: str, status: str) -> List[Dict]:
    query = (
        db.collection("scrolls")
        .where("agent_id", "==", agent_id)
        .where("phase", "==", phase)
        .where("status", "==", status)
    )
    return [doc.to_dict() | {"id": doc.id} for doc in query.stream()]