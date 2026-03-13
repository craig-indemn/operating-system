# GIC Email Intelligence

Build a comprehensive understanding of GIC Underwriters' quoting operation by analyzing their quote@gicunderwriters.com inbox, then design and demo an intelligent system that organizes their workflows, identifies automation opportunities, and eventually connects to all their communication channels (email, phone via RingCentral). The system should be state-based, data-driven, with a data layer that ingestion and processing mechanisms build on top of.

## Status
Session 2026-03-13-b closed. **Data extraction complete. UI design agreed. Ready for detailed technical design.**

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
- Board columns: New → Info Needed → With Carrier → Quoted → Action Required
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
- 2026-03-13: Board columns: New → Info Needed → With Carrier → Quoted → Action Required (to be validated against data)
- 2026-03-13: Autonomous responses shown as drafts in demo (no write access), approve/send in production
- 2026-03-13: Need comprehensive technical design before building — every detail thought through

## Open Questions (for next session)
- Validate lifecycle stages against actual email data — are the 5 columns right?
- How do we link emails to submissions? Reference numbers (143xxx)? Conversation threads? Subject line parsing? Named insured matching? Combination?
- Backend architecture — real-time polling vs webhooks? Processing pipeline design?
- How do we draft accurate autonomous responses? Study GIC's actual info request templates?
- Data model — what's the submission schema? How do state transitions work?
- How does the demo environment work — live data or snapshot?
- How do we test and verify data extraction quality before demoing?
- How does RingCentral data merge into the same pipeline?
- How do we handle the bilingual aspect (Spanish emails)?
- What are the business-line-specific information requirements? (roofing vs restaurants vs trucking)
