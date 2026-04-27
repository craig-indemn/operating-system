---
ask: "Continue working through Craig's Slack Saved-for-Later queue from the 2026-04-23 + 2026-04-24 unblock sessions. Ship the items that became implementable. Record full state for handoff to next session (Observatory triage is the next big one)."
created: 2026-04-27
workstream: devops
session: 2026-04-27
sources:
  - type: slack
    description: "saved.list API on Indemn workspace; archived 5 items via saved.delete; posted 4 thread replies in #dev-squad and 1 DM to Dolly"
  - type: github
    description: "indemn-cli PRs #11 (banner, merged + published 1.4.0) and #13 (functions configurationSchema, in review). form-extractor PR #17 (renderer style alignment, pushed to existing branch). 2 commits added to existing intake-manager work via earlier sessions"
  - type: linear
    description: "Created AI-367 (parent), AI-368 (banner sub), AI-369 (functions). AI-368 → Done. AI-367 → In Progress."
  - type: aws
    description: "SSM read+modify on dev-services i-0fde0af9d216e9182 (manual deploy of form-extractor container, read-only inspections elsewhere)"
  - type: google-calendar
    description: "Created 15-min sync invite for Tue 2026-04-28 8:30 AM ET (Craig + Rem + Rudra + Dhruv)"
---

# 2026-04-27 — Saved-items triage + indemn-cli shipping + form-extractor renderer style

This session picked up where 2026-04-23 (saved-triage) and 2026-04-24 (multi-day-unblock) left off. Several items that were "blocked on PR review" or "blocked on design questions" became implementable; shipped them. New items appeared in the queue and got triaged.

---

## State of the Slack Saved-for-Later queue

**Started this session:** 8 items (per 2026-04-24 multi-day artifact §8 + 2 new since)
**Ended this session:** 4 items (3 active needing attention + 1 long-archived file)

### Archived this session (with the action that justified archiving)

| # | When saved | Item | What happened |
|---|---|---|---|
| 1 | 2026-04-24 | Rudra DM: set `JOSHU_MAX_RECORD_ATTEMPTS=1` | Already done in 2026-04-24 session §7 Phase 6. Verified, archived. |
| 2 | 2026-04-24 | Dolly DM: form-extractor "no runner" on a deploy run | Merged form-extractor PR #27 (broken deploy job removal); manually deployed `indemneng/doc-extractor:main` to dev-services to ship Dolly's python-dotenv 1.2.2 + Rudra's 2026-04-21 security patches. Replied to Dolly. |
| 3 | 2026-04-23 | Rem rollup in #customer-implementation; ask was "sync on manager-agent test process" | Booked 15-min calendar event Tue 2026-04-28 8:30 AM ET with Rem + Rudra + Dhruv (per Craig's instruction: include people who actually built the manager-agent after Craig's prototype). Google Meet invite sent. |
| 4 | 2026-04-23 | Dolly: add `list orgs` to indemn-cli | Discovered `indemn org list` already shipped in `@indemn/cli@1.3.0` (commit 8ad514f). Notified Dolly in the dev-squad reply alongside the banner ship. |
| 5 | 2026-04-23 | Dolly + Jonathan: "show org name persistently in every CLI command" — the Celine-in-Insurica near-miss fix | **AI-368 shipped.** Banner now renders on every CLI command. Published `@indemn/cli@1.4.0` to npm. |
| 6 | 2026-04-17 | Dolly: form-extractor renderer should use Inter font + platform colors not website brand | **Pushed to PR #17** branch — re-skinned to Inter font + Tailwind blue/slate (matches Copilot Dashboard's PrimeNG IndemnPreset). Replied to Dolly for re-review. |

### Still active in the queue

| # | When saved | Item | Status |
|---|---|---|---|
| 7 | 2026-04-22 | Jonathan: `functions create` + `params add` field gaps in CLI | **AI-369 PR #13 in review.** Bundle of fixes pushed; awaiting Rudra/Jonathan re-review. Once merged: push main → prod, publish 1.5.0, archive. |
| 8 | 2026-04-25 | Jonathan: Observatory tabs broken for Insurica Reception agent (Volume "No data", Flow "No flow data", other tabs show 0 conversations despite overview) | **Untriaged.** Next session's primary focus — see below. |
| 9 | 2026-04-27 | Craig's own reply to Dhruv ("Will share all the details with you once ready") in thread `1777260393.941529` | Craig handling on the side. Out of scope for next session. |
| 10 | 2026-03-18 | Archived file `F0AMS9UF351` | Long-cleared, ignore. |

---

## indemn-cli — what shipped + what's in flight

Project INDEX (`projects/jarvis-cli-mcp/INDEX.md`) says version 1.1.1; **actual current is 1.4.0 on npm + 1.5.0 in PR**. Update that INDEX next session.

### 1.4.0 — shipped 2026-04-27 13:52 UTC

**PR #11** (`feat/cli-banner-active-org`) merged 2026-04-27 05:54 UTC by Dhruv. Pushed `main → prod` to trigger publish workflow. Workflow run `24999030396` ran clean (npm ci → build → test → publish). **Linear AI-368 → Done.** Slack reply posted in #dev-squad thread `1776877932.050409` tagging Jonathan/Ganesh/Dolly with full summary + upgrade instructions.

The banner: every command prints `[<org_name> · <short_id> · <env>]` to stderr. Red for prod, dim yellow for dev. Suppressible via `--json`, `--no-banner`, or `INDEMN_NO_BANNER=1`. Self-heals on first run for pre-1.4 configs (lazy-fetches org name once, caches).

Bundled in the same PR: a tiny CI fix (`--passWithNoTests` flag dropped during repo migration from `craig-indemn/indemn-cli` to `indemn-ai/indemn-cli`).

Other things that landed alongside on `main`:
- **PR #12**: `.npmrc` with `ignore-scripts` (npm supply-chain hardening)
- **PR #8**: someone else's parallel `--passWithNoTests` fix
- **PR #10**: 15 dependabot security alerts (merged 2026-04-21 by Rudra)

So 1.4.0 includes all of those.

### 1.5.0 — PR #13 awaiting review

**PR #13** (`feat/cli-functions-config-schema`) — Linear AI-369. Closes Jonathan's 2026-04-22 ask that `functions create`/`update` only writes `name`/`type`/`description` and silently produces non-functional REST API tools.

Three commits on the branch:
1. `45aa8d7` — initial 2-step create + update merge + new flags + types
2. `2bd3902` — kebab-case auth fix + `functions test` fix + `--config` envelope unwrap + default no-auth
3. (none after the second commit — branch is at HEAD `2bd3902`, CI green)

Reviewers requested: **Rudra9214** (Rudra) + **nellermoe** (Jonathan). Slack ping posted in thread `1775717163.201049`.

**Verified end-to-end on dev** against a real test bot (`FAQ Bot` / `69d39e35cbd5097ac679606a` in dev org `69d39de1d6313bcaf94f39ae`):
- Created 4 test functions (no-auth, bearer-token, api-key, custom_tool), inspected `configurationSchema` + `executionSchema`, ran `functions test` against real httpbin.org and wttr.in endpoints, confirmed Bearer + custom-header round-trips work, partial update preserves other fields, `--no-craft-response` flips boolean to false, `--config` envelope unwrap works.
- All test functions deleted; bot back to original 2 functions.

**Two real bugs surfaced in self-review** beyond what was in the original commit:
1. Server expects kebab-case auth types (`api-key`, `basic-auth`, `bearer-token`, `no-auth`); my snake_case silently passed validation but produced no Authorization header. Fixed; snake_case still accepted as a forgiving alias.
2. `indemn functions test` was always failing (pre-existing CLI bug, not introduced by AI-369): the server's test endpoint reads configurationSchema from request body, not from the stored bot tool. CLI was sending empty body. Fixed by fetching the function's stored config first.

Plus polish:
- Default `authorization` to `{type:"no-auth"}` for rest_api when no `--auth-type` (server validation requires the field)
- `--config` auto-unwraps a `{configurationSchema:{...}}` envelope so users can pipe `functions list --json` output back through

**On merge:**
1. `git push origin main:prod` on `indemn-ai/indemn-cli`
2. Watch publish workflow
3. Verify `npm view @indemn/cli version` shows 1.5.0
4. Linear AI-369 → Done; comment with publish timestamp
5. Reply in #dev-squad thread `1775717163.201049` tagging Jonathan
6. `saved.delete` on saved item ts `1776881443.001079`

### Tail ticket (not yet filed)

Worth filing a low-priority backend ticket: *"copilot-server: add `convertPayloadToExecutionSchema` call to `createBotTool` for symmetry with `updateBotTool`."* Once shipped, the CLI can drop the 2-step create. Currently in the AI-369 PR description but not filed. Owner: TBD; doesn't block anything.

---

## form-extractor PR #17 — renderer style alignment

PR #17 (`feat/add-renderer-scheduler`) was Craig's PR opened 2026-04-06; Dolly approved on 2026-04-17 with two design notes: Inter font (not Barlow), platform-aligned colors (not website brand). PR sat idle 10 days.

This session pushed commit `b6f5cf0` to the branch:
- Bundled Inter v4.1 (Regular/Medium/SemiBold/Bold ~411-420KB each) from rsms/inter; deleted Barlow TTFs
- Updated `renderer/src/shared/styles.ts`: registered Inter family, replaced color tokens with Tailwind-aligned palette matching Copilot Dashboard's PrimeNG `IndemnPreset` (primary = blue-600, body = slate-800, muted = slate-500, border = slate-200, background = slate-50, severity = blue-800/600/400)
- Updated 2 call sites (`v2-cover.tsx`, `item-page.tsx`) to use renamed tokens
- Smoke-rendered a sample PDF (`/tmp/smoke-eval-v2.pdf`, 174KB, embeds 4 Inter weights, no Barlow references)

**Untouched:** `Indemn_PrimaryLogo_Iris.png` cover-page logo. Dolly didn't flag it; left it for her to call out if she wants.

**Slack reply** posted in thread `1776360145.234999` to Dolly summarizing the changes. Saved item archived. **PR still OPEN** — awaiting Dolly's re-review.

**Note about scope:** Only changed the form-extractor renderer's styles. Two other locations have similar React-PDF templates (`indemn-cli/src/report/styles.ts` and `indemn-platform-v2/ui/src/components/report/styles.ts`) — both still use Barlow + iris/eggplant. They're already in production. If Dolly wants those aligned too, that's a follow-up.

---

## Calendar — Tue 2026-04-28 8:30 AM ET

15-min Google Meet (`https://meet.google.com/dsy-okqw-fgc`), event id `rnth8urv89ncbsqahvgb2hahp4`. Attendees: Craig + Rem (george@indemn.ai) + Rudra (rudra@indemn.ai) + Dhruv (dhruv@indemn.ai). Goal: align on JM manager-agent test process per Rem's 2026-04-23 ask.

Time chosen because Rudra is likely India-based (8:30 AM ET = 6:00 PM IST, end-of-day-friendly for him). George's Tuesday calendar had open slots; Dhruv likewise.

---

## Linear state at session end

| Ticket | State | Notes |
|---|---|---|
| **AI-367** (parent: prevent cross-workspace mistakes) | In Progress | Both sub-asks addressed; depends on AI-369 to fully close |
| **AI-368** (active-org banner) | **Done** | Shipped in @indemn/cli@1.4.0 |
| **AI-369** (functions configurationSchema) | Ready for Testing | PR #13 awaiting review |
| DEVOPS-147 (form-extractor CI/CD full fix) | Backlog (P4) | Untouched this session — still tracked |

---

## Where the next session should pick up

**Primary work**: triage Jonathan's Observatory bug (saved item #8 / parent thread `1777060307.862239` in #dev-squad).

Symptoms Jonathan reported on 2026-04-25:
- Reception agent for Insurica
- "Volume" tab → "No data available for the selected scope and date range."
- "Flow" tab → "No flow data available — no conversation flows for the selected scope and date range."
- Other tabs show 0 conversations despite overview tab showing data
- Insurica is the workspace context

**Where to start the investigation:**
1. Pull the parent thread (`1777060307.862239`) for full context of what Jonathan was trying to do
2. Read [observability-env-inventory](2026-03-03-observability-env-inventory.md) for what services power the dashboard
3. The Observatory code lives at `indemn-ai/Indemn-observatory` (note capital I) — runs on copilot-prod EC2 `i-0df529ca541a38f3d` per `## What's Deployed` in INDEX.md
4. Most likely root cause is data-scope mismatch — the overview pulls from one collection/aggregation but the Volume/Flow tabs filter by org/agent in a way that excludes the Insurica Reception agent's data. Possible angles: (a) bot_id vs project_id mismatch, (b) date filter timezone bug, (c) agent type filter excluding "reception"-style agents, (d) data ingestion gap for that specific agent
5. Reproduce Jonathan's view in the Observatory UI on prod (read-only) before touching code
6. The observability service has dev (i-0fde0af9d216e9182) + prod (i-0df529ca541a38f3d) instances — check both, see if it's prod-specific

**Secondary work** (in flight, may resolve passively):
- AI-369 PR #13: when Rudra or Jonathan approves → push `main → prod` on indemn-cli → publish 1.5.0 → close out Linear + archive saved item #7
- form-extractor PR #17: when Dolly re-approves → can be merged

**Out of scope for next session:**
- Saved item #9 (Craig's reply to Dhruv) — Craig handling separately

---

## Patterns worth carrying forward

1. **Self-review against a real environment catches what validation-only testing misses.** Two real bugs in AI-369 (kebab-case auth + broken `functions test`) only surfaced after creating + testing real functions on a dev bot. Validation tests had all passed. Always touch the actual API before claiming "done."

2. **PRs that sit waiting for design review tend to grow stale silently.** PR #17 sat 10 days after Dolly's notes. PR #11 needed an explicit ping to Dhruv to land. When work is blocked on review, default to nudging in Slack rather than waiting.

3. **The publish workflow on indemn-cli is `main → prod` push.** Not a tag-based release. Standard pattern shared with middleware-socket-service. The `prod` branch had been stuck at the migration commit (`aa7b438`) for ~3 weeks — earlier publish attempts on 2026-04-15 had failed and no one noticed. Pushing `main → prod` brought 9 commits at once.

4. **Server kebab-case vs CLI snake_case** is a recurring gotcha. The server's auth types (`api-key`, `basic-auth`) are kebab-case constants. Future CLI features should default to kebab-case to match server contracts; accept snake_case as a forgiving alias.

5. **Calendar diplomacy for distributed teams.** Rudra's likely timezone (IST) made afternoon-ET slots painful. Choosing 8:30 AM ET for an India-based engineer trades a tiny bit of Craig's morning for a much-better experience for the engineer. Default to checking attendee timezones before defaulting to your own working hours.

---

## Action checklist for next session pickup

- [ ] Triage saved item #8 (Jonathan Observatory) — start with parent thread `1777060307.862239`
- [ ] Watch PR #13 — on approve: push main → prod, verify 1.5.0 on npm, close AI-369, reply to Jonathan, archive saved item #7
- [ ] Watch PR #17 — on Dolly's re-approve: merge or coordinate merge
- [ ] Update `projects/jarvis-cli-mcp/INDEX.md` Status section (currently says "1.1.1" — should reflect 1.4.0 on npm + 1.5.0 in flight)
- [ ] Optional: file the copilot-server tail ticket for `createBotTool` configurationSchema → executionSchema symmetry
