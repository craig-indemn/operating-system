---
ask: "Build an endorsement verification path for the Monday demo — flexible for any endorsement type, following web operator harness conventions"
created: 2026-02-19
workstream: web-operator
session: 2026-02-19-a
sources:
  - type: github
    description: "web_operators repo — docs/path-format.md, paths/ecm_cap_renewal/ (context, guardrails, path_v1), skills/agent_browser_cli/SKILL.md"
  - type: gmail
    description: "MaeLena's ECM CAP CHG guide.docx (9 annotated screenshots) — extracted via XML parsing"
  - type: slack
    description: "Rudra's Feb 18 update on endorsement verification work in progress"
---

# Endorsement Path Creation

## What Was Built

Created `paths/ecm_cap_endorsement/` with three files:

### context.md
Grounding document explaining the endorsement verification task. Key framing: the operator's job is **verification, not data entry** — the account manager already made the change, the operator confirms it was done correctly. Lists all common endorsement types (vehicle, driver, coverage, secured party) so the agent understands the full scope.

### guardrails.md
Safety constraints adapted from the renewal guardrails. Key additions specific to endorsements:
- "Endorsement Verification, Not Data Entry" rule — if the change doesn't match, that's an error to flag, not something to fix
- Verify before issuing — must confirm the specific change, read notes, and check PDF before issuing
- No outbound communication (demo site sends real emails/SMS)

### path_v1.md — 8 Steps, 3 Procedures
Parses correctly with the existing `path_parser.py` (verified via `uv run`).

| Step | Goal | Give-up |
|------|------|---------|
| 1. Login to Applied Epic | Authenticate and reach dashboard | 15 turns → stop |
| 2. Collect BAUT Endorsement Activities | Build list of all BAUT CHG3 activities | 10 turns → flag and stop |
| 3. Open the CHG3 Activity | Open activity, read description + association + all notes | 15 turns → flag and stop |
| 4. Download and Read the Endorsement PDF | Navigate to attachments, download PDF, extract change data | 20 turns → flag and stop |
| 5. Verify the Change in Epic | Open policy, find correct service summary row, verify specific change | 20 turns → flag and stop |
| 6. Update Premium and Commission | Enter premium from PDF, calculate commission (skipped if verification failed) | 10 turns → flag and stop |
| 7. Issue the Endorsement | Actions → Issue/Not Issue Endorsement → Finish (skipped if verification failed) | 10 turns → flag and stop |
| 8. Close or Reassign the Activity | Close with "decs checked" note OR reassign to Sheryll Bausin with error notes | 15 turns → flag and stop |

**Procedures:**
- Reassign Activity — detailed steps for error case reassignment
- Navigate via File → Exit — reliable way to return to Home in the Angular SPA
- Poll for Page Load — progress bar polling pattern

### Key Design Decisions

**Flexible, not hardcoded**: Step 5 (Verify the Change) branches by `change_type` from working memory:
- Vehicle changes → check Vehicles tab (add/remove/trade)
- Driver changes → check Drivers tab
- Coverage changes → check Coverages tab
- Secured party changes → check Additional Interests tab
- Multiple changes → check each relevant tab in order

**Error path is first-class**: Steps 6 and 7 are skipped entirely if verification fails. Step 8 branches into close (8b) or reassign (8c) based on `verification_passed`. The operator never issues a broken endorsement.

**Multi-activity loop**: Step 8d loops back to Step 3 for processing additional activities in one run, matching the production model (20-50 endorsements per batch).

**All Applied Epic quirks baked in**:
- Real mouse events for Angular dropdown menus (Access, Actions, File)
- File → Exit as the only reliable navigation back to Home
- Progress bar polling before trusting table contents
- ASI component workarounds (eval for virtual list rows, tag-and-dblclick pattern)
- "Show Only Important Policy Documents" filter for attachments
- Correct attachments page (Access → Attachments dropdown, NOT sidebar link)

## Demo Environment Concern

**State persists in the demo.** Once an endorsement is issued and activity closed, it can't be re-run. MaeLena created two specific test cases:

| Test Case | Account | Purpose |
|-----------|---------|---------|
| Dry Ridge Farm, LLC | Correct submission | Standard vehicle trade — should pass cleanly |
| Bill Kistler | Error case | 4 intentional errors — should catch and reassign |

**Risk**: If we burn through these during testing, they won't be available for Monday's demo.

**Mitigation plan**:
1. First, inventory all BAUT CHG3 activities to see how many we have
2. Test Steps 1-5 (non-destructive) without issuing or closing
3. Save at least one clean activity for the live demo
4. Consider asking MaeLena for additional test activities via George

## Approach for Testing and Demo Prep

1. **Check activity inventory** — log in and count available BAUT CHG3 activities
2. **Shake out the path with Claude Code** — manually walk through steps against a test activity, stop before irreversible actions
3. **Run through harness with Haiku 4.5** — test speed and cost with the real web operator
4. **Compare models** — if Haiku isn't reliable enough, test Sonnet and open source alternatives
5. **Final demo run** — save a clean activity for Monday's live demo

## Files Created
- `/Users/home/Repositories/web_operators/paths/ecm_cap_endorsement/context.md`
- `/Users/home/Repositories/web_operators/paths/ecm_cap_endorsement/guardrails.md`
- `/Users/home/Repositories/web_operators/paths/ecm_cap_endorsement/path_v1.md`
