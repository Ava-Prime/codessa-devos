# ADR 0012: Define Initial Firestore Data Model for 'Scrolls' and 'Agents'

- **Status:** Accepted  
- **Date:** 2025-07-03  
- **Deciders:** Phoenix  

## Context and Problem Statement

Codessa DevOS leverages Firestore as its primary structured memory store to persist conversations, reflections, scrolls, and metadata for AI agents. To maintain consistency and enable efficient queries, a clear and extensible data model must be defined upfront, particularly for two core collections: `scrolls` and `agents`.

The `scrolls` collection stores structured representations of user interactions, AI reflections, and summarized knowledge artifacts.

The `agents` collection tracks metadata about the AI agents themselves, including state, configuration, and capabilities.

## Considered Options

- Flexible schema-less storage without enforced structure  
- Strict schema definitions enforced via validation layers or code  
- Hybrid approach: well-defined document schemas with allowance for extensions  

## Decision Outcome

**Chosen option:** Hybrid schema approach with documented field definitions and validation in application code to maintain flexibility while ensuring data consistency.

---

## Firestore Collections and Document Schemas

### Collection: `scrolls`

Each document represents a knowledge artifact or conversation reflection.

| Field Name        | Type          | Description                                      |
|-------------------|---------------|------------------------------------------------|
| `id`              | `string`      | Firestore document ID (UUID)                    |
| `created_at`      | `timestamp`   | Creation timestamp                              |
| `updated_at`      | `timestamp`   | Last update timestamp                           |
| `title`           | `string`      | Human-readable title of the scroll              |
| `summary`         | `string`      | Auto-generated or user-written summary          |
| `content`         | `string`      | Full textual content of the scroll               |
| `topics`          | `array<string>` | Tags or key topics extracted from the scroll   |
| `related_agents`  | `array<string>` | References to agent IDs involved in this scroll |
| `status`          | `string`      | Status flags (e.g., "draft", "finalized")       |
| `created_by`      | `string`      | Identifier of the user or system who created it |

### Collection: `agents`

Each document represents a configured AI agent within the Codessa ecosystem.

| Field Name        | Type          | Description                                      |
|-------------------|---------------|------------------------------------------------|
| `id`              | `string`      | Firestore document ID (agent name or UUID)     |
| `name`            | `string`      | Human-readable name of the agent                 |
| `description`     | `string`      | Brief description of the agent’s purpose          |
| `config`          | `map`         | Configuration parameters and settings            |
| `status`          | `string`      | Operational status (e.g., "active", "paused")    |
| `created_at`      | `timestamp`   | Creation timestamp                                |
| `last_active_at`  | `timestamp`   | Last heartbeat or usage timestamp                 |
| `owner`           | `string`      | User or system owner identifier                    |

---

## Positive Consequences

- Enables consistent queries and data integrity  
- Simplifies front-end UI and back-end logic development  
- Supports extensibility by allowing extra fields in `config` or content  
- Facilitates auditability and operational monitoring of agents and scrolls  

## Negative Consequences

- Slight overhead in maintaining schema documentation and validation  
- Potential need for schema migrations if data model evolves significantly  

---

## Future Considerations

- Implement Firestore security rules based on these schemas  
- Build client-side validation and error reporting for writes  
- Consider versioning scrolls and agent configs for audit trails  

---

## Related Decisions

- ADR 0010: Why Firestore for Structured Memory  
- ADR 0011: Why Streamlit for Rapid Developer UI  
- ADR 0001: Use Google Vertex AI for the Core LLM Engine  
