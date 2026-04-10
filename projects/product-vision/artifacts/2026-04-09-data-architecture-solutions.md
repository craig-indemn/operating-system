---
ask: "How do we address all 14 findings from the data architecture review while maintaining simplicity?"
created: 2026-04-09
workstream: product-vision
session: 2026-04-08-a
sources:
  - type: conversation
    description: "Craig and Claude working through all 14 findings, simplifying where possible"
  - type: artifact
    description: "2026-04-09-data-architecture-review-findings.md"
---

# Data Architecture Solutions — All 14 Findings Addressed

## #1: Org Isolation — OrgScopedCollection Wrapper

All application code accesses MongoDB through a wrapper that ALWAYS injects org_id. Nobody has access to the raw Motor collection.

```python
class OrgScopedCollection:
    def __init__(self, collection, org_id):
        self._collection = collection
        self._org_id = org_id
    
    async def find(self, filter=None, *args, **kwargs):
        filter = filter or {}
        filter["org_id"] = self._org_id
        return self._collection.find(filter, *args, **kwargs)
    
    # Same for find_one, update_one, delete_one, aggregate...
```

The entity framework, kernel capabilities, CLI commands — everything uses OrgScopedCollection. The raw Motor client is hidden inside kernel initialization. A developer CAN'T write an unscoped query because they never touch the raw collection.

Cross-org queries (platform admin): separate `PlatformCollection` accessor, only available to platform-admin role.

Plus: automated cross-tenant isolation tests in CI — two test orgs, every query path verified.

## #2: Per-Org Secrets — AWS Secrets Manager

Per-org secrets (OAuth tokens, carrier API keys) live in AWS Secrets Manager (already in use). Integration entities store a `secret_ref`, not the actual credentials.

```bash
indemn integration set-credentials INT-001 --credentials-from-file @creds.json
# Writes to AWS Secrets Manager, stores ref on Integration entity

indemn integration rotate-credentials INT-001
# Rotates in Secrets Manager, updates ref
```

The entity framework never sees credentials. Only the kernel's adapter resolution code reads from Secrets Manager using the integration's secret_ref. Credentials never flow through entity queries, CLI output, or API responses.

## #3: Skill Injection — Content Hashing + File-Based Updates + Version Approval

Skills are updated via file push:

```bash
# Write/edit the skill locally, then push
indemn skill update email-classification --from-file ./email-classification.md
```

On update:
1. Content hash computed and stored with the new version
2. New version created in `pending_review` status (if approval required for this org)
3. Active version continues to be used until new version approved

```bash
indemn skill approve email-classification --version 3
# Activates version 3

indemn skill rollback email-classification --to-version 2
# Reactivates version 2
```

On load (when associate reads skill):
- Content hash verified. If modified directly in MongoDB (bypassing CLI), hash doesn't match → skill rejected.

Associates can NEVER modify skills. Skill write permission is admin/FDE only.

## #4: Rule Action Injection — Validation at Creation Time

The `indemn rule create` command validates:
1. Every field in `--sets` exists in the target entity's schema
2. The creating actor's role has write permission for those fields
3. State machine fields (status, stage) are REJECTED — transitions must go through `transition_to()`

```
Error: Cannot set field "stage" via rule action.
State transitions must go through the entity's transition mechanism.
```

## #5: Sandbox Security — Daytona Configuration

The sandbox contract (enforced by Daytona):
- No outbound network except through `indemn` CLI
- No environment variable access — credentials injected via read-only CLI config
- No filesystem access outside `/workspace`
- No shell metacharacters — `execute()` uses `subprocess.run(args_list)`, never `shell=True`
- Resource limits (CPU, memory, disk, time) — configurable per associate

## #6: Tamper-Evident Audit Trail — Append-Only + Hash Chain

Two measures:
1. MongoDB application user has `insert` permission on changes collection. Not `update`. Not `delete`.
2. Each change record includes `previous_hash` — SHA-256 of the previous record. Tampering breaks the chain.

```bash
indemn audit verify --org gic
# "4,721 records verified. Chain intact."
```

## #7: Environment Isolation — Already Addressed

Indemn already has separate dev and prod Atlas clusters. The `deploy` command operates across clusters (reads from staging cluster, writes to prod cluster). No additional work needed.

## #8: Dynamic Entity Class Limitations — Accept and Design Around

| Limitation | Approach |
|---|---|
| Circular relationships | Two-pass resolution at class creation. Documented. |
| Index validation | Validate field names against schema at entity creation time |
| Pre/post save hooks | Kernel capabilities provide hooks, wired at class creation |
| Computed fields | `map_from` (declarative mapping) for MVP. Complex = kernel capability |
| No IDE autocomplete | Accepted. CLI/skills are the interface. |
| No static type checking | Runtime validation in entity creation CLI. Capabilities tested with dynamic entities. |

## #9: API Server Entity Resolution — Beanie for Everything, Restart on Type Changes

Entity type creation/modification is an administrative operation. When it happens, the system does a rolling restart of the API server and Temporal Workers (automated, seconds). The CLI is ephemeral — loads definitions fresh from DB each invocation.

**No lazy loading. No per-request resolution. No Motor/Beanie split.** Beanie initializes from entity definitions in the database at startup. Restart on type changes. Simple.

```bash
indemn entity create Document --fields '...' --state-machine '...'
# Definition written to DB
# API server + Workers: automated rolling restart (seconds)
# CLI: next invocation picks it up (ephemeral)
```

CLI discoverability: `indemn <entity_type> <operation> [args]`. Available entity types queried from the API. Tab completion via API query. Same pattern as `kubectl`.

## #10: Platform Upgrade Path — Capability Schema Versioning

Every kernel capability declares its config schema version. Entity definitions store which version they use. Platform upgrades include migration scripts.

```bash
indemn platform upgrade --dry-run
# Shows what would change across all orgs

indemn platform upgrade
# Runs migrations. Auditable. Rollbackable.
```

## #11: Standard Entity Library — Seed YAML + Template Org

Seed files in the codebase (`seed/entities/*.yaml`, `seed/skills/*.md`, `seed/roles/*.yaml`). On `indemn platform init`, a `_template` org is created from seed files.

```bash
indemn org create gic --from-template standard
# Clones template org into GIC with all standard definitions
```

Updates: modify seed YAML, run `indemn platform seed --update`. Existing orgs pull updates: `indemn org pull-updates gic --from-template standard --dry-run`.

## #12: Schema Migration — First-Class Capability

Schema changes will be regular as entity definitions evolve through real usage. Migration tooling must be solid from the start.

**What happens for each type of change:**

### Add Field (No Migration)
```bash
indemn entity modify Submission --add-field '{"priority": "str", "default": "normal"}'
# Definition updated in DB. Rolling restart.
# Existing documents: Pydantic assigns default "normal" on load. No data migration.
```

### Remove Field (Deprecate + Cleanup)
```bash
indemn entity modify Submission --deprecate-field old_field
# Field hidden from CLI/API/skills. Data retained. 
# Background cleanup: indemn entity cleanup Submission --field old_field --dry-run
```

### Rename Field (Batched $rename)
```bash
indemn entity migrate Submission --rename-field named_insured primary_insured --dry-run
# "2,894 documents would be renamed. Estimated time: 12 seconds."

indemn entity migrate Submission --rename-field named_insured primary_insured
# Runs $rename in batches of 500. Progress reported.
# During migration: entity definition accepts BOTH field names (alias).
# After migration complete: alias removed, only new name accepted.
# Changes collection records the migration.
```

### Change Field Type (Batched Transform)
```bash
indemn entity migrate Submission --convert-field premium --from str --to decimal --dry-run
# "2,894 documents would be converted. 2,891 convertible, 3 require manual review."

indemn entity migrate Submission --convert-field premium --from str --to decimal
# Converts in batches. Unconvertible documents flagged for manual review.
# During migration: entity definition accepts BOTH types (Union).
# After migration complete: only new type accepted.
```

### Migration Properties
- **Idempotent:** Can be re-run safely if interrupted
- **Dry-runnable:** Always preview before executing
- **Batched:** Configurable batch size, doesn't block the system
- **Auditable:** Changes collection records migration (what, how many, duration, success/failure)
- **Rollbackable:** Reverse migrations available (`--reverse`)
- **Progress reporting:** Shows completion percentage during execution

### The Migration Window
During a rename or type change, there's a window where some documents have the old schema and some have the new. The entity definition handles this with field aliases (for renames) or union types (for type changes). After migration completes, the alias/union is removed and the definition is cleaned up.

```
1. indemn entity migrate Submission --rename-field named_insured primary_insured
2. Definition updated: both field names accepted (primary_insured with alias named_insured)
3. Rolling restart: API/Workers load new definition accepting both names
4. Migration runs: documents renamed in batches
5. Migration complete: alias removed from definition
6. Rolling restart: only primary_insured accepted
```

## #13: Thundering Herd — Temporal Worker Config

Handled by Temporal Worker configuration:
- `max_concurrent_activities` per worker (e.g., 20) naturally throttles
- Temporal's task queue rate limiting manages dispatch flow
- Retry policies with exponential backoff handle LLM rate limits

No custom batching in the Queue Processor needed.

## #14: Queue Processor HA — Deployment Platform

Handled by the deployment platform (Railway/ECS):
- Auto-restart on crash (built-in to Railway/ECS task definitions)
- Health checks via deployment platform's native monitoring
- Add leader election or Change Streams if needed at scale

---

## Summary: What We're Actually Building

| Category | Solution | Complexity |
|----------|----------|------------|
| **Org isolation** | OrgScopedCollection wrapper | One class |
| **Secrets** | AWS Secrets Manager (existing) | Config change |
| **Skill security** | Content hash + version approval | One field + lifecycle |
| **Rule security** | Creation-time validation | CLI validation |
| **Sandbox** | Daytona spec | Provider config |
| **Audit tamper evidence** | Append-only + hash chain | One field + permissions |
| **Environment isolation** | Already have separate clusters | None needed |
| **Dynamic entity limits** | Accept + validate + document | Documentation |
| **Entity type changes** | Beanie for everything, rolling restart | Simplest approach |
| **Platform upgrades** | Capability versioning + migration scripts | Standard pattern |
| **Standard library** | Seed YAML + template org | Seed files + clone |
| **Schema migration** | First-class `migrate` command with batching, dry-run, aliases | CLI command + migration engine |
| **Thundering herd** | Temporal Worker config | Config values |
| **Queue Processor HA** | Deployment platform auto-restart | Platform config |

No new infrastructure. No new architectural concepts. Security hardens. Operations get robust. Schema evolution is first-class. The architecture stays simple.
