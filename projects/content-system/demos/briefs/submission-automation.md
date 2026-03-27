# Video Brief: Submission Automation

## Read First
- Video production playbook: `.claude/skills/content-showcase/references/video-production.md`
- Brand alignment: `projects/content-system/artifacts/2026-03-27-brand-alignment-reference.md`
- Smart Inbox demo as reference: `demos/smart-inbox/` (same animation patterns)
- Intake Manager repo: `/Users/home/Repositories/intake-manager/` (for technical accuracy)
- Existing page: `src/content/outcomes/submission-automation.mdx` in `/tmp/engineering-blog-sync/`

## What This Is

The Intake Manager (product name: Submission Automation) is a **full underwriting submission pipeline** — much broader than "submission triage." It's a production application at https://intakecopilot.indemn.ai.

**End-to-end flow:**
1. **Email ingestion** — Connects to Gmail/Outlook via Composio webhooks. Emails arrive, attachments download automatically.
2. **Thread-based tracking** — Every submission becomes a thread that accumulates documents over days/weeks. Event types: EMAIL_RECEIVED, DOCUMENT_UPLOAD, PARAMETER_UPDATE, QUOTE_REQUESTED, etc.
3. **AI extraction** — Two pipelines: v1 (GPT multi-step) and v2 (Claude deep agent that autonomously reads PDFs, detects workflow, extracts parameters, validates). Handles ACORD forms (80, 125, 126, 130, 140), loss runs, driver MVRs, vehicle schedules.
4. **Parameter merging** — Documents arriving on different days get unified. Four merge strategies: OVERWRITE, APPEND, KEEP_EXISTING, NEWER_WINS.
5. **Validation** — LangGraph-based with org-specific rules. Three outcomes: VALID, INVALID (auto-decline), SUBMIT FOR UNDERWRITER REVIEW.
6. **Multi-carrier quoting** — Provider integrations: ACIC (full XML API), Nationwide (portal auth + OAuth + API), Northfield (trucking/GL). SSE streaming for real-time progress. Quote comparison UI.
7. **Submission states** — PROCESSING → AWAITING_INFO / AWAITING_REVIEW / READY_FOR_QUOTE → QUOTED → BOUND / DECLINED / EXPIRED

**What makes this different from Email Intelligence (Smart Inbox):**
- Email Intelligence classifies and triages emails
- Submission Automation takes it through the ENTIRE pipeline: extraction → validation → quoting → binding
- They can work together: Email Intelligence feeds qualified submissions into Submission Automation

**Matrix alignment:**
- Category: **Operational Efficiency**
- Associate: **Intake Associate**
- Target: Carriers / Distribution

## Storyboard (suggested)

**Total target: ~60-75s. No dialogue — music + optional VO.**

The visual story: "A submission email arrives. Watch it go from raw documents to quoted policy — autonomously."

**Act 1 — The Submission Arrives (5s)**
An email notification: "New submission — 3 attachments". ACORD form icons. Clean and simple.
HTML animation or Kling establishing shot.

**Act 2 — The Pipeline (35-40s)**

Phase 1 — Ingestion + Extraction (~12s):
- Email card appears with attachments (ACORD 125, 126, Loss Runs)
- Documents "open" — pages fan out
- Data fields extract one by one into a structured form (similar to Smart Inbox deep dive but for commercial lines)
- Business name, address, operations, revenue, employee count, coverage requested
- Multiple documents merging into one unified record (show the merge visually — fields from doc 1 + fields from doc 2 = complete record)

Phase 2 — Validation (~8s):
- Rules engine runs — checklist style
- Green checks: business info, operations, coverage limits
- Warning: loss history needs review
- Outcome badge: "READY FOR QUOTE"

Phase 3 — Multi-Carrier Quoting (~12s):
- "Submitting to carriers..." — 3 carrier cards appear (ACIC, Nationwide, Northfield)
- Progress bars fill for each carrier (SSE streaming feel)
- Quote results populate: premium, coverage, terms
- Side-by-side comparison highlights best match
- "Quote ready for review"

Phase 4 — Notification (~5s):
- Notification sent to underwriting team
- Dashboard view: submission card with status "QUOTED", quote comparison ready
- "Your team reviews and binds. Everything else was automatic."

**Act 3 — Stats (10s)**
- Full pipeline: email → quote in minutes
- Multi-carrier comparison
- Thread-based: documents arriving over days unified automatically
- "From raw submission to quote-ready package — no manual processing"

**Act 4 — CTA (5s)**
Standard CTA.

## Page Updates

Page exists at `src/content/outcomes/submission-automation.mdx` with existing interactive demo. Embed the video above the demo:
```html
<video controls playsinline style="width: 100%; border-radius: 12px; margin: 2rem 0; box-shadow: 0 4px 24px rgba(0,0,0,0.12);">
  <source src="/videos/products/submission-automation.mp4" type="video/mp4" />
</video>
```

The page content may need updating to reflect the full quoting pipeline (current page underrepresents the multi-carrier quoting capability). But video first, page content refinement is a separate pass.

## Key Visual Patterns to Use

- **Email card with attachments** (from InboxCounter/EmailDeepDive) — adapt for submission email
- **Data extraction** (from EmailDeepDive) — ACORD form extraction with field population
- **Document merge** — new pattern: two source columns merging into one unified record
- **Validation checklist** (from EmailDeepDive gap analysis) — adapt for rules validation
- **Multi-card progress** — new pattern: 3 carrier cards with progress bars filling simultaneously
- **Quote comparison** — new pattern: side-by-side cards with highlighted best match
- **Stats reveal** (from StatsReveal)
- **CTA** (from CTACard) — copy directly

## Lexicon Reminders
- "Associate" not "agent"
- "Intake Associate" is the marketing name
- "Revenue capacity" framing — every hour your team spends on manual data entry is an hour not spent on underwriting relationships
- Human-in-the-loop: "Your team reviews and binds. The Associate handles everything before that."
- Don't say the AI "makes decisions" about coverage — it prepares the package for human decision-making
