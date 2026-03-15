# The Hive

Awareness and connective tissue for the operating system. Two-layer data model stores entities (structured records in MongoDB) and knowledge (git-tracked markdown files indexed to MongoDB). A unified CLI provides 14 commands for record CRUD, search, sync, and system status. Context assembly sessions use the Hive CLI as their toolkit to hydrate working sessions with relevant context.

## Capabilities

- Two-layer record management: entities (MongoDB source of truth) and knowledge (markdown files + MongoDB index)
- Schema-validated entity types with typed references and reverse lookups
- Knowledge records with YAML frontmatter, wiki-links, and semantic search
- Unified CLI with transparent entity/knowledge routing
- Cross-layer reference traversal (multi-hop)
- Knowledge file sync to MongoDB (with embedding support)
- External system sync adapters (Linear, Calendar, Slack, GitHub)
- Context assembly playbooks for system-specific session initialization
- Self-improvement feedback loop

## Skills

| Skill | Purpose |
|-------|---------|
| `/hive` | Entry point — record CRUD, search, sync, status |

## State

- **MongoDB** — `hive` database, `records` collection. Entities are source of truth here. Knowledge records are derived (rebuilt via sync).
- **Vault** — `hive/` directory with knowledge markdown files (notes, decisions, designs, research, sessions). Git-tracked.
- **Registry** — `hive/.registry/` with entity type YAMLs and ontology.yaml. Git-tracked.

## Dependencies

- MongoDB Community Edition (local, via Homebrew)
- Python 3.12+ with pymongo, pyyaml
- Ollama with nomic-embed-text (for semantic search, Phase 2)
- Git (knowledge files are version-controlled)

## Integration Points

- **Reads from:** Project artifacts, session state files, external system APIs (via sync adapters)
- **Produces:** Entity records, knowledge records, context assembly notes, feedback records
- **Reports to:** Hive UI (Wall tiles), context assembly sessions, working sessions (via `hive get/search/refs`)
- **Used by:** Content system (workflow lifecycle), code-dev skill (checkpointing), session manager (session summaries), brainstorming skill (decision checkpoints)
