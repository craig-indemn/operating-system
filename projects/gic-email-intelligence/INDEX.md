# GIC Email Intelligence

Build a comprehensive understanding of GIC Underwriters' quoting operation by analyzing their quote@gicunderwriters.com inbox, then design and demo an intelligent system that organizes their workflows, identifies automation opportunities, and eventually connects to all their communication channels (email, phone via RingCentral). The system should be state-based, data-driven, with a data layer that ingestion and processing mechanisms build on top of.

## Status
Session 2026-03-13-a closed. **Extraction pipeline built, ready to run.**

**What happened this session:**
- Set up Microsoft Graph API integration (Entra app registration, Exchange Online RBAC scoping to quote@gicunderwriters.com)
- Tested API — confirmed read-only access working, read live emails
- Credentials saved to 1Password, PowerShell setup script saved for customer
- Explored inbox manually — discovered folder structure, email types, sender patterns
- Created project with phased approach (Explore → Workflow Model → Demo → Production Agent)
- Documented exploration objectives and what we need to learn
- Had Claude analyze 25 diverse email samples — discovered 8 email types with subtypes, proposed extraction schema
- Built extraction script (extract_emails.py) — pulls all emails + downloads raw attachments
- Tested extraction pipeline — confirmed working with attachment downloads
- Decision: use Claude vision for ALL PDF extraction (no OCR/PyMuPDF), guarantees accuracy

**Next session:**
1. Run full extraction (all ~3,157 emails + attachments) — `python3 extract_emails.py`
2. Run Claude vision pass on all PDF attachments using parallel subagents
3. With complete dataset, design comprehensive end-to-end plan covering: analysis pipeline, workflow modeling, demo architecture, testing strategy, everything
4. The plan should be a full design document — not just a task list

**What we know so far:**
- 3,153 total emails across all folders (Sep 15 2025 → present, ~6 months)
- 98% have attachments (PDF quote letters, applications, etc.)
- PRIVATE LABEL folder (2,957 emails) = USLI automated quote notifications with structured data
- Inbox (90 emails) = mix of human-driven activity: info requests, replies, phone tickets, bind requests, agent submissions
- GIC is a **wholesale insurance broker** in Miami — sits between retail agents and carriers (USLI, Hiscox, Stoner)
- Sent Items has only 3 emails — GIC staff reply from personal accounts, not from quote@
- Replies from retail agents come back to quote@ inbox (visible as "Re:" and "RE:" threads)
- GIC's internal quoting system (Unisoft) generates numbered submissions (143xxx series)
- Phone tickets from CSR team capture phone call requests as structured emails
- Some communication in Spanish (bilingual operation)
- RingCentral phone integration is coming soon — system should eventually connect to both channels

**Email types identified in manual exploration:**
1. USLI quote notifications (retailer submitted quote via USLI Retail Web)
2. GIC internal system notifications (new quote submissions from Unisoft)
3. Info requests & replies (GIC asks retail agent for missing info, agent replies)
4. Phone tickets (CSR logs phone calls as email tickets to quote inbox)
5. Direct agent submissions (retail agents emailing quote requests/bind requests)
6. Carrier communications (USLI pending files, status updates)
7. Internal routing (GIC staff forwarding items to quote inbox)
8. Urgent follow-ups (agents chasing GIC for responses)
9. Hiscox quote confirmations (separate carrier feed)
10. Reports (daily report packages from Unisoft)

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Microsoft Graph API | API | https://graph.microsoft.com/v1.0/users/quote@gicunderwriters.com |
| GIC Underwriters | Customer | https://www.gicunderwriters.com |
| Entra App Registration | Auth | App ID: 4bf2eacd-4869-4ade-890c-ba5f76c7cada |
| Credentials | 1Password | GIC Outlook Integration |
| RingCentral Integration | OS Project | projects/ringcentral-integration/INDEX.md |
| GIC Improvements | OS Project | projects/gic-improvements/INDEX.md |
| Audio Transcription | Reference | projects/audio-transcription/INDEX.md (similar pipeline approach) |

## Phased Approach

### Phase 1: Exploration & Source of Truth
- Extract all 3,153 emails into structured dataset (JSONL)
- Categorize every email type and map the workflows
- Measure cycle times (submission → info request → reply → outcome)
- Identify all business lines, carriers, retail agents, volume patterns
- Produce comprehensive overview for insurance-experienced teammates
- **Output:** Persistent data foundation + workflow analysis document

### Phase 2: Workflow Model & Automation Design
- Define the formal state machine — every status a quote can be in, every transition
- Flow diagrams for each business line / workflow type
- Identify automation points with the team (where can we speed things up?)
- Design the data layer architecture (state-based, events-driven)
- **Output:** Workflow specifications + automation opportunity map

### Phase 3: Demo Application
- Web app connected to Graph API (real-time email data)
- Pipeline/Kanban view: quotes as cards moving through stages
- Organization layer: group emails into quote lifecycles by reference number
- Automation layer: detect state changes, draft follow-ups, flag bottlenecks
- Eventually connect RingCentral phone data to same pipeline
- **Output:** Working demo that could become production

### Phase 4: Production Agent (future)
- AI agent that processes emails, extracts data, updates state
- Automated follow-ups for missing information
- Integration with GIC's internal systems
- Connected to both email and phone channels
- **Output:** Production system

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-03-13 | [exploration-objectives](artifacts/2026-03-13-exploration-objectives.md) | What are the objectives of exploration and what do we need to learn before building the demo? |
| 2026-03-13 | [email-taxonomy-and-schema](artifacts/2026-03-13-email-taxonomy-and-schema.md) | Email types discovered from 25 samples + proposed extraction schema |

## Decisions
- 2026-03-13: Microsoft Graph API with client credentials flow for email access (read-only Mail.Read)
- 2026-03-13: Exchange Online RBAC scopes access to quote@gicunderwriters.com only
- 2026-03-13: System should be state-based and data-driven with a data layer that processing builds on top of
- 2026-03-13: Inspired by audio-transcription pipeline but adapted for emails — extract everything, have Claude understand everything, synthesize
- 2026-03-13: Demo should connect to everything (email now, RingCentral phone soon)
- 2026-03-13: Claude vision for ALL PDF attachment extraction — no OCR libraries, accuracy over speed
- 2026-03-13: Information requirements = what's needed per business line (complete picture), not just what's missing
- 2026-03-13: The submission is the central entity, not the email — emails are events in a submission's lifecycle
- 2026-03-13: Need comprehensive end-to-end design document before building anything — covering analysis, workflow model, demo, testing

## Open Questions
- What are the actual objectives of exploration? What data do we need for the demo?
- What makes a "great system" we can demo? What would wow GIC?
- How does the data layer work? What's the schema for quote state?
- How do we link emails to quotes? Reference numbers (143xxx)? Conversation threads? Subject line parsing?
- What's the information flow — how are things updated, how does state change?
- How does RingCentral data merge into the same pipeline?
- What does the production agent look like vs the demo?
- Which workflows consume most of GIC's time? (need data to answer)
- How do we handle the bilingual aspect (Spanish emails)?
