---
ask: "Session 2 — resumed UG intake-manager after Rem's response. Verify Bug #3 hypotheses against design intent, not just code. Reframe the ask to Rudra + Rem correctly."
created: 2026-04-17
workstream: union-general-intake-manager
session: 2026-04-17-b
sources:
  - type: slack
    description: "Full #dev-squad thread (C08AM1YQF9U ts=1776450222.923819) including Rem's reply pointing to fee-logic design thread; edited my own message + posted reply re-framing Bug #3 as a UX question"
  - type: slack
    ref: "https://indemn.slack.com/archives/C08KW3QMQE8/p1774284374497959"
    description: "Rem added me to #indemn-uniongeneral channel; pulled the full fee-logic design thread (Ben + Dhruv, 2026-03-23 → 2026-03-27)"
  - type: mongodb
    description: "Pulled raw_response for Xol Lounge across ACIC + Northfield + Nationwide CL quote docs from ug_submission.quotes on prod via SSM"
  - type: code
    ref: "indemn-ai/intake-manager@main"
    description: "Git blame on the 'don't add fake fees' design comment (quote_service.py + quotes.py:981-982), plus full read of the end-to-end taxes_and_fees flow request → storage"
  - type: google-drive
    description: "Downloaded UG Fee Logic_Broker_Inspection.xlsx from local download (Craig fetched it); contents fully captured below"
  - type: github
    description: "Verified intake-manager PR #118 state (Rudra approved, not yet merged)"
---

# Session 2 — reframing Bug #3 from "code drift" to "UX question"

## What changed in session 2

Session 1 produced a confident-sounding but partially wrong analysis of Bug #3 (fee-calc inconsistency). Session 2 corrected that by grounding every claim in code, data, or design intent — and the conclusion is materially different from what I told Rem + Rudra in session 1.

**Session 1 framing** (wrong): "Three carrier code paths have drifted apart. Option B: build a centralized resolver. Want to fix this."

**Session 2 framing** (correct): "Each carrier's stored `taxes_and_fees` faithfully mirrors what that carrier's API returned. The current behavior is a deliberate design choice explicitly documented in the code. What Ben is observing is a UX inconsistency in the rendered comparison — not a code bug. Is the design intent still right, or should we change it?"

## Evidence that reframed it

### 1. The "don't add fake fees" comment is deliberate

Git blame on `app/routers/quotes.py:981-982`:
```
61570dd3 (Dhruv Rajkotia 2026-03-26)
  # If a provider doesn't return fees, we don't add fake ones.
  # Users can manually add fees via the Edit button if needed.
```

Timeline:
- 2026-03-25 15:40 UTC — Ben posts `UG Fee Logic_Broker_Inspection.xlsx` in `#indemn-uniongeneral` fee thread
- 2026-03-26 11:13 UTC (Dhruv's morning) — Dhruv commits `61570dd3` adding the "don't add fake fees" comment
- 2026-03-26 17:39 UTC (later that day) — Ben clarifies "we do not tax our policy/broker fee or the inspection fee. Only the premium is taxed."

Dhruv implemented the feature with an explicit architectural choice: **trust the carrier response, don't synthesize fees, let users edit manually via the Edit button in the UI.** That's the design on record in the code.

### 2. Correct per-carrier behavior (verified from Xol Lounge raw_response)

| Carrier | raw_response content | Stored taxes_and_fees | Design match? |
|---|---|---|---|
| Nationwide CL (Scottsdale) | `taxesAndFees: [Broker Fee $200, Inspection Fee $200]` with `taxableInd: "No"` | `Broker Fee $200 + Inspection Fee $200` | ✓ carrier echoed injected fees, parser extracted them cleanly |
| ACIC | `premium_breakdown: {taxes: 120, fees: 207.20}` (aggregate, no breakout); no `tax_breakdown` in this response | `Taxes $120 + Fees $207.20` | ✓ parser extracted what ACIC returned. Whether $207.20 *includes* our $200 Broker or drops it is indeterminate from the response |
| Northfield | `premium_breakdown: {gl: 7847, property: 0, inland_marine: 0, liquor: 0, total: 7847}`. No tax/fee fields. `raw_xml` not persisted | empty `[]` | ✓ parser extracts zero tax/fee fields because the SmartRater xml_parser only looks at premium-shaped fields |

### 3. The 2/26 figure from session 1 was misleading

Session 1 claimed "only 2 of 26 Nationwide CL quotes have Broker/Inspection stored — 8% compliance." Re-queried with proper filters (bindable status only, last 21 days):

| Carrier | Total | Bindable | With Broker/Inspection |
|---|---|---|---|
| Nationwide CL | 16 | 2 | 2 (100%) |
| ACIC | 16 | 5 | 0 (ACIC stores its own aggregate taxes/fees, not broker/inspection as line items) |
| Northfield | 15 | 6 | 0 (by design) |

The 14 Nationwide CL failures were Pattern C (NoneType crash — fixed in my still-open PR #118). When a Nationwide CL quote actually succeeds, it's 100% compliant.

### 4. UG Fee Logic_Broker_Inspection.xlsx content

Ben's authoritative spec (full content — for posterity since file lives only in UG Slack workspace):

| Carrier | Broker Fee | Inspection Fee | Notes |
|---|---|---|---|
| SIC PL | $125 | $95 | |
| SIC PL HV | $350 | $350 | HV = High Value: Coverage A ≥ $1M |
| SIC CL | $200 | $200 | Only when inspection is required, usually when property coverage is quoted; fee is per-location |
| Northfield | $200 | $200 | |
| ACIC | $200 | $200 | |

Plus Ben's tax rule (from thread): *"we do not tax our policy/broker fee or the inspection fee. Only the premium is taxed."*

### 5. Current code vs Ben's spec — where they match and don't

- `is_taxable: false` on broker/inspection in `_build_fee_items()` (quote_service.py:102) — ✓ matches Ben's tax rule
- Fixed $200 Broker + $200 Inspection injected via `_FALLBACK_PROVIDER_FEES` — partially matches. Ben's spec says inspection is **per-location** for SIC CL; code treats it as flat.
- Injected fees are sent to each carrier API in the request payload — ✓
- Stored `taxes_and_fees` comes from the normalizer's extraction of the RESPONSE (not the request) — explicit choice
- Users can edit manually via UI — per the design comment, but unclear if Ben's workflow uses that path

## What I did in #dev-squad

Edited original message (ts=1776450222.923819) — items 1 and 2 kept, item 3 replaced with "revising my take in a reply below"

Posted reply (ts=1776454148.743169) framing Bug #3 as a product/UX question with 3 specific decisions to make:

1. Should the 3 carriers render a uniform line-item breakdown in the comparison?
2. If uniform — inject UG defaults display-only, or split ACIC's aggregate "Fees", or something else?
3. State SL taxes + stamping fees — only ACIC surfaces them today; do we want uniform state tables?

Tagged Rem + Rudra for input. Awaiting their response before proposing any code change.

## Where each bug stands after session 2

| Bug | Status |
|---|---|
| #1 Pattern A (invalid class code 9711) | Not started. Unblocked. Next session pulls the MongoDB doc for thread `AQQkADA...EOW6JgWwEgCg7bI4JvL_iw=` and traces the class code back through extraction / class-code matcher |
| #1 Pattern C (NoneType crash) | PR #118 open, approved by Rudra 2026-04-17, **not yet merged.** Safe to merge anytime |
| #2 False-positive validations | Blocked on live repro from Ben. Ask still with Rem |
| #3 Fee/tax inconsistency | Reframed as product/UX question. Awaiting Rem + Rudra responses |

## Context future-me needs

- The UG Fee Logic spreadsheet content is captured in this artifact (section 4) since it lives in UG's Slack workspace and my Indemn-scoped token can read the message but not download the file.
- Rem added me to `#indemn-uniongeneral` (C08KW3QMQE8) on 2026-04-17; I can read the channel but any file posted there is cross-workspace and needs the user to help fetch.
- PR #118 is ready to merge. When it does, Pattern C crashes should disappear from logs. That's verification evidence for Ben's "older subs still failing" — Pattern C was a large fraction of the noise.
- The `AIRTABLE_BASE_ID` confusion in Rudra's DM (see devops artifact from 2026-04-24) is unrelated to intake-manager but the same general class of issue — Rudra's DM value ≠ the AWS PS value; leaving the PS value authoritative was the right call.

## What a future session should do

1. **Wait for Rem/Rudra's response** on the 3 UX questions before proposing code
2. **Unblock Pattern A** (does not require anyone's response):
   - Pull MongoDB `submission_parameters` for thread `AQQkADA...EOW6JgWwEgCg7bI4JvL_iw=`
   - Check `primaryClassCode` vs the business description
   - Trace through `app/services/class_code_matcher.py` (embed → Atlas vector search → GPT-4o-mini rerank) and `app/services/pipeline_v2/tools.py::lookup_class_codes`
   - Decide if class code matcher picked wrong, or if the ACORD 126 had 9711 literally
3. **Merge PR #118** if Rudra hasn't already — it's a 3-line fix that unblocks Nationwide CL crashes
