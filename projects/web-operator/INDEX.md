# Web Operator

Development workstream for the web-operator service. Uses operating system skills (Slack, meetings, pipeline, etc.) to pull context and data that informs implementation decisions in the web-operator repo. The code lives in its own repository; this project tracks context, decisions, and artifacts that bridge OS intelligence into that development work.

## Status
Session 2026-02-26-a complete. Local model testing + hosted API research + Gemini 2.5 Flash integration.

**What was accomplished this session (2026-02-26-a):**
1. Analyzed Rudra's `feat-web-operator-improvement` branch (5 commits, ~11,600 lines — API layer, framework, scripts, Docker, testing)
2. Tested local models for tool calling: Qwen3 14B works mechanically but FAILS on real Epic workflows (hallucinates, skips steps). 30B-A3B OOM on 24GB RAM. **Conclusion: local 14B models not powerful enough.**
3. Researched hosted open-source APIs: Together AI, Fireworks, DeepInfra, DeepSeek, Google Gemini. Compared pricing against Claude Sonnet ($3/$15).
4. Integrated **Gemini 2.5 Flash** ($0.15/$0.60 — 95% cheaper than Sonnet) into the framework. Tool calling works, correct tool calls made, ~2s/turn (vs 28-33s local).
5. Hit login script bug — `epic_login` can't find credential form on IDP popup tab. Not a model issue.

**Next up:**
1. Debug the login script — `agent-browser tab switch` to IDP popup isn't reading the right tab content (P0)
2. Complete a full Gemini run once login works (P0, blocked by #1)
3. Compare Gemini vs Haiku quality on real workflow (P1, blocked by #2)
4. Share recommendations with Rudra (P1, blocked by #3)

**Previous session (2026-02-19-b):**
1. Committed and pushed all session-a work (both repos)
2. Walked through endorsement path Steps 1-5 with agent-browser against Fergerson activity
3. Confirmed Steps 1-4 work (login, collect activities, open activity/notes, download/read PDF)
4. Found agent-browser `!` escaping bug — password entry needs eval workaround
5. Found critical Step 5 blocker — 2024-2025 BAUT policy period missing from Policies sidebar
6. Documented all findings in shakeout artifact

**Previous session (2026-02-19-a):**
1. Created web-operator project in the OS with full INDEX.md
2. Read CLAUDE.md, HANDOFF.md, framework-architecture.md — deep codebase understanding
3. Pulled all emails (Johnson thread, meeting notes) and Slack (#customer-implementation full thread)
4. Synthesized endorsement workflow from MaeLena's guide (docx extracted, 9 annotated screenshots reviewed)
5. Downloaded ECM CAP CHG guide.docx to web_operators/docs/
6. Built `paths/ecm_cap_endorsement/` — path_v1.md (8 steps, 3 procedures), context.md, guardrails.md
7. Validated path parses correctly with existing path_parser.py
8. Logged into Applied Epic, inventoried all 18 activities — 4 BAUT available
9. Defined testing strategy: test on expendable activities, save 2 for Monday demo

**Next up (run `bd ready` in this project dir):**
1. Resolve Step 5 blocker — investigate why 2024-2025 BAUT policy is missing from Policies sidebar (P0)
2. Apply path refinements from shakeout (password eval, Step 5 nav) (P0, blocked by #1)
3. Complete shakeout of Steps 5-8 once policy navigation is resolved (P0, blocked by #2)
4. Run through harness with Haiku 4.5 — evaluate speed/cost (P0, blocked by #3)
5. Monday demo dry run (P0, blocked by #4)
6. Investigate missing Dry Ridge Farm / Bill Kistler test cases (P1)
7. Benchmark additional models if Haiku insufficient (P1, blocked by #4)

## External Resources
| Resource | Type | Link |
|----------|------|------|
| web_operators repo | Local repo | /Users/home/Repositories/web_operators |
| GitHub repo | GitHub | github.com/indemn-ai/web-operators |
| Internal project plan | Google Doc | https://docs.google.com/document/d/1pi6WhS0nKBHqHhPTwOtG1LbXutk_pu70XjWow-NPyZc |
| External brief | Google Doc | https://docs.google.com/document/d/1rnYeLqwFesuHx307GnQhzNEkxIt4vdpy1ki7zd7ZGaM |
| Shared folder (customer) | SharePoint | https://johnsonins.sharepoint.com/:f:/g/shares/IgDT9Bz-zucATqAcRxIeYBRPARoH5BqwMrpHl2Vi30sbo0o |
| Shared folder (internal) | Google Drive | https://drive.google.com/drive/folders/1ODqXHpkjOLNo3_vj18bYwgh16J92g8Ru |
| Session management plan | Notion | https://www.notion.so/indemn/Web-Operator-Session-Management-Johnson-Insurance-3096834b8cbe800bab0bfe5828534c5e |
| Feb 16 call transcript | Google Doc | https://docs.google.com/document/d/1CmiVciKDA27WpOubLfqfhcgl5Jqya8aQs8jUv-qIbU0 |
| ECM CAP CHG guide | Local file | /Users/home/Repositories/web_operators/docs/ECM CAP CHG guide.docx |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-02-19 | [project-context-synthesis](artifacts/2026-02-19-project-context-synthesis.md) | Full context synthesis — codebase, emails, Slack, meeting notes, production decisions |
| 2026-02-19 | [endorsement-workflow-analysis](artifacts/2026-02-19-endorsement-workflow-analysis.md) | Endorsement verification workflow, team activity, demo prep requirements, critical gap (no endorsement path) |
| 2026-02-19 | [endorsement-path-creation](artifacts/2026-02-19-endorsement-path-creation.md) | Built endorsement path (8 steps, 3 procedures), design decisions, demo environment risk, testing approach |
| 2026-02-19 | [activity-inventory](artifacts/2026-02-19-activity-inventory.md) | Logged into Epic, inventoried all 18 activities — 4 BAUT available, testing strategy defined |
| 2026-02-19 | [endorsement-path-shakeout](artifacts/2026-02-19-endorsement-path-shakeout.md) | Steps 1-5 walkthrough — Steps 1-4 work, Step 5 blocked (missing policy period), password bug found |
| 2026-02-26 | [rudra-feat-branch-analysis](artifacts/2026-02-26-rudra-feat-branch-analysis.md) | Comprehensive analysis of Rudra's feat-web-operator-improvement branch — API layer, middleware, scripts, Docker, testing |
| 2026-02-26 | [local-model-tool-calling-test](artifacts/2026-02-26-local-model-tool-calling-test.md) | Local model research + testing — Qwen3 14B and 30B-A3B work with Ollama + LangChain tool calling, ready to wire into Rudra's framework |

## Decisions
- 2026-02-10: No API access for Applied Epic — full web operator approach required (Kyle confirmed)
- 2026-02-13: CLI-first browser tool (Agent Browser) with browser-use as fallback
- 2026-02-16: Endorsement scope refined — operator confirms changes, doesn't make them. "Just confirm whether they WERE edited correctly."
- 2026-02-16: Production schedule — trigger Tuesday noon, fallback Wednesday morning (20-50 endorsements/batch)
- 2026-02-16: No alerts/notifications needed — use Epic's built-in reporting + activity notes
- 2026-02-16: Sequential execution only for Epic (one session per account)
- 2026-02-16: MongoDB + filesystem hybrid for session management (Dhruv + Craig aligned)
- 2026-02-17: MaeLena deferred billing/invoices — focus on endorsements and renewals first
- 2026-02-19: Endorsement path built as separate path (not retrofitted into renewal path) — simpler, verification-focused
- 2026-02-19: Test on expendable activities (#1 Fergerson, #2 Echerd), save #0 Thanh Tran and #3 Wong/Huang for demo
- 2026-02-19: Sheryll Bausin (not "Cheryl") is the reassignment target for failed endorsements
- 2026-02-19: agent-browser escapes `!` in fill/type — must use eval with native input setter for passwords with special characters
- 2026-02-19: Heredoc syntax required for complex eval expressions through bash (`cat <<'JSEOF'`)
- 2026-02-26: Local 8B models (Llama3.1, Qwen3) too small for tool calling. 14B works mechanically but fails on complex multi-step workflows. Not viable for production.
- 2026-02-26: Gemini 2.5 Flash chosen for hosted testing — multimodal, $0.15/$0.60, excellent tool calling, `langchain-google-genai` already installed
- 2026-02-26: `agent.py` patched to make `thinking` param Anthropic-only (was breaking non-Anthropic models)

## Open Questions
- How to handle Epic password resets (every ~3 months, next expected end of April)?
- What happened to Dry Ridge Farm and Bill Kistler activities? (Rudra may have consumed them)
- ~~What does the `indemn/feat-web-operator-improvement` branch contain?~~ → Answered in artifact `rudra-feat-branch-analysis`
- Why does `agent-browser tab switch 1` on the IDP popup tab return the main tab's page content? Is the IDP form in an iframe?
- Is Gemini 2.5 Flash quality sufficient for the full Epic workflow? (Need to complete a run to find out)
- Should we use Haiku ($1/$5, zero code changes) instead of Gemini ($0.15/$0.60, needs patches)?
- Is the Feb 18 code on `indemn/main` (2 commits ahead of `origin/main`) ready to merge?
- Are there POL3 activities in the sandbox? (Not visible in default activity view — may need filter change)
- Why is the 2024-2025 BAUT policy period (CAP500961) missing from the Fergerson account's Policies sidebar? Only 2021-2022 and 2022-2023 periods visible under any filter. The endorsement activity and PDF reference this period. Is this a demo environment data gap, or is there a different navigation path?
- Does the Thanh Tran activity (#0, updated 2/18/2026) have the policy period visible? Might be a better test candidate.
