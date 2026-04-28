---
ask: "Comprehensive handoff for Session 12. Captures: what we set out to do, what we shipped (LangSmith tracing on async-deepagents harness, kernel CLI bug fix Bug #34, harness completion check tightening, EC skills v6 + v7, Document Drive metadata sync), what we DISCOVERED was broken (deepagents skill discovery — every EC iteration v3→v7 has been ineffective because the agent never reads the associate skill content), the kernel-level harness work that's STILL needed, the open behavioral issues (agent tendency to email-create), the architectural alignment with Craig (evals-as-OS-adapter Path 3, harness reports facts-OS-interprets-meaning, no inlining skills into system prompts), and the explicit do-not-skip reminders for next session."
created: 2026-04-28
workstream: customer-system
session: 2026-04-28-session-11
sources:
  - type: conversation
    description: "Session 11 working session — LangSmith wiring, kernel CLI bug discovery, completion check tightening, EC iterations v6 + v7, deepagents skill-discovery investigation"
  - type: langsmith
    ref: "Project indemn-os-associates (id 19302981-aa9e-4869-9137-59a38d7646df)"
    description: "Diana@CKSpecialty traces 019dd522-… through 019dd602-… — five sequential reproduction attempts isolating each issue"
  - type: github
    ref: "indemn-os main commits 956d7d5, db97694, d914d76, 5ec4e9f"
    description: "Three substantive harness/kernel changes shipped + one over-engineered fix that didn't fully solve the deepagents skill issue"
---

# Session 11 Handoff — LangSmith wired in; CLI bug + completion check fixed; deepagents skill-discovery STILL BROKEN

> ⚠️ **READ THIS DOCUMENT IN FULL FIRST. THEN READ THE TWO-TRACK LIST IN SECTION 1 IN FULL. THEN BEGIN WORK.**
>
> Session 11 covered a LOT of ground and discovered that EVERY prior EC skill iteration (v3 → v7) has been ineffective because of a deepagents harness configuration bug we have not yet fully resolved. The next session inherits a partially-fixed state and a clear next-investigation path.
>
> **Section 1 below is the non-negotiable reading list. Do not skip Track 2 (the OS docs).**

---

## 1. MANDATORY READING — both tracks, in this order

Both tracks are required. Reading only one is a discipline violation. The customer system is a build ON the OS — you cannot do competent work in either without the other.

### Track 1 — This project (customer-system)

Read in this order. Each path is absolute.

1. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/CLAUDE.md` — orientation, vision, journey (Sessions 6/7/8/9/10/11 — read 11 carefully, it's this session). Files index. When-working-on-X router. Foundational principles. **Note especially the new "When working on X → Debugging an associate's behavior (LangSmith tracing)" router entry added in Session 10.**
2. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/INDEX.md` — Status (Session 11 entry at top), Decisions log (5+ Session 10 decisions + Session 11 decisions), Open Questions, Artifacts table.
3. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/vision.md` — slow-changing end-state. Section 4 captures the trace-as-build principle. Vision §2 item 7 ("LangSmith on all harnesses") is now LIVE for async-deepagents.
4. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/roadmap.md` — current Phase B1 progress.
5. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/os-learnings.md` — running register. **Critical NEW entry: deepagents skill-discovery broken (Bug #35). Bug #34 (kernel CLI) is now 🟢 Fixed.**
6. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/artifacts/2026-04-28-session-11-handoff.md` — this file.
7. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/artifacts/2026-04-28-session-9-handoff.md` — Session 9 handoff (read for the trace-as-build-method principle and the original kill-switch finding).
8. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/artifacts/2026-04-28-phase-b1-data-state-and-trace-plan.md` — Phase B1 working plan. Many items done; B1 still has open items.
9. `/Users/home/Repositories/operating-system/.claude/worktrees/roadmap/projects/customer-system/skills/email-classifier.md` — current EC v7 skill content (in DB at content_hash `897d05babf0d3b83…`). **Important context for Section 4 below.**

### Track 2 — The OS (the platform you are building ON)

Track 2 is mandatory. The customer system is a domain modeled on the OS — these docs explain what the OS is and how it works. **Reading only Track 1 produces work that fights the OS instead of leveraging it.** Read in this order. Each path is absolute.

1. `/Users/home/Repositories/indemn-os/CLAUDE.md` — OS builder's manual. Compact reference.
2. `/Users/home/Repositories/indemn-os/README.md` — top-level OS orientation.
3. `/Users/home/Repositories/indemn-os/docs/white-paper.md` — canonical OS vision.
4. `/Users/home/Repositories/indemn-os/docs/architecture/overview.md` — trust boundary, dispatch pattern, deployment topology.
5. `/Users/home/Repositories/indemn-os/docs/architecture/entity-framework.md` — `save_tracked()`, state machines, schema migration.
6. `/Users/home/Repositories/indemn-os/docs/architecture/watches-and-wiring.md` — watches, conditions, scoping, message cascade, selective emission.
7. `/Users/home/Repositories/indemn-os/docs/architecture/associates.md` — actor model, skills, harness pattern, execution lifecycle. **Re-read with extra attention this session — the deepagents progressive disclosure mechanism is described here and the bug we're hunting is in this layer.**
8. `/Users/home/Repositories/indemn-os/docs/architecture/rules-and-auto.md` — rule engine, lookups, capabilities, the `--auto` pattern.
9. `/Users/home/Repositories/indemn-os/docs/architecture/integrations.md` — adapters, credential resolution, webhooks. Relevant: Path 3 evals architecture treats the evaluations service as a future kernel adapter (`system_type: evaluation`).
10. `/Users/home/Repositories/indemn-os/docs/guides/domain-modeling.md` — the 8-step process.

### Coverage check (do this before claiming reading is done)

Answer the following before starting work:

- **Track 1:** Where is the LangSmith tracing addition documented? (CLAUDE.md "When working on X → Debugging an associate's behavior".) What's the LangSmith project name + project ID? What metadata is attached to each trace? What was Session 10's "kernel CLI bug" (Bug #34)? What was Session 11's NEW Bug #35? Is EC's v6/v7 skill content actually being read by the agent at execution time (per Section 3 below)?
- **Track 2:** What does `save_tracked()` do? What are the three event types that trigger selective emission? What does `--auto` mean? What is the trust boundary? Why is the kernel domain-agnostic? **What does deepagents' progressive disclosure look like — what file/dir layout does it expect for skills, and how does the harness write them?**

If you can answer these without re-reading, the reading is loaded. Begin work.

---

## 2. State of the project at end of Session 11

### What just shipped (Session 11)

**Three substantive kernel/harness changes on indemn-os main:**

| Commit | What | Status |
|---|---|---|
| `956d7d5` | feat(harness): wire LangSmith tracing into async-deepagents | ✅ Live, working |
| `db97694` | fix(cli): include `entity_resolve` in `_COLLECTION_LEVEL_CAPS` (Bug #34) | ✅ Fixed |
| `d914d76` | fix(harness): require ≥1 successful mutating CLI call for `queue complete` | ✅ Fixed (closes silent-stuck-state regression) |
| `5ec4e9f` | fix(harness): pass skills LIBRARY dir to deepagents, not per-skill subdirs | ⚠️ **Did not fully solve the issue** — see Section 3 |

**EC skill iterated:** v6 (content_hash `5bbfdd13ad26c8db…`) → v7 (content_hash `897d05babf0d3b83…`). v7 added Hard Rule #10 (mandatory Step 3 — Contact resolve) + #11 (resolve order: Contact before Company), plus strengthened Step 4 multi-1.0 ambiguity language with Diana@CKSpecialty as a worked example.

**Document `69efbdea4d65e2ca69b0dd80` synced** with Drive metadata: `drive_file_id: 1pM3tYg6rHzG8RW6xU_titouiq_iddhIC`, `drive_url: https://drive.google.com/file/d/1pM3tYg6rHzG8RW6xU_titouiq_iddhIC/view`. Entity now reflects reality.

**LangSmith infrastructure** (vision §2 item 7 foundation milestone): live in production. Project `indemn-os-associates` (id `19302981-aa9e-4869-9137-59a38d7646df`). API key at AWS Secrets `indemn/dev/shared/langsmith-api-key`. RunnableConfig dict on `agent.ainvoke()` carries metadata `{associate_id, associate_name, message_id, entity_type, entity_id, runtime_id, correlation_id}` + tags `{associate:<name>, entity_type:<type>, runtime:<id>}`. Auto-tracing of LLM/tool/state-graph calls. Five Diana@CKSpecialty traces from this session captured below.

### What we DISCOVERED via LangSmith (this session's biggest finding)

**Every Email Classifier skill iteration v3 → v7 has been ineffective.** The agent has never read the email-classifier associate skill content. Confirmed via direct system-prompt inspection from the LangSmith trace `019dd602-ddb9-7f03-946c-fcee7413e11f` (Diana run #5):

> **Email-classifier Skills**: `act-69f1278a4f26/skills` (higher priority)
>
> **Available Skills:**
>
> **(No skills available yet. You can create skills in act-69f1278a4f26/skills)**

This is the deepagents framework's skills-discovery message. Despite the harness writing `/workspace/act-69f1278a4f26/skills/email-classifier/SKILL.md` and (post commit `5ec4e9f`) passing the library dir `act-69f1278a4f26/skills` to `create_deep_agent(skills=[...])`, deepagents reports "(No skills available yet)" — meaning it's not finding any skill subdirectories with their SKILL.md inside.

**Implications:**

- Hard Rule #1 ("Never auto-create a Company"), Rule #3 (multi-1.0 → needs_review), Rule #8 (resolve errors → halt), Rule #9 (never email create), Rule #10 (Contact resolve mandatory), Rule #11 (Contact-first ordering) — **the agent has never seen any of these.**
- Every iteration of EC behavior in Sessions 9, 10, and 11 has been the agent operating on the harness DEFAULT_PROMPT alone, plus whatever it learns from `indemn skill get <Entity>` (which surfaces ENTITY auto-generated skills, NOT the associate skill).
- The improved behavior in Run #5 (agent finally called Contact resolve) came from reading the Contact entity skill — which has a Resolve section because `entity_resolve` is activated on Contact — NOT from the associate skill.

### Reproductions in LangSmith (project `indemn-os-associates`)

Five sequential traces on Diana@CKSpecialty's email (`69ea56250a2b41b7696076b3`):

| Run | Trace ID | Outcome | Diagnosis |
|---|---|---|---|
| #1 (pre-LangSmith Session 9) | n/a | EC auto-created Company `69f0df1bbca2d725ce90ed58` | Session 9 attributed to "skill compliance gap" — wrong |
| #2 (LangSmith on, CLI broken) | `019dd522-ac39-7fc2-bcab-dacdc450cfc5` | EC auto-created `69f0ee5b78abc86f9ca2a648` | **Trace showed `entity-resolve` returned HTTP 422** — Bug #34 (CLI bug). Fixed via `db97694`. |
| #3 (CLI fixed, EC v4) | `019dd589-8d80-7aa3-93af-b59aff572184` | EC tried `email create` (E11000), narrated "email already exists", harness silent-completed | Two new findings: skill update-vs-create confusion + harness `agent_did_useful_work` looseness. Latter fixed via `d914d76`. |
| #4 (EC v6, completion tightened) | `019dd5c1-3aab-7ea3-aa08-d007044570a1` | EC linked Diana to existing CK Specialty Company. Skipped Step 3 (no Contact link). | Looked like a partial win, attributed to skill needing v7. |
| #5 (EC v7, harness "skills lib dir" fix) | `019dd602-ddb9-7f03-946c-fcee7413e11f` | Agent DID call Contact entity-resolve (improvement!) but tried `email create` 4× (all failed). | **Discovered the real root cause: agent has never read the EC associate skill.** "Available Skills: (No skills available yet)" in system prompt. Step 3 came from reading the Contact entity skill, not the associate skill. |

### State at end of session

**Pipeline associates:**
- Email Classifier — **suspended** (kill switch). v7 skill in DB but agent not reading it.
- Touchpoint Synthesizer — suspended (unchanged from Session 9).
- Intelligence Extractor — active. Silent-stuck-state regression that previously caught it is fixed (`d914d76`).

**Diana@CKSpecialty's email** (`69ea56250a2b41b7696076b3`):
- status: `received` (reset)
- company: `null`
- sender_contact: `null`
- version: 11 (multiple touch-and-reset cycles this session)

**Companies in CK Specialty cluster** (multi-1.0 ambiguity case):
- `69ea8f92ff375a32fa25a056` — "Ck Specialty Insurance Associates" (name only)
- `69eaa394ff375a32fa25ab0a` — "CK Specialty" (name + domain `ckspecialty.com`)
- `69ea8eb0ff375a32fa259ffd` — "CK Specialty" (fuzzy)
- (the auto-created `69f0df...` and `69f0ee...` from Sessions 9 + 10 were rolled back)

These dupes need eventual cleanup but they're informative for testing — they reproduce the multi-1.0 scenario reliably.

**Recent OS bugs landed in parallel (other sessions, NOT this one):**
- `a355d2a` — fix(cli): use inflect for collection_name auto-derive (Bug #15)
- `0b5a484` — fix(kernel): auto-populate entity.created_by on insert (Bug #27)
- `f6f9fbe` — fix(bulk): singular delete + reject empty filter on destructive ops (Bug #2, #4)
- `d037987` — Merge bugfix/bulk-delete-trust

These aren't Session 11 work but they're on main now and may interact with our work (e.g., the inflect change affects collection naming — verify no regressions during next session).

---

## 3. The deepagents skill-discovery bug — what's known + what to investigate

This is THE thing for the next session. The whole "EC compliance" thread has been chasing a downstream symptom of this.

### What we tried this session (the journey, in order)

1. **Inlining skill content into the system prompt** (the "AI slop" fix) — Craig rejected: violates OS vision. Per the OS architecture, deepagents progressive disclosure IS the right pattern. Inlining short skills bypasses the mechanism instead of fixing it. Reverted immediately.

2. **Pass library dir to deepagents instead of per-skill paths** (commit `5ec4e9f`) — based on reading deepagents docs, `skills` parameter takes a list of skill LIBRARY directories (each containing skill subdirs with their own SKILL.md). The harness was passing per-skill subdir paths. Fixed by changing the harness to write to `<lib>/<slug>/SKILL.md` and pass `<lib>` instead of `<lib>/<slug>`. **DEPLOYED + TESTED — STILL DOESN'T WORK.** System prompt continues to say "(No skills available yet. You can create skills in act-…/skills)".

### Hypothesis space for what's actually wrong

The fix in `5ec4e9f` IS what the deepagents docs describe. So one of these must be true:

- **(A) Path resolution issue.** deepagents' default `StateBackend` interprets paths as virtual paths inside its own state. Our harness uses `LocalShellBackend` (per `harness_common/backend.py`) with `root_dir` set per-activity to `/workspace/{activity_id}`. We pass `act-{message_id[:12]}/skills` (relative path). Maybe LocalShellBackend resolves this against its `root_dir` so it becomes `/workspace/act-{X}/act-{X}/skills` — DOUBLE-NESTED → doesn't exist. Try passing just `skills` (relative to root_dir) OR the absolute path `/workspace/{activity_id}/skills/`.
- **(B) Frontmatter format issue.** Each SKILL.md has frontmatter:
  ```
  ---
  name: email-classifier
  description: <description>
  ---
  ```
  Maybe deepagents expects additional fields (license, allowed-tools, etc.) or a different format. Per the deepagents docs only `name` + `description` are required, so this is unlikely but worth checking.
- **(C) deepagents version mismatch.** Check the version of deepagents installed in the harness vs the docs we read at `https://docs.langchain.com/oss/python/deepagents/skills`. Maybe the API changed. Run `uv pip show deepagents` in the harness venv.
- **(D) LocalShellBackend doesn't support the skills mechanism.** Maybe skills only work with `StateBackend` or `FilesystemBackend`. Check deepagents source / experiment with a different backend.

### Diagnostic next steps for Session 12

1. **Read deepagents source code in the harness's installed version.** `find /Users/home/Repositories/indemn-os/.venv -path "*deepagents*"` if that env exists, or check the Docker image. Look at how `skills=` is interpreted — exact path resolution + what kind of backend it works with.
2. **Reproduce locally if possible.** Build a minimal reproduction outside the harness (just `create_deep_agent` with a known skill on disk) to isolate the bug.
3. **Check the LangSmith trace for any `read_file` tool calls.** If the agent ever tries `read_file` on the skill path on its own, that tells us the path is at least surfaced. If not, the discovery is failing entirely.
4. **Try absolute paths first** (option A above) — fastest to test. Change the harness to pass `/workspace/{activity_id}/skills` (absolute) instead of `{activity_id}/skills` (relative). Deploy + retest Diana.

### What NOT to do

- **Don't inline the skill into the system prompt.** Craig explicitly rejected this. The OS vision requires deepagents progressive disclosure to work properly, not to be bypassed.
- **Don't add more EC skill iterations until the discovery bug is fixed.** The agent isn't reading the skill regardless of what's in it. v7 → v8 → v9 won't matter.
- **Don't over-engineer the fix.** Craig pushed back on the verbose version. The change should be minimal — possibly one line at the `create_deep_agent` call site.

---

## 4. Architectural alignments from this session

These are the load-bearing decisions Craig made + we agreed on. Carry them forward.

### Path 3 for evaluations architecture

The existing `evaluations` repo (separate Indemn repo at `/Users/home/Repositories/evaluations/`, port 8002, LangSmith-based, rubric + custom LLM judges, component-scoped, single-turn / multi-turn-replay / multi-turn-simulated) eventually becomes a kernel adapter — `system_type: evaluation`, provider: `langsmith` or `indemn-evals`. Until then:

- Customer-system uses LangSmith API directly (`https://api.smith.langchain.com/api/v1/...`)
- Borrows rubric/test-set/run patterns from the evaluations repo without taking the dependency
- Native OS evaluations design doc lands in `../product-vision/` as a separate fork-session

Craig's framing: "evaluations are part of the OS vision, depending on eval results actions get taken". Long-term the eval feedback loop drives skill iteration / capability changes / etc.

### Harness reports facts; OS interprets meaning

The harness's tightened `agent_did_useful_work` (commit `d914d76`) is observation-only — "did any state-changing CLI call succeed?". It does NOT know what each associate is supposed to do. Detection of "agent didn't fulfill skill intent" lives in evals (Phase E) and observability dashboards on top of LangSmith — NOT in the harness.

My initial proposal was harness checks "did the watched entity transition" — Craig pushed back: that's domain knowledge that doesn't belong in glue code. Some associates legitimately don't transition their watched entity. The check should be domain-agnostic.

### Skills must use deepagents progressive disclosure

Don't inline skills into system prompts. The OS vision requires deepagents' skills mechanism to work. The harness's job is to write skills to the filesystem in the format deepagents expects, then pass the path to `create_deep_agent`. Currently broken — see Section 3.

### Bug fixes are 100% a priority alongside roadmap progress

Craig: "Bug fixes are 100% a priority too btw". The session's mix of feature work (LangSmith) + bug fixing (Bug #34 CLI, completion check, Document sync) was deliberate. Don't bias toward only feature work or only bugs.

---

## 5. What's next — start of Session 12

### Top priority

**Fix deepagents skill discovery** so the agent actually reads the email-classifier associate skill. See Section 3 hypothesis space + diagnostic steps. Minimal change at the `create_deep_agent` call site is the hypothesis. If the fix is non-trivial, it may need to be a fork-session.

Once skill discovery works:
1. Reactivate EC, reprocess Diana → expect agent to follow Hard Rules #1-11 from v7 (no email create, Contact resolve called, multi-1.0 → needs_review).
2. If v7 doesn't behave correctly even with skill loaded, iterate to v8 (now it MEANS something).
3. Eventually: build EC eval set (Path 3, LangSmith API directly) for durable regression coverage. Craig deferred this — bring back up after skill discovery is fixed and we have a few clean iterations.

### Other carry-over (not blocking the deepagents fix)

- **Reactivate Touchpoint Synthesizer + Intelligence Extractor** to verify cascade end-to-end (vision §2 item 4: watch cascade reliable).
- **Filed kernel bug** — `kernel/cli/app.py` has the same `_COLLECTION_LEVEL` divergence as `indemn_os/main.py`. Lower priority since the harness uses the published `indemn_os` CLI.
- **Slack ingestion** (vision §2 + roadmap Phase B continuous thread) — foundational per Apr 27 Alliance trace, still 🔴 Open.
- **Open design questions** carried forward (Opportunity vs Problem, Document-as-artifact for emails, 12 sub-stages, origin/referrer tracking, Playbook hydration mechanism).
- **Document.source enum missing `slack_file_attachment`** — small papercut.

### Roadmap-alignment check (do at session start)

After reading Section 1 + before doing work, walk through vision.md §2 (the 9 foundation items) + roadmap.md (Phase B sub-phases) and confirm what's done, what's in flight, what's open. Session 11 substantially progressed:
- ✅ Item 7 (LangSmith on harnesses — async-deepagents specifically)
- ✅ Bug #34 fix (kernel CLI)
- ✅ Silent-stuck-state regression closed (harness completion check)
- ⚠️ Item 3 (pipeline associates running hands-off) — blocked on the deepagents skill-discovery bug
- ⚠️ Item 4 (watch cascade reliable end-to-end) — only EC half-tested, TS + IE haven't been triggered autonomously yet

Items 1, 2, 5, 6, 8, 9 are also in various states — see CLAUDE.md "Where we are now" + os-learnings.md.

---

## 6. Do-not-skip reminders

Things that bit us this session and prior — codified.

1. **Do not skip Track 2 OS reads.** This session went deep on harness internals and frequent reference back to `docs/architecture/associates.md` was load-bearing. Track 2 is mandatory.
2. **Do not inline skills into system prompts.** Craig explicit: violates OS vision. deepagents progressive disclosure IS the design.
3. **Do not over-engineer.** Craig: "It could be literally 1 line in the deepagents creation". The fix should be minimal. Don't refactor signatures or add docstrings just because you can.
4. **Don't conflate "committed" with "verified".** I committed the over-engineered library-dir fix and pushed to main without testing. The fix didn't work. Always run the actual test before claiming a fix works.
5. **Branch awareness.** Craig has been working in parallel on bugfix branches. The local working tree may be on his branch when you arrive. Always `git branch --show-current` + `git status` before committing or pushing. Push to the correct branch.
6. **LangSmith is the diagnostic layer.** Use it. Every "the agent did the wrong thing" should flip to "let me look at the trace" before "let me iterate the skill". The trace shows what the agent actually saw, what it actually called, and what it actually decided.
7. **When you don't understand a third-party library, READ THE DOCS.** Don't poke at source files via `find` or `grep` when web docs exist. WebFetch the official docs first.
8. **Write the handoff at the end of every substantive session.** The Session 9 + 10 + 11 handoffs are the canonical examples. Future sessions depend on this.

---

## 7. Open design questions carried forward

Same as Sessions 9 + 10 — none resolved this session:

- **Skill compliance enforcement** — once deepagents skill discovery is fixed, we can finally test whether the v7 Hard Rules actually constrain agent behavior. If not: force-reasoning rules vs eval-driven fine-tuning.
- **Opportunity vs Problem entity** — does unmapped pain need its own entity?
- **Document-as-artifact pattern for emails** — Email entity, Document entity, or hybrid?
- **Stages — 12 sub-stages with multi-select for archetypes** (Kyle's Apr 24 ask).
- **Origin / referrer tracking** (Pat Klene → GR Little example).
- **Playbook hydration mechanism** — manual? scheduled associate? human-in-the-loop?

---

## 8. Cleanup state at end of session

- ✅ EC `69ea1bca23eefe641ea13f44` transitioned to `suspended`
- ✅ Diana@CKSpecialty `69ea56250a2b41b7696076b3` reset to `received`, no Company link, no Contact link
- ✅ No orphan auto-created Companies (verified via mongosh — last 30 min count = 0)
- ✅ All commits pushed to indemn-os main: `956d7d5`, `db97694`, `d914d76`, `5ec4e9f`
- ✅ Project docs (CLAUDE.md, INDEX.md, os-learnings.md, EC skill source) committed in operating-system os-roadmap

---

## 9. The shape of this handoff

Same template as Session 9 + 10 handoffs — the project's canonical session-handoff form. Continue the lineage. Session 12 should write its own handoff in this format at the end.

End of Session 11 handoff. Next session begins with the mandatory reading list in Section 1, in full, no skipping.
