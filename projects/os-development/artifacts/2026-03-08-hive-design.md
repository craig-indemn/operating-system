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

1. **Everything is a note.** One universal format. Tags and metadata differentiate behavior. No type hierarchy.
2. **The Hive is connective tissue, not a replacement.** Systems keep their own architectures. The Hive connects and indexes them.
3. **Context is assembled, not curated.** An LLM produces tailored session initialization instructions from the graph. No manual INDEX.md maintenance.
4. **The ontology is the contract.** A controlled vocabulary (tag registry) ensures consistency across all sessions and systems. It evolves deliberately.
5. **Simple foundations, infinite growth.** The data model is minimal. Complexity lives in the connections, not the schema. New systems plug in without changing the core.
6. **The system runs itself.** Everything is done through Claude Code sessions. The Hive is designed for LLM consumption first, human visualization second.

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
- **Hive Data Layer** — flat markdown vault + local MongoDB index. Source of truth is markdown. MongoDB is derived.
- **Hive CLI** — Python tool for note CRUD, search, context assembly, sync, ontology management.
- **System Integration** — each system reports to the Hive through its own CLI. The `/hive` skill handles native knowledge operations.

---

## The Note

Every object in the Hive is a note — a markdown file with YAML frontmatter.

### Minimum Schema

```yaml
---
tags: [idea, voice, scoring]
domains: [indemn]
---

# Voice Scoring Architecture

Content here. Links to other notes via [[note-id]].
```

Three required fields: `tags`, `domains`, and a `# Title` heading. Everything else is optional metadata that determines behavior.

### Behavioral Metadata

Notes gain capabilities through optional fields:

| Field | What it enables |
|-------|----------------|
| `status:` | Makes the note trackable — appears on kanban (backlog, ideating, active, in-review, done, archived) |
| `assignee:` | Makes the note owned — filterable by person |
| `priority:` | Makes the note prioritizable (low, medium, high, critical) |
| `linear:` | Syncs with a Linear issue (e.g., `AI-123`) |
| `date:` | Temporal anchor (for meetings, events, decisions) |
| `attendees:` | Meeting participants |
| `rationale:` | Why a decision was made |
| `brand:` | Content brand association |
| `platform:` | Publishing platform (substack, medium, youtube) |
| `published_at:` | When content was published |
| `url:` | External resource link |
| `email:`, `role:` | Person metadata |
| `repo:` | Codebase repository path or URL |
| `system:` | Which system created/manages this note |
| `ref:` | Pointer to where the actual artifact lives (for awareness records) |

### Two Kinds of Notes

| | Native Knowledge | Awareness Records |
|--|--|--|
| **What** | Ideas, specs, designs, decisions, research, brainstorming | Index entries for system-managed artifacts |
| **Content** | Full — the note IS the artifact | Lightweight — what happened, where it lives, what it's connected to |
| **Where the real thing lives** | In the Hive vault | In the system (content repo, code repo, service) |
| **Has `ref:` field** | No | Yes — points to the actual artifact's location |
| **Has `system:` field** | Sometimes | Always |
| **Examples** | Design spec, architecture decision, research findings, brainstorming output | "Draft created", "Feature deployed", "PR merged", "Blog published" |

### Note Identity

- **Hive-native notes:** `YYYY-MM-DD-descriptive-slug` (e.g., `2026-03-08-voice-scoring-spec`)
- **External-source notes:** `source-external-id` (e.g., `linear-DEVOPS-42`, `meeting-2026-03-01-oconnor`)
- ID is the filename without `.md`
- Date prefix is creation date, provides temporal ordering
- Collisions on the same day: append `-2`, `-3`
- Claude Code generates slugs from content

### Links

Two mechanisms, both auto-indexed into MongoDB:

**Inline wiki-links** (Zettelkasten-style, in content):
```markdown
This builds on [[2026-02-19-dispatch-system-design]] and addresses
the scoring gap from [[meeting-2026-03-01-oconnor-voice]].
```

**Frontmatter links** (structured, for explicit connections):
```yaml
links:
  - 2026-03-07-voice-evaluations
  - linear-AI-123
```

**Three kinds of connections (all automatic):**
1. **Workflow links** — system creates them based on lineage (plan created from spec → linked)
2. **Contextual links** — shared session, domain, tags → automatically connected
3. **Semantic links** — content similarity discovered via embeddings

Manual linking is rarely needed. The graph grows as a byproduct of working.

---

## The Ontology

A controlled vocabulary defined in `hive/.registry/ontology.yaml`. Every Claude Code session reads this before creating notes.

### Tag Categories

| Category | Tags | Purpose |
|----------|------|---------|
| Knowledge | `idea`, `spec`, `plan`, `design`, `research`, `reference` | Core knowledge graph nodes |
| Work | `task`, `epic`, `feature`, `initiative` | Trackable items — kanban-visible when they have `status:` |
| Record | `meeting`, `decision`, `session-summary`, `event` | Point-in-time captures |
| Output | `blog`, `newsletter`, `report`, `video`, `presentation` | Produced deliverables |
| Structural | `domain`, `project`, `person`, `system`, `codebase`, `brand` | Long-lived reference nodes |
| Source | `external` | Content from external sources (articles, websites, papers) |

### Registry Format

```yaml
# hive/.registry/ontology.yaml

tags:
  idea:
    description: "A seed thought, not yet developed"
    category: knowledge
  spec:
    description: "A design specification for something to be built"
    category: knowledge
    expected_fields: [status]
  task:
    description: "A specific piece of actionable work"
    category: work
    expected_fields: [status, assignee, priority]
  meeting:
    description: "A meeting that occurred"
    category: record
    expected_fields: [date, attendees]
  # ... (full registry in implementation)

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

### Ontology Evolution

- New tags are added deliberately, never silently invented
- When a session needs a tag that doesn't exist: check if an existing tag covers the concept. If not, create the note with a proposed new tag, add it to `ontology.yaml` with description and category, and mention it in the session summary.
- Systems register their own domain-specific tags when they integrate with the Hive

---

## Storage Architecture

### Vault (Source of Truth)

```
hive/
  2026-03-08-voice-scoring-spec.md
  2026-02-19-dispatch-system-design.md
  linear-DEVOPS-42.md
  meeting-2026-03-01-oconnor-voice.md
  entity-indemn.md
  entity-craig.md
  .registry/
    ontology.yaml
  .attachments/
    (binary files — images, PDFs, etc.)
  .templates/
    (example notes for common patterns)
```

- All notes flat in `hive/`
- `hive/` is an Obsidian vault — point Obsidian here for graph visualization
- `hive/` lives in the operating-system repo, version-controlled by Git
- `.registry/` contains the ontology and any future configuration
- `.attachments/` for binary files referenced by notes
- `.templates/` for example notes (guidance for Claude Code, not enforced)

### MongoDB (Derived Index)

**Instance:** Local MongoDB Community Edition (via Homebrew). Private, zero cost, fast.

**Database:** `hive`

**Collection:** `notes`

```json
{
  "_id": ObjectId,
  "note_id": "2026-03-08-scoring-ui-spec",
  "title": "Voice Scoring UI Specification",
  "tags": ["spec", "voice", "scoring"],
  "domains": ["indemn"],
  "status": "active",
  "system": "content",
  "ref": null,

  "content": "Full markdown content without frontmatter",
  "content_embedding": [/* vector from local embedding model */],

  "links": ["2026-03-07-voice-evaluations", "2026-03-01-rubric-component"],

  "source": {
    "origin": "session",
    "ref": "os-hive-2026-03-08"
  },

  "external_refs": {
    "linear": "AI-123",
    "github_pr": "indemn-ai/indemn-platform-v2#456"
  },

  "file_path": "hive/2026-03-08-scoring-ui-spec.md",

  "created_at": ISODate,
  "updated_at": ISODate,
  "created_by": "session:os-hive-2026-03-08"
}
```

**Indexes:**
- `note_id`: unique
- `tags`: multikey
- `domains`: multikey
- `status`: regular
- `system`: regular
- `links`: multikey (for graph traversal — forward and reverse lookups)
- `external_refs.linear`: sparse
- `content_embedding`: regular array (cosine similarity computed in application code)
- Full-text index on `title` + `content`

**Supported queries:**
- Semantic: vector similarity on `content_embedding` (computed in Python)
- Graph traversal: `{links: "target-id"}` for forward, `{note_id: {$in: source.links}}` for reverse
- Filtered: `{tags: "task", status: "active", domains: "indemn"}`
- Keyword: full-text search on `title` + `content`
- Timeline: `{created_at: {$gte: last_week}}`
- System-scoped: `{system: "content", tags: "draft", status: "in-review"}`
- Neighborhood: `$graphLookup` for multi-hop traversal

**Note:** Atlas Vector Search is cloud-only. For local MongoDB, embeddings are stored as arrays and cosine similarity is computed in Python. At the scale of hundreds to low thousands of notes, this is fast enough. If it becomes a bottleneck, add a dedicated vector store (ChromaDB, LanceDB) later.

### Embedding Model

- **Initial:** Local model via Ollama (e.g., `nomic-embed-text` or `mxbai-embed-large`)
- **Abstracted:** Behind a simple interface so the model is swappable

```python
def embed(text: str) -> list[float]:
    # Ollama today, OpenAI tomorrow, whatever
    pass
```

- Each note is embedded when created or updated during sync
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

Beyond startup, Claude Code can query the Hive on-demand:
- `hive search "rubric component"` — find related notes mid-session
- `hive note get 2026-03-01-rubric-component` — read a specific note in full
- `hive context "deployment patterns" --domain career-catalyst` — cross-domain discovery

### Skill and System Awareness

Skills and systems are themselves represented as notes in the Hive:

```yaml
tags: [skill, tool]
domains: [indemn, career-catalyst, personal]
---
# /linear
Issue tracking via linearis CLI. Relevant when: working on tasks
that have Linear issue IDs or need work tracking.
```

The context assembly graph can then connect: "voice scoring task → has `linear: AI-123` → the `/linear` skill is relevant" and surface it in the session instruction.

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
- Read `hive/.registry/ontology.yaml` for available tags, domains, expected fields
- Create notes via `hive note create` for knowledge artifacts
- Create awareness records when your skill produces deliverables
- Use `hive context <topic>` for background knowledge
- If you need a new tag, register it in `ontology.yaml` with description and category
- Document your Hive integration in the skill's SKILL.md

**For existing skills becoming Hive-aware:**
- Add `hive context` at the start if the skill needs background knowledge
- Add `hive note create` at key output points (after brainstorming, spec creation, completion)
- The Hive is additive — don't replace the skill's core logic

**The Hive skill (`/hive`) handles:**
- Native knowledge CRUD, search, context assembly, sync, ontology management
- Other skills call the `hive` CLI, not MongoDB or vault files directly

---

## The Hive CLI

Python CLI (Click or Typer). Same pattern as `bd` for beads.

### Commands

```bash
# Setup
hive init                    # Create vault, .registry, start MongoDB, seed ontology

# Context assembly (the main command)
hive context "voice scoring"                    # Full session initialization instruction
hive context "voice scoring" --domain indemn    # Scoped to a domain
hive context "voice scoring" --deep             # Full note content, not summaries
hive context "voice scoring" --objective "build the scoring UI"  # Tailored for purpose

# Search
hive search "deployment patterns"               # Semantic search
hive search "rubric" --tags spec --domain indemn  # Filtered search

# Note operations
hive note create --tags spec,voice --domains indemn --title "Voice Scoring Spec"
hive note create --file /path/to/content.md     # Create from existing file
hive note get 2026-03-08-scoring-spec           # Read a note
hive note update 2026-03-08-scoring-spec        # Update (re-index)

# Listing and filtering
hive notes --tags task --status active                    # Active tasks
hive notes --tags decision --since 2026-03-01             # Recent decisions
hive notes --system content --status drafting             # Content drafts
hive notes --domains career-catalyst                      # Everything in a domain

# Sync
hive sync                    # Index all vault files into MongoDB
hive sync --re-embed         # Re-generate all embeddings (when switching models)

# Ontology
hive tags list               # Show all registered tags with descriptions
hive tags add <tag> --category work --description "..."   # Register new tag
hive domains list            # Show all domains
hive domains add <domain> --description "..."             # Register new domain

# Status
hive status                  # Overview: note counts by domain, recent activity, active work
```

### Architecture

```
hive/                         # CLI package
  cli.py                      # Click/Typer CLI entry point
  note.py                     # Note CRUD operations
  context.py                  # Context assembly engine
  search.py                   # Search (semantic + filtered)
  sync.py                     # Vault → MongoDB sync
  ontology.py                 # Ontology management
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

**LLM-driven arrangement, not algorithmic.** The Wall's organization is not a weighted scoring formula. This is an LLM-based system — the intelligence should come from LLMs. The Wall shows what matters based on LLM reasoning about current state, not from `score = (priority × 0.5) + (recency × 0.3)`. The LLM understands "meeting in 2 hours and prep hasn't been done" without hand-coded rules.

### Tile Visual Design

**Fluid sizing.** Tiles are not three fixed sizes. They show as much information as fits their current rendered space. Title is always visible. Status and color are always present. As a tile gets more space: context line appears, then tags, then timestamps, then summaries. The transition is continuous, not stepped.

**Fewer tiles at useful size, not more tiles at useless size.** When the Wall is compressed, it shows a smart highlight reel — active items, things needing attention, upcoming events. The full inventory is available in Overview mode. This keeps the compressed state scannable.

**Visual encoding — three axes:**

| Axis | Maps to | Purpose |
|------|---------|---------|
| **Color** | System (content, code, sessions, calendar, email, linear, etc.) | "What kind of thing is this?" |
| **Accent/border** | Domain (Indemn, Career Catalyst, Personal) | "Which world does it belong to?" |
| **Brightness/opacity** | Status (vivid=active, normal=to-do, muted=backlog, faded=done) | "What's its energy level?" |

If a note has no `system` field (native knowledge), color comes from the primary tag category (Knowledge, Work, Record, Output) as defined in the ontology.

**Rectangular tiles for MVP.** Honeycomb/hexagonal tiles are visually aligned with the hive metaphor but significantly harder to implement (CSS grid/flexbox are rectangle-native). Start with rounded rectangular tiles, dense packing, minimal gaps, organic feel. Honeycomb is a future CSS-level evolution if warranted.

### Tile Data Mapping

Every visual element on a tile maps to a Hive note field:

```
Note field              →  Tile visual
──────────────────────────────────────────────
title                   →  Tile label
tags[]                  →  Type indicator
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

### 3. Linear Integration Details
**Question:** What triggers Linear sync? How are conflicts resolved? One-way or bidirectional?
**Leaning:** Bidirectional. `hive linear sync` command. Linear is authority for work state (status, assignee). Hive is authority for knowledge connections. Sync on demand, not continuous.
**Decide during:** Phase 3 implementation.

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
**Goal:** The vault exists, notes can be created and queried, the ontology is seeded.

- [ ] Create `hive/` directory in the OS repo
- [ ] Create `hive/.registry/ontology.yaml` with initial tags, domains, statuses
- [ ] Create `hive/.templates/` with example notes for common patterns
- [ ] Install local MongoDB Community Edition (`brew install mongodb-community`)
- [ ] Build `hive` CLI core (Python, Click/Typer):
  - `hive init` — set up vault structure, create MongoDB database and collection, seed indexes
  - `hive note create` — create a markdown note with frontmatter, write to vault, index into MongoDB
  - `hive note get` — read a note by ID
  - `hive sync` — parse all vault markdown files, extract frontmatter + content, upsert into MongoDB
  - `hive tags list` — display registered tags from ontology.yaml
  - `hive status` — count notes by domain, show recent activity
- [ ] Create the `/hive` skill (`.claude/skills/hive/SKILL.md`)
- [ ] Migrate 5-10 existing artifacts as proof of concept (add Hive frontmatter, index)
- [ ] Create initial entity notes: domains (Indemn, Career Catalyst, Personal), key people, key projects
- [ ] Verify: can create notes, can query MongoDB, can list/filter notes

**Exit criteria:** `hive note create` and `hive sync` work. A handful of real notes exist and are queryable.

### Phase 2: Context Engine
**Goal:** Sessions can hydrate context from the Hive. Semantic search works.

- [ ] Install Ollama + embedding model locally
- [ ] Build embedding abstraction layer (`embed.py`)
- [ ] Add embedding generation to `hive sync` (embed content, store vectors in MongoDB)
- [ ] Build `hive search` — semantic search via cosine similarity + keyword/tag filters
- [ ] Build `hive context` — retrieval algorithm (semantic + graph + recency scoring) that returns ranked notes
- [ ] Create context instruction template (knowledge, skills, reads, reminders sections)
- [ ] Integrate with session startup — update `/sessions` skill to recommend `hive context` at start
- [ ] Build `hive note create --from-file` — convert existing markdown files to Hive notes
- [ ] Migrate all 73 existing artifacts to Hive notes (add frontmatter, index, embed)
- [ ] Extract decisions from INDEX.md files into standalone decision record notes
- [ ] Test: start a session, run `hive context`, verify the briefing is useful and accurate

**Exit criteria:** `hive context "voice evaluations"` returns a useful, relevant briefing with knowledge, skills, and reminders. Semantic search finds conceptually related notes.

### Phase 3: Integration
**Goal:** The Hive is woven into the daily workflow. Linear syncs. Sessions create notes.

- [ ] Build `hive linear sync` — pull Linear issues as awareness records, push Hive task notes to Linear
- [ ] Update `/sessions` skill — session close creates a session-summary record note
- [ ] Update brainstorming skill — key ideas and decisions become Hive notes
- [ ] Update project skill — `/project` queries Hive alongside/instead of INDEX.md
- [ ] Create awareness records for all active Linear issues (bulk import)
- [ ] Create entity notes for all Linear teams, key repos
- [ ] Build `hive notes` listing/filtering commands
- [ ] Determine beads ↔ Hive relationship — mirror beads tasks as awareness records
- [ ] Test: full workflow — brainstorm → spec → tasks → dispatch → completion, all tracked in Hive

**Exit criteria:** A complete feature lifecycle is traceable through the Hive. Linear issues appear as notes. Session summaries auto-create.

### Phase 4: System Integration
**Goal:** Multiple systems report to the Hive. Cross-system context assembly works.

- [ ] Content system integration — content CLI creates awareness records for ideas, drafts, published posts
- [ ] Dispatch integration — dispatch creates awareness records for task completion/failure
- [ ] GitHub integration — PRs and merges create awareness records (via hooks or skill updates)
- [ ] Meeting ingestion — meeting summaries from Postgres become Hive record notes
- [ ] Update context assembly to surface cross-system connections
- [ ] Document the system integration convention (for future systems)
- [ ] Test: context for a feature shows related Linear issues, PRs, content, meetings

**Exit criteria:** Working on a feature surfaces connected content drafts, meetings, Linear issues, and PRs from across systems.

### Phase 5: The Hive UI
**Goal:** The Hive is the home screen. Wall + Focus Area. Tiles. Session spawning with context.

- [ ] Evolve OS Terminal React app — replace session grid with Wall + Focus Area layout
- [ ] Build tile component — fluid sizing, progressive information disclosure, color/accent/brightness encoding
- [ ] Build Wall layout — tiles surrounding Focus Area, breathing with activity level, smart highlight reel in compressed mode
- [ ] Build Focus Area — equal-sized auto-grid of terminal panels (xterm.js, existing) + browser panels (iframe, new)
- [ ] Build Overview toggle — expand Wall to full screen, collapse back to Focus
- [ ] Add Hive API routes to Express backend — wrap Hive CLI with JSON output
- [ ] Add WebSocket Hive updates — push note changes to frontend (~30s polling + on-action)
- [ ] Build domain filtering — click domain tile to filter Wall
- [ ] Build search tile — search input that queries `hive search`
- [ ] Build quick capture tile — input that creates notes, LLM auto-tags async
- [ ] Build "create linked note" interaction — one-click note creation linked to parent tile
- [ ] Build session spawning from tiles — click tile → `session create` → first message with tile metadata via `tmux send-keys`
- [ ] Build session initialization flow — objective question → targeted context retrieval → work begins
- [ ] Merge session state tiles (from `sessions/*.json`) with Hive note tiles into unified Wall
- [ ] Color/visual mapping from `ontology.yaml` — system colors, domain accents, status brightness
- [ ] Responsive layout — ultra-wide (Wall + Focus coexist), smaller screens (Wall collapses)
- [ ] Configure Obsidian vault pointing at `hive/` for alternative visualization

**Exit criteria:** The Hive is the home screen. You see your world as tiles, click to start context-hydrated sessions, work in Focus panels, observe everything from the Wall. The OS Terminal's session grid is fully replaced.

### Phase 6: Expansion
**Goal:** The Hive handles external sources, multiple users, and self-improvement.

- [ ] External source ingestion — Slack messages, emails, calendar events → record notes
- [ ] Multi-user — shared MongoDB or generated output views for CEO/teammates
- [ ] Graph quality management — archival conventions, stale note detection, pruning
- [ ] Automated ontology management — detect tag drift, suggest merges
- [ ] Self-improvement — track which context was useful (feedback loop from sessions)
- [ ] New system templates — streamline creating Hive-integrated systems
- [ ] Cross-domain discovery automation — proactively surface connections

**Exit criteria:** External sources flow into the Hive. The CEO gets weekly views. Graph quality stays high as the system scales.

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

### Continual Improvement Mechanisms
- **Context feedback:** When a session starts with Hive context and the briefing is missing something critical, note what was missing. Use this to tune retrieval weights.
- **Ontology evolution:** New tags emerge from real work. The registry grows to match how the system is actually used.
- **Embedding model upgrades:** As better local models emerge, swap via `hive sync --re-embed`. The abstraction layer makes this painless.
- **Skill integration depth:** Start with basic Hive integration in skills. Deepen over time as patterns emerge.
- **Cross-domain discovery:** Track when a session discovers a useful cross-domain connection. Use this to improve semantic search and graph expansion.

---

## Key Decisions Made

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-08 | Everything is a note — one universal format, tags differentiate behavior | Simpler than a type hierarchy. Behavior comes from metadata fields, not types. |
| 2026-03-08 | The Hive is connective tissue, not a data layer | Systems keep their own architectures. The Hive indexes, links, and surfaces — it doesn't replace. |
| 2026-03-08 | Two kinds of notes: native knowledge and awareness records | Native knowledge lives in the Hive. System artifacts stay in their systems with lightweight Hive index entries. |
| 2026-03-08 | Flat vault structure | Organization comes from the graph (tags, links, domains), not the filesystem. The UI handles presentation. |
| 2026-03-08 | Local MongoDB, not Atlas | Personal/cross-domain data shouldn't live on Indemn's cluster. Local is private, free, fast. |
| 2026-03-08 | Local embedding model (Ollama), swappable | Start local for experimentation. Abstraction layer enables switching to API models later. |
| 2026-03-08 | Controlled vocabulary via `ontology.yaml` | Prevents tag fragmentation across sessions. Evolves deliberately, not accidentally. |
| 2026-03-08 | Context assembly produces session initialization instructions | Not just knowledge — includes relevant skills, proactive reads, and reminders. Tailored by objective. |
| 2026-03-08 | System CLIs handle Hive updates, not raw `hive note create` | Each system manages its own domain logic. The Hive CLI is the low-level building block. |
| 2026-03-08 | Skills must document their Hive integration convention | New skills follow the convention. Existing skills evolve incrementally to become Hive-aware. |
| 2026-03-08 | Markdown files are source of truth, MongoDB is derived | Git-trackable, human-readable, Obsidian-compatible. MongoDB rebuilt from files via `hive sync`. |
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
