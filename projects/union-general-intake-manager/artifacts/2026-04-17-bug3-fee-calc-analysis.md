---
ask: "Deep-dive Bug #3 (fee-calc inconsistency across carriers) in intake-manager — identify root cause by reading code side-by-side across ACIC, Nationwide CL (Scottsdale), and Northfield"
created: 2026-04-17
workstream: union-general-intake-manager
session: 2026-04-17-a
sources:
  - type: github
    ref: "indemn-ai/intake-manager@main"
    description: "Shallow clone at /tmp/ug-recon/intake-manager (depth=1)"
  - type: code
    description: "Side-by-side read: quote_service.py (dispatcher+fee injection), acic/xml_parser.py (_parse_tax_breakdown), acic/xml_builder.py (fee sending), nationwide/normalizer.py (taxesAndFees extraction), nationwide/cl/provider.py, nationwide/cl/payload_builder.py, northfield/xml_parser.py + northfield/provider.py + northfield_normalizer.py (all three confirmed ZERO references to tax/fee/surplus/broker/inspection)"
---

# Bug #3 — Fee calculation inconsistency across carriers

## The observed symptom

From Ben's screenshot (artifacts/2026-04-17-ben-bailey-screenshot.png):

| Carrier | GL Base | Surplus-lines Taxes | Surplus-lines Fees | Broker Fee | Inspection Fee | Total |
|---------|---------|---------------------|--------------------|------------|----------------|-------|
| Atlantic Casualty (ACIC) | $3,800 | $120 | $207.20 | — | — | $4,127.20 |
| Scottsdale (SIC / Nationwide CL) | $3,946 | — | — | $200 | $200 | $4,346 |
| Northfield | $7,847 | — | — | — | — | $7,847 |

Three carriers, three disjoint fee behaviors. Ben said: *"Taxes/Fees for surplus lines show up only for ACIC and broker/inspection fees only appear on SIC."*

## Root cause

**There is no unified fee/tax pipeline.** Each carrier's provider is solely responsible for what ends up in `quote_doc.taxes_and_fees`, and the three carrier paths are not consistent.

### The intended flow (from code comments and logic)

1. **Inject defaults before send:** `quote_service._inject_default_fees_if_missing()` (quote_service.py:200) writes `broker_fee` + `inspection_fee` into `accumulated_params["taxes_and_fees"]` if no meaningful fees are already present. Defaults come from `workflows_config.quote_config.provider_default_fees` in MongoDB, with hardcoded fallback in `_FALLBACK_PROVIDER_FEES` (quote_service.py:25). Fallback table has entries for NATIONWIDE, NATIONWIDE_HV, NATIONWIDE_CL, NORTHFIELD, ACIC — all at $200/$200 except Nationwide PL ($125/$95 standard or $350/$350 HV).
2. **Provider sends request:** Each provider's payload builder serializes `taxes_and_fees` into the carrier's request format.
3. **Provider parses response:** Each provider's parser/normalizer extracts what came back.
4. **Result stored + served:** `quote_enrichment.enrich_quote()` (quote_enrichment.py:33) returns `quote_doc.get("taxes_and_fees", [])` straight through to the frontend.

### Where each carrier diverges

| Carrier | Reads injected fees from params? | Sends in request? | Extracts fees from response? | Net result |
|---------|----------------------------------|-------------------|------------------------------|------------|
| **ACIC** | Yes — `xml_builder.py:1391` filters for `type="fee"` and maps to ACIC's XML `fees` element | Yes | **Partial** — `xml_parser.py:1212` `_parse_tax_breakdown()` reads `net.AtlanticCasualty_SLTaxes` + `slTaxes` + `slFees` from response. These are **ACIC-computed surplus-lines state taxes/fees**, not the broker/inspection we sent. **Broker/inspection we injected get dropped on the round-trip.** | Surplus-lines taxes+fees ✓, broker/inspection ✗ |
| **Scottsdale (Nationwide CL)** | Yes — `nationwide/cl/payload_builder.py:1329` `_build_taxes_and_fees()` reads MongoDB format and emits Nationwide `taxesAndFees` with `otherDescription` for custom fees | Yes | Yes — `nationwide/normalizer.py:554-615` extracts `taxesAndFees` array from response. Skips `$0` flat fees via `SKIP_ZERO_FLAT_FEES = {"Broker Fee", "Inspection Fee", "Other Fee 1", "Other Fee 2"}`. Uses `otherDescription` for "Other Fee X" entries to restore human-readable names. | Broker/inspection ✓ (because Nationwide echoes back what we sent), surplus-lines taxes only if Nationwide computes them |
| **Northfield** | **NO** — grep on `/app/services/quote/providers/northfield/**` for `tax\|fee\|surplus\|broker\|inspection`: **zero matches**. Same for `app/services/quote/normalizers/northfield_normalizer.py`. | NO | NO | Empty. Base premium only. |

### The Northfield gap is the most glaring

The Northfield code path is end-to-end fee-blind:
- `providers/northfield/xml_builder.py` — doesn't put injected fees in the request
- `providers/northfield/xml_parser.py` — doesn't extract any tax/fee elements from the response
- `providers/northfield/provider.py` — doesn't touch `taxes_and_fees` in the QuoteResult
- `normalizers/northfield_normalizer.py` (used by quote_enrichment) — doesn't populate `taxes_and_fees`

So for Northfield, the injected $200/$200 defaults from `_FALLBACK_PROVIDER_FEES["NORTHFIELD"]` are discarded before the request is even sent.

### Why ACIC loses broker/inspection

ACIC's xml_builder sends only items filtered by `type="fee"` (line 1391, comment at line 1383). But ACIC's xml_parser is scoped to `_parse_tax_breakdown` (line 1212) which reads specific XML paths for *surplus-lines* taxes/fees (the regulatory ones). ACIC's response doesn't round-trip arbitrary agency fees back to us — so broker/inspection vanish on the response side.

### Why Northfield's premium looks "too round"

$7,847.00 with zero surcharges is suspicious because surplus-lines quotes in most states require state taxes + stamping fees regardless of carrier. Since Northfield (Travelers subsidiary, E&S) writes surplus-lines, the *real* quote at bind time would include state taxes. The intake-manager rater just isn't showing them.

This is both a fee-calc consistency bug AND an accurate-quoting bug — we're showing customers numbers that don't reflect what they'll actually pay.

## Architectural gap

There is no common step that:
1. Computes **state-level surplus-lines taxes + stamping fees** based on risk state and premium, applying uniformly to any surplus-lines carrier quote. This is a state regulation, not a carrier-specific calculation.
2. Ensures **agency broker/inspection fees** are present on every carrier quote, regardless of whether the carrier API echoes them back.

Both should be carrier-agnostic post-processing over the QuoteResult. Instead, the logic is split inside each carrier's normalizer, and two of three normalizers don't handle it.

## Fix options (in increasing order of scope)

### Option A — Per-carrier patch (narrowest)

1. **Northfield:** Add taxes_and_fees handling — either preserve the injected defaults from accumulated_params into the QuoteResult, or parse the Northfield XML response for equivalent elements (need to know whether Northfield returns them).
2. **ACIC:** After parsing ACIC's surplus-lines taxes/fees, append the injected broker/inspection fees from accumulated_params to the result (they round-tripped out, so we reinstate them from the request).

Risk: still three disjoint code paths. Next carrier added will repeat the same bug.

### Option B — Centralized post-processing step (recommended)

Add a `taxes_and_fees_resolver` step in `quote_service.QuoteGenerationService.generate_quote` after the provider call:

1. Start with `result.taxes_and_fees` (whatever the provider extracted).
2. Ensure broker/inspection fees exist — if the result has `type="fee"` items with amount > 0 matching broker/inspection descriptions, keep them; otherwise append from the injected defaults used in the request.
3. Compute state surplus-lines taxes + stamping fees using a state-level table and the final premium, if the carrier is a surplus-lines carrier AND we didn't already extract them from the response (prevents double-counting ACIC's regulator-returned values).

This centralizes the logic, keeps provider-specific parsers focused on what the carrier actually returns, and guarantees consistency across carriers.

### Option C — State tax/stamping fee configuration data model

Orthogonal to the code fix — surplus-lines tax rates and stamping fee schedules vary by state and need to be maintained. If this data is already elsewhere (e.g., ACIC computes it server-side so we rely on their number), we need either:
- A state-by-state surplus-lines tax/fee table in MongoDB, configurable per workflow, OR
- Confidence that each carrier returns their own state-appropriate taxes and we *just* need to extract them consistently.

Need to verify with UG ops / Rem which is correct before implementing.

## Immediate questions before fixing

1. **Is ACIC's $120 tax + $207.20 fees correct for the state in question?** Need to know the risk state to verify. If yes, then ACIC's response is authoritative and we just need to get equivalent numbers out of Nationwide CL and Northfield responses (or compute them ourselves for carriers that don't return them).
2. **Does Nationwide CL actually return state surplus-lines taxes?** The code in `nationwide/normalizer.py` extracts `taxesAndFees` generically — if Scottsdale's response had tax items, the normalizer would show them. The screenshot shows none, suggesting Nationwide CL's API doesn't return state taxes for surplus-lines quotes (or we're not requesting them).
3. **Does Northfield's API return tax/fee elements at all?** We can't tell from code alone since the parser ignores them. Need to inspect a raw Northfield response from MongoDB.
4. **Should broker/inspection fees always be $200 for every surplus-lines submission**, or does it vary by state / agency setup? The `_FALLBACK_PROVIDER_FEES` treats them as flat per-provider — is that the intent?

Before touching code, pull a raw sample of each carrier's response from MongoDB and confirm what the carriers actually return vs. what our parsers ignore. That confirms/denies Hypothesis vs. Data.

## Next actions

1. **Access MongoDB** (via `/mongodb` skill + read-only) to pull 1–2 recent quote documents per carrier, specifically their `raw_response` fields. Confirm what ACIC/Nationwide-CL/Northfield actually return.
2. **Identify the risk state** for the screenshot's submission — need it to validate ACIC's tax/fee numbers against state tables.
3. **Choose Option A (narrow patch) vs. Option B (centralized)** with Craig — depends on appetite for scope.
4. **Ask Rem** whether surplus-lines taxes should always match what ACIC returns (implying ACIC is source of truth) or whether there's an authoritative state tax table the app should own.
