---
ask: "Find the edge cases, gaps, contradictions, and integration points the other research areas might miss in the blueprint system design"
created: 2026-03-24
workstream: os-development
session: 2026-03-24-a
sources:
  - type: codebase
    description: "systems/session-manager/cli.py, systems/dispatch/engine.py, lib/os_state.py, systems/hive/cli.py, .claude/hooks/*"
  - type: design
    description: "2026-03-08-hive-design.md, 2026-03-24-blueprint-system-problem-statement.md, 2026-03-24-hive-phase6-brainstorm.md"
  - type: codebase
    description: "hive/.registry/ontology.yaml, hive/.registry/types/workflow.yaml, .claude/skills/code-dev/, .claude/skills/dispatch/"
---

# Blueprint System Research: Edge Cases, Gaps, and Contradictions

Research angle: the in-between. Problems that fall through the cracks between research areas.

---

## 1. Interactive Blueprint + Human Unavailability

**The scenario:** A blueprint is running in hybrid mode. Steps 1-3 were autonomous. Step 4 requires human review (e.g., "approve this draft before publishing"). Craig is running, asleep, on a call, or otherwise unavailable.

**Findings:**

- The existing session manager has no concept of "waiting for human input." Session states are: `started`, `active`, `idle`, `context_low`, `ended`, `ended_dirty`. There is no `waiting_for_human` or `blocked` state. A step that needs Craig looks identical to a step that is idle because the LLM finished its turn.

- The session `close` command in `cli.py` (line 400-415) waits 30 seconds for idle, then offers to interrupt. This is designed for cleanup, not for blocking waits. There is no mechanism for "wait indefinitely until human responds."

- The Hive workflow entity has statuses: `active`, `paused`, `completed`. There is no `blocked` or `waiting_for_input` status. The ontology has global statuses: `backlog`, `ideating`, `active`, `in-review`, `done`, `archived`. None express "blocked on human."

- The brainstorm says sessions can run without human in the loop. But the code-dev skill explicitly requires human validation at decision checkpoints ("Signals a decision has been validated: the user confirms a choice"). A blueprint that encodes the code-dev workflow assumes interactive human involvement at unpredictable intervals.

- No notification system exists. The Hive Wall tiles would show state, but Craig has to be looking at the Wall. There are no push notifications, no Slack pings, no mobile alerts. If a blueprint blocks at 3am waiting for approval, nothing notifies Craig.

- Timeout behavior is undefined. Does a step that blocks for human input for 4 hours auto-cancel? Auto-continue with a default? Stay blocked forever? The dispatch engine has `MAX_RETRIES_PER_TASK = 3` as a backstop, but that is for implementation failures, not for "human never showed up."

- The context assembly session pattern (from the Hive design doc) is explicitly "short-lived" — it terminates after writing a note. What happens if a context assembly step in a blueprint writes a note but the intended human consumer never reads it?

**Questions this raises:**
- What states should a blueprint step be able to enter beyond pass/fail?
- How does the system distinguish "step is waiting for human" from "step is idle because the LLM is done thinking"?
- What is the maximum time a step can wait? Is it configurable per step?
- What is the fallback if Craig is unreachable for hours/days?

---

## 2. Resource Contention — Repos, Sessions, APIs

**The scenario:** Two blueprints both need to modify the same repository. Or both need to use the Slack API. Or both need the same tmux session name.

**Findings:**

### Git Worktree Contention

- The session manager creates git worktrees at `.claude/worktrees/<name>` (cli.py line 161). There are already 40 worktrees on disk. Each worktree is a full working copy of the OS repo. The `git worktree add` command creates a new branch `os-<name>`.

- Two blueprints targeting the same external repo (e.g., both want to modify `indemn-platform-v2`) would create separate worktrees, but both would `git add -A && git commit` into the same repo clone path. The dispatch engine's `git_commit` function (engine.py line 301) does `git add -A` in `target_repo` — if two dispatch processes run against the same `target_repo` path simultaneously, they will corrupt each other's staging areas.

- The dispatch engine already uses a single `target_repo` path, not a worktree. Two concurrent dispatches to the same repo = guaranteed conflict. There is no locking mechanism.

- Worktrees solve this for the OS repo (each session gets its own), but the dispatch engine passes `target_repo` as a bare directory path. Nobody creates a worktree of the target repo.

### tmux Session Name Collision

- Session names are used as tmux session names with `os-` prefix (cli.py line 146). The `cmd_create` function checks for name collision (line 151-153) but only against the sessions state files. If a blueprint spawns sessions programmatically with names like `blueprint-<id>-step-1`, the naming convention must prevent collisions across all concurrent blueprints.

- The session manager rejects creation if a session with the same name exists and is not ended. But blueprints could generate names that collide with manually-created sessions.

### API Rate Limits

- The dispatch engine already encounters `rate_limit_event` messages from the Claude API (engine.py line 33, monkey-patched). Running multiple blueprints simultaneously means multiple Claude Code sessions all consuming the same subscription.

- The Claude Code subscription has rate limits. The current dispatch engine runs one task at a time (sequential loop). Blueprints with fan-out parallelism would spawn multiple concurrent sessions, multiplying API consumption.

- External APIs (Slack, Linear, Google Calendar, GitHub) also have rate limits. If a blueprint runs `hive sync linear` while another blueprint is also querying Linear through the linearis CLI, both hit the same token. No coordination exists.

### MongoDB Contention

- The Hive uses local MongoDB (`mongodb://localhost:27017`, config.py line 16). The `atomic_write_json` pattern in `os_state.py` uses file-level atomic writes (tempfile + rename) but MongoDB writes have no such guarantee across multiple CLI invocations.

- Two blueprint steps both calling `hive create note` simultaneously could produce records with colliding `record_id` slugs (the date-slug format makes same-day collisions possible, handled by `-2`, `-3` suffixes — but the collision detection requires reading existing records and creating atomically, which is not wrapped in a transaction).

- The `records.py` module would need to be examined for whether it handles concurrent inserts gracefully. Slug uniqueness enforcement under concurrent load is a classic race condition.

**Questions this raises:**
- What is the concurrency model? Serial per repo? Per blueprint? Per step? Fully parallel?
- Who prevents two blueprints from modifying the same repository simultaneously?
- Is there a resource lock table? File locks? Advisory locks in MongoDB?
- What is the maximum number of concurrent Claude Code sessions the subscription supports?

---

## 3. Promoting Ad-Hoc Work to a Blueprint

**The scenario:** Craig works interactively on something new. The pattern emerges. He says "this should be a blueprint."

**Findings:**

- There is no mechanism today to introspect what happened during a session and extract it as a reusable workflow. Session transcripts exist as `.jsonl` files, but these are raw conversation logs — not structured workflow definitions.

- The Hive captures decision checkpoints and session summaries as knowledge records. But these are narrative prose, not executable step definitions. A decision like "Use argparse instead of Click" is not a blueprint step.

- The existing dispatch system uses beads epics as the executable plan format (YAML-like tasks with acceptance criteria). Blueprints would need a different format — beads are specific to a single execution, not reusable templates.

- The brainstorm mentions "one-time blueprints" vs "repeatable blueprints." The promotion path would be: one-time execution (ad-hoc) → observe the pattern → extract a repeatable blueprint. But the extraction step is entirely manual. The system captures _what was decided_ (decisions) and _what happened_ (session summaries) but not _the sequence of tool invocations that accomplished it_.

- Skills already encode reusable patterns (code-dev phases, brainstorm-hive checkpointing). The gap is that skills are instructions for a Claude Code session to follow, not executable state machines. The promotion path might be: ad-hoc work → decisions/summaries in Hive → human writes a skill → skill gets promoted to blueprint definition. But this requires a human to distill the pattern.

- The code-dev skill's phases (design → review → planning → execution → testing → deployment) are essentially a blueprint expressed as a skill. But they have no execution state, no step tracking, no ability to resume from a specific phase. They are guidelines, not orchestration.

**Questions this raises:**
- What format are blueprints defined in? YAML? Python? Skill-like markdown?
- Can a session's tool usage log be post-processed into a draft blueprint?
- Who writes the blueprint — Craig manually, an LLM, or some extraction tool?
- Is there a "record mode" where the system watches what you do and templates it?
- What is the minimum viable format for "a simple blueprint that just runs 3 CLI commands in sequence"?

---

## 4. Blueprint Inter-Dependencies and Triggering

**The scenario:** Blueprint A (morning consultation) discovers that a critical Linear issue was assigned overnight. This should trigger Blueprint B (code development workflow for the issue). Blueprint B's output might trigger Blueprint C (content pipeline — blog about the feature).

**Findings:**

- The problem statement says blueprints are "fractal" — a step can be a sub-blueprint. But it is silent on whether a blueprint can trigger a _sibling_ blueprint (not a sub-step, but a separate blueprint execution).

- The dispatch engine is fire-and-forget: `asyncio.run(dispatch(epic_id))` runs to completion. There is no event bus, no pub/sub mechanism, no way for one dispatch run to signal another.

- The Hive has no event/trigger system. Records are created and queried, but there is no "when record X is created, do Y" mechanism. The sync adapters pull on schedule or command — they do not push events.

- The brainstorm mentions event-triggered blueprints but does not elaborate on the event source. Current event sources: Claude Code hooks (SessionStart, Stop, UserPromptSubmit, TaskCompleted, SessionEnd) and the statusLine hook. These are per-session, not per-record or per-blueprint.

- The workflow entity's `status` field changes when a system updates it. If Blueprint A updates a workflow to "completed," there is no watcher that triggers Blueprint B. You would need polling or a change stream.

- MongoDB supports change streams for real-time notifications on collection changes. But the Hive CLI currently does read-modify-write without change streams. Adding a watcher daemon would be new infrastructure.

- Shared state between blueprints would have to go through the Hive. Blueprint A creates a knowledge record. Blueprint B reads it. But the timing is unclear — when does Blueprint B know to look? Does it poll? Does it get notified?

**Questions this raises:**
- Can blueprints trigger other blueprints? Or only sub-blueprints (child steps)?
- What is the event model? What events can blueprints emit? What can they listen for?
- Is there a queue/bus, or does everything go through Hive records as the communication channel?
- What prevents circular triggers (A triggers B triggers A)?
- How is the Hive record a communication channel if there are no watchers?

---

## 5. Security and Guardrails for Autonomous Execution

**The scenario:** A scheduled blueprint runs at 7am. It has `bypassPermissions` mode. A step sends an email to a customer. Another step pushes code to the production branch. Another step posts to the company Slack channel.

**Findings:**

- The existing dispatch engine hardcodes `permission_mode="bypassPermissions"` (engine.py lines 213, 251). There is no per-task or per-step permission granularity. The entire dispatch session runs with full permissions.

- The secrets-guard hook (`.claude/hooks/secrets-guard.sh`) blocks `.env` reads and secret variable echoing. But it does NOT block sending emails, posting to Slack, pushing to production branches, or any other destructive external action. It only guards credential exposure.

- There is no audit trail for autonomous actions. The dispatch engine logs to stdout and writes `learnings.md`. But there is no record of "at 7:02am, this blueprint sent an email to customer X with content Y." The Hive creates awareness records, but those are created by the system CLI, not enforced by infrastructure.

- The session manager's permission modes are binary: `bypassPermissions` (no prompts at all) or `acceptEdits` (approve file edits but not reads). Neither mode has per-tool granularity (e.g., allow Bash commands but block `git push` to certain branches).

- The brainstorm says "not all sessions are interactive." The problem statement says blueprints can be "fully autonomous." But the current hook infrastructure has no mechanism to restrict what autonomous sessions can do beyond the secrets-guard.

- The `allowed_tools` parameter in the Agent SDK (dispatch design doc) can restrict which tools a session has access to. But this is set per-session at creation time, not per-step. A blueprint with 5 steps where only step 3 should be able to post to Slack would need different tool configurations per step, which means different sessions.

- No kill-switch exists. If a runaway autonomous blueprint is doing damage, the only option is `session destroy` (which force-kills the tmux session) or killing the Python process. There is no "pause all blueprints" command.

**Questions this raises:**
- What is the permission model per step? Per blueprint? Per harness?
- Are there actions that should NEVER be autonomous (e.g., sending customer-facing emails)?
- How are destructive actions logged in a way that can be audited after the fact?
- Is there a concept of "approval queue" where autonomous steps can queue actions for human approval?
- What is the kill-switch? How do you stop all autonomous execution immediately?
- Should there be a "dry run" mode where the blueprint executes but all external actions are simulated/logged instead of executed?

---

## 6. Blueprint Versioning and In-Flight Executions

**The scenario:** A content pipeline blueprint is in the middle of execution (step 3 of 6 — draft is being refined). Craig updates the blueprint definition to add a new "SEO optimization" step between steps 3 and 4. What happens to the in-flight execution?

**Findings:**

- The dispatch engine reads the task list once at the start and refreshes children on each loop iteration (engine.py line 383: `children = get_children(epic_id, beads_dir)`). If someone adds a new child bead mid-execution, it would be picked up on the next iteration. But modifying existing children's definitions mid-execution is undefined behavior.

- Blueprint definitions do not exist yet as versioned artifacts. Skills are files in `.claude/skills/` — they are versioned by git but there is no concept of "this execution uses skill version X." The session loads whatever skill is on disk when it starts.

- The Hive design doc mentions that knowledge records are git-tracked markdown files. If blueprints are also markdown/YAML files, they get git versioning for free. But the execution state would need to reference the specific version (commit hash) of the blueprint definition it started with.

- Beads (the current task tracking format) are not versioned. A bead's description can be edited at any time. If the dispatch engine re-reads the epic description mid-execution, it gets the latest version, not the version it started with.

- The problem statement says "blueprint state lives in the Hive, not in sessions." If the blueprint definition is a Hive record and execution state is also a Hive record, editing the definition while execution state references it creates a coupling that needs explicit handling.

**Questions this raises:**
- Are blueprint definitions immutable once execution starts? Or does the execution pin to a specific version?
- If a blueprint definition changes, do in-flight executions continue with the old definition or adopt the new one?
- What is the format for blueprint definitions? Is it the same as the execution state?
- How do you roll back a blueprint definition change? Is git history sufficient?

---

## 7. Error Escalation Cascade

**The scenario:** A scheduled blueprint step fails. Retries 3 times (per the dispatch engine's MAX_RETRIES_PER_TASK). All fail. A notification is sent to Craig. Craig is in a meeting for 2 hours. Meanwhile, downstream steps are blocked. Other blueprints that depend on this blueprint's output are also blocked.

**Findings:**

- The dispatch engine's only error response is: exhaust retries, then skip the task and continue to the next one. If the failed task blocks downstream tasks (via dependencies), those also get skipped. The engine ends with a summary: "3/7 tasks passed, 4 failed." No escalation occurs.

- There is no notification mechanism when a task exhausts retries. The dispatch engine prints to stdout, writes to `learnings.md`, and exits. If this is running in a tmux pane, nobody sees it unless they look.

- The learnings file is append-only per execution. It captures failure reasons but does not flag them for attention. There is no priority/severity classification on failures.

- The session manager's stale detection (cli.py lines 285-296) marks sessions as `ended_dirty` if the tmux session disappears. But a blueprint execution that fails is not the same as a session becoming stale — the execution completed, it just didn't succeed.

- There is no concept of "escalation policy." The system does not know: "if this step fails, try an alternative approach" vs "if this step fails, alert Craig immediately" vs "if this step fails, pause and wait for human intervention."

- Cross-blueprint dependency failure is unaddressed. If Blueprint A's output is Blueprint B's input, and Blueprint A fails, Blueprint B either (a) never starts, (b) starts with stale/missing input, or (c) starts and fails. No coordination mechanism exists between blueprint executions today.

**Questions this raises:**
- What is the escalation chain? Step fail → retry → ??? → notify → ??? → human fix → ???
- Can a blueprint define fallback steps (if A fails, try B)?
- How are downstream blueprints notified that an upstream dependency failed?
- Is there a "dead letter" concept for permanently failed steps?
- What is the SLA for human response to escalated failures?

---

## 8. Long-Running and Never-Ending Blueprints

**The scenario:** A "monitor production health" blueprint runs every 15 minutes indefinitely. A "sync external systems" blueprint runs every hour. A "process incoming emails" blueprint watches for new email and processes each one.

**Findings:**

- The dispatch engine runs once and exits. It is not a daemon. Making it long-running would require either (a) a cron job that re-invokes it, (b) a daemon wrapper, or (c) a fundamentally different execution model.

- The problem statement says "scheduled autonomous workflows" should run on schedule (e.g., 7am weekdays). This implies cron-like scheduling. macOS has `launchd` for scheduling. Claude Code apparently has scheduling capabilities (mentioned in the brainstorm: "Claude Code now has cron/scheduling capabilities via a command").

- There are no long-running processes in the OS today. All sessions are interactive or run-to-completion. The dispatch engine is run-to-completion. The Hive CLI is command-line invocations. Even the OS Terminal is a web server that serves a UI — it doesn't orchestrate work.

- Resource accumulation is a concern for never-ending blueprints. Each execution creates session state files, worktrees, tmux sessions, knowledge records, and log entries. The sessions directory already has 79 state files. A blueprint running every 15 minutes would create 96 session state files per day, 672 per week. No cleanup daemon exists.

- The Hive's `hive archive` command can archive stale records, but it requires manual invocation. There is no automatic cleanup for execution artifacts from recurring blueprints.

- tmux session accumulation: each session creates a tmux session. Recurring blueprints would need to reuse session names or clean up after themselves. The current `cmd_create` blocks if a session with the same name exists.

- Git worktree accumulation: there are already 40 worktrees on disk. Recurring blueprints that create worktrees without cleanup would exhaust disk space.

**Questions this raises:**
- What is the lifecycle of execution artifacts from recurring blueprints? Auto-cleanup? TTL?
- Is there a daemon process, or is everything cron-triggered?
- How many concurrent tmux sessions can the system handle before degrading?
- How many worktrees can git manage before performance degrades?
- What is the cleanup strategy? Who cleans up after recurring blueprints?
- What is the monitoring story for the monitoring blueprints themselves? Who watches the watchers?

---

## 9. Scale: 50+ Blueprints Scheduled and Running

**The scenario:** Craig has 15 projects. Each project has 2-3 recurring blueprints (morning sync, progress check, deployment monitor). Plus ad-hoc blueprints for active work. Total: 50+ blueprint definitions, 10-20 potentially running at any time.

**Findings:**

- The session manager's `list_sessions` function (cli.py line 96) scans every `.json` file in the sessions directory sequentially. At 79 files, this is fast. At 500+ files (from recurring blueprint sessions), it would degrade. No indexing, no database — just filesystem scan.

- The OS Terminal UI polls session state via Express API routes. With 50+ active sessions, the polling load increases linearly. The WebSocket relay handles one terminal per connection. 50 concurrent terminals would mean 50 WebSocket connections.

- Claude Code subscription rate limits are the binding constraint. If each blueprint step requires a Claude Code session, and the subscription allows N concurrent sessions, then the system is bounded by N. The current dispatch engine runs sequentially (one session at a time). Parallel execution across blueprints would hit this limit.

- Memory: each Claude Code session consumes memory for the model context. Each tmux pane consumes memory. Each worktree consumes disk. The brainstorm mentions 3-5 active sessions as Craig's norm. Scaling to 20+ concurrent sessions is a different resource profile.

- Priority and queuing: the dispatch engine picks tasks by dependency order, not by priority. If 20 blueprints all want to run, there is no queue, no priority scheduler, no resource allocator. They would all try to run simultaneously.

- The Hive Wall would need to display 50+ tiles representing active/scheduled blueprints. The current design shows tiles for all active records. Blueprint executions would either drown out other tiles or need a separate view.

**Questions this raises:**
- What is the maximum concurrent execution capacity? (bound by Claude subscription, memory, tmux limits)
- Is there a priority queue for blueprint executions?
- How does the scheduler decide which blueprint runs when resources are scarce?
- Can blueprints be paused/preempted in favor of higher-priority work?
- What is the resource budget (tokens, dollars, sessions) per blueprint? Per day? Per project?
- How does the Hive Wall scale visually with 50+ execution tiles?

---

## 10. Blueprint-Project-System Relationship Model

**The scenario:** The "content pipeline" blueprint is used by the Career Catalyst project and also by the Indemn marketing project. The blueprint uses the content system's CLI. Is the blueprint owned by the system, the project, or neither?

**Findings:**

- The OS has three primitives: Skills (capabilities), Projects (memory), Systems (processes). The dispatch design doc establishes this hierarchy. But the problem statement says "dispatch is replaced by the blueprint execution framework." This means blueprints absorb one of the three primitives.

- Today's structure:
  - Skills live in `.claude/skills/<name>/` — reusable, stateless
  - Projects live in `projects/<name>/` — have state (INDEX.md, beads, artifacts)
  - Systems live in `systems/<name>/` — have state (SYSTEM.md, engine code)

- The problem statement says "blueprints belong to systems but can use multiple systems." This implies blueprints are owned by systems. But the brainstorm talks about per-project blueprints ("a feature build, a particular codebase change — executed once"). A one-time blueprint for a project is not a system capability.

- The Hive design doc says "systems own workflow lifecycle, not the Hive." The workflow entity is created by the system CLI. But blueprints would also create workflow entities (or be the mechanism for creating them). This creates a potential conflict: does the blueprint runner create the workflow, or does the system CLI?

- The Hive has entity types: project, workflow, and the type registry. There is no `blueprint` entity type. Where do blueprint definitions live? As a new entity type? As knowledge records tagged `blueprint`? As files in `systems/<name>/blueprints/`?

- The code-dev skill is `user-invocable: false` — it is automatically invoked by Claude when code development context is detected. The brainstorm-hive skill is also `user-invocable: false`. These skills are essentially blueprints expressed as Claude instructions. The overlap between skills and blueprints is significant and ambiguous.

- The content system lives in a separate repository (`/Users/home/Repositories/content-system/`). Its `cs.py` manages state. A blueprint that uses the content system must either call `cs.py` directly or call Hive CLI which calls `cs.py`. The layering is unclear.

**Questions this raises:**
- Where do blueprint definitions physically live? Filesystem? MongoDB? Both?
- Who owns a blueprint — a system, a project, or is it standalone?
- Can the same blueprint be used by different projects with different configurations?
- How does a blueprint parameterize itself per-project? (e.g., "content pipeline" blueprint for different brands)
- What is the relationship between skills and blueprints? Are skills absorbed? Do they coexist?
- Is `workflow` the right entity type for blueprint execution, or do we need a separate `execution` or `thread` type?

---

## 11. Session Lifecycle Events and Blueprint Awareness

**The scenario:** A blueprint step is running in a Claude Code session. The session hits context_low (10% remaining). Or the session crashes. Or the machine restarts.

**Findings from session-manager infrastructure:**

- The hook infrastructure fires events: `SessionStart`, `Stop` (LLM turn completed), `UserPromptSubmit`, `TaskCompleted`, `SessionEnd`. The `statusLine` hook tracks `context_remaining_pct`. These all update the session state file.

- The `context_low` state (update-context.py line 57-68) is detected and recorded. But nobody acts on it. The session continues until compaction kicks in or the context is exhausted. For blueprint steps, context exhaustion during a long step means loss of partial progress.

- The `ended_dirty` state means the tmux session disappeared without graceful close. The session manager detects this (cli.py line 285-296) on the next `list` call. But the blueprint runner would not know until it checks. There is no push notification that a session died.

- Machine restart kills all tmux sessions. The sessions skill documents a recovery flow (SKILL.md lines 76-106) that is entirely manual. Blueprint recovery after restart is unaddressed.

- The dispatch engine is a Python process in a tmux pane. If the tmux pane dies, the engine dies. In-flight work may be partially committed. The dispatch engine has no checkpointing of its own state — it tracks progress via beads, but the engine's loop state (current iteration, current task, attempts counter) is in-memory only.

- Assembly sessions (cli.py line 222-253) are one-shot: send first message, wait for completion. But there is no timeout on completion. If the assembly session hangs, nothing detects it.

**Questions this raises:**
- How does the blueprint runner detect that a session has died mid-step?
- What happens to in-progress work when a session hits context exhaustion?
- How does the system recover from a machine restart? Is blueprint execution state durable?
- Should the blueprint runner have its own health check / heartbeat mechanism?
- What is the retry policy for infrastructure failures (session crash) vs task failures (LLM couldn't do it)?

---

## 12. Data Privacy and Domain Boundaries

**The scenario:** Craig has three domains: Indemn (work), Career Catalyst (side business), Personal. A morning consultation blueprint pulls from all three. An Indemn deployment blueprint should not see personal notes. A content blueprint for Career Catalyst should not reference Indemn customer data.

**Findings:**

- The Hive has a `domains` field on every record. The ontology defines three domains: `indemn`, `career-catalyst`, `personal`. Records can belong to multiple domains.

- Context assembly is not domain-scoped by default. The Hive design doc says the context assembly agent searches broadly. `hive search` and `hive refs` do not filter by domain unless `--domains` is explicitly passed.

- The secrets-guard hook protects credentials but not data. There is no mechanism to prevent a session working on Indemn code from reading personal notes in the Hive.

- The dispatch engine has `permission_mode="bypassPermissions"`. It can read any file on disk, query any MongoDB collection, and access any Hive record regardless of domain.

- Some Hive records contain information that should not cross domain boundaries: customer names (Indemn), personal health notes (personal), financial details (Career Catalyst). The current system has no access control on records.

- Blueprint definitions would need domain scoping. An autonomous Indemn blueprint should not create records in the personal domain, and a personal blueprint should not reference Indemn customer data.

- The Hive's `hive sync` adapters pull from domain-specific external systems (Linear for Indemn, personal Calendar for personal). But once records are in the Hive, there is no domain boundary enforcement.

**Questions this raises:**
- Should blueprints have domain restrictions (can only read/write records in certain domains)?
- Is domain enforcement done at the CLI level, the MongoDB level, or the blueprint runner level?
- What happens when a record belongs to multiple domains? Does an Indemn-scoped blueprint see it?
- Is there a risk of personal data leaking into Indemn content through the flywheel mechanism?
- Should the context assembly agent for Indemn work be constrained to Indemn records only?

---

## 13. Testing Blueprints Before Deployment

**The scenario:** Craig writes a new "customer onboarding" blueprint. He wants to test it before scheduling it to run every time a new customer signs up.

**Findings:**

- There is no test infrastructure for blueprints. The dispatch engine can only run against real repos and real beads. There is no mock/sandbox mode.

- The existing test suite (`tests/test_session_cli.py`) tests the session manager CLI functions but uses mocked subprocess calls. There is no integration test that actually creates a session, runs a dispatch, and verifies the output.

- The Hive has a local MongoDB instance, which could serve as a sandbox. But there is no concept of a "test Hive database" vs "production Hive database." Everything runs against the same `hive` database on `localhost:27017`.

- A blueprint that sends Slack messages, pushes code, or creates Google Docs cannot be safely tested without side effects. There is no dry-run mode in any of the existing CLIs (the Hive CLI, the session CLI, the dispatch engine).

- The `hive archive --dry-run` flag exists (SKILL.md line 158), suggesting the pattern of dry-run flags is established but not pervasive.

- Skills are tested by running them. There is no skill test framework. A blueprint (which absorbs the skill's role) would similarly only be testable by execution.

**Questions this raises:**
- Is there a dry-run mode for blueprints?
- Can blueprints run against a test Hive database?
- How do you test blueprints that have side effects (sending emails, posting to Slack)?
- Is there a concept of "staging" vs "production" for blueprint definitions?
- Can you "step through" a blueprint one step at a time for debugging?

---

## 14. Migration Path: From Skills + Manual Sessions to Blueprints

**The scenario:** Today, Craig uses skills (code-dev, brainstorm-hive, call-prep) and manually manages sessions. Tomorrow, blueprints should handle this. What is the transition?

**Findings:**

- The problem statement says "Dispatch is replaced by the blueprint execution framework." This means the dispatch engine (`systems/dispatch/engine.py`) and its skill (`.claude/skills/dispatch/SKILL.md`) become legacy. But the engine has working Agent SDK integration, beads integration, and verification patterns that the blueprint system needs.

- The problem statement also says "Playbooks are absorbed as the context-assembly step of blueprints." Playbooks are part of the Hive design doc's context assembly system (each system defines its own context playbook). These are markdown files in `systems/hive/playbooks/`. They become blueprint steps.

- Skills like `code-dev` and `brainstorm-hive` are `user-invocable: false` — Claude auto-invokes them. Converting these to blueprints changes their invocation model. Currently, Claude reads the skill and follows its instructions. In a blueprint model, the blueprint runner would invoke the skill's logic as a step.

- The code-dev skill's phases (design → review → planning → execution → testing → deployment) map naturally to blueprint steps. But each phase today is guided by the skill's markdown instructions, not by an orchestrator. The human (or Claude's judgment) decides when to transition phases. In a blueprint, phase transitions would be explicit step boundaries.

- The morning skill, weekly-summary, and call-prep are workflow skills that map cleanly to scheduled blueprints. They already have defined steps and produce specific outputs.

- The session manager would need to be aware of blueprints. Currently it creates sessions with a name, project, and optional add-dirs. Blueprint execution would need additional metadata: which blueprint, which step, which execution ID. The session state file format would need extension.

- The Hive workflow entity currently tracks long-running work with `sessions` (a list of session IDs). Blueprint execution would create a more structured relationship: execution → steps → sessions. This is a superset of the current model but changes the data shape.

**Specific coexistence problems:**
- If blueprints and manual skills coexist during migration, how does the system know whether a code-dev session is blueprint-driven or skill-driven?
- If some workflows use blueprints and others still use INDEX.md + skills, context assembly needs to handle both.
- The `hive create workflow` command would need to optionally associate a workflow with a blueprint definition.
- Beads currently own task tracking for dispatch. Blueprints may use a different task format. During migration, both formats would exist.

**Questions this raises:**
- Is the migration big-bang or incremental?
- Can skills and blueprints coexist? For how long?
- What happens to the dispatch engine? Is it refactored into the blueprint runner, or deprecated?
- How do you convert an existing skill (markdown instructions) into a blueprint (executable steps)?
- What is the minimum change to the session manager to support blueprint-driven sessions?

---

## 15. Contradictions and Tensions in the Source Material

**Explicit contradictions found:**

1. **Session-count agnostic vs. session-as-primitive.** The problem statement says blueprints are "session-count agnostic" — state lives in the Hive, not the session. The brainstorm says "sessions are the underlying primitive of Hive workflows — every piece of work happens through a session." If sessions are the primitive but blueprints don't care about session count, the execution model is underspecified. What actually runs the work if not a session? The answer is probably "a session runs each step, but the blueprint doesn't care which session or how many." But this means the blueprint runner must manage session lifecycle, which is currently the session manager's job.

2. **LangGraph is the orchestration engine vs. simple blueprints should be simple.** The problem statement says "LangGraph is the orchestration engine for complex blueprints." It also says "simple blueprints should be simple to define and run" and "don't require LangGraph for a 3-step workflow." This creates a two-tier execution model that needs careful design. A 3-step blueprint and a LangGraph-orchestrated blueprint need different runners, different definition formats, and different debugging tools.

3. **Harness-agnostic vs. everything in tmux.** The problem statement says "steps can execute via Claude Code sessions, Python scripts, CLI commands, LangGraph agents, or any other harness." But the infrastructure note says "the execution primitive is a tmux terminal — anything that can run in a terminal can be a step." This means the harness abstraction is really "things you can run in tmux," which excludes some harnesses (e.g., direct Agent SDK Python calls that produce structured output, or LangGraph agents that run in a persistent Python process).

4. **Infrastructure-level tracing vs. self-compressing system.** The problem statement says "infrastructure-level tracing, not self-reported by the executing session." But the "self-compressing" property says "as execution proceeds, artifacts are created in the Hive" — which IS self-reporting. The executing session creates Hive records as a byproduct of working (via the code-dev skill, brainstorm-hive skill, etc.). The tension is: does the blueprint runner trace execution (infrastructure), or does the session report what it did (self-report), or both?

5. **Dispatch replaced vs. Dispatch is the only working execution engine.** The problem statement says "Dispatch is replaced by the blueprint execution framework." But dispatch is the only proven execution infrastructure: it has Agent SDK integration, beads task management, verification loops, learnings accumulation, and git commit management. The blueprint system would need to reproduce all of this functionality plus add orchestration, scheduling, and multi-harness support. This is a large scope expansion.

**Tensions (not contradictions but design pressures):**

6. **Simplicity vs. power.** The philosophy doc says "no magic, no abstraction for abstraction's sake." The blueprint system is inherently an abstraction layer over sessions, skills, and the Hive. The tension is between making blueprints powerful enough to handle all scenarios (fan-out, conditional routing, multi-harness, cross-system, scheduled) while keeping simple cases simple. Every workflow engine that has tried to solve this (Airflow, Temporal, Prefect, GitHub Actions) has ended up complex.

7. **CLI-first philosophy vs. orchestration.** The OS philosophy is "Claude Code is expert at using CLIs." Blueprints are orchestration. Orchestration typically requires a daemon/service, not CLI invocations. The dispatch engine is the closest thing to a daemon, and it is a one-shot Python script. Scaling to scheduled recurring blueprints requires something that is always running — which is a departure from the CLI-first pattern.

8. **The Hive as brain vs. The Hive as execution state store.** The design doc says "the Hive is a brain; systems are the hands." Blueprints store execution state in the Hive. This makes the brain also partly a nervous system (tracking in-flight execution, step completion, failure states). The Hive was designed for knowledge and awareness, not for operational state machines.

---

## Summary of the Hardest Problems

Ranked by difficulty and impact:

1. **Resource contention for concurrent execution** — no locking, no coordination, no queue. Everything assumes sequential single-user operation.
2. **No notification/event system** — everything is pull-based (polling session state, scanning directories). Push notifications for blueprint events do not exist.
3. **The gap between skills and blueprints** — skills are instructions; blueprints are executable state machines. The conversion path is unclear and the coexistence model is undefined.
4. **Scale of recurring blueprint artifacts** — session files, worktrees, Hive records, tmux sessions all accumulate without cleanup.
5. **Security model for autonomous execution** — `bypassPermissions` is the only proven autonomous mode, with no per-action granularity.
6. **Machine restart recovery** — all in-memory state (dispatch engine loop, tmux sessions) is lost. No durable execution checkpointing.
7. **The orchestration daemon problem** — CLI-first philosophy meets the need for something always-running that manages schedules and reacts to events.
