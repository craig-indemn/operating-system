---
ask: "Pull Craig's Slack 'Saved for Later' queue and enumerate each item so we can systematically decide what to action, delegate, or close"
created: 2026-04-23
workstream: devops
session: 2026-04-23-a
sources:
  - type: slack
    description: "saved.list API on Indemn workspace; 10 items (1 archived/done); resolved messages via conversations.history + conversations.replies fallback for thread messages"
---

# Slack "Saved for Later" triage — 2026-04-23

10 items in Craig's saved queue. Ordered newest first. Secret values in item #4 are deliberately NOT reproduced here; refer back to the original Slack message.

Legend: **ASK** = direct action on Craig. **FYI/READ** = informational, no action. **REVIEW** = needs Craig's input.

---

## 1. Customer implementation update — FYI/READ

- **When saved:** 2026-04-23 14:09
- **Channel:** `#customer-implementation` (C06PBJSAGN6)
- **From:** George Remmer (Rem) → to Rudra
- **Link:** https://indemn.slack.com/archives/C06PBJSAGN6/p1776967005791189
- **Summary:** Rem's rollup of Johnson + JM (Jewelers Mutual) delivery status.

Johnson:
- BAUT (commercial auto) completed and works as intended.
- Still waiting on sandbox test additions to verify underwriting rule integration.
- MaeLena to confirm whether the issuance step issue is a sandbox restriction vs. an error on our end.

JM (Jewelers Mutual):
- Once Joshu is pushed, Rem will sync daily with Mitchell to watch for bugs. Mitchell opted to go-live without a new sandbox (Joshu would've charged for one).
- Waiting on JM legal to return with the specific language they want on the website (they gave the "from" but not the "to").
- New page needed for vendor insurance using Thimble integration — Ganesh exploring.
- Awaiting Releventful to sign with JM so the embed integration can finish.
- Need to run manager-agent tests — **Rem asked Craig to sync on that process**.
- Next big ask: "return to conversation" to help JM change over approved/missing-info email sequences.
- Event Agent: needs a revamp; Rem taking that himself (not a dev task).
- FNOL Agent: needs testing.
- Summary component: Dhruv pushed changes that reorder based on whether user is on a venue page (JM cross-sell go-live requirement). v2 adds quote info, v3 makes it editable.

**Action for Craig:** reach out to Rem to sync on manager-agent test process.

---

## 2. voice-livekit disk space — ASK

- **When saved:** 2026-04-23 13:04
- **Channel:** DM Dolly Talreja (D0A4GLM648G)
- **Link:** https://indemn.slack.com/archives/D0A4GLM648G/p1776963535054529
- **Message:** *"Also, can you please clear the space? I know you did it the other day, not sure how we exhausted it again :confused:"*
- **Failed run:** https://github.com/indemn-ai/voice-livekit/actions/runs/24847250794
- **Attached file:** screenshot 2026-04-23

**Notes:**
- Different host from the earlier operations_api disk issue — `voice-livekit` runs on EC2 `i-01e65d5494fd64b05` (not `dev-services`).
- Same class of fix as 2026-04-21: `docker image prune -a -f` almost certainly enough, but worth investigating if something's chewing disk faster than expected given the prior cleanup.

**Action for Craig:** approve cleanup on voice-livekit, same playbook as before.

---

## 3. web-operators manual deploy — ASK

- **When saved:** 2026-04-23 13:04
- **Channel:** DM Dolly Talreja (D0A4GLM648G)
- **Link:** https://indemn.slack.com/archives/D0A4GLM648G/p1776962827182009
- **Message:** *"Hey Craig, when you get some time, can you please deploy this manually? https://github.com/indemn-ai/web-operators/actions/runs/24847166761 — The github workflow is commented, need to check with Dhruv why it is like this."*

**Notes:**
- web-operators is the Johnson Insurance renewal automation framework (Web Operator Framework — deep agent + agent-browser + Path Documents).
- The workflow being commented out is a separate mystery — Dhruv apparently gated it intentionally. Ask Dhruv on return; meanwhile one-off manual deploy unblocks Dolly.

**Action for Craig:** decide whether to uncomment the workflow or keep it as manual-only; coordinate with Dhruv.

---

## 4. operations_api PR #119 dev push + env updates — ASK

- **When saved:** 2026-04-23 10:43
- **Channel:** DM Rudraraj Thakar (D0A3RUQ6Y92)
- **Link:** https://indemn.slack.com/archives/D0A3RUQ6Y92/p1776954624947429
- **PR:** https://github.com/indemn-ai/operations_api/pull/119
- **Message:** *"Need your help to push this in DEV [...] also need to update the envs"*

**Env vars Rudra wants set in dev** (values are in his DM; copying those values into this artifact would leak them — look at the original message):

- `MONGODB_URI`
- `API_TOKEN`
- `COPILOT_USERNAME` / `COPILOT_PASSWORD`
- `OPENAI_API_KEY`
- `STRIPE_SECRET_KEY`
- `REDIS_HOST` / `REDIS_PORT` / `REDIS_USERNAME` / `REDIS_PASSWORD`
- `SLACK_WEBHOOK_URL` / `SLACK_ERROR_WEBHOOK_URL`
- `MARKEL_API_KEY` / `MARKEL_ENDPOINT`
- `CMF_API_KEY` / `CMF_ENDPOINT`
- `GIC_USERNAME` / `GIC_PASSWORD` / `GIC_BASE_URL`
- `BONZAH_EMAIL` / `BONZAH_PASSWORD` / `BONZAH_BASE_URL`
- `INSURICA_SALESFORCE_BASE_URL` / `INSURICA_SALESFORCE_CLIENT_ID` / `INSURICA_SALESFORCE_CLIENT_SECRET`
- `MIXPANEL_TOKEN`
- `DD_AGENT_HOST`, `ENVIRONMENT`, `COPILOT_API_URL`, `DD_TRACE_AGENT_PORT`, `NODE_ENV`, `DD_VERSION`, `DD_ENV`
- Joshu Sync group: `JOSHU_API_TOKEN`, `JOSHU_BASE_URL`, `JOSHU_PRODUCT_VERSION_ID`, `JOSHU_SYNC_ENABLED`, `JOSHU_SYNC_CRON`, `JOSHU_TRIGGER_AUTH_TOKEN`, `JOSHU_MAX_RECORD_ATTEMPTS`, `JOSHU_DOC_READY_POLL_MS`, `JOSHU_DOC_READY_TIMEOUT_MS`
- `AIRTABLE_BASE_ID`, `JOSHU_AIRTABLE_SOURCE_TABLE`, `JOSHU_AIRTABLE_SOURCE_VIEW`, `JOSHU_AIRTABLE_POLICY_FIELD_ID`, `JOSHU_AIRTABLE_CERTIFICATE_FIELD_ID`, `JOSHU_AIRTABLE_BASE_ID`
- `GOOGLE_GEOCODING_API_KEY`

**Notes:**
- Most of these should live in AWS Parameter Store / Secrets Manager under `indemn/dev/services/operations_api/*` rather than hand-pasted into `.env.aws`. Worth flagging to Rudra that the right pattern is PS, not DM.
- operations_api deploy already succeeded at 2026-04-21 after the disk cleanup, so the env-var flow works — just needs these new values seeded.

**Action for Craig:** push PR #119 to dev after setting the new env vars; probably a good moment to move env storage from hand-maintained file to Parameter Store for this service.

---

## 5. Sales-call transcript extraction framing — FYI/DISCUSS

- **When saved:** 2026-04-23 10:42
- **Channel:** DM Kyle Geoghan (D0A39F4FEEN)
- **Link:** https://indemn.slack.com/archives/D0A39F4FEEN/p1776954425985149
- **Message:** *"It's about how we define what we extract from a sales call transcript and what we build around it, including drafted emails, next steps, run evaluation of the opportunity, resources to potentially create, etc"*

**Notes:**
- Continuation of a broader product conversation with Kyle — scoping what we extract from sales-call transcripts (drafted emails, next steps, opportunity evaluation, resources).
- Fits naturally in the OS / intelligence layer direction. No immediate blocker; likely a design conversation to have.

**Action for Craig:** schedule a focused sync with Kyle on this; feeds into the meeting intelligence roadmap.

---

## 6. CLI feature request — `list orgs` — ASK (small)

- **When saved:** 2026-04-23 08:52
- **Channel:** `#dev-squad` (C08AM1YQF9U)
- **From:** Dolly
- **Link:** https://indemn.slack.com/archives/C08AM1YQF9U/p1776948534553849
- **Message:** *"Can you also add `list orgs` command that shows the name of the org and its id. I think it would be helpful to get the id from the cli without going to the platform."*

**Notes:**
- Small CLI addition (name + id listing). Pairs with Dolly's ask in #7 (persistent org-name in CLI prompts).

**Action for Craig:** add `list orgs` to the indemn-cli; ties in with the broader CLI-context-visibility theme.

---

## 7. Dolly → Ganesh on dev vs. prod demo orgs — REVIEW

- **When saved:** 2026-04-23 07:38
- **Channel:** `#dev-squad` (C08AM1YQF9U)
- **From:** Dolly
- **Link:** https://indemn.slack.com/archives/C08AM1YQF9U/p1776937137772539
- **Summary:** Dolly's reply to Ganesh about the dev-vs-prod demo question.

Her position:
- Project/org-id mappings already removed; stale Insurica conversations no longer appear there.
- Agrees experimentation belongs in dev, but pushing back on moving *demos* to dev because:
  1. 50+ orgs in dev → sales has trouble finding their agents
  2. Dev has in-progress features and unreleased logic that shouldn't be exposed during demos
  3. Dev instability risks demos breaking at bad moments
- Wants to wait for Dhruv before migrating any prod voice agents to dev (multiple mappings, Pinecone data, LiveKit integration — she doesn't have access to either).
- Also points out this risk exists for web agents too: wrong-org creation via CLI (no org-name visible) leads to cross-workspace data issues.
- **Direct ask to Craig:** add persistent org-name display in every CLI command, like Python venv or Mongo shell's active-db prompt. Right now `whoami` only shows org ID.

**Action for Craig:**
1. Weigh in on the dev-vs-prod demo debate with Ganesh (Dolly is making a fair case to keep demos in prod until Dhruv's back).
2. CLI improvement: surface org name alongside org ID in every command response (closes the wrong-workspace class of bug Dolly described).

---

## 8. CLI `functions create` coverage gaps — ASK/INVESTIGATE

- **When saved:** 2026-04-23 07:38
- **Channel:** `#dev-squad` (C08AM1YQF9U)
- **From:** Jonathan Nellermoe → to Craig
- **Link:** https://indemn.slack.com/archives/C08AM1YQF9U/p1776881443001079
- **Message:** *"following up, here is my assessment — The CLI `functions create` and `params add` write name / type / description / parameters — but not `endpoint` URL, `method`, `payload`, `responseField`, `outputInstructions`, `craftResponse`"*

**Notes:**
- Current CLI `functions create` + `params add` don't fully round-trip a function definition — they skip the execution-shape fields (endpoint, method, payload) and the response-shape fields (responseField, outputInstructions, craftResponse).
- Users relying on the CLI will end up with incomplete function defs that behave differently from platform-created ones.
- This is an indemn-cli feature gap, pairs with items #6 and #7 (a cluster of CLI improvements).

**Action for Craig:** patch `functions create` + `params add` to write the full field set, or document the limitation explicitly and have users round-trip through platform UI.

---

## 9. form-extractor UI review feedback — REVIEW (old)

- **When saved:** 2026-04-17 09:55
- **Channel:** `#dev-squad` (C08AM1YQF9U)
- **From:** Dolly
- **Link:** https://indemn.slack.com/archives/C08AM1YQF9U/p1776430922570959
- **Message:** *"I have approved the #2 PR but a few things: 1) The default font should be 'Inter', we use Barlow only for website. 2) I guess the color scheme you are using is again similar to the website, can you change it to match the platform. I believe the form-extractor is a part of the platform solution so the design should be in sync."*

**Notes:**
- Week-old feedback on a form-extractor PR Dolly approved.
- Two design items: (a) swap font Barlow → Inter for platform; (b) align color scheme with platform, not marketing website.
- Likely still open unless addressed in a later PR. Cross-check with recent form-extractor PRs.

**Action for Craig:** confirm these landed (or schedule the follow-up); coincides with the broader form-extractor CI/CD work just tracked in DEVOPS-147.

---

## 10. Archived file — done

- **When saved:** 2026-03-18 (archived 2026-04-17)
- **Item:** `F0AMS9UF351` (file, `state: archived`, `todo_state: saved`)
- Already cleared; no action.

---

# Prioritized action stack

| # | Type | Item | Effort | Blocker for |
|---|---|---|---|---|
| 2 | ops | voice-livekit disk cleanup | 10 min | Dolly's deploy |
| 4 | ops + secrets | operations_api PR #119 + env updates (move to PS?) | 30-45 min | Rudra |
| 3 | ops | web-operators manual deploy | 15 min | Dolly |
| 6 | feature | `list orgs` CLI command | 30-60 min | Dolly (small) |
| 7 | feature | CLI org-name in prompt | 1-2 hr | Dolly / cross-workspace class of bugs |
| 8 | feature | CLI `functions create` field gaps | 1-2 hr | Jon |
| 9 | design | form-extractor Inter + platform colors | 1-3 hr | — |
| 1 | discussion | Manager-agent test process sync w/ Rem | meeting | JM delivery |
| 5 | discussion | Kyle sales-transcript framing | meeting | Intelligence roadmap |
| 7 | decision | Dev vs. prod demo orgs w/ Ganesh | async comment | — |

**Most time-sensitive:** #2 (Dolly is waiting on disk cleanup now), #4 (Rudra's dev push + secrets), #3 (web-operators manual deploy).

**Longest-running:** #9 (form-extractor design feedback from 2026-04-17 — 6 days old, probably should close the loop first).

**Clusters:** items #6, #7, #8 are all indemn-cli improvements — could batch into one workstream.
