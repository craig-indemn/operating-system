# Silent Sports

Re-engagement of Silent Sports (McKay Insurance) with a Crawl/Walk/Run proposal framework. Certificate generation is the primary hook — net new capability for Indemn that becomes reusable across customers. Kyle's internal review doc (March 15, 2026) lays out the framework and assigns questions to Cam (pricing), Craig/Ryan (technical feasibility of doc gen), George (rate engine), and Rocky (relationship/re-engagement).

## Status
**Mint implementation COMPLETE and DEMO-READY.** All 9 tasks across 4 waves executed. 5-agent parallel review completed with all critical/medium issues resolved. Repo shared with team. Repo: [craig-indemn/silent-sports-doc-gen](https://github.com/craig-indemn/silent-sports-doc-gen)

Demo tested end-to-end in browser:
- Press N → submission appears in inbox with SSE real-time updates
- Click Open Review → extracted fields with confidence indicators
- Click Approve & Generate → both PDFs generate (ACORD 25 ~325KB, Premium Disclosure ~15KB)
- Auto-approve mode works — submissions flow through without human review
- `npm run dev:all` starts all 3 services

**Done this session (2026-03-17):**
- Executed full implementation plan (Waves 0-3)
- 5-agent code review against design spec — fixed ACORD 25 field mapping, React 18/19 conflict, SSE data completeness, state machine transitions
- Posted update to Kyle in #customer-implementation thread with both generated PDFs attached
- Shared repo link — Dhruv can review

**Next:** Schedule demo with Kyle. Address open questions (Meg's rate spreadsheet, cert numbering, pricing model). Product showcase.

### The Framework
| Phase | Name | Price | Months | Key Deliverables |
|-------|------|-------|--------|-----------------|
| CRAWL | Submissions + First Document | $1,500/mo | 1-3 | Submission processing, Accord 25 cert gen, email notifications, data export |
| WALK | Customer Access | $3,000/mo | 4-6 | Customer-facing quoting, conversational app, Program Builder, web chat |
| RUN | Revenue Engine | $5,000/mo | 7-12 | Voice agent, renewal automation, lightweight AMS alternative, broker portal |

### Document Types (CRAWL scope)
1. **Accord 25 Certificate** — Industry standard, medium complexity, ~2-3 days (Month 1)
2. **Member Certificate** — Custom Silent Sports template, medium-high complexity, ~3-5 days (Month 3)
3. **Premium Disclosure** — Custom page, low-medium complexity, ~2-3 days (Month 2)
4. **Endorsement Documents** — TBD, lowest priority, scope after first 3

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Mint Repo | GitHub | [craig-indemn/silent-sports-doc-gen](https://github.com/craig-indemn/silent-sports-doc-gen) |
| Internal Team Review Doc | Google Doc | [Silent Sports — Internal Team Review](https://docs.google.com/document/d/1LTZ1Lw3lO_8wPWWAEMR_fJ3HvKKql0OXv-NUJYTh6pg/edit) |
| Jan 28 Call Notes | Google Doc | [Jan 28 Call Notes](https://docs.google.com/document/d/1hVD34xr-EZLwsdyxfXgI622RuEn_4TDkO10pkenPhQE/edit) |
| Dec 2025 Proposal | Google Doc | [Original Proposal](https://docs.google.com/document/d/1mv4yk5SzS0LL80k2TjrFKmiMxUt1ziEIfCNd7UuiH7w/edit) |
| Silent Sports Drive Folder | Google Drive | [Drive Folder](https://drive.google.com/drive/folders/1tCtM4NGghc2xq9p31Y4FxDSyxhNG0KhT) |
| Visual Roadmap (V3) | Web | [indemn-pipeline.vercel.app/share/silent-sports](https://indemn-pipeline.vercel.app/share/silent-sports) |
| Kyle's Slack Message | Slack | #customer-implementation, ts=1773677360.280319 |
| Pipeline Profile | Repo | indemn-pipeline/customers/silent-sports/PROFILE.md |
| Pitch Brief | Repo | indemn-pipeline/docs/SILENT-SPORTS-PITCH-BRIEF.md |
| Four Outcomes Map | Repo | indemn-context/product/FOUR-OUTCOMES-PRODUCT-MAP.md |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-03-16 | [kyle-proposal-framework](artifacts/2026-03-16-kyle-proposal-framework.md) | What is Kyle's Silent Sports re-engagement proposal and what questions does Craig need to answer? |
| 2026-03-16 | [mint-design-spec](artifacts/2026-03-16-mint-design-spec.md) | Design the document generation MVP — architecture, components, demo flow, UI |
| 2026-03-16 | [mint-implementation-plan](artifacts/2026-03-16-mint-implementation-plan.md) | Comprehensive implementation plan for parallel Claude Code execution |

## Decisions
- 2026-03-17: Demo tested in browser, all integration issues resolved (React version conflict, SSE partial data, state machine transitions, PDF HTTP serving)
- 2026-03-17: Posted update to Kyle in #customer-implementation with generated PDF attachments
- 2026-03-17: 5-agent parallel review — fixed ACORD 25 field-map (fill_48/49/50 were in wrong rows), generation status on total failure, agent extracting step
- 2026-03-16: Mint implementation complete — 4 waves, 9 tasks, 3 parallel agent dispatches per wave
- 2026-03-16: Integration fix — auto-populate `date` field in ACORD 25 generation (subs/generate.ts)
- 2026-03-16: Named the doc gen engine **Mint** ("mint a certificate")
- 2026-03-16: MVP demo scope is Accord 25 + Premium Disclosure (not all 3 docs)
- 2026-03-16: Hybrid PDF approach — pdf-lib for standard forms (Accord 25), React-PDF for custom docs (Premium Disclosure)
- 2026-03-16: Fully standalone — separate repo, no dependencies on existing Indemn services
- 2026-03-16: CLI-first — deep agent uses `mint` and `subs` CLIs, not HTTP APIs directly
- 2026-03-16: Two-layer CLI — `mint` (reusable PDF gen) + `subs` (submissions workflow). Agent uses both.
- 2026-03-16: Communication via shared submissions REST API + SSE (not WebSocket)
- 2026-03-16: SQLite for submissions state persistence (single file, zero setup)
- 2026-03-16: ACORD 25 AcroForm confirmed working with pdf-lib (96 fields, proof of concept done)
- 2026-03-16: Settings collapsed into inbox header (auto-approve toggle, not a separate screen)
- 2026-03-16: Skills-driven agent — document knowledge in Skills, not hardcoded in agent
- 2026-03-16: Review UI with shadcn/ui — approachable but premium feel
- 2026-03-16: Demo shows both human-in-the-loop and full-auto modes
- 2026-03-16: Repo starts under `craig-indemn`, migrates to `indemn-ai` when ready

## Open Questions
- Need Meg's rating spreadsheet to implement real rate calculations (mocked for demo)
- Pricing: Setup fee per doc type (Option A) vs bundle into monthly (Option B)? (Cam's question)
- Confirm cert numbering scheme with Scott/Meg (auto-increment in SQLite for now)
- Relationship temperature — is Scott still warm? (Rocky's question)
- Surplus lines tax rate for Montana (mocked at 3% for demo, need to confirm)
