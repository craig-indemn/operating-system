---
ask: "What UX issues were found during hands-on browser testing?"
created: 2026-03-16
workstream: gic-email-intelligence
session: 2026-03-16-b
sources:
  - type: browser-testing
    description: "Live testing at localhost:5173 with 10 sample submissions, screenshots captured"
---

# UX Testing Findings

## Issues Found & Fixed

### Board Cards (FIXED)
- **Red age badges** showing "94d" in New column — confusing because it shows time since first email, not when something needs attention. Removed entirely.
- **Agent reasoning text** leaking into cards — the LLM's stage reasoning (e.g., "Most recent email is a gic_application — submission just arrived and is unreviewed") was stored in `attention_reason` field and displayed on every card. Fixed: validate attention_reason as enum value only.
- Cards now show: name, LOB pill, agent name, relative last activity time, email count, sparkle for drafts, attention reason tag (attention column only).

### Detail View (FIXED)
- **Suggested action buried at bottom** — had to scroll past empty fields to find the one actionable element. Moved to top of right column.
- **Wall of empty dashes** — Premium: `--`, Carrier: `--`, etc. for every field with no data. Now: only fields with values are shown.
- **"No extracted data yet"** — technical jargon meaningless to end user. Removed; component returns null when no data.
- **Developer field names** — `retail_agent_name`, `coverage_limits` in missing fields list. Now: "Retail Agent Name", "Coverage Limits".
- **"Missing" → "Still needed"** — more action-oriented language.
- **"Extracted Data" → "What We Know"** — human-friendly heading.

### Email Bodies (FIXED)
- **Migrated emails had no body text** — the original extraction got empty text for HTML-only emails. Re-fetched from Graph API for sample submissions. Full batch will need same treatment.

### E2E Test Data Leak (FIXED)
- Test cleanup did `db.drafts.delete_many({})` — wiped all production drafts. Scoped to test data only.

## Issues Still Open (Next Session)

### Board Level
- Only 10 submissions — board feels empty. Need full batch to show real pipeline volume.
- "With Carrier" column is always empty (by design — manual stage). May confuse viewers. Consider hiding or explaining.
- Time filters (7d/30d/All) — with historical data, 30d only shows 4 submissions. Default may need tuning.

### Card Level
- Cards don't show what TYPE of email triggered the submission (quote? decline? application?). The email_type info is available but not surfaced.
- No visual indicator of urgency beyond the Attention column's reason tags.

### Detail View
- **Email expand affordance is poor** — tiny `>` chevron is the only indicator that clicking expands the email body. Need a more obvious "Read email" interaction.
- **Timeline with 1 email looks lonely** — huge empty space below. With full batch data (multi-email submissions), this fills up naturally.
- **Completeness ring shows generic fields** for non-GL LOBs — only GL has a specific config. Other LOBs fall back to 8 generic fields.

### Data Quality
- Some submission names are wrong (e.g., "Johnny" instead of full insured name, "Unknown (Workers Comp - Porro Insurance)") — agent classification quality varies.
- `named_insured` sometimes picks up partial names or sender names instead of the actual insured.

### General
- No loading indicator during search debounce
- WebSocket connection requires replica set — may not work on all MongoDB deployments
- The "Last synced" footer is subtle — should be more prominent if sync is stale
