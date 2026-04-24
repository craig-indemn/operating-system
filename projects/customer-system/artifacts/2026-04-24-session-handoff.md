---
ask: "Handoff from 2026-04-24 session — orient the next session on vision, context, and current state"
created: 2026-04-24
workstream: customer-system
session: 2026-04-24-roadmap
---

# Session Handoff — 2026-04-24

Next session reads this first to get oriented, then works through the reading list below.

## Objective

Build the customer operating system. Emails + meetings flow through the pipeline → entities populate (Company, Contact, Touchpoint, Tasks, Decisions, Signals, Commitments, Operations, Opportunities, Proposal, Phase) → the playbook running against the current entity state for each customer renders the next artifact. Follow-up email for an early-stage meeting. Proposal draft for a mature one. Task list for delivery. Same mechanism, different outputs depending on state.

First concrete proof point in flight: draft follow-up emails for Foxquilt (Apr 22 exec call with Karim Jamal) and GR Little (Apr 22 discovery with Walker Ross), generated from what the OS extracts. Kyle wants to compare to what he'd have sent and iterate.

## Philosophical frame (from today's refinement)

These four principles are load-bearing for every design and execution decision going forward. Internalize them before acting.

### 1. The playbook IS the entity model IS the proposal IS the follow-up email

There is no "email drafter" or "proposal generator" as a standalone feature. There is one system: interactions come in, entities populate, the playbook running against the current entity state renders whatever artifact is appropriate right now. The same substrate produces a follow-up email for an early-stage meeting, a proposal for a mature deal, a task list for an active delivery. Previous session's artifact `2026-04-23-playbook-as-entity-model.md` locked this in.

Consequence: don't build bespoke associates per artifact type. Build the playbook as state + rendering.

### 2. Kyle's detailed specs are aspirational signal, not implementation requirements

Kyle is CEO, uses Claude Code to generate very detailed documents (field-level enums, JSON schemas, phased project plans with Friday deadlines). These read like specs but are not — he doesn't have the systems context to write the entity model for us. Pattern-matching on them as requirements wastes time debating schema before outputs exist.

What to do: extract the *intent* (what outcomes does he want to see?) and ignore the implementation detail. Show concrete output, let Kyle react to reality. His Apr 23 verbal conversation is cleaner signal than his Apr 24 written prep doc.

### 3. The ledger is authoritative — don't speculate when data can answer

Today's Company-duplication diagnosis went in circles until we actually queried the changes collection. The answer was there the whole time — 444 of 446 creations attributed to Platform Admin actor, all standalone (no upstream message cascade). Stop theorizing about LLM instruction quality and read the ledger first.

### 4. Refining thinking IS progress

Visible output isn't the only progress. Today we fixed two adapter/CLI bugs, documented 28 OS bugs, surfaced the "playbook = entity model" framing in a way that reshapes the architecture going forward, and cleaned up 133 of 446 Company duplicates. The remaining cleanup was blocked by Bug #23 (bulk-delete drops MongoDB operators) — a bug we'd never have found without actually trying to use the system at scale. That finding matters more than another deleted record would have.

## Reading protocol

### Required — OS foundation

1. **`/Users/home/Repositories/indemn-os/CLAUDE.md`** — builder's manual: entity definitions, watches, associates, rules, integrations, auth, debugging, CLI reference. Start here for how the OS actually works.
2. **`/Users/home/Repositories/indemn-os/docs/white-paper.md`** — full canonical vision. Long (993 lines) but load-bearing for understanding what we're building, why modular-monolith, why CLI-first, the six primitives, the self-evidence property. The "North Star" document.
3. **`docs/architecture/overview.md`** — system architecture: trust boundary, dispatch pattern, deployment topology. Read after CLAUDE.md for the full picture.
4. **`docs/architecture/entity-framework.md`** — how entities work end-to-end: save_tracked(), state machines, computed fields, the dynamic class factory. Critical for any entity modeling work.
5. **`docs/architecture/associates.md`** — actor model, skills as markdown programs, harness pattern (CLI subprocess, not SDK), async and real-time execution. Read before touching any associate work.
6. **`docs/architecture/watches-and-wiring.md`** — the nervous system: watch events, condition language, the unified queue, cascade propagation. This is how the system *runs*.
7. **`docs/architecture/rules-and-auto.md`** — rule engine, lookups, kernel capabilities, the `--auto` pattern. Essential for the "deterministic first, LLM fallback" discipline.
8. **`docs/architecture/integrations.md`** — adapters, credential resolution, inbound webhooks, content visibility. You'll touch this any time you connect external systems.
9. **`docs/guides/domain-modeling.md`** — the 8-step process we use to build any domain on the OS (includes worked examples). Our process.

### Required — Current project state

10. **`projects/customer-system/INDEX.md`** — the project's source of truth for resume. Current status, deals, decisions, open questions, all artifacts listed.

### Required — Today's session (2026-04-24)

11. **`projects/customer-system/artifacts/2026-04-24-session-handoff.md`** — this file.
12. **`projects/customer-system/artifacts/2026-04-24-alignment-framing.md`** — the lens through which we interpret Kyle's prep doc. How to talk to him, how to pushback respectfully, how to extract intent without debating schema.
13. **`projects/customer-system/artifacts/2026-04-24-kyle-craig-apr23-sync.md`** — Apr 23 Kyle+Craig transcript. The cleaner signal of what Kyle actually wants. Read before the Apr 24 prep doc.
14. **`projects/customer-system/artifacts/2026-04-24-kyle-prep-doc-apr24.md`** — Kyle's written prep doc for the scheduled (but not-yet-held) Apr 24 sync. Preserved but framed: treat as aspirational signal, not spec. Contains two JSON-shaped extractions of the Foxquilt + GR Little meetings that represent the output he wants to see, plus a 3-phase plan we're NOT committing to as written.
15. **`projects/customer-system/artifacts/2026-04-24-os-bugs-and-shakeout.md`** — 28 OS bugs surfaced by dogfooding. Bug #23 (bulk-delete drops MongoDB operators) is the critical blocker for cleanup. Bug #16 + #22 (associates auto-create companies + service-token untraceability) are the critical blockers for running the pipeline reliably.

### Required — Entity model (the spec we're working to)

16. **`projects/customer-system/artifacts/2026-04-22-entity-model-brainstorm.md`** — field-level spec for all 22 entities we designed. The current entity model on the live OS.
17. **`projects/customer-system/artifacts/2026-04-22-entity-model-design-rationale.md`** — WHY the entity model looks the way it does. Tradeoffs, rejected alternatives, how it fits the OS vision. Read if the brainstorm alone leaves "why this and not that" questions.
18. **`projects/customer-system/artifacts/2026-04-23-playbook-as-entity-model.md`** — **the key insight:** the entity model IS the playbook. Gaps drive next steps. Proposal emerges when entities are complete enough. This reframes the whole project.

### Required — Prior session implementation context

19. **`projects/customer-system/artifacts/2026-04-23-implementation-session.md`** — what was built in the prior session (Apr 22-23). Most of the current running state.
20. **`projects/customer-system/artifacts/2026-04-23-pipeline-operations-guide.md`** — how to run, monitor, and troubleshoot the pipeline. Auth patterns, CLI commands, Temporal management, known issues. Read before operating anything.

### Required — Original problem + vision (from 2026-04-14 kickoff)

21. **`projects/customer-system/artifacts/2026-04-14-problem-statement.md`** — 7 concepts with evidence. Why we're building this. What the team said is broken.
22. **`projects/customer-system/artifacts/2026-04-14-system-capabilities.md`** — 17 functional areas, ~130 capabilities, attributed to sources. The full scope of what the system eventually needs to do.
23. **`projects/customer-system/artifacts/2026-04-14-vision-and-trajectory.md`** — phased roadmap shared with Kyle and Cam. Where we said we're going.
24. **`projects/customer-system/artifacts/context/2026-04-14-craigs-brain-dump.md`** — Craig's raw notes from conversations with Kyle, George, Ganesh. Craig's original synthesis.
25. **`projects/customer-system/artifacts/context/2026-04-21-kyle-craig-call-transcript.txt`** — Apr 21 call: prospect strategy, deal priorities, use-Craig-as-guinea-pig idea. The other critical Kyle conversation besides the Apr 23 one.

### Required — Kyle's operational context (trimmed)

26. **`projects/customer-system/artifacts/context/kyle-exec/PLAYBOOK-v2.md`** — Kyle's sales motion playbook: stages, signals, cadence, the "Rocky problem," the associate's job per deal. Maps directly to our playbook concept. Required.
27. **`projects/customer-system/artifacts/context/kyle-exec/PROSPECT-SIX-LEADS-v0.md`** — the 6 active prospects (FoxQuilt, Alliance, Amynta, Rankin, Tillman, O'Connor). Concrete context for any work on deals or prospect data.

### Required — OS design synthesis

28. **`projects/product-vision/CLAUDE.md`** — product-vision project orientation, session bootstrap, design integrity rules. Sibling to the OS CLAUDE.md but focused on the WHY.
29. **`projects/product-vision/artifacts/2026-04-16-vision-map.md`** — 23-section authoritative synthesis of 104 design files. Replaces reading individual design artifacts. The authoritative design-layer statement.

### On demand — read if a specific question arises

**OS architecture deep-dives** (skip unless debugging the specific area):
- `docs/architecture/realtime.md` — voice/chat harness internals, Attention entity
- `docs/architecture/authentication.md` — Session entity, JWT details, MFA
- `docs/architecture/infrastructure.md` — Railway topology, scaling
- `docs/architecture/security.md` — OrgScopedCollection, credential management, audit trail
- `docs/architecture/observability.md` — changes collection schema, OTEL spans

**OS how-to guides** (skip unless doing that specific kind of work):
- `docs/guides/adding-entities.md`
- `docs/guides/adding-associates.md`
- `docs/guides/adding-watches.md`
- `docs/guides/adding-integrations.md`
- `docs/guides/development.md`
- `docs/getting-started.md`

**Kyle EXEC on-demand** — **explicitly deprioritized** per today's framing: Kyle's detailed schema docs are aspirational signal, not implementation spec. Reading them upfront risks the next session treating them as requirements:
- `kyle-exec/DICT-PROSPECTING-v2.md`
- `kyle-exec/DICT-SALES-v2.md`
- `kyle-exec/DICT-CUSTOMER-SUCCESS-v2.md`
- `kyle-exec/MAP.md` (30 workstreams across 5 pillars — tangential to customer system work)

**Superseded or administrative:**
- `2026-04-14-source-inventory.md` — administrative, where docs came from
- `2026-04-14-phase-1-domain-model.md` — superseded by 2026-04-22 brainstorm
- `2026-04-21-session-handoff.md` — superseded by this one
- `2026-04-21-meeting-ingestion-session.md` — superseded by impl-session + ops-guide
- `2026-04-21-deal-entity-evolution.md` — deal entity changes already incorporated
- `2026-04-21-action-items.md` — superseded by today's next-steps
- `2026-04-23-system-flow-v4.html` — visual diagram for Kyle (reference only)

## Current state (concrete)

**Services (as of 2026-04-24 ~13:00 EDT):**
| Service | URL |
|---------|-----|
| API | `https://api.os.indemn.ai` |
| UI | `https://os.indemn.ai` |
| Chat Runtime | `wss://indemn-runtime-chat-production.up.railway.app/ws/chat` |

**Associates:**
- Email Classifier — **suspended** (id `69ea1bca23eefe641ea13f44`)
- Touchpoint Synthesizer — **suspended** (id `69ea1bd123eefe641ea13f48`)
- Intelligence Extractor — **suspended** (id `69ea1bd223eefe641ea13f4c`)
- OS Assistant — **active** (id `69e50bdce35065d0498df6cc`)

**Data:**
- Meetings: 72 (67 freshly ingested today for last 7 days, including Foxquilt + GR Little Apr 22)
- Emails: ~1136 (from prior sessions' backfill)
- Contacts: 420
- Companies: 313 (partial cleanup — target ~90; blocked by Bug #23)
- Deals: 7 (6 prospect + 1 IIANC)
- Meeting touchpoints: 0 (cleared during session)
- Email touchpoints: 69 (not touched)
- Dead letters: 9 (not purged — blocked by Bug #23)

**Critical identifiers:**
- `_platform` org: `69e23d586a448759a34d3823`
- Platform Admin actor: `69e23d586a448759a34d3824`
- Kyle Geoghan actor: `69e7d26f23eefe641ea13e47`
- Google Workspace Integration: `69e7a018bd939892d8e7a2a5`
- Foxquilt meeting (Apr 22 exec call): `69eb94a92b0a50861892382d`
- GR Little meeting (Apr 22 discovery): `69eb94a92b0a50861892382a`
- Apr 17 Nick discovery (Foxquilt provenance): `69eb94a92b0a508618923843`
- "Fox Quilt" Company (Apr 18 baseline, linked to FOXQUILT-2026 deal): `69e41a8eb5699e1b9d7e991d`

## Known bugs

Full list in `projects/customer-system/artifacts/2026-04-24-os-bugs-and-shakeout.md`. Four critical/high-severity ones worth flagging inline:

- **#23 (Critical):** `bulk-delete` silently drops MongoDB operator filters (`$in`, `$gte`, `$ne`, `$oid`). Blocks any non-trivial cleanup. Must fix before doing more bulk operations at scale.
- **#16 (High):** Associates auto-create Company records despite skill saying never. 446 companies created vs ~90 legit. Root cause not yet identified.
- **#17 (High):** No meeting-to-company classifier in pipeline. Synth skill assumes `meeting.company` is set; fetch_new leaves it null. Pipeline works accidentally when synth-LLM matches company on its own, fails when it doesn't.
- **#22 (High):** Service token untraceability — all associates authenticate as Platform Admin, can't tell which one acted when forensics are needed.

Fixed today: #1 (adapter date filter), #14 (CLI timeout).

## Authentication pattern

```bash
TOKEN=$(curl -s -X POST https://api.os.indemn.ai/auth/login \
  -H "Content-Type: application/json" \
  -d '{"org_slug": "_platform", "email": "craig@indemn.ai", "password": "indemn-os-dev-2026"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

INDEMN_API_URL=https://api.os.indemn.ai INDEMN_SERVICE_TOKEN="$TOKEN" INDEMN_CLI_TIMEOUT=600 \
  uv run indemn <command>
```

Direct MongoDB (the AWS secret at `indemn/dev/shared/mongodb-uri` has a wrong URI — Bug #12):

```bash
mongosh "mongodb+srv://dev-indemn:wJnKmz4P0q39GpXZ@dev-indemn.mifra5.mongodb.net/indemn_os" --quiet --eval '...'
```

## What was committed to git today

On `indemn-os` main (deployed via `railway up --service indemn-api`):

```
f0dfe89 fix(cli): bump POST/PUT timeout to 600s, configurable via INDEMN_CLI_TIMEOUT
8afda9d fix(google_workspace): normalize 'since' to RFC3339 before Meet API filter
```

On `operating-system` `os-roadmap` branch:

```
16ee6e2 project(customer-system): add bugs #22-28 to shakeout artifact
e9c16b9 project(customer-system): session 2026-04-24 artifacts
```

## Kyle meeting status

The Apr 24 sync did not happen during today's session. Kyle is expecting a demo of draft follow-up emails for the Apr 22 Foxquilt + GR Little meetings. When that sync happens, re-anchor on his Apr 23 verbal ask ("mock up a follow-up email to see how closely it aligns with what I would have sent") rather than his Apr 24 written prep doc.
