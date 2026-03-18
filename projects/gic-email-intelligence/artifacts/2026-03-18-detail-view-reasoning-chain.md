---
ask: "How should the submission detail view present information so the user understands the full reasoning chain — from conversation to extraction to analysis to action?"
created: 2026-03-18
workstream: gic-email-intelligence
session: 2026-03-18-a
sources:
  - type: conversation
    description: "Craig + Claude brainstorming session on UX redesign after deep audit of all 10 submissions"
  - type: browser-testing
    description: "Systematic review of every submission via agent-browser + full database dump"
  - type: technical-design
    description: "Full 1,526-line technical design including LOB requirements, classification taxonomy, extraction pipeline"
---

# Detail View Redesign — Transparent Reasoning Chain

## Context

The current detail view has the right components but presents them as disconnected pieces. The user sees extracted data, a completeness ring, and a draft — but can't follow HOW the system got from the email to the suggestion. Craig's feedback: "I literally don't know how I would talk about the UI in the demo."

The fix isn't removing intelligence — it's making the reasoning chain transparent at every step.

## The Problem

The UI shows confident outputs without explaining:
- How did we get to this stage?
- Where did the extracted data come from?
- What are we comparing against and why?
- Why are specific items "missing"?
- Why is this draft suggesting these specific things?

## The Solution: A Vertical Reasoning Chain

The detail view right column becomes a step-by-step pipeline where each section logically flows to the next. The user can follow the chain and understand (and verify) the system's reasoning.

### Layout

```
┌─────────────────────────────────────────────────────────┐
│ ← Blaze Pilates  Professional Liability  Attention      │
├──────────────────────────┬──────────────────────────────┤
│                          │                              │
│  CONVERSATION            │  1. AI SUMMARY               │
│  (auto-expanded)         │  "USLI needs more info.      │
│                          │   GIC sent partial, not      │
│  ┌─ Elizabeth (USLI)     │   sufficient."               │
│  │  Pending file for     │                              │
│  │  BLAZE PILATES...     │  2. WHAT WE EXTRACTED        │
│  └───────────────────    │  Named insured: Blaze...     │
│                          │  Address: 1864 Radius...     │
│  ┌─ Maribel (GIC) ──┐   │  Space: Rented               │
│  │  Agent response:  │   │  (each tagged with source    │
│  │  BLAZE PILATES    │   │   thread message)            │
│  │  1864 RADIUS DR   │   │                              │
│  │  RENTED           │   │  3. LOB REQUIREMENTS         │
│  └───────────────────┘   │  "For Professional Liability │
│                          │   submissions, based on our  │
│  ┌─ Elizabeth (USLI)     │   analysis of GIC's email    │
│  │  Cannot proceed       │   patterns:"                 │
│  │  without all info     │  - Named insured             │
│  └───────────────────    │  - Business address          │
│                          │  - Coverage limits           │
│  Attachments: ...        │  - Effective date            │
│                          │  - Loss runs (3 years)       │
│                          │  - Signed application        │
│                          │  ...                         │
│                          │                              │
│                          │  4. GAP ANALYSIS             │
│                          │  ✅ Named insured (msg 2)    │
│                          │  ✅ Address (msg 2)          │
│                          │  ❌ Loss runs                │
│                          │  ❌ Years in business        │
│                          │  ❌ Coverage limits          │
│                          │  "5 of 12 fields filled"     │
│                          │                              │
│                          │  5. SUGGESTED DRAFT          │
│                          │  ┌────────────────────────┐  │
│                          │  │ To: agent@...          │  │
│                          │  │ Subject: Info Request  │  │
│                          │  │                        │  │
│                          │  │ [editable text area]   │  │
│                          │  │                        │  │
│                          │  │ Dear Maria,            │  │
│                          │  │ We need the following: │  │
│                          │  │ - Loss runs (3 years)  │  │
│                          │  │ - Years in business    │  │
│                          │  │ ...                    │  │
│                          │  └────────────────────────┘  │
│                          │  [Edit] [Approve] [Dismiss]  │
│                          │                              │
└──────────────────────────┴──────────────────────────────┘
```

### Section Details

#### 1. AI Summary (2-3 sentences)
Natural language explanation of what's happening with this submission.

Examples:
- "This is a USLI pending file for Blaze Pilates (Professional Liability). USLI requested additional information. GIC responded with partial details but USLI says it's not sufficient — all pending items must be answered."
- "USLI declined this Commercial Package submission for Simaval Services LLC. Reason: 'No more than 500 acres' criterion was not met. The retail agent (Maria Bergolla at Univista Insurance) needs to be notified."
- "Hiscox returned a quote for Waterhouse Construction LLC — $707/year Professional Liability with $2M limits. Quote needs to be forwarded to the retail agent."

This is derived from the email classification + thread content. It tells the user what's going on before they read anything else.

#### 2. What We Extracted
Key-value pairs pulled from the conversation thread and PDF attachments. Each field tagged with its source — referencing the specific thread message or PDF attachment it came from.

Existing implementation: `ExtractedData.tsx` with `SourceChip` components. Enhancement: source chips reference specific thread messages ("from message 2" or "from COVERAGESUMMARY.PDF").

Only shows fields that HAVE values. No empty dashes.

#### 3. LOB Requirements (Source of Truth)
"For [LOB] submissions, the following information is typically required:"

Shows the LOB config's required_fields and required_documents. This is the standard we're comparing against. Grounded in research:
- LOB configs derived from analysis of 3,165 classified emails
- Required fields based on what USLI quotes contain (quote output ≈ application input)
- Common missing items from 212 USLI pending notices
- Starting with GL config (519 emails, 20 vision extractions), expanding per-LOB

Optionally expandable "How we know this" section explaining the research methodology. Builds trust and is a differentiator in the demo: "We analyzed your entire email history to understand what's needed."

#### 4. Gap Analysis (Checklist, not just a ring)
Each required field is a row showing status:
- ✅ Field name — value (source: thread message N / PDF name)
- ❌ Field name — not found in conversation

Replaces the completeness ring with an actionable checklist. The percentage/count can still be shown as a header ("5 of 12 fields filled") but the detail is the checklist.

Each ❌ item directly maps to a bullet point in the suggested draft.

#### 5. Suggested Draft (Editable + Actionable)
Flows from the gap analysis: "Based on the missing items above, here's a suggested email."

Features:
- **Editable text area** — Maribel can tweak wording, remove items she already has, add context
- **Approve button** — marks as approved (in production: sends the email)
- **Dismiss button** — removes the suggestion
- **Regenerate button** — asks AI to try again with updated context
- **Edit/Preview toggle** — switch between editing and seeing the formatted version

The draft subject line follows GIC's format: "Info Request for [INSURED]- [GIC_NUMBER]"
The draft body references specific missing items from the gap analysis.

## Conversation: Auto-Expanded Thread

The left column shows the parsed email thread auto-expanded. No click to open.

Thread messages displayed as bubbles:
- **External messages** (agents, carriers) — left-aligned, white background
- **GIC messages** (Maribel, Julissa, quote@) — right-aligned, blue background
- Each bubble shows: sender name, date, body text
- Chronological order (oldest at top, newest at bottom)
- Attachments listed below the conversation

This is grounded in the thread parser (`thread_parser.py`) which handles:
- Outlook-style separators (From/Sent/To/Subject)
- Gmail-style separators (On [date] wrote:)
- Spanish variants (De/Enviado/Para/Asunto)
- Signature and disclaimer stripping

## Board View

The board columns (New, Awaiting Info, With Carrier, Quoted, Attention) stay — they were validated against actual data distribution.

Cards could benefit from a small context line explaining WHY they're in that column:
- "USLI declined" (Attention)
- "Agent replied with info" (New — needs review)
- "Hiscox quote received" (Quoted)

## Future: Analytics View

Craig plans to add a way for users to see analytics about the inbox:
- Who is reaching out (agent/agency volumes)
- Types of submissions (email type distribution)
- LOB breakdown
- Volume trends over time

All data already exists in MongoDB from the 3,165 email classifications. This is a natural second view/tab.

## Future: Making Research Accessible

The analysis and data extraction research should be available for users to understand how the system works. Ideas:
- "How it works" section in the UI
- LOB requirement configs viewable and editable by GIC staff
- Classification accuracy metrics
- Extraction confidence indicators

Deferred until after the reasoning chain redesign is complete.

## Implementation Priority

1. **Auto-expand conversation** — remove the click-to-open, show thread immediately
2. **AI Summary section** — derive from classification + thread content
3. **Gap analysis checklist** — replace completeness ring with ✅/❌ checklist tied to LOB config
4. **Editable draft** — text area with approve/dismiss/edit controls
5. **LOB requirements display** — show the source of truth being compared against
6. **Card context lines** — explain WHY each card is in its column

## Data Fixes Needed (Parallel)

The 10 sample submissions have data quality issues from agent classification errors:
- ESR Services: wrong stage ("Quoted" but email says "no application")
- Florida Georgia: decline draft in "New" column
- Mercado: stale draft referencing "Johnny"
- Porro Insurance: not a real submission
- Blaze Pilates: draft goes to GIC internal staff
- Email counts were wrong (fixed: all now show 1)

These need to be corrected either by re-running the agent with better context, manual correction, or filtering out bad submissions for demo.
