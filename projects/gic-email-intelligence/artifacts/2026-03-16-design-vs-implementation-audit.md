---
ask: "Review the entire implementation against the design — where are we matching and where are we not?"
created: 2026-03-16
workstream: gic-email-intelligence
session: 2026-03-16-b
sources:
  - type: code-review
    description: "Section-by-section comparison of technical design (1,527 lines) against implementation (98 files, 11,828 LOC)"
---

# Design vs Implementation Audit

## Summary

13 of 16 design sections fully match. 3 are partial. 13 actionable gaps identified — 3 high priority, 5 medium, 5 low.

## Section-by-Section

### Section 1: System Overview — MATCH
All architectural layers present. No gaps.

### Section 2: Architecture — MATCH
Three layers (Frontend/API/Core), CLI-first, agent-as-brain pattern. Tools call core DB directly instead of subprocess — deviation from design but objectively better.

### Section 3: Lifecycle Stages — MATCH
All 5 stages, 4 attention reasons, 13 email types present in enums. Stage mapping encoded in agent skills.

### Section 4: Submission Linking — MATCH (with minor gaps)
- USLI prefix-to-LOB mapping: all 23 prefixes present
- Fuzzy matching with ambiguity detection: implemented
- **Gap G1**: Fuzzy match missing ±90 day time-window and same-LOB filter
- **Gap G2**: `detect-duplicates` CLI displays results but doesn't write `potential_duplicate_of` to the submission
- **Gap G3**: Duplicate detection threshold 80% vs design's 75%

### Section 5: Data Model — MATCH (with minor gap)
All 5 collections match exactly. All fields, all indexes.
- **Gap G4**: Missing `classification.named_insured` text index from `indexes.py`

### Section 6: CLI Design — MATCH
All commands present. Cosmetic name differences (`classify` vs `save-classification`, `link` vs `link-email`, `stage` vs `update-stage`). Functionality identical.

### Section 7: Agent Harness + Skills — MATCH (with gaps)
Harness, 5 skills, structured tools, orchestration all present.
- **Gap G5**: `--workers` concurrency not implemented (batch is serial)
- **Gap G6**: Missing `--skip-linking` and `--only-drafts` agent CLI flags

### Section 8: Ingestion Layer — MATCH
Graph API client, token management, pagination, folder resolution, rate limiting, dedup, S3 attachments all match.

### Section 9: Backend API — PARTIAL
All 9 endpoints present. Auth, CORS, search, board response shape, detail response shape match.
- **Gap G7**: WebSocket only watches `emails` collection — missing `submissions` and `drafts` watchers → `stage_change`, `draft_ready`, `stats_update`, `sync_status` events never fire
- **Gap G8**: No API rate limiting middleware (design specifies 100 req/min per IP)
- **Gap G9**: Health check missing `last_processed_at` in agent section

### Section 10: Frontend — MATCH (with UX gaps)
Board view, submission cards, search, detail view, timeline, extracted data, completeness ring, draft card all present.
- **Gap G10**: Detail view is full-page navigation, not slide-in overlay from right (design: 200ms slide-in)
- **Gap G11**: Notification counts display but are not clickable/filterable
- **Gap G12**: No per-field source indicators in extracted data (only section-level "PDF" chips)
- Note: field-to-timeline click highlighting is a stretch — not critical for demo

### Section 11: LOB Requirements — PARTIAL
- **Gap G13**: `gl.json` exists at `agent/lob_configs/gl.json` but is never loaded. Completeness calculation uses hardcoded generic 8-field list instead of LOB-specific config with `required_fields` + `required_documents`.

### Section 12: Deployment — MATCH
Dockerfile, supervisord, env vars, health check all match.

### Section 13: Security — PARTIAL
- **Gap G8** (same as above): No API rate limiting

### Section 15: Testing — PARTIAL
- **Gap G14**: No E2E pipeline test (design: seed 10 emails, run pipeline, assert everything)
- **Gap G15**: No ground-truth skill tests against `all_classifications.json`/`all_vision_results.json`
- **Gap G16**: Minimal API integration tests (1 test in `test_api.py`)

## Gap Priority

| Gap | Description | Priority | Impact |
|-----|-------------|----------|--------|
| G7 | WebSocket missing submissions/drafts watchers | High | Live updates broken for stage changes, drafts |
| G13 | LOB config not loaded, generic completeness | High | Completeness ring shows wrong data per LOB |
| G10 | Detail is full-page nav, not slide-in overlay | High | UX doesn't match design, less polished |
| G1 | Fuzzy match missing time-window + LOB filter | Medium | Could link unrelated submissions |
| G2 | detect-duplicates doesn't write potential_duplicate_of | Medium | Duplicate detection is display-only |
| G4 | Missing named_insured text index | Medium | Search performance on large datasets |
| G5 | --workers concurrency not implemented | Medium | Slow batch processing (serial only) |
| G8 | No API rate limiting | Medium | Security gap |
| G11 | Notification counts not clickable | Low | Minor UX polish |
| G12 | No per-field source indicators | Low | Minor UX polish |
| G6 | Missing --skip-linking/--only-drafts flags | Low | Agent CLI convenience |
| G9 | Health missing last_processed_at | Low | Monitoring detail |
| G3 | Duplicate threshold 80% vs 75% | Low | Tuning parameter |
| G14-16 | Test coverage gaps | Low | Quality, not demo-blocking |
