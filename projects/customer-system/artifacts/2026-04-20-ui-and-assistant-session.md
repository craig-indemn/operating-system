---
ask: "Session handoff — UI polish, assistant UX refactor, and what's working"
created: 2026-04-20
workstream: customer-system
session: 2026-04-20-roadmap
sources:
  - type: codebase
    ref: "/Users/home/Repositories/indemn-os"
  - type: design
    ref: "docs/plans/2026-04-20-assistant-ux-design.md"
  - type: design
    ref: "docs/plans/2026-04-20-os-ui-polish-and-assistant.md"
---

# Session Record — 2026-04-20: UI Polish + Assistant UX Refactor

## Reading Protocol — MANDATORY

**Read these files before doing any work:**

1. `projects/product-vision/artifacts/2026-04-16-vision-map.md` — authoritative design (23 sections)
2. `projects/product-vision/CLAUDE.md` — session bootstrap, artifact index
3. `projects/customer-system/INDEX.md` — project status, decisions, data inventory
4. `/Users/home/Repositories/indemn-os/CLAUDE.md` — the builder's manual (entities, watches, rules, associates, CLI)
5. This file (the rest of this document)
6. `projects/customer-system/artifacts/2026-04-20-session-handoff.md` — previous session handoff

## What Was Done This Session

### 1. UI Polish (15 improvements, all deployed)

**Critical fixes:**
- Horizontal scrolling on entity tables (min-w-0 on root div)
- Changes timeline working (API field `events` → `timeline` rename)
- Relationship ObjectIds resolve to names (depth=2 fetch)
- State field uses actual `is_state_field` from meta, not hardcoded "status"
- Table fits viewport with sticky headers, both-axis scroll, visible 12px scrollbars
- Content column constrained so wide tables don't expand TopBar

**Important improvements:**
- Toast notification system (replaced all alert() calls)
- Page indicator in pagination
- Form validation for required fields with error messages
- Create form populates field defaults from entity definition
- Contextual empty states with "Clear filters" action
- Column visibility persisted to localStorage
- Search/filter state synced to URL query params (debounced, bookmarkable)
- Collapsible entity sections in sidebar navigation

**Polish:**
- Favicon (inline SVG hexagon) + dynamic page titles per view
- Breadcrumb navigation on detail and create views
- Keyboard shortcut help modal (press `?`)
- Collapsible sidebar (hamburger menu in TopBar)
- Markdown rendering in assistant responses

### 2. Assistant UX Refactor (split pane architecture)

**Layout:**
- Assistant is now a resizable split pane on the right side (not a fixed overlay)
- ResizeDivider component with drag-to-resize (functional updater to avoid stale closure)
- Width persisted to localStorage, clamped 300px–60% viewport
- Collapse button on right edge when closed, `/` and `Cmd+K` shortcuts to open
- TopBar has "Assistant /" button when pane is closed

**Skills (CRITICAL — how it actually works):**
- Skills are fetched from the database via `indemn skill list` on session start
- Written to `/workspace/skills/{name}/SKILL.md` with YAML frontmatter
- Passed to `create_deep_agent(skills=["skills"])` — the PARENT directory
- deepagents' SkillsMiddleware discovers subdirectories, loads metadata into prompt
- Agent reads full skill content on demand via `read_file` (progressive disclosure)
- This is the correct deepagents pattern — NOT concatenating all skills into the system prompt

**Streaming:**
- `astream_events()` replaces `ainvoke()` for token-by-token streaming
- `on_chat_model_stream` events → `token` messages to UI → real-time display
- `on_tool_end` events → entity detection → `entity_list`/`entity_detail` messages

**Entity detection (dual path):**
- Harness-side: `on_tool_end` parses tool output, detects JSON with `_id` fields, sends typed messages
- Client-side: `tryDetectEntityData()` in AssistantPanel catches JSON in streamed text (fallback)
- Bracket-depth counting handles CLI decorative borders after JSON
- Both paths needed: LLM sometimes echoes JSON (client catches it), sometimes summarizes (harness catches it)

**Inline rendering:**
- CompactEntityTable: max 10 rows, auto-detects name/state fields, clickable links, "Show all" overflow
- EntityCard: single entity with key fields, state badge, "View →" link
- CollapsibleToolCall: collapsed one-liner, expandable to full args JSON
- Entity type inferred from data fields via allEntityMeta cache (harness sends empty string)

**Conversation persistence:**
- History button shows past conversations (fetches from /api/interactions/)
- "New Conversation" closes WebSocket, next message creates fresh Interaction
- Resume indicator ("Session resumed" divider) on reconnect
- First-message preview saved on Interaction entity for history UI

**Model:** gemini-3-flash-preview (Vertex AI). Note: if this hangs, the model may not be enabled on the GCP project. gemini-2.5-flash is the fallback.

**System prompt:** Action-biased. "Execute actions — don't explain how." Destructive confirmation for terminal transitions. Never use task/subagent tools.

### 3. CI Fixes (all passing)

- JWT_SIGNING_KEY env var for unit and integration tests
- Removed tests for deleted skill parsing functions
- Fixed state machine tests (explicit _state_field_name)
- Resolved all 110 ruff lint errors
- setup-uv upgraded to v6
- .gitkeep files in seed/ directories for Docker build
- All 4 CI jobs pass: lint, test-unit, test-integration, build

## Architecture Reference

| Service | URL | Status |
|---------|-----|--------|
| API | https://indemn-api-production.up.railway.app | Running |
| UI | https://indemn-ui-production.up.railway.app | Running |
| Chat Runtime | wss://indemn-runtime-chat-production.up.railway.app/ws/chat | Running |

**Deployment:** `railway service <name> && railway up` from indemn-os repo root. UI needs separate deploy (not auto-deploy from push).

**CLI:**
```bash
export INDEMN_API_URL=https://indemn-api-production.up.railway.app
INDEMN=/Users/home/Repositories/bot-service/.venv/bin/indemn
$INDEMN auth login --org _platform --email craig@indemn.ai --password indemn-os-dev-2026
```

**Key IDs:** Platform org `69e23d586a448759a34d3823`, admin actor `69e23d586a448759a34d3824`, OS Assistant `69e50bdce35065d0498df6cc`, chat runtime `69e2777c02fab4de6eea7d9e`

## What's Working (Verified)

- Entity CRUD via CLI and API
- UI auto-generates from entity definitions (self-evidence property)
- Search, filter, sort, column picker, pagination on list views
- State transitions with confirmation (toast feedback)
- Cross-entity navigation via relationship links (resolved to names)
- Changes timeline on detail views (field-level old → new)
- Assistant connected via real chat harness (not kernel endpoint)
- Assistant loads skills via progressive disclosure (deepagents)
- Assistant streams responses token-by-token
- Entity data renders as interactive tables in assistant
- Conversation history and resume
- Resizable split pane

## What's Not Yet Proven / Known Issues

- **Assistant entity rendering is inconsistent** — sometimes the LLM echoes JSON (client-side detection catches it and shows table + JSON), sometimes it summarizes (harness detection shows table + summary). The dual detection handles both but can occasionally show duplicate data.
- **Conversation persistence across browser restart** — localStorage keeps messages visible, but LangGraph checkpoint resume from MongoDB hasn't been verified E2E.
- **gemini-3-flash-preview availability** — hung indefinitely once. May need gemini-2.5-flash fallback.
- **401 errors in console** — entity meta and list requests fail with 401 on token expiry. Token refresh may not be working correctly.
- **Bulk transitions** — checkboxes render, confirmation works, but actual bulk state changes not tested.
- **Watches** — zero configured. The system has no reactive wiring yet.
- **Automations** — no associates processing entity changes.

## Design Documents Created

- `docs/plans/2026-04-20-os-ui-polish-and-assistant.md` — 15-task implementation plan (all executed)
- `docs/plans/2026-04-20-assistant-ux-design.md` — approved assistant UX design (split pane, persistence, entity rendering, verification plan)

## What's Next

Craig is moving into the next phase of customer system development — building watches and automations. This will shake out a different part of the OS (the reactive wiring: watches on roles, message creation, associate processing).

Before starting:
1. Read the vision map (especially Sections 5, 11, 12 on watches, actors, real-time)
2. Read the customer system domain model and entity definitions
3. Understand what watches need to be configured for the team to get value
4. Design the automation layer with Craig
