---
ask: "Complete session handoff — everything built, discovered, and decided across sessions 2026-04-16 through 2026-04-17"
created: 2026-04-17
workstream: gic-email-intelligence
session: 2026-04-17a
sources:
  - type: codebase
    description: "9 commits pushed to craig-indemn/gic-email-intelligence main branch"
  - type: gmail
    description: "JC Apr 16 production unblock email, endorsement inbox thread"
  - type: unisoft-uat
    description: "Task creation, agent sync, smoke tests"
  - type: unisoft-prod
    description: "Dual proxy setup, endpoint discovery, task group discovery"
---

# Session Handoff — 2026-04-17

## Synopsis: Where We Are Right Now

The GIC Email Intelligence system processes emails from `quote@gicunderwriters.com`, extracts data from PDFs, classifies email types, and — for new business submissions — automatically creates Quote IDs in Unisoft AMS with tasks for GIC's underwriting team.

**What's built and working in UAT:**
- Full automation pipeline: email → extract → classify → link → create Quote → upload attachments → create Task → log activity → record completion
- Deepagent (Gemini 2.5 Pro via Vertex AI) follows an 8-step skill with fail-fast discipline
- Multi-field agency matching: phone (40%), name/fuzzy (30%), address (15%), email (15%) — finds agencies that name search alone misses
- 3-layer duplicate detection: submission-level check, cross-submission check, Unisoft's HasDuplicates flag
- Human-in-the-loop: tasks assigned to group queues (not individual users), team picks up from Unisoft task list
- ~4,500 emails processed, 163 AMS-linked, 60% automation rate on new applications

**What's built and ready for production:**
- Dual Unisoft proxy: UAT on port 5000, Prod on port 5001, same EC2
- Prod task groups discovered: NEW BIZ (#3), NEW BIZ Workers Comp (#4)
- Prod LOBs: 21 (vs 18 in UAT — prod has more)
- LLM costs shifted from Anthropic (depleted) to Gemini via Vertex AI (has credit)
- Dev Railway crons paused to prevent credit burn

**What has NOT been tested in production yet:**
- No email has been processed against the prod Unisoft
- No Quote or Task has been created in prod
- Agent data not synced from prod (prod agencies may differ from UAT)
- The automation skill still references UAT GroupIds (2) not prod GroupIds (3/4)

---

## Infrastructure Map

### EC2 Unisoft Proxy (`i-0dc2563c9bc92aa0e`)
| | UAT | Production |
|---|---|---|
| Port | 5000 | 5001 |
| Service | UniProxy | UniProxy-Prod |
| Config | `C:\unisoft\UniProxy.env` | `C:\unisoft\UniProxy-Prod.env` |
| SOAP URL | `ins-gic-service-uat-app.azurewebsites.net/imsservice.svc` | `services.gicunderwriters.co/management/imsservice.svc` |
| File URL | `services.uat.gicunderwriters.co/attachments/insfileservice.svc` | `services.gicunderwriters.co/attachments/insfileservice.svc` |
| ClientId | GIC_UAT | GIC |
| WS-Security | UniClient / (in machine env) | UniClient / (same password) |
| API Key | `84208b3...` | `prod-84208b3...` |
| Status | Running ✓ | Running ✓ |
| Security Group | `sg-04cc0ee7a09c15ffb` ports 5000+5001 open |

### Railway Services (dev environment)
| Service | Status | Key Env Vars |
|---------|--------|--------------|
| api | Running (Gemini) | `GOOGLE_SA_JSON`, `LLM_PROVIDER=google_vertexai` |
| automation | Paused (`PAUSE_AUTOMATION=true`) | Same + `UNISOFT_PROXY_URL=http://54.83.28.79:5000` (UAT) |
| processing | Paused (`PAUSE_PROCESSING=true`) | Same |
| sync | Running (cheap, Graph API only) | No LLM needed |

### MongoDB (`gic_email_intelligence` on dev-indemn Atlas)
| Collection | Records | Purpose |
|------------|---------|---------|
| emails | ~5,000 | Raw email data from Graph API |
| submissions | ~3,800 | Grouped applicant records |
| extractions | ~4,500 | PDF extraction results |
| unisoft_agents | 1,571 | Synced from UAT Unisoft (phone, address, name for matching) |

### LLM Provider
| Model | Use | Provider |
|-------|-----|----------|
| Gemini 2.5 Pro | Automation agent (deepagent) | Vertex AI via SA `prod-gemini-470505` |
| Gemini 2.5 Flash | Extraction, classification, linking | Vertex AI via same SA |
| Claude Sonnet | Not used (Anthropic credits depleted) | — |

### Unisoft UAT State (test data created this session)
| Entity | IDs | Purpose |
|--------|-----|---------|
| ActionId 40 | "Review automated submission" | Custom task action for automation |
| GroupId 2 | "Indemn Automation - New Biz" | Test group in UAT |
| TaskIds 16851-16855 | Various test tasks | Linked to test quotes |
| QuoteIds 17341-17344 | Test quotes (some duplicates) | Created during smoke testing |

---

## What We're Waiting On (External Blockers)

### From Mike Burke
- **Endorsement submission process rundown** — how endorsements work in Unisoft, step by step
- **List of no-brainer endorsement types** — high-volume, rule-based changes (address updates, adding vehicles, etc.)
- **Status:** JC asked Mike on Apr 13. No response yet as of Apr 17.
- **Impact:** Blocks endorsement automation (the NEXT domain after quotes). Doesn't block quotes going to production.

### From Makul Gupta / Grove Networks
- **Write access to quotes inbox** (`quote@gicunderwriters.com`) — needed for email-to-subfolder move ("INDM" folder for processed emails)
- **Status:** JC asked Makul on Apr 1. Mukul forwarded to Grove Networks. No response as of Apr 17.
- **Impact:** Blocks the "move processed emails to subfolder" feature. Doesn't block automation. Team still sees all emails in inbox until this is resolved.

### From Anthropic (optional)
- **Credit top-up** — Anthropic account is depleted. We migrated to Gemini, so this is only needed if we want to fall back to Claude.
- **Impact:** None for current work. Nice to have as fallback.

---

## What To Do Next (Production Cutover)

These steps should be done IN ORDER. Each step depends on the previous one.

### Step 1: Sync Prod Agents to MongoDB
**Why:** Prod Unisoft has different agencies than UAT. The 37 agencies that were "missing" in UAT may exist in prod. We need local phone/address data for matching.
**How:**
```bash
cd /Users/home/Repositories/gic-email-intelligence
UNISOFT_API_KEY=prod-84208b3173143d239773fd79c570c8bf4a4bc86b2f40605f53b05639d13524de \
  UNISOFT_PROXY_URL=http://54.83.28.79:5001 \
  PYTHONPATH=unisoft-proxy/client \
  .venv/bin/python unisoft-proxy/client/cli.py agents sync
```
**Expected:** ~1500-2000 agents synced (prod may have more than UAT's 1571). Takes ~15-30 min.
**Verify:** `mongosh ... --eval 'db.unisoft_agents.countDocuments({})'` should increase.
**Risk:** Low — read-only from Unisoft, write to our MongoDB.
**Note:** Consider whether to merge UAT+prod agents in the same collection or separate. Currently they'd overwrite each other by agent_number. If agent numbers differ between UAT and prod, we might want to tag them with an `environment` field. Decision: probably just overwrite — we only care about prod agents for prod automation.

### Step 2: Update Automation Skill for Prod
**Why:** The skill has UAT-specific GroupIds and references.
**What to change in `src/gic_email_intel/automation/skills/create-quote-id.md`:**
- Step 6 group routing table:
  - WC → GroupId **4** (NEW BIZ Workers Comp) — was "TBD"
  - All other LOBs → GroupId **3** (NEW BIZ) — was GroupId 2
- Step 8: `--entered-by` should use `indemnai` for prod (not `ccerto`)
**How:** Edit the skill file, commit, push.
**Risk:** Low — skill is text, easily reversible.

### Step 3: Update Railway Env for Prod Proxy
**Why:** Railway automation service currently points at UAT proxy (port 5000). Needs to point at prod (port 5001).
**What to change:**
```bash
railway service automation
railway variables --set "UNISOFT_PROXY_URL=http://54.83.28.79:5001"
railway variables --set "UNISOFT_API_KEY=prod-84208b3173143d239773fd79c570c8bf4a4bc86b2f40605f53b05639d13524de"
```
**Also consider:** Whether to change the `entered-by` default in the task CLI to `indemnai`.
**Risk:** Medium — this makes the cron create real data in prod Unisoft when unpaused. Do this BEFORE testing, keep cron paused until after Step 5.

### Step 4: Deploy Latest Code to Railway
**Why:** Code changes from this session (task creation, Gemini, agency matching, duplicate detection, prod proxy support) need to be on Railway.
**How:** `railway up -s automation --environment development -d --ci`
**Risk:** Low — code is tested. Cron is paused so no automatic processing.

### Step 5: Manual Smoke Test Against Prod
**Why:** First-ever prod automation run. Must be watched closely.
**How:**
1. Reset a known email: `gic emails reset <email_id>`
2. Run locally with prod proxy: 
   ```bash
   UNISOFT_PROXY_URL=http://54.83.28.79:5001 \
   UNISOFT_API_KEY=prod-... \
   gic automate run -t agent_submission --max 1 --verbose
   ```
3. Watch the agent:
   - Does it find the agency via `agents match`? (Prod agencies may match differently)
   - Does it create a Quote in prod Unisoft?
   - Does it create a Task in the right group (NEW BIZ #3 or Workers Comp #4)?
   - Does HasDuplicates fire? (Prod may already have this applicant from manual entry)
4. Check in Unisoft desktop app: does the task appear in the NEW BIZ queue?
**Verify with JC:** After creating one test Quote+Task, ask JC to confirm he sees it in the task queue.
**Risk:** MEDIUM — creates real data in prod. But JC said "UAT is safe" and approved production. The task goes to the group queue, the team reviews before acting.

### Step 6: Unpause Railway Automation Cron (Controlled)
**Why:** Let the system process emails automatically.
**How:** 
```bash
railway service automation
railway variables --set "PAUSE_AUTOMATION=false"
```
**But first:** Consider setting `--max 5` or similar throttle so the first batch is small. The automate CLI already has `--max` (default 50) which is controlled by the Railway start command.
**Monitor:** Watch the first few cron ticks via `railway logs -s automation`. Check MongoDB for new `automation_status=completed` records. Check Unisoft for new tasks.
**Risk:** HIGH if something is wrong — could create many incorrect Quotes/Tasks in prod. Mitigations: start with max=1, watch first run, increase gradually.

### Step 7: Unpause Processing Cron (Optional)
**Why:** New emails arriving in the inbox need extraction+classification before automation can process them.
**Decision:** Only unpause if you want ongoing automated processing. Otherwise, keep paused and process new emails on-demand.
**How:**
```bash
railway service processing
railway variables --set "PAUSE_PROCESSING=false"
```

---

## Things That Don't Block Prod Cutover (Parallel Work)

### Endorsements Inbox
- Read access to `endorsements@gicunderwriters.com` was granted by JC/Mukul on Apr 1
- Craig confirmed access on Apr 1 with TJ at Grove Networks
- Next: connect the sync pipeline to the endorsements inbox, begin ingesting to understand volume and content
- Blocked on Mike Burke's endorsement process rundown + no-brainer list
- This is a SEPARATE project from quotes — different email types, different automation rules

### Inbox Subfolder Move
- JC wants processed emails moved from inbox to "INDM" subfolder
- Requires write access to the quotes inbox (waiting on Makul/Grove)
- Once write access granted: use Graph API `Move` action on processed emails
- Not part of the automation pipeline — it's a cleanup step

### USLI Offer-to-Agent
- JC flagged as a "quick win" from the Apr 13 meeting
- USLI development paused overall (portal changing end of month)
- But offer-to-agent is a specific, small task that could be done
- Low priority vs. getting quotes to production

### Anthropic Fallback
- If Gemini proves unreliable for the deepagent, we can fall back to Claude
- Requires topping up Anthropic credits
- The code supports both providers via `LLM_PROVIDER` env var
- Currently: `google_vertexai` everywhere

---

## Commits This Session (9 commits, all pushed to origin/main)

| # | Commit | What |
|---|--------|------|
| 1 | `4b8a708` | Task creation CLI + skill + emails complete --task-id |
| 2 | `0ae581d` | Gemini migration + skill inlining fix |
| 3 | `541b908` | Proxy UniProxy.cs source in repo + deploy README |
| 4 | `6d86560` | Pause kill switches for dev crons |
| 5 | `4c55a4f` | Phase 2: multi-field agency matching |
| 6 | `832a66c` | Fix null Quote response CLI bug |
| 7 | `34cc013` | Check ReplyStatus before accessing response data |
| 8 | `740a8e5` | Phase 3: 3-layer duplicate detection |
| 9 | `a9536b5` | Dual proxy with comprehensive documentation |

---

## Key Technical Lessons (Reference for Next Time)

### 1. WCF DNS Identity for Production
The prod Unisoft SOAP endpoint at `services.gicunderwriters.co` requires `EndpointIdentity.CreateDnsIdentity("gicunderwriters.co")` on the WCF endpoint address. Without it, `MessageSecurityException` at `SecuritySessionSecurityTokenProvider.GetTokenCore` — WCF cannot establish the secure conversation session. This is NOT a TLS cert issue (skip_cert_validation doesn't help) and NOT a credential issue (UniClient + password are correct). It's a WCF message-layer requirement for the security context token negotiation. The proxy auto-detects `gicunderwriters.co` in the URL and adds the identity.

### 2. WS-Security Credentials
`UniClient` with the same password works for both UAT and prod. These are NOT the desktop app login credentials (ccerto/GIC2026$$! for UAT, indemnai/GIC2000undw! for prod). They're a shared WCF service account. The password is stored in AWS Machine env on EC2: `[Environment]::GetEnvironmentVariable("UNISOFT_WS_PASS", "Machine")`.

### 3. Dual Proxy Service Name Routing
Both services run the same compiled code but as differently-named exes (`UniProxy.exe` vs `UniProxy-Prod.exe`). ServiceName = exe filename (without extension). At startup, `OnStart` reads `C:\unisoft\{ServiceName}.env`. If both exes have the same name, both read the same config → port conflict → crash.

### 4. Port Requirements
Each port needs: (a) URL ACL reservation: `netsh http add urlacl url=http://+:{PORT}/ user=Everyone`, (b) Windows Firewall rule, (c) AWS Security Group inbound TCP rule. Missing any of these → `HttpListenerException` or connection timeout.

### 5. Discovering Prod SOAP URLs
The URL JC sent (`ins-gic-client-prod-app.azurewebsites.net/publish.htm`) is the ClickOnce APP download, not the API endpoint. The actual SOAP URL is inside the app's exe.config. Download it WITHOUT installing the app:
```powershell
$base = "https://ins-gic-client-prod-app.azurewebsites.net/"
# Get version from deployment manifest
[xml]$m = Get-Content (Invoke-WebRequest "${base}Unisoft.Insurance.BackOffice.GIC.application" -OutFile m.xml -PassThru).FullName
$folder = [IO.Path]::GetDirectoryName($m.assembly.dependency.dependentAssembly.codebase) -replace "\\","/"
# Download config
Invoke-WebRequest "$base$($folder -replace ' ','%20')/Unisoft.Insurance.BackOffice.GIC.exe.config.deploy" -OutFile app.config
Select-String app.config -Pattern "endpoint address"
```

### 6. Gemini Skill Inlining
The deepagents SDK `skills=` parameter expects a directory-per-skill layout with `SKILL.md`. Our flat-file never loaded. Claude inferred the workflow from the system prompt alone; Gemini didn't. Fix: inline the skill content directly in the system prompt via `_build_system_prompt()`. This is the reliable path for any non-Claude model.

### 7. Unisoft Subject Max Length
Task and Quote subjects are silently truncated at 50 characters. The CLI auto-truncates with ellipsis. Important metadata (LOB, AgentNo, QuoteId) lives in the task association fields, not the subject.

### 8. Proxy Nested DTO Serialization
`AppendDtoField` in the proxy was hardcoded to emit nested sub-DTOs as nil. Fixed to recursively serialize with the parent's `b:` namespace prefix and alphabetical field ordering. This unlocked TaskAssociation inside Task (and may fix other nested DTOs we haven't tried yet). All registered DTOs are in `dtoNamespaces` dict — add new entries when needed.

---

## Key Files Quick Reference

| Need to... | File |
|------------|------|
| Resume this project | This handoff |
| See all decisions | `INDEX.md` Decisions section |
| Modify the pipeline | `src/gic_email_intel/agent/harness.py` |
| Modify the automation agent | `src/gic_email_intel/automation/agent.py` |
| Modify the automation skill | `src/gic_email_intel/automation/skills/create-quote-id.md` |
| Modify the Unisoft CLI | `unisoft-proxy/client/cli.py` |
| Modify the proxy | `unisoft-proxy/server/UniProxy.cs` → deploy to EC2 via SSM |
| Set up proxy from scratch | `unisoft-proxy/server/README.md` (9-step guide) |
| Read Unisoft API spec | `research/unisoft-api/wsdl-complete.md` |
| Check agency matching | `unisoft agents match` CLI command |
| Check duplicate detection | `gic submissions check-duplicate` CLI command |
| See prod task groups | Above (NEW BIZ #3, Workers Comp #4) |

## Environment Setup (for a new session)

```bash
# GIC repo
cd /Users/home/Repositories/gic-email-intelligence

# Local .env has: MONGODB_URI, LLM_PROVIDER=google_vertexai, LLM_MODEL=gemini-2.5-pro,
# GOOGLE_APPLICATION_CREDENTIALS pointing at .gcp-sa.json

# Unisoft CLI (UAT)
UNISOFT_API_KEY=84208b3173143d239773fd79c570c8bf4a4bc86b2f40605f53b05639d13524de \
  PYTHONPATH=unisoft-proxy/client \
  .venv/bin/python unisoft-proxy/client/cli.py {command}

# Unisoft CLI (PROD)
UNISOFT_API_KEY=prod-84208b3173143d239773fd79c570c8bf4a4bc86b2f40605f53b05639d13524de \
  UNISOFT_PROXY_URL=http://54.83.28.79:5001 \
  PYTHONPATH=unisoft-proxy/client \
  .venv/bin/python unisoft-proxy/client/cli.py {command}

# Run automation (UAT)
.venv/bin/gic automate run -t agent_submission --max 1 --verbose

# MongoDB
mongosh "mongodb+srv://dev-indemn:wJnKmz4P0q39GpXZ@dev-indemn.mifra5.mongodb.net/gic_email_intelligence"
```
