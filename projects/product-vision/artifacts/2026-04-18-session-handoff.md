---
ask: "Session handoff — OS wiring complete, customer system ready to build. Everything the next session needs."
created: 2026-04-18
workstream: product-vision
session: 2026-04-18-a
sources:
  - type: codebase
    ref: "/Users/home/Repositories/indemn-os"
    description: "All kernel + harness + CLI + UI code"
  - type: project
    ref: "projects/customer-system"
    description: "Customer system domain model, setup scripts, data"
  - type: artifact
    ref: "2026-04-17-wiring-audit.md"
    description: "139-behavior audit — all items resolved"
---

# Session Handoff — 2026-04-18

## What This Session Did

1. **Comprehensive wiring audit**: 10 parallel agents audited 139 designed behaviors across all subsystems. Found 13 UNWIRED, 27 PARTIAL, 6 BUGS.
2. **Fixed everything**: 7 parallel waves of implementation. Code reviewed twice. 2 blockers caught and fixed (test file 3-tuple, PyJWT dependency).
3. **Deployed and verified E2E**: All 6 Railway services. 29/29 tests pass (14 API, 10 browser, 5 chat harness including conversation persistence).
4. **Built `indemn init`**: CLI command that scaffolds any project for OS development.
5. **Updated OS documentation**: Entity criteria (7 tests), kernel-vs-domain separation, developer setup.
6. **Rewrote customer-system setup scripts**: All 14 entity definitions corrected to match actual CLI syntax.
7. **Fixed chat harness checkpointer**: Static IP was missing on Railway service. Switched from pymongo to motor (async driver). Conversation persistence now works.

## What the Next Session Does

**Build the customer system on the live OS.** This is the first real domain — 14 entities, 87 companies, 92 contacts, the Indemn team as actors. It proves the OS works for real and refines the domain modeling process.

---

## Reading Protocol for Next Session

### Step 1: OS Technical Context (~5 min)
Read these to understand what the OS is and how to build on it:

1. `/Users/home/Repositories/indemn-os/CLAUDE.md` — the builder's manual (entity types, field syntax, watches, rules, associates, debugging, entity criteria, developer setup)
2. `projects/product-vision/artifacts/2026-04-16-vision-map.md` — 23-section authoritative design (only if you need architectural context beyond the CLAUDE.md)

### Step 2: Customer System Context (~10 min)
Read these to understand what we're building:

3. `projects/customer-system/INDEX.md` — project status, decisions, data inventory, open questions
4. `projects/customer-system/artifacts/2026-04-14-phase-1-domain-model.md` — 14 entity definitions with fields, state machines, relationships
5. `projects/customer-system/artifacts/2026-04-14-domain-model-thinking.md` — entity criteria framework, design principles, what the kernel handles
6. `projects/customer-system/artifacts/2026-04-14-problem-statement.md` — why we're building this, success criteria

### Step 3: Setup Scripts (~2 min)
Scan these — they're the execution plan:

7. `projects/customer-system/data/setup/01-bootstrap.sh` through `05-seed.sh`
8. `projects/customer-system/data/import/` — CSV files ready for bulk import

### Step 4: Skills and Process
9. The `indemn init` command scaffolds `.claude/` with the domain-modeling skill and OS builder guide. Run it in the working directory if not already done.
10. `.claude/skills/domain-modeling/SKILL.md` in the OS repo — the refined 8-step process

---

## Pre-Flight Checklist (do these before building)

### 1. Verify OS is running
```bash
curl -s https://indemn-api-production.up.railway.app/health
# Expect: {"status":"healthy","checks":{"mongodb":"ok","temporal":"ok"}}
```

### 2. Install CLI (editable, from repo)
```bash
cd /Users/home/Repositories/indemn-os/indemn_os
pip install -e .
```

### 3. Authenticate
```bash
export INDEMN_API_URL=https://indemn-api-production.up.railway.app
indemn auth login --org _platform --email craig@indemn.ai --password indemn-os-dev-2026
```

### 4. Verify CLI works
```bash
indemn entity list          # Should show TestTask, Interaction, VerifyTest
indemn actor list            # Should show craig, kyle, test actors
indemn skill list            # Should show 7 kernel entity skills
indemn platform health       # API + MongoDB + Temporal status
```

### 5. Initialize project (if working in a separate directory)
```bash
indemn init                  # Creates .claude/ with OS context + domain-modeling skill
```

---

## Execution Plan

### Phase A: Entity Definitions
Run `04-entities.sh` — creates all 14 entity types. After each entity:
- Verify: `indemn <entity> list` works
- Verify: skill auto-generated (`indemn skill get <Entity>`)
- Verify: UI shows the entity in navigation

### Phase B: Actors + Roles
Run `02-actors.sh` then `03-roles.sh`:
- Creates 13 team members as human actors
- Each gets a `setup_token` for password setup
- Creates `team_member` role with full access
- Grants role to all actors

### Phase C: Seed Data
Run `05-seed.sh` — reference data (stages, outcome types, associate types):
- 24 associate types from the Four Outcomes product map
- 4 outcome types
- Pipeline stages with probability + staleness thresholds

### Phase D: Bulk Import
Import the prepared CSVs:
```bash
indemn company bulk-create --from-csv data/import/companies-merged.csv
indemn contact bulk-create --from-csv data/import/contacts-merged.csv
indemn conference bulk-create --from-csv data/import/conferences.csv
```

### Phase E: Validate
- `indemn company list` — 87 companies
- `indemn contact list` — 92 contacts
- Transition a company: `indemn company transition <id> --to pilot`
- Trace it: `indemn trace entity Company <id>`
- Open the UI: verify all entity types in navigation, data renders, transitions work

### Phase F: Watches + Automation (design with Craig)
- What should trigger notifications?
- When a Deal hits "verbal", who gets notified?
- Staleness monitoring: which entities, what thresholds?
- Meeting intelligence extraction: associate design

---

## Known State

### Deployed Services (all healthy)
| Service | Status | URL |
|---------|--------|-----|
| indemn-api | Running | https://indemn-api-production.up.railway.app |
| indemn-queue-processor | Running | (internal) |
| indemn-temporal-worker | Running | (internal) |
| indemn-runtime-async | Running | Temporal queue |
| indemn-runtime-chat | Running | wss://indemn-runtime-chat-production.up.railway.app/ws/chat |
| indemn-ui | Running | https://indemn-ui-production.up.railway.app |

### Bootstrap Data in MongoDB
- `_platform` org: `69e23d586a448759a34d3823`
- Admin actor (craig@indemn.ai): `69e23d586a448759a34d3824`
- Kyle actor (kyle@indemn.ai): `69e28fedf508e1ceb69654c7`
- Async Runtime: `69e23d846a448759a34d3829`
- Chat Runtime: `69e2777c02fab4de6eea7d9e`
- 7 kernel entity skills uploaded
- TestTask, Interaction, VerifyTest entity definitions

### Credentials
All in AWS Secrets Manager under `indemn/dev/shared/`:
- `mongodb-uri`, `temporal-cloud`, `jwt-signing-key`, `grafana-otlp`
- `google-cloud-sa`, `anthropic-api-key`
- `runtime-async-service-token`, `runtime-chat-service-token`

### Git State
- **indemn-os repo**: `main` branch, latest commit includes `indemn init` + all wiring fixes
- **OS repo**: `os-roadmap` branch has this handoff + wiring audit artifact
- **Customer system**: `os-customer-system` branch has rewritten setup scripts

---

## Design Integrity Rules (unchanged)

1. Vision IS the MVP. Never simplify or defer without Craig's explicit approval.
2. Implement EXACTLY what the design specifies.
3. Verify against the live system. Don't just commit — confirm it works E2E.
4. When Craig asserts something was designed, search until you find it.

---

## What Could Go Wrong

1. **Setup scripts may hit API edge cases** — field type validation, state machine format, collection name conflicts. Fix in real time.
2. **Bulk import CSV format may not match** — the `--from-csv` flag on bulk-create may need specific column headers matching field names.
3. **Computed fields not yet supported** — Deal entity has composite_score, probability, weighted_value. These need to be added after base entity creation.
4. **Entity name collisions** — if any customer-system entity names collide with kernel entities (they shouldn't — we checked).
5. **The kernel may have bugs we haven't hit yet** — this is the first real domain. Expect to discover and fix issues.

The approach: run each script step by step, verify after each, fix what breaks, push fixes, redeploy, continue. This IS the process — building the first domain shakes out the OS.
