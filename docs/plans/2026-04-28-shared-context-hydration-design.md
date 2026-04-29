# Design: Shared-Context Hydration for Customer-System Sessions

**Date:** 2026-04-28
**Status:** Approved (Craig + Claude, Session 12 brainstorm)
**Author:** Craig + Claude

## Problem

Sessions working on the customer-system + Indemn OS need **shared mental model** with Craig — the journey, the breakthroughs, the architecture, the principles, the current state, the open work. Without it, sessions propose things Craig would never propose: simplifying vision for "MVP simplicity," inlining skills instead of fixing deepagents progressive disclosure, routing around bugs instead of fixing them, re-litigating settled decisions.

Current discipline (per Session 11 handoff): every session reads **Track 1** (11 customer-system docs) + **Track 2** (10 OS docs) before any work — roughly **500K tokens**. The reading list itself is an artifact of past discipline failures (Sessions 8 and 9 skipped Track 2 and made bad calls).

Three problems with this:

1. **Hydration cost is so high there's no headroom for actual work.** 500K tokens spent on shared-mind hydration means real work fights for context. Net effect: lots of talking, not much building.
2. **The reading list is a raw artifact trail, not a curated mental model.** A session reading 500K of cumulative artifacts ends up with surface familiarity, not actual shared understanding.
3. **Sessions still drift even after reading.** Without an explicit objective and execution-mode discipline, sessions fall into brainstorming/planning loops instead of executing the roadmap.

## Goal

A single session-start prompt — usable across N parallel siblings AND across N sequential resets — that:

- Hydrates the shared mental model with maximum efficiency (target ~95K, not 500K)
- Sets an explicit execution objective so sessions drive toward shipping, not discussing
- Stays current as work happens (next session inherits the previous session's state)
- Enforces reading discipline (mandatory, no skipping)
- Provides on-demand depth via a router for work-area-specific deep dives

## Design

### Two-layer hydration

**Layer 1 — Always loaded (~95K total):**

The canonical shared mental model. Every session reads ALL of these in order:

| File | Purpose | Update cadence |
|---|---|---|
| `customer-system/CLAUDE.md` | Comprehensive overarching context: what we're building, how, why, architecture, journey, foundations, best practices, index | Rare (architecture shifts) |
| `customer-system/vision.md` | Slow-changing end-state articulation | Rare |
| `customer-system/roadmap.md` | Execution spine — phases, current state, where we're going | Every session that moves a phase |
| `customer-system/os-learnings.md` | Running register of OS gaps surfaced by customer-system work | When OS gap surfaces or status changes |
| `customer-system/CURRENT.md` *(new)* | Fast-changing state — what just happened, what's in flight, what's next | Every session |
| `indemn-os/CLAUDE.md` | OS shared mind — already tight, keep as-is | Rare |

**Layer 2 — On-demand:**

Loaded by the session itself once work area is clear. Pointed at by the "When working on X, READ these" router in `customer-system/CLAUDE.md`. Includes:

- `indemn-os/docs/architecture/*.md` — entity-framework, watches-and-wiring, associates, rules-and-auto, integrations, etc.
- `indemn-os/docs/white-paper.md` — canonical OS vision
- `indemn-os/docs/guides/*.md` — domain-modeling and how-to guides
- `customer-system/INDEX.md` — full append-only journey/decisions/artifacts ledger
- `customer-system/artifacts/*.md` — individual artifacts (handoffs, design docs, traces)
- `customer-system/SESSIONS.md` *(new)* — append-only log of session objectives + outcomes

The bias: more reading, not less. On-demand depth is the working material. The always-loaded layer is the foundation.

### `customer-system/CLAUDE.md` — comprehensive, restructured

Not distilled to tidbits. Comprehensive. Eight top-level sections in this order:

1. **What we're building** — overarching context for the customer-system as the first build on the OS. References vision.md for canonical articulation.
2. **How we're building it** — methodology (trace-as-build, fork pattern, dogfooding, OS bug convergence as continuous thread).
3. **Why we're building it this way** — design rationale, alternatives considered and rejected, the breakthrough.
4. **Architecture** — the 27-entity model, Touchpoint Option B, Playbook consulted twice, Proposal hydrates from DISCOVERY, structural decisions, open questions. Pointers to OS architecture docs for OS internals.
5. **Journey** — cumulative thinking across sessions. Substance, not bullets.
6. **Foundations** — the 20 design principles + invariants.
7. **Best practices** — cadence, discipline, start-of-session protocol, end-of-session protocol.
8. **Index of files** — the When-Working-on-X router pointing at on-demand depth.

What's removed from current CLAUDE.md: the redundant 700+ lines that sprawl across multiple sections, the redundant "Files Index" (folded into the router), the long REQUIRED READING blocks (replaced by the new prompt).

### `customer-system/CURRENT.md` — new file

50-100 lines. Lives at project root. Rewritten every session. Contains:

- **Current top of roadmap** — what phase/sub-task is in flight
- **Pipeline associate states** — EC, TS, IE: active / suspended / status
- **Parallel sessions running** — each session's objective, worktree path, current focus
- **Blockers** — what's gating progress right now
- **Next steps** — what the next session should pick up

This replaces the "Status" section that currently lives at top of CLAUDE.md and INDEX.md.

### `customer-system/SESSIONS.md` — new file

Append-only log. New entries at the **top**. Each entry:

```markdown
## Session N — YYYY-MM-DD — short title

**Objective:** [from the prompt's objective slot]
**Parallel sessions during:** [list]
**Outcome:** [3-5 bullets — what shipped, what's open]
**Handoff to next:** [pointer or short instruction]
**Touched:** [files / entities modified]
```

Loaded on-demand. Useful for: looking back at history, learning the objective format, parallel-session awareness, change-log scan.

### `customer-system/PROMPT.md` — the session-start prompt

The literal prompt to paste into 1-N sessions. Three responsibilities:

1. **Enforce mandatory reads** — list all Layer 1 files. Reading is mandatory, no skipping.
2. **Set the objective** — explicit, specific, execution-oriented. The objective slot is the only thing that varies per invocation.
3. **Instill execution discipline** — shared context contains the result of prior brainstorming; USE it; flag any genuine new design question to Craig BEFORE drifting into discussion.

The prompt also includes a confirmation step: the session must state what it loaded (top of roadmap, what CURRENT.md says is in flight, parallel-session state, its understanding of the session's specific objective) before doing any work.

### Update discipline

| File | When to update |
|---|---|
| `CURRENT.md` | Every session — replace |
| `SESSIONS.md` | Every session — append entry at top |
| `roadmap.md` | When phase state moves |
| `os-learnings.md` | When OS gap surfaces or status changes |
| `INDEX.md` | When Decision made / Open Question resolved / Artifact produced |
| `CLAUDE.md` | Rare — architecture shift, new principle, new router entry |
| `vision.md` | Rare — end-state articulation changes; stamp dated artifact |
| `indemn-os/CLAUDE.md` | Rare — OS architecture shift |

**End-of-session protocol** (enforced by closing prompt or hook — TBD):

1. Always: update `CURRENT.md` (replace) + `SESSIONS.md` (append entry)
2. If roadmap state moved: update `roadmap.md`
3. If OS gap surfaced/changed: update `os-learnings.md`
4. If Decision/Open Question/Artifact: append to `INDEX.md`
5. If durable substance changed: update `CLAUDE.md` or `vision.md` (rare)

**Anti-rot mechanism:** the session-start confirmation step reads CURRENT.md + recent SESSIONS entries. If they're stale or contradict reality, the next session catches it immediately. The hydration discipline is self-policing because the next session relies on it.

### Parallel session model

When multiple sessions run in parallel:

- Each session updates `CURRENT.md` with its slice (named section per session)
- `SESSIONS.md` appends are conflict-free (one entry per session per its run)
- Git handles any text conflicts at merge time
- Sessions check `CURRENT.md`'s "parallel sessions running" section to avoid duplicating or stepping on sibling work

## Tradeoffs

**What this design buys:**

- Hydration cost reduced ~5x (500K → ~95K)
- Single steady-state prompt, usable across N parallel + sequential sessions
- Shared mental model genuinely loaded (not surface familiarity from raw artifacts)
- Execution-oriented (objective + discipline against drift)
- Self-policing (next session catches rot in CURRENT.md)

**What it costs:**

- Two new files to maintain (CURRENT.md, SESSIONS.md)
- CLAUDE.md restructure work (one-time)
- Discipline cost at end of session (~5 minutes of updates)
- On-demand reads require the session to know when to pull more

**Honest concern:** reducing hydration solves the *cost* of getting to shared understanding. It doesn't fully solve "we're talking but not building." That second problem is partly discipline — sessions getting into brainstorm/plan loops instead of execute loops. The execution-oriented prompt addresses this, but it's not bulletproof. May need additional reinforcement (explicit "execute mode" prompts; closing prompts that demand deliverables; etc.) — to be added if the basic design proves insufficient.

## Rollout

This session (Session 12) lands the design as code:

1. Document this design (this file) — DONE
2. Draft new `customer-system/CLAUDE.md` (comprehensive, restructured)
3. Create `customer-system/CURRENT.md` with today's fresh state
4. Create `customer-system/SESSIONS.md` with the first entry (this session)
5. Write `customer-system/PROMPT.md` (the session-start prompt template)
6. Verify `indemn-os/CLAUDE.md` is good as-is (already confirmed)
7. Commit everything together

**Test:** the next session spun up uses `PROMPT.md` as its kickoff. If the session arrives with shared mental model intact and drives toward execution without re-litigating, the design works. If the session is missing something load-bearing, we iterate on what goes in CLAUDE.md / CURRENT.md.

## References

- Current `customer-system/CLAUDE.md` — the bloated source we're restructuring
- Current `customer-system/vision.md` — kept as-is
- Current `customer-system/roadmap.md` — kept as-is
- Current `customer-system/os-learnings.md` — kept as-is
- Current `customer-system/INDEX.md` — kept as-is (becomes on-demand reference)
- `artifacts/2026-04-28-session-11-handoff.md` — the 500K reading list this design replaces
- Session 12 transcript (this brainstorm) — source of the design decisions

---

*This design is the result of a brainstorm session. It is approved as of 2026-04-28. Future revisions land as separate dated artifacts in this directory.*
