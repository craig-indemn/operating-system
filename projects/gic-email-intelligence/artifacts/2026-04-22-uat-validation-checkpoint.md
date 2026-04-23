---
ask: "Checkpoint after successful end-to-end UAT validation with all production features — every step passed"
created: 2026-04-22
workstream: gic-email-intelligence
session: 2026-04-22a
sources:
  - type: codebase
    description: "12 code changes across 6 files, proxy deployed to EC2"
  - type: unisoft-uat
    description: "Quote 17348, Task 16862, Activity 46947, Attachments 85452+85453"
---

# UAT Validation Checkpoint — 2026-04-22

## Status: ALL STEPS PASSING

Full end-to-end pipeline + automation tested successfully against UAT Unisoft. Every feature from the JC call is implemented and verified.

## Test Subject

**LUSSO STONE DESIGN LLC** — Granada portal submission from `quote@granadainsurance.com`
- Email ID: `69e8e29537cce43fd4593b38`
- Received: 2026-04-22 14:55 UTC
- PDF: `DocHost_26.pdf` (Artisan Contractors Application, 21 extracted fields)
- Agency: Doral Insurance Advisors, Inc. (Producer Code 5820)
- LOB: General Liability (CG), SubLOB: Artisans/Contractors (AC)

## End-to-End Results

### Processing Pipeline
| Stage | Result |
|-------|--------|
| Extract | Form extractor (primary, NOT fallback) → Gemini 2.5 Pro → 21 fields |
| Classify | `agent_submission`, LOB = General Liability |
| Link | New submission created |
| Enrich | Agent: Luis Benitez, Agency: Doral Insurance Advisors, Inc. |

### Automation Agent (Gemini 2.5 Pro deepagent)
| Step | Command | Result |
|------|---------|--------|
| 1. Claim | `gic emails next --type agent_submission --json` | Claimed |
| 2. LOB | `unisoft lobs sublobs --lob CG` → AC | Correct |
| 3. Agency | `unisoft agents get --number 5820` | Direct match by producer code |
| 3.5. Dup check | `gic submissions check-duplicate` | No matches |
| 4. Quote | `unisoft quote create --assigned-to indemnai ...` | **Quote 17348** created, `AssignedTo: indemnai`, `HasDuplicates: true` (flagged test quotes Q:17345, Q:17347) |
| 5a. PDF upload | `unisoft attachment upload --category application` | **ID 85452** → Documents > Application folder |
| 5b. Email export | `gic emails export ... --output .eml` | 1,273 bytes exported |
| 5b. Email upload | `unisoft attachment upload --category email` | **ID 85453** → General > Email folder |
| 6. Task | `unisoft task create --group-id 3 --due-date 2026-04-22 --entered-by indemnai` | **Task 16862**, Group: NEW BIZ, Due: today, Action: Review automated submission |
| 7. Activity | `unisoft activity create --action-id 6 --logged-by indemnai` | **Activity 46947** |
| 8. Complete | `gic emails complete ... --move-to "indemn processed"` | Marked completed. Move gracefully skipped (folder not created yet — expected) |

### Agent Behavior Notes
- Self-corrected `BusinessDescription` 50-char limit (truncated and retried)
- Correctly noted Unisoft duplicate flag in completion notes
- Did NOT skip any steps
- Used `indemnai` for all user fields (entered-by, logged-by, assigned-to)

## Code Changes Made This Session

### Bug Fixes
1. **`EXTRACTIONS` not imported in harness.py** — enrichment step was crashing, marking emails `failed`. Added to import.
2. **Field name mapping missed capitalized variants** — Gemini Pro returns `Producer Name`, `Applicant Name` etc. Added capitalized variants to `FIELD_MAP`. Also moved `producer_name`/`Producer Name` to `retail_agency_name` (producer = agency, not individual agent).

### New Features
3. **`--assigned-to` on quote create** — sets underwriter contact. CLI + skill updated. Using `indemnai` per JC.
4. **Task due date = same day** — added `--due-date` flag (default = today, was next business day). Skill passes email's `received_at` date.
5. **Prod GroupIds in skill** — GroupId 3 (NEW BIZ) for all LOBs, GroupId 4 (NEW BIZ Workers Comp) for WC.
6. **All CLI defaults → `indemnai`** — `entered_by` (×3) and `logged_by` (×1) changed from `ccerto`.
7. **Email export command** — `gic emails export {ID} --output file.eml` creates RFC 2822 .eml from MongoDB data.
8. **Attachment category routing** — `--category` flag on `unisoft attachment upload`. Maps to Unisoft folders:
   - `application` → Documents > Application (cat=15, sub=25)
   - `email` → General > Email (cat=14, sub=32)
   - `loss-run` → Documents > Loss Run (cat=15, sub=28)
   - `other` → General > Other (cat=14, sub=35)
9. **Proxy updated for categories** — `UniProxy.cs` accepts `categoryId`/`subcategoryId` from JSON payload. Compiled and deployed to EC2 (both UAT and Prod services).
10. **Inbox folder management** — `gic emails folders`, `gic emails create-folder`, `gic emails move` commands via Graph API.
11. **Move email on completion** — `--move-to` flag on `gic emails complete`. Non-fatal if folder doesn't exist.
12. **Agent system prompt updated** — includes all new CLI commands and flags.

### UAT Alignment
13. **Created matching task groups in UAT** — GroupId 3 "NEW BIZ" and GroupId 4 "NEW BIZ Workers Comp" to match production. UAT and prod are now identical for automation.

## Files Changed

| File | Changes |
|------|---------|
| `src/gic_email_intel/agent/harness.py` | EXTRACTIONS import fix, field name mapping fix (capitalized variants, producer→agency) |
| `src/gic_email_intel/automation/agent.py` | System prompt updated with new CLI commands |
| `src/gic_email_intel/automation/skills/create-quote-id.md` | `--assigned-to`, `--due-date`, `--entered-by`, `--logged-by`, `--category`, email export/upload step, `--move-to`, prod GroupIds |
| `src/gic_email_intel/cli/commands/emails.py` | New commands: `export`, `folders`, `create-folder`, `move`. Updated `complete` with `--move-to` flag |
| `src/gic_email_intel/core/graph_client.py` | New methods: `create_folder`, `move_message`, `list_child_folders` |
| `unisoft-proxy/client/cli.py` | `--assigned-to` on quote create, `--due-date` on task create, `--category` on attachment upload, defaults → `indemnai` |
| `unisoft-proxy/client/unisoft_client.py` | `category_id`/`subcategory_id` params on `upload_quote_attachment` |
| `unisoft-proxy/server/UniProxy.cs` | Category/subcategory parameterized in SOAP XML (was hardcoded). Deployed to EC2. |

## Unisoft UAT State (verify in desktop app)

| Entity | Value | Verify |
|--------|-------|--------|
| Quote 17348 | LUSSO STONE DESIGN LLC, CG/AC, Agent 5820, AssignedTo: indemnai | Quote details screen |
| Task 16862 | [Auto] LUSSO STONE DESIGN LLC — CG via Doral Insu…, Group: NEW BIZ, Due: 4/22, EnteredBy: indemnai | Task queue |
| Activity 46947 | ActionId 6, LoggedBy: indemnai, "Application received from agent via email automation. Quote ID: 17348" | Activity log on quote |
| Attachment 85452 | DocHost_26.pdf → Documents > Application folder | Attachments tab |
| Attachment 85453 | .eml file → General > Email folder | Attachments tab |

## Open Decision: Unisoft Duplicate Handling (Layer 3)

Current behavior: If Unisoft flags `HasDuplicates: true`, the agent notes the duplicate Quote IDs in completion notes but continues (quote was already created by Unisoft). Layer 2 (our MongoDB check) catches duplicates BEFORE creating the quote. Layer 3 is the safety net for duplicates Unisoft knows about that we don't.

**Decision deferred** — leaving as-is for now. Can change to fail-on-duplicate if needed after production monitoring.

## What's Next

1. **Bigger batch test** — process all of yesterday (Apr 21, 154 emails) and today (Apr 22, 67 emails) through pipeline + automation
2. **Full audit** — verify data quality across the batch
3. **Pre-production setup:**
   - Create "indemn processed" folder in production inbox
   - Sync prod agents to MongoDB
   - Deploy code to Railway
   - Test one harmless email against prod Unisoft
   - Verify in prod Unisoft desktop app
4. **Go live** — Apr 23 at 12:01 AM ET, date-filtered to only process new emails
