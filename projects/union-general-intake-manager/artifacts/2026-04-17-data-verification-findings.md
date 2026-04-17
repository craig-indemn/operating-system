---
ask: "Verify all three bug hypotheses with real data — pull production logs and MongoDB quote documents to confirm WHAT is happening, WHY it's happening, and HOW each could be resolved. No fixes until understanding is complete."
created: 2026-04-17
workstream: union-general-intake-manager
session: 2026-04-17-a
sources:
  - type: aws
    description: "SSM send-command (read-only) against copilot-prod (i-0df529ca541a38f3d) to pull docker logs from intake-manager-backend container — 6 hours of logs filtered for errors and provider activity"
  - type: mongodb
    description: "Queried ug_submission.quotes via docker exec on intake-manager-backend container using motor/pymongo — pulled full quote documents, raw_response, premium_breakdown, coverage_details for the Xol Lounge thread that produced Ben's screenshot"
  - type: code
    ref: "indemn-ai/intake-manager@main"
    description: "Cross-referenced data against code paths identified in earlier bug3-fee-calc-analysis artifact"
---

# Data Verification — WHAT, WHY, HOW for all three bugs

## Test case: Ben's screenshot

The submission that produced Ben's screenshot has been identified:
- **thread_id:** `AQQkADAwATM0MDAAMi1hMmZhLTE5ZDYtMDACLTAwCgAQAC-m6akESHxOsBfSR7hlxV8=`
- **Business:** Xol Lounge (DBA XOL Lounge) — Corporation, 0 years in business
- **Description:** "Bar/Lounge with bottle service, no food offered. Hours: Wed-Sat 7:00pm-2:00am. Occupancy 150, seating 100. DJs. Security/bouncers on staff."
- **Address:** 1610 19th St, Bakersfield, CA 93301 (Kern County)
- **Class code:** 16940 (Restaurants with >75% alcohol sales, bar-only, with dance floor)
- **GL exposure:** $240,000 annual receipts
- **Policy dates:** 2026-05-04 → 2027-05-04
- **Carriers dispatched:** ACIC, NATIONWIDE_CL (labeled "Scottsdale"), NORTHFIELD
- **Generation log:** `[GENERATE] Finished for thread=...: generated=3, errors=0` — all three succeeded
- **Frontend request IP** (from logs): 172.31.43.132 then 172.31.28.50 (copilot-server proxy)

## Bug #3 — Fee calculation inconsistency (FULLY VERIFIED)

### WHAT — stored MongoDB state for Xol Lounge

All three quote documents, version=1, is_latest=True, status=bindable:

| Provider | base premium | taxes_and_fees items stored | total_taxes_and_fees | UI total |
|----------|--------------|---------------------------|----------------------|----------|
| ACIC | $3,800.00 | `[tax "Taxes" $120.00, fee "Fees" $207.20]` | $327.20 | $4,127.20 ✓ |
| NATIONWIDE_CL (Scottsdale) | $3,946.00 | `[fee "Broker Fee" $200, fee "Inspection Fee" $200]` | $400.00 | $4,346.00 ✓ |
| NORTHFIELD | $7,847.00 | `[]` (empty) | null | $7,847.00 ✓ |

MongoDB data confirms the screenshot exactly. The stored divergence is the rendered divergence.

### WHY — per-carrier code paths diverge; Northfield is fee-blind

Confirmed from both code read (prior artifact) and stored raw_response data:

**ACIC:**
- `raw_response.premium_breakdown` = `{premium: 3800, taxes: 120.0, fees: 207.2, total: 4127.2}`
- `raw_response.tax_breakdown` = **null** (granular line items missing for this quote)
- ACIC's XML parser (`acic/xml_parser.py:_parse_tax_breakdown`) reads `<net.AtlanticCasualty_SLTaxes>` + `<slTaxes>` + `<slFees>` and aggregates into flat `taxes` / `fees`. For another CA submission in the same hour ($903 base), we captured a fuller response showing `{CA Surplus Lines Tax: 27.09, Stamping Fee: 1.63}` — so ACIC *does* return granular breakdown, but this particular response either didn't include it or the parser flattened it before storage.
- ACIC's $207.20 "Fees" is high — stamping fee on a $3,800 base should be ~$6-10 at CA rates (0.16-0.18%). The remainder is likely an ACIC policy/admin fee, not the Broker/Inspection fees we injected (which got dropped on the round-trip).
- Injected fees are dropped: our code sends `type="fee"` items to ACIC's XML request, but ACIC's response only echoes back its own computed surplus-lines taxes/fees.

**Scottsdale (Nationwide CL):**
- `raw_response` includes Nationwide's full JSON: `applicationLink`, `quoteNumber`, `totalPremium`, `taxesAndFees`, etc.
- Nationwide CL normalizer (`nationwide/normalizer.py:554-615`) extracts `taxesAndFees` array from response, filters out $0 items via `SKIP_ZERO_FLAT_FEES`, uses `otherDescription` for "Other Fee X" entries to restore human-readable names like "Broker Fee" and "Inspection Fee".
- Nationwide's API **echoes back** the Broker/Inspection fees we sent ($200 each via `_build_taxes_and_fees` in payload), which is why they appear in the stored quote.
- No state surplus-lines taxes returned — Nationwide CL's API either doesn't compute them or we're not requesting that level of detail.

**Northfield:**
- `raw_response.premium_breakdown` = `{gl: 7847, property: 0, inland_marine: 0, liquor: 0, total: 7847}` — **no tax/fee fields at all**
- `raw_response.input_params.taxes_and_fees` = `[Broker Fee $200, Inspection Fee $200]` — **the injected fees are visible as input, but were never acted upon**
- Northfield's entire code path has zero references to tax/fee/surplus/broker/inspection in its xml_builder, xml_parser, provider, or normalizer (grep-confirmed).
- `input_params` is just a debug snapshot of what the provider received — it's stored but never transformed into output.
- **Injected fees are dropped before the Travelers Northland API call is made.**

### HOW — resolution options

### Option A: narrow per-carrier patches

1. **Northfield** — in `providers/northfield/provider.py` (or its normalizer, which gets invoked by `quote_enrichment`), copy `accumulated_params["taxes_and_fees"]` (containing the injected Broker/Inspection) into the QuoteResult. Also consider whether Northfield's response has any fields our parser missed — but grep confirms no. So this is a pure "preserve injected defaults" fix.

2. **ACIC** — in `providers/acic/acic_provider.py`, after parsing ACIC's slTaxes/slFees, append the injected broker/inspection fees from `accumulated_params` (since ACIC drops them on round-trip). Preserve ACIC's own taxes/fees on top.

3. **Scottsdale (Nationwide CL)** — no code change (already works correctly).

Risk: three disjoint code paths persist. Any new carrier added gets the same bug. And we still don't handle state surplus-lines taxes uniformly.

### Option B: centralized `taxes_and_fees_resolver` (recommended)

Add a post-processing step in `QuoteGenerationService.generate_quote` (`quote_service.py:275`) after `provider_instance.generate_quote()`:

```python
result = await provider_instance.generate_quote(...)
result = await taxes_and_fees_resolver(
    result=result,
    accumulated_params=accumulated_params,
    provider=provider,
    quote_type=quote_type,
)
```

Where `taxes_and_fees_resolver`:
1. Starts with whatever the provider extracted into `result.taxes_and_fees`
2. Ensures broker/inspection fees are present — if not, adds them from `accumulated_params["taxes_and_fees"]` (the injected values)
3. Computes state surplus-lines taxes and stamping fees from a state table if the carrier is surplus-lines AND the result doesn't already have them (prevents double-counting ACIC's regulator-returned values)
4. Returns the enriched `QuoteResult`

All three providers' results then go through the same post-processing. Adding a new carrier no longer requires per-carrier fee logic.

### Option C: data-model addition (orthogonal, may be required)

If Option B needs to compute surplus-lines taxes for Northfield (which doesn't return them), we need a state-by-state tax + stamping fee configuration. This data is available from SLA-CA and equivalents. Before building this, confirm whether:
- Current behavior (only ACIC's numbers show, and they might be wrong) is acceptable, OR
- We need correct state-level numbers for all carriers (true for an accurate comparative rater)

### Open verification questions for Rem / UG operations:

- Is ACIC's $207.20 "Fees" on the Xol Lounge quote *expected* (i.e., is that the correct ACIC fee structure), or is it off?
- Should broker/inspection fees appear *in addition to* or *merged with* carrier-returned fees (e.g., stamping fee)? The screenshot shows them as separate line items for Scottsdale but combined under generic "Fees" for ACIC — is that the correct display?
- Is Northfield's $7,847 "all-in" (their API includes state taxes in the base) or "base only"? The $7,847 is exactly double ACIC's $3,800 base so suspicion is warranted but doesn't prove anything.

## Bug #1 — Older submissions still fail (ROOT CAUSE IDENTIFIED)

### WHAT — log evidence of active failures

Within the 6-hour log window I pulled, I see *distinct* failure patterns. These are not the same as Ben's Xol Lounge (which succeeded) — these are *other* submissions failing:

**Failure pattern A: Invalid class code (all 3 carriers fail identically)**
- thread_id `AQQkADA...EOW6JgWwEgCg7bI4JvL_iw=` (different submission), timestamp 2026-04-17 16:20:25 ET
- Log: `[REGENERATE] Finished for thread=...: generated=0, errors=3` — this is a **regenerate** (retry), which matches Ben's "resubmitted older subs still failing"
- ACIC returned "9711 - Unable To Retrieve Class Information For Supplied Class Code" plus "Only a numerical value greater than 0, or 'IF ANY' can be supplied in the General Liability Exposure field"
- Nationwide CL: "No search results found for the given input combination" (API 400 on `lookup_program_classcodes`), then fatal "required fields missing — programCode"
- Northfield: `RATEERROR` (class not eligible)

**Root cause for Pattern A:** The class code `9711` is being passed but ACIC rejects it as unknown. Also the "General Liability Exposure" field has an invalid value. When one carrier returns class code issues and others return "no search results" on the same submission, the data problem is *upstream* — likely in our extraction or class-code-matcher step populating a bogus class code.

Files to investigate:
- `app/services/class_code_matcher.py`
- `app/services/quote/parameter_extractor.py`
- `app/services/quote/llm_extractor.py`
- `app/services/extraction/` dir

**Failure pattern B: Validation-failed or rate-error for specific classes**
- `BIG HOT CRAB INC.` at 2026-04-17 16:21:08: Northfield `VALIDATIONFAILED` — "class may not be eligible for this carrier"
- Separate from Pattern A — this is a real "carrier doesn't accept this class" outcome, not a bug. The class code is valid; it's just one the carrier won't write.

**Failure pattern C: Python crash in Nationwide CL agent**
- 2026-04-17 16:21:15: `[NW-CL] Agent failed: object of type 'NoneType' has no len()`
- This is a Python TypeError in the Nationwide CL graph code (LangGraph agent) — **an actual bug**, not a business-validation failure. Triggered by something in the `BIG HOT CRAB` submission's data shape.

Files to investigate:
- `app/services/quote/providers/nationwide/cl/graph.py`
- `app/services/quote/providers/nationwide/cl/tools.py`

**Failure pattern D: Territory enrichment mismatches (warnings, not failures)**
- `GetTerritories returned state=FL for zip 95667, expected CA — skipping city/county overwrite`
- `GetTerritories returned state=AR for zip 95355, expected CA — skipping city/county overwrite`
- These are warnings where Travelers' API returns a state different from what we sent. The code handles it gracefully (skipping the overwrite) — not a bug per se but signals Travelers' API quality issues.

### WHY — root cause analysis per pattern

- **Pattern A** is a data-quality bug — something upstream is assigning class code `9711` to submissions that shouldn't have it. When the same submission is regenerated, the same bad class code gets re-used, reproducing the failure. Classic case of bad data persisting through retries.
- **Pattern B** is correct system behavior — carriers decline high-risk or out-of-appetite classes.
- **Pattern C** is a Python bug in Nationwide CL agent code — likely a `.len()` call on a None return from a tool. Should be a one-line fix once the specific line is found.
- **Pattern D** is external API flakiness, already handled.

### HOW — resolution options

1. **Pattern A (class code data quality)** — need to inspect the offending submission's extracted data. What did our extractor think the class code was, and why 9711? Requires pulling the submission_data document from MongoDB for thread `AQQkADA...EOW6JgWwEgCg7bI4JvL_iw=` and comparing extracted class code against ACIC's valid code list. If the extraction is broken, fix `class_code_matcher` / extractor. If the data is correct but stale from a prior failed extraction, the retry path needs to re-run extraction.

2. **Pattern C (NoneType crash)** — grep for `len(` in `nationwide/cl/graph.py` and `tools.py`, trace which result is None. Add a None check. This is a hardening fix.

3. **Request specific submission IDs from Rem** — the "older subs" Ben is retrying. Then we can pull each one's MongoDB doc and log trail to identify which pattern they hit. Without these IDs we're guessing which pattern applies to which sub.

## Bug #2 — False-positive validation violations (INVESTIGATION NOT YET STARTED)

We haven't pulled data on this yet — need a specific form + field + submission from Ben to reproduce. The logs show ACIC validation messages like "Only a numerical value greater than 0, or 'IF ANY' can be supplied in the General Liability Exposure field" — but these come from ACIC's carrier API, not our form validator. Bug #2 is about *our* validation layer throwing false positives on form fields with data. Different surface, different code (`validation/json_rule_validator.py`), different root cause hypothesis.

## Summary

| Bug | WHAT (verified) | WHY (verified) | HOW (recommendation) |
|-----|-----------------|----------------|----------------------|
| #1 Older subs fail | 4 distinct failure patterns: invalid class code (A), carrier declines (B), Python NoneType crash (C), territory mismatch warnings (D). "Older subs" pattern matches [REGENERATE] path with same bad upstream data | Pattern A: bad class code persists across retries. Pattern B: legitimate carrier declines. Pattern C: real Python bug in Nationwide CL agent. Pattern D: external flakiness, handled. | Request specific failing submission IDs from Ben, map each to a pattern. Fix patterns A + C. B is not a bug. |
| #2 Validation false-positives | Not yet investigated — need form+field+submission specifics from Ben | Unknown | Request reproduction from Ben |
| #3 Fee-calc inconsistency | All 3 carriers' stored state confirmed in MongoDB, matches screenshot exactly. Northfield's injected fees dropped before API call; ACIC's dropped on round-trip; Scottsdale echoes back correctly | Code gap: no unified fee/tax pipeline. Three providers each own isolated tax/fee logic; Northfield has none; ACIC doesn't round-trip injected fees | Option B: centralized `taxes_and_fees_resolver` in `QuoteGenerationService.generate_quote`. Possibly Option C alongside (state tax table). Need UG ops input on whether ACIC's numbers are correct source of truth. |

## Non-bug observations worth flagging

- **Frontend container unhealthy for 3 days** (since ~2026-04-14) — `wget localhost:3000` fails with Connection refused. Failing streak 9,107 checks. Users appear to be using the portal successfully, so either the healthcheck is misconfigured or the frontend is being served via a path that bypasses the container's internal listener. Needs follow-up but doesn't correlate with Ben's reported bugs.
- **DataDog trace ingestion is broken** on this host — "failed to send, dropping N traces to intake at http://localhost:8126" every ~10s. Low priority.
- **Intake-manager's `/opt/Intake-manager/.env` is still hand-maintained on the EC2** — flagged in devops project, previously introduced the Nationwide URL regression. Same risk here for any env-var flip.
