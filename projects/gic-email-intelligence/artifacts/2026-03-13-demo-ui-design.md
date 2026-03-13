---
ask: "What should the GIC email intelligence demo look like — UI design, layout, interactions, and how it proves autonomous capability?"
created: 2026-03-13
workstream: gic-email-intelligence
session: 2026-03-13-a
sources:
  - type: conversation
    description: "Brainstorming session — three parallel UI concepts (Augmented Inbox, Submission Command Center, Hybrid Split), refined into final design"
  - type: email
    description: "GIC meeting notes, Kyle's follow-up, partnership agreement — informed stakeholder context and demo requirements"
  - type: microsoft-graph
    description: "3,165 classified emails + 280 PDF extractions informing the data model and workflow understanding"
---

# GIC Email Intelligence — Demo UI Design

## What This Is

A standalone React web app that connects to GIC's quote@gicunderwriters.com inbox via Microsoft Graph API, organizes their email-driven quoting operation into a submission-centric pipeline, and demonstrates autonomous data extraction + suggested actions. Built with React + shadcn/ui frontend, Python backend.

## What the Demo Proves

1. **We can read their emails and extract the data correctly** — every field traceable to its source
2. **We understand their workflows and what happens next** — stage detection, missing info identification
3. **We can act autonomously** — draft follow-ups, identify bottlenecks, suggest next steps
4. **This is better than Outlook** — organized by submission, not by email

## Stakeholders

- **Juan Carlos (JC)** — EVP, Chief Underwriting Officer. Decision maker.
- **Maribel** — GIC staff, champion for email automation and analytics
- **Mukul Gupta** — Granada Insurance, technical coordination

## Constraints

- Read-only email access (Mail.Read via Graph API)
- No write access to their email (can't send drafts)
- No access to internal systems (Unisoft) yet
- Demo uses real email data to prove understanding

## Design Decisions

- **C's architecture + B's features**: Split view layout with submission-centric features
- **Two views with natural flow**: Board → Submission Detail
- **The board IS the inbox**: organized by submission instead of by email
- **Autonomous capability in detail view**: system drafts responses based on what's missing
- **One screen primary experience**: search bar on top, board below, detail as overlay

---

## View 1: The Board

Full-width columns representing submission lifecycle stages. This is the primary view — where you land, where you see everything.

### Top Bar (persistent across all views)

| Element | Position | Purpose |
|---------|----------|---------|
| Logo/app name | Left | Branding |
| Unified search bar | Center, full-width | The phone call test — type insured name, agent, submission number, "restaurants Miami", anything. Instant results. |
| Notification counts | Right of search | "3 new · 5 need response · 2 expiring" — clickable, each filters the board |
| User avatar | Far right | Who's logged in |

### Board Columns

| Column | What's in it | Color accent |
|--------|-------------|--------------|
| **New** | Submissions just received, not yet reviewed | Blue |
| **Info Needed** | GIC needs more info from the agent | Amber |
| **With Carrier** | Submitted to USLI/Hiscox/etc, waiting for quote | Gray |
| **Quoted** | Carrier returned a quote, ready to send to agent | Green |
| **Action Required** | Agent replied, something needs human review | Red |

Columns to validate against actual data — these are hypothesis stages based on email exploration.

### Submission Cards

Each card represents one submission (not one email). Content:

- **Insured name** — bold, primary identifier ("Rodriguez Grocery & Deli")
- **Line of business** — small tag ("GL", "Commercial Package", "Personal Liability")
- **Retail agent + agency** — "Maria Chen · Apex Insurance"
- **Age** — "3 days" with color coding (green < 2 days, amber 2-5, red > 5)
- **Last activity** — "Agent replied 2h ago"
- **Assigned to** — avatar/initials if claimed
- **Action icons** (bottom of card):
  - Email icon — opens latest email in thread
  - Phone icon — agent's phone number, click to call. Badge if phone ticket/recording exists
  - Count indicator — "4 emails · 1 call"

Cards self-sort by urgency within each column — oldest and most urgent at top. No manual prioritization needed.

### Board Interactions

- **Click a card** → opens Submission Detail as full-screen overlay
- **Search** → instant results dropdown with submission card previews, click to open detail
- **Click notification count** → filters board to matching submissions
- **Multi-user**: avatar badges on cards show who's viewing/claimed. Passive awareness, no locking.

---

## View 2: Submission Detail

Opens as a **full-screen overlay** (slide-in or modal) — close it and you're back on the board exactly where you were.

### Header Bar (always visible at top of detail view)

- Back arrow → return to board
- **Insured name** (large) + submission number
- **Line of business** tag
- **Stage badge** (current lifecycle stage)
- **Assigned to** (avatar, reassignable)
- **Agent info**: name + phone (clickable to call) + email
- **Age** and **effective date** if applicable

### Two-Column Layout Below Header

#### Left Column (55%) — The Timeline

Every interaction in chronological order (newest at top):

| Entry Type | Icon | What it shows |
|-----------|------|---------------|
| **Email received** | Envelope | Sender, subject, 1-line preview. Click to expand full body inline. |
| **Email sent** (by GIC) | Envelope with arrow | Same format — shows GIC's outbound messages in the thread |
| **Phone ticket** | Phone | Caller, request summary, agent contact info |
| **USLI notification** | Carrier icon | Quote received — premium + key terms extracted and highlighted |
| **Status change** | Circle arrow | "Moved to Quoting by Sarah K." with timestamp |
| **System note** | Info icon | "Missing: loss runs, subcontractor details" |

Each entry: type icon, sender/source, timestamp, 1-line preview. Click to expand.

Attachments on emails are listed inline — PDF names with file size, clickable to view.

#### Right Column (45%) — Extracted Data + Suggested Action

**Top Section: Extracted Data**

Structured fields pulled from emails and PDFs by Claude:

| Section | Fields |
|---------|--------|
| **Insured** | Name, address, entity type, years in business |
| **Coverage** | Lines requested, limits, deductible, effective date |
| **Carrier** | Which carrier(s), quote status, premium if quoted |
| **Prior Insurance** | Current carrier, expiration, loss history summary |
| **Business Details** | Revenue, employees, square footage, class code — whatever was in the application |

**Completeness Ring** — visual indicator: "7 of 10 required fields complete"
- Required fields are business-line-specific (roofing needs different info than restaurants)
- Missing fields are highlighted below the ring
- Every extracted field has click-to-source — shows the exact email or PDF snippet it came from

**Bottom Section: Suggested Action**

Context-dependent. The system determines what should happen next and shows it:

| Submission State | Suggested Action |
|-----------------|-----------------|
| Missing info | **"Draft follow-up ready"** — shows the drafted email text requesting missing loss runs and subcontractor breakdown. Recipient, subject line, body all pre-filled. |
| Agent replied with info | **"Ready to submit to carrier"** — all required fields complete, system confirms readiness |
| USLI quote received | **"Quote ready to forward to agent"** — key terms summarized (premium, limits, effective date) |
| No response in 5+ days | **"Follow-up #2 draft ready"** — escalation email drafted |
| Agent sent urgent follow-up | **"Urgent — agent has requested 3 times"** — highlights the urgency with full request history |

In the demo: the draft is displayed as "This is what we would send."
In production: an approve/send button.

---

## Technical Architecture

### Frontend
- **React** with **shadcn/ui** component library
- TypeScript
- Responsive but desktop-first (this is an office tool)

### Backend (Python)
- **FastAPI** or similar
- Microsoft Graph API integration (email ingestion)
- Claude API for email classification, data extraction, draft generation
- Database for submission state, extracted data, user assignments

### Data Flow
```
Graph API (emails) → Python backend (classify + extract via Claude) → Database (submissions + extracted data) → React frontend (board + detail views)
```

### Real-time
- Poll Graph API on interval (or use webhooks if available) for new emails
- WebSocket or polling from frontend to backend for live updates

---

## What's NOT in the Demo

- Sending emails (no write access)
- Unisoft integration (no API access yet)
- RingCentral phone integration (coming later)
- User authentication / role-based access (demo uses a single login)
- Analytics dashboard (future feature)
- Mobile support

---

## Demo Flow (when presenting to JC and Maribel)

1. **Open the app** — they see the board with their real submissions, organized by stage
2. **Point out the counts** — "You have 5 submissions waiting for info, 12 new USLI quotes, 2 that have been stuck for a week"
3. **Search for a submission they know** — type an insured name, find it instantly
4. **Open a submission detail** — show the timeline, all emails consolidated
5. **Show extracted data** — "We pulled this from the application PDF" — click to source
6. **Show completeness** — "This submission is missing loss runs and subcontractor info"
7. **Show the draft** — "Here's the follow-up email we'd send to the agent asking for the missing info"
8. **Show an urgent case** — a submission where the agent has followed up 3 times. The system flagged it.
9. **The moment**: "This is running on your live inbox right now. Every email that comes in gets classified, extracted, and organized — automatically."
