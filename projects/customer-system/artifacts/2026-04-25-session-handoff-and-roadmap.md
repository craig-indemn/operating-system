---
ask: "Encapsulate the Apr 24 2026 session — what we built, what we found, what Kyle reacted to, what's next — so the next session can pick up cleanly without re-reading the full artifact set. Includes the agreed roadmap shape."
created: 2026-04-25
workstream: customer-system
session: 2026-04-24-roadmap (continued)
---

# Session Handoff & Roadmap — End of 2026-04-24

The session that traced one meeting end-to-end through the OS, surfaced the structural gaps, shipped a Kyle-facing demo that he validated, and ended with an agreed roadmap.

This handoff is the single starting point for the next session. Read this; jump into the linked artifacts only when you need detail.

---

## What we set out to do

Take the Apr 22 GR Little first-discovery call through the entity system end-to-end. Find what's broken from first principles. Produce a draft follow-up email for Kyle to compare against what he'd have sent. Land on a refined understanding of how the customer-system pieces fit together.

## What happened (in order)

1. **Designed the Playbook entity.** Kyle's PLAYBOOK-v2 doc was explicitly NOT used as a seed (treated as aspirational signal, not spec). Built our own shape: stage, description, entry_signals, required_entities, expected_next_moves, artifact_intent. One record per Stage. Terminus = Proposal at PROPOSAL stage.
2. **Replaced the stale Playbook entity definition.** Discovered Bug #29 in the process — entity-def replacement doesn't evict old API routes; required an `indemn-api` redeploy (with explicit user permission).
3. **Hydrated GR Little graph manually.** Picked canonical Company from 5 dupes. Consolidated Walker Ross + created Heather Contact. Created GRLITTLE-2026 Deal at discovery. Linked the meeting to the Company. Created Touchpoint manually (Synth was suspended; no re-trigger mechanism for historical meetings — Bug #10). Triggered the Intelligence Extractor — **it failed structurally** (no path from Touchpoint to source Meeting transcript). Did extraction by hand. Created 3 Opportunities + empty Proposal v1 per the design refinement. Drafted the follow-up email.
4. **Built the visual one-pager (v2).** Email hero + temporal timeline + extraction quote→entity→email-line table + mechanism table (stage-by-stage) + Proposal spine growth. Showed it to Kyle.
5. **Kyle reacted positively.** "Maybe a little too long. Pretty close to what it should be. Worth doing on every call. Everything's a v0. Whole company's excited about the Indemn operating system."
6. **Aligned on roadmap.** Craig's data-engineer framing: hydrate → connect processes → resolve bugs → iterate to acceleration.

## Concrete entity state — GR Little (live in dev OS, `_platform` org)

| Entity | Count | Notable IDs |
|---|---|---|
| Company | 1 canonical, 4 dupes flagged | canonical: `69eb95f22b0a508618923977` (G.R. Little Agency, grlittle.com) |
| Contact | 2 used + 1 dup Walker | Walker: `69ea9e56ff375a32fa25a34c` · Heather: `69ebb6f72b0a508618923c02` |
| Deal | 1 | `69ebb7222b0a508618923c06` (GRLITTLE-2026, stage: discovery, warmth: Warm) |
| Meeting | 1 | `69eb94a92b0a50861892382a` (Apr 22, 31min, 34509-char transcript) |
| Touchpoint | 1 | `69ebbec5472952352cdfda4f` (status: processed) |
| Tasks / Decisions / Commitments / Signals | 2 / 2 / 4 / 5 | All linked to company + source_meeting + touchpoint |
| Opportunity | 3 | After-hours phone (→Front Desk), Billing inquiry (→Service), Outbound renewal (→Renewal) |
| Proposal | 1 | `69ebcd39472952352cdfddb1` (v1, drafting, no Phases yet) |
| Playbook | 1 | `69ebbe2f472952352cdfda2b` (DISCOVERY stage, fully populated artifact_intent) |

## Artifacts produced this session (priority order for re-reading)

| Artifact | Why it matters |
|---|---|
| `2026-04-24-information-flow-v2.html` | The Kyle-facing demo. Open this first to remember the shape. |
| `2026-04-24-kyle-sync-recap.md` | What Kyle said, what he wants next, action items. |
| `2026-04-24-design-dialogue-playbook-artifact-proposal.md` | Architectural refinements aligned but not yet implemented. |
| `2026-04-24-extractor-pipeline-gap.md` | Why the Extractor failed and three fix options. **Option B is the chosen path.** |
| `2026-04-24-extractor-procedure-and-requirements.md` | Step-by-step procedure for autonomous Extractor + 9 OS capability gaps. |
| `2026-04-24-playbook-entity-vision.md` | Playbook's role: terminus is Proposal, consulted twice per touchpoint. |
| `2026-04-24-trace-plan-and-design-notes.md` | Plan + open question on reliable Company/Contact identity. |
| `2026-04-24-grlittle-followup-email-draft.md` | The drafted email + how each line traces to entities. |
| `2026-04-24-os-bugs-and-shakeout.md` (Bug #29 added) | Running OS bug list. 29 bugs total, 4 fixed. |
| `context/2026-04-24-kyle-craig-sync-transcript.txt` | Full meeting transcript (1344 lines). |

## Architectural decisions aligned (not yet implemented)

1. **Playbook is consulted twice per touchpoint** — by the Extractor (`required_entities` → extraction schema) and by the Artifact Generator (`artifact_intent` → render spec).
2. **Proposal is created at DISCOVERY as an empty spine.** Hydrated by every subsequent touchpoint. At PROPOSAL stage the Artifact Generator just renders it. Same mechanism every stage; only the Playbook record changes.
3. **Opportunities created from DISCOVERY onward** for pain points that map to an AssociateType. Pain without product fit stays as Signal (or future Problem entity).
4. **Touchpoint Synthesizer must populate forward source pointers** on Touchpoint. Option B from extractor-pipeline-gap.
5. **Raw Meeting/Email content remains available to associates** as ground truth via CLI. Don't formalize as a separate pattern — it's already there. Touchpoint summary + entities are curation; raw content provides voice / texture / personal references.

## Open design questions

- **Opportunity vs Problem** — does unmapped-pain need its own entity, or does Opportunity loosen `mapped_associate` to nullable?
- **Document-as-artifact** — drafted email's home in the entity graph. Document entity already designed for Proposal→Document; needs full resolution for emails.
- **Stages — 12 with sub-stages, multi-select for archetypes** (Kyle ask). Open design.
- **Origin / referrer tracking** (Pat Klene → GR Little) — field on Deal or new Introduction entity?
- **Phase 1 ordering** — cleanup duplicates BEFORE entity-resolution capability (one-off script) or AFTER (dogfoods the capability)? **Lean: after.**
- **Phase 3 scope** — does per-customer page + per-meeting trace page belong in Phase 3, or split out as 3.5? **Lean: in Phase 3, time-box.**

## Bug status (priority order)

| # | Title | Severity | Status |
|---|---|---|---|
| 1 | Meet adapter rejects date-only `since` | High | 🟢 Fixed (`8afda9d`) |
| 14 | CLI POST/PUT timeout 60s | Med | 🟢 Fixed (`f0dfe89`) |
| 23 | `bulk-delete` silently drops MongoDB operator filters | **Critical** | 🔴 Open |
| 29 | Entity-def replacement doesn't evict old API routes | **High** | 🔴 Open |
| 16 | Associates auto-create Companies | **High** | 🔴 Open (root: entity-resolution missing) |
| 17 | No meeting-to-company classifier | **High** | 🔴 Open (subsumed by #16's fix) |
| 22 | Service token untraceability | **High** | 🔴 Open |
| 9 | Associates pass dicts not ObjectIds | High | 🔴 Open |
| 10 | No backfill / re-trigger for historical entities | Med | 🔴 Open |
| 18 | Synth doesn't update `Meeting.touchpoint` back-reference | Med | 🔴 Open |
| (others 2-8, 11-13, 15, 19-21, 24-28) | Various | Low/Med | 🔴 Open |

Full detail in `2026-04-24-os-bugs-and-shakeout.md`.

---

## ROADMAP — Agreed direction

### Spine (sequential)

#### Phase 1 — Hydration foundation
*Goal: data flows in continuously, no orphan entities, no dupes.*

- Recurring email fetch (scheduled associate; all team members)
- Meeting backfill — 30-day window, full team
- **Entity-resolution capability** (kernel) — given (domain, name, email), return likely existing matches; associates call before creating. Root fix for Bug #16.
- Duplicate cleanup using the resolution capability above

**P1 done test:** drop the system for a week; new meetings/emails appear in the graph correctly hydrated.

#### Phase 2 — Pipeline reliability
*Goal: drop a new meeting in, entities populate themselves correctly without intervention.*

- Bug #29 fix (route eviction in `kernel/api/registration.py` before include)
- **Option B** — Touchpoint `source_entity_type` + `source_entity_id`; Synth populates; Extractor reads
- Bug #9 (dicts vs ObjectIds) — skill prompt + entity-skill enhancement
- Cross-invocation tool-cache leak — scope `/large_tool_results/` per message_id
- Silent workflow stuck-state — workflow detects empty agent output, marks failed
- Synth + Extractor running cleanly on Phase 1 backfill, end-to-end, zero intervention

**P2 done test:** drop a new meeting in; Touchpoint appears and entities extracted correctly without touching anything.

#### Phase 3 — Productionize the artifact path
*Goal: every meeting produces a draft artifact for human review + one-click send.*

- **Playbook-informs-extraction** refinement: Extractor reads `Playbook[Deal.stage].required_entities` as schema
- **Artifact Generator associate** — watches `Touchpoint → processed`, reads (Deal + Touchpoint + entities + Playbook + raw source), produces stage-appropriate artifact (email at DISCOVERY/DEMO, Proposal doc at PROPOSAL, etc.)
- Per-customer page (v2 diagram but live, every customer, all touchpoints)
- Per-meeting trace page (on-demand "how did this meeting flow")
- Trim email length (Kyle's feedback) — refine DISCOVERY Playbook `artifact_intent`
- Default-include meeting recording link (Apollo/Drive "anyone can view")

**P3 done test:** Kyle gets a draft email in his inbox after each meeting; reviews and sends with minor edits.

#### Phase 4 — Adoption surface + persistent loops
*Goal: sales team uses it; AI takes over routine notification work.*

- **V0 sales dashboard** — list view, real pipeline data. Columns: customer value / success path / days to next step / next step / owner. Push-to-talk to update.
- **Stage refinement** — 12 sub-stages per Kyle, multi-select for archetypes, qualification built in
- **Origin tracking** — referrer/source on Deal or new Introduction entity (open design)
- **Commitment-driven persistent-AI loop** — Commitment created (indemn-side) → notify assignee → track to fulfilled
- **Stale-detection associate** — finds Deals/Commitments past due_date, surfaces to owner

**P4 done test:** Cam opens dashboard, sees customers, updates fields, gets Slack notifications when Commitments hit.

### Parallel (any time)

- **Observatory reporting** — fix Jonathan's broken table + scheduled daily/weekly usage reports to Kyle
- **Documentation** — operational learnings captured continuously

### The acceleration mechanic

Each phase done makes the next 2-3x faster. P1 done = no manual data setup. P2 done = associates self-serve. P3 done = artifact generation is a product feature. P4 done = sales team adoption. By the end of P4, a new customer onboards via the same flow GR Little did, but autonomously — and the OS is the platform we wanted.

---

## Things to remember next session

- **Auth** — see `2026-04-23-pipeline-operations-guide.md`. `INDEMN_API_URL` + `INDEMN_SERVICE_TOKEN` + `INDEMN_CLI_TIMEOUT=600`.
- **Mongo direct** — `mongosh "mongodb+srv://dev-indemn:wJnKmz4P0q39GpXZ@dev-indemn.mifra5.mongodb.net/indemn_os"`. Note: `companys` + `opportunitys` collections (Bug #15).
- **Production safety** — read-only on shared services unless explicitly authorized. Today required permission to redeploy `indemn-api` for Bug #29 workaround.
- **Pipeline associates state**: Email Classifier (suspended), Touchpoint Synthesizer (suspended), Intelligence Extractor (active). Review before Phase 1/2 work; may need to stay suspended until reliability fixes land.
- **GR Little Company duplicates** (4 of them) flagged but not deleted — Bug #23 blocks bulk-delete with operator filters. Cleanup is part of Phase 1.
- **Apr 24 sync** — Kyle stopped proactively sending Cloud-Code-AI data dumps. Craig asks when needed.
- **Kai status** — Craig does not manage; Kai goes through Kyle. Project-proposal framework in `2026-04-24-kyle-sync-recap.md`.
- **Two memory entries added today**: `project_customer_system_entity_identity.md` + `project_customer_system_artifact_entity_pattern.md` — both are "open question, revisit" notes.
- **Bugs that fixing immediately would unblock the most**: #29 (eviction), #16 (auto-create Companies / entity-resolution), Option B fix (Touchpoint source pointers). Together these get the autonomous pipeline to a usable state.

## Action items from the Kyle sync (Craig's commitments)

1. Send Cloud Code plugin (token usage tracker) to Kyle
2. Send GR Little email + traced journey artifacts to Kyle for written feedback
3. Check Apollo API for "anyone can view" link on recording
4. Build V0 sales pipeline dashboard / list view (Phase 4 work, top priority for Kyle)
5. Fix observatory broken reporting table (Jonathan's bug)
6. Schedule daily/weekly observatory usage report to Kyle
7. Tell Kai: all manager proposals go through Kyle; collaboration on project basis OK
8. Document operational learnings as we iterate

These items split across phases — #1, #2, #7 are immediate / one-off; #4 is Phase 4; #5 + #6 are the parallel observatory track; #3 is part of Phase 3 polish; #8 is ongoing.
