# Session-Start Prompt

> **Purpose:** the literal prompt to paste into 1-N sessions (parallel siblings or sequential resets) working on the customer-system + Indemn OS. Hydrates the canonical shared mental model in ~95K tokens (down from ~500K of the prior reading-list discipline). Sets an explicit objective. Instills execution discipline.
>
> **Usage:** copy everything between the `===PROMPT START===` and `===PROMPT END===` markers below. Fill in the `[OBJECTIVE FOR THIS SESSION]` slot. Paste into the new session.
>
> **Why this works:** the shared mental model is comprehensive in the always-loaded files; on-demand depth is pulled per task; the objective drives execution; the confirmation step verifies hydration; the discipline lines prevent drift into brainstorming. Sessions arrive with peer-level shared understanding and execute toward the roadmap, not re-litigate decisions.

---

```
===PROMPT START===

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

Once the mandatory set is loaded, follow CLAUDE.md's "When working on X, READ these" router (Section 8) to pull additional depth for your specific task — Alliance, dashboards, extraction, Artifact Generator, OS internals, LangSmith debugging, etc.

Bias toward MORE reading, not less. The mandatory set is the foundation. On-demand depth is your working material. Don't try to operate blind on a specific task.

## YOUR OBJECTIVE FOR THIS SESSION

[OBJECTIVE FOR THIS SESSION]

## Operating discipline (non-negotiable)

- **The shared context contains the result of prior brainstorming. USE it.** Don't re-litigate decisions. If you find yourself proposing something that was already decided, stop and re-read the relevant section.
- **If something genuinely isn't settled, flag it to Craig BEFORE drifting into design discussion.** Don't unilaterally redesign. Add to the cumulative thinking; don't redirect it.
- **Drive toward execution.** State intent → do the work → report. The roadmap (`roadmap.md`) defines the work. CURRENT.md tells you what's in flight.
- **Parallel sessions are listed in CURRENT.md.** Don't duplicate or step on sibling work. If your objective overlaps a sibling's, raise it before proceeding.
- **Wait for Craig's signal** before running end-of-session protocol. When signaled, run ALL of CLAUDE.md § 7 "End-of-session protocol" — none are optional.

## Confirmation step (do this BEFORE any work)

After loading the mandatory set, state:

1. **Top of roadmap** — what phase / sub-task is current per `roadmap.md`
2. **What CURRENT.md says is in flight** — top of roadmap state, pipeline associate states, parallel sessions running, blockers
3. **Previous 1-2 entries from SESSIONS.md** — what just shipped, what was the previous handoff
4. **Your understanding of this session's specific objective** — restated in your own words

Only after that, begin work.

===PROMPT END===
```

---

## Variants

### When Craig wants a focused work session

Replace `[OBJECTIVE FOR THIS SESSION]` with something specific and execution-oriented. Examples that work:

- *"Execute roadmap Phase B1.5 — reactivate Email Classifier and reprocess Diana@CKSpecialty (`69ea56250a2b41b7696076b3`) once Bug #35 is resolved. Verify EC v7 actually constrains behavior per Hard Rules #1-11. If multi-1.0 ambiguity is detected, agent must transition to needs_review per Hard Rule #3 — not auto-create a Company. Use LangSmith trace to verify the agent read the EC associate skill."*

- *"Continue work from Session 12 on the deepagents skill-discovery investigation (Bug #35). Hypothesis A from Session 11 handoff Section 3: path resolution against LocalShellBackend.root_dir is double-nesting. Read `harnesses/async-deepagents/main.py` and the deepagents source to confirm path-resolution behavior. Test the absolute-path fix. Deploy via `railway up --service indemn-runtime-async`. Verify with a Diana reprocess + LangSmith trace inspection."*

- *"Design the resolution for Open Design Question #1 (Opportunity vs Problem entity). Read `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` § Topic 2 first. Then engage Craig in brainstorm. This is a cross-session design question — flag it explicitly that brainstorm is appropriate here, since this is one of the five open questions noted in CLAUDE.md § 4. Output: a decision in INDEX.md § Decisions and a structural change to the entity model if applicable."*

### When Craig wants a quick status check (lightweight session)

Replace `[OBJECTIVE FOR THIS SESSION]` with a status objective. Example:

- *"Verify current state of the customer-system pipeline. Run: `indemn actor list --type associate` to confirm pipeline associate states match CURRENT.md. Check the Diana@CKSpecialty test entity (`69ea56250a2b41b7696076b3`) is at `received` with no Company / Contact links. Report any drift. Do NOT make changes — verification only. End the session by stating: pipeline state vs. expected, drift found (yes/no), recommended next action."*

### When Craig wants to wrap an existing session

A separate closing prompt (TBD — could be added). Roughly:

- *"Wrap this session. Run the end-of-session protocol per CLAUDE.md § 7: update CURRENT.md (replace), append to SESSIONS.md, update roadmap.md / os-learnings.md / INDEX.md as warranted, commit everything in one tight commit. Verify each file before declaring done."*

---

## Maintenance

- This file (`PROMPT.md`) is itself part of the shared context. If we change the structure of always-loaded files, update this prompt to match.
- The prompt is steady-state — Craig should not need to redesign it per session. Only the `[OBJECTIVE FOR THIS SESSION]` slot varies.
- If sessions consistently arrive without shared context loaded properly, the failure mode is upstream — fix CLAUDE.md / CURRENT.md / this prompt. Don't patch it at the session level.
