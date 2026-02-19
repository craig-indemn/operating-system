---
ask: "Triage and fix dev deployment issues reported by Dolly — CSS leakage, persistent loading indicator"
created: 2026-02-19
workstream: platform-development
session: 2026-02-19-b
sources:
  - type: slack
    description: "Dolly's testing feedback in #dev-squad (2026-02-19 06:55 EST) — 4 issues reported with screenshots"
  - type: github
    description: "indemn-ai/copilot-dashboard-react — build-federation.js patched, commit 47f342a"
  - type: github
    description: "indemn-ai/copilot-dashboard — PR #958 for Jarvis loading fix"
---

# Session 2026-02-19-b: Dev Deployment Fixes

## What Happened

Dolly reported 4 issues from testing the dev deployment (devcopilot.indemn.ai). We triaged all 4 into beads, then investigated and resolved 2 this session.

## Issues Triaged

| Bead | Priority | Issue | Status |
|------|----------|-------|--------|
| `gn2` | P1 | CSS style leakage from React federation into Angular | **Closed** — fixed and verified on dev |
| `jim` | P1 | "Loading..." persists at bottom of AgentOverview | **Closed** — PR #958 |
| `e6f` | P1 | Persistent loading indicator at bottom of each tab | **Closed** — same root cause as `jim` |
| `wem` | P0 | Evaluations failing at baseline generation / Jarvis not initialized | **Open** — next up |
| `5q2` | P2 | Architecture discussion: repo structure and frontend-to-DB access | **Open** |

## Fix 1: CSS Style Leakage (gn2)

**Root cause:** The `@originjs/vite-plugin-federation` plugin generates `dynamicLoadingCss([...], false, ...)` in `remoteEntry.js`, which injects the full 130KB Tailwind CSS bundle into Angular's `document.head`. This conflicts with PrimeFlex (e.g., `.grid { display: grid }` overrides PrimeFlex `.grid { display: flex }`). The CSS was being loaded twice — correctly into Shadow DOM via `createShadowMount`/`styles.ts`, and redundantly into `<head>` via the plugin.

**Fix:** Added Phase 3 post-processing to `scripts/build-federation.js` that patches `remoteEntry.js` after the Vite build, flipping `dontAppendStylesToHead` from `false` to `true` in all 5 `dynamicLoadingCss` calls. This stores CSS URLs in harmless `window` arrays instead of injecting `<link>` tags.

**Commit:** `47f342a` on `indemn-ai/copilot-dashboard-react` main

**Verification:** Deployed to dev EC2, used `agent-browser` to navigate to devcopilot.indemn.ai, logged in, loaded agent detail page. Confirmed:
- `document.querySelectorAll('link[href*="style-"]').length` = 0
- Angular sidebar, header, nav rendering correctly
- React AgentOverview rendering correctly inside shadow root

## Fix 2: Persistent "Loading..." Indicator (jim, e6f)

**Root cause:** The `appdashboard-jarvis-chat` Angular wrapper initializes `isLoading = true` but only calls `loadComponent()` when `visible = true`. Since the Jarvis chat panel starts hidden (it's a modal triggered by the FAB button), `isLoading` stays `true` forever. The template's `*ngIf="isLoading && !loadError"` renders "Loading..." unconditionally at the bottom of the bot-details page.

The "Loading..." was NOT from the AgentOverview component — DOM inspection via `agent-browser` traced it to `APPDASHBOARD-JARVIS-CHAT` in the `bot-details.component.html` layout.

**Fix:** Added `visible &&` to both `*ngIf` conditions in `jarvis-chat.component.html` so loading/error states only render when the panel is supposed to be visible.

**PR:** [#958](https://github.com/indemn-ai/copilot-dashboard/pull/958) on `indemn-ai/copilot-dashboard` — awaiting review

## Skills Created

### `/local-dev` skill
Created at `.claude/skills/local-dev/SKILL.md` — documents how to start/stop/manage all Indemn platform services locally using `local-dev.sh`. Covers service groups, federation build, ports, common patterns.

### `/agent-browser` skill
Created at `.claude/skills/agent-browser/SKILL.md` — documents browser automation via the `agent-browser` CLI. Used for verifying deployments, testing UI, and checking CSS isolation on dev. Adapted from the `web_operators` repo skill.

## Deployment Notes

- **indemn-platform-v2 CI/CD:** Self-hosted GitHub Actions runner has been broken since Feb 11 (24h timeout, cancelled runs). Manual rebuild on dev EC2 required: `cd /opt/copilot-dashboard-react && sudo docker compose pull app && sudo docker compose up -d --no-deps app`
- **copilot-dashboard:** Has branch protection on main — changes must go through PRs
- **MongoDB access:** IP-restricted — dev services work on EC2 but local services fail auth when not on whitelisted IP
