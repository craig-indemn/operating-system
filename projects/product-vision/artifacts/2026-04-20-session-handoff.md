---
ask: "Universal session handoff — full context hydration for any session working on the Indemn OS"
created: 2026-04-20
workstream: product-vision
session: 2026-04-20-roadmap
sources:
  - type: codebase
    ref: "/Users/home/Repositories/indemn-os"
  - type: project
    ref: "projects/product-vision"
  - type: project
    ref: "projects/customer-system"
---

# Session Handoff — 2026-04-20

## For Any Session Working on the Indemn OS

This handoff gives you everything you need to understand what the OS is, what's been built, and how to contribute. You are likely one of multiple parallel sessions working on the OS simultaneously. Read thoroughly before doing anything.

**You MUST read every file in the mandatory section. No exceptions. No skimming.**

---

## Reading Protocol — MANDATORY

### 1. The Vision (read FIRST — this is what the system SHOULD be)

- `/Users/home/Repositories/indemn-os/CLAUDE.md` — the builder's manual. Entity types, field syntax, watches, rules, associates, auth, deployment, debugging, entity criteria, 8-step domain modeling.
- `projects/product-vision/artifacts/2026-04-16-vision-map.md` — **THE authoritative reference.** 23-section design synthesis from 104 source files. Every architectural decision is here. When in doubt, check this document.
- `projects/product-vision/CLAUDE.md` — session bootstrap protocol, artifact index, design integrity rules.

### 2. What's Built (read to understand current state)

- `projects/product-vision/INDEX.md` — full project history, all artifacts, all decisions (read § Status + § Decisions)
- `projects/customer-system/INDEX.md` — the first real domain on the OS, data inventory, what works
- `projects/customer-system/artifacts/2026-04-20-ui-and-assistant-session.md` — latest session: UI polish, assistant refactor, what's proven vs unproven

### 3. Implementation Specs (read when working on specific subsystems)

- `projects/product-vision/artifacts/2026-04-14-impl-spec-phase-0-1-consolidated.md` — kernel framework spec
- `projects/product-vision/artifacts/2026-04-14-impl-spec-phase-2-3-consolidated.md` — associate execution + integrations spec
- `projects/product-vision/artifacts/2026-04-14-impl-spec-phase-4-5-consolidated.md` — base UI + real-time spec
- `projects/product-vision/artifacts/2026-04-17-wiring-audit.md` — 139 behaviors audited, implementation source of truth

**DO NOT re-read individual design artifacts unless the vision map is ambiguous on a specific point. The synthesis documents exist so you don't have to.**

---

## What the OS Is

An object-oriented insurance system where every insurance concept has schema + state machine + API + CLI. AI agents are a CHANNEL into the platform, not a separate system. Define an entity and it auto-generates its API, CLI, documentation (skills), permissions, and UI — the self-evidence property.

**Six primitives**: Entity, Message, Actor, Role, Organization, Integration.
**Seven kernel entities**: Organization, Actor, Role, Integration, Attention, Runtime, Session.
**Trust boundary**: Kernel (direct MongoDB) vs everything else (CLI subprocess only).

## What's Deployed

| Service | URL |
|---------|-----|
| API | https://indemn-api-production.up.railway.app |
| UI | https://indemn-ui-production.up.railway.app |
| Chat Runtime | wss://indemn-runtime-chat-production.up.railway.app/ws/chat |

**External**: MongoDB Atlas (`dev-indemn.mifra5.mongodb.net`), Temporal Cloud (`indemn-dev.hxc6t`), Grafana Cloud, GCP Vertex AI.

**CLI:**
```bash
export INDEMN_API_URL=https://indemn-api-production.up.railway.app
INDEMN=/Users/home/Repositories/bot-service/.venv/bin/indemn
$INDEMN auth login --org _platform --email craig@indemn.ai --password indemn-os-dev-2026
$INDEMN entity list --format table
$INDEMN company list --limit 3
$INDEMN platform health
```

**Key IDs**: Platform org `69e23d586a448759a34d3823`, admin actor `69e23d586a448759a34d3824`, OS Assistant `69e50bdce35065d0498df6cc`, chat runtime `69e2777c02fab4de6eea7d9e`.

**Deployment**: `cd /Users/home/Repositories/indemn-os && railway service <name> && railway up`. UI and chat harness do NOT auto-deploy from git push.

## What's Built and Working

**Kernel (all 15 subsystems implemented with real logic):**
- Entity framework (dynamic class creation from definitions in MongoDB)
- save_tracked (atomic: entity + changes + watches in one transaction)
- Watch system (evaluator + cache + scope resolution)
- Rule engine (conditions + lookups + group status + veto)
- State machine enforcement
- Auth (JWT + service tokens + rate limiting)
- Org lifecycle (clone/diff/deploy)
- Schema migration, bulk operations, integration adapters (Outlook + Stripe)
- Observability (OTEL spans), queue processor, Temporal client
- Seed loading, capability system (@exposed decorator)

**Customer System (first real domain — 14 entities, real data):**
- 87 companies, 92 contacts, 24 associate types, 2 conferences, 7 stages, 4 outcome types
- 14 human actors with team_member role
- All data imported and queryable

**UI (15 improvements shipped 2026-04-20):**
- Auto-generated entity list/detail/create views from definitions
- Horizontal scroll, sticky headers, visible scrollbars
- Search, filter, sort, column picker (persisted), pagination
- State transitions with toast confirmation
- Breadcrumbs, favicon, dynamic page titles, keyboard shortcuts
- Collapsible sidebar, URL-synced filters
- Changes timeline (field-level audit trail)

**Assistant (refactored 2026-04-20):**
- Resizable split pane (not overlay) — peer to entity views
- Skills via deepagents progressive disclosure (SKILL.md files, loaded on demand)
- Streaming via `astream_events()` (token-by-token)
- Entity detection: harness-side `on_tool_end` + client-side `tryDetectEntityData`
- Inline rendering: CompactEntityTable, EntityCard, CollapsibleToolCall
- Conversation history and resume
- Model: gemini-3-flash-preview (Vertex AI)

**CI (fully green):**
- lint, test-unit (93 tests), test-integration, Docker build all pass

## What's NOT Built Yet

- **Watches** — zero configured. The system has no reactive wiring. No entity change flows to anyone.
- **Automations** — no associates processing entity changes (meeting intelligence extraction, staleness monitoring, notifications).
- **Voice harness** — design exists, not built.
- **Integration adapters beyond Outlook/Stripe** — no Slack, no Google Drive.
- **Grafana dashboards** — OTEL traces flow but no dashboards configured.
- **Token refresh** — 401 errors in browser console suggest refresh may not be working.

## Design Integrity Rules

1. **Vision IS the MVP.** Never simplify or defer without Craig's explicit approval.
2. **Implement EXACTLY what the design specifies.** Every flag, parameter, behavior.
3. **Verify against the live system.** Don't just commit — confirm it works E2E.
4. **When Craig asserts something was designed**, search until you find it in the artifacts.
5. **Skills are auto-generated from entity definitions** — never hardcode CLI commands or entity types.
6. **The assistant uses skills for knowledge, the CLI for operations.** No shortcuts.
7. **Always use the CLI for OS operations**, not direct API calls. The CLI IS the universal interface.
8. **Understand before implementing.** Read the data, see the actual output, know the exact shape before writing code.

## Working in Parallel

**You are likely one of multiple sessions.** Other sessions may be working on different parts of the OS simultaneously. Key coordination rules:

- **Use git worktrees** for isolation. Don't work directly on main unless you're the only one.
- **Commit frequently** with descriptive messages. Other sessions read your commits.
- **Don't modify files another session is actively working on** without coordinating with Craig.
- **The indemn-os repo is the shared codebase.** The operating-system repo holds project artifacts and plans.
- **Check `git log --oneline -20` before starting work** to see what other sessions have done recently.
- **Deploy carefully.** `railway up` deploys immediately to production. Coordinate with Craig before deploying.

## Git

- **indemn-os**: `main` branch. All OS code. `/Users/home/Repositories/indemn-os/`
- **operating-system**: `os-roadmap` branch for project artifacts. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/`
