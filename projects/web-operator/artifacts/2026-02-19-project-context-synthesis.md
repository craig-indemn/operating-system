---
ask: "Gain comprehensive understanding of the web-operator project — codebase, customer emails, Slack discussions, team activity, and production decisions"
created: 2026-02-19
workstream: web-operator
session: 2026-02-19-a
sources:
  - type: github
    description: "web_operators repo — CLAUDE.md, HANDOFF.md, framework-architecture.md, git log"
  - type: gmail
    description: "Johnson Insurance + Indemn email thread (6 messages), Epic credentials email, 4 Gemini meeting notes"
  - type: slack
    description: "#customer-implementation channel — full web operator discussion thread, Craig-Kyle DMs"
---

# Web Operator Project — Full Context Synthesis

## What This Is

A reusable web automation framework where an LLM agent (Claude Opus 4.6 via Deep Agents/LangGraph) operates a browser via Agent Browser CLI to complete tasks. It follows structured "path documents" (markdown playbooks) and improves over successive runs.

**First customer**: Johnson Insurance (largest Everett Cash Mutual agency)
**Contract**: $10,000/year, signed Feb 4, 2026
**Primary contact**: MaeLena Apperson (Operations Coordinator, maelena@gojohnsonins.com)
**Account lead**: Kyle Geoghan

## The Problem

Johnson's VA spends significant time manually processing ECM policy documents into Applied Epic. They have RPA (Coventus) that pulls docs from ECM and attaches them in Epic every Monday night. The bottleneck is the last mile — manual data entry/verification from the documents into Applied Epic. No API access (Applied Epic API-SDK is a separate paid add-on they don't have), so it's full web operator automation.

## Scope — Three Phases

### Phase 1: Endorsements (CHG) — ACTIVE
The account manager makes policy changes before submitting the endorsement. The operator's job is:
1. Confirm the changes in Epic match the endorsement request document
2. Update the premium to match the revised document
3. Add a note to the activity (worked / something wrong)
4. Close the activity if successful, reassign to Cheryl if not

**Key insight from Feb 16 call**: "We don't even have to edit docs. Just confirm whether or not they WERE edited correctly."

**Materials received from MaeLena (Feb 17)**:
- ECM CAP CHG endorsement guide (1.4MB docx) — standard vehicle trade walkthrough
- Reference CHG under Dry Ridge Farm, LLC in Epic Demo — correct submission example
- CHG under Bill Kistler with intentional errors — wrong effective date, wrong VIN, vehicle not removed, line not updated (for testing error detection)

### Phase 2: Renewals (POL3)
Full renewal processing — FOP (Farmowners) and CAP (Commercial Auto). POL3 activities now added to sandbox (as of Feb 17). Framework paths already built (v1 for both FOP and CAP), but need revalidation with actual POL3 data.

### Phase 3: Billing/Invoices — DEFERRED
Carrier invoice processing. Pushed back by MaeLena: "Let's pause on that and keep our focus on one project at a time."

## Production Operations Model

- **Volumes**: 20-50 endorsements batched Monday nights via RPA
- **Schedule**: Trigger Tuesday noon, fallback run Wednesday morning
- **Notifications**: None needed — add notes to activities, use Epic's built-in reporting for weekly summary
- **Auth**: Same login as sandbox (Enterprise ID: JOHNS87, Usercode: INDEMNAI), no MFA
- **Password resets**: Every ~3 months (end of April estimate), need to design handler
- **Session constraint**: Applied Epic only supports one active session per account — parallel runs would force-logout

## Architecture

### Framework Modules
| Module | Role |
|--------|------|
| `agent.py` | Assembles Deep Agent with tools, skills, middleware |
| `middleware.py` | Observation masking, state injection via working_memory.md, progress-aware stall detection |
| `path_parser.py` | Parses structured markdown paths into dataclasses |
| `executor.py` | Streams LangGraph events, captures trajectory |
| `runner.py` | Creates run dirs, writes trajectory.jsonl + outcome.json |
| `comparison.py` | Cross-run evaluation and batch config |
| `resume.py` | Resume-from-step support |
| `tools.py` | Shell subprocess wrapper + visual PDF reader |

### Tech Stack
- Agent brain: `deepagents` (LangChain Deep Agents)
- LLM: `langchain-anthropic` (Claude Opus 4.6)
- State: `langgraph-checkpoint-sqlite`
- Browser: `agent-browser` (npm CLI, snapshot+refs)
- PDF: `poppler` (pdftoppm)
- Package mgr: `uv`

### Production Architecture Decisions (Craig + Dhruv aligned)
1. **MongoDB as source of truth**, filesystem for execution — pull configs at session start into unique session workspace, clean up after
2. **Sequential execution first** — one active run at a time (Epic session limitation)
3. **Standalone instance** for web operators (not co-located with production services)
4. **Deployment**: EventBridge scheduling -> Lambda triggers -> SQS for concurrency
5. **Agent Browser sessions** for future concurrency when workflows allow it
6. **Dhruv's session management plan**: [Notion doc](https://www.notion.so/indemn/Web-Operator-Session-Management-Johnson-Insurance-3096834b8cbe800bab0bfe5828534c5e)

## Cost Analysis

| Stage | Cost/Run | Notes |
|-------|----------|-------|
| Early prototype (Rudra) | ~$13-18 | 1000 steps, uncontrolled runs |
| Current (Feb 18) | ~$3 | Context reuse, stall detection, guardrails |
| Target (open source) | ~$0.10 | Once path is well-established |
| Monthly estimate | ~$40 | 400 runs/month at $0.10 |

**Craig's cost strategy**: Refine paths using Claude Code subscription (free Opus), run execution on cheaper models. Open source models fine-tuned for browser use often match frontier performance.

## Team

| Person | Role | Focus |
|--------|------|-------|
| Kyle Geoghan | Account lead | Customer relationship, strategy |
| George Remmer (Rem) | PM | Customer comms, call coordination, status tracking |
| Rudra Thakar | Tech lead | Running the agent, path refinement, cost optimization |
| Dhruv Rajkotia | Architecture | Productionalization, session management, CI/CD |
| Craig Certo | Framework design | Middleware, harness, path structure, model benchmarking |

## Development Timeline

| Date | Milestone |
|------|-----------|
| Feb 4 | Contract signed, kickoff email |
| Feb 5 | MaeLena sends Epic credentials + 27 activities |
| Feb 9-10 | Initial sync calls, API research (no API access confirmed) |
| Feb 11 | Craig shares proposal doc, team alignment |
| Feb 12 | Framework scaffolding, first smoke tests, PDF reader |
| Feb 13 | Phases 1-4 complete (173 tests), Rudra starts CAP flow |
| Feb 15 | Craig pushes middleware optimizations |
| Feb 16 | First full CAP run (199 steps), stall detection rewrite, call with Johnson |
| Feb 17 | Path restructured (10→8 steps, per-activity pipeline), MaeLena sends endorsement guide + POL3 activities |
| Feb 18 | Rudra: cost down to $3/run, working on endorsement verification workflow |

## Current State (as of Feb 19)

### What's working
- Framework is solid: 173 tests, Phases 1-4 complete
- Progress-aware stall detection with Haiku alignment checks
- Per-activity pipeline loop (ensures PDF and policy come from same account)
- Cost reduced from ~$18 to ~$3/run
- Real-time cost breakdown logging
- Full run isolation

### What Rudra is actively building
- Cross-check PDFs against associated notes
- Cross-check PDFs against policy details (partially done)
- Auto-create note activity once verification is complete

### Key discoveries from live runs
- Applied Epic's `File → Exit` is the only reliable way to return to Home (SPA hash routing doesn't work)
- Epic uses custom ASI web components that sometimes hide inputs from accessibility tree
- `dispatchEvent(new MouseEvent('contextmenu', ...))` doesn't work in Angular — need real mouse commands
- "Show Only Important Policy Documents" link replaces broken search filter for attachments

### Open items
- Re-run CAP path with per-activity pipeline (path restructured but not fully validated)
- FOP path hasn't been re-run with new middleware
- Browser cleanup (`agent-browser close`) needs to go in executor's `finally` block
- Phase 5 (deployment: MongoDB, EC2, concurrent sessions) not started
- Endorsement verification workflow in progress
- Remote branch `indemn/feat-web-operator-improvement` exists with additional work

### Repo structure
- GitHub: `indemn-ai/web-operators`
- Local: `/Users/home/Repositories/web_operators`
- Two remotes: `origin` (Craig's fork) and `indemn` (org repo)
- Active branch: `main` + `indemn/feat-web-operator-improvement`
