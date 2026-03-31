# GIC Email Intelligence

Build a comprehensive understanding of GIC Underwriters' quoting operation by analyzing their quote@gicunderwriters.com inbox, then design and demo an intelligent system that organizes their workflows, identifies automation opportunities, and eventually connects to all their communication channels (email, phone via RingCentral). The system should be state-based, data-driven, with a data layer that ingestion and processing mechanisms build on top of.

## Status

**Session 2026-03-31. Production live, critical bugs fixed, ready for full re-sync + backfill.**

System is deployed on Railway + Amplify. Auth works (copilot-server JWT). Week 1 backfill completed (124 emails) but revealed two critical data issues that require a full re-sync before continuing:

1. **Empty email bodies** — Graph API `Prefer: text` header caused HTML-only emails to sync with empty body. Fixed: removed text preference, sync now captures HTML and extracts text. All existing emails need re-sync.
2. **Empty extracted_fields** — `dict[str, Any]` in Pydantic schema generated an empty JSON schema that LangChain/Anthropic enforced as "must be empty object." Fixed: replaced with `list[ExtractedField]` (explicit key/value pairs). Verified working — 10+ fields now extracted per PDF.

**Next step:** Full re-sync (delete all emails, re-pull from Graph API with body fix), clean slate, then backfill 1 month in weekly batches with Haiku.

**What was done this session (2026-03-30/31):**
1. **Production deployment plan** — Full brainstorm: Railway backend, Amplify frontend, shared JWT auth, MongoDB proxy, weekly backfill strategy. See `artifacts/2026-03-30-production-deployment-plan.md`.
2. **Fixed extraction pipeline** — Replaced broken ReAct pdf-extractor with structured output module. Downloads from S3, sends as multimodal content blocks, gets validated Pydantic model.
3. **Pipeline reorder** — extract → classify → link (was classify → link → extract). Classifier now has extraction context.
4. **Configurable stages** — `PIPELINE_STAGES=extract,classify,link` env var. Assess/draft disabled by default.
5. **JWT auth** — Copilot-server integration. Login page, signin proxy, GIC org scoping. Fixed: token "JWT " prefix stripping, CORS origins, 401 race condition.
6. **Railway deployment** — 3 services (API, sync cron, processing cron). MongoDB proxy through dev-services EC2. Primary detection script. Static IP `162.220.234.15`.
7. **Amplify deployment** — `gic.indemn.ai` (prod), dev on Amplify default domain. Route 53 DNS.
8. **Observatory link** — PR #57 at indemn-ai/indemn-observatory, GIC org scoped. Awaiting review.
9. **Week 1 backfill** — 124 emails processed (123 succeeded, 1 failed). Revealed empty body + empty extracted_fields bugs.
10. **Bug fixes:** Graph API datetime format (Z suffix), PDF attachment URLs (VITE_API_BASE), CORS origins, orphaned submissions cleanup.
11. **Root cause: empty extracted_fields** — `dict[str, Any]` → `list[ExtractedField]`. LangChain/Anthropic set `additionalProperties=false` on dict schemas. See pydantic-ai #4117.
12. **Root cause: empty email bodies** — Graph API `Prefer: text` returns empty for HTML-only emails. Removed preference, added `_extract_body()` helper.
13. **Skills created** — Railway CLI, AWS Amplify, LangChain. All in OS `.claude/skills/` with references.

**Production URLs:**
- Frontend: `https://gic.indemn.ai` (prod) / `https://main.d244t76u9ej8m0.amplifyapp.com` (dev)
- API: `https://api-production-e399.up.railway.app` (prod) / `https://api-production-79f0.up.railway.app` (dev)
- Login: `support@indemn.ai` (or any copilot account with GIC org)
- GitHub: `craig-indemn/gic-email-intelligence` (private)
- Railway project: `4011d186-1821-49f5-a11b-961113e6f78d` (environments: development, production)
- Amplify app: `d244t76u9ej8m0` (branches: main → dev, prod → gic.indemn.ai)

**Infrastructure:**
- MongoDB proxy: dev-services EC2 (44.196.55.84), ports 27017-27019 (dev), 27020-27022 (prod)
- Static IP: `162.220.234.15` (Railway Pro, per-service — must enable on each service in dashboard)
- Sync cron: **paused** (pending re-sync)
- Processing cron: **paused** (pending re-sync + clean slate)

**Backfill plan (not yet executed):**
1. Delete all emails from MongoDB
2. Re-sync all emails from Graph API (with body fix — captures HTML)
3. Clean slate all derived data
4. Process 1 month (March 2026) in weekly batches with Haiku (~$25-35 estimated)

**Known issues to address:**
- UI: extracted fields section vs gap analysis is confusing (layout/UX issue, noted in `artifacts/2026-03-31-ui-issues-noted.md`)
- Socat proxy not persistent (nohup, not systemd — dies on EC2 reboot)
- MongoDB proxy is temporary — remove when Atlas IP allowlist updated with Railway static IP
- Observatory link PR awaiting team review

**Key references:**
- Pipeline review: `artifacts/2026-03-30-pipeline-architecture-review.md`
- Deployment plan: `artifacts/2026-03-30-production-deployment-plan.md`
- Implementation plan: `artifacts/2026-03-30-production-implementation-plan.md`
- MongoDB proxy: `artifacts/2026-03-30-mongodb-proxy-setup.md`
- UI issues: `artifacts/2026-03-31-ui-issues-noted.md`

---

**What was built this session (2026-03-30):**
1. **Production deployment plan** — Full brainstorm: Railway backend, Amplify frontend, shared JWT auth, MongoDB proxy, weekly backfill strategy. See `artifacts/2026-03-30-production-deployment-plan.md`.
2. **Fixed extraction pipeline** — Replaced broken ReAct pdf-extractor (couldn't see PDFs) with structured output module. Downloads from S3, sends as multimodal content blocks, gets validated Pydantic model. Unbiased schema (`dict[str, Any]`).
3. **Pipeline reorder** — extract → classify → link (was classify → link → extract). Classifier now has extraction context.
4. **Configurable stages** — `PIPELINE_STAGES=extract,classify,link` env var. Assess/draft disabled by default.
5. **JWT auth** — Copilot-server integration. Login page, signin proxy, GIC org scoping. Token prefix "JWT " handling.
6. **Railway deployment** — 3 services (API, sync cron, processing cron). MongoDB proxy through dev-services EC2. Primary detection script. Static IP `162.220.234.15`.
7. **Amplify deployment** — `gic.indemn.ai` (prod), dev on Amplify default domain. Route 53 DNS.
8. **Observatory link** — Mail icon in header links to `gic.indemn.ai/?token=${jwt}` (code written, not yet deployed).
9. **Clean slate on prod** — All derived data deleted. 3,469 emails reset to pending.
10. **Skills created** — Railway CLI, AWS Amplify, LangChain. All in OS `.claude/skills/` with references.

**Production URLs:**
- Frontend: `https://gic.indemn.ai` (prod) / `https://main.d244t76u9ej8m0.amplifyapp.com` (dev)
- API: `https://api-production-e399.up.railway.app` (prod) / `https://api-production-79f0.up.railway.app` (dev)
- Login: `support@indemn.ai` (or any copilot account with GIC org)
- GitHub: `craig-indemn/gic-email-intelligence` (private)
- Railway project: `4011d186-1821-49f5-a11b-961113e6f78d`
- Amplify app: `d244t76u9ej8m0`

**Backfill status:** Week 1 (Mar 1-8, 124 emails) processing with Haiku. Weeks 2-4 pending assessment.

**What's NOT done:**
1. Backfill weeks 2-4 (Mar 8-31)
2. Sync cron bug (datetime timezone format)
3. Observatory link deployment
4. LOB configs beyond GL/Golf Cart
5. No URL routing in frontend
6. MongoDB proxy is temporary (remove when Atlas IP allowlist updated)
7. Socat not persistent (nohup, not systemd — dies on EC2 reboot)

**Key references:**
- Pipeline review: `artifacts/2026-03-30-pipeline-architecture-review.md`
- Deployment plan: `artifacts/2026-03-30-production-deployment-plan.md`
- Implementation plan: `artifacts/2026-03-30-production-implementation-plan.md`
- MongoDB proxy: `artifacts/2026-03-30-mongodb-proxy-setup.md`

---

**Session 2026-03-25. Demo delivered to JC and Maribel.** Full system live with 3,469 emails, 2,894 submissions, all assessed. Indemn branding applied. Outlook Add-in working. Demo walked through Overview → submission examples → Outlook sidebar → golf cart automation path.

**What was built this session (2026-03-24/25):**
1. **Business model research** — 7 research documents (171KB) analyzing GIC's actual operations from email data, web research, Gmail threads, Ryan's UX observations. Key finding: 93% of inbox is automated USLI notifications, only 5% of submissions need human work. See `research/business-model-synthesis.md`.
2. **8-stage lifecycle redesign** — Replaced broken 5-stage model. Added situation assessment layer ("understand before acting"), carrier/agent entities, ball-holder tracking. Design reviewed 3 times. See `artifacts/2026-03-24-data-model-redesign.md`.
3. **Full implementation** — 25 files changed (backend + frontend), 4-wave parallel execution. Models, tools, pipeline, API routes, all UI pages updated.
4. **Assessment backfill** — All 2,894 submissions assessed via parallel subagents. 105 legitimate drafts generated (82 decline notifications, 15 info requests, 8 quote forwards).
5. **Root cause fix: draft accuracy** — Disabled draft types the system can't produce accurately (status_update, followup, remarket_suggestion) until data sources exist. Documented WHY each is disabled and WHAT enables it.
6. **Fresh data sync** — Synced 255 new emails (Mar 16-25), classified and linked via subagents. 13 recent submissions had PDFs extracted and assessed.
7. **UI honest-ification** — UI only shows what's real. Gap analysis hidden for generic LOBs. Auto-notified USLI submissions dimmed. UW buttons are honest manual stage transitions. Pipeline bar simplified for auto-notified.
8. **Indemn branding** — Barlow font, CSS variable design system, GIC logo + "Powered by Indemn", Indemn iris accent color. Clickable table rows.
9. **Overview page** — 5-section demo narrative (what we did, what we found, how it works, what it means, automation path).
10. **Outlook Add-in** — Deployed to Vercel, cloudflared tunnel to localhost, 4 demo emails seeded.

**Previous sessions:** 2026-03-20 (Outlook Add-in), 2026-03-18/19 (inbox intelligence tool), 2026-03-16 (full implementation), 2026-03-13 (initial data extraction + classification).

**Repo:** `/Users/home/Repositories/gic-email-intelligence/` (50+ commits on `main`, local only)

### Research
Living research corpus in `research/` — 7 documents, 171KB, updated 2026-03-24. Start with `research/business-model-synthesis.md` for the unified picture. See `research/README.md` for full index.

### Current State (as of 2026-03-25)
- **3 tabs**: Submissions (queue), Overview (demo narrative), Insights (merged analytics + system)
- **3,469 emails** synced (last sync Mar 25), classified, linked to 2,894 submissions
- **2,894 submissions** — all assessed. 8-stage lifecycle: received, triaging, awaiting_agent_info, awaiting_carrier_action, processing, quoted, declined, closed
- **~330 PDF extractions** across ~30 submissions. 97% of PDFs still unextracted (extraction is the main data gap)
- **105 suggested drafts** — 82 decline notifications, 15 info requests, 8 quote forwards. All backed by assessments, all enabled draft types only.
- **3 new MongoDB collections**: assessments (2,894), carriers (3: USLI, Hiscox, Granada), agents (55)
- **Indemn design system** — Barlow font, CSS variables, GIC logo, "Powered by Indemn"
- **Outlook Add-in** — deployed at gic-addin.vercel.app. Needs cloudflared tunnel to connect to local backend.
- **LOB configs**: GL (10 fields) and Golf Cart (17 fields) configured. 35 others use generic 8-field config.
- **Draft types**: 3 enabled (info_request, quote_forward, decline_notification). 3 disabled (status_update, followup, remarket_suggestion) — documented in situation_assessor.md and harness.py.

### To Run
```bash
# Backend
cd /Users/home/Repositories/gic-email-intelligence
uv run uvicorn gic_email_intel.api.main:app --port 8080

# Frontend
cd ui && npm run dev

# Outlook Add-in (optional — needs tunnel)
nohup cloudflared tunnel --url http://localhost:8080 > /tmp/cloudflared.log 2>&1 &
# Get tunnel URL from /tmp/cloudflared.log, then:
cd addin && VITE_API_BASE=https://<tunnel>.trycloudflare.com/api VITE_API_TOKEN=0So5zcDzGPnMdADZqh62r8Hpi559W9RbXqJlc3D_RBQ npm run build
cp manifest.xml dist/ && cd dist && npx vercel --prod --yes && npx vercel alias gic-addin.vercel.app

# Web app URL
open "http://localhost:5173/?token=0So5zcDzGPnMdADZqh62r8Hpi559W9RbXqJlc3D_RBQ"
```

### Demo Examples (verified, extraction-backed)
| Submission | LOB | Story | Draft |
|-----------|-----|-------|-------|
| Vivaria Florida LLC | GL | Complete ACORD submission, 100% extracted, system correctly didn't request info | None (correct) |
| Klein International LLC | GL | USLI pending file, agent partial reply, draft requests remaining items | info_request to lbenitez@doraladvisors.com |
| Magdalena Soto | Commercial Property | USLI decline with 2 specific reasons from PDFs | decline_notification to glendys@sebandainsurance.com |
| William Wacaster | Golf Cart | Portal submission, 95% extracted, ready for UW — the automation story | None (correct) |

### Key Architecture Decisions
- **Situation assessment is the single source of truth** for completeness, gap analysis, and draft decisions. `compute_completeness()` is the fallback only when no assessment exists.
- **Draft types are gated** — only info_request, quote_forward, decline_notification are enabled. Others disabled until data sources exist (management system API, outbound tracking, carrier appetite data). Guard in harness.py `ENABLED_DRAFT_TYPES`.
- **Assessments drive everything downstream** — the pipeline is: classify → link → extract → assess → [maybe draft]. The assessor replaces the old stage_detector. See `situation_assessor.md`.
- **Two operating modes**: brokered (USLI/Hiscox) vs direct_underwritten (golf carts on Granada paper). Encoded in `operating_mode` field and LOB config `workflow_type`.
- **Auto-notified USLI submissions** (95% of volume) get template assessments and are dimmed in the UI. The 5% that need human work are the focus.

### What's NOT Done
1. **PDF extraction coverage** — only ~330 of 3,100+ PDFs extracted (10%). This is the biggest data gap. Submissions without extractions have inaccurate completeness and may have wrong drafts.
2. **LOB configs** — only GL and Golf Cart configured. 35 LOBs use generic 8-field config. Gap analysis hidden for these.
3. **Disabled draft types** — status_update, followup, remarket_suggestion need: management system API (Unisoft/Jeremiah), outbound email tracking, carrier appetite data.
4. **No URL routing** — React useState navigation, no shareable URLs, browser back doesn't work.
5. **Push to GitHub** — still local only, need indemn-ai org permissions.
6. **Production deployment** — running on localhost. Needs AWS (ECS/EC2 + domain + SSL).
7. **Email sending** — drafts are suggestions only. Actual sending requires Mail.Send permission from GIC.

### Session 2026-03-20 — What Was Built

**Outlook Add-in (end-to-end working)**
- React task pane (350px sidebar) with 6 components: TaskPane, SubmissionHeader, AddinSummary, AddinGapAnalysis, AddinDraft
- Office.js integration: reads current email subject/body, extracts ref numbers, calls backend lookup
- ItemChanged handler for re-fetching when switching emails (pinning works on M365 work accounts)
- `displayReplyAllFormAsync()` for "Reply with this" — opens native Outlook reply with draft pre-filled
- Markdown-to-HTML conversion in draft preview and reply (bold, italic, bullets)
- Deployed to Vercel at `gic-addin.vercel.app`
- Indemn BubbleMark (iris) branding at 16/32/80px

**Backend: Lookup Endpoint**
- `POST /api/lookup-email` with 5-step matching waterfall: internet_message_id → submission ref numbers → email classification ref numbers → subject match → fuzzy name match
- Extracted `get_submission_detail()` helper from inline route handler for reuse
- Server-side reference number extraction from subject (catches non-USLI formats)
- CORS updated for Vercel + cloudflare tunnel origins

**Email Seeding Script**
- `scripts/seed_outlook.py` — OAuth flow + Graph API sendMail to personal Outlook.com
- 5 demo emails covering: carrier pending, declined, quoted, new, awaiting info
- Entra app registered: `0ec79e75-d1c6-4f65-8418-22a4ed7a6506` (personal account, Mail.ReadWrite + Mail.Send + User.Read)

**Infrastructure**
- Hello-world sideload validation at `addin-test.vercel.app` (confirmed Office.js loads on personal Outlook.com)
- Cloudflared tunnel for exposing localhost:8080 to Vercel-hosted add-in
- 4-round design review cycle before implementation (all issues resolved)

**To run the demo:**
1. `cd /Users/home/Repositories/gic-email-intelligence && uv run uvicorn gic_email_intel.api.main:app --port 8080`
2. `cloudflared tunnel --url http://localhost:8080` — note the tunnel URL
3. Rebuild add-in with tunnel URL: `cd addin && VITE_API_BASE=https://<tunnel>.trycloudflare.com/api VITE_API_TOKEN=0So5zcDzGPnMdADZqh62r8Hpi559W9RbXqJlc3D_RBQ npm run build`
4. Deploy: `cp manifest.xml dist/ && cd dist && npx vercel --prod --yes`
5. Sideload `addin/manifest.xml` on Outlook.com
6. Open a seeded email → click "Analyze Email"

### Session 2026-03-18/19 — What Was Built

**Thread Parser & Conversation View**
- Email thread parser splits embedded reply chains into individual messages (Outlook, Gmail, Spanish separators)
- Conversations auto-expand as chat-style bubbles (GIC = blue/right, external = white/left)

**Reasoning Chain (Detail View Right Column)**
- AI Summary → What We Know (with sources) → LOB Requirements → Gap Analysis → Suggested Draft
- Stage-aware gap analysis: new submissions check full LOB requirements, quoted submissions only check quote details, declines show no requirements
- Two-tier gap analysis: Active Requests (amber, from conversation) + General Requirements (collapsed)
- Amber highlighting connects conversation → gap analysis → draft body

**Draft Workflow**
- Drafts as "Suggested Reply" in conversation, pinnable to bottom as compose bar
- Edit/Approve/Dismiss with editable text area
- After approve: Copy Draft (clipboard) + Open in Outlook (mailto)
- Auto-prompt "Mark as done?" after sending → resolves submission
- Missing/internal recipients flagged with editable To field, send blocked until resolved
- Manual "Mark as Done" button in detail header

**Board: Triaged Inbox**
- 3 action queues: Ready to Send, Needs Review, Monitoring
- Cards show lifecycle badges (📋 New, ✅ Quoted, ⚠️ Declined) + AI action summaries
- Meaningful empty states ("All caught up", "Nothing needs your attention")
- Dashboard bar with queue counts and sync status

**Done State & History**
- POST /api/submissions/{id}/resolve with resolution type (quote_forwarded, info_request_sent, decline_notified, manually_closed)
- Resolved submissions excluded from board and dashboard counts
- History section in Analytics with color-coded resolution badges
- GET /api/submissions/history endpoint

**Analytics & How It Works**
- Analytics tab: volume chart, email type breakdown, LOB distribution, top agents, resolution history
- How It Works tab: 7 sections explaining methodology with real numbers (3,214 emails, 13 types, 280 PDFs, etc.)
- Stage-aware requirement profiles explained with color-coded cards

**Data Quality & Infrastructure**
- 105 LOB variants → 35 clean categories
- All 5,888 attachments uploaded to S3
- PDF extraction from all email types (not just carrier)
- Batch processing with --model and --limit flags (Haiku for cost efficiency)

### What's NOT Done
1. **Full batch processing** — Only 100 of 3,155 emails processed through linker/stage/draft pipeline. 9 submissions still have no drafts (Haiku failed silently). Many email loops not yet closed because related emails haven't been linked.
2. **OCR for scanned PDFs** — Some USLI quote PDFs are scanned images. AI vision can identify them but can't extract premium/limits/effective date. Need OCR preprocessing (Tesseract/Textract).
3. **HTML attachment extraction** — Mercado Insurance has an HTML application file that the extractor doesn't handle.
4. **Push to GitHub** — Need indemn-ai org permissions
5. **Deploy to AWS** — Docker image → ECS/EC2, domain (gic.indemn.ai), SSL. Would eliminate need for cloudflared tunnel.
6. **Demo video recording** — Craig wants to record a walkthrough before showing to GIC
7. **Pinning on personal Outlook.com** — SupportsPinning in manifest but pin icon doesn't appear on consumer accounts. Works on M365 work accounts (GIC deployment).
8. **Remove debug output** — TaskPane shows debug JSON on no-match state. Remove before demo.
9. **Production auth** — Add-in uses embedded API token. Production needs Office.js SSO (`getAccessTokenAsync`).
10. **internetMessageId storage** — Not in sync pipeline yet. Production needs it for exact email matching.

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
| 2026-03-18 | [lifecycle-done-state-history](artifacts/2026-03-18-lifecycle-done-state-history.md) | Done state design: what "done" means, resolution types, history view, first-time onboarding |
| 2026-03-19 | [outlook-addin-research](artifacts/2026-03-19-outlook-addin-research.md) | Outlook Add-in development research — architecture, APIs, deployment, testing, constraints for GIC plugin |
| 2026-03-19 | [outlook-addin-design](artifacts/2026-03-19-outlook-addin-design.md) | Outlook Add-in design — task pane UI, lookup endpoint, email seeding, demo strategy, deployment plan |
| 2026-03-20 | Implementation plan at `docs/plans/2026-03-20-outlook-addin-implementation.md` (in repo) | 14-task implementation plan with parallel tracks for backend, frontend, seeding, and integration |
| 2026-03-23 | [intake-manager-integration-analysis](artifacts/2026-03-23-intake-manager-integration-analysis.md) | Full exploration of intake-manager codebase + side-by-side comparison + integration vision for merging GIC intelligence into intake-manager |
| 2026-03-23 | [gic-demo-strategy](artifacts/2026-03-23-gic-demo-strategy.md) | Demo strategy for JC/Maribel: 3-act narrative, targeted reclassification, UI reshape to Ryan's wireframes, golf cart LOB focus, 2-day execution plan |
| 2026-03-24 | [session-handoff](artifacts/2026-03-24-session-handoff.md) | Comprehensive handoff: system state, data pipeline, UI status, critical draft accuracy issue, golf cart analysis, what needs fixing |
| 2026-03-24 | [data-model-redesign](artifacts/2026-03-24-data-model-redesign.md) | Comprehensive data model & lifecycle redesign — 8-stage model, situation assessment layer, context-aware draft generation, sourced from 7 research documents |
| 2026-03-24 | [implementation-plan](artifacts/2026-03-24-implementation-plan.md) | 4-wave implementation plan with 15 parallel tasks — backend, frontend, migration, browser testing |
| 2026-03-25 | [demo-talking-points](artifacts/2026-03-25-demo-talking-points.md) | Demo walkthrough for JC — 4 acts, talking points, examples, Q&A prep |
| 2026-03-30 | [pipeline-architecture-review](artifacts/2026-03-30-pipeline-architecture-review.md) | Complete end-to-end pipeline walkthrough — every step, every file, every limitation. Pre-production review. |
| 2026-03-30 | [production-deployment-plan](artifacts/2026-03-30-production-deployment-plan.md) | Full production plan — Railway backend, Amplify frontend, pipeline fix, auth, Observatory integration, historical data processing, definition of done |
| 2026-03-30 | [production-implementation-plan](artifacts/2026-03-30-production-implementation-plan.md) | Bite-sized implementation plan — 16 tasks across 4 parallel tracks (pipeline fix, infra, auth, production) |
| 2026-03-30 | [mongodb-proxy-setup](artifacts/2026-03-30-mongodb-proxy-setup.md) | EC2 socat proxy setup for Railway → Atlas connectivity. Temporary. Includes teardown instructions. |
| 2026-03-31 | [ui-issues-noted](artifacts/2026-03-31-ui-issues-noted.md) | UI issues from prod review — extracted fields vs gap analysis confusion, PDF links (fixed), empty bodies (fixed) |

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
- 2026-03-18: Gap analysis is stage-aware: new submissions check full LOB requirements, quoted checks only quote details, declined has no requirements
- 2026-03-18: "Done" means: draft sent (auto-prompted), manually closed, or superseded. Resolution types: quote_forwarded, decline_notified, info_request_sent, followup_sent, manually_closed
- 2026-03-18: Resolved submissions excluded from board, visible in Analytics History section
- 2026-03-18: How It Works page explains methodology — data sources, classification, linking, extraction, stage-aware requirements, draft generation, pipeline
- 2026-03-18: Use Haiku for batch processing (10x cheaper), Sonnet for PDF extraction quality
- 2026-03-18: Some USLI PDFs are scanned images — need OCR preprocessing for premium/limits extraction
- 2026-03-19: Build Outlook Web Add-in (Office.js) as task pane sidebar — React app deployed to Vercel, reads current email via Office.js, matches to backend via reference numbers
- 2026-03-19: Reply mechanism: displayReplyAllFormAsync() — opens native Outlook reply with draft pre-filled, no Mail.Send permission needed
- 2026-03-19: Demo strategy: seed emails from GIC's quote@ into Craig's personal Outlook.com inbox via Graph API delegated permissions, sideload add-in there
- 2026-03-19: Matching waterfall: internet_message_id (real deployment) → reference_numbers (demo) → fuzzy insured name (fallback)
- 2026-03-19: Standalone web app stays as analytics/management view, add-in is the day-to-day workflow tool
- 2026-03-20: Outlook Add-in renamed to "Indemn Email Intelligence" with Indemn BubbleMark branding
- 2026-03-20: Lookup endpoint enhanced: email classification ref matching + subject matching + server-side extraction (handles non-USLI ref formats)
- 2026-03-20: Demo emails seeded via sendMail to personal Outlook.com (craigindemn@outlook.com) — direct inbox creation doesn't activate add-ins
- 2026-03-20: Pinning (SupportsPinning) requires VersionOverridesV1_1, not V1_0 — works on M365 work accounts, not personal Outlook.com
- 2026-03-20: Cloudflared tunnel needed for demo (add-in on Vercel can't reach localhost backend)
- 2026-03-30: Post-demo direction shift: focus on data quality and extraction pipeline, not auto-drafts/ball-holder. System becomes pipeline into AMS (Unisoft).
- 2026-03-30: Railway for backend (3 services: API, sync cron, processing cron), AWS Amplify for frontend
- 2026-03-30: Pipeline reorder: extract → classify → link. Extraction first so classifier has PDF content.
- 2026-03-30: Assess and draft stages disabled by default via PIPELINE_STAGES config. Re-enable when data sources exist.
- 2026-03-30: JWT auth via copilot-server (prod: copilot.indemn.ai). Shared JWT_SECRET, HS256, no exp verification.
- 2026-03-30: GIC org scoped access: @indemn.ai = admin, GIC org members = access, others = 403.
- 2026-03-30: MongoDB Atlas proxy via dev-services EC2 (socat). Temporary until Atlas IP allowlist updated.
- 2026-03-30: Railway static IP per-service, not per-project. Must enable on each service individually.
- 2026-03-30: railway.json should NOT set startCommand or healthcheckPath — these are per-service via GraphQL API.
- 2026-03-30: Copilot-server returns token as "JWT <jwt>" — backend must strip prefix from token VALUE, not just header.
- 2026-03-30: Haiku for batch processing (~4x cheaper than Sonnet, sufficient for extraction/classification).
- 2026-03-31: dict[str, Any] DOES NOT WORK with LangChain structured output — LangChain/Anthropic set additionalProperties=false. Use list[ExtractedField] with explicit key/value pairs instead. (pydantic-ai #4117)
- 2026-03-31: Graph API Prefer: text header causes HTML-only emails to return empty body. Remove the preference, capture native format.
- 2026-03-31: VITE_API_BASE must be used everywhere the frontend calls the API — relative /api only works with local Vite proxy.

## Open Questions (deferred — not blocking demo)
- How does RingCentral data merge into the same pipeline? (Same pattern: RingCentral CLI + skills)
- How do we handle the bilingual aspect? (Classifier skill handles Spanish; draft generator needs Spanish templates)
- Business-line-specific requirements beyond GL? (Each LOB gets a config file following GL pattern, expand post-demo)
- Multi-tenancy for other brokers? (Add tenant_id to all collections if needed)
- Unisoft integration? (Depends on Jeremiah intro — not yet made)
- Email sending in production? (Requires Mail.Send permission, separate Entra consent from GIC)
