---
ask: "Brainstorm the overall demo strategy for presenting GIC Email Intelligence to JC and Maribel, integrating Ryan's wireframes, golf cart LOB focus, and two-day timeline"
created: 2026-03-23
workstream: gic-email-intelligence
session: 2026-03-23-a
sources:
  - type: github
    description: "GIC Email Intelligence codebase exploration"
  - type: github
    description: "Intake Manager codebase exploration"
  - type: mongodb
    description: "LOB distribution and golf cart email analysis from gic_email_intelligence database"
  - type: web
    description: "Ryan's wireframes: gic_wholesaler_wireframes.html, gic_wholesaler_diagram.html, indemn_wireframes_v3.html, indemn_placement_flows.html, indemn_retail_ia.html, indemn_component_inventory_v2.html"
---

# GIC Demo Strategy — Golf Cart LOB Focus

## Goal

Present GIC Email Intelligence to JC (EVP, Chief Underwriting Officer) and Maribel (operations champion) as a screen-share walkthrough. Two-day build timeline.

## Success Criteria

JC walks away thinking:

1. **"They understand our inbox"** — We've organized 3,214 emails into something intelligible. LOB breakdown, agent activity, submission lifecycles. Golf carts are visible as a distinct product line.
2. **"This can automate what Maribel does"** — End-to-end workflow for a golf cart submission: email arrives, data extracted, gaps identified, info request drafted. Outlook add-in shows analysis in Maribel's Outlook sidebar.
3. **"I can see where this is going"** — UI aligned with Ryan's wireframe vision. Golf carts is step 1. The architecture handles any LOB. The path from email intelligence → full quote-and-bind automation (like Event Guard) is clear.

**Parlay into:** Release to GIC team for real-world testing + begin development of fully autonomous solution.

## Demo Narrative — Three Acts

### Act 1: "We've organized your inbox" (5 min)

Open with analytics. Show JC his own data:
- 3,214 emails analyzed from quote@gicunderwriters.com
- LOB distribution — golf carts visible as a distinct category alongside GL, Personal Liability, Special Events, etc.
- Agent activity — which retail agencies send the most volume
- Email type breakdown — quotes, submissions, declines, info requests
- Cycle times if derivable from the data

The "mirror moment" — JC sees his operation quantified for the first time.

### Act 2: "We can automate what Maribel does" (10 min)

Drill into a golf cart submission:
- Email arrives from retail agent with ACORD/application
- System extracts: applicant name, address, vehicle (year/make/VIN), drivers, coverage limits, storage info
- Gap analysis identifies what's missing
- AI drafts an info request to the retail agent
- Show the Outlook Add-in: Maribel opens the email, sidebar shows analysis + draft, clicks "Reply with this"

Maribel's 15-minute manual process → 30 seconds.

### Act 3: "Here's where this is going" (5 min)

Show the Submission Queue (aligned with Ryan's wireframe):
- Pipeline table: Risk/Insured, Retail Agent, Line, Stage, Last Activity, Action Needed
- Filter by LOB → show only golf carts
- Click into a Risk Record → submission data, thread, status pipeline, UW decision prompt
- Explain: golf carts is step 1, architecture handles any LOB, path to full automation

## Data Quality Fix — Targeted Reclassification

### Problem

The email classifier has a hardcoded LOB list that doesn't include "Golf Cart" or "Motorsports." Result:
- 3 Motorsports portal submissions → misclassified as "Trucking"
- 1 direct agent golf cart submission → misclassified as "Inland Marine"
- Named insured not extracted for any portal submissions
- 6 GIC portal submissions (Motorsports, Roofing, PestControl) not understood as a distinct intake channel

### Current LOB Distribution (from MongoDB)

| LOB | Count | | LOB | Count |
|-----|-------|-|-----|-------|
| Personal Liability | 725 | | Contractors Equipment | 71 |
| General Liability | 574 | | Umbrella | 46 |
| Special Events | 245 | | Multi-Class Package | 44 |
| Non Profit | 219 | | Builders Risk | 42 |
| Excess Personal Liability | 217 | | Specified Professions | 40 |
| Commercial Package | 205 | | Inland Marine | 33 |
| Commercial Property | 200 | | Medical Professional | 27 |
| Professional Liability | 86 | | + 16 more LOBs | ~100 |
| Excess Liability | 78 | | **Total classified** | **3,104** |
| Allied Healthcare | 76 | | Unclassified | 49+61 |

Golf carts: **0** (hidden as Trucking/Inland Marine)

### Fix Approach — Two-Stage Targeted Reclassification

**What gets reclassified (~250 emails):**
- All non-USLI email types: `agent_submission`, `gic_application`, `agent_reply`, `agent_followup`, `gic_info_request`, `gic_internal`
- The 49 unclassified emails
- All 6 GIC portal submissions

**What stays untouched (~2,900 emails):**
- USLI emails (`usli_quote`, `usli_pending`, `usli_decline`) — LOB derivable from reference prefix (MGL=GL, XPL=Excess PL, etc.)

**Stage 1: Open reclassification (parallel subagents)**
- Improved prompt: open LOB (not closed list), portal format recognition, better named insured extraction
- Parallel Claude Code subagents reading from MongoDB
- Output: raw classifications with freely determined LOBs

**Stage 2: Normalization**
- Collect all unique LOBs from Stage 1 + existing USLI classifications
- Build canonical mapping (e.g., "Golf Carts" → "Golf Cart", "Motorsports - Golf Cart" → "Golf Cart")
- Apply mapping → GIC's canonical LOB catalog
- Update MongoDB

### Golf Cart LOB Config

Create `golf_cart.json` with required fields derived from the Motorsports portal application data:
- Applicant: name, address, homeowner status
- Vehicle: year, make, VIN
- Driver: name, DOB, gender, driving record
- Coverage: liability limits, UM/UIM
- Storage: type (garage, driveway, carport)
- Registration: street-legal vs. private property
- Purchase date

This powers gap analysis and completeness computation for golf cart submissions.

## UI Reshape — Toward Ryan's Wireframes

### Source: `gic_wholesaler_wireframes.html`

Ryan designed two new screens specifically for the GIC wholesaler context:

### New Screen 1: Submission Queue (replaces Kanban board)

Based on Ryan's wireframe. Flat table, submission-first organizing:

| Column | Description |
|--------|-------------|
| Risk / Insured | Primary label. Name + sub-type + received date |
| Retail Agent | Agency name + number. Secondary, for context/filtering |
| Line | LOB badge(s) |
| Stage | UW pipeline: Extracting → Missing Data → UW Review → Clarifying → Quoted → Bound |
| Last Activity | Relative time |
| Action Needed | Specific human-readable action or "—" |
| | Open button |

Features:
- Filters: Stage, Line, Retail Agent, Sort
- Search by insured, agent, policy
- "Unread email bar" at bottom: "N unread submission emails — Indemn has read and parsed these"
- Rows highlighted when action needed

### New Screen 2: Risk Record (replaces Submission Detail)

Based on Ryan's wireframe. Four-panel layout:

**Left column:**
- Submission Data panel: extracted fields with provenance tags ("extracted from email · Mar 16")
- All Interactions thread: reverse-chronological, multi-channel (email with channel tags)

**Right column:**
- Submission Status: progress bar (Received → Extracted → UW Review → Quoted → Bound)
- UW Decision prompt (when applicable): Approve / Refer to senior UW / Decline
- Coverage Workstream CTA: Application · Quote · Bind · Pay
- Documents: source email, ACORD, uploads

**Header:**
- Breadcrumb: Submissions → [Insured Name] · [LOB]
- Retail agent + agency in subheader (metadata, not anchor)
- Stage badge

### What Stays

- **Analytics tab** — inbox understanding, LOB distribution, agent activity (Act 1)
- **Outlook Add-in** — sidebar intelligence (Act 2)
- **Backend API** — classification, extraction, gap analysis, drafts all unchanged

### Stage Vocabulary Mapping

| Our current stage | Ryan's wireframe stage | Notes |
|---|---|---|
| new | Received / Extracting | Split into two stages |
| awaiting_info | Missing Data / Clarifying | Distinguish "we need info" from "carrier asked a question" |
| with_carrier | Submitted | Forwarded to carrier |
| quoted | Quoted | Same |
| attention (declined) | Declined | Explicit status |
| (new) | UW Review | New stage — GIC makes underwriting decision before quoting |
| (new) | Bound | New terminal stage |

## Execution Plan — Two Days

### Day 1: Data Quality + UI Skeleton

**Morning:**
1. Fix classifier prompt — open LOB, portal format recognition, better extraction
2. Reclassify ~250 non-USLI emails via parallel subagents reading from MongoDB
3. Stage 2: normalize LOBs → canonical catalog, update MongoDB
4. Create golf cart LOB config (`golf_cart.json`)

**Afternoon:**
5. Process golf cart submissions through pipeline (link → extract → gap analysis → draft)
6. Build Submission Queue view (table, filters, action needed column)
7. Build Risk Record view (4-panel layout, submission data, thread, status pipeline)

### Day 2: Polish + Demo Prep

**Morning:**
8. Polish analytics with corrected data (golf carts visible, accurate LOB distribution)
9. Wire Submission Queue → Risk Record navigation
10. Seed 2-3 golf cart lifecycle emails if needed (info request → reply → quote)

**Afternoon:**
11. Outlook Add-in running with cloudflared tunnel
12. End-to-end demo dry run — all three acts
13. Remove debug output, clean up edge cases

## Architecture Notes

### Relationship to Intake Manager

This prototype is a stepping stone. The target state is integration into the intake-manager repo:
- Submission Queue = intake-manager's submission list (reconfigured for wholesaler)
- Risk Record = intake-manager's submission detail (reconfigured for wholesaler)
- Analytics = new capability intake-manager doesn't have yet
- Outlook Add-in = new capability, separate Vite build

For the demo, the prototype stands on its own. Post-demo, the migration path is documented in `artifacts/2026-03-23-intake-manager-integration-analysis.md`.

### Golf Cart as the Wedge

Golf carts represent the full automation opportunity:
1. **Today (demo):** Email intelligence — understand the inbox, extract data, draft info requests
2. **Next (release):** Operational tool — Maribel uses it daily for golf cart submissions
3. **Target:** Full quote-and-bind automation — like Event Guard / Jewelers Mutual. Retail agent submits → system extracts → validates → quotes → binds. No human in the loop.

Golf carts are ideal for this because:
- GIC is the carrier (not brokering to USLI) — simpler workflow, full control
- New product line — no legacy process to disrupt
- Low volume (4 submissions so far) — safe to automate early
- South Florida market — growing golf cart insurance demand

## Files Reference

- GIC repo: `/Users/home/Repositories/gic-email-intelligence/`
- Intake Manager repo: `/Users/home/Repositories/intake-manager/`
- Ryan's GIC wireframes: `artifacts/gic_wholesaler_wireframes.html`
- Ryan's GIC interaction flow: `artifacts/gic_wholesaler_diagram.html`
- Ryan's retail wireframes: `artifacts/indemn_wireframes_v3.html`
- Ryan's placement flows: `artifacts/indemn_placement_flows.html`
- Ryan's retail IA: `artifacts/indemn_retail_ia.html`
- Ryan's component inventory: `artifacts/indemn_component_inventory_v2.html`
- Integration analysis: OS repo `artifacts/2026-03-23-intake-manager-integration-analysis.md`
