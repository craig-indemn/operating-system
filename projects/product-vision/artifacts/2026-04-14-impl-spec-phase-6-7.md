---
ask: "Implementation specification for Phase 6 (Dog-Fooding) and Phase 7 (First External Customer)"
created: 2026-04-14
workstream: product-vision
session: 2026-04-14-a
sources:
  - type: artifact
    ref: "2026-04-13-white-paper.md"
    description: "Design source of truth"
  - type: artifact
    ref: "2026-04-13-remaining-gap-sessions.md"
    description: "Domain modeling process, operations, transition"
  - type: artifact
    ref: "2026-04-10-crm-retrace.md"
    description: "Indemn CRM modeled on the kernel — entities, roles, watches, associates"
  - type: artifact
    ref: "2026-04-10-gic-retrace-full-kernel.md"
    description: "GIC modeled on the kernel — the first external customer candidate"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-0-1.md"
    description: "Foundation spec"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-2-3.md"
    description: "Associate execution + integration spec"
  - type: artifact
    ref: "2026-04-14-impl-spec-phase-4-5.md"
    description: "Base UI + real-time spec"
---

# Implementation Specification: Phase 6 + Phase 7

## Relationship to Prior Phases

Phases 0-5 build the platform. Phases 6-7 prove it works with real users on real data. These are not code-specification phases — they are operational phases that apply the domain modeling process (from the white paper Section 3) to real workloads.

The implementation detail here is not "what classes to write" but "what entities to define, what watches to configure, what skills to author, and what the acceptance criteria are for real-world operation."

---

# Phase 6: Dog-Fooding

## What It Produces

Indemn running its own operations on the OS. The team uses it daily. Associates process real data. The base UI is the operational surface. Issues found are fixed in the kernel. The system is stable enough that the team relies on it.

## 6.1 Scope

The CRM retrace (artifact `2026-04-10-crm-retrace.md`) defined the complete domain model for Indemn's internal operations. Phase 6 implements it on the kernel built in Phases 0-5.

The CRM retrace is the blueprint. It specified:
- 9 domain entities (Organization, Contact, Deal, Meeting, MeetingIntelligence, ActionItem, Interaction, HealthSignal, Note)
- 5 org-level integrations (Granola, Gemini, Slack Bot, Linear, Meetings DB)
- 60 actor-level integrations (15 team members × 4 types: Gmail, Calendar, Slack, Drive)
- 8 roles (team_member, account_owner, ops, executive, meeting_processor, health_monitor, sync_associate, follow_up_checker)
- 6 associates (Meeting Processor, Health Monitor, Overdue Checker, Craig's Gmail Sync, Kyle's Gmail Sync, etc.)
- Rules for health scoring, action item priority, overdue detection

## 6.2 Implementation Sequence

### Step 1: Define Domain Entities

Use the CLI to create entity definitions for each CRM entity. These become dynamic classes via the entity factory.

```bash
# Each entity defined via CLI, stored in MongoDB
indemn entity create Organization \
  --fields '{"name": {"type": "str", "required": true}, "domain": {"type": "str"}, "industry": {"type": "str"}, "status": {"type": "str", "enum_values": ["prospect", "active", "churned"]}, "tier": {"type": "str", "enum_values": ["standard", "enterprise", "strategic"]}, "primary_owner_id": {"type": "objectid"}, "health_score": {"type": "str"}, "last_interaction_at": {"type": "datetime"}}' \
  --state-machine '{"prospect": ["active"], "active": ["churned"], "churned": ["active"]}'

indemn entity create Contact \
  --fields '{"name": {"type": "str", "required": true}, "email": {"type": "str"}, "phone": {"type": "str"}, "title": {"type": "str"}, "organization_id": {"type": "objectid"}, "last_interaction_at": {"type": "datetime"}}'

# ... remaining 7 entities per the CRM retrace
```

### Step 2: Configure Integrations

```bash
# Org-level
indemn integration create --owner org --name "Granola Bot" \
  --system-type meeting_transcription --provider granola \
  --access-roles "team_member,ops,admin"

# Actor-level (per team member)
indemn integration create --owner actor --actor craig@indemn.ai \
  --name "Craig's Gmail" --system-type email --provider gmail
indemn integration set-credentials INT-CRAIG-GMAIL --from-file @craig-gmail-creds.json

# Repeat for each team member × each integration type
```

### Step 3: Create Roles with Watches

Per the CRM retrace:

```bash
indemn role create team_member \
  --permissions '{"read": ["Organization", "Contact", "Meeting", "Interaction", "ActionItem", "HealthSignal"], "write": ["ActionItem", "Note"]}' \
  --watches '[{"entity_type": "ActionItem", "event": "fields_changed", "conditions": {"field": "is_overdue", "op": "equals", "value": true}}]'

indemn role create account_owner \
  --permissions '{"read": ["*"], "write": ["Organization", "Contact", "Deal", "HealthSignal"]}' \
  --watches '[
    {"entity_type": "HealthSignal", "event": "created", "scope": {"type": "field_path", "path": "organization.primary_owner_id"}},
    {"entity_type": "ActionItem", "event": "fields_changed", "conditions": {"field": "is_overdue", "op": "equals", "value": true}, "scope": {"type": "field_path", "path": "organization.primary_owner_id"}}
  ]'

# ... remaining roles
```

### Step 4: Create Rules and Lookups

```bash
# Health scoring rules
indemn rule create --entity Organization --org indemn \
  --when '{"all": [{"field": "last_interaction_at", "op": "older_than", "value": "30d"}, {"field": "tier", "op": "in", "value": ["enterprise", "strategic"]}]}' \
  --action set_fields --sets '{"health_score": "at_risk"}'

# Overdue detection (activated as stale_check capability)
indemn entity enable ActionItem stale-check \
  --when '{"all": [{"field": "due_date", "op": "older_than", "value": "0d"}, {"field": "status", "op": "not_equals", "value": "completed"}]}' \
  --sets-field is_overdue
```

### Step 5: Author Associate Skills

Write markdown skills for each associate:

```markdown
# Meeting Intelligence Extraction

When a Meeting entity is created with a transcript:
1. Read the transcript from S3 via the transcript_ref
2. Extract decisions, quotes, objections, learnings, signals, and action items
3. For each extraction:
   `indemn meetingintelligence create --meeting {meeting.id} --kind {kind} --text "{text}"`
4. For action items with assignees and due dates:
   `indemn actionitem create --owner {owner_actor_id} --description "{text}" --due-date {date} --source meeting:{meeting.id}`
```

```bash
indemn skill create meeting-extraction --content-from-file ./skills/meeting-extraction.md
```

### Step 6: Create Associates

```bash
indemn actor create --type associate --name "Meeting Processor" \
  --role meeting_processor \
  --skills '["meeting-extraction"]' \
  --mode reasoning

indemn actor create --type associate --name "Overdue Checker" \
  --role follow_up_checker \
  --skills '["overdue-check"]' \
  --mode deterministic \
  --trigger "schedule:0 8 * * *"

indemn actor create --type associate --name "Craig's Gmail Sync" \
  --role sync_associate \
  --skills '["email-sync"]' \
  --mode deterministic \
  --trigger "schedule:*/5 * * * *" \
  --owner-actor craig@indemn.ai
```

### Step 7: Create Human Actors

```bash
indemn actor create --type human --name "Craig" --email craig@indemn.ai
indemn actor add-role craig@indemn.ai --role admin
indemn actor add-role craig@indemn.ai --role account_owner
indemn actor add-auth craig@indemn.ai --method password
# ... invite flow sends magic link

# Repeat for all 15 team members
```

### Step 8: Test Pipeline End-to-End

1. Process a real meeting transcript → MeetingIntelligence entities created
2. Action items with due dates → ActionItem entities created
3. Overdue checker runs → is_overdue flags set → account owners notified
4. Health monitor runs → HealthSignal entities created for at-risk accounts
5. Team members see their queue in the base UI
6. Assistant answers "what's the story with INSURICA?" by querying the data

### Step 9: Iterate Based on Real Usage

The team uses the system daily. Issues surface:
- Missing fields on entities → `indemn entity modify`
- Rules too aggressive/lenient → adjust thresholds
- Skills need refinement → `indemn skill update`
- New watches needed → `indemn role add-watch`
- Kernel bugs → fix in kernel code, deploy

This is the value of dog-fooding: every issue discovered and fixed here is an issue that won't hit the first external customer.

## Phase 6 Acceptance Criteria

```
1. TEAM USES IT DAILY
   - All team members have accounts and roles
   - Base UI is the primary surface for customer intelligence
   - Queue view shows pending work
   - Entity views show customer data

2. ASSOCIATES PROCESS REAL DATA
   - Meeting transcripts processed into intelligence
   - Action items tracked with overdue detection
   - Health signals generated from real interaction patterns
   - Email sync working for team members with personal integrations

3. THE ASSISTANT WORKS
   - "What's the story with INSURICA?" returns a comprehensive answer
   - "Who has overdue follow-ups?" returns actionable data
   - "Prepare me for the GIC call tomorrow" pulls meeting history + signals

4. THE SYSTEM CHURNS
   - Entity changes → watches fire → associates process → entity changes → cycle continues
   - The full loop works with real data in real time
   - Queue depths are manageable, no stuck messages
   - OTEL traces show the full cascade

5. ISSUES ARE FIXED IN THE KERNEL
   - Bugs found during dog-fooding are fixed in kernel code
   - Entity definition changes are made via CLI (no kernel code changes for domain)
   - The platform improves from usage

6. IT'S STABLE ENOUGH TO RELY ON
   - The team does not need to fall back to other tools for basic operations
   - Uptime is consistent (no daily crashes or data issues)
   - Performance is acceptable (page loads under 2 seconds)
```

---

# Phase 7: First External Customer

## What It Produces

A real insurance business running on the OS, processing real data, with real users and real associates working the same queues. The customer's operations are modeled, not custom-coded.

## 7.1 Customer Selection

The white paper identifies the domain modeling process as an 8-step procedure. The first external customer is onboarded through this process.

**Primary candidate: GIC Underwriters.** Reasons:
- Existing Indemn customer ($36K ARR, email intelligence pipeline)
- Craig built the GIC email intelligence system — deep domain knowledge
- Full GIC retrace already completed against the kernel (artifact `2026-04-10-gic-retrace-full-kernel.md`)
- B2B email processing pipeline — exercises the core entity/message/watch/associate loop
- Meaningful complexity (7 entities, 6 associates, classification rules, fuzzy matching, HITL)
- Not consumer-facing (no real-time voice/chat required — Phase 5 capabilities can mature in parallel)

**Alternative: New customer.** If GIC migration timing doesn't align, a new customer going directly onto the OS is the alternative. The same domain modeling process applies.

## 7.2 Domain Modeling Process (8 Steps)

From the white paper Section 3, applied to GIC:

### Step 1: Understand the Business

Already done through years of working with GIC. The GIC retrace artifact contains the complete understanding:
- Wholesaler/MGA processing email submissions from retail agents
- Two internal teams (CS and underwriting)
- USLI, Hiscox, Granada/GIC as carrier partners
- Ball-holder tracking (queue → GIC → agent → carrier → done)
- Hard classification rules for known carriers, LLM for unknowns
- Stale detection with follow-up tracking
- Draft generation for agent/carrier responses

### Step 2: Define the Entities

Per the GIC retrace:
- Email, Extraction, Submission, Assessment, Draft, Carrier, Agent
- Each with specific fields, state machines, and relationships
- All created via `indemn entity create` commands (listed in the retrace artifact)

### Step 3: Define the Roles and Watches

Per the GIC retrace:
- email_sync, extractor, classifier, linker, assessor, draft_writer, underwriter, operations, stale_checker
- Each with specific watches targeting entity events with conditions
- All created via `indemn role create` commands (listed in the retrace artifact)

### Step 4: Define Rules and Configuration

Per the GIC retrace:
- USLI/Hiscox/servicing classification rules
- Veto rule for USLI declines
- Reference pattern extraction rules
- LOB prefix lookup table
- Carrier name variation lookup
- Required field rules per LOB

### Step 5: Write the Skills

Associate skills for:
- email-sync-skill (deterministic: just calls fetch)
- pdf-extraction-skill (reasoning: OCR + LLM extraction)
- email-classification-skill (hybrid: rules first, LLM fallback)
- submission-linking-skill (hybrid: reference patterns + fuzzy + LLM)
- situation-assessment-skill (reasoning: analyze completeness + recommend)
- draft-writing-skill (reasoning: generate response drafts)
- stale-check-skill (deterministic: just calls the capability)

### Step 6: Set Up Integrations

```bash
# GIC's Outlook connection
indemn integration create --owner org --name "GIC Outlook" \
  --system-type email --provider outlook --provider-version v2 \
  --access-roles "underwriter,operations,admin,email_sync"
```

### Step 7: Test in Staging

```bash
# Clone production org as staging
indemn org clone gic --as gic-staging

# Apply all configuration to staging
# Test with real-ish data:
# - Forward a subset of emails to a staging inbox
# - Run the pipeline
# - Verify: classification accuracy, linking accuracy, assessment quality
# - Verify: watches fire correctly, associates process as expected
# - Verify: underwriter queue shows the right items
# - Verify: stale detection works on appropriate timelines
```

### Step 8: Deploy and Tune

```bash
# Promote staging config to production
indemn deploy --from-org gic-staging --to-org gic --dry-run
indemn deploy --from-org gic-staging --to-org gic

# Monitor in real time via base UI
# Tune based on real data:
# - needs_reasoning rate tells you where to add rules
# - Queue depths tell you if associates are keeping up
# - Changes collection shows decision quality
# - OTEL traces show processing times
```

## 7.3 Migration Considerations

GIC is an existing customer with a running email intelligence system on the current platform. The transition:

1. **Run both systems in parallel.** Same emails go to both the current system and the new OS. Compare outputs. Fix discrepancies.

2. **The current system stays running.** No disruption. The OS is additive. Per the white paper: "different codebases, different infrastructure, different databases. They don't share resources and they don't need to communicate."

3. **Cut over when confident.** When the OS produces the same (or better) results consistently, stop the old pipeline. The customer's workflow doesn't change — same emails, same outputs, different engine underneath.

4. **Metrics for confidence:**
   - Classification accuracy matches or exceeds current system
   - Linking accuracy matches or exceeds
   - Assessment quality comparable (human review of samples)
   - Processing latency comparable or better
   - No data loss (every email that enters is processed)
   - Two weeks of parallel operation with no discrepancies

## 7.4 What This Proves

The first external customer running on the OS proves:

1. **The kernel works for real insurance operations.** Not just CRM dog-fooding — actual insurance email processing with underwriting workflows.

2. **Domain modeling is configuration, not construction.** GIC's setup is CLI commands creating entities, rules, watches, associates, and skills. No custom kernel code for this customer.

3. **The --auto pattern delivers value.** Classification rules handle the common cases deterministically. LLM handles the edge cases. The `needs_reasoning` rate shows where to add more rules.

4. **The unified queue works.** Human underwriters and AI associates operate the same queue. Work flows between them naturally.

5. **The system is production-grade.** Real data, real users, real volume, real uptime requirements. Issues found here inform kernel hardening.

## Phase 7 Acceptance Criteria

```
1. REAL INSURANCE WORKFLOW RUNS ON THE OS
   - GIC's email processing pipeline operates entirely on the OS
   - Emails are fetched, classified, linked to submissions, assessed, drafted
   - Underwriters see their queue in the base UI
   - All processing is via associates using skills and CLI commands

2. CONFIGURATION, NOT CUSTOM CODE
   - GIC's domain is modeled via entity definitions, rules, watches, skills
   - No kernel code changes were needed for GIC-specific behavior
   - Another similar customer could be set up by repeating the process

3. REAL USERS OPERATE THE SYSTEM
   - GIC underwriters log in and use the base UI
   - They claim queue items, review assessments, approve drafts
   - The assistant helps them with queries and operations

4. THE SYSTEM HANDLES REAL VOLUME
   - GIC's daily email volume (~100-200 emails/day) processes smoothly
   - No queue buildup, no stuck messages, no missed emails
   - Processing latency is acceptable (emails processed within minutes)

5. PARALLEL RUN VALIDATES ACCURACY
   - OS results match or exceed the current system
   - Classification accuracy >= current system
   - Linking accuracy >= current system
   - Two weeks of parallel operation with zero critical discrepancies

6. THE BUSINESS VALUE IS CLEAR
   - GIC team productivity measurably improved (or at least maintained)
   - The --auto pattern keeps LLM costs proportional to edge cases
   - The system gets more deterministic over time (rules added for repeated patterns)
```

## 7.5 What Comes After

Each subsequent customer is faster than the last. Phase 7 establishes the pattern:
- Standard entity definitions emerge from repeated use (seed templates)
- Skills get reused and refined (submission processing skill works for any email-driven MGA)
- Rule patterns become starting points (USLI classification rules inform other carrier rules)
- Adapter library covers more providers (Outlook proven, Gmail next, then others)
- The domain modeling process is proven and documented

The build sequence is complete when new customers are configuration, not construction. Phase 7 is the proof point. Everything after it is scaling.

---

# Cross-Phase: Shared Open Questions

These questions span multiple phases and should be resolved early in implementation:

1. **Entity definition hot-reload vs. restart.** The spec says rolling restart on entity type changes. The frequency of entity definition changes during active development (Phases 1-6) may make restarts disruptive. A lazy-loading approach where entity classes are resolved per-request (checking a definitions cache with a short TTL) would eliminate restarts at the cost of first-request latency. Worth prototyping in Phase 1 to determine the right trade-off.

2. **Beanie integration depth.** How deeply to use Beanie's features (Link/BackLink, aggregation, document state tracking) vs. keeping a thinner layer over raw Motor. The dynamic class creation approach pushes toward a thinner layer. Kernel entities (static classes) can use Beanie's full feature set. Dynamic entities may use a subset. The right boundary emerges during Phase 1 implementation.

3. **Associate skill execution safety.** When an associate executes CLI commands via the API, every command goes through auth middleware and permission checking. But the LLM could generate unexpected commands. The CLI (in API mode) is the security boundary — it only accepts valid entity operations, and the auth layer enforces what the associate's role can do. However, rate limiting on associate API calls may be needed to prevent runaway LLM loops. Design during Phase 2.

4. **Seed data management.** Standard entity definitions (seed YAML) need a workflow for updating across running orgs. `indemn platform seed --update` updates the template org. Existing customer orgs need a `indemn org pull-updates --from-template standard --dry-run` mechanism. The exact workflow for rolling out definition changes to customer orgs needs design during Phase 6-7.
