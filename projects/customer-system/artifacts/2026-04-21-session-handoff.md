---
ask: "Prepare handoff so the roadmap session can merge this session's work"
created: 2026-04-21
workstream: customer-system
session: 2026-04-21-customer-system
---

# Session Handoff — 2026-04-21 Customer System Session

## For the Roadmap Session: What to Merge

This session worked on the customer system from a design + implementation side session. The roadmap session needs to pull in everything that was done here so both sessions are in sync.

### What Was Done (in order)

**1. Kyle's EXEC documents read and saved**
- 7 files saved to `projects/customer-system/artifacts/context/kyle-exec/`
- INDEX.md, PLAYBOOK-v2.md, DICT-PROSPECTING-v2.md, DICT-SALES-v2.md, DICT-CUSTOMER-SUCCESS-v2.md, PROSPECT-SIX-LEADS-v0.md, MAP.md
- These are Kyle's vision for the prospect/sales/CS system from Apr 20

**2. Cam's Proposals read (not saved locally — in Google Drive)**
- Folder ID: `1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph`
- 6 proposals: Alliance, Branch, Johnson, GIC, Charley, SaaS Agreement
- Key insight: proposals are outcome-anchored, phased, customer-specific. Revenue Capacity is the core framing. Every new customer gets a free/cheap pilot.

**3. Deal entity modified (5 fields added)**
Already live on the OS. Fields added:
- `deal_id` (str, unique) — human-readable like FOXQUILT-2026
- `next_step` (str) — the ONE thing that needs to happen next
- `next_step_owner` (objectid → Actor) — who moves it forward
- `use_case` (str) — what they want us to solve
- `proposal_candidate` (str, enum Y/N/Maybe) — Kyle+Cam filter

**4. SuccessPhase entity created**
Already live on the OS. Per-deal phased progression:
- `deal` (objectid → Deal, required)
- `phase_number` (int, required)
- `name` (str, required)
- `entry_criteria` (str)
- `expected_outcome` (str)
- `go_no_go_signal` (str)
- `owner` (objectid → Actor)
- `stage` (state field: not_started → in_progress → complete → skipped)
- `notes` (str)

**5. Data created on the live OS**
- 1 new company: Amynta (Guardsman Home Warranty) — `69e796c9d1924f5584bc76e2`
- 6 deals created:

| deal_id | Company | Stage | Owner |
|---------|---------|-------|-------|
| FOXQUILT-2026 | Fox Quilt | demo | Kyle |
| ALLIANCE-2026 | Alliance Insurance | proposal | Marlon |
| AMYNTA-GRD360-2026 | Amynta | discovery | Kyle |
| RANKIN-2026 | Rankin Insurance | signed | Kyle |
| TILLMAN-2026 | Tillman Insurance | discovery | Kyle |
| OCONNOR-2026 | O'Connor Insurance | signed | Cam |

**6. P0 bug fixes (committed to indemn-os main)**
- `fix(trace)`: ObjectId serialization in trace API — changes timeline now works
- `fix(ui)`: Deep links on related entities — stopPropagation on ResolvedLink
- Kyle login: password set for kyle@indemn.ai (password: indemn-kyle-2026)

**7. Activity feed (committed to indemn-os main)**
- `GET /api/trace/activity` — global changes feed with filters
- `/activity` UI view — chronological feed, expandable field changes, entity links
- Heartbeat noise filtered (Runtime heartbeats bypass changes collection now)

**8. Detail view overhaul (committed to indemn-os main)**
- InlineField component — read mode by default, click to edit, accept/cancel
- DetailPanel component — side panel from list view (single click opens, double-click navigates)
- EntityDetailView rewritten — read view with label/value grid, inline editing
- ExpandableText for long text fields — truncated preview, click to expand
- Table columns: max-w-64 with truncate

**9. Custom domains (DNS live)**
- `os.indemn.ai` → UI (CNAME fc4bwhy5.up.railway.app)
- `api.os.indemn.ai` → API (CNAME p3ti9o3m.up.railway.app)
- Route53 records created in hosted zone Z06753801TP0QWFKAPKF8

**10. CLI v0.1.0 published**
- GitHub release: https://github.com/craig-indemn/indemn-os/releases/tag/v0.1.0
- Install: `bash install-cli.sh`
- `indemn init` creates `.claude/` with Session Startup protocol + domain-modeling skill

**11. Repo setup (committed to indemn-os main)**
- README.md — team entry point
- docs/getting-started.md — updated with correct URLs
- docs/white-paper.md — full vision document
- .claude/skills/domain-modeling/SKILL.md — 8-step process for Claude Code
- `indemn init` CLAUDE.md updated with Session Startup section

### Commits on indemn-os main (this session's)

```
74186de fix(ui): table column max-width + expandable text fields in detail view
6c43ae9 feat(cli): add Session Startup section to indemn init CLAUDE.md
3132b72 feat: repo setup for team — README, getting-started, domain-modeling skill, white paper
2e92c47 feat(cli): publish v0.1.0 — install script + GitHub release
12c3e70 fix(ui): TypeScript errors in DetailPanel and EntityDetailView — FieldMeta type
83f7bd1 feat(ui): read view with inline editing + detail panel from list
420aa07 fix(ui): activity feed column overflow — truncate long labels, flex min-w-0
4f108dc fix(activity): filter heartbeat noise + bypass changes collection for Runtime
57fa266 feat(activity): global activity feed — changes collection as a live view
8af88b2 fix(ui): deep links on related entities — stop propagation on ResolvedLink click
97f18c1 fix(trace): serialize ObjectId values in trace API responses
```

### Commits on os-customer-system branch (this worktree)

```
c086446 project(customer-system): P0 + P1 complete — system ready for team
1ba2a24 project(customer-system): update INDEX with session 2 status
635773d project(customer-system): Kyle's EXEC docs + Deal entity evolution plan
43221ef project(customer-system): setup scripts, automations scoped, session checkpoint
7488690 project(customer-system): prepared import data — 87 companies, 92 contacts, 24 associate types
0a3a81f project(customer-system): session 1 — problem statement, capabilities, vision, phase 1 domain model
```

### What the Roadmap Session Should Do

1. **Pull indemn-os main** — all the code changes (trace fix, activity feed, detail view, repo setup) are already committed there
2. **Read this handoff** — understands what data is live, what entities changed, what's deployed
3. **Merge the os-customer-system branch** artifacts into its worktree if needed (Kyle's EXEC docs, deal evolution plan, action items)
4. **Update its own INDEX.md** with the new state: 6 deals live, Deal has 5 new fields, SuccessPhase exists, custom domains, CLI published, P0+P1 complete
5. **API was redeployed 3 times this session** — entity definitions reloaded, new endpoints live. No further deploy needed unless the roadmap session has pending changes.

### Key IDs

| Thing | ID |
|-------|-----|
| Amynta company | `69e796c9d1924f5584bc76e2` |
| FoxQuilt deal | `69e796f8d1924f5584bc76e6` |
| Alliance deal | `69e79a31f0d2c6b73f885a32` |
| Amynta deal | `69e79a3bf0d2c6b73f885a35` |
| Rankin deal | `69e79a45f0d2c6b73f885a38` |
| Tillman deal | `69e79a4ff0d2c6b73f885a3a` |
| O'Connor deal | `69e79a58f0d2c6b73f885a3c` |
| SuccessPhase entity def | `69e79669d1924f5584bc76da` |
| Kyle actor (active, has password) | `69e28fedf508e1ceb69654c7` |

### What's NOT Done (P2)

- SuccessPhase data — entity exists, 0 records. Populate when phase data comes from Kyle syncs.
- Meeting ingestion — roadmap session is working on Google Meet adapter
- Staleness detection — watches not configured yet
- Cadence enforcement — associate work, after watches

### MongoDB Connection Note

The AWS secret at `indemn/dev/shared/mongodb-uri` points to `dev-indemn-pl-0.mifra5.mongodb.net` which DOES NOT WORK. The OS uses `dev-indemn.mifra5.mongodb.net`. Direct connection:
```
mongosh "mongodb+srv://dev-indemn:wJnKmz4P0q39GpXZ@dev-indemn.mifra5.mongodb.net/indemn_os"
```
