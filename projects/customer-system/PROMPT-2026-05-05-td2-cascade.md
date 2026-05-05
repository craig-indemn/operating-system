You are starting a session on the operating-system project — building the Indemn customer system on top of the Indemn Operating System (OS). This prompt hydrates your shared mental model with Craig so you can execute alongside him as a peer, not a junior re-deriving decisions he's already made.

## MANDATORY: read the canonical shared context, in this order

These files together ARE your shared mental model. Read all of them. No skipping. No skimming.

1. /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/CLAUDE.md
2. /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/vision.md
3. /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/roadmap.md
4. /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/os-learnings.md
5. /Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/CURRENT.md
6. /Users/home/Repositories/indemn-os/CLAUDE.md

Reading is non-negotiable. Without these you will propose things Craig would never propose (simplify vision, inline skills, route around bugs), re-derive decisions already made, lose the thread.

## After loading: pull on-demand depth for your work area

Once the mandatory set is loaded, follow CLAUDE.md's "When working on X, READ these" router (Section 8). For TD-2 cascade activation specifically, also pull:

- `roadmap.md § TD-2` in full — this is the resolved design for the 7-associate cascade, ReviewItem pattern, activation order, done-test. It's ~170 lines of detail. READ IT ALL.
- `skills/email-classifier.md` (EC v9 current content — you'll update to v10)
- `skills/touchpoint-synthesizer.md` (TS v6 current — you'll update to v7)
- `skills/intelligence-extractor.md` (IE v3 current — verify through full cascade)
- `kernel/entity/save.py` — `bulk_save_tracked` is the batch creation path (Session 18 shipped it)
- `kernel/message/emit.py::_build_related_entities` — polymorphic Option B support is live (Session 18)
- `harnesses/async-deepagents/cron_runner.py` — the cron_runner exec path
- `harnesses/async-deepagents/main.py` — `process_with_associate` branching

For MeetingClassifier specifically (the first trace target):
- Run `indemn meeting get <armadillo-meeting-id> --include-related --depth 2` to see the Armadillo Apr 28 discovery meeting's current state
- Run `indemn employee list` to see who's in the system (for attendee resolution)
- Check Armadillo's Company entity: `indemn company get 69f22186...444d`

Bias toward MORE reading, not less. TD-2 is the biggest single deliverable — 7 associates, 3 new, 2 upgraded, 2 verified.

## YOUR OBJECTIVE FOR THIS SESSION

**TD-2 cascade activation — start with MeetingClassifier.**

Per `roadmap.md § TD-2`, the cascade is:
```
Source entity created (Email | Meeting | SlackThread)
  → [EC | MC | SC]              Source classifier (one fires per source type)
    → Source classified
      → TS                      Touchpoint creator (+ Deal-creation)
        → Touchpoint logged
          → IE                  Intelligence extractor
            → Touchpoint processed
              → Proposal-Hydrator + Company-Enricher (parallel)
```

**This session's specific scope — MeetingClassifier (MC):**

1. **Trace manually first** (trace-as-build per CLAUDE.md § 2). Pick Armadillo's Apr 28 discovery meeting. Act AS the MeetingClassifier:
   - Load the meeting via CLI
   - Resolve attendees as Contacts (external) or Employees (internal) using `indemn contact entity-resolve` and `indemn employee entity-resolve`
   - Identify the Company from external attendees
   - Classify scope (external — has non-Indemn attendees)
   - Write the entity updates via CLI: `indemn meeting update <id> --data '{"company":"...", "scope":"external", "status":"classified"}'`
   - Verify the entity state post-trace

2. **Write the MC skill** from what worked in the trace. The skill is the procedure that produced correct state.

3. **Wire MC infrastructure:**
   - Create `meeting_classifier` role with watch on `Meeting created`
   - Create MC actor (mode=hybrid, runtime=async-deepagents-dev)
   - Push skill to dev OS

4. **Activate + drain a small batch.** Reprocess 3-5 meetings, watch LangSmith traces, verify correct classification.

5. **If MC is clean:** move to the next associate in activation order (EC v10, or SC if Slack data warrants it). Multi-session work — close cleanly per session whenever a natural boundary is reached.

**Key design decisions already resolved (don't re-litigate):**
- One associate per significantly-different (trigger, entities, context, skill) tuple
- ReviewItem on ambiguity — never block the cascade
- Hard Rule #1 inverted: resolve-before-create, autonomous create on 0/0
- Employee entity_resolve is NOW LIVE (Session 18) — MC can resolve internal participants
- Polymorphic --include-related is NOW LIVE (Session 18) — TS v7's source pointers will be followable
- Per-event Touchpoints (NOT per-thread) — every meeting = its own Touchpoint

**Done-test for MC specifically:**
- MC skill in dev OS with content_hash
- meeting_classifier role + watch on `Meeting created` (condition: `status=logged`)
- MC actor (mode=hybrid, active)
- Armadillo's Apr 28 meeting: company=Armadillo, scope=external, attendees resolved, status=classified
- 3-5 additional meetings classified correctly via autonomous MC activation
- LangSmith traces show clean tool use + correct entity-resolve calls
- No auto-created duplicate Companies or Contacts (resolve-before-create working)

**After MC is proven:** proceed to next in activation order per roadmap.md § TD-2. The session may ship MC only, or MC + one more associate if time/context permits. Close cleanly either way.

## Operating discipline (non-negotiable)

- **Trace-as-build.** Don't write the skill first. Run the CLI commands yourself. See what works. The skill is the writeup of what worked.
- **Use `indemn` CLI first.** If you reach for mongosh during the trace, that's a signal the CLI needs more — log it in os-learnings.md.
- **`indemn diagnose` is now available** (Session 18). Use `indemn diagnose actor <mc-id>` and `indemn diagnose cron <name>` instead of raw mongo queries for debugging runs.
- **`bulk_save_tracked` exists** in `kernel/entity/save.py`. If MC needs to create multiple Contacts in one go, use it.
- **Don't re-derive the cascade architecture.** It's resolved in roadmap.md § TD-2. Read it, use it.
- **Bug #12 discipline:** `mongosh-connect.sh` does inline host swap. DO NOT overwrite the shared mongodb-uri AWS Secret.
- **Wait for Craig's signal** before running end-of-session protocol.

## Confirmation step (do this BEFORE any work)

After loading the mandatory set, state:

1. **Top of roadmap** — TD-2 cascade activation (pre-TD-2 hardening complete per Session 18)
2. **What CURRENT.md says is in flight** — TD-2 begins; all Tier 1 items shipped; 4 fetchers active; EC/TS suspended; IE active
3. **Previous 1-2 entries from SESSIONS.md** — Session 18 (OS hardening sprint — 5 items shipped, 514 tests) and Session 17 (TD-1 verified, Bug #50, chunk-cap)
4. **Your understanding of this session's specific objective** — Build MeetingClassifier via trace-as-build on Armadillo's Apr 28 meeting. Wire infrastructure. Activate. Verify. Then proceed to next associate if time permits.

Only after that, begin work.
