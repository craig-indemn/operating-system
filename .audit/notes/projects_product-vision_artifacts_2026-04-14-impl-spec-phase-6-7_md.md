# Notes: 2026-04-14-impl-spec-phase-6-7.md

**File:** projects/product-vision/artifacts/2026-04-14-impl-spec-phase-6-7.md
**Read:** 2026-04-16 (sampled opening + domain modeling; 439 lines total. SUPERSEDED by consolidated.)
**Category:** spec-superseded

## Key Claims

Base Phase 6+7 implementation spec. **SUPERSEDED** by 2026-04-14-impl-spec-phase-6-7-consolidated.md (minor changes since this is mostly operational).

Key content:
- **Phase 6** = Dog-Fooding: Indemn runs its own CRM on the OS per 2026-04-10-crm-retrace. 9 domain entities, 5 org-level + 60 actor-level integrations, 8 roles, 6 associates, health scoring + overdue detection rules.
- **Phase 7** = First External Customer: GIC per 2026-04-10-gic-retrace-full-kernel. Email pipeline.
- **Not code-specification phases** — operational phases. "The implementation detail here is not 'what classes to write' but 'what entities to define, what watches to configure, what skills to author, and what the acceptance criteria are for real-world operation.'"
- **Phase 6 scope = CRM retrace blueprint.** Phase 7 scope = GIC retrace blueprint.
- **8-step domain modeling process** applied per-customer (from remaining-gap-sessions.md).

## Architectural Decisions

- **Phase 6 and 7 are operational, not code phases.**
- **CRM and GIC retrace artifacts are the blueprints** — Phase 6-7 implements them on the kernel.
- **Domain modeling process is standardized** (entities → roles → rules → skills → integrations → test → deploy+tune).

## Layer/Location Specified

- **Phase 6 Indemn CRM**: domain entities created via CLI in indemn org. All data, no kernel code changes.
- **Phase 7 GIC**: domain entities created via CLI in gic org. All data.
- **Integration with current system**: none. New OS alongside current system per coexistence decision.
- **Harnesses required** (per realtime-architecture-design):
  - Phase 6 needs: async-deepagents (Meeting Processor, Health Monitor, Follow-up Checker, Weekly Summary, Personal Syncs) + chat-deepagents (CRM Assistant).
  - Phase 7 needs: async-deepagents (classifier, linker, assessor, draft writer, stale checker) + optional voice.
- **Currently**: none of these harnesses exist. Phase 6/7 BLOCKED on Finding 0.

**Finding 0 relevance**: Phase 6 and 7 are BLOCKED by Finding 0. The dog-fooding use case (Indemn CRM) requires harnesses that don't exist. The first-customer use case (GIC) likewise requires harnesses. Until Finding 0 is fixed (build 3 harness images, move agent execution out of kernel), Phases 6-7 cannot be executed as designed.

## Dependencies Declared

- Kernel (Phase 0-5 complete)
- CRM domain (9 entities + 5 org + 60 actor integrations + 8 roles + 6 associates)
- GIC domain (Email + Submission + Extraction + Assessment + Draft + Carrier + Agent + ~5-7 roles + 5-8 associates)
- Outlook Graph API (GIC)
- Granola + Gemini + Slack + Gmail + Calendar + Drive + Linear + Postgres (CRM)

## Code Locations Specified

- No new kernel code. Domain modeling via CLI populates entity definitions + rules + lookups + skills + integrations + associates in MongoDB.

## Cross-References

- 2026-04-10-crm-retrace.md (Phase 6 blueprint)
- 2026-04-10-gic-retrace-full-kernel.md (Phase 7 blueprint)
- 2026-04-13-remaining-gap-sessions.md (8-step domain modeling)
- 2026-04-14-impl-spec-phase-0-1.md (foundation)
- 2026-04-14-impl-spec-phase-2-3.md (associate execution + integrations)
- 2026-04-14-impl-spec-phase-4-5.md (Base UI + real-time)
- 2026-04-14-impl-spec-phase-6-7-consolidated.md (SUPERSEDES this)
- 2026-04-14-impl-spec-gaps.md (4 gaps — smallest phase gap count)

## Open Questions or Ambiguities

- Phase 6 parallel-run mechanism (resolved in consolidated + gap-resolutions).
- Phase 7 GIC migration concrete steps — resolved via coexistence model (no bridge; parallel runs).
- **Blocking issue for both**: Finding 0. The harnesses don't exist. Dog-fooding cannot happen on in-kernel agent execution (no CRM Assistant can run, no personal syncs can run as intended).

**Supersedence note**: SUPERSEDED by consolidated. Phase 6/7 are operational blueprints; their execution is blocked by Finding 0 until harnesses are built.
