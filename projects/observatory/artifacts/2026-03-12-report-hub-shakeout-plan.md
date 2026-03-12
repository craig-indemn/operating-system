---
ask: "End-to-end shakeout plan for the Report Hub — test every user flow via agent-browser and fix bugs"
created: 2026-03-12
workstream: observatory
session: 2026-03-12-b
sources:
  - type: github
    description: "PR #38 code review findings, design doc requirements"
---

# Report Hub E2E Shakeout Plan

## Prerequisites

1. Start analytics services: `local-dev-aws.sh start analytics --env=dev`
2. Verify backend healthy: `curl http://localhost:8004/health`
3. Verify frontend serving: `curl -s http://localhost:5175 | head -5`
4. Generate a dev JWT for browser auth:
   ```bash
   JWT_SECRET=$(grep "^JWT_SECRET=" /Users/home/Repositories/.env.dev | cut -d= -f2)
   cd /Users/home/Repositories/indemn-observability && ./venv/bin/python3.12 -c "
   import jwt
   token = jwt.encode({'_id': 'dev-test-user', 'email': 'support@indemn.ai', 'sub': 'support@indemn.ai'}, '$JWT_SECRET', algorithm='HS256')
   print(token)
   "
   ```
5. Inject token into browser: `agent-browser eval "localStorage.setItem('token', '<TOKEN>'); location.reload()"`

## Test Matrix

### Test 1: Reports Tab Loads (Platform Scope)

**Steps:**
1. Navigate to `http://localhost:5175/reports`
2. Snapshot interactive elements
3. Verify all 5 report type cards visible:
   - Voice Daily Report (Agent-level)
   - Distinguished Programs Internal Agent Report (Agent-level)
   - Monthly Customer Insights (Customer-level)
   - Customer Analytics (Customer-level)
   - Outlook Integration Guide (Customer-level)
4. Verify Generated Reports table is present

**Expected:** All 5 cards render. Table shows previously generated reports.

### Test 2: Org Scope Filtering

**Steps:**
1. Select "EventGuard" in the sidebar
2. Snapshot Reports tab
3. Verify: customer-level reports (insights, analytics, onboarding) visible
4. Verify: agent-level reports (voice-daily, distinguished-internal) hidden or visible based on org_ids config
5. Select "Dev-Dhruv" in the sidebar
6. Verify: voice-daily card visible (org_ids includes Dev-Dhruv's dev ID)

**Expected:** Report type cards filter correctly based on selected org.

### Test 3: Generate Customer Insights Report

**Steps:**
1. Select "EventGuard" in sidebar
2. Click "Generate" on Monthly Customer Insights card
3. Verify GeneratePanel appears with:
   - Date range picker (date_from, date_to)
   - NO agent dropdown (customer-scope report)
   - Org selector (should auto-select EventGuard)
4. Set date range: 2025-01-01 to 2026-03-12
5. Click "Generate Report"
6. Wait for loading to complete
7. Verify: toast success message
8. Verify: new row appears in Generated Reports table

**Expected:** Report generates, toast shown, table updated.

### Test 4: Generate Agent-Level Report (Voice Daily)

**Steps:**
1. Select "Dev-Dhruv" in sidebar
2. Click "Generate" on Voice Daily Report card
3. Verify GeneratePanel has:
   - Date range picker
   - Agent dropdown (should show agents from agent_ids list)
4. Select an agent from dropdown
5. Set date range: 2026-03-05 to 2026-03-12
6. Click "Generate Report"
7. Wait for completion

**Expected:** Agent dropdown shows filtered agents. Report generates successfully.

### Test 5: Download Report (THE KNOWN BUG)

**Steps:**
1. Find a generated report in the table
2. Click the download button
3. Monitor: what happens? Does a new tab open? Does download start? Any errors?
4. Check browser console for errors: `agent-browser eval "window.__getErrors ? window.__getErrors() : 'no listener'"`
5. Check network tab: did the download endpoint return a presigned URL?
6. Try manual download via curl:
   ```bash
   curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8004/api/reports/{id}/download
   ```

**Expected:** Clicking download should call `/api/reports/{id}/download`, get a presigned S3 URL, and open it in a new tab. This is the known bug — investigate and fix.

**Likely issues to check:**
- Is the download button calling the right API method?
- Is the presigned URL being opened correctly (window.open vs anchor download)?
- Is the S3 URL valid? Does it have correct credentials?
- Is CORS blocking the S3 download?
- Is the report_id being passed correctly (MongoDB ObjectId format)?

### Test 6: Generate Onboarding Guide (No Dates Required)

**Steps:**
1. Select any org in sidebar
2. Click "Generate" on Outlook Integration Guide card
3. Check: does the panel show date pickers? (The onboarding guide has empty `parameters: {}` — no dates required)
4. Click "Generate Report"

**Expected:** May need special handling for reports with no date parameters. Check if the frontend handles empty parameters correctly. The extractor ignores dates, so any dates should work, but the UX should ideally not require dates for this report type.

### Test 7: Error Handling — Empty Date Range

**Steps:**
1. Try generating a report with a very narrow date range that has no data
2. Verify: error message shown via toast (not a stack trace)
3. Verify: UI returns to a usable state (not stuck in loading)

**Expected:** "Data extraction failed" error shown in toast. No internal details leaked.

### Test 8: Error Handling — Invalid Agent for Org

**Steps:**
1. Via curl, try generating a report with an agent_id that doesn't belong to the org:
   ```bash
   curl -X POST http://localhost:8004/api/reports/generate \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"report_type":"voice-daily","org_id":"676be5a7ab56400012077e7d","agent_id":"FAKE_AGENT_ID","date_from":"2026-03-01","date_to":"2026-03-12"}'
   ```
2. Verify: 403 response with "Agent not found in this organization"

**Expected:** Agent-org validation blocks the request.

### Test 9: Reports Table Pagination and Sorting

**Steps:**
1. At platform scope, verify reports table shows all orgs' reports
2. Select a specific org — verify table filters
3. Check if table is sorted by date (newest first)

**Expected:** Filtering and sorting work correctly.

### Test 10: ReportButton Export (Overview Tab)

**Steps:**
1. Navigate to Overview tab
2. Click the Export button
3. Verify: only CSV and JSON options (no PDF options)
4. Test CSV export
5. Test JSON export

**Expected:** Old PDF menu items removed. CSV/JSON still work.

## Bug Fix Workflow

For each bug found:
1. Identify root cause (frontend vs backend vs S3 config)
2. Fix in the `feature/report-hub` branch
3. Test the fix locally
4. Commit with descriptive message
5. Push to `indemn` remote
6. Verify CI still passes

## After Shakeout

1. Commit any fixes
2. Merge PR #38
3. Verify deploy to dev via `https://devobservatory.indemn.ai/reports`
4. Update INDEX.md with final status
