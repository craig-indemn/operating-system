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

### 1. The Operating System (READ THESE FIRST)
- `/Users/home/Repositories/indemn-os/CLAUDE.md` — the OS builder's manual (entity definitions, watches, associates, rules, integrations, auth, debugging, CLI)
- `/Users/home/Repositories/indemn-os/docs/white-paper.md` — the canonical vision document

**Architecture docs (in `/Users/home/Repositories/indemn-os/docs/architecture/`):**
- `overview.md` — system architecture, trust boundary, deployment topology
- `entity-framework.md` — how entities work, save_tracked, state machines, computed fields
- `associates.md` — how associates work, harness pattern, skills, progressive disclosure
- `watches-and-wiring.md` — how watches fire, condition language, scope qualifiers
- `integrations.md` — adapters, credentials, Integration entity, fetch patterns
- `realtime.md` — Runtime, Attention, harness pattern, mid-conversation events
- `authentication.md` — Session entity, JWT, service tokens, MFA, platform admin
- `rules-and-auto.md` — rules engine, --auto pattern, lookups
- `infrastructure.md` — Railway deployment, services, scaling, costs
- `security.md` — trust boundary, OrgScopedCollection, skill hash verification
- `observability.md` — OTEL traces, changes collection, correlation IDs

**How-to guides (in `/Users/home/Repositories/indemn-os/docs/guides/`):**
- `adding-entities.md` — step-by-step for creating entity definitions
- `adding-associates.md` — creating associates with skills, roles, watches, runtime assignment
- `adding-watches.md` — watch configuration, events, conditions
- `adding-integrations.md` — building adapters, credentials, testing
- `domain-modeling.md` — the 8-step process for building any domain
- `development.md` — local dev, testing, CI, deployment
- `getting-started.md` (in `/docs/`) — first-time setup

**IMPORTANT: These docs are the source of truth for how the OS works.** Read the relevant guide BEFORE implementing. Many bugs in this session came from not understanding the harness architecture documented in `associates.md`.

### 1b. Customer System Project Status
- `projects/customer-system/INDEX.md` — full project status, decisions, what's next

### 2. The Context (why we're building this)
- `projects/customer-system/artifacts/2026-04-14-problem-statement.md` — 7 concepts with evidence
- `projects/customer-system/artifacts/2026-04-14-system-capabilities.md` — 17 areas, ~130 capabilities
- `projects/customer-system/artifacts/2026-04-14-vision-and-trajectory.md` — phased roadmap shared with Kyle
- `projects/customer-system/artifacts/context/2026-04-14-craigs-brain-dump.md` — Craig's raw notes from team conversations
- `projects/customer-system/artifacts/context/2026-04-14-source-inventory.md` — all 28+ source documents inventoried
- `projects/customer-system/artifacts/context/2026-04-21-kyle-craig-call-transcript.txt` — **LATEST**: full 40K transcript of Craig+Kyle call on Apr 21 covering prospect strategy, deal priorities, next phase requirements

### 3. Kyle's Vision (what Kyle wants)
- `projects/customer-system/artifacts/context/kyle-exec/PLAYBOOK-v2.md` — Kyle's operating playbook
- `projects/customer-system/artifacts/context/kyle-exec/DICT-PROSPECTING-v2.md` — prospecting data dictionary
- `projects/customer-system/artifacts/context/kyle-exec/DICT-SALES-v2.md` — sales data dictionary
- `projects/customer-system/artifacts/context/kyle-exec/DICT-CUSTOMER-SUCCESS-v2.md` — customer success data dictionary
- `projects/customer-system/artifacts/context/kyle-exec/PROSPECT-SIX-LEADS-v0.md` — the 6 active prospects
- `projects/customer-system/artifacts/context/kyle-exec/MAP.md` — Kyle's relationship map

### 4. Entity Model + Implementation (latest work)
- `projects/customer-system/artifacts/2026-04-22-entity-model-brainstorm.md` — Field-level specs for all 22 entities, implementation plan, associate wiring
- `projects/customer-system/artifacts/2026-04-22-entity-model-design-rationale.md` — WHY the model is designed this way, tradeoffs, OS vision fit, associate skills
- `projects/customer-system/artifacts/2026-04-23-playbook-as-entity-model.md` — KEY INSIGHT: the entity model IS the playbook, gaps drive next steps, proposal emerges when complete
- `projects/customer-system/artifacts/2026-04-23-implementation-session.md` — **LATEST**: full session record — what was built, infrastructure fixes, learnings, what's next
- `projects/customer-system/artifacts/2026-04-23-system-flow-v4.html` — Visual diagram for Kyle

### 5. Pipeline Operations (how to run the system)
- `projects/customer-system/artifacts/2026-04-23-pipeline-operations-guide.md` — auth, CLI commands, email/meeting fetch, queue monitoring, Temporal management, concurrency, Railway deployment, known issues, troubleshooting

### 6. What Was Built (recent sessions)
- `projects/customer-system/artifacts/2026-04-21-session-handoff.md` — parallel session: Deal entity, SuccessPhase, UI, domains, CLI
- `projects/customer-system/artifacts/2026-04-21-meeting-ingestion-session.md` — roadmap session: Google Meet adapter, Employee entity, actor cleanup
- `projects/customer-system/artifacts/2026-04-21-deal-entity-evolution.md` — how Deal entity was designed
- `projects/customer-system/artifacts/2026-04-21-action-items.md` — prioritized action items from session 2
- `projects/customer-system/artifacts/2026-04-14-phase-1-domain-model.md` — the original 14-entity domain model

### 7. OS Vision (when making architectural decisions)
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

## What's In The System (as of Apr 24, 2026)

### Entities (26 total)
| Entity | Count | Notes |
|--------|-------|-------|
| Company | 88 | Root entity |
| Contact | 92+ | Growing via Email Classifier (auto-creates from emails) |
| Deal | 6 | Kyle's 6 prospects |
| Meeting | 20 | Apr 20-21 only (30-day backfill pending) |
| Employee | 15 | Full team |
| Email | ~930 | Full team week of Apr 21-24 |
| Document | 0 | Pending Drive adapter + attachment extraction |
| Touchpoint | 20+ | Auto-created from classified emails |
| Operation | 0 | Wave 4 — human enrichment |
| Opportunity | 0 | Wave 4 — human enrichment |
| Proposal | 0 | Wave 5 — proposal generation |
| Phase | 0 | Wave 5 — replaces SuccessPhase |
| Associate | 0 | Wave 5 — deployed instances |
| CustomerSystem | 0 | Wave 4 — human enrichment |
| BusinessRelationship | 0 | Wave 4 — human enrichment |
| Task | 20+ | Auto-extracted from touchpoints (real: "Ship Alliance proposal by Apr 26") |
| Decision | 4+ | Auto-extracted |
| Signal | 16+ | Auto-extracted |
| Commitment | 9+ | Auto-extracted |

### Associates (3 active)
| Associate | Role | Watches | Status |
|-----------|------|---------|--------|
| Email Classifier | email_classifier | Email created | Active, working |
| Touchpoint Synthesizer | touchpoint_synthesizer | Email→classified, Meeting created | Active, working |
| Intelligence Extractor | intelligence_extractor | Touchpoint created | Active, working |

### Integrations
- Google Workspace (active) — domain-wide delegation, Meet API + Calendar API + Admin SDK + Gmail API
- `indemn email fetch-new` pulls emails from any @indemn.ai user
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

## Kyle's Latest Context (Apr 23 Slack DMs)

Kyle's message to Craig: "I think we should take the two meetings from yesterday and build a dataset around them that we can trust as updates every time a sales call happens."

The two meetings: FoxQuilt (CEO Karim Jamal) and G.R. Little (Walker Ross agency). Kyle wants the system to automatically extract from every sales call: drafted emails, next steps, opportunity evaluation, resources to create.

This maps directly to our pipeline: Meeting → Touchpoint → Intelligence Extractor → Tasks, Decisions, Commitments, Signals. The "dataset" Kyle describes IS the entity population from our model.

Kyle also wants to connect on the OS before end of day — Craig has a sync at 3:30 PM with Kyle. See `artifacts/2026-04-23-system-flow-v4.html` for the diagram Craig can walk Kyle through.

## Instructions for Next Session

**CRITICAL: Read the OS docs BEFORE implementing anything.** The indemn-os repo has comprehensive architecture docs and how-to guides. Many bugs in the Apr 22-23 session came from not understanding how the harness loads skills, how Temporal dispatches workflows, and how deepagents progressive disclosure works. All of this is documented in the repo.

**Before executing, brainstorm with Craig.** Get alignment on approach before writing code. Craig wants to think through how things should work within the OS architecture, not just get things built.

**Next steps and how they connect to the vision:**

1. **Recurring email fetch** — the system should automatically ingest new emails for the whole team. This is how the timeline stays current without manual intervention. Use the OS scheduling mechanism (actors with `--trigger-schedule` cron).

2. **Alliance email backfill** — manually curate historical Alliance emails via `gog` CLI. This fills in the interaction timeline for Alliance going back to January so we can build the proposal from real data.

3. **Meeting backfill** — pull 30 days of meeting history. Combined with emails, this gives a complete interaction timeline.

4. **Wave 4: Human enrichment** — Craig populates Operations, Opportunities, CustomerSystem, BusinessRelationship for Alliance via CLI. This is the "understanding the business" layer that the playbook-as-entity-model insight describes.

5. **Wave 5: Proposal generation** — create Proposal + Phases for Alliance. An associate generates the proposal document from the entities. This is the culmination — proving that the entity model IS the playbook and the proposal emerges from it.

Each step builds on the previous. The vision: every interaction teaches us something, entities get populated, gaps drive next steps, and when the picture is complete enough, the proposal materializes.

## Design Integrity Rules

1. **Vision IS the MVP.** Never simplify or defer without Craig's explicit approval.
2. **The entity command IS the interface.** `indemn meeting fetch-new` dispatches through Integration automatically.
3. **Employee is domain data, Actor is OS infrastructure.** Employee links to Actor via actor_id.
4. **Company matching and meeting classification are post-processing** — associate job, not adapter.
5. **One associate for full meeting pipeline** — fetch + extract (not split into two).
6. **Always use the CLI for OS operations**, not direct API calls.
