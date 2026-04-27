---
ask: "Save the handoff prompt as a copy-pasteable document so the next session can resume cleanly without context loss"
created: 2026-04-27
workstream: devops
session: 2026-04-27
sources:
  - type: artifact
    description: "Companion to projects/devops/artifacts/2026-04-27-saved-items-cli-shipping.md — the full session rollup. This file is just the prompt extracted for easy paste."
---

# Handoff prompt — paste at start of next session

Resume where we left off — we just committed the session checkpoint (commit `abc3afd` on `os-aws` branch). Active project: `devops`. Read `projects/devops/INDEX.md` and the 2026-04-27 artifact `projects/devops/artifacts/2026-04-27-saved-items-cli-shipping.md` — both have the full state. Before anything else, check Slack saved-for-later (saved.list API) and pull current PR states for indemn-cli #13 + form-extractor #17.

Priorities, in order:

A. **Triage Jonathan's Observatory bug (saved-item primary).** Parent thread `1777060307.862239` in #dev-squad (`C08AM1YQF9U`) — pull it for context first. Symptoms: Reception agent for Insurica, Volume tab "No data", Flow tab "No flow data", other tabs show 0 conversations despite the overview tab showing data. Likely a data-scope mismatch (bot_id vs project_id, or a filter excluding the agent type, or a date/timezone bug). Repo at `indemn-ai/Indemn-observatory` (capital I). Deployed to copilot-prod EC2 `i-0df529ca541a38f3d`. Reproduce in the UI before touching code. Read `projects/devops/artifacts/2026-03-03-observability-env-inventory.md` for the env reference.

B. **AI-369 (indemn-cli PR #13).** If Rudra or Jonathan approved and merged: `cd /Users/home/Repositories/indemn-cli && git fetch && git push origin main:prod` to trigger the npm publish workflow. Verify `npm view @indemn/cli version` shows 1.5.0. Then: Linear AI-369 → Done with publish timestamp comment, post a Slack reply in thread `1775717163.201049` tagging Jonathan (`<@U07U9TCVBS8>`) confirming the ship, and `saved.delete` on saved item ts `1776881443.001079`. If still open, nudge reviewers.

C. **form-extractor PR #17.** If Dolly re-approved: coordinate merge with Craig (the PR brings the new renderer service online — non-trivial deploy implications, don't merge unilaterally). If still open with no further notes, no action.

D. **Tuesday 8:30 AM ET calendar event** (`https://meet.google.com/dsy-okqw-fgc`) is a 15-min sync with Rem + Rudra + Dhruv on the JM manager-agent test process — Craig will attend; just be aware it's on the calendar.

Out of scope: saved item from 2026-04-27 13:27 UTC (Craig's own reply to Dhruv re GIC source code) — Craig is handling that side-channel.

Don't post anything to Slack without explicit approval. No preamble — give Craig the status in under 200 words and let him drive.
