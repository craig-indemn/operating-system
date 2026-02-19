---
ask: "Check how many BAUT CHG3 activities are available in the demo environment before burning any on testing"
created: 2026-02-19
workstream: web-operator
session: 2026-02-19-a
sources:
  - type: web
    description: "Logged into Applied Epic demo (johns87.appliedepic.com), read full activities list via agent-browser"
---

# Demo Environment Activity Inventory

## Summary

18 total activities assigned to Indemn AI. 4 are BAUT (CAP endorsements) — our target for the Monday demo.

## Breakdown by Type

| Type | Count | Policy Type |
|------|-------|-------------|
| **BAUT** | **4** | Commercial Auto (CAP) — endorsement verification target |
| FARM | 7 | Farmowners Policy |
| AGPK | 6 | Agribusiness |
| Other | 1 | Terry Wilson — "Policy Documents" (no type keyword) |

## The 4 BAUT Activities (in list order)

| Index | Account | Change Description | Last Updated |
|-------|---------|-------------------|--------------|
| 0 | Thanh Tran & Thuy Vu | Add 2025 Lexus NX450 | 2/18/2026 (very recent) |
| 1 | Paul & Tammy Fergerson | Remove the 1978 Ford F150 | 2/5/2026 |
| 2 | Christopher & Kim Echerd | Remove 2009 Honda Civic | 2/5/2026 |
| 3 | Kai Tung Leo Wong & Yi Qing Huang | Lowering coverage of 2005 Dodge Dakota and 2013 Audi Q5 to liab only | 2/5/2026 |

## Endorsement Type Variety

The 4 activities represent three different endorsement types:
- **Vehicle addition** (#0 — add Lexus)
- **Vehicle removal** (#1, #2 — remove Ford F150, remove Honda Civic)
- **Coverage change** (#3 — lower coverage to liability only)

This is good for testing path flexibility — the path must handle all three types.

## Key Observations

1. **Dry Ridge Farm, LLC is NOT in the list** — MaeLena's "correct submission" example from the endorsement guide. Either already processed by Rudra during testing, or under a different view/filter.
2. **Bill Kistler is NOT in the list** — MaeLena's intentional error case (4 errors). Same possibility — may have been consumed during Rudra's testing.
3. **Activity #0 (Thanh Tran) was updated 2/18/2026** — the same day as Rudra's latest commits. Likely touched during his testing but not fully processed (still in the list).
4. **No POL3 activities visible** — the renewal activities MaeLena added may require a different activity view/filter to see.

## Testing Strategy

**Use for testing (expendable):**
- Activity #1 (Fergerson — remove Ford F150) — simple vehicle removal
- Activity #2 (Echerd — remove Honda Civic) — simple vehicle removal

**Save for Monday demo:**
- Activity #0 (Thanh Tran — add Lexus NX450) — vehicle addition, freshest data
- Activity #3 (Wong/Huang — lower coverage to liab only) — coverage change, shows versatility

**Testing approach:** Walk through Steps 1-5 (non-destructive) on a test activity. Stop before Step 6 (premium update), Step 7 (issue), and Step 8 (close/reassign) to preserve the activity for re-testing or demo use.
