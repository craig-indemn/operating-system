---
ask: "Prioritized action list for the implementation session — UI improvements, bug fixes, access, and next features"
created: 2026-04-21
workstream: customer-system
session: 2026-04-21-a
sources:
  - type: conversation
    description: "Craig's UI feedback, Kyle's EXEC docs, live system inspection"
---

# Action Items for Implementation Session

Prioritized by what Kyle needs before the next daily sync, then what the team needs for adoption.

---

## P0 — Before Kyle's Next Sync

### Fix: Trace API ObjectId serialization bug
The changes collection has perfect field-level audit data (verified in MongoDB). The trace API endpoint (`/api/trace/entity/:type/:id`) throws `TypeError: 'ObjectId' object is not iterable` when called. The UI's Changes timeline depends on this.

**Root cause:** ObjectId fields in the changes response aren't being serialized to strings before JSON output.
**File:** likely `kernel/api/` trace route handler
**Verified:** `db.changes.find({"entity_id": ObjectId("69e796f8d1924f5584bc76e6")})` returns correct data with field-level old_value/new_value, actor attribution, timestamps, hash chain.

### Fix: Deep links on related entities
Blue highlighted relationship fields (e.g., Company on a Deal detail view) don't navigate to the related entity when clicked. They should route to `/:entityType/:entityId`.

**Current behavior:** Click opens the edit page for the entity you're already on.
**Expected:** Click navigates to the related entity's detail page.

### Kyle access to the OS
Create Kyle as a user who can log into the UI and use the CLI.
- Create auth credentials for Kyle (password setup or magic link)
- Verify Kyle can log in at the UI and see Deal list
- Send Kyle the URL and credentials

---

## P1 — Team Adoption Readiness

### Better detail view UX
Current detail page shows all fields as form inputs, text fields like notes are hard to read, and navigating to edit takes you to a separate page.

Options to explore:
- **Read view by default** — format text fields properly (especially notes, next_step, use_case), toggle to edit mode on demand
- **Side panel** — click a row in list view, detail opens as a panel without leaving the list
- **Related entities inline** — on a Deal detail, show Company card, Contacts, SuccessPhases as linked sections
- **Inline editing** — click a field to edit it in place rather than a full edit page

Design decision needed before implementation.

### Custom domain
Set up a proper domain like `os.indemn.ai` or `app.indemn.ai` pointing to the Railway UI deployment. Currently `indemn-ui-production.up.railway.app`.

### CLI published and installable
The `indemn` CLI currently lives in the repo. Publish it so team members can install and use it (pip package or similar). Currently only works from Craig's local venv.

### Repo setup for team
The indemn-os repo needs CLAUDE.md and documentation that lets any team member (or AI session) understand the codebase and contribute. The CLAUDE.md exists but the repo should be accessible to the team with proper README, setup instructions, and context.

---

## P2 — System Evolution

### Populate SuccessPhase data
SuccessPhase entity exists but is empty. Populate as phased data materializes from Kyle's daily syncs. FoxQuilt and Alliance have explicit phases in Kyle's docs. Others need ground-truthing first.

### Meeting ingestion pipeline
Pull meeting transcripts from Google Drive (Gemini/Granola), create Meeting entities, extract intelligence (Tasks, Decisions, Commitments, Signals). This is Track B-D from the meeting-ingestion-plan.md in the other session.

### Staleness detection
Watches on Deals where days since last activity exceeds stage-specific thresholds. Notify the deal owner. This is Cam's "top salesperson" vision — automated nudges.

### Cadence enforcement
The associate's job per deal from Kyle's playbook: current-state summary, days-since-last-touch, next-move recommendation, pre-drafted artifacts, escalation flags, handoff packets.

---

## P3 — Future

### Package entity
7 SKUs × 3 tiers from Kyle's DICT-CUSTOMER-SUCCESS-v2. Useful when proposal generation becomes a workflow.

### Implementation entity evolution
investorCohort, readinessCohort, contractStatus from Kyle's CS dictionary. Useful when customer delivery tracking becomes the focus.

### Proposal drafting automation
Using Cam's proposal templates + deal data to generate proposal drafts. Requires Package entity and deeper deal data.

### Google Drive integration adapter
For ongoing meeting transcript sync and customer document access.

### Slack integration adapter
For notifications, last-contact verification, and the `#prospects-ledger` manual note input that Kyle described.

---

## Reference: What Was Done This Session

- Read and saved Kyle's EXEC folder (7 files: INDEX, PLAYBOOK-v2, 3 data dictionaries, 6 leads, MAP)
- Read Cam's Proposals folder (6 proposals: Alliance, Branch, Johnson, GIC, Charley, SaaS Agreement)
- Added 5 fields to Deal entity: deal_id, next_step, next_step_owner, use_case, proposal_candidate
- Created SuccessPhase entity (per-deal phased progression with state machine)
- Created Amynta company
- Created Kyle's 6 deals: FOXQUILT-2026, ALLIANCE-2026, AMYNTA-GRD360-2026, RANKIN-2026, TILLMAN-2026, OCONNOR-2026
- Deployed API to pick up entity changes
- Verified changes collection has full field-level audit trail with hash chain
- Identified trace API bug (ObjectId serialization)

## Reference: AWS Secrets Manager MongoDB URI Mismatch

The secret at `indemn/dev/shared/mongodb-uri` points to `dev-indemn-pl-0.mifra5.mongodb.net` which times out. The OS uses `dev-indemn.mifra5.mongodb.net` (no `-pl-0`). Either update the secret or add a separate OS-specific secret. Direct connection works:
```
mongosh "mongodb+srv://dev-indemn:wJnKmz4P0q39GpXZ@dev-indemn.mifra5.mongodb.net/indemn_os"
```
