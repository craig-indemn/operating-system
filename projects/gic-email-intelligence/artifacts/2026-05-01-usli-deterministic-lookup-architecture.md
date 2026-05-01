---
ask: "Lock the deterministic Quote-lookup architecture for the USLI quote automation. Replace the original design's name-search-as-primary + ambiguous-folder-as-daily-fallback model with a three-tier lookup that builds the deterministic key on our side and closes the loop by stamping it back into Unisoft. This is B.5 of the implementation plan, repurposed from a JC ask into an architectural spec."
created: 2026-05-01
workstream: gic-email-intelligence
session: 2026-05-01-deterministic-lookup
sources:
  - type: experiment
    description: "Empirical inspection 2026-05-01 of 7 real USLI-linked Quotes in prod Unisoft. Every Quote.ConfirmationNumber, Quote.Source, Quote.PolicyNumber, Submission.ConfirmationNo (CarrierNo=2) returned null. Confirmed Unisoft has zero record of USLI refs today."
  - type: mongodb
    description: "Live query of gic_email_intelligence.submissions on prod cluster. 5 of 7 linked submissions have multiple distinct USLI refs in reference_numbers (e.g., IGLESIA TABERNACULO has 5 refs against 1 Quote), confirming name-search alone produces ambiguous results in real data."
  - type: codebase
    description: "Reviewed src/gic_email_intel/agent/skills/submission_linker.md and the linker behavior — confirmed it deduplicates on insured-name fuzzy match with same-LOB + 90d window, so multiple USLI refs for the same insured naturally land on one submission record."
  - type: artifact
    description: "Builds on 2026-05-01-unisoft-quote-search-canonical-shape.md (the name-search wire format) — that artifact gave us a working name-search; this artifact specifies how to use it in a deterministic lookup."
---

# USLI Quote Automation — Deterministic Lookup Architecture

## Why this exists

The original design (`2026-04-29-usli-quote-automation-design.md` § "One skill, branched on lookup") assumed:

1. Name-search would be the primary lookup mechanism for finding the right Unisoft Quote when a USLI quote-response email arrives.
2. Ambiguous matches (>1 Quote returned) would route to a new `Indemn USLI Needs Review` folder for JC to triage.
3. Stamping the USLI ref on `Quote.ConfirmationNumber` was an "upgrade-only optimization" deferred to post-launch (K.5).

Two empirical findings from 2026-05-01 invalidated that:

- **The USLI ref is not stored anywhere on the Unisoft side today.** Inspection of 7 real USLI-linked Quotes: every candidate field (`Quote.ConfirmationNumber`, `Quote.Source`, `Quote.OriginatingSystem`, `Quote.PolicyNumber`, `Submission.ConfirmationNo` for CarrierNo=2) is null. JC's broker workflow doesn't stamp it; USLI Retail Web's auto-quote integration doesn't write it back.
- **Name-search alone produces ambiguous results in real prod data.** "IGLESIA TABERNACULO" has 5 distinct USLI refs against a single Mongo submission. "Blanca A Benitez" has 2. Same insured + same agent + multiple time-spaced re-quotes is the norm, not the exception. Defaulting to "ambiguous folder" for these would push 30–50% of daily volume to manual triage.

The corrective architecture: build a deterministic key on our side, stamp it into Unisoft on every write, close the loop so future lookups are instant.

## Three-tier lookup algorithm

```
Input: usli_ref (e.g., "MGL026A6ER4"), insured_name, agent_no, lob

┌─────────────────────────────────────────────────────────────────┐
│ Tier 1 — Mongo lookup by USLI ref                              │
│                                                                 │
│ db.submissions.find_one({                                       │
│   "reference_numbers": usli_ref,                                │
│   "unisoft_quote_id": {"$ne": None}                             │
│ })                                                              │
│                                                                 │
│ → 1 hit:  return quote_id (deterministic, instant). DONE.       │
│ → 0 hits: continue to Tier 2.                                   │
│ → >1 hits: linker bug (same ref on multiple records). Use       │
│            highest unisoft_quote_id, log a warning.             │
└─────────────────────────────────────────────────────────────────┘
                                    │ 0 hits
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Tier 2 — Unisoft search via GetQuotesForLookupByCriteria        │
│                                                                 │
│ Build canonical Criteria (per                                   │
│ 2026-05-01-unisoft-quote-search-canonical-shape.md):            │
│   - Criteria.Name = insured_name                                │
│   - Criteria.AgentNo = agent_no (resolved from email)           │
│   - Criteria.WordLookupType = "Contains"                        │
│   - Criteria.StatusId = 1 (active only)                         │
│   - Top-level: PageNumber=1, ItemsPerPage=20, IsNewSystem=false │
│                                                                 │
│ Post-filter results client-side:                                │
│   - LastActivityDate within last 60 days                        │
│   - LOB matches LOB inferred from usli_ref prefix               │
│     (MGL→CG, MPL→CP, MSE→Special Events, NPP→CG, XSL→CU, ...)  │
│                                                                 │
│ → 1 hit after filter: return quote_id. Run BACKFILL.            │
│ → 0 hits: caller goes to Path 2 (create new Quote).             │
│ → >1 hits even after LOB+date+agent filter:                     │
│     → fall back to "highest QuoteId" tiebreak. USLI re-quotes   │
│       use new IDs and the latest is canonical >99% of the time. │
│     → Log the tiebreak (so soak surfaces any false-positives).  │
│     → Run BACKFILL on the chosen Quote.                         │
└─────────────────────────────────────────────────────────────────┘
                                    │ 0 hits
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Tier 3 — Path 2 create                                          │
│                                                                 │
│ unisoft quote create + unisoft submission create                │
│   --confirmation-no <usli_ref>  ← stamp at creation             │
│ Then proceed with attachment uploads + activity firing.         │
└─────────────────────────────────────────────────────────────────┘
```

### Backfill (the loop closure)

Whenever Tier 2 succeeds (or Tier 3 creates a new record), two writes happen:

**Mongo backfill:** if Tier 2 found a match, set `unisoft_quote_id` on the linked Mongo submission so the next lookup hits Tier 1.

```python
db.submissions.update_one(
    {"_id": submission_oid},
    {"$set": {"unisoft_quote_id": quote_id, "unisoft_quote_id_source": "tier_2_name_search"}},
)
```

**Unisoft stamping:** call `unisoft submission update --submission-id N --confirmation-no <usli_ref>` (C.3, already shipped) on the matched USLI Submission. After this write, the Unisoft side ALSO has the link — meaning if Mongo is ever rebuilt, name-search-with-filter still finds the same Quote (because we can post-filter by `Submission.ConfirmationNo == ref` in future iterations).

For Tier 3 creates: the new Submission is created with `--confirmation-no <usli_ref>` already populated (C.2 shipped this flag).

### Why the loop closure matters

Within ~2 weeks of running, the active USLI Submission inventory has `ConfirmationNo` populated for everything we've touched. From that point forward:

- Every quote re-quote (USLI sending a new ref against the same insured) hits Tier 1 instantly.
- The historical "ambiguous match" cases collapse — even if there are 3 active Quotes for the same insured, the rebuilt index distinguishes them by the per-ref link.
- A future "K.5" optimization (server-side ref-search via `Submission.ConfirmationNo == ref` filter, if Unisoft adds it to QuoteSearchCriteria) becomes a free upgrade — the data is already there.

## Concrete frequency claim

The original design predicted ambiguous matches as "daily handling, route to Needs Review folder."

Under the new architecture:
- **First contact** with an insured: Tier 2 runs. If exactly one active Quote for that agent + LOB + recency exists, deterministic. Genuinely ambiguous in <5% of first-contact cases.
- **Re-quote contact** (same insured, new USLI ref): Tier 1 hits. Deterministic always.
- **Mature steady state** (≥2 weeks in): >95% of incoming USLI quote emails go through Tier 1. Tier 2 ambiguity is <1% of overall volume.

`Indemn USLI Needs Review` becomes a real edge-case backstop — expected ≤2 emails per month, not per day. Threshold for soak validation (G.3) is the inverse: anything higher signals an algorithm bug, not a real ambiguity.

## Mongo schema

No new collection required. The existing `submissions` collection has:

| Field | Type | Source | Use |
|---|---|---|---|
| `_id` | ObjectId | Mongo | identity |
| `named_insured` | string | linker | Tier 2 input |
| `reference_numbers` | array<string> | linker (extracted from email subject/body) | Tier 1 lookup key |
| `unisoft_quote_id` | int? | this architecture (Tier 2 backfill or Tier 3 create) | Tier 1 returned value |
| `unisoft_submission_id` | int? | C.3 update + C.2 create | Used downstream by activity binding |
| `intake_channel` | string | linker | Tier 2 disambiguation aid |
| `retail_agent_email` | string | linker | Agent resolution |

**Index added by this architecture:** `submissions.reference_numbers` (multi-key index — Mongo handles arrays natively).

```javascript
db.submissions.createIndex({"reference_numbers": 1, "unisoft_quote_id": 1});
```

This is the only schema change required. No new collection, no migration.

## CLI surface — the deterministic-lookup primitive

A new helper `find_quote_for_usli_ref()` in `src/gic_email_intel/automation/usli_helpers.py`. Exposed via a thin CLI wrapper `gic submissions find-quote-for-usli`:

```bash
gic submissions find-quote-for-usli \
    --usli-ref MGL026A6ER4 \
    --insured "Las Marias Properties LLC" \
    --agent-no 7406 \
    --lob CG \
    [--mongo-only]   # optional: skip Tier 2/3, return null if Tier 1 misses
```

Output (JSON):
```json
{
  "state": "found" | "ambiguous" | "create_new",
  "quote_id": 17129 | null,
  "lookup_path": "tier_1_mongo" | "tier_2_name_search" | "tier_3_create_new",
  "candidates": [...],   // populated only when state=="ambiguous" with the >1 candidates
  "tiebreak_applied": "highest_quote_id" | null,
  "backfill_applied": {"mongo": true, "unisoft": true} | null
}
```

The D.2 skill (`process-usli-quote.md`) calls this once and branches on `state` — no lookup logic in skill prose. This means the LLM's only judgment-call surface is reading the email, not navigating the lookup algorithm.

## Failure modes & routing

| Outcome | Folder | Activity? | Email? | Notes |
|---|---|---|---|---|
| Tier 1 hit, 1 Quote → process normally | `Indemn USLI Processed` | yes | yes | The fast path. >95% steady-state volume. |
| Tier 2 hit (1 after filter) → backfill + process | `Indemn USLI Processed` | yes | yes | First-contact path. |
| Tier 2 ambiguous, tiebreak applied | `Indemn USLI Processed` | yes | yes | Logged for soak review; if tiebreak proves wrong in soak, tighten filters. |
| Tier 3 create (no match anywhere) → Path 2 create | `Indemn USLI Processed` | yes | yes | USLI Retail Web auto-quote, dominant Path 2 case. |
| Mongo Tier 1 returns >1 (linker bug) → use highest quote_id | `Indemn USLI Processed` | yes | yes | Log warning; surface in soak metrics. |
| Tier 3 create fails (e.g., agency not in Unisoft) | `Inbox` | no | no | `automation_status=failed`, manual handling. |
| Activity creation fails after Submission created | `Inbox` | no — partial | no | Same as today's agent_submission failure mode. |
| Email send fails after activity created | `Inbox` | yes | no — partial | Same as today's agent_submission failure mode. |

The `Indemn USLI Needs Review` folder, originally the "ambiguous match" daily destination, is **deleted from this architecture**. Tier 2 ambiguity uses tiebreak; Tier 1 ambiguity is a linker bug that gets logged. There's no normal-flow case that routes to a Needs Review folder.

## Soak metrics — revised G.3 thresholds

Under name-search-only the design tracked an "ambiguous-match rate" with a 5% threshold. Under deterministic lookup, the metrics tighten and shift:

| Metric | Threshold (soak) | Threshold (steady-state) | Source |
|---|---|---|---|
| Successful end-to-end runs | ≥ 10 distinct usli_quote emails | n/a | unchanged from plan |
| Tier 1 hit rate (% of emails) | ≥ 0% (start) | ≥ 95% (≥ 2 weeks) | new |
| Tier 2 ambiguous-tiebreak rate | < 5% | < 1% | replaces "ambiguous-match rate" |
| Stamping success rate (every Submission ends with non-null ConfirmationNo) | = 100% | = 100% | new — non-negotiable |
| Customer-copy uploads to Unisoft | = 0 | = 0 | unchanged (whitelist policy from B.3) |
| Notification template empty/unrendered | = 0 | = 0 | unchanged |
| Stale-claim recovery activations | = 0 | = 0 | unchanged |

A failure on stamping success is a hard stop — every USLI Submission we touch MUST end with `ConfirmationNo` set, otherwise the loop-closure breaks and the architecture degrades back to name-search-with-tiebreak.

## What this replaces in the original design + plan

- **Replaces:** § "One skill, branched on lookup" diagram in `2026-04-29-usli-quote-automation-design.md` (the simple `0/1/>1 hits` flowchart).
- **Replaces:** B.5 implementation-plan task ("Confirm with JC — ambiguous-match folder"). New B.5 is "lock the deterministic-lookup architecture" — this artifact IS that lock.
- **Supersedes:** K.5 ("Exact-match Quote lookup IF B.2 found a real ref field") — empirically B.2 found that no field exists; the equivalent capability is built into Tier 1 v1 instead of deferred.
- **Adds:** C.7 task for the `find_quote_for_usli_ref()` helper + CLI shim (new task, not in original plan).
- **Modifies:** D.2 skill to call the deterministic-lookup CLI rather than embedding the algorithm in skill prose.
- **Modifies:** G.3 metrics per the table above.
- **Removes:** the `Indemn USLI Needs Review` Outlook folder. Phase E.1's task to add it is dropped; only the existing folder constants (`INDEM_USLI_PROCESSED`) remain.

## Open questions that this artifact does NOT resolve

- **LOB-prefix → Unisoft-LOB mapping table.** USLI ref prefixes (MGL, MPL, MSE, NPP, XSL, ...) need to map to Unisoft LOB codes (CG, CP, ...) for Tier 2's LOB filter. This is stable data but not yet codified in the fixture. Captured as a TODO in C.7's implementation; the helper accepts a `--lob` argument and the skill's Step 2 figures out the LOB before calling.
- **Tiebreak strategy validation.** "Highest QuoteId" is the reasoning; the soak (G.3) needs to surface any case where tiebreak picks the wrong Quote. If observed, refine the filter (e.g., narrow date window from 60d to 30d, or filter by SubLOB).
- **Migration of historical USLI submissions.** ~7 known historical linkages exist in Mongo today. K.8 (new task, not in original K) is a one-shot script to backfill `Submission.ConfirmationNo` in Unisoft for those 7 records so the inventory is complete from day one.

These are intentionally out of scope for v1; deferred to soak observation.
