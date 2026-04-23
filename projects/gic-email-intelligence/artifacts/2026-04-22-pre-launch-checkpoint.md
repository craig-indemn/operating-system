---
ask: "Pre-launch checkpoint — full state of UAT shakeout, production readiness, what's left to do"
created: 2026-04-22
workstream: gic-email-intelligence
session: 2026-04-22a
sources:
  - type: codebase
    description: "14 code changes, proxy deployed, Railway dev+prod configured"
  - type: unisoft-uat
    description: "5 quotes created (17351-17355), 5 tasks (16863-16867)"
  - type: mongodb
    description: "51/253 emails processed, 10 automations run (5 success, 5 failed)"
  - type: google-doc
    ref: "https://docs.google.com/document/d/1Tb07Om95dllD9Fg4BqCWk0ny0b7GTaKPvYU3ndtsxJA"
    name: "JC call Apr 22"
---

# Pre-Launch Checkpoint — 2026-04-22 Evening

## Where We Are

UAT shakeout is running. Processing and automation services are live on Railway dev environment, working through 253 emails from Apr 21-22. Production Railway environment is deployed with kill switches on, ready to flip.

## UAT Shakeout Results (In Progress)

### Pipeline (extract → classify → link → enrich)
- **51 of 253 processed** (still running, ~20 per cron tick every 5 min)
- **0 pipeline failures** — every email processed successfully
- Classification breakdown: 13 agent_submission, 8 other, 6 portal, 6 agent_reply, 5 followup, 4 internal, 3 gic_app, 2 usli_pending, 2 report, 1 usli_quote, 1 usli_decline

### Automation (agent_submission → Unisoft AMS)
- **5 completed, 5 failed** out of 10 attempted (50% success rate in UAT)
- All 5 successes created Quote + Task + uploaded attachments + logged activity

#### Successful Automations (verify these in Unisoft UAT)
| Insured | Quote | Task | Group |
|---------|-------|------|-------|
| Coastal Craftsman Services LLC | 17351 | 16863 | NEW BIZ |
| Ixil Corp dba Casa Maya Grill | 17352 | 16864 | NEW BIZ |
| AG Construction Solution Service | 17353 | 16865 | NEW BIZ |
| SOLIDCLEAN SOLUTIONS LLC | 17354 | 16866 | NEW BIZ |
| Florida Air and Mechanical Contract | 17355 | 16867 | NEW BIZ |

#### Failed Automations (investigated — all legitimate)
| Insured | Root Cause | In Prod? |
|---------|-----------|----------|
| B and G Fiber | NavSav Tampa agency not in Unisoft (0 matches in 2,847 prod agents) | No — real gap |
| Evan Dubart Ellis | Concept Special Risks — UK agency, not registered | No — real gap |
| GALEANO ENTERPRISE | Palm Branches #7764 exists in prod but NOT in UAT. Prod/UAT mismatch from agent sync | **Yes — will work in prod** |
| Enmanuel Bermudez | Cornerstone Underwriting Partners not in Unisoft | No — real gap |
| Gold Crown Contractors | "Performance & Payment Bond" — not a Unisoft LOB. Surety bonds are a different product | N/A — correct refusal |

**Expected prod success rate:** Higher than 50%. Palm Branches will succeed (exists in prod). The 3 genuinely missing agencies are real gaps JC's team handles manually. The bond request is a correct refusal.

## Issues Found and Fixed This Session

### Bugs Fixed
1. **EXTRACTIONS import missing** (harness.py) — enrichment step was crashing, marking emails failed
2. **Field name mapping** (harness.py) — Gemini Pro returns capitalized field names (`Producer Name` vs `producer_name`). Added variants. Also fixed `producer_name` mapping to agency not agent.
3. **S3 credentials missing on Railway automation** — attachment uploads failing. AWS creds were never set on the automation service. **Fixed: added AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET to both dev and prod automation services.**
4. **Graph API credentials missing on Railway automation** — email move would fail. **Fixed: added GRAPH_* vars to both dev and prod automation services.**
5. **Linker recursion on already-linked emails** — defensive fix to skip linker if email already has submission_id
6. **Prod/UAT agent mismatch** — synced prod agents to MongoDB (2,847) but automation runs against UAT proxy. Agent #7764 found in MongoDB but doesn't exist in UAT. **This is a test-environment-only issue. In production, agents match the proxy.**

### Features Implemented
7. `--assigned-to` on quote create → sets underwriter to `indemnai`
8. Task due date = same day as email received (was next business day)
9. Prod GroupIds in skill (3=NEW BIZ, 4=NEW BIZ Workers Comp), created matching groups in UAT
10. All CLI defaults changed to `indemnai` (entered_by, logged_by)
11. Activity ActionId via environment variable (dev=6 audit only, prod=197 sends email to agent)
12. Attachment category routing (`--category application/email/loss-run/other`) — proxy updated and deployed to EC2
13. Email export as .eml (`gic emails export`)
14. Inbox folder management (`gic emails folders/create-folder/move`)
15. Move email on completion (`--move-to` flag on `gic emails complete`)
16. LangSmith tracing — explicit callback for deepagent, confirmed working
17. UI: automation failures visible in queue (red pill + error text + row highlight)
18. UI: renamed filters (Automation: Completed/Failed/Pending; Email type: Agent Submissions)

## Production Readiness

### Ready ✓
| Item | Status |
|------|--------|
| Prod proxy (EC2 :5001) | Healthy — 21 LOBs, DNS identity working |
| Prod task groups | GroupId 3 (NEW BIZ), GroupId 4 (NEW BIZ Workers Comp) confirmed |
| Prod agents synced | 2,847 agents in MongoDB (vs 1,571 from UAT) |
| "indemn processed" folder | Created in production inbox, move tested (round trip verified) |
| Railway prod environment | All services deployed with kill switches on |
| Railway prod env vars | Unisoft prod URL/key, ActionId 197, LangSmith, AWS, Graph API, Google SA, MongoDB — all set |
| Railway dev env vars | Fixed: added missing AWS + Graph API creds on automation service |
| LangSmith tracing | Working on both processing and automation projects |
| Code pushed | All changes committed and pushed to main |
| EC2 proxy updated | Category routing deployed, both UAT and prod services running |
| JC's user | `indemnai` (email: quotes@gicunderwriters.com) — confirmed working |
| Activity ActionId 197 | "Application Acknowledgement" found in prod activities |

### To Verify in Unisoft UAT (Craig doing now)
- [ ] Check Quotes 17351-17355 — correct insured, LOB, agent, AssignedTo
- [ ] Check Tasks 16863-16867 — correct group (NEW BIZ), due date (same day), entered by, subject
- [ ] Check attachments — PDFs in Documents > Application folder, .eml in General > Email folder
- [ ] Check activities — ActionId 6 logged on each quote

### To Do Before Go-Live (Apr 23 at 12:01 AM ET)

**Required:**
1. Verify UAT quotes/tasks in Unisoft desktop app (Craig doing now)
2. Wait for UAT batch to finish processing (199 emails remaining, ~45 min)
3. Review final UAT automation results — expect more successes as agent_submissions come through
4. ~~Test one email against prod Unisoft~~ — can do this by running one automation locally with prod proxy URL
5. Confirm Amplify UI deploy completed (filter changes)
6. Set date filter on prod automation start command so it only processes Apr 23+ emails

**Nice to have:**
7. Bump Railway processing batch limit for faster initial run
8. Test LangSmith traces appear in UI at smith.langchain.com

### To Do at Go-Live
1. Set `PAUSE_PROCESSING=false` on Railway production environment
2. Set `PAUSE_AUTOMATION=false` on Railway production environment
3. Monitor first cron ticks via `railway logs` and LangSmith
4. Monitor first few quotes in Unisoft prod via RDP
5. Be available for JC's team Thursday morning

## Environment Configuration Summary

### Railway Dev (running now — UAT shakeout)
| Var | Value |
|-----|-------|
| UNISOFT_PROXY_URL | http://54.83.28.79:5000 (UAT) |
| UNISOFT_API_KEY | 84208b3... (UAT) |
| UNISOFT_ACTIVITY_ACTION_ID | 6 (default — audit only) |
| PAUSE_PROCESSING | false (running) |
| PAUSE_AUTOMATION | false (running) |

### Railway Prod (deployed, paused — ready for go-live)
| Var | Value |
|-----|-------|
| UNISOFT_PROXY_URL | http://54.83.28.79:5001 (Prod) |
| UNISOFT_API_KEY | prod-84208b3... (Prod) |
| UNISOFT_ACTIVITY_ACTION_ID | 197 (Application Acknowledgement — sends email) |
| PAUSE_PROCESSING | true (waiting for go-live) |
| PAUSE_AUTOMATION | true (waiting for go-live) |

### Shared (same in both environments)
| Var | Where |
|-----|-------|
| MONGODB_URI | dev-indemn Atlas (all data on dev cluster) |
| GOOGLE_SA_JSON | Vertex AI SA for Gemini |
| GRAPH_* | Microsoft Graph API for quote@gicunderwriters.com |
| AWS_* | S3 for attachments |
| LANGCHAIN_* | LangSmith tracing |

## Monitoring in Production

1. **LangSmith** — https://smith.langchain.com
   - `gic-email-processing` — every extraction, classification, linking trace
   - `gic-email-automation` — every deepagent run with all CLI commands
2. **Railway logs** — `railway logs -s automation --environment production`
3. **MongoDB** — query automation_status, automation_result on emails collection
4. **gic.indemn.ai** — UI with Automation filter (Completed/Failed/Pending), Email type filter (Agent Submissions)
5. **Unisoft desktop** — RDP to EC2, check NEW BIZ task queue

## Key Files Changed (commit 9ea644f)

| File | What |
|------|------|
| harness.py | EXTRACTIONS import, field mapping, skip-if-linked guard |
| agent.py | LangSmith tracing callback, updated system prompt |
| create-quote-id.md | All JC requirements: assigned-to, due-date, categories, email upload, move, prod GroupIds |
| emails.py | export, folders, create-folder, move commands; --move-to on complete |
| graph_client.py | create_folder, move_message, list_child_folders |
| cli.py (unisoft) | --assigned-to, --due-date, --category, defaults→indemnai, env-driven ActionId |
| unisoft_client.py | category_id/subcategory_id params |
| UniProxy.cs | Parameterized category routing (deployed to EC2) |
| SubmissionQueue.tsx | Red failure pills, error text in rows, renamed filters |
| config.py | UNISOFT_ACTIVITY_ACTION_ID setting |
