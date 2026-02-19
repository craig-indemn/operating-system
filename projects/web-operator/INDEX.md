# Web Operator

Development workstream for the web-operator service. Uses operating system skills (Slack, meetings, pipeline, etc.) to pull context and data that informs implementation decisions in the web-operator repo. The code lives in its own repository; this project tracks context, decisions, and artifacts that bridge OS intelligence into that development work.

## Status
Session 2026-02-19-a complete. Full context hydration done — codebase, Gmail, Slack, meeting notes synthesized. Endorsement path built and validated. Demo environment inventoried.

**What was accomplished this session:**
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
1. Shake out the endorsement path manually with Claude Code + agent-browser (P0)
2. Refine path based on findings (P0, blocked by #1)
3. Run through harness with Haiku 4.5 — evaluate speed/cost (P0, blocked by #2)
4. Monday demo dry run (P0, blocked by #3)
5. Investigate missing Dry Ridge Farm / Bill Kistler test cases (P1)
6. Benchmark additional models if Haiku insufficient (P1, blocked by #3)

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

## Open Questions
- How to handle Epic password resets (every ~3 months, next expected end of April)?
- What happened to Dry Ridge Farm and Bill Kistler activities? (Rudra may have consumed them)
- What does the `indemn/feat-web-operator-improvement` branch contain?
- Is the Feb 18 code on `indemn/main` (2 commits ahead of `origin/main`) ready to merge?
- Are there POL3 activities in the sandbox? (Not visible in default activity view — may need filter change)
