---
ask: "Final version of the #dev-squad message posted to Rem (primary) + Rudra (cc) with findings, Pattern C PR link, and questions back. Preserved for session handoff."
created: 2026-04-17
workstream: union-general-intake-manager
session: 2026-04-17-a
sources:
  - type: slack
    ref: "https://indemn.slack.com/archives/C08AM1YQF9U/p1776450222923819"
    description: "Posted to #dev-squad, ts=1776450222.923819, 2026-04-17"
---

# Dev-squad message — posted 2026-04-17

**Channel:** #dev-squad (C08AM1YQF9U)
**Addressed to:** Rem (U03DP1H58B1) — primary, Rudra (U0881BF4EMN) — cc
**Permalink:** https://indemn.slack.com/archives/C08AM1YQF9U/p1776450222923819

---

## Message body (as sent)

Hey @Rem — here's where I landed on the three things you flagged. @Rudra fyi.

Short version: I did a full diagnostic pass (pulled production logs, looked at exactly what each carrier returned on Ben's Xol Lounge quote and the others around it) and have a clear picture on two of the three. Third still needs a live example.

**1) Submissions that keep failing on retry**

Several different failure modes were getting lumped together here. One was a real code bug that caused the Nationwide/Scottsdale path to crash outright whenever a class-code description came back missing from the carrier API. I've shipped a fix — @Rudra, could you take a look when you have a chance? https://github.com/indemn-ai/intake-manager/pull/118

The bigger pattern isn't a code bug — some submissions are being tagged with an invalid class code earlier in the pipeline, and on retry the same bad data gets re-sent, so the same carriers reject it. I've already pulled concrete failing submissions from the logs and I'm tracing where the bad class code originates upstream. If Ben happens to remember specific companies he re-tried recently, I'd love to run against his actual test cases too — but I have enough to move on.

**2) Validation messages on fields that have data**

I haven't caught one live yet, and the code has several validator paths so without a real instance it's guesswork. If Ben can grab a screenshot next time it happens — the form, the field it's flagging, what the message says, plus carrier + state if visible — I can trace exactly which validator is misfiring.

**3) Fees/taxes inconsistent across carriers**

I've traced the mechanical gap. Each of the three carriers takes its own path through the code and they've drifted apart:
  • ACIC returns CA surplus-lines taxes in its response, so those show. The broker/inspection fees we add get dropped on the return trip.
  • Scottsdale echoes back broker/inspection but doesn't return state taxes.
  • Northfield doesn't handle fees in either direction, so nothing shows.

Net effect: Ben's seeing three different fee pictures in the rater because the code is doing three different things — not because the carriers are actually priced that differently. A fix will make the numbers we show customers consistent and closer to what they'll actually pay at bind.

Before I propose a fix direction, I want to make sure I understand the original design intent — Dhruv built most of this and the team clearly tested it a lot. Is there any existing documentation or prior context I could read on how taxes, stamping fees, and broker/inspection were meant to work across carriers? I'd like to understand what *was supposed to* happen before proposing how to change it.

Two related questions where you're the right person to decide, @Rem:
  1. For state surplus-lines taxes + stamping fees — is ACIC's computed number the source of truth you trust, or does UG maintain its own state tax table the app should apply uniformly across every surplus-lines carrier?
  2. Do you know if Northfield normally returns taxes/fees broken out or bundles them into the base premium? Their $7,847 for Xol was suspiciously clean.

Happy to jump on a call for any of it — easier to talk through than type.

---

## What's now pending

| Item | Owner | Status |
|------|-------|--------|
| Review PR #118 (Pattern C NoneType fix) | Rudra | Awaiting review |
| Response on Bug #3 policy questions | Rem | Awaiting response |
| Response on existing design docs for fees/taxes | Rem (or Rudra if Rudra has context) | Awaiting response |
| Screenshot + details for Bug #2 repro | Ben (via Rem) | Opportunistic — when it next happens |
| Specific companies from Bug #1 retries | Ben (via Rem) — optional | Not blocking (I have logs) |
| Trace upstream class-code assignment for Pattern A | Craig (me) | Next session, not blocked on Ben/Rem |
