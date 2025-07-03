# ADR 0003: Use Firestore for Codessa DevOS Agent State & Memory

- Status: Accepted
- Date: 2024-10-28
- Deciders: Phoenix
- Supersedes: None

## Context and Problem Statement

Codessa DevOS needs persistent memory to store:

- Prompts and agent responses
- Reflections and scrolls
- Agent metadata (status, actions taken, history)
- App-specific configurations and semantic relationships

We require a scalable, fully managed NoSQL database that integrates seamlessly with GCP, supports flexible JSON-like documents, and enables querying, ordering, and indexing over time-based data.

## Considered Options

1. Firestore (Native NoSQL for GCP)
2. Google Cloud SQL (Relational)
3. MongoDB Atlas (3rd-party NoSQL)
4. Redis (in-memory cache)
5. ChromaDB / Pinecone (vector stores only)

## Decision Outcome

Chosen Option: Firestore (in Native mode)

### Positive Consequences

- 🔄 Schema-flexible JSON documents: Ideal for storing unstructured agent responses and scrolls.
- ☁️ Fully Managed: Zero server management and seamless scaling.
- 🔐 Tight GCP Integration: Secured via IAM and service accounts, no need for external credentials.
- 📊 Queryable and Indexed: Supports rich filtering, ordering, timestamps — critical for timeline-based memory.
- 🧠 Native fit for agentic memory graphs (scrolls, tools, reflections, etc.)

### Negative Consequences

- 📉 Not ideal for analytical workloads: Use BigQuery or export for large-scale analysis.
- 💰 Pricing considerations: Reads/writes and document sizes must be monitored to manage cost.
- 🔃 No full-text search: We'll use Vertex AI Search or integrate a vector DB for semantic search if needed.

## Notes

Firestore will serve as Codessa's "short-to-medium term memory" layer, storing structured user and agent data. For semantic retrieval or multi-turn vector-based recall, we may layer in a vector database such as ChromaDB or Pinecone in Phase 2.

This ADR is part of the MVP-1 stack: Streamlit + Firestore + Secret Manager + Vertex AI.

## References

- [Firestore](https://cloud.google.com/firestore)
- [Google Cloud SQL](https://cloud.google.com/sql)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [Redis](https://redis.io/)
- [ChromaDB](https://www.trychroma.com/)
- [Pinecone](https://www.pinecone.io/)
- [Vertex AI Search](https://cloud.google.com/vertex-ai/docs/generative-ai/search/overview)
- [BigQuery](https://cloud.google.com/bigquery)
- [Secret Manager](https://cloud.google.com/secret-manager)

## Conclusion

This decision establishes Firestore as the primary persistence layer for Codessa DevOS agent state and memory, leveraging its strengths for flexible, scalable document storage within the GCP ecosystem. Future ADRs will detail the specific data models and collection structures within Firestore.
