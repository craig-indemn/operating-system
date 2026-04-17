---
ask: "Consolidated implementation specification for Phase 6 (Dog-Fooding) and Phase 7 (First External Customer) — resolving all 4 applicable gaps"
created: 2026-04-14
workstream: product-vision
session: 2026-04-14-a
sources:
  - type: artifact
    ref: "2026-04-13-white-paper.md"
    description: "Design-level source of truth"
  - type: artifact
    ref: "2026-04-14-impl-spec-gaps.md"
    description: "Gap identification — this resolves G-52, G-53, G-54, G-55"
  - type: artifact
    ref: "2026-04-10-crm-retrace.md"
    description: "Indemn CRM modeled on the kernel"
  - type: artifact
    ref: "2026-04-10-gic-retrace-full-kernel.md"
    description: "GIC modeled on the kernel"
  - type: artifact
    ref: "2026-04-13-remaining-gap-sessions.md"
    description: "Domain modeling process, operations, transition"
  - type: verification
    description: "This document supersedes 2026-04-14-impl-spec-phase-6-7.md"
---

# Implementation Specification: Phase 6 + Phase 7 (Consolidated)

**This document supersedes `2026-04-14-impl-spec-phase-6-7.md`.**

## Relationship to Prior Phases

Phases 0-5 build the platform. Phases 6-7 prove it works. Phase 6 dog-foods Indemn's own operations — the team uses the OS daily, associates process real data, the base UI is the operational surface. Phase 7 puts the first external insurance customer on the OS.

These are operational phases, not code-specification phases. The implementation detail here is: what entities to define, what watches to configure, what skills to author, how to validate, and how to migrate.

---

# Phase 6: Dog-Fooding

## What It Produces

Indemn running its own operations on the OS. The team uses it daily. Associates process real data. The base UI is the operational surface. Issues found are fixed in the kernel.

## 6.1 The CRM Retrace as Blueprint

The CRM retrace artifact (`2026-04-10-crm-retrace.md`) defines the complete domain model for Indemn's internal operations. It was the third pressure test of the kernel — a generic B2B customer intelligence system with zero insurance concepts. It validated domain-agnosticity and exercised actor-level integrations at scale.

Phase 6 implements exactly what the retrace specified.

## 6.2 Domain Modeling — The 8-Step Process Applied [G-55]

The white paper Section 3 defines an 8-step domain modeling process. Here it is applied to Indemn's CRM as a concrete CLI sequence.

### Step 1: Understand the Business

Already done. Indemn is a 15-person company selling AI associates for insurance. The CRM needs to: track customer relationships across meetings/emails/Slack, process meeting transcripts into actionable intelligence, monitor follow-ups and health signals, prepare for customer calls, produce weekly summaries.

**Verify before proceeding:** Can you describe the business entirely in terms of entities and their states? Yes — Company (prospect→active→churned), Contact (linked to company), Deal (stage pipeline), Meeting (scheduled→completed→processed), ActionItem (created→completed), HealthSignal (detected→acknowledged→resolved).

### Step 2: Define the Entities

```bash
# Run these commands in order. Each creates an entity definition in MongoDB.

# NOTE: "Organization" is a reserved kernel entity name (the multi-tenancy scope primitive).
# CRM customer organizations use "Company" to avoid collision.
indemn entity create Company \
  --fields '{
    "name": {"type": "str", "required": true},
    "domain": {"type": "str"},
    "industry": {"type": "str"},
    "status": {"type": "str", "enum_values": ["prospect", "active", "churned"], "is_state_field": true},
    "tier": {"type": "str", "enum_values": ["standard", "enterprise", "strategic"]},
    "primary_owner_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Actor"},
    "health_score": {"type": "str", "enum_values": ["healthy", "at_risk", "churn_risk"]},
    "last_interaction_at": {"type": "datetime"}
  }' \
  --state-machine '{"prospect": ["active"], "active": ["churned"], "churned": ["active"]}'

indemn entity create Contact \
  --fields '{
    "name": {"type": "str", "required": true},
    "email": {"type": "str"},
    "phone": {"type": "str"},
    "title": {"type": "str"},
    "organization_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Company"},
    "last_interaction_at": {"type": "datetime"}
  }'

indemn entity create Deal \
  --fields '{
    "name": {"type": "str", "required": true},
    "organization_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Company"},
    "stage": {"type": "str", "enum_values": ["prospecting", "qualification", "proposal", "negotiation", "closed_won", "closed_lost"], "is_state_field": true},
    "value": {"type": "decimal"},
    "currency": {"type": "str", "default": "USD"},
    "owner_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Actor"},
    "expected_close_date": {"type": "date"},
    "status": {"type": "str", "enum_values": ["active", "won", "lost"], "default": "active"}
  }' \
  --state-machine '{"prospecting": ["qualification"], "qualification": ["proposal", "closed_lost"], "proposal": ["negotiation", "closed_lost"], "negotiation": ["closed_won", "closed_lost"]}'

indemn entity create Meeting \
  --fields '{
    "title": {"type": "str", "required": true},
    "scheduled_at": {"type": "datetime"},
    "duration_minutes": {"type": "int"},
    "attendees_actor_ids": {"type": "list"},
    "attendees_contact_ids": {"type": "list"},
    "organization_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Company"},
    "source": {"type": "str", "enum_values": ["granola", "gemini", "zoom", "manual"]},
    "transcript_ref": {"type": "str"},
    "status": {"type": "str", "enum_values": ["scheduled", "completed", "processed"], "is_state_field": true}
  }' \
  --state-machine '{"scheduled": ["completed"], "completed": ["processed"]}'

indemn entity create MeetingIntelligence \
  --fields '{
    "meeting_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Meeting"},
    "kind": {"type": "str", "enum_values": ["decision", "quote", "objection", "learning", "signal", "action_item"]},
    "text": {"type": "str", "required": true},
    "confidence": {"type": "float"},
    "extracted_by": {"type": "str"}
  }'

indemn entity create ActionItem \
  --fields '{
    "owner_actor_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Actor"},
    "description": {"type": "str", "required": true},
    "due_date": {"type": "date"},
    "source_meeting_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Meeting"},
    "organization_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Company"},
    "status": {"type": "str", "enum_values": ["open", "completed", "cancelled"], "is_state_field": true, "default": "open"},
    "is_overdue": {"type": "bool", "default": false},
    "completed_at": {"type": "datetime"}
  }' \
  --state-machine '{"open": ["completed", "cancelled"]}'

indemn entity create Interaction \
  --fields '{
    "kind": {"type": "str", "enum_values": ["email", "slack", "call", "in_person"]},
    "contact_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Contact"},
    "organization_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Company"},
    "direction": {"type": "str", "enum_values": ["inbound", "outbound"]},
    "participants_actor_ids": {"type": "list"},
    "occurred_at": {"type": "datetime"},
    "content_preview": {"type": "str"},
    "source_integration_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Integration"},
    "full_content_ref": {"type": "str"}
  }'

indemn entity create HealthSignal \
  --fields '{
    "organization_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Company"},
    "kind": {"type": "str", "enum_values": ["churn_risk", "expansion", "engagement_drop", "champion_lost"]},
    "severity": {"type": "str", "enum_values": ["low", "medium", "high", "critical"]},
    "detected_at": {"type": "datetime"},
    "basis": {"type": "str"},
    "status": {"type": "str", "enum_values": ["detected", "acknowledged", "resolved"], "is_state_field": true, "default": "detected"}
  }' \
  --state-machine '{"detected": ["acknowledged", "resolved"], "acknowledged": ["resolved"]}'

indemn entity create Note \
  --fields '{
    "subject_type": {"type": "str"},
    "subject_id": {"type": "objectid"},
    "author_actor_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Actor"},
    "content": {"type": "str", "required": true}
  }'
```

**Verify:** Restart API server. Run `indemn organization list`, `indemn contact list`, etc. All entity types have CLI commands and API routes.

### Step 3: Define Roles and Watches

```bash
# Team member — everyone gets this
indemn role create team_member \
  --permissions '{"read": ["Company", "Contact", "Meeting", "Interaction", "ActionItem", "HealthSignal", "Note", "Deal"], "write": ["ActionItem", "Note"]}' \
  --watches '[
    {"entity_type": "ActionItem", "event": "fields_changed", "conditions": {"all": [{"field": "is_overdue", "op": "equals", "value": true}]}, "scope": {"type": "field_path", "path": "owner_actor_id"}}
  ]'

# Account owner — owns customer relationships
indemn role create account_owner \
  --permissions '{"read": ["*"], "write": ["Company", "Contact", "Deal", "HealthSignal"]}' \
  --watches '[
    {"entity_type": "HealthSignal", "event": "created", "scope": {"type": "field_path", "path": "organization.primary_owner_id"}},
    {"entity_type": "ActionItem", "event": "fields_changed", "conditions": {"field": "is_overdue", "op": "equals", "value": true}, "scope": {"type": "field_path", "path": "organization.primary_owner_id"}},
    {"entity_type": "Meeting", "event": "created", "scope": {"type": "field_path", "path": "organization.primary_owner_id"}}
  ]'

# Meeting processor — AI role
indemn role create meeting_processor \
  --permissions '{"read": ["Meeting"], "write": ["MeetingIntelligence", "ActionItem"]}' \
  --watches '[{"entity_type": "Meeting", "event": "transitioned", "conditions": {"field": "status", "op": "equals", "value": "completed"}}]'

# Health monitor — AI role
indemn role create health_monitor \
  --permissions '{"read": ["Company", "Interaction"], "write": ["Company", "HealthSignal"]}' \
  --watches '[]'

# Overdue checker — AI role (schedule-triggered)
indemn role create follow_up_checker \
  --permissions '{"read": ["ActionItem"], "write": ["ActionItem"]}' \
  --watches '[]'

# Ops — sees everything
indemn role create ops \
  --permissions '{"read": ["*"], "write": ["Company", "ActionItem", "HealthSignal"]}' \
  --watches '[
    {"entity_type": "HealthSignal", "event": "created", "conditions": {"field": "severity", "op": "in", "value": ["high", "critical"]}},
    {"entity_type": "Deal", "event": "transitioned", "conditions": {"field": "stage", "op": "equals", "value": "closed_won"}}
  ]'
```

**Verify:** `indemn role list --show-watches` shows the full system wiring.

### Step 4: Define Rules and Configuration

```bash
# Health scoring rules
indemn rule create --entity Company --capability auto_classify \
  --name "enterprise-no-contact-30d" \
  --when '{"all": [{"field": "last_interaction_at", "op": "older_than", "value": "30d"}, {"field": "tier", "op": "in", "value": ["enterprise", "strategic"]}]}' \
  --action set_fields --sets '{"health_score": "at_risk"}'

indemn rule create --entity Company --capability auto_classify \
  --name "any-no-contact-90d" \
  --when '{"all": [{"field": "last_interaction_at", "op": "older_than", "value": "90d"}]}' \
  --action set_fields --sets '{"health_score": "churn_risk"}'

# Activate overdue detection capability on ActionItem
indemn entity enable ActionItem stale_check \
  --config '{"when": {"all": [{"field": "due_date", "op": "older_than", "value": "0d"}, {"field": "status", "op": "not_equals", "value": "completed"}]}, "sets_field": "is_overdue", "sets_value": true}'
```

### Step 5: Write Skills

Create markdown skill files:

```bash
# Meeting intelligence extraction skill
cat > /tmp/meeting-extraction.md << 'SKILL'
# Meeting Intelligence Extraction

When a Meeting transitions to "completed" and has a transcript:

1. Read the transcript from S3: the transcript_ref field contains the S3 path
2. Analyze the transcript and extract:
   - **Decisions**: concrete decisions made during the meeting
   - **Quotes**: notable statements worth capturing verbatim
   - **Objections**: concerns or pushback raised
   - **Learnings**: insights about the customer or market
   - **Signals**: health indicators (churn risk, expansion opportunity, champion changes)
   - **Action items**: commitments made with owners and due dates

3. For each extraction:
   `indemn meetingintelligence create --data '{"meeting_id": "{meeting.id}", "kind": "{kind}", "text": "{text}", "confidence": {confidence}}'`

4. For action items with assignees and due dates:
   `indemn actionitem create --data '{"owner_actor_id": "{owner_id}", "description": "{text}", "due_date": "{date}", "source_meeting_id": "{meeting.id}", "organization_id": "{meeting.organization_id}"}'`

5. Transition the Meeting to "processed":
   `indemn meeting transition {meeting.id} --to processed`
SKILL

indemn skill create meeting-extraction --content-from-file /tmp/meeting-extraction.md

# Overdue check skill (deterministic)
cat > /tmp/overdue-check.md << 'SKILL'
# Overdue Action Item Check

Run the stale_check capability on ActionItem:
`indemn actionitem stale-check --auto`

This marks overdue items with is_overdue=true.
The is_overdue field change triggers watches for account owners and ops.
SKILL

indemn skill create overdue-check --content-from-file /tmp/overdue-check.md
```

### Step 6: Set Up Integrations

```bash
# Org-level integrations
indemn integration create --owner org --name "Granola Bot" \
  --system-type meeting_transcription --provider granola \
  --access-roles "team_member,ops,admin"

indemn integration create --owner org --name "Indemn Slack Bot" \
  --system-type messaging --provider slack_bot \
  --access-roles "team_member,ops,admin"

# Actor-level integrations (per team member)
for member in craig kyle cam dhruv ryan george peter; do
  indemn integration create --owner actor --actor ${member}@indemn.ai \
    --name "${member}'s Gmail" --system-type email --provider gmail
  indemn integration create --owner actor --actor ${member}@indemn.ai \
    --name "${member}'s Calendar" --system-type calendar --provider google_calendar
  indemn integration create --owner actor --actor ${member}@indemn.ai \
    --name "${member}'s Slack" --system-type messaging --provider slack_user
done

# Set credentials for each (via interactive OAuth or from file)
# indemn integration set-credentials INT-XXX --from-file @creds.json
```

### Step 7: Create Associates and Human Actors

```bash
# Associates
indemn actor create --type associate --name "Meeting Processor" \
  --role meeting_processor --skills '["meeting-extraction"]' --mode reasoning

indemn actor create --type associate --name "Overdue Checker" \
  --role follow_up_checker --skills '["overdue-check"]' --mode deterministic \
  --trigger-schedule "0 8 * * *"

indemn actor create --type associate --name "Craig Gmail Sync" \
  --role sync_associate --skills '["email-sync"]' --mode deterministic \
  --trigger-schedule "*/5 * * * *" --owner-actor craig@indemn.ai

# Human actors
indemn actor create --type human --name "Craig" --email craig@indemn.ai
indemn actor add-role craig@indemn.ai --role admin
indemn actor add-role craig@indemn.ai --role account_owner
indemn actor add-auth craig@indemn.ai --method password
# Send invitation magic link...

# Repeat for all team members
```

### Step 8: Test and Iterate

```bash
# Test 1: Process a real meeting transcript
indemn meeting create --data '{"title": "GIC Weekly Sync", "scheduled_at": "2026-04-14T10:00:00Z", "status": "completed", "transcript_ref": "s3://indemn-files/meetings/gic-weekly.txt", "organization_id": "ORG-GIC"}'
# → Meeting Processor's watch should fire
# → MeetingIntelligence entities should be created
# → ActionItems should be created for commitments made

# Test 2: Overdue detection
indemn actionitem create --data '{"description": "Follow up with Julia at INSURICA", "due_date": "2026-04-10", "owner_actor_id": "ACTOR-CAM", "organization_id": "ORG-INSURICA"}'
# Wait for 8am cron → Overdue Checker runs → is_overdue=true → Cam notified

# Test 3: Health monitoring
# After 30 days of no interaction with an enterprise customer:
# → Health rule fires → health_score="at_risk" → HealthSignal created → account owner notified

# Test 4: The assistant
# Log in → type "what's the story with INSURICA?"
# → Assistant queries Company, Meetings, Interactions, HealthSignals, ActionItems
# → Returns a comprehensive briefing
```

**Iterate based on real usage.** The team uses the system daily. Issues surface:
- Missing fields → `indemn entity modify`
- Rules too aggressive/lenient → adjust thresholds
- Skills need refinement → `indemn skill update`
- New watches needed → `indemn role add-watch`
- Kernel bugs → fix in kernel code, deploy

## Phase 6 Acceptance Criteria

```
1. ALL TEAM MEMBERS HAVE ACCOUNTS AND ROLES
2. BASE UI IS THE PRIMARY SURFACE for customer intelligence
3. MEETING TRANSCRIPTS → INTELLIGENCE entities (decisions, signals, action items)
4. OVERDUE DETECTION WORKS — daily cron, notifications to owners
5. HEALTH SCORING WORKS — rules fire based on interaction recency
6. THE ASSISTANT ANSWERS "what's the story with X?" comprehensively
7. THE SYSTEM CHURNS — entity changes → watches → associates → entity changes
8. NO DAILY CRASHES — stable enough that the team relies on it
9. ISSUES FIXED IN KERNEL — bugs found here are fixed in kernel code
```

---

# Phase 7: First External Customer

## What It Produces

A real insurance business running on the OS, processing real data, with real users and real associates working the same queues. The customer's operations are modeled, not custom-coded.

## 7.1 Customer Selection

**Primary candidate: GIC Underwriters.**

Reasons from the white paper and retrace:
- Existing Indemn customer ($36K ARR, email intelligence pipeline)
- Craig built the GIC email intelligence system — deep domain knowledge
- Full GIC retrace completed against the kernel (artifact `2026-04-10-gic-retrace-full-kernel.md`)
- B2B email processing pipeline exercises the core kernel loop
- Meaningful complexity (7 entities, 6 associates, classification rules, fuzzy matching, HITL)
- Not consumer-facing (no real-time voice/chat required in the happy path)

## 7.2 Domain Modeling — 8-Step Process for GIC [G-55]

### Step 1: Understand the Business

Already deeply understood from years of working with GIC. The retrace artifact contains the complete understanding. Key aspects:

- Wholesaler/MGA processing email submissions from retail agents
- Two internal teams: CS (customer service) and underwriting
- Three carrier partners: USLI, Hiscox, Granada/GIC
- Pipeline: email arrives → extract attachments → classify type → link to submission → assess completeness → draft response → human review
- Ball-holder tracking: queue → GIC → agent → carrier → done
- Hard rules for known carriers (USLI domain → USLI type), LLM for unknowns
- Stale detection: 7+ days with 2+ follow-ups → stale

### Step 2: Define the Entities

Per the GIC retrace, create 7 domain entities:

```bash
indemn entity create Email --fields '{
  "from_address": {"type": "str", "required": true, "indexed": true},
  "to_addresses": {"type": "list"},
  "subject": {"type": "str"},
  "body": {"type": "str"},
  "has_attachments": {"type": "bool", "default": false},
  "attachments": {"type": "list"},
  "classification": {"type": "str"},
  "classification_type": {"type": "str"},
  "lob": {"type": "str"},
  "submission_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Submission"},
  "thread_id": {"type": "str"},
  "received_at": {"type": "datetime"},
  "external_id": {"type": "str", "unique": true}
}' --state-machine '{"received": ["classified"], "classified": ["linked"], "linked": ["processed"]}'

indemn entity create Extraction --fields '{
  "email_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Email"},
  "source_file": {"type": "str"},
  "extracted_data": {"type": "dict"},
  "confidence": {"type": "float"}
}'

indemn entity create Submission --fields '{
  "named_insured": {"type": "str", "required": true, "indexed": true},
  "lob": {"type": "str"},
  "stage": {"type": "str", "enum_values": ["received", "triaging", "awaiting_agent_info", "awaiting_carrier_action", "processing", "quoted", "declined", "closed"], "is_state_field": true},
  "carrier_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Carrier"},
  "agent_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Agent"},
  "external_ref": {"type": "str"},
  "effective_date": {"type": "date"},
  "data": {"type": "dict"},
  "last_activity_at": {"type": "datetime"},
  "followup_count": {"type": "int", "default": 0},
  "is_stale": {"type": "bool", "default": false},
  "ball_holder": {"type": "str"}
}' --state-machine '{"received": ["triaging"], "triaging": ["awaiting_agent_info", "awaiting_carrier_action", "processing"], "awaiting_agent_info": ["processing"], "awaiting_carrier_action": ["processing"], "processing": ["quoted", "declined"], "quoted": ["closed"], "declined": ["closed"]}' \
  --computed-fields '{"ball_holder": {"source_field": "stage", "mapping": {"received": "queue", "triaging": "gic", "awaiting_agent_info": "agent", "awaiting_carrier_action": "carrier", "processing": "gic", "quoted": "agent", "declined": "gic", "closed": "done"}}}'

indemn entity create Assessment --fields '{
  "submission_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Submission"},
  "situation_type": {"type": "str"},
  "completeness_score": {"type": "float"},
  "missing_fields": {"type": "list"},
  "next_action": {"type": "str"},
  "draft_appropriate": {"type": "bool", "default": false},
  "needs_review": {"type": "bool", "default": false}
}'

indemn entity create Draft --fields '{
  "assessment_id": {"type": "objectid", "is_relationship": true, "relationship_target": "Assessment"},
  "recipient": {"type": "str"},
  "subject": {"type": "str"},
  "body": {"type": "str"},
  "draft_type": {"type": "str"},
  "requires_approval": {"type": "bool", "default": true},
  "status": {"type": "str", "enum_values": ["generated", "pending_review", "approved", "rejected", "sent"], "is_state_field": true}
}' --state-machine '{"generated": ["pending_review"], "pending_review": ["approved", "rejected"], "approved": ["sent"]}'

indemn entity create Carrier --fields '{
  "name": {"type": "str", "required": true},
  "contact_info": {"type": "dict"},
  "binding_authority": {"type": "dict"},
  "lob_appetite": {"type": "list"}
}'

indemn entity create Agent --fields '{
  "name": {"type": "str", "required": true},
  "email": {"type": "str", "indexed": true},
  "agency": {"type": "str"},
  "producer_code": {"type": "str"}
}'
```

### Step 3: Roles and Watches

Per the GIC retrace:

```bash
indemn role create email_sync --permissions '{"read": ["Email"], "write": ["Email"]}'

indemn role create extractor --permissions '{"read": ["Email"], "write": ["Extraction"]}' \
  --watches '[{"entity_type": "Email", "event": "created", "conditions": {"field": "has_attachments", "op": "equals", "value": true}}]'

indemn role create classifier --permissions '{"read": ["Email", "Extraction"], "write": ["Email"]}' \
  --watches '[
    {"entity_type": "Email", "event": "created", "conditions": {"field": "has_attachments", "op": "equals", "value": false}},
    {"entity_type": "Extraction", "event": "created"}
  ]'

indemn role create linker --permissions '{"read": ["Email", "Submission"], "write": ["Email", "Submission"]}' \
  --watches '[{"entity_type": "Email", "event": "method_invoked", "conditions": {"field": "method", "op": "equals", "value": "auto_classify"}}]'

indemn role create assessor --permissions '{"read": ["Submission", "Email", "Extraction"], "write": ["Assessment"]}' \
  --watches '[{"entity_type": "Submission", "event": "created"}]'

indemn role create draft_writer --permissions '{"read": ["Assessment", "Submission"], "write": ["Draft"]}' \
  --watches '[{"entity_type": "Assessment", "event": "created", "conditions": {"field": "draft_appropriate", "op": "equals", "value": true}}]'

indemn role create underwriter --permissions '{"read": ["*"], "write": ["Submission", "Draft", "Assessment"]}' \
  --watches '[
    {"entity_type": "Assessment", "event": "created", "conditions": {"field": "needs_review", "op": "equals", "value": true}},
    {"entity_type": "Draft", "event": "created", "conditions": {"field": "requires_approval", "op": "equals", "value": true}},
    {"entity_type": "Submission", "event": "transitioned", "conditions": {"field": "stage", "op": "equals", "value": "triaging"}}
  ]'

indemn role create operations --permissions '{"read": ["*"], "write": ["Email", "Submission"]}' \
  --watches '[
    {"entity_type": "Submission", "event": "fields_changed", "conditions": {"field": "is_stale", "op": "equals", "value": true}},
    {"entity_type": "Draft", "event": "transitioned", "conditions": {"field": "status", "op": "equals", "value": "approved"}},
    {"entity_type": "Submission", "event": "transitioned"}
  ]'

indemn role create stale_checker --permissions '{"read": ["Submission"], "write": ["Submission"]}'
```

### Step 4: Rules and Lookups

```bash
# Classification rules
indemn rule create --entity Email --capability auto_classify --name "usli-from-domain" \
  --when '{"field": "from_address", "op": "ends_with", "value": "@usli.com"}' \
  --action set_fields --sets '{"classification": "usli_quote"}'

indemn rule create --entity Email --capability auto_classify --name "hiscox-from-domain" \
  --when '{"field": "from_address", "op": "ends_with", "value": "@hiscox.com"}' \
  --action set_fields --sets '{"classification": "hiscox_quote"}'

indemn rule create --entity Email --capability auto_classify --name "servicing-pattern" \
  --when '{"field": "subject", "op": "matches", "value": "POL-\\\\d+"}' \
  --action set_fields --sets '{"classification": "servicing_request"}'

# Veto: USLI email that's a decline
indemn rule create --entity Email --capability auto_classify --name "usli-decline-veto" \
  --when '{"all": [{"field": "from_address", "op": "ends_with", "value": "@usli.com"}, {"field": "subject", "op": "contains", "value": "Decline"}]}' \
  --action force_reasoning --forces-reasoning-reason "USLI email but subject suggests decline"

# Lookups
indemn lookup create --name usli-prefix-lob \
  --data '{"MGL": "general_liability", "XPL": "excess_personal_liability", "MSE": "special_events", "MPL": "professional_liability"}'

indemn lookup create --name carrier-name-variations \
  --data '{"USLI": "CARR-001", "United States Liability": "CARR-001", "Hiscox": "CARR-002", "Hiscox Inc": "CARR-002"}'

# Activate capabilities
indemn entity enable Email auto_classify --config '{"evaluates": "auto_classify", "sets_field": "classification"}'
indemn entity enable Submission stale_check --config '{"when": {"all": [{"field": "last_activity_at", "op": "older_than", "value": "7d"}, {"field": "followup_count", "op": "gte", "value": 2}]}, "sets_field": "is_stale", "sets_value": true}'
```

### Steps 5-8: Skills, Integrations, Test, Deploy

Skills: write markdown for each associate (email-sync, pdf-extraction, email-classification, submission-linking, situation-assessment, draft-writing, stale-check). Each skill references the entity skills for available CLI commands and describes the behavioral instructions.

Integrations: GIC's Outlook connection (org-level).

Test: `indemn org clone gic --as gic-staging`. Run the pipeline against staging with a subset of real emails. Verify classification accuracy, linking accuracy, assessment quality.

Deploy: `indemn deploy --from-org gic-staging --to-org gic --dry-run` then `--apply`.

## 7.3 Migration via Parallel Run [G-53]

### How Same Emails Go to Both Systems

**Approach: The new OS polls the same Outlook inbox as the current system, in read-only mode.**

The current GIC email intelligence system polls the Outlook inbox and marks emails as read/processed. The new OS polls the same inbox but does NOT mark emails as read — it tracks which emails it has already processed via the `external_id` field (Outlook message ID) to avoid duplicates.

```bash
# The OS email sync associate polls Outlook with a filter:
# "receivedDateTime ge {last_sync_time}"
# It creates Email entities with external_id = Outlook message ID
# If an Email with that external_id already exists, it skips (idempotent)
# It does NOT modify the Outlook messages (no read receipts, no moves)
```

Both systems process the same emails independently. The old system continues to work unchanged. The new OS processes in parallel.

### Accuracy Comparison [G-54]

```bash
# 1. Export old system decisions for a batch of emails
# (Query the existing GIC database for classification/linking results)

# 2. Run the same emails through the new OS
# (Already happening via parallel run)

# 3. Generate comparison report
indemn report compare \
  --old-system-export old-classifications.csv \
  --os-entity Email \
  --match-field external_id \
  --compare-fields classification,submission_id \
  --output comparison-report.csv
```

The comparison report shows per-email: old classification vs new classification, match/mismatch, and details for investigation.

For MVP, this can be a manual process:
1. Query old system: "for emails received this week, what were the classifications?"
2. Query new OS: `indemn email list --received-after 2026-04-07 --format json`
3. Join by external_id, compare classification fields
4. Investigate mismatches

### Cutover Criteria

From the white paper: "cut over when confident." Specific metrics:

- Classification accuracy ≥ current system (measured over 2+ weeks)
- Linking accuracy ≥ current system
- Assessment quality comparable (human review of 50+ samples)
- Processing latency ≤ current system (emails processed within minutes)
- No data loss (every email that enters is processed)
- Two weeks of parallel operation with zero critical discrepancies
- GIC team (JC, Maribel) validates the base UI is usable for their workflow

## 7.4 Org Export/Import Format [G-52]

```bash
# Export all configuration for an org (no entity instances)
indemn org export gic --output gic-config/

# Produces a directory:
gic-config/
  org.yaml              # Organization settings
  entities/             # Entity definitions
    Email.yaml
    Submission.yaml
    ...
  roles/                # Role definitions with watches
    classifier.yaml
    underwriter.yaml
    ...
  rules/                # Rules organized by entity type
    Email/
      usli-from-domain.yaml
      ...
  lookups/
    usli-prefix-lob.yaml
    carrier-name-variations.yaml
  skills/
    email-classification.md
    submission-linking.md
    ...
  actors/               # Associate configurations (not human actors)
    email-classifier.yaml
    ...
  integrations/         # Integration configs (without secrets)
    gic-outlook.yaml
    ...
  capabilities/         # Capability activations per entity
    Email.yaml
    Submission.yaml
```

What is NOT exported: entity instances (business data), messages, changes, sessions, attentions, secrets/credentials.

```bash
# Import into a new org
indemn org import --from gic-config/ --as gic-copy
```

## Phase 7 Acceptance Criteria

```
1. REAL INSURANCE WORKFLOW ON THE OS
   GIC email pipeline runs entirely on the OS — fetch, classify, link, assess, draft

2. CONFIGURATION, NOT CUSTOM CODE
   GIC modeled via entity definitions, rules, watches, skills — no kernel code changes

3. REAL USERS OPERATE IT
   GIC underwriters log in, see their queue, review assessments, approve drafts

4. HANDLES REAL VOLUME
   ~100-200 emails/day process smoothly — no queue buildup, no stuck messages

5. PARALLEL RUN VALIDATES ACCURACY
   Classification ≥ current system. Linking ≥ current system. Two weeks, zero critical mismatches.

6. THE --auto PATTERN DELIVERS VALUE
   needs_reasoning rate decreases over time as rules are added for repeated patterns

7. REPLICABLE
   Another similar customer (MGA with email pipeline) could be set up by repeating the 8-step process
```

---

## Gaps Resolved in This Document

G-52 (org export format), G-53 (parallel run mechanism), G-54 (accuracy comparison), G-55 (domain modeling as CLI sequence).
