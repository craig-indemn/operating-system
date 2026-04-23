---
ask: "Go-live day handoff — everything needed to continue monitoring and improving"
created: 2026-04-23
workstream: gic-email-intelligence
session: 2026-04-23a
sources:
  - type: codebase
    description: "Multiple fixes deployed during go-live morning"
  - type: unisoft-prod
    description: "3 quotes created: 146250, 146251, 146253"
  - type: langsmith
    description: "Root cause analysis on extraction and linker failures"
---

# Go-Live Day Handoff — 2026-04-23

## Status: PRODUCTION IS LIVE AND RUNNING

As of 1:35 PM ET, the system is processing emails end-to-end in production. 15 emails received today, all processed, 0 failures, 2 agent submissions automated into prod Unisoft.

## Production Results So Far

| Insured | Quote | Task | LOB |
|---------|-------|------|-----|
| Mey Enterprise, LLC | 146250 | 135249 | GL/Liquor Liability |
| Mey Enterprise, LLC | 146251 | 135250 | Commercial Property (2nd LOB) |
| Stucco Finesse LLC | 146253 | 135251 | GL/Artisans |

## Issues Found and Fixed During Go-Live Morning

### 1. Google Cloud SA JSON truncated on Railway prod
- **Symptom:** All 6 initial emails failed with "Unable to load PEM file"
- **Root cause:** Private key was truncated (1091 chars vs 1958) when set via CLI. Special characters in the JSON got mangled.
- **Fix:** Extracted exact value from dev environment via Python SDK, re-set on prod processing + automation services.

### 2. Extraction fails on multi-PDF emails (MALFORMED_FUNCTION_CALL)
- **Symptom:** MEY ENTERPRISE (5 PDFs, 712 KB) returned None from Gemini structured output
- **Root cause from LangSmith:** `finish_reason: MALFORMED_FUNCTION_CALL`, 0 completion tokens, 20K input tokens. Gemini Flash can't produce valid structured output for large multi-document extractions.
- **Fix:** Switched extraction model from `gemini-2.5-flash` to `gemini-2.5-pro`. Also added None guard so crash doesn't propagate.
- **Follow-up:** Per-PDF processing (instead of batching all PDFs in one prompt) would allow Flash to work. Deferred.

### 3. Automation service running uvicorn instead of automation command
- **Symptom:** Automation never picked up completed emails. Logs showed MongoDB change stream timeouts.
- **Root cause:** Prod automation `startCommand` was `null`. Dockerfile default CMD is `uvicorn` (API server). Service was running the API server on a cron schedule instead of `gic automate run`.
- **Fix:** Set `startCommand: "gic automate run -t agent_submission"` via Railway GraphQL API.

### 4. Automation service can't connect to MongoDB Atlas
- **Symptom:** Automation crashes with ServerSelectionTimeoutError every cron tick
- **Root cause:** Automation service on prod Railway didn't have static outbound IP enabled. Atlas allowlist only has Railway's static IP. Processing/sync had static IP enabled but automation didn't.
- **Fix:** Craig enabled static IP in Railway dashboard for automation prod.

### 5. Linker ReAct agent loops and crashes (recursion limit)
- **Symptom:** Multiple emails fail with "Recursion limit of 15 reached"
- **Root cause from LangSmith:** Linker creates submission, links email, then loops — creates another submission, re-links. No explicit stop condition in the skill prompt. LLM non-deterministically fails to stop.
- **Fixes applied:**
  - Added "you are DONE" completion instruction to linker skill prompt
  - Added code-level resilience: if linker crashes but `submission_id` IS set, continue pipeline instead of failing
- **Result:** Linker may still loop internally, but the pipeline recovers and completes.

### 6. Submissions stuck at stage "new" (invisible in UI)
- **Symptom:** Successfully automated submissions don't appear in the board
- **Root cause:** The board API only queries stages: received, triaging, etc. Stage "new" is not included. Linker crash prevents stage update from "new" to "received".
- **Fix:** Manually updated stuck submissions. The linker resilience fix (issue 5) prevents this going forward — pipeline continues to enrichment and completion even if linker crashes.
- **Follow-up needed:** Set default stage to "received" instead of "new" when creating submissions, so they're always visible.

### 7. Classification: quote@gicunderwriters.com portal emails (from yesterday's session)
- Hard rule added: `quote@gicunderwriters.com` + "Application Request" in subject → `gic_application` (not `agent_submission`). These are GIC portal notifications that already have Quote IDs.

## Current Infrastructure State

### Railway Production
| Service | Status | Start Command | Cron |
|---------|--------|---------------|------|
| sync | Running | `outlook-inbox sync` | continuous |
| processing | Running | `outlook-agent process --batch` | */5 * * * * |
| automation | Running | `gic automate run -t agent_submission` | */5 * * * * |
| api | Running | uvicorn (serves board API) | continuous |

### Key Env Vars (prod)
- `UNISOFT_PROXY_URL=http://54.83.28.79:5001`
- `UNISOFT_TASK_ACTION_ID=70` (Review automated submission)
- `UNISOFT_ACTIVITY_ACTION_ID=197` (Application Acknowledgement)
- `PROCESSING_START_DATE=2026-04-23`
- `LANGCHAIN_TRACING_V2=true` + `LANGCHAIN_PROJECT=gic-email-automation` / `gic-email-processing`
- Static IP enabled on ALL prod services

### Monitoring
- **gic.indemn.ai** — Period: Today, Email type: Agent Submissions
- **LangSmith** — smith.langchain.com, projects gic-email-processing and gic-email-automation
- **Unisoft prod** — RDP to EC2, check NEW BIZ task queue
- **Railway logs** — `railway logs -s processing --environment production` / `-s automation`

### Pause Commands
```bash
cd /Users/home/Repositories/gic-email-intelligence
railway variables --environment production -s processing --set "PAUSE_PROCESSING=true"
railway variables --environment production -s automation --set "PAUSE_AUTOMATION=true"
```

## Known Issues (Non-Blocking)

1. **Linker still loops sometimes** — the prompt fix + code resilience handles it, but the linker wastes LLM tokens looping. Proper fix: make linking deterministic (not LLM-driven) for the common case.
2. **Denormalization gaps** — automation results on emails don't always sync to submissions. May need to run manual sync periodically or fix the denormalization in `gic emails complete`.
3. **Stage "new" submissions** — any submission created by a crashed linker needs stage set to "received". The code fix should prevent new ones, but monitor.
4. **UI domain** — `gic.indemn.ai` domain switch to prod branch may still be propagating. Both branches use same MongoDB so data is the same.

## Files Changed Today (commits on main + prod branches)

| Commit | Change |
|--------|--------|
| `75c923d` | Extractor: handle None result from Gemini, switch to Pro |
| `c95d685` | Extraction model: Flash → Pro |
| `f30cd18` | Linker skill: explicit stop condition |
| `b1f7ce6` | Linker resilience: continue pipeline if link succeeded despite crash |

## To Resume Next Session

1. Read this artifact for current state
2. Read `artifacts/2026-04-22-session-close-go-live.md` for full infrastructure context
3. Check `gic.indemn.ai` for current email/automation status
4. Check MongoDB: `mongosh "mongodb+srv://dev-indemn:wJnKmz4P0q39GpXZ@dev-indemn.mifra5.mongodb.net/gic_email_intelligence" --eval 'db.emails.countDocuments({received_at:{$gte:ISODate("2026-04-23T00:00:00Z")}})'`
5. Continue monitoring and improving
