---
name: hive
description: Unified record management — entities (people, companies, projects, workflows) and knowledge (decisions, designs, research, notes) with two-layer storage, semantic search, and cross-system sync. Use when creating records, searching knowledge, checking refs, or querying the Hive.
argument-hint: [status | get <id> | create <type> "title" | search "query" | list <type> | refs <id> | recent]
---

# The Hive

Awareness and connective tissue for the operating system. Two-layer data model: entities (structured, MongoDB) and knowledge (markdown files, git-tracked, MongoDB-indexed).

## Status Check

```bash
hive status && echo "HIVE OK" || echo "HIVE NOT AVAILABLE"
```

## Setup

If hive is not available:

```bash
# 1. Install MongoDB
brew tap mongodb/brew && brew install mongodb-community && brew services start mongodb-community

# 2. Initialize Hive
hive init
```

## Architecture

**Two layers:**
- **Entities** — person, company, product, project, workflow, meeting, brand, platform, channel. Stored in MongoDB only. Schema-validated via `.registry/types/`.
- **Knowledge** — notes, decisions, designs, research, session summaries, feedback. Markdown files with YAML frontmatter in `hive/`. MongoDB indexes them for search.

**Routing:** The CLI auto-detects which layer based on the argument. If it's a registered entity type → MongoDB. If it's a known tag → markdown file + index. Entity types and tags are always disjoint sets.

**Output format:** JSON when piped, text when interactive. Override with `--format json|text|md`.

## Commands

### Get a record: `hive get <id>`

```bash
hive get craig                         # Entity by slug
hive get 2026-03-15-hive-design        # Knowledge by date-slug
hive get craig --fields name,email     # Specific fields
hive get craig --format json           # Force JSON output
```

### Create a record: `hive create <type-or-tag> "title"`

```bash
# Entities (→ MongoDB)
hive create person "Craig" --email craig@indemn.ai --company indemn --domains indemn
hive create company "Indemn" --domains indemn --industry "Insurance Technology"
hive create workflow "Voice Scoring UI" --objective "Build scoring component" --domains indemn --refs project:platform-dev
hive create project "Hive" --domains indemn --status active

# Knowledge (→ markdown file + MongoDB index)
hive create decision "Use two-layer architecture" --domains indemn --refs project:hive --rationale "Simpler than 14+ types"
hive create note "Interesting pattern" --domains personal --body "Content goes here"
hive create design "Hive CLI spec" --domains indemn --refs project:hive --status active
hive create research "PKM tool comparison" --domains personal
```

### Update a record: `hive update <id>`

```bash
hive update craig --status inactive
hive update voice-scoring-ui --current-context "Session 3 done. Remaining: tests."
hive update voice-scoring-ui --add-sessions session-uuid-4
hive update 2026-03-15-hive-design --add-tags architecture --status done
hive update craig --add-refs project:hive
```

### Search: `hive search "query"`

```bash
hive search "voice scoring"                          # Semantic + keyword
hive search "deployment" --domains indemn             # Filter by domain
hive search "decision" --tags decision --recent 30d   # Decisions from last 30 days
hive search "Craig" --entities-only                   # Only entities
hive search "architecture" --knowledge-only --limit 5 # Only knowledge, top 5
```

### List records: `hive list <type-or-tag>`

```bash
hive list person                             # All people
hive list person --domain indemn             # Indemn people only
hive list workflow --status active           # Active workflows
hive list decision --recent 30d             # Recent decisions
hive list note --refs-to craig              # Notes referencing Craig
```

### References: `hive refs <id>`

```bash
hive refs craig                              # All refs to/from Craig
hive refs craig --direction out              # Only outbound
hive refs indemn --direction in              # Everything referencing Indemn
hive refs voice-scoring-ui --depth 2         # Two-hop traversal
```

### Recent activity: `hive recent [duration]`

```bash
hive recent                                  # Last 7 days (default)
hive recent 30d                              # Last 30 days
hive recent 7d --domains indemn              # Indemn activity only
hive recent 24h --types person,workflow      # Recent people and workflows
```

### Sync: `hive sync [system]`

```bash
hive sync                                    # Re-index all knowledge files
hive sync --re-embed                         # Re-generate embeddings
hive sync --no-embed                         # Fast sync, skip embedding
hive sync linear                             # Pull from Linear (Phase 3)
hive sync calendar                           # Pull from Calendar (Phase 3)
```

### Feedback: `hive feedback "message"`

```bash
hive feedback "Search should weight recent records higher"
# Auto-tags: [feedback, hive-improvement]
# Auto-links to current session context
```

### Status: `hive status`

```bash
hive status                                  # Record counts, MongoDB status
```

### Init: `hive init`

```bash
hive init                                    # Verify MongoDB, indexes, vault, run sync
```

### Registry: `hive types|tags|domains`

```bash
hive types list                              # All entity types
hive types show person                       # Person type schema
hive tags list                               # All knowledge tags
hive domains list                            # All domains
```

### Graph Quality: `hive health | archive`

```bash
hive health                                  # Graph health score, stale/orphan counts
hive archive --days 60 --dry-run             # Preview stale records to archive
hive archive --days 60                       # Actually archive them
hive archive --days 30 --type workflow       # Archive only stale workflows
```

### Ontology: `hive ontology check|usage`

```bash
hive ontology check                          # Find unused tags, unregistered tags, merge candidates
hive ontology usage                          # Tag usage statistics with visual bars
```

### Cross-Domain Discovery: `hive discover`

```bash
hive discover                                # Find connections across domain boundaries
hive discover --limit 10                     # Top 10 cross-domain connections
```

## Knowledge Directories

| Tag | Directory |
|-----|-----------|
| note | `hive/notes/` |
| decision | `hive/decisions/` |
| design | `hive/designs/` |
| research | `hive/research/` |
| session_summary | `hive/sessions/` |
| feedback | `hive/notes/` |
| context_assembly | `hive/sessions/` |

## Knowledge Frontmatter Format

```yaml
---
title: "Record title"
tags: [decision, architecture]
domains: [indemn]
refs:
  project: hive
  people: [craig]
status: active
created: 2026-03-15
rationale: "Optional per-tag convention fields"
---

# Record Title

Body content with [[wiki-links]] to other knowledge records.
```
