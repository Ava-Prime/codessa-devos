# ADR 0006: Use Google Firestore for Semantic Memory & Reflection Logs

- Status: Accepted
- Date: 2024-10-30
- Deciders: Phoenix

## Context and Problem Statement

Codessa DevOS requires a persistent memory store for:

- Logging user-agent interactions (prompts, responses, metadata)
- Storing "Scrolls" — structured semantic documents and reflections
- Supporting structured queries for summarization, search, and agent cognition
- Enabling memory replay and retrieval-augmented generation (RAG)
- Scaling across multiple agents in a multi-tenant system

We need a managed, scalable, cloud-native NoSQL solution with strong GCP integration, support for structured documents, and real-time querying.

## Considered Options

1. 🗂️ Firestore (native to GCP, serverless, NoSQL document store)
2. 🛢️ BigQuery (optimized for analytics, not realtime writes)
3. 🧠 ChromaDB / Weaviate / Pinecone (optimized for vector storage only)
4. 🧱 MongoDB Atlas (external, GCP-compatible but 3rd party)
5. 📄 SQLite (local, embedded, non-cloud-native)

## Decision Outcome

Chosen Option: Firestore (Native Mode)

### Positive Consequences

- ✅ Serverless, GCP-native: Zero ops, autoscaling, high availability
- 🔐 IAM-controlled access with service accounts
- 🧠 Hierarchical document schema supports nested data (scrolls, summaries, actions)
- 🔄 Real-time sync support (ideal for future agent coordination)
- 📊 Easily exportable to BigQuery for downstream analytics
- 📍 Built-in support for structured querying, filters, ordering, pagination
- 💬 Streamlit, Functions, and Agents can access the same shared memory store

### Negative Consequences

- ⏱ Querying at scale requires indexing (manual tuning needed for complex queries)
- ❌ No built-in vector similarity search (must integrate separately)
- 💰 Document read costs can add up at high volume (requires caching)
- 🔐 Field-level encryption or row-level ACLs not natively supported

## Notes

Firestore is currently used to store:

- codessa-reflections (raw prompts + Gemini/Vertex responses)
- scrolls (semantic memory, structured reflections, agent logs)
- metadata for conversations, users, tools, and tasks (planned)

The schema is designed for maximum flexibility, with potential evolution toward hybrid storage (Firestore for metadata + Vector DB for embeddings).

Future Phases may add:

- Firestore triggers to generate summaries or sync to Notion
- Use of ChromaDB or Vertex AI Vector Search for RAG
- Export pipelines to BigQuery or Data Studio dashboards

### Additional Notes

- **Scalability**: Firestore's ability to handle large datasets and high read/write volumes makes it suitable for Codessa's growing memory needs.
- **Integration with GCP Ecosystem**: Seamless integration with other Google Cloud services (e.g., Cloud Functions, Cloud Run, Vertex AI) simplifies development and deployment.
- **Flexible Data Model**: The NoSQL document model allows for flexible schema design, accommodating evolving data structures for reflections and semantic memory.
