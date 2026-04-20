---
ask: "Session handoff — context hydration for continuing OS + customer system work"
created: 2026-04-20
workstream: customer-system
session: 2026-04-19-20
sources:
  - type: codebase
    ref: "/Users/home/Repositories/indemn-os"
  - type: project
    ref: "projects/customer-system"
  - type: project
    ref: "projects/product-vision"
---

# Session Handoff — 2026-04-20

## Reading Protocol — MANDATORY

**You MUST read these files before doing any work. No exceptions.**

### 1. The Vision (read FIRST — this is what the system SHOULD be)

- `/Users/home/Repositories/indemn-os/CLAUDE.md` — the builder's manual. Entity types, field syntax, watches, rules, associates, auth, deployment, debugging, entity criteria, 8-step domain modeling.
- `projects/product-vision/artifacts/2026-04-16-vision-map.md` — 23-section authoritative design synthesis from 104 source files. This is THE reference for "is this in alignment with the vision?"
- `projects/product-vision/CLAUDE.md` — session bootstrap protocol, artifact index, design integrity rules.

**Every decision you make should be checkable against the vision map. If you're unsure whether something aligns, re-read the relevant section.**

### 2. Current State (read to understand where things are)

- `projects/customer-system/INDEX.md` — project status, decisions, data inventory
- `projects/customer-system/artifacts/2026-04-14-phase-1-domain-model.md` — 14 entity definitions with fields, state machines, relationships
- This handoff (the rest of this file)

---

## What Exists

### The OS (indemn-os repo, main branch)

A working object-oriented insurance platform deployed on Railway. 6 services: API, queue processor, Temporal worker, async runtime, chat runtime, UI.

**The self-evidence property works**: define an entity in MongoDB → API endpoints, CLI commands, UI list/detail views, auto-generated skill documentation all exist immediately. No custom code per entity.

### The Customer System (first real domain on the OS)

14 entity definitions. Real data imported:
- 87 companies (9 customer, 7 pilot, 71 prospect)
- 92 contacts linked to companies
- 24 associate types across the Four Outcomes
- 2 conferences (InsurTechNY, ALER26) linked to 47 companies
- 7 pipeline stages with probabilities
- 4 outcome types
- 14 human actors with team_member role

### The UI

Login → sidebar navigation (domain entities / system entities) → entity list views with search, per-column filters, sort, column picker, pagination, bulk checkboxes → detail views with editable fields, enum dropdowns, entity pickers, state transitions, relationship links → cross-entity navigation → assistant panel.

### The Assistant

An "OS Assistant" associate actor with 23 entity skills loaded, connected to the chat-deepagents runtime via WebSocket. The UI has a panel at the top ("Ask or tell me to do something...") that connects to it.

---

## Honest Assessment — What's Real vs What's Wired

**Real and working:**
- Entity CRUD via CLI and API
- UI renders entities automatically from definitions
- Search, filter, sort, column picker on list views
- Detail view editing with enum dropdowns and entity pickers
- State transitions with confirmation
- Cross-entity navigation via relationship links
- Observability with real state distribution data
- Token refresh (just implemented — needs production verification)

**Wired but not proven:**
- **Assistant operations** — it answered "ARR is 70000" by reading a JSON context field the UI passed it. It has NOT been verified to actually run CLI commands (create entity, transition, query). The skills are loaded and the system prompt says to use the CLI, but the execute tool / shell access in the deepagents framework hasn't been tested for real operations. This is the gap between "connected" and "working."
- **Conversation persistence** — interaction_id reuse is coded but not verified across browser reloads
- **Changes timeline** — the trace API works but the UI component may not render changes for all entities
- **Bulk transitions** — checkboxes render but the bulk action bar with transition buttons hasn't been tested with actual state changes
- **Token refresh** — just committed, not yet verified in production

**Not built:**
- **Watches** — zero watches configured. No entity change flows to anyone. The OS is a database with a UI until watches are wired. Per the vision: watches on roles are what make the system reactive.
- **Automations** — no associates processing entity changes (meeting intelligence extraction, staleness monitoring, notifications)
- **The data model hasn't been validated by use** — nobody has created a Deal, logged a Meeting, tracked a Task, or recorded a Signal through the system yet. The domain model is theory until exercised.

---

## Pre-Flight

```bash
# Health check
curl -s https://indemn-api-production.up.railway.app/health

# CLI (installed in bot-service venv)
export INDEMN_API_URL=https://indemn-api-production.up.railway.app
INDEMN=/Users/home/Repositories/bot-service/.venv/bin/indemn
$INDEMN auth login --org _platform --email craig@indemn.ai --password indemn-os-dev-2026

# Verify
$INDEMN entity list --format table
$INDEMN company list --limit 3
$INDEMN platform health
```

## Architecture Reference

| Service | URL |
|---------|-----|
| API | https://indemn-api-production.up.railway.app |
| UI | https://indemn-ui-production.up.railway.app |
| Chat Runtime | wss://indemn-runtime-chat-production.up.railway.app/ws/chat |

Key IDs: _platform org `69e23d586a448759a34d3823`, admin actor `69e23d586a448759a34d3824`, chat runtime `69e2777c02fab4de6eea7d9e`, OS assistant `69e50bdce35065d0498df6cc`

Git: indemn-os on `main`, OS repo on `os-roadmap` branch.

## Design Integrity Rules

1. Vision IS the MVP. Never simplify or defer without Craig's explicit approval.
2. Implement EXACTLY what the design specifies.
3. Verify against the live system. Don't just commit — confirm it works E2E.
4. When Craig asserts something was designed, search until you find it.
5. Skills are auto-generated from entity definitions — never hardcode CLI commands or entity types.
6. The assistant uses skills for knowledge, the CLI for operations. No shortcuts.
7. Always use the CLI for OS operations, not direct API calls. The CLI IS the universal interface.
