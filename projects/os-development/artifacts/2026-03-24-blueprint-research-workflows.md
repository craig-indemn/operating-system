---
ask: "Map real workflows to blueprint candidates — categorize by complexity, automation potential, frequency, and systems involved"
created: 2026-03-24
workstream: os-development
session: 2026-03-24-a
sources:
  - type: filesystem
    description: "All 16 project INDEX.md files, 4 system SYSTEM.md files, 34 skills, 4 playbooks, session-manager CLI, Hive CLI implementation"
  - type: design
    description: "Hive design doc (2026-03-08), dispatch design (2026-02-19), Phase 6 brainstorm (2026-03-24), blueprint problem statement (2026-03-24)"
---

# Blueprint Research: Mapping Real Workflows to Blueprint Candidates

## Angle 1: What Craig Actually Works On (From Project Evidence)

### Active Projects (16 total, from `projects/*/INDEX.md`)

| Project | Domain | Nature | Status |
|---------|--------|--------|--------|
| os-development | OS infra | System building, design iteration | Active — Hive phases 1-5 complete, Phase 6 (blueprints) in design |
| platform-development | Indemn eng | Feature dev across 6+ repos, eval framework, deployment | Active — prod deployed, ongoing feature work |
| voice-evaluations | Indemn eng | Multi-repo feature across evaluations, voice-livekit, observatory, platform-v2 | Active — implemented, blocked on Langfuse creds |
| oconnor-evaluations | Indemn eng | Running/refining eval rubrics and test sets for customer agents | Active — 2 of 4 agents evaluated |
| os-evaluations | Indemn eng | Running evaluations on prod agents, Jarvis improvements | Active — Family First at 40% pass |
| devops | Indemn infra | AWS secrets migration across 12 services, CI/CD | Active — 12 PRs open, awaiting review |
| content-system | Content | Blog pipeline, brand identity, multi-platform publishing | Active — 2 posts done, personal brand established |
| web-operator | Indemn eng | Browser automation for insurance workflows in Applied Epic | Active — endorsement path built, model testing |
| gic-observatory | Indemn customer | Customer-specific analytics features in Observatory | Active — features on main, blocked on prod deploy |
| observatory | Indemn eng | Auth fixes, feature PRs for Observatory platform | Active — waiting on PR merges |
| engineering-blog | Indemn content | Astro blog at blog.indemn.ai, deployment pipeline | Active — deployed, needs Vercel integration |
| series-a | Indemn biz | Fundraising materials, pitch deck, data story | Active — pitch slide v1 approved |
| nvidia-inception | Indemn biz | NVIDIA accelerator application, AWS credits | Active — waiting on Cam's review |
| ringcentral-integration | Indemn customer | Customer phone system integration design | Blocked — waiting on customer response |
| audio-transcription | Indemn customer | Transcription pipeline, capability document | Complete |
| analytics-dashboard | Indemn eng | Usage analytics feature in Observatory | Complete |

**Observations:**
- Work spans 5 distinct categories: engineering (7), infrastructure (1), content (2), business/fundraising (2), customer-specific (4)
- Most projects involve multiple repos and multiple sessions
- Many projects are blocked on external dependencies (reviews, credentials, customer responses)
- Engineering projects are the heaviest — each involves 5-20+ sessions and 3-6 repos

### What Craig Does Day-to-Day (Inferred from Project Activity)

From session histories across all 16 projects, Craig's actual activities include:

1. **Design/brainstorming sessions** — Extended voice brainstorming (via Wispr), iterating on architecture, captured as design docs and decision checkpoints. (os-development: 8+ design sessions on the Hive alone)
2. **Code implementation sessions** — Writing code across service repos, debugging, testing. (platform-development: 10+ sessions, voice-evaluations: 5 sessions)
3. **Code review and debugging** — Reviewing teammate branches, analyzing test failures, fixing bugs. (web-operator: analyzing Rudra's branch; platform-development: COP-325 17-issue review)
4. **Evaluation runs and analysis** — Running AI agent evaluations, classifying failures, iterating rubrics/test sets. (oconnor-evaluations, os-evaluations: 5+ sessions each)
5. **DevOps/infrastructure work** — AWS secrets migration, CI/CD setup, deployment. (devops: 6 sessions)
6. **Content creation** — Blog posts, brand identity, newsletter setup. (content-system: 4+ sessions)
7. **Research and analysis** — Audio transcription pipeline, model testing, platform research. (audio-transcription: 5 sessions, web-operator: model comparison)
8. **Customer-facing preparation** — Call prep, pitch decks, application materials. (series-a, nvidia-inception, ringcentral)
9. **Morning planning / session management** — Starting the day, checking what's active, prioritizing. (sessions skill, morning skill)
10. **Report generation** — Observatory reports, weekly summaries, eval trace exports. (gic-observatory, eval-analysis skill)
11. **PR management** — Creating PRs, tracking review status, managing merge order. (devops: 12 PRs, voice-evaluations: 5 repos)
12. **Data exploration** — MongoDB queries, Postgres queries, API exploration. (analytics-dashboard, gic-observatory, series-a)
13. **Deployment** — Docker, EC2, Vercel, self-hosted runners. (platform-development, engineering-blog, devops)
14. **Communication** — Slack messages, email, sharing results with teammates. (oconnor-evaluations: sharing with Pete, devops: coordinating with Dhruv)
15. **System building** — Building the OS itself, session manager, Hive, terminal UI. (os-development: 20+ sessions)

---

## Angle 2: Current Systems and Their Operational Patterns

### Session Manager (systems/session-manager/)
- **What it does:** Creates Claude Code sessions in tmux with git worktree isolation, tracks state via hooks, lifecycle CLI
- **Operational pattern:** `session create` -> `session list` -> `session attach` -> `session send` -> `session close` -> `session destroy`
- **State:** One JSON file per session in `sessions/`, updated by hooks (SessionStart, Stop, UserPromptSubmit, TaskCompleted, SessionEnd)
- **Key finding:** Sessions are the atomic execution unit of all work. Everything happens through sessions. The session manager already provides the infrastructure for spawning, monitoring, and closing sessions. A blueprint system would use this as its execution substrate.

### Dispatch (systems/dispatch/)
- **What it does:** Executes beads epics (parent task with child tasks) via Agent SDK, fresh context per task, separate verification sessions
- **Operational pattern:** Ralph loop — read spec -> pick next task -> spawn session -> verify -> update beads -> loop
- **State:** Beads (task status), learnings file (append-only), git history
- **Key finding:** Dispatch is the existing autonomous execution engine. It already implements "fresh context per task" and "independent verification." The blueprint problem statement explicitly says "Dispatch is replaced by the blueprint execution framework." Dispatch's patterns (fresh context, verification loop, learnings accumulation) are blueprint primitives.

### The Hive (systems/hive/)
- **What it does:** Two-layer data (entities in MongoDB, knowledge as markdown), 14-command CLI, semantic search, sync adapters, context assembly playbooks
- **State:** MongoDB `hive` database (entities + knowledge index), `hive/` vault directory (knowledge markdown files), `.registry/` (type schemas + ontology)
- **Current sync adapters:** Linear, Calendar, Gmail, Slack, GitHub — all built
- **Current playbooks:** morning, content, code-dev, ceo-weekly — all built
- **Key finding:** The Hive already has the context assembly infrastructure. Playbooks are essentially the "context gathering" step of what would be a blueprint. The Hive CLI is what agents use during execution. Blueprints would formalize what playbooks currently do informally.

### OS Terminal / Hive UI (systems/os-terminal/)
- **What it does:** Bloomberg-style terminal grid evolved into Hive UI (Wall + Focus Area), tiles for all records, session spawning with context assembly
- **Key finding:** The UI already supports the "observe what's running" requirement. Tiles represent running sessions, Hive records, and synced items. Blueprint executions would naturally appear as tiles on the Wall.

---

## Angle 3: Current Skills as Blueprint Building Blocks

### Tool Skills (18 total) — Atomic Capabilities
| Skill | What It Wraps | Blueprint Role |
|-------|--------------|----------------|
| slack | agent-slack CLI | Input (read channels) + Output (post messages) |
| google-workspace | gog CLI | Input (email, calendar) + Output (docs, emails) |
| linear | linearis CLI | Input (issues) + Output (status updates) |
| github | gh CLI | Input (PRs, issues) + Output (PRs, reviews) |
| stripe | stripe CLI | Input (revenue data) |
| airtable | curl REST | Input (configs, records) |
| apollo | curl REST | Input (company enrichment) |
| vercel | vercel CLI | Output (deployments) |
| postgres | psql | Input (meeting intelligence data) |
| mongodb | mongosh | Input (tiledesk data) |
| local-dev | local-dev.sh | Environment setup step |
| agent-browser | agent-browser CLI | Execution (web automation) |
| image-gen | Gemini API | Output (visual assets) |
| excalidraw | excalidraw-to-svg | Output (diagrams) |
| langfuse | curl REST | Input (voice traces) |
| aws | aws CLI | Infrastructure management |
| 1password | op CLI | Secrets access |
| markdown-pdf | md-to-pdf | Output (branded PDFs) |

### Workflow Skills (7 total) — Proto-Blueprints
| Skill | Steps | Systems Involved | Blueprint Potential |
|-------|-------|-----------------|---------------------|
| `/morning` | 7 assembly steps + interactive conversation + closing | Hive (all sync adapters), Calendar, Linear, Slack, Email, GitHub | HIGH — already has a playbook, runs daily, structured steps |
| `/call-prep` | 6 data gathering steps + output compilation | Postgres (meetings), Slack, Gmail, Pipeline API | HIGH — structured, repeatable, clear input (company) and output (briefing) |
| `/weekly-summary` | 6 data gathering steps + output compilation | Postgres (meetings), Pipeline API, Slack | HIGH — structured, repeatable, schedulable |
| `/follow-up-check` | 5 check steps + recommendations | Postgres (meetings), Pipeline API, Gmail | HIGH — structured, repeatable, schedulable |
| `/eval-analysis` | 7 analysis steps + optional fix execution | Evaluations API, MongoDB | MEDIUM — structured but requires human judgment on fixes |
| `/dispatch` | Ralph loop: read spec -> execute -> verify -> loop | Agent SDK, Beads, Git, target repos | HIGH — already autonomous, already a loop engine |
| `/project` | CRUD operations + session lifecycle | Filesystem, Beads, Git | LOW — meta-operations, not a workflow |

### System Skills (3 total) — Orchestrators
| Skill | What It Does | Blueprint Role |
|-------|-------------|----------------|
| `/sessions` | Session lifecycle management, briefings | Session management is the execution substrate |
| `/code-dev` | Phase-based code workflow with Hive checkpointing | Already a proto-blueprint with design->review->plan->execute->test->deploy phases |
| `/brainstorm-hive` | Decision checkpointing during brainstorming | A step type within design-phase blueprints |

---

## Angle 4: Workflow Categorization (15+ Recurring Workflows)

### Simple Workflows (1-3 steps, single session, single system)

**1. Quick Capture / Note Creation**
- Steps: User speaks -> LLM tags/classifies -> Hive record created
- Frequency: Multiple times daily
- Systems: Hive
- Automation: Fully autonomous after voice input
- Current implementation: Quick capture tile in UI, `hive create note`

**2. Record Lookup / Context Query**
- Steps: Query Hive -> format results -> present
- Frequency: Multiple times daily
- Systems: Hive
- Automation: Fully autonomous (triggered by question)
- Current implementation: `hive get`, `hive search`, `hive refs`

**3. External System Sync**
- Steps: Pull from external API -> map to Hive records -> update MongoDB
- Frequency: Scheduled (every 30 minutes to daily)
- Systems: Hive sync adapters + external APIs (Linear, Calendar, Gmail, Slack, GitHub)
- Automation: Fully autonomous, schedulable
- Current implementation: `hive sync <system>`, cron scripts exist (`sync_cron.sh`, `sync_cron_install.sh`)

### Medium Workflows (3-7 steps, single session, 2-4 systems)

**4. Morning Consultation**
- Steps: (1) Sync external systems, (2) Gather calendar/workflows/priorities, (3) Present briefing, (4) Interactive priority setting, (5) Update records, (6) Create session summary
- Frequency: Daily (weekday mornings)
- Systems: Hive, Calendar, Linear, Slack, Email, GitHub
- Automation: Hybrid — steps 1-3 autonomous, step 4 interactive, steps 5-6 autonomous after interactive
- Current implementation: `/morning` skill + `playbooks/morning.md`
- Blueprint notes: Steps 1-3 could run at 6:30am autonomously. Craig reviews the briefing at 7am and drives the interactive conversation. Steps 5-6 execute based on conversation.

**5. Call Preparation**
- Steps: (1) Look up company, (2) Pull meeting history, (3) Pull signals/objections, (4) Search Slack, (5) Search email, (6) Check pipeline, (7) Compile briefing
- Frequency: Ad-hoc (before customer calls, several per week)
- Systems: Postgres (meetings DB), Slack, Gmail, Pipeline API, Hive
- Automation: Fully autonomous (given company name)
- Current implementation: `/call-prep` skill
- Blueprint notes: Triggered by calendar event or manual request. Output is a structured briefing document.

**6. Weekly Intelligence Summary**
- Steps: (1) Gather meetings, (2) Gather decisions, (3) Gather action items, (4) Gather signals, (5) Check pipeline, (6) Pull notable quotes, (7) Compile report
- Frequency: Weekly
- Systems: Postgres (meetings DB), Pipeline API, Slack, Hive
- Automation: Fully autonomous, schedulable
- Current implementation: `/weekly-summary` skill + `playbooks/ceo-weekly.md`
- Blueprint notes: Could run every Friday afternoon autonomously. Output is a markdown/PDF report.

**7. Follow-Up Check**
- Steps: (1) Check overdue items, (2) Check upcoming items, (3) Check stale deals, (4) Cross-reference commitments, (5) Verify follow-up emails, (6) Present recommendations
- Frequency: Weekly or ad-hoc
- Systems: Postgres (meetings DB), Pipeline API, Gmail
- Automation: Hybrid — gathering is autonomous, verification/action is interactive
- Current implementation: `/follow-up-check` skill

**8. Evaluation Run and Analysis**
- Steps: (1) Start local services, (2) Trigger evaluation run, (3) Wait for completion, (4) Pull results via API, (5) Classify failures, (6) Present analysis, (7) Optionally apply fixes
- Frequency: Ad-hoc (during evaluation work, could be weekly per agent)
- Systems: Evaluations API, MongoDB, percy-service, bot-service
- Automation: Hybrid — steps 1-5 autonomous, steps 6-7 interactive
- Current implementation: `/eval-analysis` skill
- Blueprint notes: Could be scheduled to run nightly against all active agents, with results ready for review in the morning.

**9. PR Management Cycle**
- Steps: (1) Check PR statuses across repos, (2) Identify blocked/stale PRs, (3) Request reviews or follow up, (4) Monitor CI results, (5) Merge when ready
- Frequency: Daily (part of active dev work)
- Systems: GitHub, Linear, Slack
- Automation: Hybrid — status checking autonomous, merge decisions interactive
- Current implementation: `gh` CLI, no dedicated skill
- Blueprint notes: PR status dashboard could update autonomously. Merge decisions need human.

**10. Report Generation (Customer Analytics)**
- Steps: (1) Query MongoDB for customer data, (2) Run aggregations, (3) Generate report pages, (4) Compile PDF, (5) Share/deliver
- Frequency: Ad-hoc (per customer request)
- Systems: MongoDB, Observatory, markdown-pdf
- Automation: Fully autonomous (given customer ID and date range)
- Current implementation: Observatory report generation, markdown-pdf skill

### Complex Workflows (7+ steps, multiple sessions, 4+ systems)

**11. Content Creation Pipeline**
- Steps: (1) Idea capture/validation, (2) Source material extraction from Hive, (3) Dynamic extraction interview, (4) Draft v1, (5) Review/feedback, (6) Draft v2..vN, (7) Approval, (8) Publish to primary platform, (9) Cross-post to secondary platforms, (10) Social promotion
- Frequency: Weekly (1-2 pieces per week target)
- Systems: Hive, Content system (cs.py), Google Docs, Substack, Medium, LinkedIn, image-gen
- Automation: Hybrid — extraction and drafting can be autonomous, review/approval is interactive, publishing can be autonomous
- Current implementation: Content system repo with cs.py, 24+ skills, Hive integration designed but not wired
- Blueprint notes: This is a multi-session workflow. Each step may be a separate session. Steps 2-4 could be a sub-blueprint. Publishing (steps 8-10) could be a sub-blueprint. The content pipeline design is already well-defined in the Hive design doc.

**12. Feature Development Lifecycle**
- Steps: (1) Design brainstorming (multiple sessions), (2) Design review (5+ independent sessions), (3) Implementation planning, (4) Plan review, (5) Execution (parallel subtasks via dispatch), (6) Code review, (7) Testing/debugging, (8) Deployment
- Frequency: Ongoing (multiple features in flight)
- Systems: Hive (workflow + decisions), Beads (tasks), Git (code), Linear (issues), GitHub (PRs), Dispatch (execution), session-manager
- Automation: Hybrid — design is interactive, execution can be autonomous, review is interactive, deployment can be autonomous
- Current implementation: `/code-dev` skill with phase-based workflow, dispatch engine for execution
- Blueprint notes: This is the most complex workflow. It spans 20+ sessions. Each phase has different automation characteristics. The code-dev skill already defines the phases. Dispatch already handles the execution phase. The Hive already tracks decisions. A blueprint would formalize the phase transitions and automate what's currently manual orchestration.

**13. DevOps Migration (Multi-Service)**
- Steps: (1) Inventory secrets/config per service, (2) Create AWS resources (SM secrets, PS params), (3) Write loader scripts per service, (4) Create PRs, (5) Populate secrets on EC2, (6) Get reviews, (7) Merge in dependency order, (8) Verify each deployment
- Frequency: Ad-hoc (infrastructure migrations)
- Systems: AWS (SM, PS, IAM), GitHub (PRs), EC2, Docker, Linear
- Automation: Hybrid — steps 1-4 can be highly autonomous (with template), steps 5-8 need human oversight for production changes
- Current implementation: Scripts in `scripts/`, manual orchestration across 12 repos
- Blueprint notes: Steps 1-4 could be a repeatable sub-blueprint for each service. The 12-service migration is a fan-out of the same template. The merge-order dependency chain (step 7) is a scheduling problem.

**14. Customer Onboarding / Integration**
- Steps: (1) Research customer system (RingCentral, Applied Epic, etc.), (2) Design integration architecture, (3) Create spec, (4) Implement integration, (5) Test with customer, (6) Deploy
- Frequency: Per new customer (monthly?)
- Systems: Varies per customer — could be any external system + Indemn platform
- Automation: Hybrid — research autonomous, design interactive, implementation autonomous (via dispatch), testing interactive
- Current implementation: Manual, project-based
- Blueprint notes: Step 1 (platform research) could be a reusable sub-blueprint — given a platform name, research APIs, pricing, integration patterns, produce a reference doc.

**15. Fundraising / Application Preparation**
- Steps: (1) Gather company intelligence from Drive/meetings/data, (2) Draft application responses, (3) Review with CEO, (4) Iterate, (5) Submit
- Frequency: Ad-hoc (per application/opportunity)
- Systems: Google Workspace (Drive, Docs), Hive, Stripe (revenue data), MongoDB (usage data)
- Automation: Hybrid — data gathering autonomous, drafting autonomous, review interactive
- Current implementation: Manual, project-based (series-a, nvidia-inception)
- Blueprint notes: Step 1 (company intelligence gathering) is a reusable sub-blueprint. It was done independently for series-a and nvidia-inception and could be formalized.

**16. Session Recovery After Machine Restart**
- Steps: (1) Detect lost tmux sessions, (2) Recreate tmux sessions per project, (3) Exit fresh Claude instances, (4) Find old session IDs from transcript directories, (5) Resume each session
- Frequency: Ad-hoc (after crashes/restarts)
- Systems: tmux, session-manager, Claude Code CLI
- Automation: Fully autonomous
- Current implementation: Documented in `/sessions` skill but entirely manual
- Blueprint notes: This is a perfect candidate for a fully autonomous blueprint. The steps are deterministic, require no judgment, and follow a fixed pattern.

---

## Angle 5: Workflows That CANNOT Be Blueprinted (Limits)

### Fundamentally Interactive Work
- **Design brainstorming** — Craig talks through ideas via Wispr Flow. The value is the back-and-forth exploration, not the execution of predefined steps. A blueprint cannot capture "iterate until the design feels right." However, the infrastructure around brainstorming (create workflow, checkpoint decisions, create session summary) CAN be blueprinted.
- **Customer conversations** — Real-time calls and meetings. Prep and follow-up can be blueprinted; the conversation itself cannot.
- **Code debugging of novel issues** — When the bug is unknown, the exploration path is unpredictable. However, the diagnostic framework (gather logs, reproduce, hypothesize, test) could be a loose blueprint.

### Judgment-Intensive Decisions
- **Scope decisions** — "Should we build this feature or not?" requires business context and human judgment that cannot be automated.
- **Architectural trade-offs** — "Should we use MongoDB or Postgres for this?" requires understanding constraints that may not be fully capturable.
- **Priority setting** — The morning consultation surfaces information, but Craig decides what matters. The blueprint can present; it cannot decide.

### External Human Dependencies
- **Waiting for reviews** (devops: 12 PRs waiting on Dhruv) — A blueprint cannot make someone review a PR. It can monitor status and notify when reviews are done.
- **Waiting for customer responses** (ringcentral: waiting on plan tier confirmation) — External timelines are not controllable.
- **Waiting for credentials** (voice-evaluations: blocked on Langfuse creds) — Access provisioning involves other humans.

### Truly Novel Work
- **First-time research** (audio-transcription: figuring out what MLX models work on Apple Silicon) — When the solution space is unknown, no blueprint applies. However, the research PATTERN (identify options, test each, compare, select) is blueprintable.
- **System architecture from scratch** — The Hive's 8-session design phase was exploratory. But the pattern of "brainstorm -> decide -> document -> iterate" is a blueprint.

### Key Insight: The Boundary is "Interactivity," Not "Complexity"
The limiting factor is not workflow complexity — the feature development lifecycle is extremely complex but largely blueprintable because its phases are well-defined. The limiting factor is whether the next step depends on real-time human judgment or an unpredictable external event. Most complex workflows have both blueprintable and non-blueprintable portions. The art is in defining where the blueprint hands off to the human and picks back up.

---

## Angle 6: New Workflows Enabled by Blueprints

### Currently Impossible, Enabled by Blueprints

**1. Overnight Data Sync and Morning Briefing**
- Today: Craig starts the day by running `/morning` interactively, which triggers sync + context gathering. This takes 5-10 minutes of a session.
- With blueprints: A scheduled blueprint runs at 6am — syncs all external systems, compiles the briefing, writes it as a Hive knowledge record. When Craig opens a session at 7am, the briefing is already a tile on the Wall, ready to review.

**2. Continuous Evaluation Monitoring**
- Today: Someone manually triggers eval runs, waits, then manually analyzes results.
- With blueprints: A scheduled blueprint runs nightly for each production agent — triggers eval, waits for completion, runs `/eval-analysis`, classifies failures, creates a Hive record with the analysis. Craig reviews a tile in the morning that says "O'Connor External: 82% (up from 76%), 2 new agent issues found."

**3. Parallel Design Review**
- Today: Craig manually creates 5 sessions for independent design reviews.
- With blueprints: A fan-out blueprint spawns 5 parallel review sessions, each with a different review prompt (security, performance, maintainability, API design, user experience). Results are collected and synthesized into a single review summary.

**4. Content Pipeline Automation**
- Today: Each content step (extraction, drafting, publishing) requires Craig to manually start a session and invoke the right skills.
- With blueprints: A content blueprint moves a piece through the pipeline — extraction happens automatically from Hive source material, draft is generated and saved for review, review feedback triggers the next draft. Craig only intervenes at the approval step. Publishing to Substack + Medium + LinkedIn happens autonomously after approval.

**5. Multi-Service Deployment**
- Today: Merging 12 PRs across services requires manual sequencing, waiting, and verification.
- With blueprints: A deployment blueprint processes the merge queue — merges PRs in dependency order, waits for CI, verifies each deployment, moves to the next. Craig is notified only if something fails.

**6. Cross-System Impact Analysis**
- Today: When a change is made to a shared service (e.g., bot-service), there's no automated way to check what else is affected.
- With blueprints: A blueprint triggered by a merge to a core repo fans out to check all dependent services — runs their test suites, checks for API compatibility, compiles an impact report.

**7. Customer Health Dashboard Refresh**
- Today: Generating a customer report is manual — query MongoDB, format data, generate PDF.
- With blueprints: A scheduled blueprint runs weekly per customer — queries fresh data, generates updated reports, compares to previous week's metrics, flags significant changes. Reports are tiles on the Wall.

**8. Self-Improving Evaluations**
- Today: When an eval run reveals evaluation problems (false failures), someone manually updates the rubric/test set.
- With blueprints: A blueprint detects evaluation problem patterns across runs, proposes rubric/test set updates, and (with approval) applies them and re-runs to verify improvement.

**9. Proactive Follow-Up Engine**
- Today: `/follow-up-check` runs when Craig asks for it.
- With blueprints: A daily blueprint checks for overdue items, drafts follow-up emails, and queues them for Craig's review. Items that have been overdue for 3+ days get escalated with more urgent messaging.

**10. Autonomous Research Sprints**
- Today: Research (like the audio transcription pipeline or RingCentral platform research) requires Craig to drive each session.
- With blueprints: A research blueprint takes a topic and runs through a structured investigation — web search, API exploration, documentation analysis, comparison matrix generation. Output is a reference artifact in the Hive.

---

## Angle 7: Frequency and Automation Potential Matrix

### Daily Workflows
| Workflow | Current Impl | Automation | Blueprint Value |
|----------|-------------|------------|-----------------|
| Morning consultation | `/morning` skill | Hybrid | HIGH — scheduling the data gathering phase saves 10 min/day |
| Session management | `/sessions` skill | Interactive | LOW — inherently interactive |
| Quick capture | Hive UI | Autonomous (after input) | LOW — already working |
| External system sync | `hive sync` + cron | Autonomous | MEDIUM — already schedulable, blueprint adds observability |
| PR status check | Manual `gh` commands | Autonomous | HIGH — daily dashboard of all PR states across repos |

### Weekly Workflows
| Workflow | Current Impl | Automation | Blueprint Value |
|----------|-------------|------------|-----------------|
| Weekly summary | `/weekly-summary` skill | Autonomous | HIGH — schedule Friday 5pm, CEO gets it Monday |
| Follow-up check | `/follow-up-check` skill | Hybrid | HIGH — autonomous detection + human-driven action |
| Evaluation runs | `/eval-analysis` skill | Hybrid | HIGH — nightly runs, morning review |
| Content pipeline stages | Content system | Hybrid | HIGH — automate extraction/drafting, human reviews |
| Graph health review | `hive health` | Autonomous | MEDIUM — weekly health report |

### Ad-Hoc Workflows
| Workflow | Current Impl | Automation | Blueprint Value |
|----------|-------------|------------|-----------------|
| Call prep | `/call-prep` skill | Autonomous | HIGH — triggered by calendar event |
| Feature lifecycle | `/code-dev` + dispatch | Hybrid | HIGH — formalize phase transitions |
| Customer report | Observatory | Autonomous | MEDIUM — parameterized by customer |
| Platform research | Manual | Autonomous | HIGH — structured investigation pattern |
| Application prep | Manual | Hybrid | MEDIUM — data gathering reusable |
| Service migration | Manual scripts | Hybrid | HIGH — template per service, fan-out |
| Session recovery | Manual (documented) | Autonomous | HIGH — fully deterministic, no judgment |

---

## Angle 8: Systems Involved Per Workflow (Intersection Map)

This shows which systems each workflow touches. Workflows that touch more systems benefit more from blueprints (more orchestration needed).

| Workflow | Hive | Sessions | Git | GitHub | Linear | Slack | Gmail | Calendar | MongoDB | Postgres | AWS | Dispatch | Content | Evaluations |
|----------|------|----------|-----|--------|--------|-------|-------|----------|---------|----------|-----|----------|---------|-------------|
| Morning consultation | X | | | X | X | X | X | X | | | | | | |
| Call prep | X | | | | | X | X | | | X | | | | |
| Weekly summary | X | | | | | X | | | | X | | | | |
| Follow-up check | | | | | | | X | | | X | | | | |
| Eval runs | X | X | | | | | | | X | | | | | X |
| Content pipeline | X | X | X | | | | | | | | | | X | |
| Feature lifecycle | X | X | X | X | X | | | | | | | X | | |
| DevOps migration | | | X | X | X | | | | | | X | | | |
| Customer report | | | | | | | | | X | | | | | |
| PR management | | | X | X | X | X | | | | | | | | |
| External sync | X | | | X | X | X | X | X | | | | | | |
| Report generation | | | | | | | | | X | | | | | |
| Session recovery | | X | | | | | | | | | | | | |
| Research sprint | X | X | | | | | | | | | | | | |

**Key observation:** The morning consultation touches the most systems (7). Feature lifecycle is the most complex (7 systems). Workflows touching 4+ systems have the highest blueprint orchestration value.

---

## Angle 9: What Exists Today vs. What Blueprints Would Formalize

### Already Structured as Steps (Just Need Formalization)
- `/morning` — 7 named assembly steps in the playbook, clear inputs/outputs
- `/call-prep` — 6 named data gathering steps, structured output
- `/weekly-summary` — 6 named data gathering steps, structured output
- `/follow-up-check` — 5 named check steps
- `/eval-analysis` — 7 named analysis steps
- `/code-dev` — 8 named phases with checkpointing patterns
- Content pipeline — Full lifecycle defined in Hive design doc

### Partially Structured (Patterns Exist, Not Formalized)
- DevOps migration — Scripts exist, merge order documented, but no orchestration
- PR management — `gh` commands known, no aggregation workflow
- Evaluation scheduling — Manual trigger, could be automated
- Customer report generation — Manual process, could be templated
- Session recovery — Documented steps, not automated

### Unstructured (Patterns Inferred from Project History)
- Feature brainstorming — Pattern is "iterate until decided" with decision checkpoints
- Research sprints — Pattern is "identify options, test each, compare, select"
- Application preparation — Pattern is "gather intelligence, draft, review, iterate"
- Customer integration design — Pattern is "research platform, design architecture, create spec"

---

## Angle 10: The Gap Between Skills and Blueprints

Skills define **what to do** in a single step. Blueprints define **how steps connect across time and sessions**.

| Gap | Example |
|-----|---------|
| **No scheduling** | `/morning` can run when invoked, but nothing triggers it at 7am |
| **No state between steps** | `/eval-analysis` runs once per invocation; there's no way to say "run this nightly and accumulate results" |
| **No fan-out** | `/code-dev` design review says "5 independent sessions" but there's no way to spawn and collect them |
| **No conditional routing** | If eval score drops below 80%, escalate; otherwise, just log. No way to express this today |
| **No human-in-the-loop gates** | Content draft created -> wait for approval -> then publish. No mechanism for "pause and wait for human" |
| **No cross-session state** | Feature development spans 20 sessions. The workflow entity tracks state, but there's no automation that says "when design review is done, start planning" |
| **No observability** | Dispatch has minimal logging. No way to see "step 3 of 7 running, 4 hours elapsed, $2.30 spent" |
| **No triggers** | Nothing happens in response to events. PR merged -> nothing. Calendar event approaching -> nothing. Email received -> nothing |

These gaps are precisely what the blueprint system would fill.

---

## Summary of Findings

**15+ recurring workflows identified**, ranging from simple (quick capture, 1 step) to complex (feature lifecycle, 8 phases over 20+ sessions).

**Automation potential distribution:**
- 4 workflows fully autonomous (sync, session recovery, report generation, customer reports)
- 8 workflows hybrid (morning consultation, content pipeline, feature lifecycle, eval runs, DevOps, PR management, follow-up checks, application prep)
- 3 workflows fundamentally interactive (brainstorming, customer conversations, scope decisions)

**Highest blueprint value (impact x feasibility):**
1. Morning consultation (daily, 7 systems, data gathering phase fully automatable)
2. Feature development lifecycle (ongoing, most complex, phase transitions need automation)
3. Content creation pipeline (weekly, multi-step, most steps automatable)
4. Evaluation monitoring (could be nightly, currently manual)
5. Weekly intelligence reports (schedulable, currently manual)

**What cannot be blueprinted:** Real-time human judgment, unpredictable external events, truly novel exploration. But even these have blueprintable infrastructure (gathering context before brainstorming, monitoring for external events, structuring research patterns).

**Key architectural observation:** The existing skill system, Hive CLI, session manager, and dispatch engine already provide most of the primitives a blueprint system needs. The gap is orchestration — connecting steps across time, sessions, and systems with state management, scheduling, conditional routing, fan-out, and observability.
