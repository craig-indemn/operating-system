---
ask: "Unified handoff — all context, all work, what's next for any session continuing the customer system"
created: 2026-04-21
workstream: customer-system
session: 2026-04-21-roadmap
---

# Unified Session Handoff — Customer System

## For Any Session Continuing This Work

This handoff covers EVERYTHING — the context from multiple sessions, brainstorming, Kyle's documents, and what's been built. Read it all.

---

## Reading Protocol — MANDATORY

### 1. The System (what's built)
- `/Users/home/Repositories/indemn-os/CLAUDE.md` — the OS builder's manual
- `projects/customer-system/INDEX.md` — full project status, decisions, what's next

### 2. The Context (why we're building this)
- `projects/customer-system/artifacts/2026-04-14-problem-statement.md` — 7 concepts with evidence
- `projects/customer-system/artifacts/2026-04-14-system-capabilities.md` — 17 areas, ~130 capabilities
- `projects/customer-system/artifacts/2026-04-14-vision-and-trajectory.md` — phased roadmap shared with Kyle
- `projects/customer-system/artifacts/context/2026-04-14-craigs-brain-dump.md` — Craig's raw notes from team conversations
- `projects/customer-system/artifacts/context/2026-04-14-source-inventory.md` — all 28+ source documents inventoried

### 3. Kyle's Vision (what Kyle wants)
- `projects/customer-system/artifacts/context/kyle-exec/PLAYBOOK-v2.md` — Kyle's operating playbook
- `projects/customer-system/artifacts/context/kyle-exec/DICT-PROSPECTING-v2.md` — prospecting data dictionary
- `projects/customer-system/artifacts/context/kyle-exec/DICT-SALES-v2.md` — sales data dictionary
- `projects/customer-system/artifacts/context/kyle-exec/DICT-CUSTOMER-SUCCESS-v2.md` — customer success data dictionary
- `projects/customer-system/artifacts/context/kyle-exec/PROSPECT-SIX-LEADS-v0.md` — the 6 active prospects
- `projects/customer-system/artifacts/context/kyle-exec/MAP.md` — Kyle's relationship map

### 4. What Was Built (recent sessions)
- `projects/customer-system/artifacts/2026-04-21-session-handoff.md` — parallel session: Deal entity, SuccessPhase, UI, domains, CLI
- `projects/customer-system/artifacts/2026-04-21-meeting-ingestion-session.md` — roadmap session: Google Meet adapter, Employee entity, actor cleanup
- `projects/customer-system/artifacts/2026-04-21-deal-entity-evolution.md` — how Deal entity was designed
- `projects/customer-system/artifacts/2026-04-21-action-items.md` — prioritized action items from session 2
- `projects/customer-system/artifacts/2026-04-14-phase-1-domain-model.md` — the original 14-entity domain model

### 5. OS Vision (when making architectural decisions)
- `projects/product-vision/artifacts/2026-04-16-vision-map.md` — authoritative 23-section OS design synthesis
- `projects/product-vision/CLAUDE.md` — session bootstrap, design integrity rules

---

## What's Deployed

| Service | URL |
|---------|-----|
| API | https://api.os.indemn.ai |
| UI | https://os.indemn.ai |
| Chat Runtime | wss://indemn-runtime-chat-production.up.railway.app/ws/chat |

CLI: `indemn auth login --org _platform --email craig@indemn.ai --password indemn-os-dev-2026`

---

## What's In The System

### Entities
| Entity | Count | Key Fields |
|--------|-------|------------|
| Company | 88 | name, stage (prospect→customer→churned), ARR, industry |
| Contact | 92 | name, email, company, role, how_met |
| Deal | 6 | deal_id, company, stage, next_step, next_step_owner, use_case |
| SuccessPhase | 0 | deal, phase_number, name, entry_criteria, go_no_go_signal |
| Meeting | 19 | title, date, duration, participants, transcript, notes, summary, organizer |
| Employee | 15 | name, email, title, google_user_id, slack_id, actor_id |
| Task | 0 | title, description, company, assignee, due_date, priority, source_meeting |
| Decision | 0 | description, company, source_meeting, decided_by, rationale |
| Signal | 0 | description, company, source_meeting, type, severity |
| Commitment | 0 | description, company, source_meeting, made_by, due_date |

### People
- 15 Employees seeded (Craig, Kyle, Cam, Dhruv, Ganesh, George Remmer, Peter, Jonathan, Ian, Dolly, Rudra, Marlon, Kai, Rocky, George Redenbaugh)
- 15 Actors cleaned up and active
- Kyle has `executive` role (read most entities, write Company/Deal/Task/Employee)
- Craig has `platform_admin` + `team_member` (full access)

### Integrations
- Google Workspace Integration (active) — domain-wide delegation, Meet API + Calendar API + Admin SDK
- `indemn meeting fetch-new` pulls meetings from all domain users

### Kyle's 6 Deals
| Deal | Company | Stage | Next Step |
|------|---------|-------|-----------|
| FOXQUILT-2026 | Fox Quilt | demo | Schedule follow-up demo |
| ALLIANCE-2026 | Alliance Insurance | proposal | Lock May meeting. Pricing decision. |
| AMYNTA-GRD360-2026 | Amynta | discovery | Post-demo debrief. ICP confirmation. |
| RANKIN-2026 | Rankin Insurance | signed | Formalize expansion contract. |
| TILLMAN-2026 | Tillman Insurance | discovery | Verify actual state. Did go-live happen? |
| OCONNOR-2026 | O'Connor Insurance | signed | Ground-truth from Cam. At risk? |

---

## What's NOT Done Yet

1. **Employee resolution in meetings** — match participants to Employee + Contact entities
2. **Meeting classification** — customer vs internal, link to Companies
3. **Extraction associate** — process meetings into Tasks, Decisions, Signals, Commitments
4. **Full 30-day meeting backfill** — only April 20-21 ingested (Meet API records expire after 30 days)
5. **SuccessPhase data** — entity exists, 0 records
6. **Watches/automations** — zero configured
7. **UI: [object Object]** — participants list renders incorrectly in table
8. **Granola integration** — some meetings use Granola, not Google transcription

---

## Design Integrity Rules

1. **Vision IS the MVP.** Never simplify or defer without Craig's explicit approval.
2. **The entity command IS the interface.** `indemn meeting fetch-new` dispatches through Integration automatically.
3. **Employee is domain data, Actor is OS infrastructure.** Employee links to Actor via actor_id.
4. **Company matching and meeting classification are post-processing** — associate job, not adapter.
5. **One associate for full meeting pipeline** — fetch + extract (not split into two).
6. **Always use the CLI for OS operations**, not direct API calls.
