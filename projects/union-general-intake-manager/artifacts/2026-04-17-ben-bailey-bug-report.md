---
ask: "Capture Ben Bailey's bug report forwarded by Rem on 2026-04-17 into structured form for systematic triage"
created: 2026-04-17
workstream: union-general-intake-manager
session: 2026-04-17-a
sources:
  - type: slack
    description: "DM thread with George Remmer (U03DP1H58B1) in D0A41991H3K, messages at ts=1776443514.330659 (forwarded from Ben) and follow-ups 1776445061–1776445295"
  - type: slack
    description: "Screenshot attached to Ben's original message — Ben Bailey (U08KVL9D0HG) in workspace TFJBK4B7A. File F0ATM1YGA6A saved locally as artifacts/2026-04-17-ben-bailey-screenshot.png"
---

# Ben Bailey bug report — Union General intake manager

**Reporter:** Ben Bailey (UG, Slack U08KVL9D0HG)
**Forwarded by:** George Remmer ("Rem", U03DP1H58B1) — 2026-04-17 12:57 ET
**Prior context:** Today's Nationwide URL fix confirmed working for *newer* submissions. These issues surfaced on the same submissions pipeline but are distinct from the URL-mismatch fix.

## Ben's verbatim message

> It looks like the newer subs are working. I tried sending some other subs through again that I tried the other day and they are still failing. Not sure what to make of that.
>
> There's some odd violation messages in some fields that say it has to be completed or requires something such as name or description but it's on fields that clearly have data in them so I'm not sure why it's flagging those incorrectly. I'm not sure the fee calculation is working right. Taxes/Fees for surplus lines show up only for ACIC and broker/inspection fees only appear on SIC.

## Issue 1 — Older submissions still fail after Nationwide fix

**Symptom:** Resubmitting previously-failed subs still errors.
**What we know:** The Nationwide auth-token regression was fixed at the infrastructure level (wrong `NATIONWIDE_API_BASE_URL`, container recreated on copilot-prod ~11:00 ET). New submissions after that time succeed. Ben's retries of older submissions still fail.
**What we don't know:**
- Whether the "older subs" hit Nationwide at all, or a different carrier
- Whether the failures are identical errors (auth? timeout? validation?) or different
- Whether cached/persisted submission state is replayed in a way that doesn't honor the fixed env
- Submission IDs — without these, we cannot pull logs to reproduce

**To investigate:**
- Ask Rem / Ben for 2–3 concrete submission IDs that are still failing
- Pull error logs from intake-manager on copilot-prod for those IDs
- Check whether submission state is stored in a way that captures carrier URL at creation time vs. resolving it at send time

## Issue 2 — False-positive validation violations

**Symptom:** Form validation reports "must be completed" or "requires name or description" on fields that Ben can see contain data.
**What we know:** Nothing concrete — Ben's report is general.
**What we don't know:**
- Which form / page triggers it
- Which fields specifically
- Whether it reproduces every time or intermittently
- Whether it's tied to a specific carrier or shared validation layer

**To investigate:**
- Ask Ben for a screen recording or step-by-step repro on one specific submission
- Once repro'd, locate validation layer — likely shared between carriers (frontend) or per-carrier (backend schema validator)

## Issue 3 — Fee calculation inconsistency across carriers

**Symptom:** Comparative rater shows divergent surcharge behavior per carrier, which is not expected for surplus-lines insurance where state rules drive taxes/fees regardless of carrier.

**Evidence from screenshot** (`artifacts/2026-04-17-ben-bailey-screenshot.png`):

| Line item | Atlantic Casualty (ACIC) | Scottsdale (SIC) | Northfield |
|-----------|--------------------------|------------------|------------|
| General Liability | $3,800.00 | $3,946.00 | $7,847.00 |
| Taxes | $120.00 | — | — |
| Fees | $207.20 | — | — |
| Broker Fee | — | $200.00 | — |
| Inspection Fee | — | $200.00 | — |
| **Total** | **$4,127.20** | **$4,346.00** | **$7,847.00** |

**Observations:**
- Taxes + Fees (surplus-lines regulatory charges) appear *only* on ACIC
- Broker Fee + Inspection Fee (agency-level charges) appear *only* on SIC
- Northfield shows no surcharges at all AND a round $7,847 GL with zero cents, visually suggesting its premium includes all-in or its fee module never runs
- Three carriers, three different fee behaviors — almost certainly per-carrier logic paths that have diverged

**Hypotheses to test:**
- **Data hypothesis:** State-level tax/fee tables exist but are only loaded/joined for some carriers. Check the rate/tax configuration data store — does it have rows for all three carriers in this state?
- **Code hypothesis:** Each carrier has its own quote-normalization path (ACIC vs. SIC vs. Northfield integrations) and they compute totals differently. Likely one path computes taxes+fees, another computes broker+inspection, a third skips surcharges entirely.
- **Response-mapping hypothesis:** Each carrier API returns surcharges under different keys; the mapper for each carrier only picks up some of them.

**To investigate:**
- Locate the quote/rater code path for each of the three carriers
- Read side-by-side to see how each populates the `taxes`, `fees`, `broker_fee`, `inspection_fee` fields
- Check whether there's a central "apply state surcharges" step and whether it runs for all carriers
- Look at the raw carrier API responses stored with the quote (if any) to separate "carrier didn't return it" from "we didn't map it"

## Priority signal

Rem, on "is this high priority":
> If you could, yes

Craig: "sure."

---

## Next actions (initial)

1. **Repo mapping** — clone `intake-manager`, `ug-apis`, `ug-service`; identify which owns: (a) comparative rater UI, (b) carrier integrations, (c) fee/tax calculation, (d) form validation
2. **Reproduction environment** — determine whether intake-manager runs locally; if not, use staging. The Nationwide fix was staging-vs-prod confusion so staging should be fully functional for this work.
3. **Request specifics from Rem/Ben** — failing submission IDs (Issue 1) and a specific form + field example (Issue 2). Don't guess; ask.
4. **Fee-calc deep-dive** — read the three carriers' rater paths side-by-side; this is the most reproducible of the three (screenshot is already a reproduction).
