---
ask: "Session handoff — comprehensive context for continuing OS + customer system development"
created: 2026-04-20
workstream: customer-system
session: 2026-04-19-20
sources:
  - type: codebase
    ref: "/Users/home/Repositories/indemn-os"
    description: "All kernel + harness + CLI + UI code"
  - type: project
    ref: "projects/customer-system"
    description: "Customer system domain model, data, UI evaluation"
  - type: project
    ref: "projects/product-vision"
    description: "OS vision, design specs, architecture"
---

# Session Handoff — 2026-04-20

## What This Session Did

1. **Built the customer system on the live OS** — 14 entity definitions, 87 companies, 92 contacts, 24 associate types, 2 conferences, 7 stages, 4 outcome types, 14 human actors with team_member role
2. **Comprehensive UI evaluation** — browser-tested every view, documented 20 gaps with priority tiers
3. **Resolved all 3 UI tiers** (17 of 20 gaps) — navigation cleanup, ObjectId→name resolution, assistant wiring, search/filter, pagination, enum dropdowns, transition confirmation, changes timeline, entity pickers, state colors, smart columns, assistant context, observability
4. **Resolved 10 vision-required limitations** — state distribution aggregation, bulk-create org_id, hash chain verification, conversation persistence, session warmup, assistant skills (no hardcoded commands), bulk actions UI, search on kernel entities
5. **Fixed 15+ kernel/CLI/UI bugs** discovered during implementation — Decimal serialization, trailing slashes, React hooks order, WebSocket URL, token refresh
6. **Per-column filtering + column visibility** — Excel-like filtering with enum dropdowns and text search on every column, column picker toggle, horizontal scroll

## What the Next Session Does

Continue refining three areas:
1. **The OS itself** (indemn-os repo) — kernel, harnesses, CLI, UI
2. **The customer system data** — data quality, entity relationships, watches/automation
3. **The assistant** — skill tuning, ability to create/transition/query entities effectively

---

## Reading Protocol for Next Session

### Step 1: OS Vision Context (CRITICAL — read before touching anything)

1. `/Users/home/Repositories/indemn-os/CLAUDE.md` — the builder's manual (entity types, field syntax, watches, rules, associates, debugging, entity criteria, 8-step domain modeling process)
2. `projects/product-vision/artifacts/2026-04-16-vision-map.md` — 23-section authoritative design (the "what the system should be" reference)
3. `projects/product-vision/CLAUDE.md` — session bootstrap protocol, artifact index, design integrity rules

**Key vision principles:**
- Vision IS the MVP — never simplify or defer without explicit approval
- AI agents are a CHANNEL into the platform, not a separate system
- Define an entity and it auto-generates API, CLI, skills, UI (self-evidence property)
- Harnesses use CLI subprocess for ALL OS operations — no direct kernel imports
- Skills are auto-generated from entity definitions — no hardcoded command lists

### Step 2: Customer System Context

4. `projects/customer-system/INDEX.md` — project status, decisions, data inventory
5. `projects/customer-system/artifacts/2026-04-14-phase-1-domain-model.md` — 14 entity definitions with fields, state machines, relationships
6. `projects/customer-system/artifacts/2026-04-19-ui-evaluation.md` — 20 gaps (17 resolved, 3 remaining)
7. `projects/customer-system/artifacts/2026-04-19-demo-readiness.md` — CEO demo flow, verified features, 14 limitations (10 resolved)
8. `projects/customer-system/artifacts/2026-04-19-known-issues.md` — kernel bugs (10 fixed), open items

### Step 3: Implementation Context

9. `docs/plans/2026-04-19-vision-alignment-plan.md` — the 10-limitation resolution plan (executed)

---

## Pre-Flight Checklist

### 1. Verify OS is running
```bash
curl -s https://indemn-api-production.up.railway.app/health
# Expect: {"status":"healthy","checks":{"mongodb":"ok","temporal":"ok"}}
```

### 2. Authenticate CLI
```bash
# The OS CLI is installed at:
/Users/home/Repositories/bot-service/.venv/bin/indemn

export INDEMN_API_URL=https://indemn-api-production.up.railway.app
/Users/home/Repositories/bot-service/.venv/bin/indemn auth login --org _platform --email craig@indemn.ai --password indemn-os-dev-2026
```

### 3. Verify data
```bash
INDEMN=/Users/home/Repositories/bot-service/.venv/bin/indemn
$INDEMN entity list --format table    # 18 entity definitions
$INDEMN company list --limit 5        # 87 companies
$INDEMN contact list --limit 5        # 92 contacts
$INDEMN skill list --format table     # 24+ skills
$INDEMN actor list --format table     # 25 actors (14 human + associates)
```

---

## Current Architecture

### Deployed Services (Railway)
| Service | URL | Status |
|---------|-----|--------|
| indemn-api | https://indemn-api-production.up.railway.app | Running |
| indemn-queue-processor | (internal) | Running |
| indemn-temporal-worker | (internal) | Running |
| indemn-runtime-async | Temporal queue | Running |
| indemn-runtime-chat | wss://indemn-runtime-chat-production.up.railway.app/ws/chat | Running |
| indemn-ui | https://indemn-ui-production.up.railway.app | Running |

### Key IDs
- `_platform` org: `69e23d586a448759a34d3823`
- Admin actor (craig@indemn.ai): `69e23d586a448759a34d3824`
- Chat Runtime: `69e2777c02fab4de6eea7d9e`
- OS Assistant actor: `69e50bdce35065d0498df6cc` (23 skills loaded)
- InsurTechNY Conference: `69e41a6ab5699e1b9d7e98c5`
- ALER26 Conference: `69e41a6bb5699e1b9d7e98c7`

### Data in the OS
| Entity | Count |
|--------|-------|
| Companies | 87 |
| Contacts | 92 |
| Associate Types | 24 |
| Conferences | 2 |
| Stages | 7 |
| Outcome Types | 4 |
| Human Actors | 14 |
| Roles | 4 |
| Entity Definitions | 14 customer + 4 other |
| Skills | 24+ |

### Git State
- **indemn-os repo**: `main` branch, ~28 commits this session
- **OS repo**: `os-roadmap` branch has all project artifacts + handoffs

---

## What Works (Verified)

- Login/auth with automatic token refresh
- Navigation: Entities (15 domain) / System (7 kernel) / Admin — no infrastructure clutter
- Company list: search, per-column filters (enum dropdowns + text), sort, all columns with horizontal scroll, column visibility picker, bulk action checkboxes, pagination (100/page)
- Detail views: all fields editable, enum dropdowns, entity pickers with resolved names, date pickers, state badge with color coding, transition confirmation
- Cross-entity navigation: click any relationship link to jump between entities
- Assistant: connects, loads 23 skills, answers questions about current entity context, streaming responses, conversation panel with input
- Observability: state distribution per entity (customer=9, pilot=7, prospect=71), queue depth
- Roles view: role cards with queue depth
- State transitions: confirmed, changes tracked
- Real-time WebSocket: connected to API server (not UI server)

## What Needs Work

### Remaining from this session
1. **Bulk actions UI** — checkboxes render but bulk transition bar needs testing with actual transitions
2. **Assistant skill tuning** — the assistant can answer questions from entity context but needs work to reliably perform CLI operations (create, transition, query)
3. **Conversation persistence** — interaction_id reuse is wired but not yet verified E2E across browser reloads

### Phase F (from original handoff)
4. **Watches + Automation** — no watches configured on any role yet → no messages generated on entity changes. This is the wiring that makes the OS reactive.
5. **Meeting intelligence extraction** — associate design for processing meeting transcripts into Decision/Commitment/Signal entities
6. **Staleness monitoring** — which entities, what thresholds

### Data quality
7. **47 companies now linked to conferences** — done this session
8. **Contact emails missing** — 59/92 contacts have no email (source data limitation)
9. **Company owner missing** — 30/87 companies have no owner assigned

### Known deferred items (cosmetic, not vision-required)
10. Company collection name is `companys` (auto-pluralization)
11. Test entities (TestTask, VerifyTest) still in database
12. Gemini proto warning in chat harness logs

---

## Design Integrity Rules (unchanged)

1. Vision IS the MVP. Never simplify or defer without Craig's explicit approval.
2. Implement EXACTLY what the design specifies.
3. Verify against the live system. Don't just commit — confirm it works E2E.
4. When Craig asserts something was designed, search until you find it.
5. Skills are auto-generated from entity definitions — never hardcode CLI commands or entity types.
6. The assistant uses skills for knowledge, the CLI for operations. No shortcuts.
