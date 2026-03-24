---
ask: "Comprehensive session handoff for continuing GIC Email Intelligence demo prep"
created: 2026-03-24
workstream: gic-email-intelligence
session: 2026-03-23/24
sources:
  - type: mongodb
    description: "gic_email_intelligence database on Atlas (dev cluster)"
  - type: github
    description: "Local repo at /Users/home/Repositories/gic-email-intelligence/"
---

# Session Handoff — GIC Email Intelligence

## What This Project Is

An email intelligence system for GIC Underwriters (a wholesale insurance broker). We ingested 6 months of emails from quote@gicunderwriters.com via Microsoft Graph API (read-only), classified them, linked them into submissions, and built a web UI + Outlook Add-in that shows GIC's team their organized inbox with AI-generated draft replies.

**Customer:** JC (EVP, Chief Underwriting Officer) and Maribel (operations) at GIC Underwriters.
**Goal:** Demo this to JC to show inbox understanding, automated draft replies, and the path to full quote-and-bind automation starting with golf carts.
**Partner repo:** The intake-manager (`/Users/home/Repositories/intake-manager/`) is the target production system built by Dhruv and Rudra. Our prototype will eventually integrate into it.

## What We Built (Sessions 2026-03-13 through 2026-03-24)

### Data Pipeline
- **3,214 emails** ingested from quote@gicunderwriters.com via Microsoft Graph API
- **3,214 classified** by LLM — email type (14 types including new `gic_portal_submission`), LOB (39 canonical), named insured, reference numbers
- **2,754 submissions** created by batch-linking emails via reference numbers
- **304 PDF extractions** via Claude Vision (including 5 golf cart application PDFs)
- **122 AI-generated drafts** (info requests, quote forwards, decline notifications, follow-ups)

### Web UI (React + Vite + Tailwind)
- **Submission Queue** — flat table with 2,754 submissions, filterable by stage/LOB/agent, searchable across full dataset, stage badges, action needed column
- **Risk Record** — 55/45 two-column layout. Left: compact submission summary + conversation timeline (real email bodies, attachment links) + pinned draft card (edit/approve/dismiss/copy/mailto). Right: AI analysis, status pipeline, UW decision buttons, documents, gap analysis, LOB requirements, stage history.
- **Analytics** — email volume chart, LOB distribution, email types, top agents
- **System Intelligence** — processing stats, LOB configuration table (all 39 LOBs with configured/generic status, carriers, required fields), data limitations section
- **Outlook Add-in** — deployed at gic-addin.vercel.app, reads current email in Outlook, matches to backend submission, shows analysis + draft in sidebar

### Backend (FastAPI + MongoDB)
- API endpoints: board view, submission detail, search, analytics, system intelligence, health
- Mutation endpoints: stage transitions, draft approve/dismiss/edit, resolve/mark-as-done
- MongoDB collections: emails, submissions, extractions, drafts, sync_state

### Key Files
- **Repo:** `/Users/home/Repositories/gic-email-intelligence/`
- **Backend:** `src/gic_email_intel/` (api/, cli/, agent/, core/)
- **Frontend:** `ui/src/` (pages/, components/, api/, hooks/, lib/)
- **Outlook Add-in:** `addin/src/`
- **LOB configs:** `src/gic_email_intel/agent/lob_configs/` (gl.json, golf_cart.json)
- **Classifier prompt:** `src/gic_email_intel/agent/skills/email_classifier.md`

## Current State of the Data

### MongoDB (gic_email_intelligence on Atlas dev cluster)
```
Emails:        3,214 (all classified, 3,086 linked to submissions)
Submissions:   2,754 (by stage: quoted 2,347 / attention 321 / new 53 / awaiting_info 32 / with_carrier 1)
Extractions:   304
Drafts:        122 (116 suggested, 6 approved, 0 sent, 0 dismissed)
Sync state:    Last sync Mar 16, 2026 — idle
```

### LOB Configuration Status
- **2 configured:** General Liability (10 fields, 2 docs, carriers: USLI + Hiscox), Golf Cart (17 fields, 2 docs, carrier: GIC Underwriters)
- **35 generic:** Using 8 generic required fields. No LOB-specific requirements.

### Golf Cart Submissions (4)
| Insured | Source | Agent | GIC# | Issue |
|---------|--------|-------|------|-------|
| William Wacaster | Motorsports portal | Brian Sandhaus / B & B Insurance | 143085 | Portal collected full app. Draft incorrectly asks for info already in the PDF. |
| Catherine Escalona | Motorsports portal | Ignacio Perez / John Sena Agency | 143097 | Same — portal app is complete. |
| Osvaldo Lopez | Motorsports portal | Daniel Herrera / Univista | 143124 | Same — portal app is complete. |
| Jessica Maria Herrero Garcia | Direct agent email | Susana Avila / Univista | none | **Misidentified.** The attached PDF (QUOTE GOLF CART.pdf) is actually an American Modern quote for Jeffrey Cueto, not a new GIC application. The system wrongly treated this as a new submission needing info. |

### What's Wrong with the Current Drafts

**Critical issue identified at end of session:** The system generates drafts without understanding the actual context of the submission. It sees "new submission" + "missing fields" and always drafts an info request. This produces incorrect/misleading drafts:

1. **Portal submissions** — The Motorsports portal already collected the application data. Drafting an info request for fields that are IN the PDF is wrong. The correct next step is: extract the data, validate completeness, move to UW review/quoting.

2. **Quote shopping emails** — Jessica's email has a competing quote from American Modern attached. The system should recognize this as a quote comparison scenario, not a new submission needing an info request.

3. **General problem** — The system acts (drafts emails) before it understands (what's the actual situation and what's the correct next step). It should: understand → interpret → present information → then act only if the action is correct.

**This applies across ALL lines of business, not just golf carts.** Many of the 122 drafts may be incorrect because the system doesn't understand the actual workflow context.

## What the Demo Needs

### The Three-Act Narrative
1. **"We understand your inbox"** — Analytics showing 3,214 emails across 39 LOBs. Real data.
2. **"We can automate the manual work"** — Show the Outlook Add-in for Maribel's workflow. Show draft replies that are ACTUALLY correct for the context.
3. **"Here's where this is going"** — Submission Queue aligned with Ryan's wireframes. Golf carts as the starting LOB. Path to full automation.

### What Must Be Fixed Before Demo
1. **Draft accuracy** — Drafts must only be generated when they're actually the correct next step. Portal submissions with complete applications should NOT get info request drafts.
2. **Golf cart workflow understanding** — For each of the 4 golf cart submissions, determine the ACTUAL next step based on the email context and attachments.
3. **Jessica Herrero Garcia** — This submission is misidentified. The named insured from the quote PDF is Jeffrey Cueto. The system needs to handle this correctly.
4. **Process-aware intelligence** — Before drafting, the system should present what it knows and what the situation is. Only suggest actions when the correct action is clear.

### What's Ready
- UI is functional: Submission Queue, Risk Record, Analytics, System Intelligence all work
- All buttons wired to real backend endpoints
- Styling unified to warm wireframe palette
- Outlook Add-in deployed with cloudflared tunnel
- 2,754 real submissions from real GIC data

## Ryan's Wireframes (Design Reference)

Located at `/Users/home/Repositories/gic-email-intelligence/artifacts/`:
- `gic_wholesaler_wireframes.html` — GIC-specific screens (Submission Queue + Risk Record)
- `gic_wholesaler_diagram.html` — GIC interaction flow (two streams: CS/servicing + placement/underwriting)
- `indemn_wireframes_v3.html` — Retail agency screens (L1 pipeline, L2 customer workspace, L3 line workstream, L4 carrier detail)
- `indemn_placement_flows.html` — Three operator scenarios (retail, wholesale/MGA, multi-division)
- `indemn_retail_ia.html` — Information architecture
- `indemn_component_inventory_v2.html` — 34 components across L0-L4

Key insight from wireframes: The GIC wholesale flow is **submission-first** (not customer-first like retail). Status tracking per submission per carrier: sent → pending → clarifying → quoted → declined → bound.

## Integration Analysis

Full analysis at `artifacts/2026-03-23-intake-manager-integration-analysis.md`. The intake-manager repo has:
- FastAPI backend with pipeline orchestrator (v1 GPT + v2 Claude deep agent)
- Next.js 16 frontend
- Multi-provider quoting (ACIC, Nationwide PL)
- Email ingestion via Composio
- JWT auth via copilot-server

Our prototype's email intelligence (classification, linking, gap analysis, drafts) is complementary to intake-manager's extraction/validation/quoting pipeline. The target state is merging them.

## Key Decisions Made

- Golf carts is the starting LOB (JC's request). GIC is the carrier for golf carts (not brokering to USLI).
- UI matches Ryan's GIC wholesaler wireframes (Submission Queue table + Risk Record 4-panel)
- Outlook Add-in is central to the day-to-day workflow (not just a demo feature)
- LOB configurations must be transparent and eventually editable
- The system should understand → interpret → present → then act (not act blindly)
- All data must be real — no synthetic/seeded content

## To Run the Demo

```bash
# Backend
cd /Users/home/Repositories/gic-email-intelligence
uv run uvicorn gic_email_intel.api.main:app --port 8080

# Frontend
cd ui && npm run dev

# Tunnel (for Outlook Add-in)
cloudflared tunnel --url http://localhost:8080

# Rebuild add-in with tunnel URL
cd addin
VITE_API_BASE=https://<tunnel>.trycloudflare.com/api VITE_API_TOKEN=0So5zcDzGPnMdADZqh62r8Hpi559W9RbXqJlc3D_RBQ npm run build
cp manifest.xml dist/ && cd dist && npx vercel --prod --yes

# Open web app
open "http://localhost:5173/?token=0So5zcDzGPnMdADZqh62r8Hpi559W9RbXqJlc3D_RBQ"
```
