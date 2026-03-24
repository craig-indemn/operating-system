---
ask: "Comprehensive implementation plan for the data model & lifecycle redesign"
created: 2026-03-24
workstream: gic-email-intelligence
session: 2026-03-24-b
sources:
  - type: design
    description: "artifacts/2026-03-24-data-model-redesign.md — the source of truth for all implementation decisions"
  - type: exploration
    description: "Full frontend (14 files) and backend (20+ files) codebase exploration with exact line numbers"
---

# Implementation Plan — Data Model & Lifecycle Redesign

> **Source of truth:** `projects/gic-email-intelligence/artifacts/2026-03-24-data-model-redesign.md`
> Every implementation decision traces back to this design document. When in doubt, read the design.

**Repo:** `/Users/home/Repositories/gic-email-intelligence/`
**Goal:** Replace the broken 5-stage model with an 8-stage lifecycle, add the situation assessment layer, update all backend and frontend code, migrate existing data, and verify everything works end-to-end.

## Architecture

The implementation follows the design's 2-phase approach:
- **Phase 1 (additive):** New models, collections, tools, and fields with defaults. No breaking changes. Old code continues to work.
- **Phase 2 (coordinated cutover):** Migration script + backend + frontend + LLM prompts deployed together.

## Execution Strategy

4 waves of parallel sub-tasks. Each wave's tasks are independent and can run simultaneously. Wave N+1 depends on Wave N completing.

```
Wave 1 (foundation)     → Wave 2 (backend logic)    → Wave 3 (frontend + integration)  → Wave 4 (migrate + verify)
├─ T1: Models/enums     ├─ T5: Assessment skill      ├─ T9: Frontend types + config      ├─ T13: Run migration
├─ T2: DB + collections  ├─ T6: Pipeline (harness)    ├─ T10: SubmissionQueue page        ├─ T14: Build verification
├─ T3: New tools         ├─ T7: API routes            ├─ T11: RiskRecord page             └─ T15: Browser testing
└─ T4: LOB configs       ├─ T8: Linker + classifier   └─ T12: Analytics + System + components
                         └─ T8b: Migration script
```

---

## Wave 1: Foundation (fully parallel, no dependencies)

### Task 1: Update Models & Enums
**Files:** `src/gic_email_intel/core/models.py`
**Design ref:** Sections "Updated Enums", "Updated Submission Schema", "Enhanced Stage History", "Situation Assessment Schema", "Carrier Entity", "Agent/Agency Entity"

1. Replace `Stage` enum: 5 values → 8 (`received`, `triaging`, `awaiting_agent_info`, `awaiting_carrier_action`, `processing`, `quoted`, `declined`, `closed`)
2. **Keep old Stage values as comments** (for migration reference) but remove from enum
3. Delete `AttentionReason` enum entirely
4. Add new enums: `BallHolder`, `Resolution`, `AutomationLevel`, `IntakeChannel`
5. Add `ProcessingStatus.ASSESSED` between EXTRACTED and COMPLETE
6. Expand `DraftType`: add `STATUS_UPDATE`, `REMARKET_SUGGESTION`
7. Add `FieldSource` model
8. Add `SituationAssessment` model (with `needs_review: bool = False`)
9. Add `Carrier` model
10. Add `Agent` model
11. Add `CrossChannelFlag` model
12. Update `Submission` model:
    - Add: `submission_group_id`, `operating_mode`, `intake_channel`, `automation_level`, `ball_holder` (with derivation comment), `resolution`, `resolved_at`, `latest_assessment_id`, `is_stale`, `stale_since`, `carrier_id`, `carrier_name`, `carrier_reference`, `retail_agent_id`, `retail_agency_code`, `premium_quoted`, `premium_bound`, `cross_channel_flags`, `resolution_note`
    - Keep: `premium` (string, Phase 1 coexistence), `carrier` (string, Phase 1 coexistence), all existing fields
    - Change default: `stage = Stage.RECEIVED`
13. Update `StageHistoryEntry`: add `ball_holder: Optional[BallHolder] = None`, rename `triggered_by_email` to `triggered_by` (keep old as alias), add `assessment_id`
14. Update `BoardSubmissionCard`: add `ball_holder`, `operating_mode`, `automation_level`, `is_stale`. Remove `attention_reason`.
15. Update `Draft`: add `assessment_id`, `confidence`, `needs_review`

**Verify:** `cd /Users/home/Repositories/gic-email-intelligence && python -c "from gic_email_intel.core.models import *; print('OK')"`

### Task 2: Database Setup & Collection Seeding
**Files:** `src/gic_email_intel/core/db.py`, new script `scripts/seed_entities.py`
**Design ref:** Sections "MongoDB Collections", "Carrier Entity", "Agent/Agency Entity"

1. Add collection constants to `db.py`: `ASSESSMENTS = "assessments"`, `CARRIERS = "carriers"`, `AGENTS = "agents"`
2. Create indexes script or add to db.py init:
   - assessments: `(submission_id, 1)`, `(submission_id, 1, assessed_at, -1)`, `(confidence, 1)`
   - carriers: `(name, 1)` unique
   - agents: `(email, 1)`, `(name, 1)`
   - submissions: `(submission_group_id, 1)`, `(carrier_id, 1)`, `(retail_agent_id, 1)`, `(latest_assessment_id, 1)`
3. Write `scripts/seed_entities.py`:
   - Seed 3 carriers: USLI (external, portal, A++ rating), Hiscox (external, email), Granada/GIC (affiliated, internal, B rating)
   - Seed agents from distinct `retail_agent_name`/`retail_agent_email` pairs across submissions collection
   - Dedup agents: match on normalized email first, then fuzzy name match
   - Link `carrier_id` and `retail_agent_id` back to submissions where possible

**Verify:** Run seed script, check collections in mongosh.

### Task 3: New Tools for Assessment Pipeline
**Files:** `src/gic_email_intel/agent/tools.py`
**Design ref:** Section "Assessment Pipeline — Tool Requirements"

Add 5 new tools:

1. `get_submission(submission_id)` — returns full submission document as JSON
2. `list_extractions(submission_id)` — returns all extractions for a submission
3. `get_lob_config(lob_name)` — returns LOB config from the registry (file-based configs)
4. `save_assessment(submission_id, assessment_json)` — saves SituationAssessment to assessments collection, updates `submission.latest_assessment_id`
5. `get_assessment(assessment_id)` — returns assessment document

Update existing tools:
6. `create_submission` — add parameters: `operating_mode`, `intake_channel`, `automation_level`, `carrier_id`, `carrier_name`, `submission_group_id`
7. `update_submission_stage` — add `ball_holder` derivation (auto-set from stage using the 1:1 mapping), accept `triggered_by` format ("email:<id>", "user:<name>", "system:*"), save to stage_history with ball_holder

Update `SKILL_TOOL_MAP`:
8. Add `situation-assessor` skill with tools: `get_email`, `list_emails`, `get_submission`, `list_extractions`, `get_lob_config`, `save_assessment`, `update_submission_stage`
9. Add `get_submission` and `get_assessment` to `draft-generator` skill
10. Add `update_submission` to `submission-linker` skill

**Verify:** `python -c "from gic_email_intel.agent.tools import *; print('OK')"`

### Task 4: Enhanced LOB Configs
**Files:** `src/gic_email_intel/core/lob_config.py`, `src/gic_email_intel/agent/lob_configs/gl.json`, `src/gic_email_intel/agent/lob_configs/golf_cart.json`
**Design ref:** Section "Enhanced LOB Configuration"

1. Update `lob_config.py` LobConfig dataclass/dict to include new fields: `tier`, `workflow_type`, `carrier_options`, `primary_carrier`, `usli_prefixes`, `portal_source`, `appetite_description`, `typical_cycle_days`
2. Update `gl.json`: add `tier: "auto_brokered"`, `workflow_type: "brokered"`, `carrier_options: ["USLI", "Hiscox"]`, `primary_carrier: "USLI"`, `usli_prefixes: ["MGL", "STK"]`
3. Update `golf_cart.json`: add `tier: "direct_underwritten"`, `workflow_type: "direct_underwritten"`, `carrier_options: ["GIC/Granada"]`, `primary_carrier: "GIC/Granada"`, `portal_source: "motorsports"`
4. Update config loader to handle new fields (backward-compatible — missing fields get defaults)
5. **Do NOT change `compute_completeness()` yet** — that's Phase 2 (depends on stage migration)

**Verify:** `python -c "from gic_email_intel.core.lob_config import get_lob_config; c = get_lob_config('General Liability'); print(c)"`

---

## Wave 2: Backend Logic (depends on Wave 1)

### Task 5: Situation Assessor Skill
**Files:** NEW `src/gic_email_intel/agent/skills/situation_assessor.md`
**Design ref:** Section "Assessment Pipeline — LLM Prompt Changes — situation_assessor.md"

1. Create `situation_assessor.md` with the prompt specified in the design:
   - System context: GIC's two operating modes, 8 stages with ball-holder tracking
   - Input: submission data, linked emails (with bodies), extractions, LOB config
   - Output: SituationAssessment JSON
   - 5 key rules: check extraction before declaring missing, recognize portal submissions, identify auto-quoted USLI, detect field conflicts, only recommend drafts when email is the correct next action
2. The prompt should reference the design's draft decision table for when drafts are appropriate
3. Include examples for the 3 original problem cases: golf cart portal, Jessica quote comparison, USLI auto-quote

**Verify:** Read the skill file, verify it matches the design's assessment schema output format.

### Task 6: Pipeline Update (Harness)
**Files:** `src/gic_email_intel/agent/harness.py`, `src/gic_email_intel/agent/skills/draft_generator.md`
**Design ref:** Section "Assessment Pipeline — Pipeline Redesign"

1. Reorder pipeline in `harness.py`:
   ```
   Old: classify → link → stage_detect → extract → draft
   New: classify → link → extract → assess → [maybe draft]
   ```
2. Remove the `stage_detect` step entirely (lines ~130-140 in current harness)
3. Add `assess` step after extraction:
   - Run situation-assessor skill with submission_id
   - The skill saves the assessment and updates submission stage
   - Check `assessment.draft_appropriate` — only proceed to draft if true
4. Update `should_generate_draft()` (line 100-106):
   ```python
   def should_generate_draft(sub: dict) -> bool:
       assessment_id = sub.get("latest_assessment_id")
       if not assessment_id:
           return False
       assessment = db[ASSESSMENTS].find_one({"_id": ObjectId(assessment_id)})
       return assessment and assessment.get("draft_appropriate", False)
   ```
5. Update `draft_generator.md`:
   - Remove self-gating logic (the skill no longer decides WHETHER to draft)
   - Add assessment context to the prompt: receives `situation_type`, `next_action`, `missing_items`, `next_action_reasoning` from the assessment
   - Add new draft types: `status_update`, `remarket_suggestion`
   - Update subject line patterns for new stage awareness
6. Delete `stage_detector.md` (or rename to `stage_detector.md.deprecated`)
7. Update `ProcessingStatus` flow in harness: after assessment → status = ASSESSED, after draft (or skip) → status = COMPLETE

**Verify:** `python -c "from gic_email_intel.agent.harness import process_email; print('OK')"`

### Task 7: API Routes Update
**Files:** `src/gic_email_intel/api/routes/submissions.py`, `src/gic_email_intel/api/routes/stats.py`
**Design ref:** Design document "Code Locations Requiring Updates" section

**submissions.py:**
1. Line 39: Update board view stages list from 5 to 8
2. Lines 97-100: Update action queue logic for new stage names
3. Lines 209-243: Rewrite `generate_summary()` for 8 stages (no more attention_reason branching)
4. Lines 321-356: Update LOB requirements stage switches (use new stages)
5. Line 461: Update `valid_stages` set to 8 new values
6. Add assessment data to submission detail response: include latest assessment when returning submission detail
7. Add `GET /api/assessments/{id}` endpoint
8. Board view aggregation: include `ball_holder`, `operating_mode`, `automation_level`, `is_stale` in card projections

**stats.py:**
9. Lines 20-29: Update stage count queries
10. Lines 68-73: Update dashboard queue logic
11. System intelligence: update stage breakdown to 8 stages

**Verify:** Start API server, hit `/api/submissions` and `/api/stats` — verify 8 stages returned.

### Task 8: Linker & Classifier Updates
**Files:** `src/gic_email_intel/core/linker.py`, `src/gic_email_intel/agent/skills/submission_linker.md`, `src/gic_email_intel/agent/skills/email_classifier.md`
**Design ref:** Sections "Submission Linker Tool Access", "Multi-LOB Email Splitting"

1. Update `submission_linker.md`: instruct linker to set `operating_mode`, `intake_channel`, `automation_level` based on:
   - LOB config's `workflow_type` → `operating_mode`
   - From address pattern: `noreply@gicunderwriters.com` → `gic_portal`, `quotes@granadainsurance.com` → `granada_portal`, USLI auto-format → `usli_retail_web`, CSR addresses → `csr_relay`
   - USLI auto-quote detection → `automation_level: "auto_notified"`
2. Update `email_classifier.md` (Phase 2 prep): add `lines_of_business: list[str]` to classification output for multi-LOB detection. For now, most emails have single LOB — this is future-proofing.
3. Update `create_submission` calls in linker to pass new fields
4. When linker detects USLI auto-quote (USLI reference prefix + `usli_quote` email type), set `automation_level: "auto_notified"` and let the assessor fast-path to close

### Task 8b: Migration Script
**Files:** NEW `scripts/migrate_stages.py`
**Design ref:** Section "Migration Strategy"

Write a migration script with 3 passes:

**Pass 1 — Stage rename:**
```python
STAGE_MAP = {
    "new": "received",
    "awaiting_info": "awaiting_agent_info",
    "with_carrier": "awaiting_carrier_action",
    "quoted": "quoted",  # unchanged
}
# For non-attention submissions, direct rename
db.submissions.update_many(
    {"stage": {"$in": ["new", "awaiting_info", "with_carrier"]}},
    [{"$set": {"stage": {"$switch": {"branches": [...], "default": "$stage"}}}}]
)
```

**Pass 2 — Attention decomposition:**
```python
# attention + declined → declined stage
db.submissions.update_many(
    {"stage": "attention", "attention_reason": "declined"},
    {"$set": {"stage": "declined", "ball_holder": "gic"}, "$unset": {"attention_reason": ""}}
)

# attention + carrier_pending → awaiting_carrier_action
db.submissions.update_many(
    {"stage": "attention", "attention_reason": "carrier_pending"},
    {"$set": {"stage": "awaiting_carrier_action", "ball_holder": "carrier"}, "$unset": {"attention_reason": ""}}
)

# attention + stale/agent_urgent → recover from stage_history
# (Use the Python algorithm from the design document)
for sub in db.submissions.find({"stage": "attention", "attention_reason": {"$in": ["stale", "agent_urgent"]}}):
    recovered_stage = recover_attention_stage(sub)
    db.submissions.update_one(
        {"_id": sub["_id"]},
        {"$set": {"stage": recovered_stage, "is_stale": True, "stale_since": sub.get("stage_changed_at")},
         "$unset": {"attention_reason": ""}}
    )
```

**Pass 3 — Set defaults for new fields:**
```python
db.submissions.update_many(
    {"operating_mode": {"$exists": False}},
    {"$set": {
        "operating_mode": "brokered",
        "intake_channel": "agent_email",
        "automation_level": "unknown",
        "ball_holder": "queue",  # Will be corrected by stage→ball_holder mapping
        "is_stale": False,
        "submission_group_id": None,
        "carrier_id": None,
        "retail_agent_id": None,
        "latest_assessment_id": None,
        "premium_quoted": None,
        "premium_bound": None,
        "cross_channel_flags": [],
    }}
)

# Derive ball_holder from stage
BALL_HOLDER_MAP = {
    "received": "queue", "triaging": "gic", "awaiting_agent_info": "agent",
    "awaiting_carrier_action": "carrier", "processing": "gic",
    "quoted": "agent", "declined": "gic", "closed": "done"
}
for stage, bh in BALL_HOLDER_MAP.items():
    db.submissions.update_many({"stage": stage}, {"$set": {"ball_holder": bh}})
```

Add `--dry-run` flag that reports counts without writing.

**Verify:** Run with `--dry-run`, verify counts match expected (53 new, 32 awaiting_info, 1 with_carrier, 2347 quoted, 321 attention).

---

## Wave 3: Frontend & Integration (depends on Wave 2)

### Task 9: Frontend Types & Shared Config
**Files:** `ui/src/api/types.ts`
**Design ref:** All enum sections in design document

1. Replace `Stage` type: 5 → 8 values
2. Delete `AttentionReason` type
3. Add types: `BallHolder`, `Resolution`, `AutomationLevel`, `IntakeChannel`, `CrossChannelFlag`, `SituationAssessment`
4. Update `Submission` interface: add all new fields (`ball_holder`, `operating_mode`, `intake_channel`, `automation_level`, `is_stale`, `submission_group_id`, `carrier_id`, `carrier_name`, `carrier_reference`, `retail_agent_id`, `premium_quoted`, `premium_bound`, `cross_channel_flags`, `latest_assessment_id`, `resolution`, `resolution_note`). Remove `attention_reason`.
5. Update `STAGE_CONFIG` record — 8 entries with labels, colors, dot colors:
   ```typescript
   const STAGE_CONFIG: Record<Stage, StageConfig> = {
     received:                { label: 'Received',           color: 'violet',  dotBg: '#8b5cf6' },
     triaging:                { label: 'Triaging',           color: 'blue',    dotBg: '#3b82f6' },
     awaiting_agent_info:     { label: 'Awaiting Agent',     color: 'amber',   dotBg: '#f59e0b' },
     awaiting_carrier_action: { label: 'With Carrier',       color: 'slate',   dotBg: '#64748b' },
     processing:              { label: 'Processing',         color: 'sky',     dotBg: '#0ea5e9' },
     quoted:                  { label: 'Quoted',             color: 'emerald', dotBg: '#10b981' },
     declined:                { label: 'Declined',           color: 'red',     dotBg: '#ef4444' },
     closed:                  { label: 'Closed',             color: 'gray',    dotBg: '#9ca3af' },
   }
   ```
6. Update `BoardResponse.stages` to Record of 8 stages
7. Update `DraftType` to include `status_update` and `remarket_suggestion`
8. Add `BALL_HOLDER_LABELS`: `{ queue: 'In Queue', gic: 'GIC', agent: 'Agent', carrier: 'Carrier', done: 'Done' }`

**Verify:** `cd ui && npx tsc --noEmit`

### Task 10: SubmissionQueue Page Rewrite
**Files:** `ui/src/pages/SubmissionQueue.tsx`
**Design ref:** 8-stage model, ball-holder tracking, situation assessment

1. Rewrite `getStageDisplay()` — simple lookup from STAGE_CONFIG (no more attention_reason branching):
   ```typescript
   function getStageDisplay(s: Submission) {
     const config = STAGE_CONFIG[s.stage]
     return { label: config.label, dot: config.dotBg, pillBg: config.color + '-50', pillText: config.color + '-800' }
   }
   ```

2. Rewrite `getActionDisplay()` — use ball_holder instead of attention_reason:
   ```typescript
   function getActionDisplay(s: Submission) {
     if (s.has_draft && s.draft_status === 'suggested')
       return { text: 'Draft ready — review and send', color: 'text-emerald-700' }
     if (s.is_stale)
       return { text: 'Stale — needs follow-up', color: 'text-orange-700' }
     switch (s.ball_holder) {
       case 'agent': return { text: 'Waiting on agent', color: 'text-amber-700' }
       case 'carrier': return { text: `Waiting on ${s.carrier_name || 'carrier'}`, color: 'text-slate-600' }
       case 'gic': return { text: 'Your turn — action needed', color: 'text-blue-700' }
       case 'done': return { text: 'Closed', color: 'text-gray-500' }
       default: return { text: 'In queue', color: 'text-violet-600' }
     }
   }
   ```

3. Rewrite `needsAttention()` — based on `ball_holder === 'gic'` and `is_stale`

4. Update stage filter dropdown to 8 stages

5. Update count calculations for new stage names

6. Add automation_level filter option: "Show only actively processed" (hides auto_notified USLI passthrough)

**Verify:** `cd ui && npm run build`

### Task 11: RiskRecord Page Rewrite
**Files:** `ui/src/pages/RiskRecord.tsx`
**Design ref:** 8-stage model, assessment display, ball-holder

1. **Pipeline progress bar** — redesign for 8 stages. Use a horizontal timeline with colored dots instead of the current 5-circle bar. Group visually:
   ```
   [Received] → [Triaging] → [Awaiting Agent / Awaiting Carrier / Processing] → [Quoted / Declined] → [Closed]
   ```
   Show current stage highlighted, completed stages with checkmarks, future stages grayed.

2. Rewrite `stageToPipelineIndex()` for new stages

3. Rewrite `badgeStyle()` — use STAGE_CONFIG colors

4. **Rewrite UW Decision Prompt** — context-sensitive to new stages:
   - `triaging`: "Route to carrier" / "Request info" / "Route to UW review" / "Decline"
   - `processing`: "Issue quote" / "Request more info" / "Decline"
   - `awaiting_agent_info`: "Still waiting" (disabled, informational)
   - `awaiting_carrier_action`: "Still waiting on [carrier]" (disabled)
   - `quoted`: "Mark as bound" / "Close as expired"
   - `declined`: "Remarket" / "Close"

5. **Add assessment summary display** at top of right column (above pipeline bar):
   ```tsx
   {data.latest_assessment && (
     <div className="rounded-lg border p-3" style={{ borderColor: '#e8e6df', background: '#fafaf7' }}>
       <p style={{ fontSize: '11px', color: '#888' }}>SITUATION ASSESSMENT</p>
       <p style={{ fontSize: '13px', color: '#1a1a18' }}>{data.latest_assessment.situation_summary}</p>
       <div className="mt-2 flex gap-2">
         <span className="rounded px-2 py-0.5" style={{ fontSize: '10px', background: '#f0efe8' }}>
           {data.latest_assessment.situation_type}
         </span>
         <span className="rounded px-2 py-0.5" style={{ fontSize: '10px', background: '#f0efe8' }}>
           Next: {data.latest_assessment.next_action}
         </span>
         {data.latest_assessment.needs_review && (
           <span className="rounded px-2 py-0.5 bg-amber-100 text-amber-800" style={{ fontSize: '10px' }}>
             Needs Review
           </span>
         )}
       </div>
     </div>
   )}
   ```

6. **Add ball-holder indicator** in submission summary:
   ```tsx
   <div style={{ fontSize: '11px', color: '#666' }}>
     Waiting on: <strong>{BALL_HOLDER_LABELS[data.ball_holder]}</strong>
     {data.carrier_name && data.ball_holder === 'carrier' && ` (${data.carrier_name})`}
   </div>
   ```

7. Update stage history display — works automatically if API returns new stage names

8. **Add cross-channel flags** if present:
   ```tsx
   {data.cross_channel_flags?.length > 0 && (
     <div className="rounded border-l-2 border-amber-400 bg-amber-50 p-2 mt-2">
       <p style={{ fontSize: '10px', color: '#854f0b' }}>CROSS-CHANNEL ACTIVITY</p>
       {data.cross_channel_flags.map(f => (
         <p key={f.detected_at} style={{ fontSize: '11px' }}>{f.summary}</p>
       ))}
     </div>
   )}
   ```

**Verify:** `cd ui && npm run build`

### Task 12: Analytics, SystemIntelligence, and Supporting Components
**Files:** `ui/src/pages/Analytics.tsx`, `ui/src/pages/SystemIntelligence.tsx`, `ui/src/components/DraftCard.tsx`
**Design ref:** 8-stage model, resolution types, draft types

**Analytics.tsx:**
1. Update `RESOLUTION_LABELS` — add new resolution types if the backend returns them
2. Resolution display works dynamically from API data — minimal changes needed

**SystemIntelligence.tsx:**
3. Rewrite `STAGE_COLORS` and `STAGE_LABELS` records for 8 stages
4. Update `stageOrder` array (line 193) to 8 values
5. Stage breakdown card: 8 pills instead of 5. Consider wrapping to 2 rows if space is tight.

**DraftCard.tsx:**
6. Update `DRAFT_TYPE_LABELS` — add `status_update: 'Status Update'`, `remarket_suggestion: 'Remarket Suggestion'`
7. Update `DRAFT_TYPE_RESOLUTION` mapping for new types

**Verify:** `cd ui && npm run build`

---

## Wave 4: Migrate, Build, & Test (depends on Wave 3)

### Task 13: Run Migration
1. Start backend: `uv run uvicorn gic_email_intel.api.main:app --port 8080`
2. Run migration dry-run: `uv run python scripts/migrate_stages.py --dry-run`
3. Verify counts match expected
4. Run migration: `uv run python scripts/migrate_stages.py --execute`
5. Run seed script: `uv run python scripts/seed_entities.py`
6. Verify in mongosh:
   ```javascript
   db.submissions.aggregate([{$group: {_id: "$stage", count: {$sum: 1}}}])
   // Should show 8 stages, no "new", "awaiting_info", "with_carrier", or "attention"
   db.carriers.countDocuments()  // Should be 3
   db.agents.countDocuments()    // Should be 100+
   ```

### Task 14: Build Verification
1. Backend: `cd /Users/home/Repositories/gic-email-intelligence && uv run python -c "from gic_email_intel.api.main import app; print('API OK')"`
2. Frontend: `cd ui && npm run build`
3. Start both:
   - `uv run uvicorn gic_email_intel.api.main:app --port 8080`
   - `cd ui && npm run dev`
4. Hit API endpoints and verify responses:
   - `curl http://localhost:8080/api/submissions` — 8 stage columns
   - `curl http://localhost:8080/api/stats` — correct counts
   - `curl http://localhost:8080/api/system` — 8 stages in breakdown
   - `curl http://localhost:8080/api/submissions/<id>` — new fields present (ball_holder, operating_mode, etc.)

### Task 15: Browser Testing
**Use agent-browser CLI to verify every UI workflow:**

1. **Submission Queue loads correctly:**
   - Open `http://localhost:5173/?token=0So5zcDzGPnMdADZqh62r8Hpi559W9RbXqJlc3D_RBQ`
   - Stage badges show new stage names (Received, Triaging, Awaiting Agent, etc.)
   - Action needed column shows ball-holder based text
   - Stage filter dropdown has 8 options
   - Table loads with submissions visible

2. **Risk Record displays correctly:**
   - Click into a submission
   - Pipeline progress bar shows 8-stage timeline
   - Ball-holder indicator visible
   - Assessment summary displays (if assessment exists — may be empty for pre-migration submissions)
   - Stage history shows new stage names
   - UW decision buttons are context-appropriate for the current stage
   - Back button works

3. **Draft workflow still works:**
   - Find a submission with a draft
   - Draft card renders with correct type label
   - Edit, Approve, Dismiss buttons work
   - Copy Draft and Open in Outlook work after approval

4. **Analytics page loads:**
   - Stage breakdown shows 8 stages
   - Charts render
   - Resolution labels display correctly

5. **System Intelligence page loads:**
   - Stage pills show 8 stages with correct colors
   - LOB configuration table loads
   - Processing stats display

6. **No console errors:**
   - Check browser console for JavaScript errors on each page
   - Check network tab for failed API calls

---

## UI Design Decisions (not in the data model design)

These visual decisions need to be made during implementation:

### Pipeline Progress Bar (RiskRecord)
The current 5-circle bar doesn't work for 8 stages. Recommended approach:
- Use a **horizontal segmented timeline** with dots at each stage
- Group into 3 visual sections separated by thin dividers:
  - **Intake**: Received → Triaging
  - **Processing**: Awaiting Agent ↔ Awaiting Carrier ↔ Processing
  - **Outcome**: Quoted / Declined → Closed
- Current stage gets a colored dot + label
- Completed stages get green checkmarks
- Future stages are gray circles
- The "Processing" section shows bidirectional arrows since submissions can loop

### Stage Badge Colors (consistent across all pages)
Use the STAGE_CONFIG defined in Task 9. Warm palette matching the existing wireframe style:
- Received: violet (new arrival)
- Triaging: blue (GIC working)
- Awaiting Agent: amber (waiting on external)
- Awaiting Carrier: slate (waiting on carrier)
- Processing: sky (GIC actively working)
- Quoted: emerald (positive outcome)
- Declined: red (negative outcome)
- Closed: gray (terminal)

### Action Needed Column
Replace attention_reason-based text with ball-holder-based text. The ball-holder tells Maribel at a glance whose turn it is. Combined with `is_stale`, this gives clear prioritization.

### Assessment Summary in Risk Record
Display as a subtle card at the top of the right column, above the pipeline bar. Shows:
- `situation_summary` as the main text
- `situation_type` and `next_action` as small tags
- `needs_review` as an amber badge if confidence < 0.7
- This replaces the generic AI Summary for assessed submissions

### Automation Level Filter
In the Submission Queue, add a toggle or filter to hide `auto_notified` submissions. This lets Maribel focus on the 5% of submissions that need her attention, hiding the 95% USLI passthrough.

---

## File Manifest

| File | Wave | Task | Action |
|------|------|------|--------|
| `src/gic_email_intel/core/models.py` | 1 | T1 | Major update — enums, models, schema |
| `src/gic_email_intel/core/db.py` | 1 | T2 | Add collection constants |
| `scripts/seed_entities.py` | 1 | T2 | New — seed carriers and agents |
| `src/gic_email_intel/agent/tools.py` | 1 | T3 | Add 5 tools, update 2, update SKILL_TOOL_MAP |
| `src/gic_email_intel/core/lob_config.py` | 1 | T4 | Update config loader + fields |
| `src/gic_email_intel/agent/lob_configs/gl.json` | 1 | T4 | Add new config fields |
| `src/gic_email_intel/agent/lob_configs/golf_cart.json` | 1 | T4 | Add new config fields |
| `src/gic_email_intel/agent/skills/situation_assessor.md` | 2 | T5 | New — the core assessment skill |
| `src/gic_email_intel/agent/harness.py` | 2 | T6 | Pipeline reorder + assessment step |
| `src/gic_email_intel/agent/skills/draft_generator.md` | 2 | T6 | Update — assessment-gated |
| `src/gic_email_intel/agent/skills/stage_detector.md` | 2 | T6 | Delete |
| `src/gic_email_intel/api/routes/submissions.py` | 2 | T7 | Major — board view, summary, stage validation |
| `src/gic_email_intel/api/routes/stats.py` | 2 | T7 | Update stage queries |
| `src/gic_email_intel/core/linker.py` | 2 | T8 | Update for new fields |
| `src/gic_email_intel/agent/skills/submission_linker.md` | 2 | T8 | Update for operating_mode detection |
| `src/gic_email_intel/agent/skills/email_classifier.md` | 2 | T8 | Minor — multi-LOB prep |
| `scripts/migrate_stages.py` | 2 | T8b | New — 3-pass migration script |
| `ui/src/api/types.ts` | 3 | T9 | Major — all type definitions |
| `ui/src/pages/SubmissionQueue.tsx` | 3 | T10 | Major — stage display, action column, filters |
| `ui/src/pages/RiskRecord.tsx` | 3 | T11 | Major — pipeline bar, UW buttons, assessment display |
| `ui/src/pages/Analytics.tsx` | 3 | T12 | Minor — resolution labels |
| `ui/src/pages/SystemIntelligence.tsx` | 3 | T12 | Major — stage colors, labels, breakdown |
| `ui/src/components/DraftCard.tsx` | 3 | T12 | Minor — new draft type labels |

---

## Success Criteria

1. `npm run build` succeeds with zero TypeScript errors
2. `uv run python -m pytest` passes (update tests as needed)
3. All 8 stages appear in the board view with correct counts
4. Submission Queue shows ball-holder-based action text, not attention_reason
5. Risk Record shows assessment summary, pipeline progress, and context-appropriate UW buttons
6. Draft workflow (edit, approve, copy, open in Outlook) still works
7. Analytics and System Intelligence pages load with 8-stage data
8. No browser console errors on any page
9. Migration script reports correct counts matching: 53 received + 32 awaiting_agent_info + 1 awaiting_carrier_action + 2347 quoted + 151 declined + 170 awaiting_carrier_action (from carrier_pending) + stale/urgent recovered
10. `auto_notified` submissions (USLI auto-quotes) are distinguishable from `actively_processed`
