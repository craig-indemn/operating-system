# Session Handoff: voice-evaluations 2026-02-27-e

## What Was Done This Session

Continued testing and verification after sessions c (implementation) and d (code review + bug fixes).

### Bug Fix Commits (COMPLETE)
Committed all previously-uncommitted bug fixes from session d across 3 repos:
- **indemn-observability** (`1a54bab`): aggregations.py (3 bugs), langfuse.py (duplicate class)
- **evaluations** (`1eddab9`): evaluations.py (400 validation), transcript_evaluation.py (TODO)
- **operating-system** (`b0204c4`): query-patterns.md (field names), SKILL.md (filter syntax)

### Transcript Evaluation (COMPLETE — PASS)
Triggered a transcript evaluation via API against real Wedding Bot web conversations:
- **Run ID**: `e086e698-8f65-4686-9980-d3b880289c90`
- **Bot**: Wedding Bot (`676be5cbab56400012077f4a`)
- **Conversations**: 2 (29-message and 24-message web conversations)
- **Results**: 76/102 criteria passed (75%), 12/12 rubric rules passed (100%)
- **Endpoint**: `POST /api/v1/evaluations` with `mode: "transcript"` and `conversation_ids`

### Federation Build Browser Testing (COMPLETE — partial)
Built and served the federation bundle, tested in copilot-dashboard (port 4500).

**Verified (PASS):**
- Federation build loads React components inside Angular copilot-dashboard
- Wedding Bot detail page shows evaluation scores (Criteria: 75%, Rubric: 100%)
- **"Transcript Criteria" stat card** renders correctly (75%, 76/102 passed) — this is the new stat card from the voice evaluations implementation
- Common Failures table displays with CRITERIA type badges
- V1 Agent badge renders correctly
- Evaluation run detail page accessible via `/organization/:orgId/ai-studio/bot/:botId/configurations?tab=overview&runId=:runId`

**Not Verified (scroll/navigation limitations):**
- Individual transcript badge on test result cards (couldn't scroll past Common Failures in fullscreen modal)
- "View Conversation" button on transcript results
- "Historical conversation" label instead of persona

**Finding: V1 bots not in evaluations overview** — The evaluations overview page (`/ai-studio/evaluations`) only lists V2 platform agents. V1 bots (like Wedding Bot) don't appear there, but their evaluation results ARE accessible via the bot detail page. This is pre-existing behavior, not a regression.

## What's Blocked

1. **Langfuse credentials** — still waiting on Jonathan. Blocks:
   - Voice conversation ingestion into Observatory (need Langfuse traces)
   - `_fetch_langfuse_tool_calls()` enrichment in transcript engine
   - Langfuse connector verification in Observatory
   - Voice channel badge visual verification
   - voice-livekit trace metadata verification

## What Needs Doing Next

### When Langfuse Credentials Arrive
1. Add `LANGFUSE_HOST`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` to `.env`
2. Run Langfuse skill status check:
   ```bash
   source .env && curl -s -o /dev/null -w "%{http_code}" \
     -u "$LANGFUSE_PUBLIC_KEY:$LANGFUSE_SECRET_KEY" \
     "$LANGFUSE_HOST/api/public/traces?limit=1"
   ```
3. Verify `_fetch_langfuse_tool_calls()` returns real tool data for a voice conversation
4. Modify `run_ingestion_task()` in Observatory to allow voice conversations through without Langsmith traces (pass empty traces for `attributes.channel == "VOICE"`)
5. Fix `derive_customer_id()` to fall back to `mongodb_doc["id_organization"]` (voice docs have org at root level, not in `snapshot.agents`)
6. Trigger Observatory ingestion for voice conversations
7. Run transcript evaluation on voice conversations
8. Re-run all browser tests:
   - Voice channel badge in Observatory
   - Transcript badge on individual result cards
   - View Conversation button
   - "Historical conversation" label

### After All Testing Complete
9. Push branches and create PRs across repos
10. Deploy to dev/staging
11. Update design document with "Implementation Status: Complete"

## Key Technical Notes

### Observatory Ingestion Gap
The Observatory ingestion pipeline (`run_ingestion_task()` in `tasks.py:348-350`) skips conversations without Langsmith traces. Voice conversations use Langfuse, not Langsmith. Two changes needed when unblocked:
1. `tasks.py`: Allow voice conversations (`attributes.channel == "VOICE"`) through without traces
2. `derivations.py`: Add `mongodb_doc.get("id_organization")` fallback in `derive_customer_id()` (voice docs have org at root, not in snapshot.agents)

### Voice Data in Dev MongoDB
- 742 voice conversations in `tiledesk.requests` with `attributes.channel: "VOICE"`
- Main org: `6613cbc6658ad379b7d516c9` (638 conversations, 21 bots)
- Date range: 2025-08-04 to 2026-02-20
- Observatory has only 4 conversations ingested (all web)

### Federation Testing
- Must kill Vite dev server (:5173) and serve federation build instead
- Build: `cd indemn-platform-v2/ui && npm run build:federation`
- Serve: `npx serve dist-federation -l 5173 --cors -n`
- Then hard refresh Angular app (Cmd+Shift+R)

## Services State
All 15 services running. Federation build serving on :5173 (not dev server).
Stop with `/opt/homebrew/bin/bash /Users/home/Repositories/local-dev.sh stop all`.

## Screenshots
Browser test screenshots in `projects/voice-evaluations/artifacts/`:
- `eval-page.png` — Evaluations overview in copilot-dashboard
- `eval-eventguard.png` — EventGuard org evaluations
- `eval-bot-detail.png` — Wedding Bot detail with evaluation scores
- `eval-fullscreen.png` — Evaluation run detail with Transcript Criteria stat card
- `eval-run-results.png` — Run results showing 75% criteria, 100% rubric
