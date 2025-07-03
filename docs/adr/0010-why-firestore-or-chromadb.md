# ADR 0010: Choose Firestore (and/or ChromaDB) for Memory Cortex and Persistent Storage

- Status: Accepted
- Date: 2024-11-02
- Deciders: Phoenix

## Context and Problem Statement

Codessa DevOS requires a robust memory subsystem to persist:

- Prompts, responses, and agent interactions (scrolls)
- User-created Codex blueprints and architecture specs
- Generated plans, metadata, timestamps, summaries
- Vector-augmented memory lookups and context awareness
- Session continuity, history, and agent reflections

This persistent memory layer is referred to as the Codessa Memory Cortex. We considered options for both document-based storage and vector search capabilities.

## Considered Options

1. Firestore (native GCP NoSQL database)
2. ChromaDB (lightweight, local or hosted vector DB)
3. Pinecone (managed vector DB, pay-per-query)
4. Supabase (Postgres + pgvector alternative)
5. BigQuery (not ideal for transactional app storage)
6. Custom local SQLite or flat files (limited, fragile)

## Decision Outcome

🧠 Hybrid Chosen: Firestore (primary) + ChromaDB (secondary for vector memory)

### Positive Consequences

- 🔁 Firestore provides real-time syncing, strong GCP IAM integration, and schema flexibility.
- 📚 Great fit for storing scrolls, codex metadata, action logs, and semantic memory.
- 🧠 ChromaDB can run embedded or server-mode for fast vector retrieval of summaries, reflections, and embeddings.
- 💰 Cost-effective and serverless: Firestore scales on demand; ChromaDB can run locally during dev or hosted for prod.
- 🔐 Strong security model via Firestore IAM and VPC Service Controls.

### Negative Consequences

- 🧩 ChromaDB does not offer high-availability or managed hosting (must be self-deployed or embedded).
- 📥 Requires dual syncing model: structured data → Firestore, embeddings → Chroma.
- 🔃 Firestore has limited support for advanced graph queries or text search (requires augmentation).
- ⚙️ Manual consistency required between vector and document stores.

## Integration Strategy

We use Firestore as the source of truth for all symbolic memory — scrolls, codices, agents, and context state.

ChromaDB serves as a context-augmented semantic lookup engine for:

- Most similar prior reflections
- Scroll summaries
- Agent memory embeddings

🗂 Firestore Schema (Example):

- codessa-reflections/{uuid}
- codex-scripts/{id}
- agent-events/{timestamp}
- memory-embeddings/{uid}

📦 ChromaDB Usage:

- Collection: memory-reflections
- Metadata: { "agent": "codessa", "phase": "MVP-1", "type": "scroll" }

Example sync flow:

```text
Scroll Generated → Firestore (structured)
               ↘
                → ChromaDB (semantic embedding)

Justification
Firestore + ChromaDB enables a powerful hybrid memory architecture: Firestore gives structured, timestamped, secure storage; Chroma enables fast, intelligent context retrieval — critical for reasoning agents like Codessa. Together, they form the backbone of Codessa’s Memory Cortex.
