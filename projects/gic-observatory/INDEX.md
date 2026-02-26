# GIC Observatory

Analytics and reporting for GIC Underwriters using the Indemn Observatory platform. GIC is the first production customer using the Observatory for web chat data analytics, with downloadable PDF reports.

## Status
**2026-02-26 (session b)**: CSR Time-of-Day activity page fully implemented, audited, and merged to main (PR #2). Backend collects CSR message timestamps from transcript parsing (reuses existing loop), buckets into 20-min intervals with UTC offset support. Frontend renders heatmap-style table in PDF. Also added "Msgs Sent" column to CSR Breakdown page. Full data audit confirmed 100% accuracy: 3,993 messages across 5 CSRs match raw MongoDB transcripts exactly.

**Next**: Deploy to prod (Vercel) and generate a final report for GIC to review. Consider whether the `utc_offset` should be stored per-org rather than derived from browser timezone.

## Critical Constraints
- **READ-ONLY MongoDB**: Production database (`MONGODB_PROD_URI`) is read-only. You do NOT have write permission. All data aggregation must happen in application code, not via MongoDB writes.
- **Observatory repo**: `/Users/home/Repositories/indemn-observability/`
- **Database**: MongoDB Atlas, `tiledesk` database
- **GIC Org**: Search by `{name: /geico|gic/i}` in `organizations` collection

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Indemn Observatory (prod) | Vercel deployment | https://indemn-observability.vercel.app |
| Observatory repo | GitHub | indemn-observability (local: `/Users/home/Repositories/indemn-observability/`) |
| MongoDB Atlas | Database | `tiledesk` database via `MONGODB_PROD_URI` env var |
| Report Library skill | OS skill | `/Users/home/Repositories/operating-system/.claude/skills/report-library/` |
| Report Generate skill | OS skill | `/Users/home/Repositories/operating-system/.claude/skills/report-generate/` |
| MongoDB skill | OS skill | `/Users/home/Repositories/operating-system/.claude/skills/mongodb/` |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-02-26 | [observatory-architecture](artifacts/2026-02-26-observatory-architecture.md) | What is the Indemn Observatory and how is it built? |
| 2026-02-26 | [customer-analytics-report](artifacts/2026-02-26-customer-analytics-report.md) | How does the current Customer Analytics PDF report work and what does it contain? |
| 2026-02-26 | [mongodb-data-model](artifacts/2026-02-26-mongodb-data-model.md) | What MongoDB collections and fields are relevant to GIC chat analytics? |
| 2026-02-26 | [pdf-generation-patterns](artifacts/2026-02-26-pdf-generation-patterns.md) | How are PDFs generated in the Observatory — both frontend and CLI? |

## Decisions
- 2026-02-26: Project created to track GIC Observatory work as a dedicated workstream
- 2026-02-26: Time-of-day distribution will use 20-minute intervals (72 buckets per 24 hours) as requested by GIC team
- 2026-02-26: Must use read-only MongoDB access — no writes to production database permitted
- 2026-02-26: Date range matches existing report scope (no separate date picker)
- 2026-02-26: Visualization is a table with inline mini-bars — CSR rows × time-bucket columns
- 2026-02-26: Metric counts individual CSR messages per 20-min window (not conversations)
- 2026-02-26: Added as a new page in the existing Customer Analytics PDF (after CSR Breakdown page)
- 2026-02-26: Transcript timestamps are UTC; added `utc_offset` query param to shift hours (browser passes local offset)
- 2026-02-26: Time bucketing reuses existing transcript parsing loop — no second API call needed
- 2026-02-26: Added "Msgs Sent" column to CSR Breakdown page to bridge conversation count and message count metrics

## Open Questions
- Should `utc_offset` be stored per-organization in the database rather than derived from the browser?
- "Coralia  Nunez" has a double-space in source data — cosmetic, but should it be cleaned up at the CSR profile level?
- 23 conversations (2.9%) have CSR engagement but no transcript messages — worth investigating the source data?
