---
ask: "Map the three UG-adjacent repos and identify which owns the comparative rater, fee calculation, validation, and carrier integrations — foundation for systematic bug investigation"
created: 2026-04-17
workstream: union-general-intake-manager
session: 2026-04-17-a
sources:
  - type: github
    description: "gh api browse of indemn-ai/intake-manager, ug-apis, ug-service (root dir + app structure + README)"
  - type: github
    description: "gh repo clone (shallow, depth=1) of all three repos to /tmp/ug-recon for grep access"
  - type: github
    description: "Code reads — quote_service.py (first 346 lines), provider registry, base provider dataclass"
---

# UG Repo Mapping

Three related repos. Only one owns the rater.

## intake-manager — the UG Portal (main product)

**Stack:** FastAPI backend + Next.js frontend, MongoDB, Python 3.11+ (uv)
**What it does:** The full UG Portal — email ingest, document extraction, AI pipeline, form rendering, comparative rater, submission management
**Where the bugs live:** This is where all three of Ben's issues surface.

Key dirs under `app/`:
- `services/quote/` — quote orchestration and per-carrier provider code **← FEE CALC BUG #3**
  - `quote_service.py` — dispatcher + fee injection logic
  - `providers/acic/`, `providers/northfield/`, `providers/nationwide/` — per-carrier integrations (with `xml_builder.py` + `xml_parser.py` each)
  - **No `providers/scottsdale/`** — Scottsdale (SIC) is actually a Nationwide E&S subsidiary and quotes through the `nationwide/cl/` path
  - `normalizers/` — only `acic_normalizer.py` and `northfield_normalizer.py` (Nationwide has its own `nationwide/normalizer.py` inside the provider)
- `services/validation/` — form-level rule validation **← FALSE-POSITIVE BUG #2 likely here**
  - `json_rule_validator.py` — the validator engine
  - Per-product JSON rule files: `general_liability.json`, `nationwide_ho.json`, `nationwide_df.json`, `northland.json`
  - `field_labels.py` + `pl_field_aliases.py` — field alias mapping (a likely false-positive source if aliases get out of sync)
  - `parameter_violation_mapper_service.py` at service root maps raw violations to user-facing messages
- `services/submission_service.py` + `routers/submissions.py` + `pipeline/` + `pipeline_v2/` **← OLDER-SUB FAILURE BUG #1**
  - Pipeline has two generations (`pipeline/` and `pipeline_v2/`) — submissions may be stuck on old path
  - `pipeline/error_classifier.py` + `pipeline/retry_worker.py` — retry logic for failed subs
- `frontend/components/quote/quote-compare-view.tsx` — renders the screenshot Ben sent

## ug-apis — Nationwide API wrapper (carrier-specific middleware)

**Stack:** FastAPI, Python, minimal
**What it does:** Normalized API layer over Nationwide E&S/Specialty Insurance — covers Personal Lines (HO3/HO4/HO5/HO6, DP1/DP2/DP3) and Commercial Lines (Excess, Package — GL + Property + OCP + Inland Marine + Crime). From `main.py`:
> `# Main FastAPI application - Nationwide API Integration`
> `title="Nationwide Insurance API"`
**Relation to intake-manager:** intake-manager's `providers/nationwide/` calls into this service. Scottsdale quotes route through here via the Commercial Lines path.
**Not directly involved in the bugs** unless the Nationwide CL response is the source of the missing broker/inspection fees for Scottsdale (unlikely — those are injected before the call, not returned from Nationwide).

## ug-service — thin record-upsert glue

**Stack:** Express.js (Node), MongoDB, dd-trace, minimal
**What it does:** Single route `GET /api/record` that takes a recordId + status + arbitrary query params, parses JSON blobs from query values, and upserts to MongoDB. Returns a simple "Data Sent" HTML page with a 1.5s auto-close script that says "Record X was sent to AA for surface automation pickup." ("AA" is likely Automation Anywhere — RPA triggered from this hand-off.)
**Relation to intake-manager:** Likely the hand-off path from intake-manager to downstream RPA automation. Not directly involved in any of the three bugs.

## Summary: which repo owns each bug

| Bug | Owning repo | Key files to read |
|-----|-------------|-------------------|
| #1 Older submissions still fail | intake-manager | `app/services/submission_service.py`, `app/services/pipeline/retry_worker.py`, `app/services/pipeline/error_classifier.py`, `app/services/pipeline_v2/` |
| #2 False-positive validation violations | intake-manager | `app/services/validation/json_rule_validator.py`, `app/services/parameter_violation_mapper_service.py`, `app/services/validation/*.json`, `app/services/validation/field_labels.py`, `app/services/validation/pl_field_aliases.py` |
| #3 Fee-calc inconsistency across carriers | intake-manager | `app/services/quote/quote_service.py` (dispatcher + fee injection), `providers/acic/xml_parser.py` (surplus-lines extraction), `providers/northfield/xml_parser.py`, `providers/nationwide/normalizer.py`, `providers/nationwide/cl/provider.py` |

## Carrier routing confirmed

- **ACIC** = Atlantic Casualty — dedicated provider, own XML parser, extracts surplus-lines taxes/fees directly from carrier response
- **Scottsdale (SIC)** = Nationwide E&S subsidiary — routes through `providers/nationwide/cl/` via ug-apis, labeled "Scottsdale" in frontend
- **Northfield** — dedicated provider, own XML parser
- **Nationwide PL** (not in screenshot) — residential (HO/DP) quoting through `providers/nationwide/pl/`
