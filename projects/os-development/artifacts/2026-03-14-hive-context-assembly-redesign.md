---
ask: "Redesign context assembly for the typed record system — deep dive on retrieval architecture, entity/knowledge layering, and workflow state management"
created: 2026-03-14
workstream: os-development
session: 2026-03-14-b
sources:
  - type: session
    description: "Deep dive design session — context assembly architecture, data layer simplification, workflow entity pattern"
  - type: artifact
    ref: "projects/os-development/artifacts/2026-03-08-hive-design.md"
    name: "The Hive Design Document (being revised)"
---

# Hive Architecture Redesign: Context Assembly & Data Layer

This artifact captures the architectural shifts made in session 2026-03-14-b. These are significant changes to the Hive's data model, storage architecture, and context assembly system. The main design document (2026-03-08-hive-design.md) will need to be updated to reflect these changes once the full context assembly design is complete.

---

## The Core Reframe: Context Assembly Is a Task, Not an Algorithm

### What the design doc had

A 10-step fixed pipeline:

```
1. Embed the query
2. Vector search: top 20 notes by cosine similarity
3. Apply domain filter
4. Graph expansion: follow outgoing links 1-2 hops
5. Score: (semantic × 0.5) + (recency × 0.3) + (graph_proximity × 0.2)
6. Deduplicate and rank
7. Select top N
8. Pass results + objective + skill registry to LLM for briefing assembly
9. LLM produces tailored session initialization instruction
10. Return instruction as markdown
```

This algorithm was designed for flat notes. It treats everything as "embed and search" — no awareness of typed entities, structured relationships, or objective-dependent retrieval strategies.

### What we decided

Context assembly is an **LLM agent that uses the Hive CLI as its toolkit.** It's not a fixed pipeline — it's a task that an LLM performs, choosing different retrieval strategies based on the user's stated intent.

**Why this is better:**
- "I want to build the scoring UI" → the agent decides to pull product entities, check Linear issues, find recent sessions on this topic, look at code decisions
- "I want to write a blog about voice agents" → the agent decides to pull meeting notes with customer quotes, find existing content drafts, check the brand entity for voice guidelines
- "What's the status of everything?" → the agent pulls all active workflows, recent session summaries, pending Linear issues

Same Hive, completely different retrieval strategies. A fixed algorithm can't do this. An LLM reading intent and choosing tools can.

**This aligns with the OS philosophy:** Claude Code is expert at using CLIs. The Hive CLI provides rich, type-aware query capabilities. The context assembly agent is just another Claude Code session using a CLI — the pattern the entire OS is built on.

### How it works

1. Craig provides intent: "I want to build the scoring UI for voice evaluations, O'Connor has been asking about it"
2. A **dedicated, short-lived LLM call** (not the working session) reads this intent
3. The LLM has access to the Hive CLI and decides what to query:
   - `hive get voice-agent` — pull the product entity
   - `hive search "scoring" --entities-only` — find related entities
   - `hive search "voice scoring" --tags decision,design` — find relevant knowledge
   - `hive get voice-scoring-ui` — check workflow state if one exists
   - `hive search "O'Connor" --recent 30d` — recent mentions of O'Connor
   - `hive get oconnor` + `hive refs oconnor` — O'Connor's entity with all references
4. The LLM assembles a curated context document from the results
5. That context document is injected into the new working session

**The working session starts with context already assembled — zero retrieval overhead.**

### Why a separate step, not the session itself

If the working session does its own retrieval, it:
- Spends its own context window on retrieval queries and results
- Mixes retrieval work with actual task work
- Can't benefit from a pre-assembled, compressed briefing

A dedicated context assembly step:
- Runs in its own context, then discards it
- Can be aggressive with queries (pull a lot, filter down, summarize)
- Produces a compressed briefing that's efficient for the working session's context window
- Can be run asynchronously before the session even starts

---

## The Two-Layer Data Architecture

### The problem with the previous design

The previous design (session 2026-03-14-a) defined 14+ types — person, company, product, project, meeting, brand, platform, channel, note, decision, design_document, implementation_plan, research, session_summary — all with YAML schema definitions in `.registry/types/`. Every type had:
- A YAML schema file defining fields
- A directory in the vault (`people/`, `companies/`, `decisions/`, etc.)
- Either a YAML file (entities) or Markdown file (knowledge) on disk
- A corresponding document in MongoDB (derived from the file)

This created several problems:
1. **File↔database sync complexity** — every record exists in two places (file + MongoDB). Keeping them in sync is an entire class of bugs.
2. **Entity files nobody would open** — `people/craig.yaml` is a structured data file. You'd never open it in a text editor. You'd use the CLI or UI. So why is it a file?
3. **Knowledge type proliferation** — does a `decision` really need a different type schema from a `note` tagged `decision`? The context assembly agent finds decisions through semantic search and tag filtering, not through type-specific queries.
4. **Over-engineering** — 14+ type schemas, auto-generated CLI commands per type, typed directories — a lot of machinery for what the context assembly agent actually needs.

### What we decided: two layers

**Layer 1: Entities (MongoDB only)**

Entities are structured records that live exclusively in MongoDB. They have schemas defined in the type registry. They are the deterministic entry points for context assembly — things the agent can query by name, structured fields, and typed relationships.

Entity types include: `person`, `company`, `project`, `product`, `workflow`, `meeting`, `brand`, `platform`, `channel`. Sync-added types: `linear_issue`, `calendar_event`, `email_thread`, `slack_message`, `github_pr`.

Entities are:
- Created and queried via the Hive CLI
- Stored only in MongoDB (not as files)
- Not git-tracked (backed up via MongoDB dumps)
- Connected to each other via typed references (person → company, workflow → project)

**Layer 2: Knowledge (Markdown files, git-tracked)**

Knowledge records are prose with YAML frontmatter. They live as markdown files in the `hive/` directory, version-controlled by Git. MongoDB indexes them (derived) for semantic search and structured queries.

Knowledge records are differentiated by **tags, not separate type schemas:**
- A decision is a note tagged `decision` with a `rationale` field in frontmatter
- A design document is a note tagged `design` with a `status` field
- A session summary is a note tagged `session_summary` with `accomplished` and `next_steps` fields
- A research note is a note tagged `research` with `sources` and `urls` fields

Knowledge records:
- Reference entities via `refs:` in frontmatter (e.g., `refs: {project: hive, people: [craig]}`)
- Link to other knowledge records via `[[wiki-links]]` in content
- Are embedded for semantic search (vectors stored in MongoDB)
- Are the substance of the Hive — ideas, reasoning, decisions, observations

### Why this split works

**Entities are anchors.** The context assembly agent needs to find them reliably and traverse through them. "Get Craig → his company → their products → related meetings" is a structured traversal that requires typed schemas and relationships. This justifies the schema overhead.

**Knowledge is discovered.** The agent finds knowledge through search (semantic, keyword, tag-based) and by traversing from entity anchors. A decision doesn't need its own type schema for the agent to find it — it needs to be well-tagged, well-referenced, and well-written. The tag `decision` plus refs to relevant entities is sufficient.

**The principle:** If the context assembly agent needs to find it by structured query as a starting point → entity type with schema. If it's discovered through traversal or search from those starting points → knowledge record (markdown note with tags and refs).

### What this eliminates

- YAML entity files (people/craig.yaml, companies/indemn.yaml) — gone
- File↔database sync for entities — entities only live in MongoDB
- Type schema definitions for knowledge records — tags replace types
- Auto-generated CLI commands per knowledge type — knowledge uses generic note commands
- 14+ type directories — replaced by a simpler knowledge directory structure

### What this preserves

- Type registry for entity schemas — still needed, still YAML definitions in `.registry/types/`
- Ontology (tags, domains, statuses) — still in `.registry/ontology.yaml`
- MongoDB as query layer — still used for both entities and knowledge indexing
- Embeddings for semantic search — still generated for knowledge records
- Typed references between entities — still the backbone of relationship traversal
- Knowledge records referencing entities — the connection between the two layers

---

## The Workflow Entity

### The problem

Long-running work (building a feature, writing a series of blog posts, onboarding a new customer) spans multiple Claude Code sessions. Each session needs to know where the work stands. Previously, INDEX.md served this role — manually maintained, frequently stale.

### What we decided

A `workflow` is a typed entity in MongoDB with structured fields:

- `name` — descriptive identifier (e.g., "voice-scoring-ui")
- `objective` — what the workflow is trying to accomplish
- `status` — active, paused, completed
- `current_context` — a summary of where things stand, updated at the end of each session
- `sessions` — ordered list of session IDs that have worked on this workflow
- `project` — typed ref to the parent project entity
- `artifacts` — list of knowledge record IDs created during the workflow

**How it works in practice:**

1. Craig says "I want to build the voice scoring UI"
2. Context assembly agent checks if a workflow exists for this → finds `voice-scoring-ui`
3. Reads `current_context`: "Session 3 completed the React component. Remaining: wire to API, write tests. O'Connor demo scheduled for Friday."
4. Follows refs to recent session summaries and decisions linked to the workflow
5. Assembles context for the new session

At session end, the workflow's `current_context` gets updated with what was accomplished and what's next. The next session reads one record to know the full state — no chain traversal needed.

**This is INDEX.md as a typed entity that updates itself.** The context assembly agent reads it, and workflow-aware sessions update it.

### Why a typed entity, not a tagged note

A workflow passes the entity test: the context assembly agent needs to find it by name ("get the voice-scoring workflow"), it has structured fields that enable useful queries ("all active workflows", "workflows for project X"), and other records reference it (session summaries ref the workflow they belong to).

A tagged note could work, but traversal becomes expensive — to understand "where are we on voice scoring?", the agent would need to find all notes tagged with the workflow, determine their ordering, and reconstruct state. The entity with `current_context` provides that in one read.

---

## Vault Structure (Revised)

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

**Key changes from previous design:**
- No entity directories (people/, companies/, etc.) — entities are MongoDB-only
- Knowledge directories organized by convention (tag-based), not enforced type schemas
- `.registry/types/` only contains entity type definitions
- Knowledge records all follow the same format: markdown with YAML frontmatter

### Knowledge Record Format

All knowledge records use the same structure regardless of tag:

```markdown
---
title: "Use typed records instead of flat notes"
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

# Use typed records instead of flat notes

The Hive needs structured entry points for context assembly to work reliably...

This builds on [[2026-03-08-hive-vision]] and addresses the retrieval
challenges identified in [[2026-03-09-context-assembly-gaps]].
```

**Notes:**
- `tags` determine the "kind" of knowledge (decision, design, research, session_summary, feedback, etc.)
- `refs` connect to entities in MongoDB (resolved by the CLI/agent)
- `[[wiki-links]]` connect to other knowledge records
- Additional frontmatter fields are convention-based per tag (decisions have `rationale` and `alternatives`, session summaries have `accomplished` and `next_steps`, etc.)
- No schema validation on knowledge records — the frontmatter is flexible

### MongoDB Schema (Revised)

**Entity documents** (source of truth):
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

**Knowledge documents** (derived from files — indexed for search):
```json
{
  "_id": ObjectId,
  "record_id": "2026-03-14-entities-mongodb-only",
  "type": "knowledge",
  "title": "Use typed records instead of flat notes",
  "tags": ["decision", "architecture"],
  "domains": ["indemn"],
  "status": "active",
  "refs_out": {
    "project": ["hive"],
    "people": ["craig"]
  },
  "wiki_links": ["2026-03-08-hive-vision", "2026-03-09-context-assembly-gaps"],
  "content": "Full markdown content without frontmatter...",
  "content_embedding": [/* vector */],
  "file_path": "hive/decisions/2026-03-14-entities-mongodb-only.md",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

**Workflow documents** (entity — source of truth in MongoDB):
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

**Key indexes remain the same:** record_id (unique), type, tags (multikey), domains (multikey), status, refs_out.company, refs_out.project, refs_out.people, content_embedding, full-text on title + content, compound {type, status}, {type, domains}.

---

## Context Assembly Agent: Two Sources, Not Five

### The simplification

The Hive's sync framework pulls data from Linear, Slack, Calendar, GitHub, Email into the Hive as synced records. This means the context assembly agent does NOT need to query five different external tools. If Linear data is stale, that's a sync frequency problem, not a context assembly problem.

**The agent has exactly two sources:**

1. **The Hive** — entities, knowledge, relationships, workflow state, AND all synced external data (Linear issues, Slack messages, calendar events, GitHub PRs). One system that has everything about Craig's world.

2. **The codebase** — when the task involves code. Code is too large, too dynamic, and too detailed to sync into the Hive. The agent needs to actually read files and grep. The Hive might know "session 3 implemented the React component" but it doesn't know the current state of `src/components/scoring/`.

**Not the agent's job:** Web search, documentation lookup, API references. Those are the working session's concern during actual work. Context assembly gives you YOUR context — your knowledge, your entities, your codebase state.

### How the agent knows which codebase

The agent doesn't need an explicit `repo` field on project entities. Instead:

- **Existing workflows carry it naturally.** Session summaries and decisions mention repos and file paths as a byproduct of working. The agent reads recent session summaries for the workflow and extracts repo information.
- **For brand new workflows** (no history yet), the agent reads the OS `CLAUDE.md` which has the full service inventory with repo paths.
- **The OS already manages repo access** — sessions are created with `--add-dir` for external repos. The context assembly agent's output can specify which repos the working session needs.

No field to maintain, no duplication with CLAUDE.md. The workflow accumulates operational context naturally.

---

## Context Assembly Agent: Implementation Mechanism

### How it runs

The context assembly agent is a **Claude Code session** created via the existing session CLI. Not an Agent SDK call, not a direct Anthropic API call. It uses the same infrastructure that manages all sessions in the OS.

**The flow:**

1. Craig interacts with the Hive UI — clicks a tile, provides intent
2. The Hive UI spawns a **short-lived context assembly session** via the session CLI (`session create`)
3. That session has: the Hive CLI, access to CLAUDE.md, access to the relevant codebase
4. The session queries the Hive, explores the codebase if relevant, and **writes the assembled context as a knowledge note** (persisted in the Hive, linked to the workflow)
5. The context assembly session terminates
6. The Hive UI spawns the **working session** via the session CLI, hydrated with that context note

**Why a session, not Agent SDK or direct API:** The OS's pattern is "everything is a session." The session manager creates sessions, tracks their state, manages their lifecycle. Context assembly is just another session with a specific job. This uses existing infrastructure — session CLI, tmux, worktrees, hooks — rather than inventing a new mechanism.

**Why not the working session itself:** If the working session does its own retrieval, it spends its own context window on retrieval queries and results, mixes retrieval work with actual task work, and can't benefit from a pre-assembled, compressed briefing. A dedicated step runs in its own context, can be aggressive with queries, and produces a compressed output efficient for the working session.

---

## The Hive CLI: Final Command Surface

### Design principles

- **Unified commands** — entity/knowledge distinction is hidden from the user. The system routes transparently based on whether the argument is a registered entity type or a knowledge tag.
- **Entity types and knowledge tags are disjoint sets.** If `meeting` is an entity type, it cannot also be a tag on knowledge records. The ontology enforces this. This eliminates routing ambiguity.
- **Layer indicators in output.** Every response shows `[entity:person]` or `[knowledge:decision]` so the user always knows which layer answered, even though they didn't have to specify.
- **Auto-detect output format.** JSON when piped (no tty), text when interactive (tty detected). Follows the `gh` CLI pattern. The context assembly agent pipes output → gets JSON automatically.
- **Verb-first grammar.** `hive get`, `hive create`, `hive search` — reads naturally for both LLMs and voice. Not `hive person get`.

### Command reference

```
hive context <query>                     # THE main command — context assembly
    --objective "..."                    # What the session is trying to accomplish
    --domain <domain>                    # Scope to domain
    --depth <1-3>                        # Graph traversal depth (default: 2)
    --budget <tokens>                    # Max context budget (default: 8000)
    --format json|md                     # Output format (default: md)

hive get <id>                            # Get any record by ID
    --fields field1,field2               # Select specific fields (reduces output)
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

**14 commands total.** Enough to be powerful, few enough to be learnable.

### Routing rules

| Input | Resolution |
|-------|-----------|
| `hive create person "Craig"` | `person` is in `.registry/types/` → entity → MongoDB |
| `hive create decision "Use X"` | `decision` is not a type, is a known tag → knowledge → markdown file + index |
| `hive create note "Quick thought"` | `note` is always knowledge (the default tag). There is no `note` entity type. |
| `hive list person` | `person` is a type → entity list from MongoDB |
| `hive list decision` | `decision` is a tag → knowledge list filtered by tag |
| `hive get craig` | Queries both layers by record_id, entity first. Returns first match with layer indicator. |
| `hive get 2026-03-14-scoring-spec` | Date-prefixed → likely knowledge. Queries both, returns match. |

### Commands deliberately excluded

- **`hive workflow get/update/complete`** — Covered by generic `hive get`, `hive update`, `hive update --status completed`. Workflow patterns documented in the skill, not special-cased in the CLI.
- **`hive feedback`** — It's `hive create note "..." --tags feedback`. No separate command.
- **`hive tags add` / `hive domains add`** — Edit `ontology.yaml` directly. Infrequent operations that don't need CLI commands.

### Context assembly agent workflow (concrete scenario)

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

---

## Reconciled Session Initialization Flow

The design doc (lines 886-924) describes the working session asking for the objective and doing its own context retrieval. We've replaced that with a dedicated context assembly session. Here's the reconciled flow:

### From a tile (existing work)

1. Craig clicks a tile on the Wall. The tile has metadata: record ID, tags, domain, system.
2. The Hive UI shows a lightweight prompt: "What are you trying to accomplish?" Craig speaks via Wispr Flow.
3. The Hive UI spawns a **context assembly session** via the session CLI. First message includes: tile metadata + Craig's stated objective.
4. The context assembly session reads the relevant **system's context assembly instructions** (from the system's skill — see below). It queries the Hive and codebase following those instructions.
5. The context assembly session writes a comprehensive context note linked to the workflow, then terminates.
6. The Hive UI spawns the **working session** via the session CLI. First message via tmux send-keys includes the context note content. The session knows the objective, the system, and has full context. No "what are you trying to accomplish?" — it already knows.
7. Work begins immediately. The working session is prompted to do its own due diligence (verify codebase state, explore further as needed).

### From scratch (new work)

1. Craig uses quick capture or tells the Hive "I want to build a new pricing engine."
2. The Hive UI prompts for objective (or the statement IS the objective).
3. Context assembly session runs — finds no existing workflow, searches for related entities and knowledge, checks CLAUDE.md for repo context.
4. The system that owns this type of work (code development, content, research) creates the workflow entity as part of its initialization.
5. Context note written, working session spawned with context.

### The system field determines the playbook

The tile's `system:` field (or Craig's stated intent for new work) tells the context assembly session which system's workflow it's assembling context for. A tile tagged `system: content` means follow the content system's context instructions. `system: code-development` means follow the code dev system's instructions.

---

## System-Specific Context Assembly

### Each system defines its own context playbook

The context note format is NOT a generic Hive-level template. Each system defines what context matters for its workflow via a dedicated section in the system's skill.

**The pattern:**
- The Hive provides the infrastructure (CLI commands, entity/knowledge layers, search)
- Each system's skill describes what context to gather and how to structure it
- The context assembly session is generic — it reads the system's instructions and follows them
- New systems define their own context needs; the context assembly session adapts automatically

**Example: code development system's context instructions might specify:**
- Pull the workflow entity and its current_context
- Find all decisions and design docs linked to the project
- Check Linear for related issues
- Assess codebase state: read key files, check recent git commits, find test coverage
- Include: design decisions with full rationale, implementation state, repo structure, relevant Linear issues, what to verify before acting

**Example: content system's context instructions might specify:**
- Pull the workflow entity and pipeline state (extraction, draft, review)
- Find brand entity for voice and style guidelines
- Pull source material: linked notes with commentary, meeting quotes, related features
- Check existing draft versions
- Include: brand voice, source material inventory, extraction progress, publishing targets, draft history

### Comprehensive, not compressed

The context note should be thorough. More context is better — by the time context assembly runs, we've already read the registry, the workflow entity, the related knowledge. Pour all of it in. The working session has a large context window. A 20k-token comprehensive briefing is a fraction of the window and leaves plenty of room for actual work.

The context note should also:
- Include full decision text with rationale (not one-line summaries)
- Include full entity profiles for relevant people and companies
- Reference Hive record IDs throughout so the session can `hive get` for deeper exploration
- Explicitly prompt the working session to do its own due diligence — verify codebase state, read files, explore before acting

---

## Workflow Lifecycle

### Systems own workflows, not the Hive

The `workflow` entity type exists in the Hive, but workflow lifecycle (creation, updates, transitions, completion) is managed by the system that owns the work. This follows the existing system integration framework: "System CLIs own their Hive updates."

- **The content system** creates a workflow entity when a content piece begins, updates it as the pipeline progresses (extraction → draft → review → publish), marks it complete when published.
- **The code development system** creates a workflow entity when a feature begins, updates it as sessions progress, marks it complete when deployed.
- **The research system** (future) creates a workflow entity when a research project begins, updates as findings accumulate.

The Hive stores the workflow entity. The context assembly agent reads it. But the system's CLI creates and updates it as part of its own domain logic. The Hive doesn't know or care about what transitions exist — it just stores the record.

### The context assembly agent READS workflows, never creates or updates them

The context assembly session queries `hive get <workflow-id>` and reads the `current_context` field. It does not create workflows for new work — that's the system's job. If Craig starts new work and no workflow exists, the working session (operating within a system) creates one as part of the system's initialization flow.

---

## Resolved Questions (No Longer Gaps)

### Context window budgeting — NOT A PROBLEM
The context note should be comprehensive. A 20k-token briefing is a fraction of Claude's context window. The context assembly session is an LLM that naturally produces coherent, non-redundant output. No explicit budgeting mechanism needed.

### Entity aliasing / fuzzy matching — HANDLED BY LLM + SEMANTIC SEARCH
When Craig says "voice scoring" or "VS," the context assembly session runs `hive search "voice scoring"`, gets results across both layers, and the LLM connects the dots. No alias registry needed. The LLM IS the fuzzy matcher. If this ever becomes a problem, `hive feedback` captures the miss and aliases can be added to entity schemas later.

### Cross-type queries — HANDLED BY LLM + CLI TOOLKIT
"Find the person who works on voice scoring" — the agent runs `hive search` across both layers and `hive refs voice-agent --types person`. The LLM combines results and reasons across types naturally. Not a design gap.

### Mobile experience — DEFERRED
Designed when the desktop Hive UI is built. The OS Terminal already has single-pane mode for ≤1024px. Mobile design builds on that foundation.

---

## Design Doc Reconciliation

The main design document (2026-03-08-hive-design.md) has these outdated sections that need rewriting:

### Must rewrite for architectural changes
- **Principle 1** — "everything is a typed record" → two-layer model (entities in MongoDB, knowledge as files)
- **Architecture Overview** (lines 37-57) — data layer description needs updating
- **Data Model: Typed Records** (lines 60-213) — major rewrite for two-layer architecture, entity schemas only in registry, knowledge differentiated by tags not types
- **Storage Architecture** (lines 314-469) — no entity directories, no YAML entity files, revised vault structure, revised MongoDB schema (entities are source of truth)
- **Context Assembly** (lines 472-577) — complete rewrite from fixed algorithm to LLM agent with system-specific playbooks
- **The Hive CLI** (lines 653-727) — 14-command unified surface replaces type-scoped commands
- **Session Initialization** (lines 886-924) — reconcile with dedicated context assembly session flow
- **Open Decisions** (lines 1058-1115) — #4 (Session Lifecycle) and #10 (Context Assembly LLM) now resolved
- **Implementation Phases** (lines 1118-1237) — restructure for new architecture

### Still valid, no changes needed
- **Vision** (lines 17-23)
- **Principles 2-7** (lines 28-33)
- **Registry** (lines 216-309) — ontology.yaml still valid, type definitions scoped to entities only
- **System Integration Model** (lines 580-650) — the convention and contract unchanged
- **The Hive UI** (lines 731-883) — Wall + Focus Area, tiles, visual encoding all valid
- **Session Initialization concept** (lines 886-924) — the "doctor appointment" metaphor valid, flow details change
- **The Flywheel** (lines 928-959) — linked notes, no hard-coded pipelines, unchanged
- **System Integration Framework** (lines 963-1055) — the contract, content/dispatch/session examples all valid
- **External System Sync Framework** (lines 1010-1055) — bidirectional sync, status lifecycle, unchanged
- **Self-Improvement** (lines 1291-1323) — hive feedback as notes, unchanged
- **Migration Strategy** (lines 1240-1264) — gradual coexistence, unchanged
- **Maintenance** (lines 1267-1290) — daily/weekly/monthly, unchanged
