# GIC Email Intelligence

Build a comprehensive understanding of GIC Underwriters' quoting operation by analyzing their quote@gicunderwriters.com inbox, then design and demo an intelligent system that organizes their workflows, identifies automation opportunities, and eventually connects to all their communication channels (email, phone via RingCentral). The system should be state-based, data-driven, with a data layer that ingestion and processing mechanisms build on top of.

## Status
Session 2026-03-18-a. **Major UX redesign complete. Reasoning chain, triaged inbox, analytics, conversation threading all built.**

**Repo:** `/Users/home/Repositories/gic-email-intelligence/` (25+ commits on `main`, local only — need org permissions to push)

### Session 2026-03-18-a — UX Redesign
This session transformed the system from a basic board+detail view into a comprehensive inbox intelligence tool:

**Thread Parser & Conversation View**
- Built email thread parser that splits embedded reply chains into individual messages
- Handles Outlook-style, Gmail-style, and Spanish-language separators
- Conversations auto-expand — no click to open. Chat-style bubbles (GIC = blue/right, external = white/left)

**Reasoning Chain (Detail View Right Column)**
- AI Summary: contextual 1-2 sentence analysis of what's happening
- What We Know: extracted data with Email/PDF source indicators
- LOB Requirements: collapsible source of truth from research (GL config)
- Gap Analysis: two-tier — Active Requests (amber, from conversation) + General Requirements (collapsed, gray)
- Amber highlighting connects conversation → gap analysis → draft body

**Draft Workflow**
- Drafts appear as "Suggested Reply" in the conversation thread
- Pin/unpin toggle: inline in conversation or pinned compose bar at bottom
- Edit/Approve/Dismiss with editable text area
- After approve: Copy Draft (clipboard) + Open in Outlook (mailto)
- Missing/internal recipients flagged with editable To field, send blocked until resolved
- Approved status persists on refresh, visible on board cards (green check)

**Board Redesign: Triaged Inbox**
- Replaced 5 lifecycle columns (New, Awaiting Info, With Carrier, Quoted, Attention) with 3 action queues:
  - Ready to Send (8): AI drafted a reply, review and approve
  - Needs Review (0): requires human attention
  - Monitoring (2): waiting on others, no action needed
- Dashboard bar with queue counts and sync status
- Cards show AI action summary ("AI drafted a reply — tap to review")

**Analytics View**
- New "Analytics" tab alongside "Inbox"
- Email volume bar chart (recharts), email type breakdown, LOB distribution, top agents table
- Summary cards: Total Emails (3,214), Email Types (13), Lines of Business (14), Active Agents (3)
- All data from real classified email dataset, queryable by time period

**Data Quality**
- Normalized 105 LOB variants → 35 clean categories across all 3,214 emails
- Fixed email counts (was 2, actually 1 for all submissions)
- Fixed PDF extraction gate (now extracts from all email types, not just carrier)
- Uploaded migrated attachments to S3, fixed download auth + redirect
- Ran PDF extractor on Ojeda (loss runs + cancellation notice now extracted)

**108 tests passing, frontend builds clean**

### Previous: UX Polish (2026-03-17-a)
- Data quality: Fixed submission names, normalized LOBs to Title Case
- Draft visibility, markdown rendering, notification badges, board defaults

### What's Built (2026-03-16-b)
- **98 files, ~13,000 LOC, 108 tests passing**, frontend builds clean
- **Backend**: Python 3.12, FastAPI (9 endpoints + WebSocket with 6 event types) + Typer CLI (7 groups, 25+ commands) + LangChain agent (5 skills, 11 tools)
- **Frontend**: React 19 + TypeScript + Vite + shadcn/ui — Kanban board (5 columns), slide-in detail overlay (timeline, extracted data, LOB-specific completeness ring, draft cards), clickable notification filters, per-field source indicators
- **Docker**: Multi-stage build, supervisord (API + sync + agent), rate limiting, health check
- **Code review**: 25 issues found → all 25 resolved
- **Design audit**: 16 gaps found → all 16 closed — every section of the 1,527-line design matches

### Database State
- 3,214 emails in MongoDB (3,165 migrated + 49 synced live)
- 2,885 pre-classified, 286 extractions, 8 drafts
- 10 sample submissions created by agent (all email types verified)
- S3 bucket `indemn-gic-attachments` with 68 attachments

### UX Testing Findings (2026-03-16-b, late session)
Craig did hands-on browser testing and found the UI was showing system internals instead of actionable info. Key feedback:
- **Cards were confusing**: red age badges (94d), agent reasoning text leaking into attention_reason field, too much crammed in
- **Detail view was useless**: wall of empty `--` dashes, "No extracted data yet" jargon, developer field names, suggested action buried at bottom
- **Email bodies were empty**: migrated emails had no body text (HTML-only emails, text came back empty from Graph API). Fixed by re-fetching from Graph API.
- **Drafts kept getting wiped**: E2E test had `delete_many({})` on drafts collection — fixed to scope cleanup

**Fixes applied:**
- Cards: removed age badges, removed agent reasoning text, show only name/LOB/agent/last-activity/email-count/attention-tag
- Detail: AI suggested action moved to TOP of right column, empty fields hidden, "What We Know" replaces "Extracted Data", human-readable field labels, "Still needed" with Title Case
- Agent: attention_reason validated as enum value, prevents freeform reasoning
- Data: re-fetched email bodies from Graph API for sample submissions

**CRITICAL NEXT SESSION**: The UI needs a full UX review with Craig before demo. Every view and flow must be crafted for maximum impact with Kyle and the GIC customer (JC, Maribel). Current state is functional but not yet demo-polished.

### What's NOT Done
1. **UX polish for demo** — every view and interaction needs to be reviewed for clarity, impact, and user-friendliness. Board cards, detail layout, search behavior, notification flow, email readability.
2. **Full batch processing** — 2,885 classified emails need agent linking + stage detection → ~$15-20 LLM cost, ~1-2 hours with 5 workers. 10-email sample proved pipeline works. Note: will need to re-fetch email bodies from Graph API for all 3,165 emails first.
3. **Push to GitHub** — need `indemn-ai` org permissions
4. **Deploy to AWS** — Docker image tested locally, need ECS/EC2 + domain (`gic.indemn.ai`) + SSL
5. **Demo dry run** — see demo script artifact for full plan

**Previous session (2026-03-16-a — design):**

**Previous sessions (2026-03-13-a and 2026-03-13-b combined):**

**What happened this session (2026-03-13-a and 2026-03-13-b combined):**

### API Setup & Exploration
- Set up Microsoft Graph API integration (Entra app registration, Exchange Online RBAC scoping)
- Confirmed read-only access working, credentials in 1Password
- PowerShell setup script saved for customer at `projects/gic-improvements/artifacts/outlook-integration-setup.ps1`

### Full Data Extraction
- Pulled all 3,165 emails + 5,888 attachments (2.2 GB) via extract_emails.py
- 5,746 PDFs, 102 images, 39 other file types
- Data stored in `data/emails.jsonl` + `data/attachments/`

### PDF Vision Pass (280 samples)
- Strategically sampled 280 PDFs across all email types and business lines
- Processed via 19 parallel Claude subagents reading actual PDFs
- Results in `data/results/batch_XXX_results.json` + `data/all_vision_results.json`
- Document types found: 145 quote letters, 105 application forms, 17 reports, 5 pending notices, plus loss runs, decline letters, portal screenshots, MVRs, driver's licenses, ACORD forms

### Full Email Classification (all 3,165)
- Classified every email via 32 parallel Claude subagents (text-only, no PDFs)
- Results in `data/class_results/cbatch_XXX_results.json` + `data/all_classifications.json`

### Email Type Distribution (complete)
| Type | Count | % |
|------|-------|---|
| USLI Quote | 2,553 | 80.7% |
| USLI Pending | 212 | 6.7% |
| USLI Decline | 147 | 4.6% |
| Agent Submission | 73 | 2.3% |
| Agent Reply | 37 | 1.2% |
| GIC Application | 32 | 1.0% |
| Report | 30 | 0.9% |
| Hiscox Quote | 24 | 0.8% |
| GIC Internal | 21 | 0.7% |
| Agent Followup | 10 | 0.3% |
| Other + misc | 26 | 0.8% |

### Lines of Business (40+ discovered)
Top 15: Personal Liability (887), GL (519), Special Events (245), Non Profit (215), Commercial Package (205), Property (205), Professional Liability/E&O (128), Allied Healthcare (74), Contractors Equipment (71), Excess Liability (64), Umbrella (46), Multi-Class Package (44), Personal Catastrophe/Collections (43), Builder's Risk (42), Excess Personal Liability (39). Plus Marine, Medical Professional, Home Business, Workers Comp, Auto, Trucking, Property Management, Real Estate, D&O, HandyPerson, Liquor Liability, Restaurant, Roofing, Pest Control, and more.

### UI Design (agreed)
- Two-view architecture: **Board** (submission pipeline) → **Submission Detail** (timeline + extracted data + suggested actions)
- Board columns: New → Awaiting Info → With Carrier → Quoted → Attention (updated 2026-03-16, see technical design)
- Detail view: left panel = chronological timeline of all interactions; right panel = extracted data with completeness ring + autonomous draft responses
- Tech: React + shadcn/ui frontend, Python backend
- Full design in `artifacts/2026-03-13-demo-ui-design.md`

### Business Context (from Gmail)
- **Juan Carlos (JC)** — EVP, Chief Underwriting Officer at GIC. Primary contact.
- **Maribel** — GIC staff, champion for email automation/analytics. The end user.
- **Mukul Gupta** — Granada Insurance (GIC parent), technical coordination
- Feb 26 call agreed: start with extracting submission data into viewable dashboard, then auto-responses, then core system data funneling
- Kyle's partnership: $5K implementation + $3K/month for web chat, email agent with data extraction, analytics, and voice agent prototyping
- **Jeremiah** — GIC contact for management system (Unisoft) APIs. Intro requested but not yet made.

**Next session — detailed technical design:**
1. **Validate lifecycle stages against actual email data** — are New/Info Needed/With Carrier/Quoted/Action Required the right stages?
2. **Submission linking logic** — how to connect emails to submissions (reference numbers, conversation threads, named insured matching)
3. **Backend architecture** — real-time email polling, classification pipeline, data model, API design
4. **Autonomous response drafting** — what the system needs to know, how to generate accurate follow-ups, studying GIC's actual info request email patterns
5. **Data model design** — submission schema, email-to-submission linking, state transitions
6. **Real-time ingestion** — how new emails are detected, processed, and displayed
7. **Demo data strategy** — do we use live data or a snapshot? How do we handle the demo environment?
8. **Testing strategy** — how we verify data extraction quality, stage detection accuracy, draft quality
9. **Implementation plan** — what to build first, dependencies, timeline

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Microsoft Graph API | API | https://graph.microsoft.com/v1.0/users/quote@gicunderwriters.com |
| GIC Underwriters | Customer | https://www.gicunderwriters.com |
| Entra App Registration | Auth | App ID: 4bf2eacd-4869-4ade-890c-ba5f76c7cada, Tenant: 7c0931fd-6924-44fe-8fac-29c328791072 |
| Credentials | 1Password | GIC Outlook Integration |
| RingCentral Integration | OS Project | projects/ringcentral-integration/INDEX.md |
| GIC Improvements | OS Project | projects/gic-improvements/INDEX.md |
| Audio Transcription | Reference | projects/audio-transcription/INDEX.md (similar pipeline approach) |
| Feb 26 Meeting Notes | Gmail | Thread: Gemini notes "Indemn & GIC - Agentic Email Automation" Feb 26, 2026 |
| Kyle's Follow-Up | Gmail | "GIC + Indemn - Feb 26 Follow-Up and Next Steps" |
| Partnership Agreement | Gmail | "GIC + Indemn - Updated Partnership Agreement" — $5K impl + $3K/month |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-03-13 | [exploration-objectives](artifacts/2026-03-13-exploration-objectives.md) | What are the objectives of exploration and what do we need to learn before building the demo? |
| 2026-03-13 | [email-taxonomy-and-schema](artifacts/2026-03-13-email-taxonomy-and-schema.md) | Email types discovered from 25 samples + proposed extraction schema |
| 2026-03-13 | [hybrid-split-view-ui-concept](artifacts/2026-03-13-hybrid-split-view-ui-concept.md) | UI concept: hybrid split view with inbox panel + intelligence panel (brainstorm output) |
| 2026-03-13 | [demo-ui-design](artifacts/2026-03-13-demo-ui-design.md) | Final demo UI design — board view + submission detail with autonomous actions |
| 2026-03-16 | [technical-design](artifacts/2026-03-16-technical-design.md) | Comprehensive technical design — architecture, data model, CLI, agent harness, skills, deployment, implementation plan |
| 2026-03-16 | Repo: `/Users/home/Repositories/gic-email-intelligence/` | Full implementation — all 10 phases, 98 files, 79 tests |
| 2026-03-16 | [design-vs-implementation-audit](artifacts/2026-03-16-design-vs-implementation-audit.md) | Section-by-section design audit — 13 MATCH, 3 PARTIAL, 16 gaps identified (all resolved) |
| 2026-03-16 | [demo-script](artifacts/2026-03-16-demo-script.md) | Full demo script for GIC team — flow, live sync testing, Q&A prep, submission picks |
| 2026-03-16 | [ux-testing-findings](artifacts/2026-03-16-ux-testing-findings.md) | Hands-on browser testing findings — card confusion, detail view problems, fixes applied |
| 2026-03-17 | [ux-deep-audit](artifacts/2026-03-17-ux-deep-audit.md) | Deep UX audit from customer perspective — every submission reviewed, 7 of 10 broken, root causes identified |
| 2026-03-18 | [detail-view-reasoning-chain](artifacts/2026-03-18-detail-view-reasoning-chain.md) | Brainstorm: redesign detail view as transparent reasoning chain — conversation → extraction → LOB requirements → gap analysis → editable draft |
| 2026-03-18 | [workflow-integration-design](artifacts/2026-03-18-workflow-integration-design.md) | Approve → Open in Outlook workflow, board draft status visibility, mailto vs Outlook deeplink vs Graph API |
| 2026-03-18 | [gap-analysis-redesign](artifacts/2026-03-18-gap-analysis-redesign.md) | Two-tier gap analysis: active requests (from conversation) vs general LOB requirements, amber color-coding across conversation + gaps + draft |
| 2026-03-18 | [board-redesign-triaged-inbox](artifacts/2026-03-18-board-redesign-triaged-inbox.md) | Brainstorm: replace lifecycle columns with action queues (Ready to Send, Needs Review, Monitoring) + dashboard analytics bar |
| 2026-03-18 | [analytics-view-design](artifacts/2026-03-18-analytics-view-design.md) | Analytics view design — volume, types, LOBs, agents, operational health metrics |

## Key Data Files
| File | What it contains |
|------|-----------------|
| `data/emails.jsonl` | All 3,165 emails — metadata + body text + attachment info |
| `data/attachments/` | 5,888 raw attachment files (2.2 GB), organized by email index |
| `data/all_classifications.json` | Claude classification of all 3,165 emails (type, line of business, named insured, reference numbers) |
| `data/all_vision_results.json` | Claude vision extraction of 280 sampled PDFs (structured insurance data) |
| `data/vision_sample.jsonl` | The 280 emails selected for PDF vision processing |
| `data/batches/` | Batch files for vision processing (19 batches) |
| `data/class_batches/` | Batch files for classification (32 batches) |
| `data/results/` | Per-batch vision results |
| `data/class_results/` | Per-batch classification results |
| `extract_emails.py` | Email + attachment extraction script |
| `sample_for_vision.py` | Strategic PDF sampling script |
| `prepare_batches.py` | Vision batch preparation script |
| `prepare_classification_batches.py` | Classification batch preparation script |

## Decisions
- 2026-03-13: Microsoft Graph API with client credentials flow for email access (read-only Mail.Read)
- 2026-03-13: Exchange Online RBAC scopes access to quote@gicunderwriters.com only
- 2026-03-13: System should be state-based and data-driven with a data layer that processing builds on top of
- 2026-03-13: Claude vision for PDF attachment extraction (no OCR libraries)
- 2026-03-13: The submission is the central entity, not the email — emails are events in a submission's lifecycle
- 2026-03-13: Demo is a standalone React + Python web app, not an Outlook plugin
- 2026-03-13: Two-view UI: Board (pipeline) → Submission Detail (timeline + data + suggested actions)
- 2026-03-13: React + shadcn/ui for frontend, Python for backend
- 2026-03-13: Autonomous responses shown as drafts in demo (no write access), approve/send in production
- 2026-03-13: Need comprehensive technical design before building — every detail thought through
- 2026-03-16: 5 action-oriented columns: New, Awaiting Info, With Carrier, Quoted, Attention (validated against data)
- 2026-03-16: Reference numbers are primary linking key (96.2% coverage). Conversation threading is useless.
- 2026-03-16: Agent harness with CLI + Skills pattern — CLI is the CRUD interface, DeepAgent is the brain
- 2026-03-16: This is the first instance of Indemn's generalizable agentic workflow pattern (DeepAgent + Skills + CLI)
- 2026-03-16: MongoDB on existing Atlas cluster, separate `gic_email_intelligence` database
- 2026-03-16: AWS deployment (ECS/EC2 + S3) alongside existing infrastructure
- 2026-03-16: LOB requirements derived from quote output data (quote fields ≈ application input). Start with GL.
- 2026-03-16: Live connection for demo, not a snapshot
- 2026-03-16: Neutral/white-label UI — no specific branding, brand later
- 2026-03-16: Clean and professional visual style — advanced but approachable
- 2026-03-16: Implementation uses structured LangChain tools (call core library directly) instead of CLI subprocess for agent — faster, type-safe, no shell quoting issues
- 2026-03-16: Auth via Authorization Bearer header for REST, query param for WebSocket (browser WS API doesn't support custom headers)
- 2026-03-16: Token persisted in sessionStorage to survive React Router navigation
- 2026-03-16: Atomic $min for first_email_at instead of read-then-write (race condition fix)
- 2026-03-16: Single $facet aggregation for board view instead of N+1 per-stage queries
- 2026-03-16: Cards show only what matters: name, LOB, agent, last activity, email count. No age badges.
- 2026-03-16: Detail view leads with action (AI draft), not data. Empty fields hidden. Human-readable labels.
- 2026-03-16: UX must be reviewed and polished per-view before demo — functional != demo-ready
- 2026-03-18: Emails in quote@ contain full conversation threads embedded in the body — parse them, don't treat as single messages
- 2026-03-18: Detail view right column is a transparent reasoning chain: Summary → Extraction → Requirements → Gap Analysis
- 2026-03-18: Gap analysis has two tiers: Active Requests (from conversation, amber) + General LOB Requirements (collapsed, gray)
- 2026-03-18: Amber color-coding connects gap items across conversation, gap analysis, and draft body
- 2026-03-18: Draft lives in the conversation as "Suggested Reply", pinnable to bottom as compose bar
- 2026-03-18: Don't fall back to internal GIC addresses for drafts — flag missing recipients, let user fill in
- 2026-03-18: Extract PDFs from ALL email types, not just carrier notifications (agent replies have loss runs too)
- 2026-03-18: Board redesigned from lifecycle stages to action queues: Ready to Send, Needs Review, Monitoring
- 2026-03-18: The product is an inbox augmentation tool — eventually an Outlook plugin, first objective is automating info requests
- 2026-03-18: Analytics view shows email volume, types, LOBs, agents — real-time understanding of the inbox
- 2026-03-18: LOB normalization: 105 variants consolidated to 35 clean categories

## Open Questions (deferred — not blocking demo)
- How does RingCentral data merge into the same pipeline? (Same pattern: RingCentral CLI + skills)
- How do we handle the bilingual aspect? (Classifier skill handles Spanish; draft generator needs Spanish templates)
- Business-line-specific requirements beyond GL? (Each LOB gets a config file following GL pattern, expand post-demo)
- Multi-tenancy for other brokers? (Add tenant_id to all collections if needed)
- Unisoft integration? (Depends on Jeremiah intro — not yet made)
- Email sending in production? (Requires Mail.Send permission, separate Entra consent from GIC)
