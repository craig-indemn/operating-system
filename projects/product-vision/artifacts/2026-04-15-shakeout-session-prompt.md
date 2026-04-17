---
ask: "Session prompt for end-to-end shakeout of the built kernel — boot the system, run a concrete test scenario, audit and report every finding"
created: 2026-04-15
workstream: product-vision
session: 2026-04-15-a
sources:
  - type: artifact
    ref: "2026-04-13-white-paper.md"
    description: "Design source of truth"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-6-7-consolidated.md"
    description: "Phase 6+7 operational spec (the test scenario source)"
---

# End-to-End Shakeout Session

You are Craig, de facto CTO of Indemn. Across 8 design sessions and 4 build sessions, you designed and built the "Operating System for Insurance" — a domain-agnostic kernel built from six primitives. All 8 build phases (0-7) are implemented. 176 tests pass. Ruff clean. Three rounds of spec audit verified the code matches the spec.

**But the system has never been booted.** No CLI command has ever hit a running API server. No entity has ever been created through the full stack. The tests prove the pieces work in isolation — this session proves they work together.

Your job is to **audit, not fix**. Run the system, document every finding, and present results to Craig for review before making any changes.

## What you MUST read first

Read EVERYTHING below. This is the complete intellectual history of the OS. You need all of it to understand what you're testing and why each piece matters. Do not skip any file. Use offset/limit to chunk large files.

### 1. The white paper (design source of truth)

/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-13-white-paper.md

### 2. The project INDEX.md (160+ locked decisions)

/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/INDEX.md

### 3. The implementation specifications (what was built)

- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-14-impl-spec-phase-0-1-consolidated.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-14-impl-spec-phase-2-3-consolidated.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-14-impl-spec-phase-4-5-consolidated.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-14-impl-spec-phase-6-7-consolidated.md

### 4. The gap identification and verification

- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-14-impl-spec-gaps.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-14-impl-spec-verification-report.md

### 5. The design artifacts

Context documents:
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/context/business.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/context/product.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/context/architecture.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/context/strategy.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/context/craigs-vision.md

Session 1 outputs:
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-03-25-session-notes.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-03-25-the-operating-system-for-insurance.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-03-25-why-insurance-why-now.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-03-25-platform-tiers-and-operations.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-03-25-associate-architecture.md

Domain model:
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-03-24-associate-domain-mapping.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-03-24-source-index.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-03-25-domain-model-research.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-03-25-domain-model-v2.md

Session 2:
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-03-30-entity-system-and-generator.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-03-30-vision-session-2-checkpoint.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-03-30-design-layer-1-entity-framework.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-03-30-design-layer-3-associate-system.md

Session 3:
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-02-core-primitives-architecture.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-02-design-layer-4-integrations.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-02-design-layer-5-experience.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-02-implementation-plan.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-03-message-actor-architecture-research.md

Session 3-4 resolution:
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-08-actor-spectrum-and-primitives.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-08-primitives-resolved.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-08-entry-points-and-triggers.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-08-kernel-vs-domain.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-08-pressure-test-findings.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-08-actor-references-and-targeting.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-09-entity-capabilities-and-skill-model.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-09-capabilities-model-review-findings.md

Session 4 (Temporal, data architecture, ironing):
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-09-temporal-integration-architecture.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-09-unified-queue-temporal-execution.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-09-data-architecture-everything-is-data.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-09-architecture-ironing.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-09-architecture-ironing-round-2.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-09-architecture-ironing-round-3.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-09-data-architecture-review-findings.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-09-data-architecture-solutions.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-09-session-4-checkpoint.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-09-consolidated-architecture.md

Session 5 (retraces, real-time):
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-10-integration-as-primitive.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-10-gic-retrace-full-kernel.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-10-base-ui-and-auth-design.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-10-eventguard-retrace.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-10-post-trace-synthesis.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-10-crm-retrace.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-10-realtime-architecture-design.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-10-session-5-checkpoint.md

Session 6 (design sessions, simplification, infrastructure):
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-10-bulk-operations-pattern.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-11-base-ui-operational-surface.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-11-authentication-design.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-13-documentation-sweep.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-13-simplification-pass.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-13-session-6-checkpoint.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-13-infrastructure-and-deployment.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-13-remaining-gap-sessions.md

Session prompts (for context on how sessions were structured):
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-09-next-session-prompt.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-13-white-paper-session-prompt.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-14-implementation-spec-session-prompt.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-14-verification-session-prompt.md

### 6. The codebase

/Users/home/Repositories/indemn-os/

Read the CLAUDE.md first. Then read these key files:
- /Users/home/Repositories/indemn-os/kernel/api/app.py (startup, router registration)
- /Users/home/Repositories/indemn-os/kernel/db.py (MongoDB init, entity registry, domain class creation)
- /Users/home/Repositories/indemn-os/kernel/entity/base.py (KernelBaseEntity + DomainBaseEntity)
- /Users/home/Repositories/indemn-os/kernel/entity/save.py (save_tracked — the critical transaction)
- /Users/home/Repositories/indemn-os/kernel/entity/factory.py (dynamic class creation from definitions)
- /Users/home/Repositories/indemn-os/kernel/message/emit.py (watch evaluation + message creation)
- /Users/home/Repositories/indemn-os/kernel/watch/scope.py (scope resolution for watches)
- /Users/home/Repositories/indemn-os/kernel/watch/evaluator.py (condition evaluator — 16 operators)
- /Users/home/Repositories/indemn-os/kernel/rule/engine.py (rule evaluation)
- /Users/home/Repositories/indemn-os/kernel/capability/auto_classify.py + stale_check.py
- /Users/home/Repositories/indemn-os/kernel/cli/app.py (CLI entry point, dynamic + static commands)
- /Users/home/Repositories/indemn-os/kernel/api/registration.py (auto-generated CRUD routes)

## The Test Scenario

After reading everything, run ONE concrete scenario end-to-end. This tests the core kernel loop: entity creation → watch fires → message created → capability invoked → entity updated.

### Step 1: Boot

1. Start the API server against Atlas dev cluster
2. Record: does it start? Any errors? How long?

### Step 2: Initialize

1. Run `indemn platform init --admin-email craig@indemn.ai --admin-password <prompt>`
2. Record: does it succeed? Can you authenticate?

### Step 3: Create two entity types

From the CRM spec (section 6.2 Step 2), create just these two:

```bash
indemn entity create Company --fields '{
  "name": {"type": "str", "required": true},
  "status": {"type": "str", "enum_values": ["prospect", "active", "churned"], "is_state_field": true},
  "health_score": {"type": "str", "enum_values": ["healthy", "at_risk", "churn_risk"]},
  "last_interaction_at": {"type": "datetime"},
  "tier": {"type": "str", "enum_values": ["standard", "enterprise", "strategic"]},
  "primary_owner_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Actor"}
}' --state-machine '{"prospect": ["active"], "active": ["churned"], "churned": ["active"]}'

indemn entity create ActionItem --fields '{
  "owner_actor_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Actor"},
  "description": {"type": "str", "required": true},
  "due_date": {"type": "date"},
  "status": {"type": "str", "enum_values": ["open", "completed", "cancelled"], "is_state_field": true, "default": "open"},
  "is_overdue": {"type": "bool", "default": false}
}' --state-machine '{"open": ["completed", "cancelled"]}'
```

Record: do both succeed? Can you list them? Can you create instances?

### Step 4: Create a role with a watch

```bash
indemn role create team_member \
  --permissions '{"read": ["Company", "ActionItem"], "write": ["ActionItem"]}' \
  --watches '[{"entity_type": "ActionItem", "event": "fields_changed", "conditions": {"all": [{"field": "is_overdue", "op": "equals", "value": true}]}, "scope": {"type": "field_path", "path": "owner_actor_id"}}]'
```

Record: does role creation work? Are watches stored?

### Step 5: Create a rule and activate a capability

```bash
indemn rule create --entity Company --capability auto_classify \
  --name "enterprise-no-contact-30d" \
  --when '{"all": [{"field": "last_interaction_at", "op": "older_than", "value": "30d"}, {"field": "tier", "op": "in", "value": ["enterprise", "strategic"]}]}' \
  --action set_fields --sets '{"health_score": "at_risk"}'

indemn entity enable ActionItem stale_check \
  --config '{"when": {"all": [{"field": "status", "op": "equals", "value": "open"}, {"field": "is_overdue", "op": "equals", "value": false}]}, "sets_field": "is_overdue", "sets_value": true}'
```

Record: do both succeed? Can you list the rule? Is the capability activated?

### Step 6: Create an actor and assign the role

```bash
indemn actor create --type human --name "Craig" --email craig@indemn.ai
indemn actor add-role craig@indemn.ai --role team_member
```

Record: does actor creation work? Does add-role resolve email and role name?

### Step 7: The real test — create an ActionItem and run stale-check

```bash
# Create an ActionItem owned by Craig
indemn actionitem create --data '{"description": "Follow up with INSURICA", "due_date": "2026-04-01", "status": "open", "is_overdue": false, "owner_actor_id": "<CRAIG_ACTOR_ID>"}'

# Run stale-check on it
indemn actionitem stale-check <ACTION_ITEM_ID> --auto
```

Record:
- Does the ActionItem get created?
- Does stale-check evaluate the conditions?
- Does it set is_overdue to true?
- Does the save trigger watch evaluation?
- Does a message get created targeting Craig (via owner_actor_id scope)?
- Can you see the message in `indemn queue list`?

### Step 8: Test org export

```bash
indemn org export <org_slug> --output /tmp/crm-export/
ls -R /tmp/crm-export/
```

Record: does it produce the expected directory structure? org.yaml, entities/, roles/, rules/, capabilities/?

## How to report

Do NOT fix anything automatically. Instead, produce a findings report with this structure:

### For each step:
```
## Step N: <name>
**Command:** <exact command run>
**Result:** PASS / FAIL
**Output:** <relevant output or error>
**Analysis:** <if FAIL: what went wrong, which file/line, root cause hypothesis>
```

### Summary table:
```
| Step | What | Result | Issue |
|------|------|--------|-------|
| 1    | Boot | PASS/FAIL | ... |
| 2    | Init | PASS/FAIL | ... |
| ...  | ...  | ...    | ... |
```

### Recommended fixes:
For each failure, propose a fix with:
- File and line number
- What to change
- Why this fixes it
- Risk assessment (could the fix break something else?)

Present the full report to Craig. Wait for approval before making any code changes.

## Critical guidance

1. **Read ALL artifacts first.** You need the full design context to diagnose failures correctly.

2. **Audit, don't fix.** Document everything. Present findings. Wait for Craig's go-ahead before changing code.

3. **Don't change the spec.** If the spec says to create an entity with these exact fields, use those exact fields. If the CLI rejects the input, the bug is in the code, not the spec.

4. **The Atlas dev cluster is the database.** Connection: `dev-indemn.mifra5.mongodb.net`. Credentials in AWS Secrets Manager at `indemn/dev/shared/mongodb-uri`. Convert private link URI by replacing `-pl-0.` with `.`.

5. **Record everything.** Every command, every output, every error. The report is the deliverable.
