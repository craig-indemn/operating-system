---
ask: "Design the Hive — a unified awareness, knowledge, and work system that becomes the connective tissue for all of Craig's work, personal projects, and life systems"
created: 2026-03-08
workstream: os-development
session: 2026-03-08-a
sources:
  - type: session
    description: "Extended brainstorming session — vision, data model, context assembly, system integration"
  - type: web
    description: "Research on Tana, Zettelkasten, graph RAG, PKM tools"
  - type: linear
    description: "Queried Linear teams and issues to understand current work tracking"
---

# The Hive — Design Document

## Vision

The Hive is the awareness and connective tissue layer for the operating system. It's where all knowledge, work, decisions, and connections live — across every domain (Indemn, Career Catalyst, Personal, and anything else). It doesn't replace the systems that do the actual work (content system, code repos, dispatch, deployment pipelines). It makes them all visible, linked, and contextually accessible.

**The Hive is a brain. Systems are the hands.** The hands do the work. The brain remembers what happened, knows what's connected, and provides context for the next action.

**Core value proposition:** Any Claude Code session can start working on any topic and immediately have the right context — what's been done, what's in flight, what's connected, what skills are relevant — without anyone manually curating that context.

## Principles

1. **Two layers: entities and knowledge.** Structured entities (person, company, project, workflow) live in MongoDB with schemas defined in the type registry. Knowledge records (decisions, designs, research, session summaries, notes) are git-tracked markdown files with YAML frontmatter, differentiated by tags — not separate type schemas. Entities are the deterministic anchors for context assembly; knowledge is discovered through traversal and search from those anchors.
2. **The Hive is connective tissue, not a replacement.** Systems keep their own architectures. The Hive connects and indexes them.
3. **Context is assembled, not curated.** An LLM produces tailored session initialization instructions from the graph. No manual INDEX.md maintenance.
4. **The registry is the contract.** A controlled vocabulary (types, tags, domains) ensures consistency across all sessions and systems. It evolves deliberately.
5. **Structure enables intelligence.** Typed records with explicit relationships let the system pre-filter, traverse connections, and answer structured queries — not just grep through flat files. The more the system knows about its data, the better it serves.
6. **The system runs itself.** Everything is done through Claude Code sessions. The Hive is designed for LLM consumption first, human visualization second.
7. **Scalable in every direction.** Add new entity types, new systems, new domains, new products, new companies — the core architecture doesn't change. Configuration-driven extensibility.

---

## Architecture Overview

```
You (director)
    ↓
Hive UI (Wall + Focus Area)
    ↓ spawns
Context Assembly Session (short-lived — gathers context, writes note, terminates)
    ↓ then
Working Session (Claude Code — starts hydrated with context note)
    ↓ uses
System Skills (/content, /dispatch, /code-dev, etc.)
    ↓
System CLIs (content, dispatch, etc.)
    ↓
Hive CLI (hive) — unified record CRUD, search, context queries
    ↓
Hive Data Layer (two layers: entities in MongoDB + knowledge as git-tracked markdown)
```

**Four layers:**
- **Hive Data Layer** — two-layer architecture. Entities (person, company, project, workflow) are source of truth in local MongoDB — structured, schema-validated, never files. Knowledge records (decisions, designs, research, session summaries, notes) are git-tracked markdown files with YAML frontmatter — MongoDB indexes them (derived) for search. Embeddings stored in MongoDB for semantic search.
- **Hive CLI** — Python tool with 14 unified commands. Entity/knowledge distinction is transparent — the CLI routes based on whether the argument is a registered entity type or a knowledge tag. JSON when piped, text when interactive.
- **Context Assembly** — a dedicated, short-lived Claude Code session that uses the Hive CLI as its toolkit. Reads user intent, queries both layers, explores codebase if relevant, writes a comprehensive context note. Each system defines its own context playbook in its skill.
- **System Integration** — each system reports to the Hive through its own CLI. Systems own workflow lifecycle (creation, updates, completion). Sync adapters pull/push external system data. The Hive stores and indexes; systems manage domain logic.

---

## Data Model: Two-Layer Architecture

The Hive uses a two-layer data architecture. **Entities** are structured records in MongoDB — the deterministic entry points for context assembly. **Knowledge** is prose in git-tracked markdown files — discovered through traversal and search from entity anchors.

### Why Two Layers

The previous design (session 2026-03-14-a) defined 14+ types with YAML schema definitions, all stored as files with MongoDB as a derived index. This created problems:

1. **File↔database sync complexity** — every entity existed in two places (YAML file + MongoDB). Keeping them in sync is an entire class of bugs.
2. **Entity files nobody would open** — `people/craig.yaml` is structured data. You'd never open it in a text editor. You'd use the CLI or UI. So why is it a file?
3. **Knowledge type proliferation** — does a `decision` really need a different type schema from a `note` tagged `decision`? The context assembly agent finds decisions through semantic search and tag filtering, not through type-specific queries.

**The principle:** If the context assembly agent needs to find it by structured query as a starting point → entity type with schema in MongoDB. If it's discovered through traversal or search from those starting points → knowledge record (markdown note with tags and refs).

### Layer 1: Entities (MongoDB Only)

Entities are structured records that live exclusively in MongoDB. They have schemas defined in `.registry/types/`. They are the deterministic entry points for context assembly — things the agent can query by name, structured fields, and typed relationships.

```yaml
# hive/.registry/types/person.yaml
type: person
fields:
  name: { type: string, required: true }
  email: { type: string }
  role: { type: string }
  company: { type: ref, target: company }
  domains: { type: list, required: true }
  tags: { type: list }
  status: { type: enum, values: [active, inactive, archived] }
display: name
```

```yaml
# hive/.registry/types/workflow.yaml
type: workflow
fields:
  name: { type: string, required: true }
  objective: { type: string, required: true }
  status: { type: enum, values: [active, paused, completed] }
  current_context: { type: string }
  sessions: { type: list }
  project: { type: ref, target: project }
  artifacts: { type: list }
  domains: { type: list, required: true }
  tags: { type: list }
display: name
```

**Entity properties:**
- Created and queried via the Hive CLI (`hive create person`, `hive get craig`)
- Stored only in MongoDB (not as files)
- Not git-tracked (backed up via MongoDB dumps)
- Connected to each other via typed references (person → company, workflow → project)
- Schema-validated on create/update

#### Core Entity Types

| Type | Key Fields | Purpose |
|------|-----------|---------|
| `person` | name, email, role, company→Company | People in Craig's world |
| `company` | name, industry, relationship | Organizations |
| `product` | name, company→Company, status | Things being built |
| `project` | name, status, domain, team→Person[] | Work areas |
| `workflow` | objective, status, current_context, sessions, project→Project | Long-running work state (replaces INDEX.md) |
| `meeting` | date, summary, attendees→Person[], company→Company | Meetings |
| `brand` | name, voice, platforms | Content brands |
| `platform` | name, type, url | Publishing/service platforms |
| `channel` | name, platform→Platform, brand→Brand | Content channels |

#### Sync-Added Entity Types

| Type | Added By | Key Fields |
|------|---------|-----------|
| `linear_issue` | Linear sync | key, title, status, assignee→Person, team |
| `calendar_event` | Calendar sync | start, end, location, attendees→Person[] |
| `email_thread` | Email sync | subject, from→Person, status |
| `slack_message` | Slack sync | channel, from→Person, thread_id |
| `github_pr` | GitHub sync | repo, number, status, author→Person |

### Layer 2: Knowledge (Markdown Files, Git-Tracked)

Knowledge records are prose with YAML frontmatter. They live as markdown files in the `hive/` directory, version-controlled by Git. MongoDB indexes them (derived) for semantic search and structured queries.

Knowledge records are differentiated by **tags, not separate type schemas:**

| Tag | Convention Fields | When Used |
|-----|------------------|----------|
| `note` | title, tags, domains, refs | Quick thoughts, observations, ideas — the catch-all |
| `decision` | rationale, alternatives | A choice was made with reasoning |
| `design` | status | Specs, architecture docs |
| `research` | sources, urls | External information brought in |
| `session_summary` | accomplished, next_steps | Created at session close |
| `feedback` | (auto-linked to session context) | Self-improvement signals |
| `context_assembly` | (auto-linked to workflow) | Context notes written by assembly sessions |

#### Knowledge Record Format

All knowledge records use the same structure regardless of tag:

```markdown
---
title: "Use two-layer architecture instead of 14+ types"
tags: [decision, architecture]
domains: [indemn]
refs:
  project: hive
  people: [craig]
status: active
created: 2026-03-14
rationale: "Structured entities with typed references enable deterministic traversal..."
alternatives:
  - "Keep flat notes with wiki-links only"
  - "Full type system for all records"
---

# Use two-layer architecture instead of 14+ types

The Hive needs structured entry points for context assembly to work reliably...

This builds on [[2026-03-08-hive-vision]] and addresses the retrieval
challenges identified in [[2026-03-09-context-assembly-gaps]].
```

**Notes on knowledge records:**
- `tags` determine the "kind" — no schema validation, just convention
- `refs` connect to entities in MongoDB (resolved by the CLI/agent)
- `[[wiki-links]]` connect to other knowledge records
- Additional frontmatter fields are convention-based per tag (decisions have `rationale`, session summaries have `accomplished`)
- No schema enforcement on knowledge — the frontmatter is flexible

### Awareness Records

Some records point to artifacts that live in external systems (code repos, content system, deployed services). These have two additional fields:

| Field | Purpose |
|-------|---------|
| `system:` | Which system owns the external artifact (content, dispatch, github, linear) |
| `ref:` | Pointer to where the actual artifact lives (file path, URL, commit hash) |

Any record can be an awareness record by having `system:` and `ref:` fields. Synced entities always have these. Knowledge records can optionally have them to point to external artifacts.

### Record Identity

- **Entity records:** descriptive slug (e.g., `craig`, `indemn`, `voice-agent`, `voice-scoring-ui`)
- **Knowledge records:** `YYYY-MM-DD-descriptive-slug` (e.g., `2026-03-08-hive-vision`)
- **Synced records:** `source-external-id` (e.g., `AI-123`, `PR-456`)
- Collisions on the same day: append `-2`, `-3`
- Claude Code generates slugs from content

### Typed References (Entity Layer)

Entities reference other entities via typed `ref` fields. These are first-class relationships, not generic links:

```json
// In a meeting entity (MongoDB)
{
  "type": "meeting",
  "attendees": ["craig", "cam"],    // → person entities
  "company": "indemn"               // → company entity
}
```

```json
// In a workflow entity (MongoDB)
{
  "type": "workflow",
  "project": "platform-dev",        // → project entity
  "refs_out": {
    "people": ["craig"],
    "product": ["voice-agent"]
  }
}
```

**Relationships are navigable in both directions.** If a meeting references Craig as an attendee, querying Craig's profile shows all his meetings. MongoDB indexes handle reverse lookups.

### Links (Knowledge Layer)

Knowledge records reference entities via `refs:` in frontmatter and connect to other knowledge via wiki-links:

```markdown
---
refs:
  project: hive
  people: [craig]
---
This builds on [[2026-02-19-dispatch-system-design]] and addresses
the scoring gap from [[meeting-2026-03-01-oconnor-voice]].
```

**Three kinds of connections (all automatic):**
1. **Typed references** — knowledge refs entities (frontmatter `refs:` field)
2. **Wiki-links** — knowledge links to knowledge (inline `[[...]]`)
3. **Semantic links** — content similarity discovered via embeddings

The graph grows as a byproduct of working. Manual linking is rarely needed.

### The Workflow Entity

Long-running work (building a feature, writing a series of blog posts, onboarding a customer) spans multiple Claude Code sessions. Each session needs to know where the work stands. Previously, INDEX.md served this role — manually maintained, frequently stale.

A `workflow` is a typed entity in MongoDB:

- `objective` — what the workflow is trying to accomplish
- `status` — active, paused, completed
- `current_context` — a summary of where things stand, updated at the end of each session
- `sessions` — ordered list of session IDs that have worked on this workflow
- `project` — typed ref to the parent project entity
- `artifacts` — list of knowledge record IDs created during the workflow

**This is INDEX.md as a typed entity that updates itself.** At session end, `current_context` gets updated with what was accomplished and what's next. The next session reads one record to know the full state.

**Systems own workflow lifecycle, not the Hive.** The content system creates a workflow when a content piece begins and updates it as the pipeline progresses. The code dev system creates one when a feature begins and updates as sessions complete. The Hive stores the record; the context assembly agent reads it; but the system's CLI creates and updates it.

---

## The Registry

The registry is the Hive's self-knowledge — it defines what entity types exist, what tags mean, and what domains are valid. Every Claude Code session reads the registry before creating or querying records.

### Registry Structure

```
hive/.registry/
  ontology.yaml          # Tags, domains, statuses, priorities
  types/                 # Entity type schemas ONLY (one YAML per type)
    person.yaml
    company.yaml
    product.yaml
    project.yaml
    workflow.yaml
    meeting.yaml
    brand.yaml
    platform.yaml
    channel.yaml
    # Sync adapters add their own:
    linear_issue.yaml
    calendar_event.yaml
    email_thread.yaml
    slack_message.yaml
    github_pr.yaml
```

**Note:** Knowledge records (decisions, designs, research, session summaries, notes) do NOT have type definitions. They are markdown files differentiated by tags defined in `ontology.yaml`.

### Type Definitions

Each entity type file defines the schema and relationships. See "Layer 1: Entities" section above for examples. Key fields:

| Field | Purpose |
|-------|---------|
| `type` | The type name (used in CLI: `hive create <type>`) |
| `fields` | Schema — field names, types, required/optional, ref targets |
| `display` | Which field is shown as the label (name, title, subject) |

### Ontology (Tags, Domains, Statuses)

Tags provide subcategorization within types. A `note` can be tagged `brainstorming`, `architecture`, `ui`. Tags are lighter than types — they don't define schemas, just categories.

```yaml
# hive/.registry/ontology.yaml

tags:
  # Subcategories for knowledge types
  brainstorming: { description: "Brainstorming output", category: creative }
  architecture: { description: "System architecture discussion", category: technical }
  ui: { description: "User interface design", category: technical }
  voice: { description: "Voice/audio related", category: domain }
  scoring: { description: "Scoring/evaluation related", category: domain }
  # Subcategories for content
  blog: { description: "Blog post content", category: format }
  newsletter: { description: "Newsletter content", category: format }
  video: { description: "Video content", category: format }
  linkedin: { description: "LinkedIn content", category: platform }
  # ... (grows with use)

domains:
  indemn:
    description: "Indemn — AI agent platform for insurance"
  career-catalyst:
    description: "Career Catalyst — side business and personal brand"
  personal:
    description: "Personal projects and life management"

statuses:
  - backlog
  - ideating
  - active
  - in-review
  - done
  - archived

priorities:
  - low
  - medium
  - high
  - critical
```

### Registry Evolution

- **New entity types:** Added as YAML files in `.registry/types/`. The CLI auto-discovers them. Sync adapters add their own types when they integrate. Only create an entity type when the context assembly agent needs structured queries as a starting point.
- **New tags:** Added deliberately to `ontology.yaml`. When a session needs a tag that doesn't exist, check if an existing tag covers the concept. If not, add it and mention it in the session summary. **Entity types and knowledge tags must be disjoint sets** — if `meeting` is an entity type, it cannot also be a knowledge tag. This eliminates routing ambiguity in the unified CLI.
- **New domains:** Added to `ontology.yaml` when Craig starts working in a new domain.
- **Principle:** Entity types are for structured records that need to be found by name, structured query, or relationship traversal as a starting point for context assembly. Tags subcategorize knowledge records. Don't create an entity type when a tagged knowledge record would suffice.

---

## Storage Architecture

### Vault (Knowledge Files)

The vault contains **knowledge records only** (markdown files). Entities live in MongoDB, not the filesystem.

```
hive/
  .registry/
    ontology.yaml                    # Tags, domains, statuses, priorities
    types/                           # Entity type schemas ONLY
      person.yaml
      company.yaml
      product.yaml
      project.yaml
      workflow.yaml
      meeting.yaml
      brand.yaml
      platform.yaml
      channel.yaml
      # Sync adapters add their own:
      linear_issue.yaml
      calendar_event.yaml
      email_thread.yaml
      slack_message.yaml
      github_pr.yaml
  .templates/                        # Example notes for common patterns
  .attachments/                      # Binary files (images, PDFs)

  # Knowledge directories (markdown files, git-tracked)
  notes/                             # Quick thoughts, observations, ideas
    2026-03-08-hive-vision.md
    2026-03-09-tile-breathing-idea.md
  decisions/                         # Notes tagged "decision" — has rationale
    2026-03-09-wall-user-driven.md
    2026-03-14-entities-mongodb-only.md
  designs/                           # Notes tagged "design" — specs, architecture
    2026-03-08-hive-design.md
  research/                          # Notes tagged "research" — external findings
    2026-03-04-gastown-findings.md
  sessions/                          # Notes tagged "session_summary"
    2026-03-08-os-hive-session-1.md

  # Synced record cache (gitignored, rebuilt via hive sync)
  .synced/
    linear/
    calendar/
    email/
    slack/
    github/
```

**Key properties:**
- **No entity directories** (people/, companies/, etc.) — entities are MongoDB-only
- **Knowledge directories organized by convention** (tag-based), not enforced type schemas
- `.registry/types/` only contains entity type definitions
- All knowledge records follow the same format: markdown with YAML frontmatter
- `hive/` lives in the operating-system repo, version-controlled by Git
- `.synced/` is gitignored — external system is source of truth, rebuilt via `hive sync`

### MongoDB

**Instance:** Local MongoDB Community Edition (via Homebrew). Private, zero cost, fast.

**Database:** `hive`

**Collection:** `records` (single collection with type discriminator — simpler than per-type collections, MongoDB handles polymorphic queries well)

#### Entity Documents (Source of Truth)

Entities live ONLY in MongoDB. No file representation.

```json
{
  "_id": ObjectId,
  "record_id": "craig",
  "type": "person",
  "name": "Craig",
  "email": "craig@indemn.ai",
  "role": "Technical Partner",
  "company": "indemn",
  "domains": ["indemn", "career-catalyst"],
  "tags": ["engineering", "leadership"],
  "status": "active",
  "refs_out": {
    "company": ["indemn"],
    "project": ["hive", "platform-dev"]
  },
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### Knowledge Documents (Derived from Files)

Knowledge records are indexed from markdown files into MongoDB for search.

```json
{
  "_id": ObjectId,
  "record_id": "2026-03-14-entities-mongodb-only",
  "type": "knowledge",
  "title": "Use two-layer architecture instead of 14+ types",
  "tags": ["decision", "architecture"],
  "domains": ["indemn"],
  "status": "active",
  "refs_out": {
    "project": ["hive"],
    "people": ["craig"]
  },
  "wiki_links": ["2026-03-08-hive-vision", "2026-03-09-context-assembly-gaps"],
  "content": "Full markdown content without frontmatter...",
  "content_embedding": [/* vector from local embedding model */],
  "file_path": "hive/decisions/2026-03-14-entities-mongodb-only.md",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### Workflow Documents (Entity — Source of Truth in MongoDB)

```json
{
  "_id": ObjectId,
  "record_id": "voice-scoring-ui",
  "type": "workflow",
  "name": "Voice Scoring UI",
  "objective": "Build the scoring UI component for voice evaluations",
  "status": "active",
  "current_context": "Session 3 completed React component. Remaining: API wiring, tests. O'Connor demo Friday.",
  "sessions": ["session-uuid-1", "session-uuid-2", "session-uuid-3"],
  "refs_out": {
    "project": ["platform-dev"],
    "people": ["craig"],
    "product": ["voice-agent"]
  },
  "artifacts": ["2026-03-10-scoring-spec", "2026-03-12-scoring-decisions"],
  "created_at": ISODate,
  "updated_at": ISODate
}
```

**Indexes:**
- `record_id`: unique
- `type`: regular (enables type-scoped queries)
- `tags`: multikey
- `domains`: multikey
- `status`: regular
- `refs_out.company`: multikey (reverse lookup — "all records referencing Indemn")
- `refs_out.project`: multikey
- `refs_out.people`: multikey (reverse lookup — "all records referencing Craig")
- `content_embedding`: regular array (cosine similarity in Python)
- Full-text index on `title` + `content`
- Compound: `{type: 1, status: 1}`, `{type: 1, domains: 1}`

**Supported queries:**
- **Type-scoped:** `{type: "person", domains: "indemn"}` — all Indemn people
- **Relationship traversal:** `{"refs_out.company": "indemn"}` — everything connected to Indemn
- **Reverse lookup:** `{"refs_out.people": "craig"}` — all Craig's meetings, workflows, projects
- **Semantic:** vector similarity on `content_embedding` (knowledge records only)
- **Tag-filtered:** `{type: "knowledge", tags: "decision", domains: "indemn"}` — active Indemn decisions
- **Keyword:** full-text search on `title` + `content`
- **Timeline:** `{type: "meeting", created_at: {$gte: last_week}}`
- **Cross-type:** `$graphLookup` for multi-hop traversal across entity types

**Note:** Atlas Vector Search is cloud-only. For local MongoDB, embeddings are stored as arrays and cosine similarity is computed in Python. At the scale of hundreds to low thousands of records, this is fast enough. If it becomes a bottleneck, add a dedicated vector store (ChromaDB, LanceDB) later.

### Embedding Model

- **Initial:** Local model via Ollama (e.g., `nomic-embed-text` or `mxbai-embed-large`)
- **Abstracted:** Behind a simple interface so the model is swappable
- Only knowledge records get embeddings — entity records are queried via structured fields
- Each knowledge record is embedded when created or updated during sync
- Re-embedding is possible when switching models (`hive sync --re-embed`)

---

## Context Assembly

The core value proposition. How a Claude Code session goes from "I want to work on X" to having full context without manual curation.

### The Core Reframe: Context Assembly Is a Task, Not an Algorithm

Context assembly is an **LLM agent that uses the Hive CLI as its toolkit.** It's not a fixed pipeline — it's a task that an LLM performs, choosing different retrieval strategies based on the user's stated intent.

**Why this is better than a fixed algorithm:**
- "I want to build the scoring UI" → the agent decides to pull product entities, check Linear issues, find recent sessions on this topic, look at code decisions
- "I want to write a blog about voice agents" → the agent decides to pull meeting notes with customer quotes, find existing content drafts, check the brand entity for voice guidelines
- "What's the status of everything?" → the agent pulls all active workflows, recent session summaries, pending Linear issues

Same Hive, completely different retrieval strategies. A fixed embed-score-rank algorithm can't do this. An LLM reading intent and choosing tools can.

**This aligns with the OS philosophy:** Claude Code is expert at using CLIs. The Hive CLI provides rich, type-aware query capabilities. The context assembly agent is just another Claude Code session using a CLI — the pattern the entire OS is built on.

### Dedicated Context Assembly Session

Context assembly runs as a **separate, short-lived Claude Code session** — not the working session itself.

**Why a separate step:**
- Runs in its own context window, then discards it
- Can be aggressive with queries (pull a lot, filter down, synthesize)
- Produces a comprehensive context note efficient for the working session
- The working session starts with context already assembled — zero retrieval overhead

**Implementation mechanism:** The context assembly session is created via the existing session CLI (`session create`). Not Agent SDK, not direct API. It uses the same infrastructure that manages all OS sessions — tmux, worktrees, hooks. The Hive UI spawns it, it writes a context note, then the working session gets created with that context.

### Two Sources, Not Five

The Hive's sync framework pulls data from Linear, Slack, Calendar, GitHub, Email into the Hive as synced records. This means the context assembly agent does NOT need to query five different external tools. If Linear data is stale, that's a sync frequency problem, not a context assembly problem.

**The agent has exactly two sources:**

1. **The Hive** — entities, knowledge, relationships, workflow state, AND all synced external data (Linear issues, Slack messages, calendar events, GitHub PRs). One system that has everything about Craig's world.

2. **The codebase** — when the task involves code. Code is too large, too dynamic, and too detailed to sync into the Hive. The agent needs to actually read files and grep. The Hive might know "session 3 implemented the React component" but it doesn't know the current state of `src/components/scoring/`.

**Not the agent's job:** Web search, documentation lookup, API references. Those are the working session's concern during actual work. Context assembly gives you YOUR context — your knowledge, your entities, your codebase state.

### How the Agent Knows Which Codebase

No explicit `repo` field on project entities. Instead:

- **Existing workflows carry it naturally.** Session summaries and decisions mention repos and file paths as a byproduct of working. The agent reads recent session summaries for the workflow and extracts repo information.
- **For brand new workflows** (no history yet), the agent reads the OS `CLAUDE.md` which has the full service inventory with repo paths.
- **The OS already manages repo access** — sessions are created with `--add-dir` for external repos. The context assembly agent's output can specify which repos the working session needs.

### System-Specific Context Playbooks

The context note format is NOT a generic Hive-level template. Each system defines what context matters for its workflow via a dedicated section in the system's skill.

**The pattern:**
- The Hive provides the infrastructure (CLI commands, entity/knowledge layers, search)
- Each system's skill describes what context to gather and how to structure it
- The context assembly session is generic — it reads the system's instructions and follows them
- New systems define their own context needs; the context assembly session adapts automatically

### Comprehensive, Not Compressed

The context note should be thorough. More context is better. A 20k-token comprehensive briefing is a fraction of the context window and leaves plenty of room for actual work. The context assembly session naturally produces coherent, non-redundant output. No explicit budgeting mechanism needed.

The context note should:
- Include full decision text with rationale (not one-line summaries)
- Include full entity profiles for relevant people and companies
- Reference Hive record IDs throughout so the session can `hive get` for deeper exploration
- Explicitly prompt the working session to do its own due diligence — verify codebase state, read files, explore before acting

### Context Assembly Agent Workflow (Concrete Scenario)

Scenario: "I want to build the scoring UI for voice evaluations"

```bash
# Step 1: Find the workflow (deterministic lookup)
hive get voice-scoring-ui --format json
# → workflow entity with current_context, objective, sessions, artifacts

# Step 2: Find all records connected to this workflow
hive refs voice-scoring-ui --format json
# → project:platform-dev, product:voice-agent, people:craig
# → also: knowledge records that ref this workflow

# Step 3: Expand from the product entity
hive refs voice-agent --format json --tags decision,design,session_summary
# → all decisions, designs, session summaries about the voice product

# Step 4: Semantic search for anything the graph missed
hive search "scoring UI voice evaluations" --recent 30d --format json
# → semantically similar knowledge from last 30 days

# Step 5: Recent activity for temporal awareness
hive recent 7d --format json
# → anything created/modified in last 7 days

# Step 6: Specific person context (O'Connor mentioned in intent)
hive get oconnor --format json
hive refs oconnor --recent 30d --format json
# → O'Connor entity + recent knowledge mentioning them
```

Six commands covering structured traversal + semantic discovery + temporal awareness. Steps 2-4 can be parallelized. The agent writes the assembled context as a knowledge note:

```bash
hive create note "Context: Voice Scoring UI — Session 5" \
  --tags context_assembly \
  --refs workflow:voice-scoring-ui,project:platform-dev \
  --domains indemn
```

### Context During Work

Beyond startup, working sessions can query the Hive on-demand:

```bash
hive get craig                                      # Any record by ID
hive refs craig --tags meeting --recent 30d         # Craig's recent meetings
hive search "deployment patterns" --domains indemn  # Semantic search
hive list person --domains indemn                   # All Indemn people
hive recent 7d                                      # Recent activity feed
hive create note "interesting tile pattern" --tags ui --domains indemn
```

### Skill and System Awareness

Skills and systems are themselves represented as records in the Hive (entity type or knowledge type — to be determined during implementation). Context assembly can then connect: "voice scoring task → references Linear issue AI-123 → the `/linear` skill is relevant" via typed relationships and surface it in the context note.

---

## System Integration Model

### The Convention

Systems keep their own internal architectures. The Hive is additive — awareness and connections.

**When building a new system:**
1. Keep your domain-specific files, configs, and folder structure
2. Create awareness records in the Hive when significant events occur (created, started, completed, published, failed)
3. Register your domain-specific tags in `ontology.yaml`
4. Build Hive operations into your system CLI — don't make Claude Code use raw `hive create note`
5. Document the Hive integration in your system's skill

**The clear line:** If it's knowledge, a decision, or a connection → native Hive note. If it's a domain-specific artifact managed by a system → it lives in the system, with a Hive awareness record pointing to it.

### Example: Content System Integration

The content system keeps: brand folders, draft files, config.yaml, voice.md, publishing pipeline.

When the content system creates a draft:
```bash
content draft create --from 2026-03-07-devops-story-idea
```

Internally, this:
1. Creates the draft file in `content-system/brands/personal/drafts/devops-transformation.md`
2. Creates a Hive awareness record:
   ```yaml
   tags: [draft, blog]
   domains: [career-catalyst]
   system: content
   status: drafting
   ref: content-system/brands/personal/drafts/devops-transformation.md
   links: [2026-03-07-devops-story-idea]
   ```

### Example: Dispatch Integration

When dispatch completes a task:
1. Task is done in the target repo (code committed, tests passing)
2. Dispatch creates a Hive awareness record:
   ```yaml
   tags: [task, completed]
   domains: [indemn]
   system: dispatch
   status: done
   ref: indemn-platform-v2 (commit abc123)
   links: [2026-03-08-voice-scoring-plan]
   ```

### Skill Integration Convention

Every skill that produces knowledge, decisions, or outputs should integrate with the Hive:

**For new skills:**
- Read `hive/.registry/` for available types, tags, domains
- Create typed records via `hive create <type>` for knowledge and entities
- Use `hive context <topic>` for background knowledge
- If you need a new type, add a YAML definition to `.registry/types/`
- If you need a new tag, register it in `ontology.yaml`
- Document your Hive integration in the skill's SKILL.md

**For existing skills becoming Hive-aware:**
- Add `hive context` at the start if the skill needs background knowledge
- Add `hive create` at key output points (decisions, specs, session summaries)
- The Hive is additive — don't replace the skill's core logic

**The Hive skill (`/hive`) handles:**
- Typed record CRUD, search, context assembly, sync, registry management
- Other skills call the `hive` CLI, not MongoDB or vault files directly

---

## The Hive CLI

Python CLI (Click or Typer). Same pattern as `bd` for beads. **Unified commands** — the entity/knowledge distinction is hidden from the user. The CLI routes transparently based on whether the argument is a registered entity type or a knowledge tag.

### Design Principles

- **Verb-first grammar.** `hive get`, `hive create`, `hive search` — reads naturally for both LLMs and voice. Not `hive person get`.
- **Transparent routing.** If the argument is a registered entity type → entity layer (MongoDB). If it's a known tag → knowledge layer (markdown files). Layer indicators in output: `[entity:person]` or `[knowledge:decision]`.
- **Auto-detect output format.** JSON when piped (no tty), text when interactive (tty detected). Follows the `gh` CLI pattern. The context assembly agent pipes output → gets JSON automatically.
- **Disjoint entity types and knowledge tags.** If `meeting` is an entity type, it cannot also be a tag. The ontology enforces this, eliminating routing ambiguity.

### Commands (14 Total)

```
hive context <query>                     # THE main command — context assembly
    --objective "..."                    # What the session is trying to accomplish
    --domain <domain>                    # Scope to domain
    --depth <1-3>                        # Graph traversal depth (default: 2)
    --budget <tokens>                    # Max context budget (default: 8000)
    --format json|md                     # Output format (default: md)

hive get <id>                            # Get any record by ID
    --fields field1,field2               # Select specific fields
    --format json|text|md                # Output format
    Routing: queries both layers, entity first, returns first match

hive create <type-or-tag> "title"        # Create a record
    --refs key:value,...                  # Entity references
    --tags tag1,tag2                     # Additional tags (knowledge only)
    --domains dom1,dom2                  # Domain classification
    --status <status>                    # Initial status
    --<field> <value>                    # Type-specific fields or frontmatter
    Routing: if type-or-tag is in .registry/types/ → entity (MongoDB)
             if type-or-tag is a known tag → knowledge (markdown file + index)
    Returns: record_id and file_path (if knowledge)

hive update <id>                         # Update any record
    --<field> <value>                    # Fields to update
    --add-tags tag1,tag2                 # Add tags without replacing
    --add-refs key:value                 # Add refs without replacing
    Routing: resolves layer from ID, updates accordingly
    For knowledge: updates frontmatter in file, re-indexes to MongoDB

hive search "query"                      # Semantic + keyword search
    --tags tag1,tag2                     # Filter by tags
    --domains dom1,dom2                  # Filter by domain
    --types type1,type2                  # Filter by entity type
    --recent <duration>                  # Time filter (7d, 30d, 3m)
    --limit <n>                          # Max results (default: 20)
    --knowledge-only                     # Skip entities
    --entities-only                      # Skip knowledge
    --format json|text|md                # Output format
    Routing: searches both layers, merges by relevance

hive list <type-or-tag>                  # List records of a type or tag
    --status <status>                    # Filter by status
    --domain <domain>                    # Filter by domain
    --recent <duration>                  # Time filter
    --refs-to <id>                       # Filter by reference to entity
    --limit <n>                          # Max results (default: 50)
    --format json|text|md                # Output format
    Routing: entity type → MongoDB query, known tag → knowledge query

hive refs <id>                           # Everything referencing this record
    --types type1,type2                  # Filter by type
    --tags tag1,tag2                     # Filter by tag
    --direction in|out|both              # Ref direction (default: both)
    --depth <1-3>                        # Traversal depth (default: 1)
    --recent <duration>                  # Time filter
    --format json|text|md                # Output format

hive recent [duration]                   # Recent activity feed (default: 7d)
    --types type1,type2                  # Filter by type
    --domains dom1,dom2                  # Filter by domain
    --limit <n>                          # Max results (default: 20)
    --format json|text|md                # Output format
    Returns: reverse-chronological mixed-type feed across both layers

hive sync [system]                       # Sync operations
    hive sync                            # Re-index all knowledge files to MongoDB
    hive sync linear                     # Pull from Linear
    hive sync calendar                   # Pull from Google Calendar
    hive sync --re-embed                 # Re-generate all embeddings

hive status                              # System overview
    Record counts by type/domain/status, recent activity, MongoDB + embedding status

hive init                                # Initialize vault, MongoDB, seed registry

hive types list                          # List registered entity types
hive types show <type>                   # Show type schema
hive tags list                           # List registered tags
hive domains list                        # List registered domains
```

### Routing Rules

| Input | Resolution |
|-------|-----------|
| `hive create person "Craig"` | `person` is in `.registry/types/` → entity → MongoDB |
| `hive create decision "Use X"` | `decision` is not a type, is a known tag → knowledge → markdown file + index |
| `hive create note "Quick thought"` | `note` is always knowledge (the default tag). There is no `note` entity type. |
| `hive list person` | `person` is a type → entity list from MongoDB |
| `hive list decision` | `decision` is a tag → knowledge list filtered by tag |
| `hive get craig` | Queries both layers by record_id, entity first. Returns first match with layer indicator. |
| `hive get 2026-03-14-scoring-spec` | Date-prefixed → likely knowledge. Queries both, returns match. |

### Commands Deliberately Excluded

- **`hive workflow get/update/complete`** — Covered by generic `hive get`, `hive update`, `hive update --status completed`. Workflow patterns documented in the skill, not special-cased in the CLI.
- **`hive feedback`** — It's `hive create note "..." --tags feedback`. No separate command.
- **`hive tags add` / `hive domains add`** — Edit `ontology.yaml` directly. Infrequent operations that don't need CLI commands.

### CLI Architecture

```
hive/                         # CLI package
  cli.py                      # Click/Typer CLI entry point
  records.py                  # Two-layer record CRUD (entity→MongoDB, knowledge→files+index)
  types.py                    # Type registry — loads entity type definitions from .registry/types/
  context.py                  # Context assembly coordination
  search.py                   # Search (semantic + structured) across both layers
  sync.py                     # Knowledge file → MongoDB sync + external system sync adapters
  registry.py                 # Registry management (types, tags, domains)
  embed.py                    # Embedding abstraction
  db.py                       # MongoDB connection
  config.py                   # Configuration (vault path, MongoDB URI, model)
```

---

## The Hive UI

Designed in session 2026-03-09-a. The Hive is the home screen of the operating system — the front door, not a panel within the OS Terminal. You open the Hive, see your world, and work from there.

### Layout: Wall + Focus Area

**The Wall** surrounds the **Focus Area**. The Focus Area is always centered. The Wall is the peripheral awareness layer — tiles representing everything in your world. The Focus Area is where active work happens — terminal panels and browser panels.

**The Wall breathes.** When less is in the Focus Area, the Wall expands and tiles grow, showing more information. When the Focus Area has multiple active panels, the Wall compresses and tiles shrink. Information density scales fluidly with available space. The more you have going on, the more you need to focus; the less you have going on, the more you're open to seeing what's happening.

**Toggle to full Overview.** Even when sessions are running, you can toggle the Wall to full-screen to see the big picture. The Focus Area minimizes. Toggle back and your sessions are still running.

**Responsive.** On an ultra-wide monitor, the Wall and Focus Area coexist comfortably. On smaller screens, the Wall collapses to a slide-out or tab bar.

### Interaction Model

**Voice-first.** Craig interacts primarily through voice via Wispr Flow (speech-to-text that pastes into the active input). The Hive must work well with voice — quick capture, responding to sessions, taking notes. All through talking into the computer.

**Parallel work is the norm.** Multiple sessions running simultaneously. While one session works on code, Craig switches to another for content, or reviews something in a browser panel. The Wall provides awareness of everything in motion while Focus panels show active work.

**Almost everything involves a Claude Code session.** Whether it's writing code, creating content, drafting an email, brainstorming, or preparing for a meeting — the primary interaction is through Claude Code sessions. The Hive surfaces what to work on; sessions do the work.

**The Hive is the surface for everything:** email (read/reply via browser panel + Claude assistance), social media (post to X, LinkedIn, Substack via browser panels or system APIs), news (read articles, repost/restack), meetings (notes captured through the Hive, prep run via call-prep sessions), calendar (see what's upcoming), code development, content creation, brainstorming, note-taking. The goal is to never leave the Hive.

### Tiles: Everything Is a Tile

Every tile on the Wall is a Hive note. Everything is a note. Everything is a tile. **Tiles are the only UI elements.** No buttons, no menus, no chrome, no toolbars. The tiles are the interface. The data is the UI.

**All types mixed on one surface.** Tiles are NOT grouped by type or system. A task tile sits next to a session tile sits next to a content draft sits next to a calendar event. Organization is by relevance and status, not by category. This matches how the brain works — you don't think in categories, you think in priorities and connections.

**Completed work stays visible.** Done items don't disappear — they fade (lower brightness) but remain on the Wall. Completed work is context for what's next AND source material for future work (the flywheel). A completed feature is a potential blog post. A published blog is a potential tweet thread. Everything builds on everything.

- **Domain filtering:** Click a domain tile to filter the Wall. This IS the fractal zoom — not a spatial zoom, just filtering. Show only Indemn, or only Career Catalyst, or everything.
- **Search:** A search tile opens a search input.
- **Quick capture:** A capture tile opens an input for fast note creation.
- **Navigation:** Tiles themselves handle all interaction.

**User-driven arrangement with smart defaults.** The Wall is your priority surface — you control what's important. No weighted scoring formula, no LLM call at render time. The intelligence is in the metadata on each note (set by LLMs when notes are created) and your explicit choices.

**Wall ordering:**
1. **User-set priority** as the primary axis — critical, high, medium, low. You set these.
2. **Status** as secondary — active items above backlog, done items faded to the edges.
3. **Recency** as tiebreaker within the same priority and status.
4. **Drag-to-reorder** for fine-tuning — manual ordering is preserved within priority buckets.

**Future: morning consultation.** A session type (not a special feature) where you start a "daily planning" session. It pulls your calendar, active tasks, priorities, what's in flight, and you have a conversation about the day. The output is updated priorities on existing notes. Fits the existing session model — just a well-designed session with the right context retrieval.

### Tile Visual Design

**Fluid sizing.** Tiles are not three fixed sizes. They show as much information as fits their current rendered space. Title is always visible. Status and color are always present. As a tile gets more space: context line appears, then tags, then timestamps, then summaries. The transition is continuous, not stepped.

**Fewer tiles at useful size, not more tiles at useless size.** When the Wall is compressed, it shows a smart highlight reel — active items, things needing attention, upcoming events. The full inventory is available in Overview mode. This keeps the compressed state scannable.

**Visual encoding — three axes:**

| Axis | Maps to | Purpose |
|------|---------|---------|
| **Color** | Type (person, meeting, decision, linear_issue, calendar_event, etc.) | "What kind of thing is this?" |
| **Accent/border** | Domain (Indemn, Career Catalyst, Personal) | "Which world does it belong to?" |
| **Brightness/opacity** | Status (vivid=active, normal=to-do, muted=backlog, faded=done) | "What's its energy level?" |

Color comes from the record's type. Each type gets a color defined in the registry or via a consistent hash. This replaces the previous "system" color mapping — types are more specific and meaningful than system names.

**Rectangular tiles for MVP.** Honeycomb/hexagonal tiles are visually aligned with the hive metaphor but significantly harder to implement (CSS grid/flexbox are rectangle-native). Start with rounded rectangular tiles, dense packing, minimal gaps, organic feel. Honeycomb is a future CSS-level evolution if warranted.

### Tile Data Mapping

Every visual element on a tile maps to a record field:

```
Record field            →  Tile visual
──────────────────────────────────────────────
title/name/display      →  Tile label (uses type's `display` field)
type                    →  Primary color + type icon
domains[]               →  Accent/border color
status                  →  Brightness/opacity
system                  →  Primary color
priority                →  Visual weight / badge
ref                     →  Awareness record indicator
external_refs           →  Reference badges (AI-123, PR #456)
updated_at              →  Timestamp ("2h ago")
links[]                 →  Connection count (in larger tiles)
content (first ~50 chars) → Context line (when space permits)
```

### Focus Area

The center of the screen. Where active work happens.

**Panel types:**
- **Terminal panels** — xterm.js, same as current OS Terminal. Claude Code sessions. The majority of interactions.
- **Browser panels** — iframe/webview for web content. Covers: reading articles, Gmail interface, social media (X, LinkedIn, Substack), custom system dashboards, any website interaction. If a system needs a custom UI beyond terminal or standard web (e.g., a content pipeline dashboard, analytics view), it hosts itself as a small web app and the Hive loads it in a browser panel — same pattern as the OS Terminal being a React app at localhost:3101.

**Equal-sized auto-grid.** Same behavior as the current OS Terminal — panels fill available space equally. No custom sizing for now.

**These two panel types cover ~90% of daily workflow.** Terminal for anything involving Claude Code (most work). Browser for anything involving web interfaces. The remaining 10% (complex app-specific interactions) happens in a regular browser outside the Hive.

**Opening and closing.** Click a tile on the Wall → opens in Focus Area via appropriate interface. Close a panel → it returns to being a tile on the Wall. The Focus Area auto-arranges as panels are added/removed.

### Quick Capture

Always-visible capture tile on the Wall. Click it, talk via Wispr Flow, done. The Hive processes it asynchronously:
- LLM determines appropriate tags and domain from the content
- May ask a follow-up question if ambiguous (appears as a notification on the capture tile)
- New note appears as a tile on the Wall, already organized

Similar to the content extraction pipeline's interview approach, but lightweight — quick categorization, not deep extraction.

### Create Linked Note

**First-class interaction.** When you're looking at a tile and want to capture a thought about it — one click, a new note opens already linked to the parent. Talk your thoughts via Wispr Flow. Done.

The new note:
- Inherits domain from parent
- Gets auto-tagged based on content
- Is linked bidirectionally to the parent note
- Appears as its own tile on the Wall

This is the primary mechanism for the flywheel (see below). Thoughts accumulate on top of existing work and become source material for future work in any system.

### Two Data Sources

| Tile type | Source | Update frequency |
|-----------|--------|-----------------|
| Active sessions | `sessions/*.json` (existing session manager infrastructure) | Real-time (hooks) |
| Everything else | Hive API (MongoDB) | ~30s polling + on-action refresh |

The UI merges both into one unified Wall. Active sessions get tile data from session state files. Hive notes get tile data from the Hive API. Both render with the same visual language. The user doesn't know or care which backend a tile comes from.

**Completed sessions** get a Hive awareness record at session close (created by the `session close` command). This puts the session's knowledge into the graph for future context assembly. Active session state stays in `sessions/*.json` where it belongs — real-time operational data doesn't belong in a knowledge graph.

### Technical Architecture

**Evolve the existing OS Terminal React app.** The Hive UI is not a new application — it's the OS Terminal grown up.

What exists (keep):
- React + Vite frontend
- xterm.js terminal rendering
- WebSocket relay to tmux (node-pty)
- Session state file watching
- Express backend

What changes:
- Layout evolves from "grid of terminals" to "Wall + Focus Area"
- New tile component alongside terminal panels
- Browser panel component (iframe)
- Quick capture component

What's new:
- **Hive API routes** — Express routes wrapping Hive CLI (`hive notes`, `hive search`, etc.) with JSON output
- **WebSocket Hive updates** — push note changes to the frontend (~30s polling or on-action)
- **UI reads from ONE source: the Hive.** All system data (content, code, calendar, email, Linear) syncs into the Hive backend. The UI doesn't call Linear API or Google Calendar. It reads Hive notes. That's the whole point of the Hive being connective tissue.

---

## Session Initialization ("The Doctor Appointment")

How a session gets started from the Hive with the right context. The "doctor appointment" metaphor: the nurse (context assembly session) does intake before the doctor (working session) sees you. You don't walk in and explain everything from scratch.

### From a Tile (Existing Work)

1. **Craig clicks a tile on the Wall.** The tile has metadata: record ID, tags, domain, system.
2. **The Hive UI shows a lightweight prompt:** "What are you trying to accomplish?" Craig speaks via Wispr Flow.
3. **The Hive UI spawns a context assembly session** via the session CLI (`session create`). First message includes: tile metadata + Craig's stated objective.
4. **The context assembly session reads the relevant system's context playbook** (from the system's skill). It queries the Hive and codebase following those instructions.
5. **The context assembly session writes a comprehensive context note** linked to the workflow, then terminates.
6. **The Hive UI spawns the working session** via the session CLI. First message via `tmux send-keys` includes the context note content. The session knows the objective, the system, and has full context. No "what are you trying to accomplish?" — it already knows.
7. **Work begins immediately.** The working session is prompted to do its own due diligence (verify codebase state, explore further as needed).

### From Scratch (New Work)

1. Craig uses quick capture or tells the Hive "I want to build a new pricing engine."
2. The Hive UI prompts for objective (or the statement IS the objective).
3. Context assembly session runs — finds no existing workflow, searches for related entities and knowledge, checks CLAUDE.md for repo context.
4. The system that owns this type of work (code development, content, research) creates the workflow entity as part of its initialization.
5. Context note written, working session spawned with context.

### Why Objective Comes First

Context retrieval needs context to be relevant. Without knowing the objective, you get everything about a topic — noisy. The objective determines what's relevant:

- "Brainstorm the architecture" → design docs, decisions, related patterns, constraints
- "Implement the component" → specs, code patterns, repo structure, PRs
- "Write a blog about it" → linked notes with commentary, user-facing impact, decisions

Same topic, different objectives, completely different context.

### The System Field Determines the Playbook

The tile's `system:` field (or Craig's stated intent for new work) tells the context assembly session which system's workflow it's assembling context for. `system: content` means follow the content system's context instructions. `system: code-development` means follow the code dev system's instructions. Each system's skill defines what to gather and how to structure the context note.

---

## The Flywheel

How work in one system becomes source material for other systems. The flywheel is not a hard-coded pipeline between specific systems — it's emergent from notes and links.

### Core Mechanism: Linked Notes

The primary interaction that drives the flywheel is **creating linked notes off existing work.** As you work, thoughts occur. You capture them as linked notes — commentary, insights, trade-offs, ideas for other things. These accumulate organically.

When any system needs context later — content system needs source material for a blog, a session needs background on a feature, meeting prep needs context on a topic — the Hive has it because you've been capturing thoughts all along.

### Example: Development → Content

1. You build a voice scoring feature over several sessions.
2. As you work, you create linked notes: "The weighted rubric approach was the right call because...", "O'Connor specifically asked for this visibility...", "This pattern could apply to Career Catalyst scoring too..."
3. Weeks later, you want to write a newsletter about it.
4. You open the content system. Context assembly finds the feature's awareness records AND all your linked notes with commentary.
5. The content extraction interview is already half-done — the material is in the Hive.
6. The published blog post becomes its own note, linked back to the feature and the design decisions.
7. That blog post might spawn more: a LinkedIn cross-post, a tweet thread, a newsletter mention.

**The flywheel: work → capture thoughts → thoughts accumulate → thoughts become source material → new work → more thoughts.** The Hive is the accumulator. Systems are the consumers. No system-specific logic in the Hive.

### No Hard-Coded Pipelines

The Hive doesn't know "when development finishes, suggest content creation." There are no arrows between systems in the Hive. Instead:

- Each system creates awareness records at meaningful transitions
- You create linked notes as thoughts occur (the key human input)
- Context assembly surfaces relevant material when any system asks for it
- The connections emerge from the graph, not from coded pipelines

This means any new system automatically participates in the flywheel by creating awareness records and being queryable via context assembly.

---

## System Integration Framework

Every system integrates with the Hive the same way. The Hive UI is completely generic — it doesn't know about specific systems. Any system plugs in by following this framework.

### The Contract

1. **Create awareness records at meaningful state transitions.** Not every minor state change — the significant lifecycle events.
2. **Set `system:` field** on all awareness records so the Hive knows which system owns them.
3. **Set `ref:` field** pointing to where the actual artifact lives (in the system's own storage).
4. **Register system-specific tags** in `ontology.yaml`.
5. **System CLIs own their Hive updates.** The Hive CLI is the low-level building block. System CLIs call it internally when transitions happen.
6. **Document the Hive integration** in the system's SKILL.md.

### Content System Integration

The content system lives in a separate repo (`/Users/home/Repositories/content-system/`) with its own state store (`cs.py`, SQLite), brand configs, and a blog creation pipeline (idea → extraction → draft → refine → approve → publish). It has 24 skills including `/content`, `/ea`, `/content-extract`, `/content-draft`, `/content-refine`, `/content-publish`, and a full video pipeline.

#### Source of Truth

**`cs.py` remains the source of truth** for content lifecycle state. It has content-specific logic (format routing, platform mapping, piece dependencies, status transition validation) that belongs in the domain, not in the Hive's generic entity system. The Hive adds cross-system context and awareness — it doesn't replace `cs.py`.

#### Hive Integration Point

**Integration lives in `cs.py` itself** — not in the content skills. When `cs.py` executes a status transition, it also calls the Hive CLI to create/update records. This follows the principle "System CLIs own their Hive updates." Every tool that uses `cs.py` automatically creates Hive records. Graceful degradation: if the `hive` CLI is unavailable, `cs.py` logs a warning and continues — the same pattern it already uses for its own failures.

#### Workflow Entity = Idea Level

Each content idea gets a Hive workflow entity. One idea can spawn multiple content pieces (blog + LinkedIn post + tweet thread), but the workflow tracks the idea-level journey. Individual pieces become awareness records referencing the workflow.

```bash
# When cs.py creates an idea, it also calls:
hive create workflow "DevOps transformation story" \
  --objective "Blog post about our DevOps journey" \
  --domains career-catalyst \
  --refs brand:personal \
  --status active
```

#### Transition Map

At each meaningful transition, `cs.py` creates a Hive knowledge record (awareness record) and updates the workflow entity's `current_context`:

| cs.py Event | Hive Knowledge Record | Tags | Ref |
|------------|----------------------|------|-----|
| Idea created | Workflow entity created | — | — |
| Idea validated | Note: idea validated with angle | `content, validated` | — |
| Piece created | Note: piece created for format/platform | `content, awareness` | — |
| Extraction complete | Note: extraction summary + key material | `content, extraction` | `drafts/{slug}/extraction.md` |
| Draft version created | Note: what changed in this version, approach | `content, draft` | `drafts/{slug}/draft-v{N}.md` |
| Feedback received | Note: feedback substance and intent | `content, feedback` | — |
| Approved | Note: final piece approved | `content, approved` | latest draft path |
| Published | Note: published with URL | `content, published` | published URL |

**Every transition updates the workflow entity:**
```bash
hive update devops-transformation-story \
  --current-context "Blog extraction complete. Draft v1 in progress. LinkedIn post planned but not started."
```

**Draft and feedback records include substance** — not just "draft v3 created" but what changed and why. The reasoning trail between drafts is valuable source material for future content on related topics and for the flywheel.

#### Context Assembly Playbook

The content system's context playbook is defined in its skill and instructs the context assembly session on what to gather for content sessions. The playbook follows priority order:

**1. Search the entire Hive for the topic.** This is the primary context. The Hive contains everything — decisions made during development, design docs, research notes, session summaries, Linear issues about the feature, Slack threads where customers discussed it, meeting notes, email threads, linked observations. All synced external data is already in the Hive. The context assembly agent uses `hive search`, `hive refs`, `hive recent` and follows the graph wherever it leads. This is the source material for the content.

**2. Explore the codebase if the topic involves code.** For technical content, the context assembly agent reads the actual implementation — key files, architecture, recent commits, interesting patterns worth writing about. The Hive knows "we built voice scoring" but the code shows *how*.

**3. Read content pipeline state from `cs.py`.** The agent calls `cs idea show {id} --json`, `cs piece list --idea {id} --json`, `cs event list --entity {id} --json` to understand where the content work stands — piece statuses, draft paths, feedback history, dependencies.

**4. Read brand voice.** From `brands/{brand}/voice.md` — tone, personality, what to embrace, what to avoid. This shapes how the working session writes.

**5. Cross-content awareness.** Other recent content workflows — what's been published, what's in flight. Avoids overlap, enables cross-referencing.

#### Context Note Structure

The context assembly session writes a comprehensive knowledge note with this structure:

```markdown
# Context: [Topic] — Content Session

## System Instructions
You are working in the content system. Use /content to manage
the blog creation pipeline. The current state is:
- Idea: [status] — [summary]
- Blog piece: [status] — [what's next]
- [Other pieces if any]

Your next step: [specific instruction — e.g., "Run /content to
continue extraction" or "Read draft-v3.md, then use
/content-refine with Craig's feedback below"]

Key skills: /content, /content-extract, /content-draft,
/content-refine, /content-publish
State store: cs.py (run `cs status --json` to check current state)
Brand: [brand name] — voice.md loaded below

## The Topic
[Everything the Hive knows — decisions, designs, research,
meetings, customer quotes, Linear issues, Slack threads, email,
code architecture. Full substance with rationale, not summaries.
This is the source material for the content.]

## People & Companies
[Full entity profiles for anyone relevant to the topic.]

## Codebase State
[If technical: key files, architecture, recent changes,
interesting patterns worth writing about.]

## Content Pipeline State
[From cs.py: idea status, piece statuses, draft version,
extraction progress, recent feedback, dependencies.]

## Brand Voice
[From voice.md: tone, personality, embrace/avoid lists.]

## What Else Is In Flight
[Other content workflows — avoid overlap, find cross-references.]

## Do Your Own Due Diligence
[Prompt: verify codebase state, re-read the latest draft,
check if anything changed since this note was assembled.]
```

The **System Instructions** section is what makes this a content session — it routes the working session into the content pipeline immediately. The **Topic** section is the bulk (potentially 15k+ tokens) — the full cross-system context that makes the content rich and informed.

### Session Manager Integration

| Event | Tags | Status | Ref |
|-------|------|--------|-----|
| Session closed | session-summary | done | `sessions/{uuid}.json` |

The awareness record captures: what was accomplished, what decisions were made, what artifacts were produced. Created by the `session close` command. Active session state stays in `sessions/*.json` (real-time, not Hive-appropriate).

### Code Development System Integration

The code development system is Craig's most-used workflow. Unlike the content system (which has its own repo and `cs.py` state store), the code dev system **composes existing OS tools** — projects, beads, dispatch, git worktrees, session manager — with the **Hive workflow entity as the unifying state tracker**. There is no separate `code-dev.py` CLI. The Hive IS the state layer.

#### The Core Problem This Solves

Code features span 20+ sessions across design, review, planning, execution, testing, and deployment. Each session gets a handoff prompt or compaction summary, but over time the context degrades — "losing the plot." Implementing sessions don't know *why* things were designed a certain way. Testing sessions don't have the design context. Debugging sessions lack architectural understanding.

The Hive solves this through **systematic checkpointing** — every design decision, trade-off, rejected alternative, and "why" is captured as a knowledge record linked to the workflow. Context assembly rehydrates any fresh session with the full reasoning trail, not a compressed summary.

#### No Separate State Store

Code development already has state in multiple places — Linear (issues), beads (tasks), git (branches/PRs), dispatch (execution). A dedicated `code-dev.py` would duplicate or need to sync with all of them. Instead:

- **Hive workflow entity** tracks high-level state (phase, current_context, sessions, artifacts)
- **Linear** tracks issues and team-facing work
- **Beads** tracks implementation tasks within a session
- **Git** tracks code (branches, PRs, commits)
- **The Hive knowledge graph** captures the reasoning trail across all of it

#### Checkpointing: Skills Own It

The skills that drive each phase of work create Hive records as a byproduct — the same principle as "System CLIs own their Hive updates." The brainstorming skill, when it reaches a decision point and gets confirmation, calls `hive create decision "..."`. The plan-writing skill records planning decisions. The debugging skill records root cause analyses. Checkpointing is built into the workflow, not a separate manual step.

**Two levels of checkpointing:**
1. **Decision-level checkpoints** — created during a session at each major decision point. Full rationale, alternatives considered, why they were rejected. 10-20+ per design session.
2. **Session summaries** — created at session close, linking to all the checkpoints made during that session and describing the arc. The narrative thread connecting the decision points.

#### Workflow Lifecycle

| Phase | What Happens | Knowledge Created |
|-------|-------------|-------------------|
| **design** | Iterative brainstorming across many sessions. The bulk of context is created here. | Decision checkpoints (each resolved question with full rationale + alternatives), design iterations, research findings, trade-off analyses, rejected approaches. High volume — 10-20+ records per session. |
| **design-review** | 5+ independent sessions review the design. Each reviews from a fresh perspective. | Review findings, concerns raised, validations, requested changes. Each review session creates records. |
| **planning** | Implementation plan built from the finalized design. | The plan itself, task breakdowns, dependency rationale, sequencing decisions. |
| **plan-review** | Plan reviewed against the design. | Review findings, gaps identified, adjustments made. |
| **execution** | Implementation via parallel subtasks. | Per-task completion records, implementation decisions made during coding, deviations from plan and why. Lower volume than design — more mechanical. |
| **code-review** | Implementation reviewed against the original design. | Review findings, issues found, fixes applied, design conformance assessment. |
| **testing** | Testing and debugging — often a long phase. | Bug reports, root cause analyses, what was tried, what worked. Substantial knowledge generated — the "why doesn't this work" reasoning trail. |
| **deployment** | Ship it. | Deployment record, issues encountered, rollback decisions if any. |

The workflow entity's `current_context` is updated at each phase transition and at session close within a phase:

```bash
hive update voice-scoring-ui \
  --current-context "Design phase complete (sessions 1-8). 5 design reviews done, all passed. Implementation plan created and reviewed. Execution in progress — 3/7 tasks complete. Task 4 (API wiring) blocked on endpoint schema question."
```

#### Context Assembly Playbook

This is the piece that solves "losing the plot." When Craig starts a fresh session on a code workflow — whether session 1 (design) or session 25 (debugging) — the context assembly agent gathers:

**1. Search the entire Hive for the topic.** Everything — decisions from design sessions, meeting notes where the feature was discussed, Linear issues, Slack threads, customer requests, related features, prior art. All synced external data is already in the Hive.

**2. The workflow entity.** `current_context` tells the session exactly where things stand — phase, recent progress, blockers, what's next.

**3. All decision checkpoints linked to this workflow.** This is the critical difference from a handoff prompt. Not a compressed summary of 20 sessions — the actual decisions with full rationale, alternatives considered, and why they were rejected. The context assembly agent includes ALL of them with substance. This is how session 25 knows *why* entities are MongoDB-only, not just *that* they are.

**4. The codebase.** Read key files, recent commits, test results, current state of the implementation. The Hive knows what was decided; the code shows what was actually built.

**5. Related workflows.** Other features that touch the same code, depend on this one, or were designed with shared assumptions.

#### Context Note Structure

```markdown
# Context: [Feature] — Code Development Session

## System Instructions
You are working on [feature]. Current phase: [phase].
[Specific instruction for what to do next — e.g., "Continue
design review" or "Debug the failing integration test"
or "Implement task 4 from the plan".]
[Key skills to use for this phase.]
[Target repo and key file paths.]

## Design Decisions (Full Reasoning)
[Every decision checkpoint — not summaries, the actual
rationale. "We chose X because Y. We considered A and B
but rejected them because Z." This section can be 10k+
tokens for a mature workflow. That's fine — this IS the
context that prevents losing the plot.]

## Current State
[From workflow entity: what phase we're in, what's been
built, what's in progress, what's blocked, what's next.]

## The Broader Context
[Everything else the Hive knows — meetings, Linear issues,
Slack discussions, customer requests, email threads,
related features and their state.]

## Codebase State
[Key files, recent commits, test results, architecture
relevant to the current phase.]

## Related Workflows
[Other features touching the same code or with dependencies
on this workflow.]

## Do Your Own Due Diligence
[Verify codebase state, run tests, read recent commits
since this note was assembled.]
```

The **Design Decisions** section is the heart of it. A compressed handoff prompt says "entities are MongoDB-only." This section says "entities are MongoDB-only because YAML entity files created file↔database sync complexity, nobody would open people/craig.yaml in a text editor, and knowledge type proliferation was unnecessary. We considered keeping files for all types (too much sync overhead) and a full type system for everything (over-engineered). Decided 2026-03-14." That level of detail is what prevents losing the plot across 20+ sessions.

#### Principle: Capture the Reasoning Trail, Not Just the Outputs

This applies to any system with creative or exploratory phases. The design phase produces high volumes of native knowledge notes — not just a single "design doc created" awareness record. The reasoning trail — questions explored, research findings, trade-off analyses, rejected approaches — is captured as individual linked notes by the skill driving the process.

More captured knowledge is better, not noisier. The context assembly agent handles relevance — semantic search and graph traversal surface what matters for each specific context request. Session 25 doesn't get all 200 decision checkpoints dumped into its context. It gets the ones relevant to what it's working on.

### External System Sync Framework

Systems that Craig operates through Claude Code sessions (content, code development) create Hive notes as a byproduct of working — the session's skill handles it. But external systems (Linear, Calendar, Email, Slack, GitHub) have data changing independently. These need a **bidirectional sync framework**.

#### Inbound: External System → Hive

| Mechanism | How it works | Best for |
|-----------|-------------|----------|
| **Pull** | `hive sync <system>` — calls external API, creates/updates notes | Calendar, Email (poll periodically) |
| **Push (webhooks)** | Hive receives HTTP events, creates/updates notes in real-time | Linear, GitHub, Slack (when webhooks available) |
| **Scheduled** | Cron or background process running pull sync on interval | Keeping data fresh without manual trigger |

Each sync adapter knows: how to authenticate, what data to pull, and how to map external data to Hive note fields (tags, status, domain, ref, system). The framework handles dedup, incremental sync, and conflict resolution.

#### Outbound: Hive → External System

Two patterns for pushing actions back to external systems:

1. **Direct tile actions** — simple state changes from the Wall, no session needed. Mark a tile as done → Hive updates the note → sync adapter pushes to the external system (e.g., close Linear issue, archive email).
2. **Session-based actions** — complex interactions that spawn a Claude Code session. Reply to an email, implement a feature, review a PR. The session uses existing skills (/linear, /google-workspace, /slack, /github) to interact with the external system.

#### Status Lifecycle Per System

Each sync adapter defines its own status mapping because different systems have different lifecycles:

- **Linear:** Open → `active`, In Progress → `active`, Done → `done`, Canceled → `archived`
- **Calendar:** Upcoming (next 24-48h) → `active`, Past → `archived`
- **Email:** Unread/flagged → `active`, Read → `done`, Archived → `archived`
- **Slack:** Unread mentions → `active`, Read → `done`
- **GitHub:** Open PR → `active`, Merged → `done`, Closed → `archived`

These mappings determine what's prominent on the Wall (active items surface, done items fade, archived items hidden by default). Each system defines what "active" means in its context.

#### What Gets Shown on the Wall

Not every note in the Hive is a Wall tile. The Wall shows notes based on their status:
- **Active/backlog** — visible, prominence based on priority
- **Done** — faded but visible (completed work is flywheel source material)
- **Archived** — hidden from Wall by default, accessible via search/filtering

The sync adapter sets status appropriately when ingesting data. No separate "show on wall" flag — the status IS the visibility control.

### Future Systems

Any new system follows the same pattern. The Hive UI doesn't change. New tiles appear automatically because they're just notes with tags and metadata. The visual encoding (color from system, accent from domain, brightness from status) works for any system that registers its tags in the ontology.

---

## Open Decisions

Decisions that need to be made during implementation, not during design.

### 1. Note Creation Mechanics
**Question:** How exactly do notes get created during sessions? Does Claude Code call `hive note create` explicitly, or is there a hook/automation?
**Leaning:** Explicit CLI calls orchestrated by skills. Session-summary notes could be automated via session close hook. Brainstorming/spec notes created by skills at key output points.
**Decide during:** Phase 1 implementation.

### 2. Sync Trigger
**Question:** How do markdown files stay in sync with MongoDB? Watcher? Hook? Manual?
**Options:** (a) `hive sync` manual command after changes, (b) Git commit hook that triggers sync, (c) File watcher daemon, (d) Sync on CLI operations (create/update auto-syncs).
**Leaning:** (d) — sync happens as part of CLI operations. `hive sync` for bulk re-indexing.
**Decide during:** Phase 1 implementation.

### 3. External System Sync Details
**Question:** Per-system sync adapter implementations — authentication, mapping, frequency, conflict resolution.
**Framework decided:** Bidirectional sync with inbound (pull/push/scheduled) and outbound (direct tile actions + session-based actions). Each adapter defines its own status lifecycle mapping. See "External System Sync Framework" section.
**Remaining:** Specific adapter implementations for each system (Linear, Calendar, Email, Slack, GitHub). Each designed when that system integration is built.
**Decide during:** Phase 3 (Linear), Phase 4+ (others).

### 4. Session Lifecycle Integration
**RESOLVED (2026-03-14):** Dedicated context assembly session. The Hive UI spawns a short-lived Claude Code session that gathers context using the Hive CLI, writes a comprehensive context note, then terminates. The working session is then spawned with the context note injected via `tmux send-keys`. No hooks, no skill invocation — the context is already assembled before the working session exists.

### 5. Hive UI in OS Terminal
**Question:** What views? How does it integrate with the existing terminal grid?
**Resolved:** See "The Hive UI" section below. Designed in session 2026-03-09-a.

### 6. Multi-User Access
**Question:** How do teammates and the CEO see the Hive?
**Direction:** Initially single-user (Craig). Multi-user likely through shared MongoDB or generated outputs (weekly summaries, newsletters). Not blocking for MVP.
**Decide during:** Phase 6.

### 7. Beads Coexistence
**Question:** Do beads stay? How do they relate to Hive task notes and Linear?
**Clarified (2026-03-09):** Beads stays in its lane — it's for implementation plans within individual Claude Code sessions (breaking down code tasks and executing them via dispatch). Beads is NOT a system-wide work tracker. The Hive handles system-wide work awareness. Linear is the team-facing issue tracker. Beads tasks may get mirrored as awareness records, but beads is not a source of truth for "what needs doing" — Linear and the Hive are.
**Decide during:** Phase 3.

### 8. Graph Quality
**Question:** How do we prevent the graph from becoming noisy? Stale notes?
**Direction:** Recency weighting in search naturally deprioritizes old notes. `status: archived` explicitly removes from active views. Periodic review (monthly?) to archive stale notes. Semantic search quality depends on embedding model — tune through experience.
**Decide during:** Ongoing after Phase 2.

### 9. Embedding Model Selection
**Question:** Which local model? Dimensions?
**Options:** Ollama `nomic-embed-text` (768d), `mxbai-embed-large` (1024d), `all-minilm` (384d)
**Leaning:** Start with `nomic-embed-text` — good balance of quality and speed. Swappable via abstraction layer.
**Decide during:** Phase 2.

### 10. Context Assembly LLM
**RESOLVED (2026-03-14):** The context assembly agent IS a Claude Code session — it uses the Hive CLI as a toolkit, decides what queries to run based on user intent, and synthesizes the results into a comprehensive context note. No fixed algorithm, no separate local LLM, no CLI-level assembly. The session's Claude instance does the reasoning. Different intent → different retrieval strategy.

---

## Implementation Phases

### Phase 1: Foundation — Data Layers + CLI
**Goal:** Both data layers exist. Entities in MongoDB, knowledge as markdown files. The 14-command unified CLI works. Registry is seeded.

- [ ] Install local MongoDB Community Edition (`brew install mongodb-community`)
- [ ] Create `hive/` directory structure — `.registry/`, `.registry/types/`, `.templates/`, knowledge subdirectories (notes/, decisions/, designs/, research/, sessions/)
- [ ] Create entity type definitions in `.registry/types/` — person, company, product, project, workflow, meeting, brand, platform, channel
- [ ] Create `hive/.registry/ontology.yaml` with initial tags (decision, design, research, session_summary, note, feedback, context_assembly), domains, statuses — ensuring disjoint sets with entity types
- [ ] Build `hive` CLI core (Python, Click/Typer) with unified routing:
  - `hive init` — set up vault, create MongoDB database, seed indexes, load types
  - `hive create <type-or-tag> "title"` — route to entity (MongoDB) or knowledge (file + index)
  - `hive get <id>` — query both layers, entity first, return with layer indicator
  - `hive update <id>` — resolve layer, update accordingly
  - `hive list <type-or-tag>` — route to entity or knowledge list
  - `hive refs <id>` — bidirectional reference traversal
  - `hive recent [duration]` — reverse-chronological mixed-type feed
  - `hive sync` — index all knowledge files to MongoDB
  - `hive status` — overview: counts by type/domain/status
  - `hive init` — initialize vault, MongoDB, seed registry
  - `hive types list/show`, `hive tags list`, `hive domains list` — registry inspection
- [ ] Build type registry loader (`types.py`) — reads entity type definitions, validates schemas
- [ ] Build two-layer record CRUD (`records.py`) — entities → MongoDB only, knowledge → files + MongoDB index
- [ ] Create the `/hive` skill (`.claude/skills/hive/SKILL.md`)
- [ ] Seed initial entities: people (Craig, Cam), companies (Indemn), products, projects, brands
- [ ] Migrate 5-10 existing artifacts as knowledge records (decisions, designs)
- [ ] Verify: entity create/get/list works, knowledge create/get/list works, refs traversal works, routing is correct

**Exit criteria:** `hive create person "Craig"` creates entity in MongoDB. `hive create decision "Use two layers"` creates markdown file + MongoDB index. `hive get craig` returns entity. `hive refs craig` shows connected records. `hive list person` and `hive list decision` route correctly. Output shows layer indicators.

### Phase 2: Context Engine + Assembly
**Goal:** Semantic search works. The context assembly agent can use the Hive CLI to curate context. Workflow entities track long-running work state.

- [ ] Install Ollama + embedding model locally (start with `nomic-embed-text`)
- [ ] Build embedding abstraction layer (`embed.py`)
- [ ] Add embedding generation to `hive sync` — embed knowledge file content, store vectors in MongoDB
- [ ] Build `hive search` — semantic search via cosine similarity + tag/domain/type/recency filters, searches both layers
- [ ] Build `hive context` — the context assembly coordination command. Takes query + objective + system, returns structured context.
- [ ] Build `hive refs` with depth — multi-hop relationship traversal across entity types
- [ ] Build context assembly session support — the session CLI can create short-lived sessions that write context notes and terminate
- [ ] Create system context playbooks — each system's skill defines what context to gather (content system and code dev system are first)
- [ ] Build workflow entity patterns — systems can create/update workflow entities to track long-running work state
- [ ] Migrate all existing artifacts to Hive knowledge records (decisions, designs, research, notes)
- [ ] Extract decisions from INDEX.md files into standalone knowledge records
- [ ] Test: context assembly session reads system playbook, queries Hive, writes comprehensive context note, working session starts hydrated

**Exit criteria:** `hive search "voice scoring"` returns relevant knowledge via semantic + keyword search. A context assembly session can use Hive CLI to assemble context for a code development workflow. Workflow entities persist state across sessions. `hive recent 7d` shows mixed-type activity feed.

### Phase 3: System Integration + External Sync
**Goal:** Content and code dev systems create awareness records and update workflows. External system data flows into the Hive.

**Note:** Sync adapters build on existing Claude Code skills — `/linear` (linearis), `/google-workspace` (gog), `/slack` (agent-slack), `/github` (gh). Each adapter adds its own entity type definition to `.registry/types/`.

- [ ] Content system integration — content CLI creates/updates workflow entities, creates awareness records at each pipeline stage (idea → extraction → draft → publish)
- [ ] Code development system integration — code dev skill creates/updates workflow entities, creates awareness records at lifecycle transitions
- [ ] Update `/sessions` skill — session close creates session-summary knowledge record linked to workflow
- [ ] Update brainstorming skill — reasoning trail captured as linked knowledge records
- [ ] Build sync adapter framework — common interface for inbound/outbound sync, dedup, incremental updates
- [ ] Build Linear sync adapter — pull issues as entity records, push status changes back
- [ ] Build Google Calendar sync adapter — pull upcoming events, status based on timing
- [ ] Build Slack sync adapter — pull unread mentions/DMs
- [ ] Build GitHub sync adapter — pull open PRs/issues
- [ ] Implement scheduled sync for continuous freshness
- [ ] Test: full workflow — brainstorm → spec → implementation → completion, all tracked as workflow entity + knowledge records + awareness records

**Exit criteria:** Content and code dev systems create workflows and awareness records as a byproduct of working. Linear issues, calendar events, Slack mentions flow into the Hive as synced entities. A complete feature lifecycle is traceable through the Hive.

### Phase 4: The Hive UI
**Goal:** The Hive is the home screen. Wall + Focus Area. Tiles. Session spawning with dedicated context assembly.

- [ ] Evolve OS Terminal React app — replace session grid with Wall + Focus Area layout
- [ ] Build tile component — fluid sizing, progressive information disclosure, color/accent/brightness encoding
- [ ] Build Wall layout — tiles surrounding Focus Area, breathing with activity level
- [ ] Build Focus Area — equal-sized auto-grid of terminal panels (xterm.js, existing) + browser panels (iframe, new)
- [ ] Build Overview toggle — expand Wall to full screen, collapse back to Focus
- [ ] Add Hive API routes to Express backend — wrap Hive CLI with JSON output
- [ ] Add WebSocket Hive updates — push changes to frontend
- [ ] Build Wall ordering — priority → status → recency, drag-to-reorder within priority buckets
- [ ] Build domain filtering — click domain tile to filter Wall
- [ ] Build search tile, quick capture tile, "create linked note" interaction
- [ ] Build session spawning from tiles — click tile → prompt for objective → spawn context assembly session → spawn working session with context
- [ ] Build direct tile actions — mark done, change priority, archive → outbound sync
- [ ] Merge session state tiles (from `sessions/*.json`) with Hive tiles into unified Wall
- [ ] Color/visual mapping from `ontology.yaml` — type colors, domain accents, status brightness
- [ ] Responsive layout

**Exit criteria:** The Hive is the home screen. You see your world as tiles, click to start context-hydrated sessions (with dedicated context assembly), work in Focus panels, observe everything from the Wall.

### Phase 5: Expansion
**Goal:** Platform integrations, multi-user, graph maturity.

- [ ] Substack, LinkedIn, X integration — content publishing and engagement tracking via sync adapters
- [ ] Gmail sync adapter — pull unread/flagged, mark read/archive
- [ ] Multi-user — shared MongoDB or generated output views for CEO/teammates
- [ ] Graph quality management — archival conventions, stale note detection, pruning
- [ ] Automated ontology management — detect tag drift, suggest merges
- [ ] Morning consultation session type — daily planning with calendar, priorities, active work
- [ ] Cross-domain discovery automation — proactively surface connections

**Exit criteria:** Content platforms connected. The CEO gets weekly views. Graph quality stays high as the system scales.

---

## Migration Strategy

### From Current Projects to Hive

The transition is gradual. Nothing breaks.

**Coexistence period:**
- `projects/` continues to work as-is
- `hive/` grows alongside it
- The `/project` skill queries both (Hive first, INDEX.md as fallback)
- New knowledge goes to `hive/`; old artifacts get migrated incrementally

**Migration steps:**
1. **Create entities** for all existing projects, people, companies — directly in MongoDB via `hive create`
2. **Migrate artifacts** — add Hive frontmatter (tags, domains, refs) to existing artifacts, copy to `hive/` knowledge directories, index into MongoDB. 73 artifacts total.
3. **Extract decisions** — pull decisions from INDEX.md files into standalone knowledge records tagged `decision`
4. **Extract external resources** — create entity records for resources listed in INDEX.md
5. **Create workflow entities** — for active work tracked in INDEX.md, capturing current_context from Status sections
6. **Deprecate INDEX.md** — once workflow entities and context assembly reliably replace INDEX.md, stop maintaining them. They remain as historical artifacts in Git.

**What doesn't migrate:**
- The `projects/` directory structure stays (at least initially) — it's not harmful
- Beads continue working per-project — they're separate from the Hive
- System architectures (content system, dispatch) don't change — they just gain Hive reporting

---

## Maintenance & Continual Improvement

### Daily
- Notes are created as a byproduct of working (sessions, brainstorming, decisions)
- Awareness records flow in from systems (content, dispatch, code, Linear)
- Graph grows organically

### Weekly
- `hive status` shows what's active, what's new, what's connected
- Weekly summary skill draws from the Hive (replaces manual INDEX.md review)
- Review newly created tags — ensure ontology consistency

### Monthly
- Archive stale notes (`status: archived`) — notes that haven't been referenced in 60+ days
- Review ontology — merge duplicate/similar tags, remove unused ones
- Assess context assembly quality — are briefings useful? Adjust scoring weights if not.
- Review graph quality — are connections meaningful? Too much noise?

### Per New System
- Register system-specific tags in `ontology.yaml`
- Document Hive integration in the system's skill
- Build awareness record creation into the system CLI
- Test cross-system context assembly

### Self-Improvement: The Feedback System

The Hive improves through its own mechanism — feedback is captured as notes, which become context for future Hive development sessions. No special infrastructure, no automated ML loops. The system eats its own cooking.

**The `hive feedback` command:**

```bash
hive feedback "context assembly for voice scoring missed the deployment pattern notes"
```

Creates a native knowledge note with:
- Your feedback message as the content
- Auto-tagged: `feedback, hive-improvement`
- Auto-linked to the current session (what you were working on when the friction occurred)
- Auto-captures session context: objective, system, domain
- In Phase 2+: captures a snapshot of what `hive context` returned, so you can see what retrieval produced vs what was actually needed

**Types of feedback that naturally emerge:**
- **Retrieval gaps** — "missed X", "Y was irrelevant", "needed more depth on Z"
- **Ontology friction** — "needed a tag that doesn't exist", "these two tags overlap"
- **Workflow friction** — "this took too many steps", "wanted to do X but couldn't"
- **Pattern recognition** — "I keep doing X manually, should be automated"

**How it drives improvement:** When you start a session to work on the Hive itself, `hive context "improve the hive"` surfaces all accumulated feedback notes. The development session has full awareness of what's been working and what hasn't — with precise diagnostic data (retrieval snapshots), not just vibes.

**Evolution:** Phase 1 — `hive feedback` auto-tags and auto-links (simple). Phase 2 — adds retrieval snapshot capture once the context engine exists. Grows with the system.

### Other Continual Improvement Mechanisms
- **Ontology evolution:** New tags emerge from real work. The registry grows to match how the system is actually used.
- **Embedding model upgrades:** As better local models emerge, swap via `hive sync --re-embed`. The abstraction layer makes this painless.
- **Skill integration depth:** Start with basic Hive integration in skills. Deepen over time as patterns emerge.
- **Cross-domain discovery:** Track when a session discovers a useful cross-domain connection. Use this to improve semantic search and graph expansion.

---

## Key Decisions Made

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-08 | ~~Everything is a note~~ **SUPERSEDED** by typed record system (2026-03-09) | Originally: one format, tags differentiate. Replaced because structured entities need schemas and typed relationships for effective search and relationship traversal. |
| 2026-03-08 | The Hive is connective tissue, not a data layer | Systems keep their own architectures. The Hive indexes, links, and surfaces — it doesn't replace. |
| 2026-03-08 | ~~Two kinds of notes~~ **EVOLVED** — now typed records with awareness via system/ref fields | Any type can be an awareness record by having system: and ref: fields. The distinction is per-record, not per-kind. |
| 2026-03-08 | ~~Flat vault structure~~ **SUPERSEDED** by typed directories (2026-03-09) | Now organized by type: people/, companies/, decisions/, notes/. Type determines directory. |
| 2026-03-08 | Local MongoDB, not Atlas | Personal/cross-domain data shouldn't live on Indemn's cluster. Local is private, free, fast. |
| 2026-03-08 | Local embedding model (Ollama), swappable | Start local for experimentation. Abstraction layer enables switching to API models later. |
| 2026-03-08 | Controlled vocabulary via `ontology.yaml` | Prevents tag fragmentation across sessions. Evolves deliberately, not accidentally. |
| 2026-03-08 | Context assembly produces session initialization instructions | Not just knowledge — includes relevant skills, proactive reads, and reminders. Tailored by objective. |
| 2026-03-08 | System CLIs handle Hive updates, not raw `hive note create` | Each system manages its own domain logic. The Hive CLI is the low-level building block. |
| 2026-03-08 | Skills must document their Hive integration convention | New skills follow the convention. Existing skills evolve incrementally to become Hive-aware. |
| 2026-03-08 | ~~Files are source of truth (for all native records), MongoDB is derived~~ **REFINED** (2026-03-14) — files are source of truth for knowledge records only. Entities live in MongoDB only. | Originally: all native records as files. Refined: entities don't need to be files (never opened in a text editor). Knowledge records (prose) remain git-tracked files. |
| 2026-03-08 | Graph expansion favors breadth over depth | Can't explore what you don't know about. Surface broadly, then go deep on-demand. |
| 2026-03-08 | Migration is gradual — projects/ coexists with hive/ | Nothing breaks. New knowledge goes to Hive. Old artifacts migrate incrementally. |
| 2026-03-08 | Hive UI lives in OS Terminal, Bloomberg-style | Never leave the system. Kanban, graph, timeline views alongside session grid. |
| 2026-03-08 | Hive notes for skills and systems enable self-aware context assembly | The Hive knows what tools exist and can recommend relevant ones per session. |
| 2026-03-09 | The Hive is the home screen — replaces OS Terminal as front door | The Hive is the awareness layer; terminals are one view within it. You start at the Hive, not the terminal grid. |
| 2026-03-09 | Wall + Focus Area layout — Wall surrounds Focus, breathes with activity | The Wall is peripheral awareness (tiles). The Focus Area is active work (terminals/browsers). Wall expands when less is active, compresses when focused. |
| 2026-03-09 | Tiles are the only UI elements — no chrome, no buttons, no menus | The data is the UI. Every interactive element is a tile showing real information. Domain filtering, search, and capture are all tiles. |
| 2026-03-09 | Fluid tile sizing, not fixed breakpoints | Tiles show as much info as fits. Continuous scaling, not three discrete sizes. Fewer tiles at useful size beats more tiles at useless size. |
| 2026-03-09 | Rectangular tiles for MVP, honeycomb deferred | Hexagonal layouts are significantly harder (CSS grid is rectangle-native). Start with rounded rectangles, organic feel. Honeycomb is a future CSS-level change. |
| 2026-03-09 | Color=system, accent=domain, brightness=status for tile encoding | Three visual axes for glanceable scanning. System is primary color, domain is accent/border, status is brightness/opacity. |
| 2026-03-09 | Two data sources: sessions/*.json (real-time) + Hive API (knowledge) | Active sessions stay in session state files (high-frequency operational data). Everything else from Hive. Completed sessions get awareness records. |
| 2026-03-09 | UI reads from Hive only — doesn't call external system APIs directly | All system data syncs into the Hive backend. The UI reads one source. That's the point of connective tissue. |
| 2026-03-09 | Session initialization: ask objective BEFORE retrieving context | Context retrieval needs context. The objective shapes what's relevant. Same topic, different objectives → different context. |
| 2026-03-09 | Context assembly parameterized by topic + objective + system | Different systems prioritize different context for the same topic. Brainstorming for code ≠ brainstorming for content. |
| 2026-03-09 | First message to new sessions via `tmux send-keys` with tile metadata | Lightweight injection — tile note ID, tags, domain, system. Session handles its own context retrieval using Hive CLI. |
| 2026-03-09 | The flywheel is emergent from linked notes, not coded pipelines | No hard-coded arrows between systems. Work → capture thoughts → thoughts accumulate → any system consumes them. The Hive is the accumulator. |
| 2026-03-09 | "Create linked note" is a first-class UI interaction | One-click note creation linked to a parent tile. Primary mechanism for flywheel — thoughts accumulate on existing work. |
| 2026-03-09 | Don't hard-code system-specific logic in the Hive UI | The UI is completely generic. Any system plugs in by creating awareness records. New systems get tiles automatically. |
| 2026-03-09 | Every system follows the same Hive integration framework | Create awareness records at meaningful transitions, set system/ref fields, register tags, document integration. |
| 2026-03-09 | Content system creates awareness records at each pipeline stage | idea → extraction → draft → approved → published → repurposed. Each stage gets a Hive record. System owns its updates. |
| 2026-03-09 | Design/brainstorming phases capture reasoning trails as many native notes, not just final artifacts | Questions, research, trade-offs, rejected approaches — all captured as linked notes by the skill driving the process. More knowledge is better; retrieval handles relevance. |
| 2026-03-09 | Code development system is a separate design effort — Hive defines the generic contract, the system defines its specific transitions | Same pattern as content system: designed separately, integrates via the standard framework. |
| 2026-03-09 | Wall arrangement is user-driven, not LLM-driven at render time | Priority (user-set) → status → recency → manual drag-to-reorder. Intelligence is in note metadata (set by LLMs at write time), not in a layout algorithm. |
| 2026-03-09 | `hive feedback` command for self-improvement — feedback is just notes | Auto-tagged, auto-linked to session context. Retrieval snapshots added in Phase 2. Feedback surfaces when working on the Hive itself. |
| 2026-03-09 | Morning consultation is a session type, not a feature | Daily planning via a session that pulls calendar, tasks, priorities. Output is updated priorities on existing notes. Future work. |
| 2026-03-09 | ~~Everything is a typed record — types defined in YAML, not code~~ **REFINED** (2026-03-14) — two layers: entity schemas in registry + tagged knowledge as markdown | Originally: 14+ types all with YAML schema definitions. Refined: entity types have schemas, knowledge types are just tags on markdown notes. Simpler, fewer types. |
| 2026-03-09 | Type system is configuration-driven and extensible | Add a YAML file to `.registry/types/` → new entity type exists. CLI auto-discovers. No code changes needed. Scales to any domain. Knowledge records are just notes with tags. |
| 2026-03-09 | ~~Entities are YAML files, knowledge is Markdown~~ **SUPERSEDED** (2026-03-14) — entities are MongoDB-only, knowledge is Markdown files | Entities don't need files — they're structured data queried via CLI/API. Knowledge records are git-tracked markdown with YAML frontmatter. |
| 2026-03-09 | Typed references replace generic wiki-links for entity relationships | person → company, meeting → attendees are typed refs, not `[[wiki-links]]`. Wiki-links remain for knowledge-to-knowledge connections. |
| 2026-03-09 | ~~Typed directories replace flat vault~~ **REFINED** (2026-03-14) — knowledge directories organized by tag convention, entities have no directories (MongoDB-only) | Entity directories (people/, companies/) eliminated. Knowledge organized by convention (notes/, decisions/, designs/) but these are tag-based, not type-based. |
| 2026-03-09 | CLI is type-aware — `hive create <type>`, `hive <type> list` | Type-scoped commands enable structured queries and pre-filtering. Better than `hive search` for known types. |
| 2026-03-09 | Create a type when: stable identity AND (referenced from other types OR structured fields enable useful queries) | Principle for type vs tag distinction. Tags subcategorize within types. Types define schemas and relationships. |
| 2026-03-09 | Color=type (not system) in tile visual encoding | More specific and meaningful. Each type gets its own color in the registry. |
| 2026-03-09 | Synced records are git-ignored, live in `.synced/` directories | External sync data (Linear, calendar, email, Slack, GitHub) creates files in `hive/.synced/<system>/` which is gitignored. Native records (entities, knowledge) are git-tracked. Source of truth for synced data is the external system, rebuilt via `hive sync <system>`. |
| 2026-03-09 | Obsidian compatibility dropped — Hive UI replaces the need | Entity records are YAML (Obsidian can't render). The Hive UI is the visualization layer. No need to maintain Obsidian compatibility. |
| 2026-03-09 | Quick capture always creates a `note` first, reclassifies async | Zero friction capture. LLM determines if it should be promoted to a typed record (task, decision, etc.). If so, creates the typed record and archives the original note. Capture speed > classification accuracy. |
| 2026-03-09 | Bidirectional sync framework for external systems | Inbound: pull/push/scheduled adapters. Outbound: direct tile actions (simple) + session-based actions (complex). Each adapter defines its own status lifecycle mapping. |
| 2026-03-09 | Status is the Wall visibility control — no separate "show on wall" flag | Active items surface, done items fade, archived items hidden. Sync adapters set status based on external system state. |
| 2026-03-14 | Context assembly is an LLM agent, not a fixed algorithm | ~~Embed → cosine similarity → graph expand → score~~ SUPERSEDED. The context assembly agent is an LLM that uses the Hive CLI as a toolkit. It reads user intent and decides what queries to run — semantic search, structured entity lookups, recency filters, relationship traversal — whatever fits the situation. Different intent → different retrieval strategy. |
| 2026-03-14 | Dedicated context assembly step before session starts | A separate, short-lived LLM call (not the working session itself) curates context. The working session starts with context already assembled — zero retrieval overhead in the session's own context window. |
| 2026-03-14 | Workflow is a typed entity — the living context anchor | A workflow entity (objective, status, current_context, sessions list, project ref) replaces INDEX.md. Gets updated as sessions progress. The context assembly agent reads it to know "where are we" without traversing the whole chain. |
| 2026-03-14 | Entities live in MongoDB only — no YAML files | ~~Entities stored as YAML files~~ SUPERSEDED. Person, company, project, workflow — structured records in MongoDB only. Not git-tracked as individual files. Backed up via MongoDB dumps. Eliminates file↔database sync complexity for entities. |
| 2026-03-14 | Knowledge lives as markdown files, git-tracked | Notes, decisions, designs, session summaries — prose with YAML frontmatter. Git-tracked. MongoDB indexes them (derived) for semantic search and structured queries. Files are source of truth for knowledge. |
| 2026-03-14 | ~~14+ type system~~ SUPERSEDED — two layers: entity schemas + tagged knowledge | Entity types (person, company, project, workflow, etc.) have schemas in the registry with structured fields and typed relationships. Knowledge records are all markdown notes differentiated by tags (decision, design, research, session_summary), not separate type schemas. Fewer types, simpler system. |
| 2026-03-14 | Entity types are deterministic entry points for context assembly | The context assembly agent starts from typed entities (query by name, structured fields, relationship traversal) then follows the associative knowledge network outward. Entities are the anchors; knowledge is discovered through traversal and search from those anchors. |
| 2026-03-14 | No entity companion notes — knowledge refs entities naturally | Entities don't need dedicated prose notes. Context about an entity lives in the knowledge records that reference it (meeting notes, decisions, session summaries). Unique context that doesn't exist elsewhere is captured as a regular note that refs the entity. |
| 2026-03-14 | Context output is a persisted, evolving workflow record — not ephemeral | Context assembly output is stored as the workflow entity's current_context field (or linked records). Subsequent sessions read the existing context + new linked records. Asynchronous — context can be pre-assembled and updated as workflows progress. |
| 2026-03-14 | Context assembly agent has exactly two sources: Hive + codebase | The Hive has all synced external data (Linear, Slack, Calendar, GitHub). The agent doesn't query external tools directly — stale data is a sync problem, not a context assembly problem. Codebase is the exception: too large/dynamic to sync, must be read directly. Web search is the working session's job. |
| 2026-03-14 | Context assembly runs as a Claude Code session via existing session CLI | Not Agent SDK, not direct API. Uses the same session infrastructure (session create, tmux, worktrees) that manages all OS sessions. The Hive UI spawns it, it writes a context note, then the working session gets created with that context. |
| 2026-03-14 | No explicit repo field on entities — workflow context carries it naturally | Session summaries and decisions mention repos as a byproduct of work. For new workflows, CLAUDE.md has the full service inventory. The OS session CLI handles repo access via `--add-dir`. |
| 2026-03-14 | Unified CLI commands — entity/knowledge distinction is transparent | `hive get`, `hive create`, `hive search` route to the correct layer automatically based on whether the argument is an entity type or knowledge tag. Layer indicators in output. JSON when piped, text when interactive. |
| 2026-03-14 | Entity types and knowledge tags must be disjoint sets | If `meeting` is an entity type, it cannot also be a knowledge tag. The ontology enforces this. Eliminates routing ambiguity in the unified CLI. |
| 2026-03-14 | 14-command CLI surface: context, get, create, update, search, list, refs, recent, sync, status, init, types, tags, domains | No `hive workflow` sugar (use generic get/update). No `hive feedback` (it's `hive create note --tags feedback`). No `hive tags add` (edit ontology.yaml directly). Workflow patterns documented in skill, not CLI. |
| 2026-03-14 | `hive recent` command for temporal awareness | Reverse-chronological mixed-type feed across both layers. The context assembly agent's most-used command — "what happened lately" is critical for every context assembly. |
| 2026-03-14 | Systems own workflow lifecycle, not the Hive | The workflow entity type exists in the Hive, but creation, updates, transitions, and completion are managed by the system that owns the work (content system, code dev system, etc.). The Hive stores it. Context assembly reads it. System CLIs create and update it. |
| 2026-03-14 | Context note format is system-specific, not a generic template | Each system's skill defines what context matters for its workflow and how the context note should be structured. The context assembly session reads the system's instructions and follows them. New systems define their own context needs. |
| 2026-03-14 | Context notes are comprehensive, not compressed | More context is better. Full decision text with rationale, full entity profiles, complete workflow state. 20k tokens is fine — fraction of the context window. The context assembly session produces coherent, non-redundant output naturally. |
| 2026-03-14 | Context assembly session reads system's context playbook from the system's skill | The Hive provides CLI infrastructure. Each system's skill describes what to gather and how to structure it. The context assembly session is generic — reads instructions, follows them. Extensible to any new system. |
| 2026-03-14 | Entity aliasing handled by LLM + semantic search — no alias registry needed | The context assembly session IS the fuzzy matcher. `hive search` returns candidates, the LLM connects dots. If problems arise, `hive feedback` captures misses for future improvement. |
| 2026-03-14 | ~~Session Initialization: session asks objective~~ SUPERSEDED by dedicated context assembly session | The design doc's flow (session asks objective → session retrieves context) replaced by: Hive UI prompts for objective → context assembly session gathers context → writes context note → working session starts hydrated. The "doctor appointment" metaphor still applies — the nurse does intake before the doctor sees you. |
| 2026-03-14 | Mobile experience deferred until desktop Hive UI is built | OS Terminal already has single-pane mode for ≤1024px. Mobile design builds on that. |

---

## What This Replaces, Augments, and Preserves

### Replaces
- **INDEX.md as resume file** → Context assembly dynamically generates the equivalent from the graph
- **Manual context curation** → LLM-assembled session initialization instructions
- **Siloed project knowledge** → Unified, linked graph across all domains

### Augments
- **The project system** → Projects become entity records in MongoDB. Workflows track state that INDEX.md used to hold. Artifacts become knowledge records. The structure evolves but the knowledge is preserved.
- **Skills** → Skills become Hive-aware, creating notes as byproducts. The skill framework itself doesn't change.
- **Sessions** → Sessions start with Hive context. Session close creates summary notes. The session system itself doesn't change.
- **Linear** → Linear issues appear as awareness records in the Hive. Linear continues to be the team's work tracking tool.

### Preserves
- **System architectures** → Content system, dispatch, code repos all keep their internal structures
- **Claude Code's native abilities** → Grep, file reads, codebase exploration all preserved. The Hive is the compass; Claude Code is the explorer.
- **Skills framework** → Skills remain the interface for everything. The Hive adds a new skill, doesn't change the framework.
- **OS Terminal** → The Hive UI evolves the OS Terminal React app. Terminal rendering (xterm.js), WebSocket relay, session state watching all preserved. The layout changes from session grid to Wall + Focus Area.
- **Git workflow** → The vault is version-controlled. Git history preserved.
