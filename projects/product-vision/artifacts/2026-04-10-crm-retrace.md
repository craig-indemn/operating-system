---
ask: "Does Indemn's internal CRM use case work cleanly on the updated kernel, with heavy actor-level integrations, and does this validate the 'kernel is domain-agnostic' claim by running on the platform without any insurance-specific primitives?"
created: 2026-04-10
workstream: product-vision
session: 2026-04-10-a
sources:
  - type: conversation
    description: "Craig and Claude tracing Indemn's internal CRM as the third pressure test"
  - type: artifact
    description: "2026-04-10-gic-retrace-full-kernel.md (first trace — B2B insurance pipeline)"
  - type: artifact
    description: "2026-04-10-eventguard-retrace.md (second trace — consumer real-time insurance)"
  - type: artifact
    description: "2026-04-10-post-trace-synthesis.md (what the first two traces together told us)"
  - type: artifact
    description: "2026-04-10-integration-as-primitive.md (actor-level integration model)"
  - type: local
    description: "Indemn's internal context: meeting intelligence DB, customer pipeline, Slack workspace, Google Workspace"
---

# CRM Retrace — Third Pressure Test

## Purpose

GIC validated the kernel against a B2B insurance email pipeline. EventGuard validated it against consumer-facing real-time insurance with fully autonomous flows. This third trace is Indemn's own internal CRM — the customer intelligence and relationship management system Kyle wants the team to use, dog-fooded on the OS itself.

This trace is designed to test three things the first two traces didn't:

1. **The kernel is genuinely domain-agnostic.** A CRM has no insurance concepts. Organizations, Contacts, Deals, Meetings, ActionItems — these are universal business concepts. If the kernel secretly requires insurance assumptions anywhere, it shows up here.

2. **Actor-level integrations at scale.** GIC used only org-level integrations (company Outlook). EventGuard was also org-level dominated (company Stripe, company LiveKit). A CRM is the opposite — every team member has personal Gmail, personal Slack, personal Calendar. Actor-level integrations are the norm, not the exception.

3. **The "Indemn runs on the OS" dog-fooding thesis.** If the OS can run Indemn's own customer intelligence system, the platform story is credible. If not, it's not.

## What Indemn's Internal CRM Needs to Do

From the business context:
- Track all customer interactions (meetings, emails, Slack, calls) in one place
- Process meeting transcripts (Granola, Gemini) and extract decisions, quotes, objections, signals, action items
- Monitor action items and follow-ups; surface overdue items
- Detect customer health signals (churn risk, expansion opportunities, engagement drops)
- Answer "what's the story with [customer]?" questions across all the intelligence
- Produce weekly summaries and pipeline status reports
- Prepare team members for customer calls (pull context from all sources)
- Track deals through pipeline stages

These are the capabilities behind several skills that already exist in the OS (`call-prep`, `weekly-summary`, `follow-up-check`, `meeting-intelligence`, `pipeline-deals`). The question is whether they can run on top of the kernel primitives as proper system behavior, not just CLI helper skills.

## Setup

### Organization

Indemn is the org. Every team member is an Actor within this org with roles reflecting their position.

```bash
# Indemn is already the operating org
indemn org show indemn  # exists
```

### Domain entities

All generic business concepts, nothing insurance-specific:

- **Organization** — a customer org (Johnson Insurance, GIC, INSURICA, etc.). Fields: `name`, `domain`, `industry`, `status`, `tier`, `primary_owner_id`, `health_score`, `data` (flexible)
- **Contact** — a person at a customer org. Fields: `name`, `email`, `phone`, `title`, `organization_id`, `linkedin_url`, `last_interaction_at`
- **Deal** — a sales opportunity. Fields: `name`, `organization_id`, `stage`, `value`, `currency`, `owner_id`, `expected_close_date`, `probability`, `status`
- **Meeting** — a scheduled or completed meeting with customers. Fields: `title`, `scheduled_at`, `duration`, `attendees` (actor_ids + contact_ids), `organization_id`, `source` (granola, gemini, zoom, manual), `transcript_ref` (S3), `status`
- **MeetingIntelligence** — extracted insights from a meeting. Fields: `meeting_id`, `kind` (decision, quote, objection, learning, signal, action_item), `text`, `confidence`, `extracted_by_actor_id`
- **ActionItem** — a follow-up or commitment. Fields: `owner_actor_id`, `description`, `due_date`, `source` (meeting_id or interaction_id), `organization_id`, `contact_id`, `status`, `is_overdue`, `completed_at`
- **Interaction** — a touchpoint: email thread, Slack message, call. Fields: `kind` (email, slack, call, in_person), `contact_id`, `organization_id`, `direction` (inbound, outbound), `participants` (actor_ids), `occurred_at`, `content_preview`, `source_integration_id`, `source_ref`, `full_content_ref` (S3 for large content)
- **HealthSignal** — a detected change in customer health. Fields: `organization_id`, `kind` (churn_risk, expansion, engagement_drop, champion_lost), `severity`, `detected_at`, `basis` (what led to the signal), `status`
- **Note** — free-form note attached to an Organization or Contact. Fields: `subject_type`, `subject_id`, `author_actor_id`, `content`, `created_at`

Nothing here is insurance-specific. These entities would work for any B2B company's customer intelligence system.

### Integrations (primitive #6) — this is the interesting part

**Org-level integrations** (shared across the team):

```bash
# Meeting transcription services (org-wide bots)
indemn integration create --owner org --name "Granola Bot" \
  --system-type meeting_transcription --provider granola \
  --access-roles "team_member,ops,admin"

indemn integration create --owner org --name "Gemini Meet Bot" \
  --system-type meeting_transcription --provider gemini \
  --access-roles "team_member,ops,admin"

# Slack workspace bot for monitoring shared channels
indemn integration create --owner org --name "Indemn Slack Bot" \
  --system-type messaging --provider slack_bot \
  --access-roles "team_member,ops,admin"

# Linear for engineering-linked customer work
indemn integration create --owner org --name "Indemn Linear" \
  --system-type project_management --provider linear \
  --access-roles "engineering,admin"

# Pipeline API / meetings database
indemn integration create --owner org --name "Meetings DB" \
  --system-type analytics_database --provider postgres \
  --access-roles "team_member,ops,admin"
```

**Actor-level integrations** (personal to each team member):

```bash
# Craig's personal credentials
indemn integration create --owner actor --actor craig@indemn.ai \
  --name "Craig's Gmail" --system-type email --provider gmail

indemn integration create --owner actor --actor craig@indemn.ai \
  --name "Craig's Calendar" --system-type calendar --provider google_calendar

indemn integration create --owner actor --actor craig@indemn.ai \
  --name "Craig's Slack" --system-type messaging --provider slack_user

indemn integration create --owner actor --actor craig@indemn.ai \
  --name "Craig's Drive" --system-type file_storage --provider google_drive

# Kyle's personal credentials
indemn integration create --owner actor --actor kyle@indemn.ai \
  --name "Kyle's Gmail" --system-type email --provider gmail
# ... etc

# Cam's personal credentials
indemn integration create --owner actor --actor cam@indemn.ai \
  --name "Cam's Gmail" --system-type email --provider gmail
# ... etc
```

For 15 team members × 4 integration types = **60 actor-level integrations**. This is the scale case for the ownership model introduced in the integration primitive artifact.

### Methods activated on entities

```bash
indemn entity add-method Meeting extract-intelligence --evaluates extraction-rule --calls-adapter llm_extract
indemn entity add-method ActionItem stale-check --when '{"all": [{"field": "due_date", "op": "older_than", "value": "0d"}, {"field": "status", "op": "not_equals", "value": "completed"}]}' --sets-field is_overdue
indemn entity add-method Organization health-score --evaluates health-scoring-rule
indemn entity add-method Organization compile-briefing --aggregates "meetings,interactions,action_items,health_signals,deals"
indemn entity add-method Interaction sync-from-source --system-type email
indemn entity add-method Meeting sync-from-source --system-type meeting_transcription
```

### Rules (Indemn-specific business rules)

```bash
# Health scoring rules
indemn rule create --entity Organization --org indemn \
  --when '{"all": [{"field": "last_interaction_at", "op": "older_than", "value": "30d"}, {"field": "tier", "op": "in", "value": ["enterprise", "strategic"]}]}' \
  --action set-fields --sets '{"health_score": "at_risk"}'

indemn rule create --entity Organization --org indemn \
  --when '{"all": [{"field": "last_interaction_at", "op": "older_than", "value": "90d"}]}' \
  --action set-fields --sets '{"health_score": "churn_risk"}'

# Action item priority rules
indemn rule create --entity ActionItem --org indemn \
  --when '{"all": [{"field": "due_date", "op": "within", "value": "3d"}, {"field": "status", "op": "not_equals", "value": "completed"}]}' \
  --action set-fields --sets '{"priority": "high"}'
```

### Roles with watches

Team members have roles representing their position plus an "owner" role for customer accounts they own:

```bash
indemn role create team_member \
  --permissions "read:Organization,read:Contact,read:Meeting,read:Interaction,read:ActionItem,read:HealthSignal,write:ActionItem,write:Note" \
  --watches '[{"entity": "ActionItem", "event": "fields_changed", "when": {"field": "owner_actor_id", "op": "equals", "value": "self"}}]'

indemn role create account_owner \
  --permissions "read:all,write:Organization,write:Contact,write:Deal,write:HealthSignal" \
  --watches '[
    {"entity": "HealthSignal", "event": "created", "scope": "actor_context"},
    {"entity": "ActionItem", "event": "fields_changed", "when": {"field": "is_overdue", "op": "equals", "value": true}, "scope": "actor_context"},
    {"entity": "Meeting", "event": "created", "scope": "actor_context"}
  ]'

indemn role create ops \
  --permissions "read:all,write:Organization,write:ActionItem,write:HealthSignal" \
  --watches '[
    {"entity": "HealthSignal", "event": "created", "when": {"field": "severity", "op": "in", "value": ["high", "critical"]}},
    {"entity": "ActionItem", "event": "fields_changed", "when": {"field": "is_overdue", "op": "equals", "value": true}, "coalesce": {"strategy": "by_correlation_id", "window": "15m"}}
  ]'

indemn role create executive \
  --permissions "read:all" \
  --watches '[
    {"entity": "HealthSignal", "event": "created", "when": {"field": "kind", "op": "equals", "value": "churn_risk"}, "when": {"field": "severity", "op": "equals", "value": "critical"}},
    {"entity": "Deal", "event": "stage_changed", "when": {"field": "to", "op": "equals", "value": "closed_won"}}
  ]'

indemn role create meeting_processor \
  --permissions "read:Meeting,read:MeetingTranscript,write:MeetingIntelligence,write:ActionItem" \
  --watches '[{"entity": "Meeting", "event": "created", "when": {"field": "transcript_ref", "op": "exists"}}]'

indemn role create health_monitor \
  --permissions "read:Organization,read:Interaction,write:Organization,write:HealthSignal" \
  --watches '[]'  # schedule-triggered only

indemn role create personal_sync \
  --permissions "read:Meeting,write:Meeting,read:Interaction,write:Interaction" \
  --watches '[]'  # schedule-triggered only
```

Note the `scope: actor_context` on account_owner's watches — they should only see events for organizations they own, not everyone's. Same qualifier we surfaced in the EventGuard trace.

### Human actors

```bash
indemn actor create --type human --name "Craig Certo" --email craig@indemn.ai
indemn actor add-role craig@indemn.ai --role team_member
indemn actor add-role craig@indemn.ai --role account_owner  # for accounts Craig owns
indemn actor add-role craig@indemn.ai --role engineering

indemn actor create --type human --name "Kyle Geoghan" --email kyle@indemn.ai
indemn actor add-role kyle@indemn.ai --role team_member
indemn actor add-role kyle@indemn.ai --role account_owner
indemn actor add-role kyle@indemn.ai --role executive

indemn actor create --type human --name "Cam Torstenson" --email cam@indemn.ai
indemn actor add-role cam@indemn.ai --role team_member
indemn actor add-role cam@indemn.ai --role account_owner
indemn actor add-role cam@indemn.ai --role executive
# etc for 15 team members
```

### Associates

Some shared across the org, some personal to team members:

```bash
# Org-level associates (shared)
indemn actor create --type associate --name "Meeting Intelligence Processor" \
  --role meeting_processor --skill meeting-extraction --mode reasoning

indemn actor create --type associate --name "Health Monitor" \
  --role health_monitor --trigger "schedule:0 */6 * * *" \
  --skill health-scoring --mode hybrid

indemn actor create --type associate --name "Follow-up Checker" \
  --role ops --trigger "schedule:0 8 * * *" \
  --skill overdue-action-items --mode hybrid

indemn actor create --type associate --name "Weekly Summary Writer" \
  --role ops --trigger "schedule:0 8 * * 1" \
  --skill weekly-summary --mode reasoning
```

**Personal sync associates** — this is where it gets interesting.

Each team member who wants their personal email/calendar/slack synced into the CRM has personal sync associates bound to them:

```bash
# Craig's personal Gmail sync — uses Craig's personal Gmail integration
indemn actor create --type associate --name "Craig's Gmail Sync" \
  --owner-actor craig@indemn.ai \
  --role personal_sync \
  --trigger "schedule:*/15 * * * *" \
  --skill personal-email-sync \
  --mode hybrid

# Craig's calendar sync
indemn actor create --type associate --name "Craig's Calendar Sync" \
  --owner-actor craig@indemn.ai \
  --role personal_sync \
  --trigger "schedule:0 */1 * * *" \
  --skill personal-calendar-sync \
  --mode hybrid
```

**Key question that surfaces here**: when Craig's Gmail Sync associate runs, it needs to use Craig's personal Gmail integration (owned by Craig, actor_id=craig@indemn.ai). But the associate itself has its own actor_id (the sync associate's ID). By default, the credential resolver would look for integrations owned by the sync associate, not by Craig.

**More on this in the "What Surfaced" section** — this is the main finding of the CRM trace.

## Key Flows

### Flow 1: Meeting intelligence processing (org-level integration)

1. Cam has a meeting with Julia (INSURICA). Meeting happens via Google Meet.
2. Granola bot (org-level integration) attends the meeting, transcribes it, and posts a webhook to the OS at completion.
3. Webhook handler looks up the Granola Integration, validates the signature via its secret_ref, parses the webhook into entity operations.
4. Creates Meeting entity: `{title, scheduled_at, duration, attendees: [cam@indemn.ai, contact_julia_insurica], organization_id: ORG-INSURICA, source: "granola", transcript_ref: "s3://..."}`.
5. Meeting:created event → `meeting_processor` watch matches.
6. Meeting Intelligence Processor claims, loads meeting + transcript (downloads from S3).
7. Calls `indemn meeting extract-intelligence MEET-091`.
8. The extract-intelligence method runs LLM extraction using the meeting-extraction skill as context.
9. Produces multiple MeetingIntelligence entities (each a decision, quote, objection, signal, etc.), plus ActionItem entities for each follow-up commitment identified in the transcript.
10. **Multi-entity transaction**: Meeting status updated to "processed" + N MeetingIntelligence entities created + M ActionItem entities created. All atomic.
11. Events emitted: Meeting:method_invoked[extract-intelligence], N MeetingIntelligence:created, M ActionItem:created.
12. Each ActionItem:created event has `owner_actor_id` set (extracted by the LLM from the transcript — "Cam will follow up with Julia about Salesforce integration by Friday" → owner=cam@indemn.ai, due_date=calculated).
13. Cam's `team_member` watch matches ActionItem events where owner_actor_id = his ID. The item appears in his queue.

### Flow 2: Personal email sync (actor-level integration)

1. Every 15 minutes, Craig's Gmail Sync associate is activated by its schedule.
2. Scheduled trigger creates a queue item targeting the sync associate's role.
3. Temporal workflow claims it, loads Craig's Gmail Sync skill.
4. Skill says: "Run `indemn email fetch-new` scoped to Craig's personal Gmail, since the last sync timestamp."
5. **Here is where the credential resolution question arises.** The associate invokes `indemn email fetch-new`. The `fetch-new` method on Email needs to resolve the right Integration.
6. **Proposed resolution** (new from this trace): associates have an `owner_actor_id` field. When the associate invokes an entity method that resolves an Integration, the resolver uses the owner's context:
   - First: does the owner (Craig) have a personal Integration of the required type? → use it.
   - Second: does the org have an Integration of the required type that the associate's role permits? → use it.
   - Third: fail.
7. With owner resolution, the sync associate finds Craig's Gmail integration, fetches credentials from `/indemn/prod/actor/craig@indemn.ai/integration/...`, and uses them.
8. Adapter pulls new emails from Craig's Gmail.
9. For each email: the sync associate runs pattern matching to identify whether it's related to an Indemn customer (from_address matches a Contact, to_address matches a Contact, etc.).
10. If customer-related: creates an Interaction entity tied to the Contact and Organization. Transaction: N Interaction entities created + Contact.last_interaction_at updated + Organization.last_interaction_at updated.
11. If NOT customer-related (Craig's personal email, subscription confirmations, etc.): discard. Do not create an Interaction. The data stays in Craig's Gmail.
12. Sync updates its last-run timestamp (stored on the associate or in a sync state entity).
13. Interaction:created events propagate to watches on account_owner role (for organizations they own).

**Privacy boundary**: Craig's Gmail is private to him. The sync associate has access BECAUSE it's owned by Craig and uses his credentials. But the resulting Interaction entities (derived from his emails) are shared within the org — other team members with read access to Organization can see that Craig emailed Julia last Tuesday. This is correct — Indemn wants shared customer awareness — but the underlying full email body is not shared (only the Interaction metadata: "Craig emailed julia@insurica.com about Salesforce integration" with a content_preview and a full_content_ref in S3 scoped to... where?).

**Another question that surfaces**: does the full content go to S3 at an org-shared path or an actor-scoped path? If org-shared, anyone with Interaction read access can pull it. If actor-scoped, only Craig can retrieve the full email. This is a privacy design decision the kernel should support but not mandate.

### Flow 3: Overdue action items (scheduled bulk update → watch coalescing)

1. Every morning at 8am, the Follow-up Checker scheduled associate runs.
2. Calls `indemn action-item stale-check --org indemn`.
3. The stale-check method finds all ActionItems where `due_date < today AND status != completed`.
4. **Bulk update in one transaction**: sets `is_overdue=true` on matching items. All committed atomically.
5. N ActionItem:fields_changed[is_overdue=true] events emitted. All share the same correlation_id (from the scheduled task's execution).
6. The ops role has a coalesced watch on this — a single queue item appears: "47 action items became overdue today" with drill-down.
7. Each account_owner's `actor_context` watch also fires for their own items. Those are NOT coalesced by ops's strategy — they're scoped per-owner. Cam sees "3 of your action items are now overdue." Kyle sees his own set.
8. Ops reviews the overall list and flags the most concerning ones. Account owners review their personal lists and take action.

**This flow exercises**: scheduled capabilities, bulk operations pattern, watch coalescing, actor-context scoping — three of the items from the post-trace synthesis.

### Flow 4: Health monitoring (scheduled hybrid associate)

1. Every 6 hours, Health Monitor runs.
2. For each Organization in the org: calls `indemn organization health-score ORG-001`.
3. The health-score method evaluates rules: if last_interaction > 30d and tier is enterprise → "at_risk". If last_interaction > 90d → "churn_risk".
4. If the score changes from previous value, update the Organization AND create a HealthSignal entity explaining the detection.
5. HealthSignal:created events propagate to:
   - Ops role (for high/critical signals) — sees in their queue
   - Executive role (for critical churn risks) — sees in their queue
   - Account owner's role with actor_context scope — only their own organizations' signals

### Flow 5: "What's the story with INSURICA?" (cross-entity query)

This is a READ operation, not a pipeline flow. Someone in the UI (or CLI) asks the CRM assistant about a customer.

1. User interaction: Kyle asks "what's the story with INSURICA?" via the chat interface (or `indemn brief ORG-INSURICA`).
2. An interactive associate (CRM Assistant) receives the query — this is a real-time interaction, so channel activation direct invocation applies.
3. The associate's skill tells it to call `indemn organization compile-briefing ORG-INSURICA`.
4. The compile-briefing method aggregates:
   - Last N meetings with their intelligence
   - Recent interactions (email, slack, calls)
   - Open action items
   - Active health signals
   - Pipeline deals in progress
   - Recent notes
5. Returns a structured context blob.
6. The associate's skill instructs the LLM to synthesize the briefing into natural language.
7. The LLM produces a narrative: "INSURICA — your biggest expansion opportunity. Julia Hester is the champion. Last meeting 3 days ago with Cam about Salesforce integration. One action item overdue (follow up on renewal template by 2026-04-08). Engagement dropped 30% last month. Health score: at_risk."
8. Returned to the user.

**This exercises**: real-time interaction, cross-entity aggregation as a kernel capability, skill-driven LLM synthesis. All read-only — no entity mutations, no watches fire.

**Important observation**: most of what a CRM does is READ operations, not write pipelines. GIC and EventGuard were write-heavy (ingest → process → emit). CRM is read-heavy (ask → aggregate → present). The kernel handles this fine — entity queries, method invocations that aggregate, skills that synthesize — but the CRM use case highlights that watches aren't the only valuable mechanism. Direct queries via the CLI/API are equally important, and they're already supported by the auto-generated API/CLI from entity definitions.

### Flow 6: Slack workspace bot (org-level) + personal Slack (actor-level) coexistence

1. **Workspace bot** monitors customer channels that both Indemn team members and customers are in (#indemn-insurica-shared, say). When a customer sends a message, the bot sees it via the workspace app token.
2. Bot creates an Interaction entity tied to the Contact and Organization, participants include the Indemn team members in the channel.
3. Interaction appears in the shared customer timeline.

4. **Personal Slack sync** captures DMs between Craig and Julia (customer). The workspace bot can't see DMs — only Craig's personal token can. Craig's personal Slack sync associate runs on his credentials.
5. It creates Interaction entities from Craig's DMs with customer contacts.
6. These Interactions contribute to the shared Org timeline (metadata), but the full content is scoped per the privacy design.

**This exercises**: both org-level and actor-level integrations feeding the same entity type (Interaction), with different authorization. The Integration primitive handles this naturally — each Integration has its own owner. The Interaction entity has a source_integration_id field that records which Integration produced it.

## What Held Up

1. **The kernel is domain-agnostic.** None of the entities (Organization, Contact, Deal, Meeting, MeetingIntelligence, ActionItem, Interaction, HealthSignal, Note) are insurance-specific. They're generic business concepts. The kernel primitives (Entity, Message, Actor, Role, Organization, Integration) work identically. Zero insurance assumptions surfaced. The "kernel is domain-agnostic" claim holds under this test.

2. **Integration primitive handles org-level AND actor-level at scale.** 15 team members × 4 integration types = 60 actor-level integrations, coexisting with 5-10 org-level integrations. The owner field on Integration is the only thing that distinguishes them. Credential resolution works by owner context. No new primitive needed — the pattern was designed right.

3. **Watches handle cross-cutting signal propagation.** ActionItem overdue → ops + account_owner. HealthSignal created → ops + executive + account_owner. Each role watches what it cares about; no central routing logic. Multi-actor visibility emerges from watches, not from explicit broadcast.

4. **Watch coalescing saves ops from overdue-item spam.** Ops role uses coalesced watch for overdue ActionItems — one batched queue item instead of 47. Account_owners use unscoped watches (but `actor_context` scoped) so they see only their own.

5. **Scheduled + event-driven workflows coexist naturally.** Meeting ingestion is event-driven (webhook → watch → process). Health monitoring is scheduled (cron → bulk update → emit events → watches propagate). Same actor model for both.

6. **Read-heavy operations work via direct CLI/API alongside watch-driven writes.** The "what's the story with X?" flow is a read aggregation that doesn't go through watches. The kernel's auto-generated CRUD + custom aggregation methods handle this cleanly. CRM use case validates that watches are for async reactive flows, not the universal mechanism.

7. **Actor-context scoping is needed across multiple flows.** Same `scope: actor_context` qualifier proposed from EventGuard applies here: account owners should see events for their own organizations, not everyone else's. This is a consistent need across traces, confirming it's a real kernel addition.

8. **Dog-fooding is credible.** The full Indemn CRM story — meeting intelligence, pipeline management, customer health, follow-up tracking, briefings — can be built as domain entities + per-org rules + skills + scheduled associates on the kernel without any insurance-specific infrastructure. If it works for GIC (insurance) AND EventGuard (insurance) AND Indemn's own CRM (not insurance), the platform story is credible.

## What Surfaced

### 1. Associates acting on behalf of a human — the owner_actor_id pattern — REAL ARCHITECTURAL ADDITION

**The problem**: Craig's Gmail Sync associate needs to use Craig's personal Gmail integration (owned by Craig). But the associate has its OWN actor_id. By default, credential resolution only looks at integrations owned by the calling actor. The associate wouldn't find Craig's integrations.

**Classification**: Real architectural addition. Not covered by the current Integration design. Needed for any scenario where an associate acts on a human's behalf using their personal credentials.

**Proposed resolution**: Associates gain an optional `owner_actor_id` field. This is separate from the associate's own actor_id. When the associate invokes an entity method that resolves an Integration, the resolver uses the owner's context in addition to the associate's own:

1. Does the associate (via its own actor_id) have a personal Integration of this type? → use it.
2. **NEW**: Does the associate's `owner_actor_id` (if set) have a personal Integration of this type? → use it. Audit records "associate X used owner Y's integration Z."
3. Does the org have an Integration of this type that the associate's role permits? → use it.
4. Fail.

This is a small addition to the Integration resolver and the Actor schema. It enables:
- Personal sync associates (the primary CRM use case)
- Assistant-style associates that act on behalf of a user
- Delegation patterns where a human authorizes an associate to use specific credentials

**Audit and consent**: when an associate is created with an owner_actor_id, the owner must consent. The consent is recorded (changes collection). Rotating the associate or transferring ownership requires re-consent. Revocation is immediate — the owner can remove the binding at any time.

**This should be documented in the Integration primitive artifact** as an extension to the credential resolution model.

### 2. Privacy scoping for content derived from personal integrations

**The problem**: Craig's personal email sync creates Interaction entities in the shared CRM. The Interaction metadata (from, to, subject, timestamp, content_preview) is shared with the team. But the full email body (stored in S3 via `full_content_ref`) — who can access it?

Options:
- **Org-shared**: full content in an org-scoped S3 path, anyone with Interaction read permission can fetch. Simplest but exposes Craig's full emails to the team.
- **Actor-scoped**: full content in an actor-scoped S3 path, only Craig (the source) can fetch. Privacy-preserving but limits the "what's the story with X" use case for other users.
- **Configurable**: Integration declares a privacy policy — metadata shared, content owner-only; or fully shared; etc.

**Classification**: Design decision, not a kernel addition. The kernel needs to support all these options via the owner field and access rules on the source Integration. Indemn picks a policy per Integration type (personal email: metadata-shared, content-owner-only; workspace Slack: fully shared; etc.).

**Finding**: the spec should explicitly address content visibility scoping for entities derived from personal integrations. Recommended default: **metadata shared, full content owner-scoped.** This preserves the team's shared awareness (who talked to whom about what) without exposing the full content of personal communications.

### 3. Read-heavy operations warrant a "query capability" pattern

**The observation**: CRM is dominated by read aggregations — "what's the story with X?", "who talked to INSURICA recently?", "which action items are overdue across the team?". These are queries across multiple entities, not pipelines.

GIC and EventGuard were dominated by writes (ingest → process → emit). CRM balances writes and reads.

**Finding**: the architecture currently has `entity method` as the mechanism for anything non-trivial. A query like "compile briefing" is a method on Organization that aggregates from many other entities. This works, but it's worth naming the pattern: **query capabilities** are entity methods that read across the entity graph and return a structured result. They don't generate events (no writes). They're parameters into skills for real-time interaction (like the CRM Assistant).

Not a new primitive, but a clarification: entity methods can be read-only aggregations, not just state-modifying operations. The `@exposed` decorator already allows this.

### 4. Cross-actor queue visibility for ops/leadership

**The observation**: Ops wants to see overdue action items across ALL owners, not just their own. Executives want to see deals closing and health risks across all accounts. These are cross-cutting visibility needs that differ from actor_context scoping.

**Finding**: the kernel already supports this via unscoped watches. Ops role has `{"entity": "ActionItem", ..., "coalesce": ...}` with no scope qualifier — meaning it matches events org-wide. Account_owner has the same event type with `scope: actor_context` — meaning they see only their own.

**Classification**: Not a new mechanism. The existing watch model handles both cases. Same watch structure, different scope (or no scope). Worth naming explicitly: watches default to org-wide (all matching events); `scope: actor_context` narrows to events related to the claiming actor's context. This is a clean semantic.

### 5. Entity derived from multiple sources

**The observation**: A Contact (Julia at INSURICA) is informed by meetings (transcript extractions), emails (Craig's personal Gmail sync), Slack (workspace bot + personal DMs), and manual notes. Multiple source integrations feed the same Contact. Multiple Interactions link to the same Contact. The Contact's `last_interaction_at` updates from whichever source is most recent.

**Classification**: Already handled by the existing primitives. Interaction has a `source_integration_id` field that records provenance. The Contact is updated by whichever actor most recently processed an interaction. No new mechanism needed.

**Finding**: worth documenting the pattern — "entities enriched from multiple sources" is common in CRM-style systems. The pattern is: domain entity (Contact) with fields updated by watch-triggered actors processing source-specific events (Interaction). Not a new primitive, but a pattern the spec should show as an example.

## What's Still Domain, Not Kernel

All of the following are Indemn-specific configuration, not kernel primitives:

- The specific entities (Organization, Contact, Deal, Meeting, etc.)
- Health scoring thresholds (30d, 90d)
- Meeting intelligence extraction categories (decision, quote, objection, signal)
- Follow-up overdue rules
- Weekly summary template
- Skill for "compile briefing"
- Which fields the LLM extracts from meeting transcripts

None of this is in the kernel. All of this is data + skills + rules in MongoDB, scoped to the Indemn org.

## Verdict

**The kernel holds up for CRM.** Three workload types now traced cleanly: B2B insurance pipeline (GIC), consumer real-time autonomous insurance (EventGuard), and generic B2B customer intelligence (CRM). Three very different shapes, zero primitive changes required.

**One new architectural addition surfaced:**

- **Associates with `owner_actor_id` and credential resolution through the owner's context.** Needed for any "associate acting on behalf of a user" pattern. This is the CRM-specific version of the mid-conversation event delivery finding from EventGuard — both are about how associates interact with the context around them.

**Several things confirmed as cross-cutting needs:**
- `scope: actor_context` on watches applies here too (account owners see only their own organizations' events)
- Watch coalescing applies here too (ops sees batched overdue items)
- Bulk operations apply here too (scheduled bulk updates to ActionItems and Organizations)
- Inbound webhook dispatch applies here too (Granola, Gemini webhooks for meeting transcripts)

Every design item from the post-trace synthesis is used in CRM. None are single-trace quirks. They're real kernel requirements.

**One design decision surfaced:**
- Privacy scoping for content derived from personal integrations (metadata vs full content visibility). This is a policy decision per Integration, not a kernel addition.

**Two patterns worth naming in the spec:**
- Query capabilities (entity methods as read-only aggregations)
- Multi-source entity enrichment (same entity informed by multiple source Integrations)

## Cross-Trace Comparison (All Three)

| Dimension | GIC | EventGuard | CRM |
|-----------|-----|-----------|-----|
| Domain | Insurance (B2B MGA) | Insurance (consumer embedded) | Generic B2B intelligence |
| Workload shape | Email-driven batch-burst | Real-time consumer + webhooks | Mixed: scheduled + event-driven + read-heavy |
| HITL | Heavy (JC, Maribel) | None in happy path | Heavy (team members are primary actors) |
| Primary integrations | Outlook | Stripe, LiveKit, SendGrid, Mint, Twilio | Granola/Gemini, Slack, Gmail/Calendar/Drive, Linear, Postgres |
| Integration ownership | 100% org-level | 100% org-level | Mixed (5-10 org + 60 actor-level) |
| Real-time | Optional (voice extension) | Core (chat + voice) | Optional (CRM Assistant chat) |
| Autonomous flow | Partial (happy path automated, review at key points) | Full (end-to-end, no humans) | Partial (humans drive, associates augment) |
| Distribution surfaces | One setup | 351 deployments | None (internal tool) |
| Primary interaction mode | Write pipeline | Write pipeline + real-time | Mixed write/read |
| Kernel additions surfaced | Watch coalescing, ephemeral locks, pipeline dashboards, queue health | Actor-context watches + Temporal signals, inbound webhook dispatch, bulk operations | `owner_actor_id` on associates, privacy scoping for personal-integration-derived content |
| Domain-agnostic validation | Partial (still insurance) | Partial (still insurance) | **Full (no insurance concepts at all)** |

Every row is different. The kernel is the same. That's the story.

## What This Trace Adds to the Open Design Work

Adding one item to the post-trace synthesis's list of open design work:

**11. Associates with owner_actor_id for delegated credential access.** Associates can be bound to a human actor. When the associate invokes an entity method that resolves an Integration, the resolver checks the owner's personal Integrations in addition to the associate's own. Audit records the delegation. Consent required on creation, revocable by the owner.

This is architecturally simple — one field on Actor, one extra check in the resolver, audit logging in the changes collection. Small addition, but real.

Also adding one new documentation item:

**12. Content visibility scoping for personal-integration-derived entities.** When an entity (like Interaction) is created from a personal Integration's data, the default should be: metadata shared with the team, full content owner-scoped (stored in an actor-scoped S3 path). Configurable per Integration if different policies are needed (workspace Slack is fully shared; personal DMs are owner-scoped). Documentation update to the Integration primitive artifact and/or a new privacy-model artifact.

## Recommendation

**Three traces is enough.** The kernel is clearly stable. Doing a fourth would be diminishing returns — we've covered B2B pipeline, consumer real-time, and generic domain with heavy actor-level integrations. No more fundamentally new workload shapes come to mind that would stress different primitives.

**What's next, in order:**

1. Design sessions on the open architectural items (now 11 total, with the owner_actor_id addition from this trace). Start with actor-context watches + Temporal signal delivery (the biggest gap from EventGuard) since it also applies to CRM.
2. Documentation updates (inbound webhook dispatch, internal vs external entities, computed field scope, content visibility scoping, associate owner_actor_id pattern).
3. Simplification pass across everything.
4. Spec writing.

The kernel is ready to be encapsulated. The remaining work is mechanism detail and documentation, not architecture.
