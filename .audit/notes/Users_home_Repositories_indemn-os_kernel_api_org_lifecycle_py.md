# Notes: /Users/home/Repositories/indemn-os/kernel/api/org_lifecycle.py

**File:** /Users/home/Repositories/indemn-os/kernel/api/org_lifecycle.py
**Read:** 2026-04-16 (full file — 421 lines; read sections 1-250 and 250-421 in full)
**Category:** code

## Key Claims

- Module docstring: "Org lifecycle operations — export, import, clone, diff, deploy. Configuration-only operations. Entity instances (business data), messages, changes, sessions, attentions, and secrets are never exported or cloned."
- Functions:
  - `export_org_config(org_id)` — exports org settings + entities + rules + lookups + skills + roles + actors + integrations (excluding secrets, business data)
  - `import_org_config(target_org_name, config)` — creates new org, imports all config
  - `clone_org(source_org_id, target_org_name)` — export + import in one step
  - `diff_org_configs(org_a_id, org_b_id)` — shows differences per category
  - `deploy_org(source_org_id, target_org_id, dry_run=True)` — previews or applies changes
  - `_apply_config_item(org_id, category, name, item_data)` — updates or creates single config item

## Architectural Decisions

- **Config-only operations, matching design**: entity instances NOT exported/cloned per design.
- **Secrets excluded**: integrations exported without `secret_ref`, `last_checked_at`, `last_error`.
- **Human actors excluded**: only associate actors exported (`type: "associate"`). Matches design (human actors are per-person, not org configuration).
- **Skill content hash recomputed on import** (via `compute_content_hash`) — maintains tamper-evidence.
- Categories exported: org settings, entities, rules, lookups, skills, roles, actors (associates only), integrations, capabilities.
- Diff computes per-category: only_in_a, only_in_b, modified.
- Deploy: dry-run preview shows changes; apply mode updates target (only_in_a + modified, skips only_in_b).
- Insert-or-update pattern for each category in `_apply_config_item`.

## Layer/Location Specified

- Kernel code: `kernel/api/org_lifecycle.py`.
- Called by admin routes and CLI commands (`indemn org export/import/clone/diff/deploy`).
- Direct MongoDB access (uses `get_database()` + Beanie documents).
- Per design (2026-04-09-data-architecture-everything-is-data.md): org lifecycle is kernel-side.

**No layer deviation.**

## Dependencies Declared

- `bson.ObjectId`
- `datetime`, `timezone`
- `kernel.db.get_database`
- `kernel.entity.definition.EntityDefinition`
- `kernel.rule.lookup.Lookup`, `kernel.rule.schema.Rule`
- `kernel.skill.schema.Skill`
- `kernel.skill.integrity.compute_content_hash`
- `kernel_entities.Organization`

## Code Locations Specified

- This file: `/Users/home/Repositories/indemn-os/kernel/api/org_lifecycle.py`
- Called by: `kernel/api/admin_routes.py`, `kernel/cli/org_commands.py`

## Cross-References

- Design: 2026-04-09-data-architecture-everything-is-data.md §"Environments = Orgs"
- Phase 6-7 spec §7.4 Org Export/Import Format
- Comprehensive audit §"Org Lifecycle — COMPLETE" confirms implementation

## Open Questions or Ambiguities

**No Pass 2 layer deviation.**

**Secondary observations:**
- The exclusion list for each category (what gets stripped during export) is hardcoded per category. Works for MVP but could be moved to metadata on the entity schemas.
- Archive/deprecated items are filtered at export (rules with status != archived, skills with status != deprecated).
- Integrations exported without credentials — credential rotation/setup remains a separate flow on import.
- `deploy_org` doesn't remove items only in target (only_in_b) — safe default, but users may want an opt-in "strict deploy" mode.
- Version increment on existing records during import — preserves version tracking.
- No Temporal workflow for deploy (spec mentions saga-compensated deployments but this is a simple sequential implementation). Acceptable for MVP.

**Per comprehensive audit**: "Export (YAML directory: entities/, roles/, rules/{entity}/, skills/*.md, lookups/, actors/, integrations/, capabilities/) — IMPLEMENTED". This file produces a nested dict, not YAML files directly. The YAML-directory format is likely handled by the CLI command (`kernel/cli/org_commands.py`), which calls this module's functions and then writes YAML to disk.

Org lifecycle is correctly placed kernel-side and matches design intent. No architectural concerns.
