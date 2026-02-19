---
ask: "Shake out the entire evaluations framework and Jarvis in the dev UI — investigate and fix failures reported by Dolly"
created: 2026-02-19
workstream: platform-development
session: 2026-02-19-c
sources:
  - type: github
    description: "indemn-ai/copilot-dashboard-react — Dockerfile + CI/CD workflows patched, commit 6cc1893"
  - type: web
    description: "agent-browser verification on devcopilot.indemn.ai — Jarvis baseline generation flow"
  - type: web
    description: "curl verification of evaluations API, platform-v2 API, and bot-context endpoints"
  - type: aws
    description: "CloudTrail + AWS Config — security group investigation for proxy.indemn.ai outage"
---

# Session 2026-02-19-c: Evaluations Fix + Infrastructure Debug

## What Happened

Continued from session 2026-02-19-b. Investigated bead `wem` (P0 — evaluations failing at baseline generation, Jarvis "not initialized" on dev). Also resolved an unrelated production outage on `proxy.indemn.ai` caused by an accidental security group change.

## Evaluations Investigation (wem)

### Findings

1. **Jarvis IS initialized** — the `jarvis-default` agent exists and responds. The "not initialized" report was misleading; Jarvis opens but immediately fails at the first tool call.

2. **Root cause: `EVALUATION_SERVICE_URL` missing from platform-v2 container `.env`**
   - The `BotContextConnector` (in `connectors/implementations/platform_api/evaluations.py`) reads `os.environ.get("EVALUATION_SERVICE_URL", "http://localhost:8002")`
   - Inside the Docker container, `localhost:8002` doesn't resolve — evaluations runs in a separate container
   - Both containers share the `shared-datadog` Docker network
   - The nginx proxy handles `/eval-api/` → `http://evaluations:8080` for browser requests, but Python backend connectors make direct HTTP calls

3. **Fix**: Added `EVALUATION_SERVICE_URL=http://evaluations:8080` to the `.env` on dev EC2, restarted container. Jarvis baseline generation now works — Bot Context tool succeeds in 257ms, subagents spawn and create rubrics/test sets.

4. **Secondary issue found**: Jarvis doesn't realize subagents already created rubric/test set, tries to create them again itself (bead `nlw` created).

### Evaluations Service Status

- **53 runs** in the database (7 unique bots), mostly from Jan 20 – Feb 9
- **7 test sets**, **23 rubrics** — all accessible via API
- **1 stuck run** from Feb 9 (status: "running", 0/40 completed, bot `68b807053275cf001319d30c`) — likely bot-service was unreachable at that time
- The evaluations service health endpoint responds correctly

### Env Var Discovery

The `.env` on dev EC2 had `INDEMN_EVALUATION_SERVICE_URL` (wrong name) instead of `EVALUATION_SERVICE_URL` (what the code reads). Both the name and the code should be aligned.

## Jarvis Avatar Fix (z7a)

### Root Cause

`VITE_FEDERATION_BASE_URL` was not set during the Docker build. Vite's `base` config (in `vite.federation.config.ts` line 49) defaults to `/`, so asset URLs like `/assets/Indemn_BubbleMark_Iris-Co-ii1Vm.png` resolve against the Angular host (`devcopilot.indemn.ai`) instead of the federation origin (`devplatform.indemn.ai`).

### Fix

- **Dockerfile**: Added `ARG VITE_FEDERATION_BASE_URL=/` + `ENV` before `npm run build:federation`
- **build.yml** (dev CI/CD): Added `build-args: VITE_FEDERATION_BASE_URL=https://devplatform.indemn.ai/`
- **build-prod.yml** (prod CI/CD): Added `build-args: VITE_FEDERATION_BASE_URL=https://platform.indemn.ai/`
- **Commit**: `6cc1893` on `indemn-ai/copilot-dashboard-react` main

## Infrastructure Incident: proxy.indemn.ai Outage

### Symptoms

`proxy.indemn.ai` returning 504 Gateway Timeout. EventGuard website (`www.eventguard.ai`) showing CORS errors (side effect of 504 with no headers).

### Root Cause

Accidental security group modification. AWS Config diff showed:
- **Deleted**: Inbound rule for TCP port 8000 from `172.31.0.0/16` on `sg-d4163da4`
- **Added**: `172.31.0.0/16` to an existing IP ranges list (SSH-related)

The deleted port 8000 rule was required for the ALB to reach the backend service. Without it, the ALB timed out → 504.

### Fix

Re-added the inbound rule: TCP port 8000, source `172.31.0.0/16` on security group `sg-d4163da4`. Services recovered immediately.

### Lesson

When modifying security group rules in the AWS Console, verify which rule is selected before editing — the UI can be confusing when multiple rules exist. The SSH rule modification inadvertently deleted the application port rule.

## Beads Status After Session

| Bead | Priority | Status | Resolution |
|------|----------|--------|------------|
| `wem` | P0 | **Closed** | EVALUATION_SERVICE_URL added to dev .env |
| `z7a` | P2 | **Closed** | VITE_FEDERATION_BASE_URL added to Dockerfile + CI/CD |
| `nlw` | P1 | Open | Jarvis duplicates rubric/test set creation after subagents |
| `5q2` | P2 | Open | Architecture discussion — repo structure + DB access |
