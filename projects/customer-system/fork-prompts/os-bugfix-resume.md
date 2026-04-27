# OS Bugfix Session — Resume Prompt

**Living document.** Update the "UPDATED PRIORITY" block whenever the main session surfaces new high-priority bugs in `os-learnings.md`. Update the "Recent fork-session progress" block whenever the fork session marks rows 🟡 In-progress / 🟢 Fixed.

**How to use:**
1. In the bugfix session, run `/clear` to wipe conversation history (or close + reopen the session in the same worktree).
2. Paste the prompt below as the first message in the cleared/fresh session.
3. The session bootstraps from durable shared context (`vision.md`, `roadmap.md`, `os-learnings.md`, `INDEX.md`, `CLAUDE.md`, the trace artifacts) — no human-in-the-middle handoff required beyond the prompt itself.

**Why this works:** the shared context lives in project files, not in conversations. A fresh session reading `os-learnings.md` sees what the previous instance marked 🟡 In-progress and 🟢 Fixed. The resume prompt just adds framing ("you're a resumed session, here's what's urgent right now") — the actual context comes from the files.

**Last updated:** 2026-04-27 — after Apr 27 Alliance trace surfaced new top-priority bugs (API 500-detail, Meeting create, entity-skill JSON examples).

---

## The prompt (paste verbatim into the cleared/fresh bugfix session)

```
You are resuming the parallel OS-bugfix session that was started earlier from the customer-system 
project's vision-and-roadmap session (2026-04-27). The previous instance of this session was cleared 
to free context. Pick up from the durable shared context — `os-learnings.md` is your work queue.

The MAIN session is still running in parallel doing the Alliance v2 proposal trace (Phase A2). New 
findings have been surfaced and logged to `os-learnings.md` since you were last running. Re-read it 
fully on bootstrap.

==== Working directories (unchanged) ====
- Project context: /Users/home/Repositories/operating-system/.claude/worktrees/<your-worktree>/projects/customer-system/
- OS kernel code: /Users/home/Repositories/indemn-os/
- OS docs: /Users/home/Repositories/indemn-os/docs/

==== Start-of-session protocol (mandatory — same as before, plus updates) ====

1. Read these files in full:
   - projects/customer-system/CLAUDE.md
   - projects/customer-system/vision.md
   - projects/customer-system/roadmap.md
   - projects/customer-system/os-learnings.md          ← YOUR WORK QUEUE. New entries since last run.
   - projects/customer-system/INDEX.md                 ← Decisions log + open questions
   - projects/customer-system/artifacts/2026-04-27-alliance-trace-plan.md     ← Plan for the live trace
   - projects/customer-system/artifacts/2026-04-27-alliance-trace.md          ← The live trace narrative the main session is building (in flight)
   - projects/customer-system/artifacts/2026-04-24-os-bugs-and-shakeout.md
   - projects/customer-system/artifacts/2026-04-24-extractor-pipeline-gap.md
   - projects/customer-system/artifacts/2026-04-24-extractor-procedure-and-requirements.md
   - /Users/home/Repositories/indemn-os/CLAUDE.md
   - /Users/home/Repositories/indemn-os/docs/architecture/entity-framework.md
   - /Users/home/Repositories/indemn-os/docs/architecture/watches-and-wiring.md
   - /Users/home/Repositories/indemn-os/docs/architecture/associates.md

2. Check `os-learnings.md` for in-flight work:
   - Rows marked 🟡 In-progress = work the PREVIOUS instance of this session started. Decide whether 
     to continue it (look at any branch in indemn-os matching the bug's name; check git log for commits) 
     or restart from scratch.
   - Rows marked 🟢 Fixed since 2026-04-27 = the previous instance completed something. Don't redo.
   - Rows still 🔴 Open = available work.

3. Before writing any code, confirm your understanding by writing back: 
   a) the top-4 bugs you intend to tackle in priority order (RE-PRIORITIZED based on what you see in 
      os-learnings.md NOW — see "UPDATED PRIORITY" below), 
   b) why those four (what they unblock for the live trace + the Phase B foundation), 
   c) any in-progress work from the previous instance you're picking up vs starting fresh, 
   d) where the work happens (which file in indemn-os/), 
   e) how you'll test the fix.

==== UPDATED PRIORITY (post-Apr-27-Alliance-trace findings) ====

The Alliance trace surfaced new high-priority bugs that are BLOCKING THE LIVE TRACE right now:

1. **API returns generic "Internal Server Error" body on 500 — no validation detail.** 
   The root issue making the entire create-500 family (Bug #25 Company, Bug #26 Deal, Meeting create 
   failure) impossible to self-diagnose. Without this fix, every other create-related bug is hard to 
   solve. Likely fix in `kernel/api/registration.py` or `kernel/api/errors.py` (global exception 
   handler). The 500 response body should include the exception message AND, for validation errors, 
   return 400 with field-level detail. Logged in os-learnings.md High section as of 2026-04-27.

2. **Meeting create returns HTTP 500.** `POST /api/meetings/` with valid-shape JSON (title + date) 
   returns 500. Blocking the Alliance trace from creating the Feb 1 + Apr 8 Meeting entities. May be 
   the same root as Bug #25/#26 or Meeting-specific. Cannot self-diagnose until #1 above is fixed. 
   Once #1 lands, retry Meeting create and the actual error will surface.

3. **Auto-generated entity skill needs JSON-shape example payloads.** Reinforces and extends the 
   existing "Generated entity skill teaches actual filter syntax" item. Without example payloads in 
   the skill output, an associate has no way to learn the right `--data` JSON shape from the skill. 
   Fix: in `kernel/skill/generator.py`, emit a working example payload per command (CRUD + transition 
   + capability). Particularly important for create/update commands.

Then the original Top 4 from the previous fork prompt (still important, but ordered AFTER the above 
because the trace is actively blocked):

4. **Touchpoint forward source pointers (Option B)** — schema + Synth update. 
   *Note: as of 2026-04-27, may already be 🟢 Fixed by previous fork instance — verify in os-learnings.md.*
5. **Silent workflow stuck-state** — workflow detects empty agent output as failure. 
   *Note: may already be 🟡 In-progress; check os-learnings.md before starting fresh work.*
6. **Cross-invocation tool-cache leak** — scope per message_id. 
   *Note: may already be 🟡 In-progress; check os-learnings.md before starting fresh work.*

After top 3 (the new ones) + 4-6 (original Top 4), continue with:
- Entity-resolution kernel capability (Bug #16 root)
- Bug #29 (route eviction)
- Bug #23 (bulk-delete operator filters)
- Bug #22 (service-token forensics)
- Bug #9 (associates pass dicts vs ObjectIds)

==== Rules of engagement (unchanged) ====

- **Production safety.** Read .claude/rules/production-safety.md. NEVER write to production systems 
  or modify EC2 instances without explicit user permission. The OS API runs on Railway — read state 
  freely; deployments and config changes need Craig's approval. Read-only on shared databases.

- **Branch-per-bug.** Make a feature branch in indemn-os, push, surface a PR for Craig's approval. 
  Don't merge to main without explicit approval. Don't deploy without explicit approval.

- **Update os-learnings.md when a bug changes status.** Mark a row 🟡 In-progress when you start; 
  🟢 Fixed when commit lands in main / is deployed (with commit ref and date). Don't delete fixed 
  rows — they're the trail. THIS IS HOW the main session sees your progress.

- **Coordinate via os-learnings.md.** The main session is running in parallel and may surface new 
  findings. Re-read os-learnings.md before starting each new bug. Mark rows 🟡 immediately when 
  you start so the main session knows not to grab them.

- **Log new bugs you discover.** Add a row to os-learnings.md with detail before continuing.

- **Test what you fix.** Use existing tests/unit, tests/integration, tests/e2e. Add basic coverage 
  for the fix path if none exists. Run the relevant test suite before declaring done.

- **Update OS docs to reflect what changed.** /Users/home/Repositories/indemn-os/docs/architecture/*.md 
  and /Users/home/Repositories/indemn-os/docs/guides/*.md need to stay accurate.

- **Push back on the priority order if you spot a dependency I missed.** If the code says #2 needs #1 
  to land first or vice versa, flag it before starting.

Begin by completing the start-of-session protocol, then write back with the 5-part response from 
step 3. We iterate from there. The MAIN SESSION IS BLOCKED on bugs #1 + #2 above — those are the 
unblock for the active trace work.
```

---

## Recent fork-session progress (snapshot — derived from `os-learnings.md`, kept here for quick scan)

This block is a courtesy summary of what the bugfix session has done recently, so Craig can see at a glance what state the parallel work is in without re-reading `os-learnings.md`. Update whenever a fork session marks rows 🟡 / 🟢.

**As of 2026-04-27 (post-bugfix-resume #2 — six PRs reviewed and merged, one bug blocked on deploy):**

Pre-existing in-progress PRs (reviewed and merged):
- 🟢 **Touchpoint Option B** — `indemn entity modify Touchpoint --add-field` + `indemn-api` redeploy + Synth skill v3. Both new fields visible in auto-generated entity skill; new Touchpoints from the Synth will populate them.
- 🟢 **Cross-invocation tool-cache leak** — merged to main as `ac6d475` (feature commit `4e7e83d`). 6 unit tests pass. **Pending: Craig redeploys async runtime.**
- 🟢 **Silent workflow stuck-state** — merged to main as `67f006c` (feature commit `852eeaa`). 20 unit tests pass. **Pending: Craig redeploys async runtime.**
- 🟢 **Generated entity skill teaches actual filter syntax + Bug #6** — merged to main as `f4fc121` (feature commit `6af2166`). 18 unit tests pass. **Pending: Craig redeploys kernel.**

New work this session (Top-4 from the Apr 27 trace):
- 🟢 **#1 — API 500 transparency** — merged as `cf5acd8` (feature commit `914fc61`). `kernel/api/errors.py` gains a Pydantic `ValidationError` → 400 handler with field-level errors array, plus a catch-all `Exception` → 500 handler returning `{error, type, message}` (logs full traceback; bounds message at 4096 chars). 10 unit tests pass. **Pending: Craig redeploys kernel.**
- 🔴 **#2 — Meeting create HTTP 500** — **BLOCKED on #1 deploy.** Cannot self-diagnose against production until the new error handler is live. Once redeploy lands, retry `POST /api/meetings/` with the Alliance trace payload; the actual exception will surface in the 500 body. Likely same root as Bug #25 (Company) and Bug #26 (Deal).
- 🟢 **#3 — Entity skill JSON-shape examples** — merged as `b83fa08` (feature commit `ab987c6`). `kernel/skill/generator.py` now renders working JSON payloads between `--data` quotes for `create` (every required field with type-appropriate placeholder; ObjectId → 24-hex string, datetime → ISO 8601, enum → first allowed value; state field excluded) and `update` (representative subset). 18 new unit tests (28 total in the file) pass. **Pending: Craig redeploys kernel.**
- 🟢 **#4 — Bug #29 entity-def route eviction** — merged as `83d2494` (feature commit `0bd4e50`). New `_evict_routes_for_prefix(app, prefix)` helper called inside `register_entity_routes` before `app.include_router(router)`. Trailing-slash check guards against prefix-lookalikes. 7 unit tests including end-to-end TestClient roundtrip proving a re-registered handler wins over the stale one. **Pending: Craig redeploys `indemn-api`.**

**For Craig's next deploy window:** kernel + `indemn-api` redeploy picks up #1, #3, #4 + the previous merges; async runtime redeploy picks up the cache-leak and silent-stuck-state fixes. Once kernel is redeployed, #2 becomes self-diagnosable.

---

## How to update this file

1. **When the main session surfaces a new high-priority bug**, edit the "UPDATED PRIORITY" block above to add it (and re-rank if needed).
2. **When a fork session marks a row 🟡 / 🟢 in `os-learnings.md`**, add/update the entry in "Recent fork-session progress" so Craig and future fork sessions can see at-a-glance status without re-reading the full register.
3. **When the trace narrative changes** (e.g., a new live trace is in flight, or the active trace changes), update the file references in the start-of-session protocol.
4. **When the rules of engagement change** (e.g., new constraints from `production-safety.md`, new branch-naming convention, etc.), edit the "Rules of engagement" block.

The file's value is that it's always usable as-is — a fresh fork session pasting the latest version always lands on the highest-priority work and never duplicates effort.

---

## Sister artifacts

- `projects/customer-system/fork-prompts/` — this directory holds prompts for parallel-session work tied to the customer-system project
- `projects/customer-system/os-learnings.md` — the work queue; this prompt's authority comes from that file being the canonical state
- `projects/customer-system/roadmap.md` — the "Continuous threads" section calls out **OS bug convergence** and **shared-context-update mechanism** as first-class operating disciplines; this file is one realization of both
- `projects/customer-system/CLAUDE.md` — the project orientation that the resumed session reads at bootstrap
