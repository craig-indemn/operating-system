# Notes: 2026-04-14-impl-spec-phase-6-7-consolidated.md

**File:** projects/product-vision/artifacts/2026-04-14-impl-spec-phase-6-7-consolidated.md
**Read:** 2026-04-16 (full file — 708 lines)
**Category:** spec

## Key Claims

- Phase 6 = Dog-Fooding (Indemn running its own operations on the OS). Phase 7 = First External Customer (GIC).
- "These are operational phases, not code-specification phases. The implementation detail here is: what entities to define, what watches to configure, what skills to author, how to validate, and how to migrate."
- Phase 6 uses the CRM retrace as blueprint — complete domain model for Indemn's internal operations.
- Phase 6 entities: Company (renamed from "Organization" to avoid kernel collision), Contact, Deal, Meeting, MeetingIntelligence, ActionItem, Interaction, HealthSignal, Note.
- Phase 6 roles: team_member, account_owner, meeting_processor (AI), health_monitor (AI), follow_up_checker (AI), ops.
- Phase 6 integrations: org-level Granola Bot, Slack Bot; actor-level per-team-member Gmail, Calendar, Slack.
- Phase 7 candidate: GIC Underwriters (existing customer, $36K ARR, email intelligence pipeline).
- Phase 7 entities: Email, Extraction, Submission, Assessment, Draft, Carrier, Agent.
- Phase 7 migration via parallel run — OS polls same Outlook inbox in read-only mode, tracks via `external_id` for idempotency.
- Cutover criteria: classification accuracy ≥ current system, linking accuracy ≥ current system, assessment quality comparable, zero data loss, two weeks parallel operation.
- Org export format is a YAML directory (entities/, roles/, rules/{entity}/, skills/*.md, lookups/, actors/, integrations/, capabilities/).

## Architectural Decisions

- **Naming collision resolution**: Kernel already has `Organization` entity (multi-tenancy scope). CRM customer orgs use `Company` to avoid collision. This is a Phase 6 decision, not a Phase 0 decision.
- Phase 6 applies the white paper's 8-step domain modeling process as a concrete CLI sequence.
- Meeting intelligence extraction is LLM-based (mode: reasoning). Overdue check is deterministic.
- Scheduled associates: Overdue Checker (`0 8 * * *`), Craig Gmail Sync (`*/5 * * * *`).
- Gmail sync associates are owner-bound (`--owner-actor craig@indemn.ai`), using owner's Integration credentials.
- Phase 7 reuses Phase 6's pattern: define entities, configure roles + watches, create rules and lookups, write skills, set up integrations, test in staging, deploy to production.
- Org clone/diff/deploy for staging → production promotion.
- "What is NOT exported: entity instances (business data), messages, changes, sessions, attentions, secrets/credentials."
- Hard rules (USLI domain, Hiscox domain) + veto rules (USLI subject contains "Decline" → force_reasoning).
- Lookup tables for carrier/LOB mappings.

## Layer/Location Specified

**This spec is largely OPERATIONAL — it's about configuring data in the deployed OS, not adding code.**

No kernel-side layer additions are specified. All activity is CLI-based configuration:
- Entity definitions created via `indemn entity create` (stored in MongoDB entity_definitions collection)
- Rules created via `indemn rule create` (stored in MongoDB rules collection per org)
- Roles created via `indemn role create` (stored in MongoDB roles collection per org)
- Skills created via `indemn skill create` (stored in MongoDB skills collection)
- Integrations created via `indemn integration create` (stored in MongoDB integrations collection)
- Associates created via `indemn actor create --type associate` (stored in MongoDB actors collection)

**No new code locations specified.** Phase 6-7 relies entirely on the kernel built in Phases 0-5 plus CLI commands.

**Dependencies on earlier phases:**
- Phase 6 depends on Phase 2 (associate execution) for the AI roles.
- Phase 6 depends on Phase 3 (integration adapters) for Gmail, Calendar, Slack adapters.
- Phase 6 depends on Phase 4 (Base UI) for team members to operate.
- Phase 7 depends on Phase 2 for AI associates in the pipeline.
- Phase 7 depends on Phase 3 for Outlook integration.

**Phase 6-7 does NOT add or change any code layers.** If Finding 0 is present in earlier phases (it is — in Phase 2 `kernel/temporal/activities.py` + Phase 4 `kernel/api/assistant.py`), Phase 6-7 relies on the deviated code and doesn't fix it.

## Dependencies Declared

- All prior-phase dependencies (Temporal, MongoDB, CLI, auth, integrations, adapters)
- Gmail OAuth for actor-level email sync
- Google Calendar OAuth
- Slack user tokens (per team member) and bot token (org-level)
- Granola Bot integration (custom adapter implied)
- Outlook for GIC email polling (reuses Phase 3 Outlook adapter)
- S3 for meeting transcript storage

## Code Locations Specified

No new code locations. Phase 6-7 works entirely through:
- Existing kernel CLI commands
- Existing kernel API endpoints
- Existing adapters from Phase 3
- Existing Base UI from Phase 4
- Skills stored in MongoDB

Any operational code (e.g., a custom Granola Bot adapter) would be added as a new adapter in `kernel/integration/adapters/` following the Phase 3 pattern.

## Cross-References

- 2026-04-13-white-paper.md
- 2026-04-14-impl-spec-gaps.md
- 2026-04-10-crm-retrace.md (CRM modeled on the kernel)
- 2026-04-10-gic-retrace-full-kernel.md (GIC modeled on the kernel)
- 2026-04-13-remaining-gap-sessions.md (domain modeling process, operations, transition)

## Open Questions or Ambiguities

**Pass 2 observations:**

- **No Finding 0-class layer deviations added by this spec.** It's an operational phase spec that relies on Phases 0-5 being correct.
- **Phase 6-7 does NOT fix Finding 0.** If agent execution stays in `kernel/temporal/activities.py`, Phase 6 associates (Meeting Processor, etc.) and Phase 7 associates (Classifier, etc.) all run inside the kernel's Temporal Worker, not in harnesses.
- **Phase 6 assistant usage** ("what's the story with INSURICA?") depends on the Phase 4 assistant having tools. Per the comprehensive audit, the assistant has no tools (Finding 2). Without resolution of Finding 0/2, the Phase 6 assistant test case (#6 in acceptance criteria: "THE ASSISTANT ANSWERS 'what's the story with X?' comprehensively") cannot be met.
- **Phase 6's daily dog-fooding test** is what would have surfaced Finding 0 — if Indemn tried to use the assistant daily, the lack of tools would have been noticed immediately. Per the comprehensive audit, Phase 6 hasn't been implemented yet — which is why Finding 0 wasn't surfaced by dog-fooding.
- **No new harnesses specified here.** If chat-harness or async-deepagents harnesses are needed for proper agent execution, they would need to be added in an earlier phase or as a retrofit. Phase 6-7 doesn't include them.

**Pass 2 conclusion for this spec**: Phase 6-7 is operational and adds no architectural deviations. It inherits Finding 0 from Phase 2 and Finding 2 from Phase 4. It's the phase that would have surfaced these issues through real usage.
