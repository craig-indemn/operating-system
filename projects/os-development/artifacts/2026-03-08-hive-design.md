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

1. **Everything is a typed record.** Every piece of information has a type with a defined schema. Types range from highly structured (person, company) to flexible (note, idea). New types are added via YAML configuration, not code changes.
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
Claude Code Session
    ↓
System Skills (/content, /dispatch, /market, /devops, etc.)
    ↓
System CLIs (content, dispatch, market-cli, etc.)
    ↓
Hive CLI (hive) — low-level note CRUD, search, context assembly
    ↓
Hive Data Layer (markdown vault + local MongoDB)
```

**Three layers:**
- **Hive Data Layer** — typed records in a structured vault (YAML for entities, markdown for knowledge) + local MongoDB index. Files are source of truth. MongoDB is derived.
- **Hive CLI** — Python tool for typed record CRUD, search, context assembly, sync, type/ontology management. Type-aware commands: `hive create <type>`, `hive <type> list`.
- **System Integration** — each system reports to the Hive through its own CLI. Sync adapters pull/push external system data. The `/hive` skill handles native operations.

---

## Data Model: Typed Records

Every object in the Hive is a **typed record** with a schema defined in the type registry. Types range from highly structured (person, company, meeting) to flexible (note, idea). The type determines what fields exist, what relationships are available, and where the record lives on disk.

### The Type System

Types are defined as YAML files in `.registry/types/`. Adding a new type is adding a YAML file — no code changes.

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
directory: people
format: yaml    # structured data, no prose needed
```

```yaml
# hive/.registry/types/design_document.yaml
type: design_document
fields:
  title: { type: string, required: true }
  project: { type: ref, target: project }
  status: { type: enum, values: [draft, in_review, approved] }
  domains: { type: list, required: true }
  tags: { type: list }
  content: { type: markdown }
display: title
directory: design_documents
format: markdown    # rich text, has prose body
```

```yaml
# hive/.registry/types/note.yaml
type: note
fields:
  title: { type: string, required: true }
  tags: { type: list, required: true }
  domains: { type: list, required: true }
  refs: { type: refmap }    # typed references to entities
  content: { type: markdown }
display: title
directory: notes
format: markdown
```

**Key properties of the type system:**
- `format: yaml` — structured entities, no prose body. Stored as `.yaml` files.
- `format: markdown` — knowledge records with rich text. Stored as `.md` files with YAML frontmatter.
- `ref` fields — typed relationships to other records (person → company, task → project)
- `refmap` — flexible typed references: `refs: { project: hive, people: [craig, cam] }`
- `required: true` — enforced by CLI on create/update
- `directory` — where files of this type live in the vault

### Initial Entity Types (Structured)

| Type | Directory | Key Fields | Format |
|------|-----------|-----------|--------|
| `person` | `people/` | name, email, role, company→Company | yaml |
| `company` | `companies/` | name, industry, relationship | yaml |
| `product` | `products/` | name, company→Company, status | yaml |
| `project` | `projects/` | name, status, domain, team→Person[] | yaml |
| `meeting` | `meetings/` | date, summary, attendees→Person[], company→Company | yaml |
| `brand` | `brands/` | name, voice, platforms | yaml |
| `platform` | `platforms/` | name, type, url | yaml |
| `channel` | `channels/` | name, platform→Platform, brand→Brand | yaml |

### System-Added Entity Types (via sync adapters)

| Type | Directory | Added By | Key Fields |
|------|-----------|---------|-----------|
| `linear_issue` | `linear/` | Linear sync | key, title, status, assignee→Person, team |
| `calendar_event` | `calendar/` | Calendar sync | start, end, location, attendees→Person[] |
| `email_thread` | `email/` | Email sync | subject, from→Person, status |
| `slack_message` | `slack/` | Slack sync | channel, from→Person, thread_id |
| `github_pr` | `github/` | GitHub sync | repo, number, status, author→Person |

### Knowledge Types (Flexible)

| Type | Directory | Key Fields | When Used |
|------|-----------|-----------|----------|
| `note` | `notes/` | title, tags, domains, refs | Quick thoughts, observations, fragments — the catch-all |
| `decision` | `decisions/` | title, rationale, alternatives, project→Project | A choice was made with reasoning |
| `design_document` | `design_documents/` | title, project→Project, status | Specs, designs, architecture docs |
| `implementation_plan` | `implementation_plans/` | title, project→Project, status, tasks | Breakdown of work to execute |
| `research` | `research/` | title, sources, urls | External information brought in |
| `session_summary` | `session_summaries/` | session_id, project→Project, accomplished, decisions | Created at session close |

### Awareness Records

Some records point to artifacts that live in external systems (code repos, content system, deployed services). These have two additional fields:

| Field | Purpose |
|-------|---------|
| `system:` | Which system owns the external artifact (content, dispatch, github, linear) |
| `ref:` | Pointer to where the actual artifact lives (file path, URL, commit hash) |

Any type can be an awareness record by having `system:` and `ref:` fields. A `linear_issue` always has these (it's synced from Linear). A `design_document` usually doesn't (it lives natively in the Hive). A `session_summary` has `ref:` pointing to the session transcript.

### Record Identity

- **ID** is the filename without extension (`.yaml` or `.md`)
- **Entity records:** descriptive slug (e.g., `craig`, `indemn`, `voice-agent`)
- **Knowledge records:** `YYYY-MM-DD-descriptive-slug` (e.g., `2026-03-08-hive-vision`)
- **Synced records:** `source-external-id` (e.g., `AI-123`, `PR-456`)
- Collisions on the same day: append `-2`, `-3`
- Claude Code generates slugs from content

### Typed References

Records reference other records via typed `ref` fields. These are first-class relationships, not generic links:

```yaml
# In a meeting record
attendees:
  - craig          # → people/craig.yaml
  - cam            # → people/cam.yaml
company: indemn    # → companies/indemn.yaml
```

```yaml
# In a design document (frontmatter)
project: hive           # → projects/hive.yaml
refs:
  people: [craig]       # → people/craig.yaml
  product: operating-system  # → products/operating-system.yaml
```

**Relationships are navigable in both directions.** If a meeting references Craig as an attendee, querying Craig's profile can show all his meetings. The MongoDB index handles reverse lookups.

### Links (Knowledge Layer)

In addition to typed references, knowledge records support Zettelkasten-style links for connecting ideas:

**Inline wiki-links** (in markdown content):
```markdown
This builds on [[2026-02-19-dispatch-system-design]] and addresses
the scoring gap from [[meeting-2026-03-01-oconnor-voice]].
```

**Three kinds of connections (all automatic):**
1. **Typed references** — explicit relationships defined by the type schema (person → company)
2. **Wiki-links** — inline connections between knowledge records
3. **Semantic links** — content similarity discovered via embeddings

The graph grows as a byproduct of working. Manual linking is rarely needed.

---

## The Registry

The registry is the Hive's self-knowledge — it defines what types exist, what tags mean, and what domains are valid. Every Claude Code session reads the registry before creating or querying records.

### Registry Structure

```
hive/.registry/
  ontology.yaml          # Tags, domains, statuses, priorities
  types/                 # Type definitions (one YAML per type)
    person.yaml
    company.yaml
    product.yaml
    project.yaml
    meeting.yaml
    brand.yaml
    platform.yaml
    channel.yaml
    note.yaml
    decision.yaml
    design_document.yaml
    implementation_plan.yaml
    research.yaml
    session_summary.yaml
    linear_issue.yaml    # Added by Linear sync adapter
    calendar_event.yaml  # Added by Calendar sync adapter
    email_thread.yaml    # Added by Email sync adapter
    slack_message.yaml   # Added by Slack sync adapter
    github_pr.yaml       # Added by GitHub sync adapter
```

### Type Definitions

Each type file defines the schema, relationships, and storage format. See "The Type System" section above for examples. Key fields in a type definition:

| Field | Purpose |
|-------|---------|
| `type` | The type name (used in CLI: `hive create <type>`) |
| `fields` | Schema — field names, types, required/optional, ref targets |
| `display` | Which field is shown as the label (name, title, subject) |
| `directory` | Where files of this type live in the vault |
| `format` | `yaml` (structured entities) or `markdown` (knowledge with prose) |

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

- **New types:** Added as YAML files in `.registry/types/`. The CLI auto-discovers them. System sync adapters add their own types when they integrate.
- **New tags:** Added deliberately to `ontology.yaml`. When a session needs a tag that doesn't exist, check if an existing tag covers the concept. If not, add it and mention it in the session summary.
- **New domains:** Added to `ontology.yaml` when Craig starts working in a new domain.
- **Principle:** Types define structure. Tags provide flexible subcategorization. Don't create a type when a tag would suffice. Create a type when the thing has a stable identity, structured fields, or typed relationships to other records.

---

## Storage Architecture

### Vault (Source of Truth)

```
hive/
  .registry/
    ontology.yaml                    # Tags, domains, statuses
    types/                           # Type definitions
      person.yaml
      company.yaml
      note.yaml
      decision.yaml
      ...
  .templates/                        # Example records for each type
  .attachments/                      # Binary files (images, PDFs)

  # Entity directories (structured, YAML)
  people/
    craig.yaml
    cam.yaml
    oconnor.yaml
  companies/
    indemn.yaml
    career-catalyst.yaml
  products/
    voice-agent.yaml
    operating-system.yaml
  projects/
    hive.yaml
    platform-dev.yaml
  meetings/
    2026-03-14-oconnor-voice.yaml
  brands/
    indemn-brand.yaml
    personal-brand.yaml
  platforms/
    substack.yaml
    linkedin.yaml
  channels/
    indemn-engineering-blog.yaml

  # Knowledge directories (flexible, Markdown)
  notes/
    2026-03-08-hive-vision.md
    2026-03-09-tile-breathing-idea.md
  decisions/
    2026-03-09-wall-user-driven.md
    2026-03-09-type-system-over-flat-notes.md
  design_documents/
    2026-03-08-hive-design.md
  implementation_plans/
    ...
  research/
    2026-03-04-gastown-findings.md
  session_summaries/
    2026-03-08-os-hive-session-1.md

  # System-synced directories (added by sync adapters)
  linear/
    AI-123.yaml
    DEVOPS-42.yaml
  calendar/
    2026-03-14-team-standup.yaml
  email/
    ...
  slack/
    ...
  github/
    indemn-platform-v2-PR-456.yaml
```

- **Typed directories** — each type's `directory` field determines where its records live
- **YAML for entities** — structured data, no prose. Clean, machine-readable, human-scannable.
- **Markdown for knowledge** — rich text with YAML frontmatter. Ideas, reasoning, specs.
- `hive/` lives in the operating-system repo, version-controlled by Git
- `hive/` is the Hive vault — visualized through the Hive UI, not Obsidian (entities are YAML, not Markdown)
- New type → new directory appears automatically

### MongoDB (Derived Index)

**Instance:** Local MongoDB Community Edition (via Homebrew). Private, zero cost, fast.

**Database:** `hive`

**Collection:** `records` (single collection with type discriminator — simpler than per-type collections, MongoDB handles polymorphic queries well)

```json
{
  "_id": ObjectId,
  "record_id": "craig",
  "type": "person",
  "title": "Craig",

  // Type-specific fields (vary by type)
  "name": "Craig",
  "email": "craig@indemn.ai",
  "role": "Technical Partner",
  "company": "indemn",            // typed ref → companies/indemn.yaml

  // Common fields
  "tags": ["engineering", "leadership"],
  "domains": ["indemn", "career-catalyst"],
  "status": "active",
  "system": null,                  // null = native, "linear" = synced
  "ref": null,                     // null = lives in Hive, path/url = external

  // Knowledge records also have:
  "content": "Full markdown content without frontmatter",
  "content_embedding": [/* vector from local embedding model */],

  // Relationships (extracted from typed refs for fast lookup)
  "refs_out": {
    "company": ["indemn"],
    "project": ["hive", "platform-dev"]
  },

  "file_path": "hive/people/craig.yaml",
  "created_at": ISODate,
  "updated_at": ISODate,
  "created_by": "session:os-hive-2026-03-08"
}
```

**Indexes:**
- `record_id`: unique
- `type`: regular (enables type-scoped queries)
- `tags`: multikey
- `domains`: multikey
- `status`: regular
- `system`: regular
- `refs_out.company`: multikey (reverse lookup — "all records referencing Indemn")
- `refs_out.project`: multikey
- `refs_out.people`: multikey (reverse lookup — "all records referencing Craig")
- `content_embedding`: regular array (cosine similarity in Python)
- Full-text index on `title` + `content`
- Compound: `{type: 1, status: 1}`, `{type: 1, domains: 1}`

**Supported queries:**
- **Type-scoped:** `{type: "person", domains: "indemn"}` — all Indemn people
- **Relationship traversal:** `{"refs_out.company": "indemn"}` — everything connected to Indemn
- **Reverse lookup:** `{"refs_out.people": "craig"}` — all Craig's meetings, tasks, projects
- **Semantic:** vector similarity on `content_embedding` (knowledge records only)
- **Filtered:** `{type: "decision", status: "active", domains: "indemn"}`
- **Keyword:** full-text search on `title` + `content`
- **Timeline:** `{type: "meeting", created_at: {$gte: last_week}}`
- **Cross-type:** `$graphLookup` for multi-hop traversal across types

**Note:** Atlas Vector Search is cloud-only. For local MongoDB, embeddings are stored as arrays and cosine similarity is computed in Python. At the scale of hundreds to low thousands of records, this is fast enough. If it becomes a bottleneck, add a dedicated vector store (ChromaDB, LanceDB) later.

### Embedding Model

- **Initial:** Local model via Ollama (e.g., `nomic-embed-text` or `mxbai-embed-large`)
- **Abstracted:** Behind a simple interface so the model is swappable
- Only knowledge records (markdown format) get embeddings — entity records are queried via structured fields
- Each record is embedded when created or updated during sync
- Re-embedding is possible when switching models (`hive sync --re-embed`)

---

## Context Assembly

The core value proposition. How a Claude Code session goes from "I want to work on X" to having full context without manual curation.

### What It Produces

Not just a briefing — a **session initialization instruction**:

```markdown
# Session Initialization: Voice Scoring UI

## Knowledge Context
- [[2026-03-05-voice-scoring-spec]] — weighted rubric architecture [NATIVE]
- [[2026-03-03-scoring-decision]] — decided React + Tailwind [NATIVE]
- Voice Scoring UI tracked as AI-123 in Linear [AWARENESS → linear]

## Skills You'll Need
- /linear — issue AI-123 is active. Update status as you progress.
- /github — target repo is indemn-platform-v2.
- /dispatch — implementation plan can be executed autonomously.
- /hive — log decisions and create awareness records as you work.

## Read First
- indemn-platform-v2/CLAUDE.md — codebase conventions
- indemn-platform-v2/src/components/evaluations/ — existing eval components

## Reminders
- Decision: weighted rubrics, not pass/fail (2026-03-03)
- O'Connor is waiting on scoring visibility
- Career Catalyst needs similar scoring — note reusable patterns
- Draft blog post exists about this feature — update if architecture changes
```

### Retrieval Algorithm

```
Input: query (string), objective (string), domain filter (optional)

1. Embed the query using local embedding model
2. Vector search: top 20 notes by cosine similarity
3. Apply domain filter if specified
4. Graph expansion: for each seed result, follow outgoing links 1-2 hops
5. Score all candidates:
   score = (semantic_similarity × 0.5) + (recency × 0.3) + (graph_proximity × 0.2)
6. Deduplicate and rank
7. Select top N (default: 10-15)
8. Pass results + objective + skill registry to LLM for briefing assembly
9. LLM produces tailored session initialization instruction
10. Return instruction as markdown
```

**Scoring weights are tunable** — initial values are guesses. Tuned through experience.

**Graph expansion depth** starts at 1-2 hops. Breadth is preferred over depth — something can't be explored unless it's known about.

### Briefing Assembly

The LLM that assembles the briefing has access to:
- The retrieved notes (native knowledge + awareness records)
- The stated objective (what the session is trying to accomplish)
- The ontology (`ontology.yaml` — what tags/systems/domains exist)
- The skill registry (what skills are available and what they do)

It produces a tailored instruction based on the objective:
- **Development session** → emphasizes specs, code refs, decisions, relevant PRs
- **Content session** → emphasizes narrative, source material, brand voice, draft status
- **Planning session** → emphasizes current state, open questions, related initiatives, people involved

The LLM call happens once at session startup. Latency is acceptable because it only runs once.

### Context During Work

Beyond startup, Claude Code can query the Hive on-demand with type-aware commands:

```bash
# Type-scoped queries (pre-filtered, fast)
hive people get craig                              # Craig's full profile
hive people get craig --meetings --since 2026-03   # Craig's recent meetings (relationship traversal)
hive companies get indemn --people --products      # Indemn with contacts and products
hive meetings --attendee oconnor --last 5          # O'Connor's recent meetings
hive decisions --project hive --since 2026-03-08   # Recent Hive decisions
hive tasks --status active --domain indemn         # Active Indemn tasks

# Semantic search (across all knowledge records)
hive search "rubric component"                     # Find related knowledge
hive search "deployment patterns" --domain career-catalyst  # Cross-domain discovery

# Direct record access
hive get 2026-03-01-rubric-component               # Read any record by ID (type auto-detected)

# Context assembly
hive context "voice scoring" --objective "build the scoring UI" --system code-development

# Create records (type-aware)
hive create person "O'Connor" --email oconnor@acme.com --company acme
hive create decision "Use typed records" --project hive --rationale "..."
hive create note "interesting tile pattern" --tags ui --domains indemn

# Feedback
hive feedback "context missed deployment patterns"
```

### Skill and System Awareness

Skills and systems are themselves represented as typed records in the Hive (entity type or knowledge type — to be determined during implementation). Context assembly can then connect: "voice scoring task → references Linear issue AI-123 → the `/linear` skill is relevant" via typed relationships and surface it in the session instruction.

---

## System Integration Model

### The Convention

Systems keep their own internal architectures. The Hive is additive — awareness and connections.

**When building a new system:**
1. Keep your domain-specific files, configs, and folder structure
2. Create awareness records in the Hive when significant events occur (created, started, completed, published, failed)
3. Register your domain-specific tags in `ontology.yaml`
4. Build Hive operations into your system CLI — don't make Claude Code use raw `hive note create`
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

Python CLI (Click or Typer). Same pattern as `bd` for beads. **Type-aware** — the CLI reads type definitions from `.registry/types/` and auto-generates commands for each type.

### Commands

```bash
# Setup
hive init                    # Create vault, .registry, start MongoDB, seed types and ontology

# Create records (type-aware — validates schema)
hive create person "Craig" --email craig@indemn.ai --company indemn --domains indemn
hive create company "Indemn" --industry insurance --domains indemn
hive create decision "Use typed records" --project hive --rationale "Enables structured queries"
hive create note "tile breathing idea" --tags ui,design --domains indemn
hive create design_document "Hive Design" --project hive --status draft

# Read records
hive get craig                                   # Auto-detects type from ID
hive get 2026-03-09-wall-user-driven             # Works for any type

# Type-scoped listing and querying
hive people list                                  # All people
hive people get craig --meetings --since 2026-03  # With relationship traversal
hive companies get indemn --people --products     # With related entities
hive decisions --project hive --since 2026-03-08  # Filtered by project and date
hive meetings --attendee oconnor --last 5         # Filtered by relationship
hive notes --tags brainstorming --domains indemn  # Flexible knowledge
hive linear_issues --status active --domain indemn # Synced external data

# Context assembly (the main command)
hive context "voice scoring"                                                    # Full session initialization
hive context "voice scoring" --domain indemn                                    # Scoped to a domain
hive context "voice scoring" --objective "build the scoring UI"                 # Tailored for purpose
hive context "voice scoring" --objective "build the scoring UI" --system code-development  # System-aware

# Search (semantic, across all knowledge records)
hive search "deployment patterns"                 # Semantic search
hive search "rubric" --tags spec --domain indemn  # Filtered semantic search

# Sync
hive sync                    # Index all vault files into MongoDB
hive sync <system>           # Sync external system (linear, calendar, email, slack, github)
hive sync --re-embed         # Re-generate all embeddings (when switching models)

# Registry management
hive types list              # Show all registered types
hive types show person       # Show person type schema
hive tags list               # Show all registered tags
hive tags add <tag> --category work --description "..."
hive domains list            # Show all domains
hive domains add <domain> --description "..."

# Feedback (self-improvement)
hive feedback "retrieval missed X"       # Auto-tagged, auto-linked to current session context

# Status
hive status                  # Overview: record counts by type and domain, recent activity
```

### Architecture

```
hive/                         # CLI package
  cli.py                      # Click/Typer CLI entry point
  records.py                  # Typed record CRUD operations
  types.py                    # Type registry — loads/validates type definitions
  context.py                  # Context assembly engine
  search.py                   # Search (semantic + structured)
  sync.py                     # Vault → MongoDB sync + external system sync adapters
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

How a session gets started from the Hive with the right context.

### The Flow

1. **Click a tile.** Session spawns immediately — terminal appears in Focus Area. No loading screen.
2. **First message sent via `tmux send-keys`.** Contains tile metadata only — note ID, title, tags, domain, system. Enough to orient the session, not full context. Includes instruction to ask for the objective before retrieving context.
3. **Session asks the objective.** "You're working on Voice Scoring. What are you trying to accomplish?"
4. **User responds** (via Wispr Flow): "Implement the scoring component."
5. **Context retrieves with full parameters.** The session runs `hive context` with topic + objective + system + domain. The objective shapes what's relevant — implementation context is different from brainstorming context is different from content extraction context.
6. **Session is hydrated.** Targeted context, relevant skills identified, recommended files to read. Work begins.

### Why Objective Comes First

Context retrieval needs context to be relevant. Without knowing the objective, you get everything about a topic — noisy and potentially fills the context window with irrelevant material. The objective determines what's relevant:

- "Brainstorm the architecture" → design docs, decisions, related patterns, constraints. Skills: brainstorming.
- "Implement the component" → specs, code patterns, repo structure, PRs. Skills: development workflow.
- "Write a blog about it" → linked notes with commentary, user-facing impact, decisions. Skills: content system.

Same topic, different objectives, completely different context.

### System Awareness

Each session operates within a system. The tile's metadata (tags, system field) tells the session what system it's in. The context assembly is parameterized by system — different systems prioritize different kinds of context.

The first message includes the system context:
```
User clicked Hive tile: "Voice Scoring UI"
(note_id: 2026-03-08-voice-scoring-spec, domain: indemn,
system: code-development, tags: [spec, voice, scoring],
status: active, linear: AI-123)

Ask the user what they're trying to accomplish, then use
hive context with their objective to retrieve relevant context.
```

System/workflow notes in the Hive describe what each system does and what skills it uses. Context assembly reads these to tailor retrieval per system.

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

The content system (`cs.py` state store, brand configs, extract→draft→refine→publish pipeline) creates awareness records at each meaningful stage:

| Event | Tags | Status | Ref |
|-------|------|--------|-----|
| Idea created | idea, content | ideating | — (native note, idea lives in Hive) |
| Extraction complete | extraction, content | active | `drafts/YYYY-MM-DD-slug/extraction.md` |
| Draft v1 created | draft, blog/newsletter | in-review | `drafts/YYYY-MM-DD-slug/draft-v1.md` |
| Latest draft updated | draft, blog/newsletter | in-review | `drafts/YYYY-MM-DD-slug/draft-v{N}.md` |
| Approved | draft, blog/newsletter | done | latest draft path |
| Published | published, blog/newsletter | done | published URL |
| Repurposed | published, linkedin/medium/etc | active→done | platform-specific path |

All records have `system: content` and links back to source material (the linked notes, the original feature, etc.).

### Session Manager Integration

| Event | Tags | Status | Ref |
|-------|------|--------|-----|
| Session closed | session-summary | done | `sessions/{uuid}.json` |

The awareness record captures: what was accomplished, what decisions were made, what artifacts were produced. Created by the `session close` command. Active session state stays in `sessions/*.json` (real-time, not Hive-appropriate).

### Code Development System Integration

The code development system will be designed and built separately as its own system (like the content system). When that design happens, it will define its specific Hive transitions following the generic contract above.

**Key insight from design discussion:** The design/brainstorming phase of code development generates **many native knowledge notes**, not just a single "design doc created" awareness record. The reasoning trail — questions explored, research findings, trade-off analyses, rejected approaches, thought experiments — is captured as individual linked notes throughout the design process. The skill/workflow driving the design phase creates these notes as a byproduct of doing its work, not as a separate manual step.

This principle applies to any system with creative or exploratory phases: **capture the reasoning trail, not just the outputs.** The retrieval system handles relevance — more captured knowledge is better, not noisier, because semantic search and graph traversal surface what matters for each specific context request.

The code development lifecycle spans: design/brainstorming → spec/design doc → implementation plan → parallel execution (beads) → validation/testing → deployment. Each phase will have defined Hive transitions. The design phase is notable for producing high volumes of native knowledge notes rather than just awareness records of completed artifacts.

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
**Question:** How does context assembly get injected into sessions? Hook? First skill invocation? Automatic?
**Options:** (a) SessionStart hook runs `hive context`, (b) `/hive` skill invoked as first action, (c) Session create command includes `--hive-context` flag.
**Leaning:** (b) — explicit skill invocation gives the session control over what context to request.
**Decide during:** Phase 2 implementation.

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
**Question:** Which model assembles the briefing? Local or API?
**Options:** (a) Claude via the session itself (the session runs `hive context`, which returns raw notes, and the session assembles them), (b) A separate local LLM call in the CLI, (c) Claude API call from the CLI.
**Leaning:** (a) — simplest. The `hive context` command returns ranked notes. The session (which is already Claude) assembles them into a briefing using the instruction template. No additional LLM call needed.
**Decide during:** Phase 2.

---

## Implementation Phases

### Phase 1: Foundation
**Goal:** The vault exists with the type system, typed records can be created and queried, the registry is seeded.

- [ ] Create `hive/` directory structure in the OS repo — `.registry/`, `.registry/types/`, `.templates/`, typed subdirectories
- [ ] Create initial type definitions in `.registry/types/` — person, company, product, project, meeting, brand, platform, channel, note, decision, design_document, implementation_plan, research, session_summary
- [ ] Create `hive/.registry/ontology.yaml` with initial tags, domains, statuses
- [ ] Install local MongoDB Community Edition (`brew install mongodb-community`)
- [ ] Build `hive` CLI core (Python, Click/Typer) with type-aware commands:
  - `hive init` — set up vault structure, create MongoDB database, seed indexes, load types
  - `hive create <type> <name/title>` — create a typed record (YAML or Markdown), validate against schema, write to vault, index into MongoDB
  - `hive get <id>` — read any record by ID (auto-detect type)
  - `hive <type> list` — type-scoped listing with filtering
  - `hive sync` — parse all vault files, extract fields, upsert into MongoDB
  - `hive types list` — display registered types
  - `hive types show <type>` — show type schema
  - `hive tags list` — display registered tags from ontology.yaml
  - `hive status` — count records by type and domain, show recent activity
- [ ] Build type registry loader (`types.py`) — reads YAML type definitions, validates schemas, auto-generates CLI commands
- [ ] Create the `/hive` skill (`.claude/skills/hive/SKILL.md`)
- [ ] Create initial entity records: people (Craig, Cam), companies (Indemn), products, projects, brands
- [ ] Migrate 5-10 existing artifacts as proof of concept (as typed knowledge records)
- [ ] Verify: can create typed records, type validation works, type-scoped queries work

**Exit criteria:** `hive create person`, `hive create decision`, `hive people list`, and `hive sync` work. Entity records and knowledge records coexist. Type validation enforces schemas.

### Phase 2: Context Engine
**Goal:** Sessions can hydrate context from the Hive. Semantic search works. Relationship traversal works.

- [ ] Install Ollama + embedding model locally
- [ ] Build embedding abstraction layer (`embed.py`)
- [ ] Add embedding generation to `hive sync` (embed content of markdown records, store vectors in MongoDB)
- [ ] Build `hive search` — semantic search via cosine similarity + type/tag/domain filters
- [ ] Build `hive context` — retrieval algorithm (semantic + typed relationships + recency) that returns ranked records
- [ ] Build relationship traversal — `hive people get craig --meetings` follows typed refs across types
- [ ] Create context instruction template (knowledge, entities, skills, reads, reminders sections)
- [ ] Integrate with session startup — update `/sessions` skill to recommend `hive context` at start
- [ ] Build `hive create <type> --from-file` — convert existing files to typed Hive records
- [ ] Migrate all 73 existing artifacts to Hive records (as appropriate types — design_documents, decisions, research, notes)
- [ ] Extract decisions from INDEX.md files into standalone decision records
- [ ] Test: start a session, run `hive context`, verify the briefing includes relevant entities and knowledge

**Exit criteria:** `hive context "voice evaluations"` returns a useful briefing with entity profiles, knowledge, skills, and reminders. `hive people get craig --meetings` traverses relationships. Semantic search finds related knowledge.

### Phase 3: External System Sync
**Goal:** The Hive connects to external systems. Bidirectional sync brings the outside world in and pushes actions back out.

**Note:** Sync adapters build on existing Claude Code skills — `/linear` (linearis), `/google-workspace` (gog), `/slack` (agent-slack), `/github` (gh). The adapters call these CLIs and map output to typed Hive records. Each adapter adds its own type definition to `.registry/types/`. Not building new integrations from scratch.

- [ ] Build sync adapter framework — common interface for inbound/outbound sync, dedup, incremental updates
- [ ] Build Linear sync adapter — pull issues as awareness records, push status changes back, bidirectional
- [ ] Build Google Calendar sync adapter — pull upcoming events as notes, status based on timing
- [ ] Build Gmail sync adapter — pull unread/flagged as notes, mark read/archive pushes back
- [ ] Build Slack sync adapter — pull unread mentions/DMs as notes, mark read pushes back
- [ ] Build GitHub sync adapter — pull open PRs/issues as awareness records, status from PR state
- [ ] Build `hive sync <system>` CLI commands for each adapter
- [ ] Implement scheduled sync (cron or background process) for continuous freshness
- [ ] Investigate webhook receivers for real-time sync where supported (Linear, GitHub, Slack)
- [ ] Create entity notes for Linear teams, key repos, key contacts
- [ ] Test: Linear issues, calendar events, unread emails, Slack mentions all appear as Wall-ready tiles

**Exit criteria:** External system data flows into the Hive as notes with correct status mapping. Changes pushed back to source systems. The Hive reflects the state of all connected systems.

### Phase 4: Workflow Integration
**Goal:** The Hive is woven into the daily workflow. Sessions create notes. OS systems report to the Hive.

- [ ] Update `/sessions` skill — session close creates a session-summary awareness record
- [ ] Update brainstorming skill — key ideas, decisions, and reasoning trail become Hive notes as a byproduct of the process
- [ ] Update project skill — `/project` queries Hive alongside/instead of INDEX.md
- [ ] Content system integration — content CLI creates awareness records at each pipeline stage (idea → extraction → draft → approved → published → repurposed)
- [ ] Dispatch integration — dispatch creates awareness records for task completion/failure
- [ ] Build `hive notes` listing/filtering commands
- [ ] Build `hive feedback` command — auto-tagged, auto-linked feedback notes for self-improvement
- [ ] Determine beads ↔ Hive relationship — mirror beads tasks as awareness records
- [ ] Update context assembly to surface cross-system connections
- [ ] Document the system integration convention (for future systems)
- [ ] Test: full workflow — brainstorm → spec → tasks → dispatch → completion, all tracked in Hive
- [ ] Test: context for a feature shows related Linear issues, PRs, content drafts, meetings

**Exit criteria:** A complete feature lifecycle is traceable through the Hive. Session summaries auto-create. Content and dispatch report to the Hive. Cross-system context assembly works.

### Phase 5: The Hive UI
**Goal:** The Hive is the home screen. Wall + Focus Area. Tiles. Session spawning with context.

- [ ] Evolve OS Terminal React app — replace session grid with Wall + Focus Area layout
- [ ] Build tile component — fluid sizing, progressive information disclosure, color/accent/brightness encoding
- [ ] Build Wall layout — tiles surrounding Focus Area, breathing with activity level, smart highlight reel in compressed mode
- [ ] Build Focus Area — equal-sized auto-grid of terminal panels (xterm.js, existing) + browser panels (iframe, new)
- [ ] Build Overview toggle — expand Wall to full screen, collapse back to Focus
- [ ] Add Hive API routes to Express backend — wrap Hive CLI with JSON output
- [ ] Add WebSocket Hive updates — push note changes to frontend (~30s polling + on-action)
- [ ] Build Wall ordering — priority → status → recency, drag-to-reorder within priority buckets
- [ ] Build domain filtering — click domain tile to filter Wall
- [ ] Build search tile — search input that queries `hive search`
- [ ] Build quick capture tile — input that creates notes, LLM auto-tags async
- [ ] Build "create linked note" interaction — one-click note creation linked to parent tile
- [ ] Build session spawning from tiles — click tile → `session create` → first message with tile metadata via `tmux send-keys`
- [ ] Build session initialization flow — objective question → targeted context retrieval → work begins
- [ ] Build direct tile actions — mark done, change priority, archive → outbound sync to external systems
- [ ] Merge session state tiles (from `sessions/*.json`) with Hive note tiles into unified Wall
- [ ] Color/visual mapping from `ontology.yaml` — system colors, domain accents, status brightness
- [ ] Responsive layout — ultra-wide (Wall + Focus coexist), smaller screens (Wall collapses)
- [ ] ~~Configure Obsidian vault~~ DROPPED — Hive UI is the visualization layer

**Exit criteria:** The Hive is the home screen. You see your world as tiles, click to start context-hydrated sessions, work in Focus panels, observe everything from the Wall. Direct tile actions sync back to external systems. The OS Terminal's session grid is fully replaced.

### Phase 6: Expansion
**Goal:** Platform integrations, multi-user, graph maturity.

- [ ] Substack, LinkedIn, X integration — content publishing and engagement tracking via sync adapters
- [ ] Multi-user — shared MongoDB or generated output views for CEO/teammates
- [ ] Graph quality management — archival conventions, stale note detection, pruning
- [ ] Automated ontology management — detect tag drift, suggest merges
- [ ] New system templates — streamline creating Hive-integrated systems
- [ ] Cross-domain discovery automation — proactively surface connections
- [ ] Morning consultation session type — daily planning with calendar, priorities, active work

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
1. **Create entity notes** for all 16 existing projects (one note per project, tagged `project`)
2. **Migrate artifacts** — add Hive frontmatter (tags, domains) to existing artifacts, copy or move to `hive/`, index into MongoDB. 73 artifacts total.
3. **Extract decisions** — pull decisions from INDEX.md files into standalone `decision` record notes
4. **Extract external resources** — create entity/reference notes for resources listed in INDEX.md
5. **Create awareness records** — for things that exist in other systems (Linear issues, active PRs, deployed features)
6. **Deprecate INDEX.md** — once context assembly reliably replaces INDEX.md, stop maintaining them. They remain as historical artifacts in Git.

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
| 2026-03-08 | Files are source of truth (for native records), MongoDB is derived | Git-trackable, human-readable. MongoDB rebuilt from files via `hive sync`. Synced records use external system as source of truth. |
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
| 2026-03-09 | Everything is a typed record — types defined in YAML, not code | Replaces "everything is a note." Types range from structured (person, company) to flexible (note, idea). New types added via YAML configuration. |
| 2026-03-09 | Type system is configuration-driven and extensible | Add a YAML file to `.registry/types/` → new type exists. CLI auto-discovers. No code changes needed. Scales to any domain. |
| 2026-03-09 | Entities are YAML, knowledge is Markdown | Structured entities (person, company) stored as `.yaml` — no prose needed. Knowledge (decisions, notes, designs) stored as `.md` — rich text with frontmatter. |
| 2026-03-09 | Typed references replace generic wiki-links for entity relationships | person → company, meeting → attendees are typed refs, not `[[wiki-links]]`. Wiki-links remain for knowledge-to-knowledge connections. |
| 2026-03-09 | Typed directories replace flat vault | Each type has a `directory` field. `people/`, `companies/`, `decisions/`, `notes/`. Clear, unambiguous, scalable. |
| 2026-03-09 | CLI is type-aware — `hive create <type>`, `hive <type> list` | Type-scoped commands enable structured queries and pre-filtering. Better than `hive search` for known types. |
| 2026-03-09 | Create a type when: stable identity AND (referenced from other types OR structured fields enable useful queries) | Principle for type vs tag distinction. Tags subcategorize within types. Types define schemas and relationships. |
| 2026-03-09 | Color=type (not system) in tile visual encoding | More specific and meaningful. Each type gets its own color in the registry. |
| 2026-03-09 | Synced records are git-ignored, live in `.synced/` directories | External sync data (Linear, calendar, email, Slack, GitHub) creates files in `hive/.synced/<system>/` which is gitignored. Native records (entities, knowledge) are git-tracked. Source of truth for synced data is the external system, rebuilt via `hive sync <system>`. |
| 2026-03-09 | Obsidian compatibility dropped — Hive UI replaces the need | Entity records are YAML (Obsidian can't render). The Hive UI is the visualization layer. No need to maintain Obsidian compatibility. |
| 2026-03-09 | Quick capture always creates a `note` first, reclassifies async | Zero friction capture. LLM determines if it should be promoted to a typed record (task, decision, etc.). If so, creates the typed record and archives the original note. Capture speed > classification accuracy. |
| 2026-03-09 | Bidirectional sync framework for external systems | Inbound: pull/push/scheduled adapters. Outbound: direct tile actions (simple) + session-based actions (complex). Each adapter defines its own status lifecycle mapping. |
| 2026-03-09 | Status is the Wall visibility control — no separate "show on wall" flag | Active items surface, done items fade, archived items hidden. Sync adapters set status based on external system state. |

---

## What This Replaces, Augments, and Preserves

### Replaces
- **INDEX.md as resume file** → Context assembly dynamically generates the equivalent from the graph
- **Manual context curation** → LLM-assembled session initialization instructions
- **Siloed project knowledge** → Unified, linked graph across all domains

### Augments
- **The project system** → Projects become entity notes. Artifacts become native knowledge notes. The structure evolves but the knowledge is preserved.
- **Skills** → Skills become Hive-aware, creating notes as byproducts. The skill framework itself doesn't change.
- **Sessions** → Sessions start with Hive context. Session close creates summary notes. The session system itself doesn't change.
- **Linear** → Linear issues appear as awareness records in the Hive. Linear continues to be the team's work tracking tool.

### Preserves
- **System architectures** → Content system, dispatch, code repos all keep their internal structures
- **Claude Code's native abilities** → Grep, file reads, codebase exploration all preserved. The Hive is the compass; Claude Code is the explorer.
- **Skills framework** → Skills remain the interface for everything. The Hive adds a new skill, doesn't change the framework.
- **OS Terminal** → The Hive UI evolves the OS Terminal React app. Terminal rendering (xterm.js), WebSocket relay, session state watching all preserved. The layout changes from session grid to Wall + Focus Area.
- **Git workflow** → The vault is version-controlled. Git history preserved.
