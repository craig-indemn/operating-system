---
ask: "Session prompt for comprehensive spec-vs-implementation audit — verify every design decision, every mechanism, every primitive against the built code"
created: 2026-04-15
workstream: product-vision
session: 2026-04-15-b
sources:
  - type: artifact
    ref: "2026-04-13-white-paper.md"
    description: "Design source of truth"
  - type: artifact
    ref: "2026-04-15-shakeout-session-findings.md"
    description: "Shakeout findings from first boot (19 findings, 15 fixed)"
---

# Comprehensive Spec-vs-Implementation Audit

You are Craig, de facto CTO of Indemn. The "Operating System for Insurance" has been designed across 8 sessions (65+ artifacts, 160+ locked decisions, a white paper) and built across 4 build sessions (8 phases, 176 tests). A shakeout session just booted the system for the first time and found 19 issues — 15 were fixed, but the audit revealed a critical gap: **the assistant has no tools and no harness** (it's a text completion, not an agent that can operate the system).

Your job in THIS session is a **comprehensive spec-vs-implementation audit**. Not running the system — that was done. This is reading the spec, reading the code, and documenting every place where what was built diverges from what was designed. Every mechanism. Every primitive. Every decision.

## CRITICAL INSTRUCTIONS

**YOU MUST READ EVERY FILE LISTED BELOW. ALL OF THEM. BEGINNING TO END. NO EXCEPTIONS.**

- Do NOT use subagents or subtasks to read files. Read them yourself, directly, using the Read tool.
- Do NOT skip files because they seem redundant or because you think you understand the topic.
- Do NOT summarize or skim. Read every line of every file.
- Do NOT rush. There is no time pressure. Thoroughness is the only metric.
- If a file is too large for one read, use offset/limit to chunk through it. Read ALL chunks.
- After reading each file, note the key points that inform the audit. Do not discard context.

The quality bar is 100%. Every deviation between spec and implementation must be found and documented. Missing one could mean an architectural assumption is wrong and compounds into larger problems later.

## What you MUST read

### Phase 1: The Shakeout Findings (read this FIRST)

This tells you what was already found and fixed. Don't re-discover these — build on them.

/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-15-shakeout-session-findings.md

### Phase 2: The White Paper (design source of truth)

Every mechanism described here must exist in the code. Every claim must be verified.

/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-13-white-paper.md

### Phase 3: The Project INDEX.md (160+ locked decisions)

Every locked decision must be reflected in the implementation. If a decision says "X works this way," the code must do X that way.

/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/INDEX.md

### Phase 4: The Implementation Specifications (what was supposed to be built)

These are the buildable specs. Every function signature, every data model, every endpoint specified here should exist in the code.

- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-14-impl-spec-phase-0-1-consolidated.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-14-impl-spec-phase-2-3-consolidated.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-14-impl-spec-phase-4-5-consolidated.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-14-impl-spec-phase-6-7-consolidated.md

### Phase 5: The Gap Identification and Verification

These document 90 gaps that were identified and supposedly resolved. Verify they actually were.

- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-14-impl-spec-gaps.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-14-impl-spec-verification-report.md

### Phase 6: The Design Artifacts (the thinking behind the decisions)

These contain the reasoning, trade-offs, and rejected alternatives. Read them to understand WHY things were designed a certain way — this informs whether the implementation captured the intent, not just the surface.

Context documents:
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/context/business.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/context/product.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/context/architecture.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/context/strategy.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/context/craigs-vision.md

Session 1:
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

Session 4:
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

Session 5:
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-10-integration-as-primitive.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-10-gic-retrace-full-kernel.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-10-base-ui-and-auth-design.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-10-eventguard-retrace.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-10-post-trace-synthesis.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-10-crm-retrace.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-10-realtime-architecture-design.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-10-session-5-checkpoint.md

Session 6:
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-10-bulk-operations-pattern.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-11-base-ui-operational-surface.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-11-authentication-design.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-13-documentation-sweep.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-13-simplification-pass.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-13-session-6-checkpoint.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-13-infrastructure-and-deployment.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-13-remaining-gap-sessions.md

Session prompts:
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-09-next-session-prompt.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-13-white-paper-session-prompt.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-14-implementation-spec-session-prompt.md
- /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/product-vision/artifacts/2026-04-14-verification-session-prompt.md

### Phase 7: The Codebase

/Users/home/Repositories/indemn-os/

Read the CLAUDE.md first. Then read EVERY Python file in the project. Do not skip any. The audit requires understanding the complete implementation.

```bash
find /Users/home/Repositories/indemn-os -name "*.py" -not -path "*/node_modules/*" -not -path "*/.venv/*" -not -path "*/__pycache__/*" | sort
```

For UI files:
```bash
find /Users/home/Repositories/indemn-os/ui/src -name "*.ts" -o -name "*.tsx" | sort
```

## The Audit

After reading EVERYTHING, produce a comprehensive deviation report. For each area of the system:

### 1. Six Primitives
For each primitive (Entity, Message, Actor, Role, Organization, Integration):
- What the white paper says it does
- What the code actually does
- Any deviations, missing features, or incorrect implementations

### 2. Seven Kernel Entities
For each kernel entity (Organization, Actor, Role, Integration, Attention, Runtime, Session):
- Fields specified vs fields implemented
- State machine specified vs implemented
- Behaviors specified vs implemented

### 3. Kernel Mechanisms
For each mechanism:
- save_tracked() transaction — does it match the spec?
- Selective emission — correct priority? correct events?
- Watch evaluation — condition language complete? scope resolution correct?
- Rule engine — all operators? veto rules? lookups?
- Capability system — auto_classify, stale_check, others specified?
- Changes collection — hash chain, field-level tracking, all change types?
- Message bus — claim, complete, fail, dead-letter, visibility timeout?

### 4. Authentication & Authorization
- Password, TOTP, SSO, token, magic_link methods
- Session types (user_interactive, associate_service, tier3_api, cli_automation)
- JWT + revocation cache
- MFA policy (role-level, actor exempt, org default)
- Platform admin cross-org sessions
- Rate limiting
- Auth events audit trail

### 5. API & CLI
- All auto-generated routes present?
- All static routes present?
- CLI commands match spec?
- Entity metadata endpoint complete?

### 6. UI
- Self-evidence property — do all views auto-generate from metadata?
- Assistant — does it have tools? Does it use a harness? (Known gap from shakeout)
- Real-time — WebSocket + Change Streams?
- Auto-generated forms — do they handle all field types?

### 7. Associate Execution
- Temporal integration — workflows, activities
- Harness pattern — is it implemented? (Known gap from shakeout)
- Skill loading with tamper detection
- Execution modes (deterministic, reasoning, hybrid)
- --auto pattern

### 8. Integration Framework
- Adapter interface (outbound + inbound)
- Credential resolution priority chain
- Webhook dispatch
- Outlook + Stripe adapters specified — are they built?

### 9. Org Lifecycle
- Clone, diff, deploy, export, import
- Environments as orgs

### 10. Infrastructure
- Dockerfile, docker-compose
- Queue processor
- Seed data loading

## Known Issues from Shakeout

These were already found. Don't re-discover them — verify the fixes are correct and check for related issues:

1. ObjectId serialization → to_dict() helper
2. init_beanie ordering → moved before entity def loading
3. Motor Database truth check → skip private attrs
4. Beanie is_root=True → removed, separate collections
5. String→ObjectId coercion → _coerce_objectid_fields
6. date→datetime → TYPE_MAP fix
7. Runtime entity registration → register_domain_entity()
8. CORS middleware → outermost
9. Entity name slug resolution → useEntityNameFromSlug hook
10. Watch cache invalidation → in save_tracked for Role
11. httpx follow_redirects → True in CLIClient
12. Dynamic CLI override → expanded _STATIC_CLI_ENTITIES
13. Hash chain verification → strftime + ms truncation
14. State machine bypass → reject state field in update
15. Bootstrap audit trail → save_tracked with __bootstrap__
16. Vite proxy /auth prefix → /auth/
17. CLI default format → json
18. **CRITICAL: Assistant has no tools, no harness** — documented, not fixed
19. Dev API key billing — external

## How to Report

Produce a structured deviation report as an artifact. For each deviation:

```
### Area: [area name]
**Spec says:** [what the design documents specify]
**Code does:** [what the implementation actually does]
**Severity:** CRITICAL / IMPORTANT / MINOR / COSMETIC
**Impact:** [what breaks or is missing because of this]
**Recommendation:** [what should be done]
```

Group by area. Prioritize by severity. Include line numbers and file paths.

Do NOT fix anything. Document everything. Present to Craig for review.
