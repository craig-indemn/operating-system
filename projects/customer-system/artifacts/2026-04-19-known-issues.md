---
ask: "Document known issues from initial customer system build for follow-up"
created: 2026-04-19
workstream: customer-system
session: 2026-04-19-a
sources:
  - type: codebase
    ref: "/Users/home/Repositories/indemn-os"
    description: "Issues discovered during Phase A-E execution"
---

# Known Issues — Customer System Build

## Kernel Bugs (Fixed, Deployed)

1. **CLI trailing slash auth loss** — httpx dropped Authorization headers on 307 redirects because Railway's proxy changes scheme (https->http->https). Fixed by adding trailing slashes to 14 collection-level API paths. Commit: `437c367`. Additional paths in `entity_commands.py` and `bulk_monitor.py` caught in code review and fixed. Commit: `dd476a9`.

2. **Decimal serialization (insert path)** — `save_tracked()` insert used `model_dump()` which preserves Python `Decimal` objects that pymongo can't serialize to BSON. Added `_convert_decimals()` recursive converter in `_serialize_entity()`. Commit: `01b9872`.

3. **Decimal serialization (update path)** — Update path used raw `model_dump()` instead of `_serialize_entity()`. Same BSON error on any transition or update of entities with decimal fields. Fixed to use `_serialize_entity()` consistently. Commit: `238f33a`.

3b. **Decimal import in recursive function** — `_convert_decimals()` had `from decimal import Decimal` inside the function body, re-importing on every recursive call. Moved to module level. Commit: `dd476a9`.

## Kernel Bugs (Open)

4. **Bulk-create via Temporal needs org_id** — The `BulkExecuteWorkflow` receives a spec dict but the Temporal worker doesn't have org_id context (set by API middleware via contextvars). The `process_bulk_batch` activity calls `current_org_id.get()` which returns None. Fix: include org_id in the spec at the API layer and use it in the activity. Workaround: individual creates work fine.

5. **Bulk-create CSV type coercion** — CSV values arrive as strings. The entity constructor may not coerce them properly (e.g., "0.05" as string vs Decimal, "14" as string vs int). Needs type coercion in the bulk activity based on entity field definitions.

6. **CLI `--from-csv` sent file path to remote API** — Fixed in CLI (`f2359c8`) to read CSV locally and send parsed rows as `source_data`. But the Temporal side still has the org_id issue (#4).

7. **Company collection name is `companys`** — Auto-pluralization just appends 's'. Should be `companies`. Cosmetic — doesn't affect functionality. Would need a schema migration to fix.

8. **`actor list --type` filter maps to `status` param** — In `actor_commands.py` line 96, the `--type` CLI flag was passed as `status` parameter to the API. Fixed to pass as `type`. Commit: `dd476a9`.

## Data Quality Notes

9. **Contact `how_met` values needed mapping** — CSV had 20+ granular values (Brella Scan, Business Card, ALER26, etc.) not in the defined enum. Mapped to closest valid enum during import; original values preserved in notes where no mapping was obvious.

10. **Company `icp_fit` had "N/A" values** — 4 companies had "N/A" which isn't a valid enum value. Stripped during import.

## Deferred Items

11. **Watches not yet configured** — Phase F from the handoff. No watches on any role → no messages generated on entity changes → trace shows 0 messages. This is expected until automation design.

12. **Conference transitions need name-based lookup** — CLI transition requires ObjectId, but users think in names. Need either name-based transition support or a lookup helper.
