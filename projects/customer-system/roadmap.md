# Customer System — Roadmap

> Living source of truth for **how we get from where we are now to the vision**. Updated every session that moves the work forward. Read with `vision.md` (what we're building, why, and the lens) and `os-learnings.md` (running register of OS bugs + capability gaps + design questions).
>
> Last updated: **2026-04-29** (Session 12 close — Bugs #35/#36/#37 closed, Hard Rule #1 inverted, Armadillo traced end-to-end as designed, shared-context hydration redesign shipped).

---

## Where we are now (2026-04-29)

**Phase A complete. Phase B1 substantially de-risked. Foundation is closer to running autonomously than at any prior point.**

- **27 entity definitions live** in dev OS, `_platform` org. Includes Playbook entity with both DISCOVERY and PROPOSAL stage records seeded.
- **Pipeline associates state:**
  - Email Classifier — *suspended* (kill switch held; v9 in DB ready, content_hash `9eef4959ae701614`). Hard Rule #1 inverted (resolve-before-create > never-auto-create). Verified live on Armadillo's first-contact email — autonomous Company + Contact creation worked.
  - Touchpoint Synthesizer — *suspended* (unchanged). Has not been triggered autonomously since Session 9.
  - Intelligence Extractor — *active*. Silent-stuck-state regression that previously caught it is fixed (Session 10 commit `d914d76`). Ran on Armadillo extracting 14 entities against the DISCOVERY Playbook.
- **Hydrated customers / prospects:**
  - **GR Little** hydrated end-to-end. Kyle validated Apr 24.
  - **Alliance** hydrated end-to-end (60+ entities). v2 proposal rendered, PDF in Cam's Drive folder, trace-showcase HTML shared with Cam + Kyle.
  - **Armadillo Insurance** hydrated end-to-end as designed (Apr 29) — first new-prospect trace post-Hard-Rule-#1-inversion. 1 Company + 1 Deal + 2 Contacts (Matan Slagter CEO, David Wellner COO) + 2 Touchpoints + 14 extracted entities.
- **~930+ emails ingested** across 11 team members. ~67+ meetings ingested. Queue drained.
- **OS bugs:** load-bearing kernel work substantially done. Bug #35 (deepagents skill discovery — was THE blocker), Bug #36 (Gmail/Calendar `fetch_new` adapter `**params` absorption), Bug #37 (Email list endpoint malformed-doc tolerance) all closed this session. Plus burst #4 fixes from Apr 27-28 (Bug #23/#24 bulk-delete operators, Bug #10 reprocess primitive, Bug #9 boundary coercion, Bug #29 route eviction, Bug #30 partialFilterExpression auto-emit, --include-related reverse refs, always-fresh entity-skill rendering, several CLI papercut fixes). The kernel is in genuinely solid shape now.
- **5 new design gaps logged this session** — Deal-lifecycle automation gap (no Deal-creator associate yet, Touchpoint↔Deal chicken-and-egg, Proposal-at-DISCOVERY auto-create not wired), Employee `entity_resolve` not activated, Company hydration is bare on auto-create, Contact richer-field parsing from email signatures, internal docs spanning multiple prospects.
- **Cleanup pending:** 500 unrelated Emails + 6 unrelated Meetings on Kyle's mailbox from Bug #36 side-effect (sit at status `received`, EC suspended so untouched). 2 malformed Email rows from Bug #37 data side (`69ea548e…6e92` Oneleet, `69ea556f…7387` Linear Orbit).
- **Open design questions (long-running, none resolved this session):** Opportunity vs Problem entity; Document-as-artifact pattern for emails; 12 sub-stages with archetype multi-select (Kyle's Apr 24 ask); origin/referrer tracking; Playbook hydration mechanism. See `os-learnings.md` for full list.

For deeper context on the journey here: `CLAUDE.md § 5 Journey`, `INDEX.md § Status`, `SESSIONS.md`.

---

## Tangible deliverables (TD-1 through TD-11)

The roadmap is organized around tangible deliverables, not foundation phases. Each TD is a concrete piece the team can use OR a foundational capability that unlocks the next concrete piece. They run mostly sequentially — the early ones are foundation, the later ones are team-facing.

Each TD entry below is **structural only** — title, what-it-delivers, done-test, dependencies, open questions to resolve before/during execution. The deep architectural detail (which associate, what trigger, what data flow, etc.) gets resolved in a focused alignment conversation BEFORE the TD is executed, and the resolved detail then gets written into the TD section. This way fidelity grows as we work through, rather than being written speculatively at high resolution.

**The trace-as-build-method principle threads through every TD.** Pick a real scenario. Run it manually first via the CLI. Verify entity state ends up correct. Then write the skill / wire the watch / build the UI / activate the autonomous version. The artifact is the writeup of what worked.

**The dogfooding principle threads through every TD.** If we can't use the OS to deliver a TD, we fix the OS until we can.

---

### TD-1 — Adapters running cleanly + historical hydration

**Delivers:** Email + Meeting + Slack + Drive data flowing in continuously to dev OS, with manual entry paths for missed/unrecorded interactions. Foundation for everything downstream. **No cascade activation yet.**

**Sub-pieces:**
- Email recurring fetch (Gmail) — scheduled associate, all 11 team mailboxes, configurable cadence
- Meeting recurring fetch (Google Meet) — same pattern + 30-day backfill of historical meetings
- Slack adapter — built (channels + DMs + MPDMs)
- Slack hydration — historical Slack content backfilled (which channels/DMs are customer-relevant; threads-as-Touchpoints; file-attachments-as-Documents)
- Drive ingestion — Cam's proposal folder, shared Kyle/Cam folder, customer-specific folders. Standalone Documents linked to Companies.
- Manual interaction entry — UI form + voice/talk-to-add (push-to-talk for quick updates)
- Outlook adapter `**params` propagation (Bug #36 follow-on)

**Done-test:** Drop a new email/meeting/Slack thread anywhere in scope; the corresponding entity appears in dev OS within the configured cadence. EC/TS/IE remain suspended — entities sit at status `received` / `logged` waiting for cascade activation.

**Dependencies:** Bug #36 cleanup (500 unrelated emails + 6 meetings) before recurring fetch turns on. Bug #37 row cleanup. Slack OAuth integration setup.

**Open questions to resolve:**
- Recurring-fetch cadence per source (15 min? hourly? per-source different?)
- Slack scope — which channels/DMs/MPDMs are in (vs. all-of-Slack)? Who decides?
- Slack thread-vs-message granularity — operate at thread level for Touchpoints? File attachments as Documents?
- Drive folder identification — explicit list, or auto-discovered?
- Manual entry UI shape — form fields, voice transcription path
- Internal Slack discussions about a customer — how do they tie back to the customer entity at ingestion time (vs. on cascade)?

---

### TD-2 — Cascade activated progressively

**Delivers:** A 7-associate cascade running autonomously on incoming Email/Meeting/Slack data. Every interaction flows through it, every entity emerges from it, the Proposal entity continuously hydrates as a side-effect. The spine of the customer system.

#### What the cascade does

When an Email, Meeting, or Slack thread arrives in dev OS (via TD-1 adapters), it cascades through:

```
Source entity created (Email | Meeting | Slack thread)
  → [EC | MC | SC]                        Source classifier (one fires per source type)
    → Source classified (Company + Contacts linked)
      → TS                                 Source-agnostic Touchpoint creator (folds Deal-creation)
        → Touchpoint logged (+ Deal + empty Proposal if needed, atomic)
          → IE                              Source-agnostic intelligence extractor
            → Touchpoint processed
              → Proposal-Hydrator           Aggregates extracted entities into the Proposal
              → Company-Enricher            (parallel, separate trigger — fills bare Companies)
```

By the time the cascade finishes for a single Email/Meeting/Slack thread, the customer constellation has gained: a Touchpoint with Option B source pointers; potentially a new Contact (with signature-parsed fields); potentially a new Company (Hard-Rule-#1 inverted: resolve-before-create, autonomous create on 0/0); potentially a new Deal at CONTACT or DISCOVERY (with empty Proposal attached); extracted intelligence (Decisions, Tasks, Commitments, Signals, Operations, Opportunities, Phases linked to the Touchpoint and the Deal); the Proposal entity updated with new entity references; the Company auto-enriched with any new structured info from the source.

#### The 7 associates — why each exists

Per the principle established in this design conversation: **a new associate is justified only when the trigger, entities used, context, or skill are significantly different from existing associates.** One associate can have multiple skills; one trigger should be one associate; decouple things separate in nature.

| Associate | Trigger | Writes | Why separate |
|---|---|---|---|
| **EmailClassifier (EC)** — exists, v9 | `Email created` | Email.company, Email.sender_contact, Email.status | Email-specific relevance filter (spam/newsletter/real); Hard-Rule-#1-inverted resolve-before-create logic; signature parsing for richer Contact fields. **Will absorb signature parsing.** |
| **MeetingClassifier (MC)** — new | `Meeting created` | Meeting.company, Meeting.attendees_contacts, Meeting.attendees_employees, Meeting.scope, Meeting.status | Meeting data shape is fundamentally different (structured attendee list from Google Meet API; transcript; usually pre-classified as relevant); reasoning is "resolve attendees + identify customer Company from external attendees" not "filter spam". |
| **SlackClassifier (SC)** — new | `SlackThread created` | SlackThread.company, SlackThread.participants_contacts, SlackThread.participants_employees, SlackThread.scope, SlackThread.status | Slack context (channel name, DM/MPDM membership) is different from email/meeting; relevance filtering is needed (much off-topic noise); thread-vs-message granularity is different. |
| **TouchpointSynthesizer (TS)** — exists, v6 (will gain Deal-creation) | `Email/Meeting/SlackThread classified` (3 watches) | Touchpoint (created), Email/Meeting/SlackThread.touchpoint, Deal (created if external + no active Deal), Proposal (created empty if Deal created), ReviewItem (if multi-Deal ambiguity for internal scope) | Source-agnostic — one Touchpoint shape regardless of source type. Folds Deal-creation atomically because Deal exists in our model purely as the carrier for a Proposal — they co-evolve. Same trigger as Touchpoint creation, same context (the source + Company + Contact). |
| **IntelligenceExtractor (IE)** — exists, v3 | `Touchpoint logged` | Decision, Task, Commitment, Signal, Operation, Opportunity, Phase (all created and linked to Touchpoint + Deal), Touchpoint.status (transitions to processed) | Source-agnostic — reads source content via Option B navigation, extracts structured intelligence. Different from Classifiers (those classify a single source; IE creates many entities) and from TS (TS doesn't read source content). |
| **Proposal-Hydrator (PH)** — new | `Touchpoint processed` | Proposal (updated — new entity references added), Proposal.status (potentially advanced), ReviewItem (if extracted entity doesn't fit cleanly) | Aggregates extracted entities INTO the Proposal entity. Different context from IE (IE reads source content; PH reads aggregated entity graph + Playbook). Different reasoning (IE extracts from text; PH consolidates from entities). Different writes (IE creates many entities; PH updates one Proposal entity by adding references). |
| **Company-Enricher (CE)** — new | `Touchpoint logged` for a Company with bare data (or scheduled cron) | Company (updated — fields filled from source content) | Different from IE (IE writes intelligence entities; CE updates Company directly). Different concern (intelligence-extraction vs Company-profile-completion). Triggers in parallel with IE — no conflict because they write to different entities. |

**Why not fewer than 7?** Folding more responsibilities into existing associates would: (a) conflate triggers that aren't actually the same trigger; (b) create context bloat per LLM call (IE would need to know about Proposals AND Companies AND extraction); (c) make failure modes harder to debug (one associate failing affects multiple concerns); (d) violate the "one trigger per associate" principle.

**Why not more than 7?** Splitting further would: (a) over-fragment work that shares context (e.g., splitting "extract Decisions" from "extract Tasks" into separate associates would duplicate source-reading); (b) increase cascade coordination complexity for no decoupling gain; (c) stretch the cascade depth (we'd be at 6-8 levels deep, and while the kernel circuit breaker is at 10, depth has practical observability cost).

The 7 associates correspond to 7 fundamentally different (trigger, entities, context, reasoning) tuples. That's the right number.

#### ReviewItem — universal escape valve for human review

Per the design decision in this conversation: **any associate that encounters any issue while working creates a `ReviewItem` and continues. It never blocks. It never throws. It creates a ReviewItem, makes its best-effort write, and moves on.**

This is a foundational pattern, not a narrow one. Use cases include but are not limited to:
- EC: ambiguous Company match (multiple at score 1.0)
- EC: 0 candidates AND signature-parse can't determine company affiliation
- MC: meeting attendees include unfamiliar emails that don't clearly resolve to any Contact/Employee
- SC: thread relevance unclear; mentioned customers ambiguous
- TS: multi-Deal ambiguity for internal Touchpoint (assigns to latest Deal + creates ReviewItem)
- TS: scope determination unclear (could be external OR internal)
- IE: source content references entities that don't exist (e.g., "the BT Core integration" — no CustomerSystem entity for it yet)
- IE: extracted Decision conflicts with prior recorded Decision
- Proposal-Hydrator: extracted Operation doesn't fit any existing Phase, and Playbook doesn't suggest one
- Company-Enricher: source mentions critical fields that need confirmation (e.g., "they're at $35M ARR" — should this update Company.annual_revenue?)

**ReviewItem entity structure:**
- `target_entity_type: str` — what entity needs review (Touchpoint, Email, Company, etc.)
- `target_entity_id: ObjectId` — which one
- `created_by_associate: str` — which associate flagged it (for triage + improvement signal)
- `reason: str` — why it needs review (free-text or enum like `ambiguous_match`, `multi_deal_internal`, `unfamiliar_reference`, etc.)
- `context: dict` — the data the associate had when it encountered the issue (e.g., the candidate IDs, the source quote)
- `proposed_resolution: str` (optional) — what the associate did as best-effort, so reviewer can accept/override
- `status: "open" | "in_review" | "resolved" | "dismissed"`
- `resolved_by_actor_id: ObjectId` (when reviewed)
- `resolution: str` (what the reviewer did)

**Reviewer role** — has watches on `ReviewItem created`. Anyone in this role gets messages. Reviewer can claim, look at the linked entity, fix anything wrong (e.g., reassign a Touchpoint to a different Deal), and transition the ReviewItem to `resolved` or `dismissed`.

**Why this is THE pattern:**
1. Associates never block — the cascade always completes its best effort
2. Visibility — every uncertain decision is surfaced, not buried in a `needs_review` state on the underlying entity
3. **Reviewing IS training data** — the corrections reviewers make become signal for the next iteration of the associate's skill or rules. Over time, patterns reviewers correct get codified into deterministic rules (the `--auto` flywheel from `rules-and-auto.md`)
4. Generic — works across all entity types and all associates without polluting individual schemas with `flag_for_review` fields

**Source-classifier exception:** EC, MC, SC are slightly different. If they cannot classify at all (0 Company candidates with no signal, sender domain unknown, attendee list all-external-but-unidentifiable), the source entity transitions to `needs_review` (terminal in the cascade — TS won't fire) and a ReviewItem is created. The cascade halts at that source until the reviewer resolves it. This is the one place we accept blocking, because proceeding without classification would create wrong downstream entities.

For all other associates (TS, IE, Proposal-Hydrator, Company-Enricher): best-effort + ReviewItem + continue. No blocking.

#### Proposal-Hydrator nuance: stages are fluid

Per the design conversation, the Proposal-Hydrator's logic is NOT "use Playbook[Deal.stage].required_entities as a hard schema and only add entities matching the schema." That's too rigid because conversations are fluid — a DISCOVERY-stage email might surface PROPOSAL-stage information; a NEGOTIATION-stage call might contain DEMO-stage questions.

Instead, Proposal-Hydrator's logic:
1. Read entities IE just extracted on this Touchpoint
2. For each extracted entity, determine if it fits the Proposal structure:
   - Operation extracted? Link to Proposal.operations
   - Opportunity extracted with a mapped AssociateType? Link to Proposal.opportunities
   - Phase extracted? Link to Proposal.phases
   - Decision/Commitment/Task/Signal? Already linked to Touchpoint and Deal — Proposal references Deal so they're transitively visible; no explicit Proposal-link needed
3. Read `Playbook[Deal.stage].required_entities` as guidance, NOT schema:
   - If the extraction added entities that the current stage didn't expect, that's interesting (might suggest the Deal should advance to next stage, or the Playbook needs refinement) — flag via ReviewItem
   - If the current stage's required_entities aren't yet populated, don't error — just leave them empty (constellation UI will show them as gaps signaling next-actions)
4. Update `Proposal.status` if appropriate (e.g., all DISCOVERY required_entities now populated → Deal can advance to DEMO; this is a signal, not an automatic transition — Deal stage transitions are human-initiated for now)

The Proposal entity is mostly references to other entities, not free-text — per principle #3 (no fluff fields). Proposal-Hydrator does not write narrative descriptions; the narrative emerges from the linked entities.

#### Sub-pieces (work to do)

1. **ReviewItem entity definition + Reviewer role** (pre-flight infrastructure for everything below)
2. **MC (MeetingClassifier) skill + role + watch + actor** — including manual trace on a real meeting (e.g., the Apr 28 Armadillo discovery call)
3. **SC (SlackClassifier) skill + role + watch + actor** — depends on TD-1 Slack adapter complete
4. **EC update** — fold signature parsing into the Contact-creation step; add ReviewItem creation on ambiguity (replacing the current "transition to needs_review and stop" pattern for non-source-classification ambiguity); ensure compatibility with v9's Hard-Rule-#1 inversion
5. **TS update** — fold Deal-creation logic; auto-create empty Proposal when creating Deal; handle internal-scope multi-Deal ambiguity via ReviewItem
6. **IE verification** — already active, but verify it works through the full cascade with TS-created Touchpoints + Option B source pointers; trace manually on Armadillo
7. **Proposal-Hydrator skill + role + watch + actor** — including manual trace on Armadillo's processed Touchpoints
8. **Company-Enricher skill + role + watch + actor** — including manual trace on Armadillo's bare Company
9. **Activation, in bottom-up order** — see below

#### Activation order: bottom-up

Per the trace-as-build-method principle and Craig's "be careful not to have a cascade happen when we're not ready" guidance, activate from the bottom of the cascade upward. Each level proves before the next is built. This way the foundation is verified at each step, and we avoid the dirty-cascade-on-unverified-data scenario.

**Pre-flight (must complete before any activation):**
- Bug #36 cleanup: 500 unrelated Emails + 6 unrelated Meetings — either delete or transition to `irrelevant`
- Bug #37 row cleanup: 2 malformed Email rows
- ReviewItem entity definition created in dev OS
- Reviewer role created with watches on `ReviewItem created`

**Activation sequence:**

1. **EC** — already at v9, verified live on Armadillo. Fold in signature parsing (skill update). Fold in ReviewItem creation for non-source-classification ambiguity. Drain a small batch of test emails. Confirm the new behavior. Then activate recurring (TD-1's recurring fetch can turn on after this).
2. **MC** — trace manually on the Apr 28 Armadillo discovery meeting. Verify attendee resolution, Company identification, scope classification. Write skill. Wire watch + role. Drain a small batch of Meetings. Activate.
3. **SC** — depends on TD-1 Slack adapter complete. Trace manually on a real Slack thread (e.g., the Apr 7-8 Retention Associate prep thread for Alliance). Verify channel-context-aware classification. Write skill. Wire. Drain. Activate.
4. **TS** — currently at v6, suspended. Fold in Deal-creation + empty Proposal creation + internal-scope multi-Deal ambiguity → ReviewItem. Trace manually on a classified Email/Meeting/SlackThread → produced Touchpoint + Deal + Proposal. Update skill (v7). Drain a small batch. Activate.
5. **IE** — currently active. Verify it works through the full cascade with TS-created Touchpoints + Option B source pointers + the fact that Deal/Proposal now exist. Trace manually on Armadillo's Touchpoints (already extracted, but re-verify). Optionally update skill if the Proposal-existence changes its work. Continue active.
6. **Proposal-Hydrator** — trace manually on Armadillo's processed Touchpoints. Confirm extracted entities link correctly to Proposal. Confirm fluid-stage handling (entities extracted that the current stage didn't expect → ReviewItem). Write skill. Wire watch + role. Drain. Activate.
7. **Company-Enricher** — trace manually on Armadillo's bare Company. Confirm enrichment logic. Decide trigger (event vs cron — default to event-triggered on `Touchpoint logged` for a bare Company). Write skill. Wire. Drain. Activate.

After all 7 are active, run the done-test (below).

#### Done-test: systematic historical replay

Rather than waiting for one new prospect's first email, we systematically replay the historical data through the cascade as if it's happening in real time:

1. We have ~930 emails + ~67 meetings already in dev OS (un-cascaded or partially-cascaded). Plus future Slack hydration from TD-1.
2. Reset relevant entities to `received`/`logged` state where needed.
3. Use the kernel `reprocess` primitive (Bug #10 closeout, commit `662dc2d`) to emit the watch-trigger for each Email/Meeting/SlackThread, in chronological order.
4. Observe the cascade fire end-to-end on each one. Watch LangSmith traces. Verify:
   - Source classification is correct (Company + Contacts/Employees linked)
   - Touchpoint created with proper scope + source pointers
   - Deal + Proposal auto-created when appropriate
   - Intelligence extracted (Decisions/Tasks/Commitments/Signals/Operations/Opportunities/Phases)
   - Proposal updated with entity references
   - Company enriched
   - ReviewItems created where the cascade hit ambiguity
5. Spot-check the resulting constellation for ~3 customers (Alliance, Armadillo, GR Little, plus any new ones that emerged in the historical replay) — does the picture match what we know about each?

**Done when:** historical replay completes cleanly across the full dataset, the constellation for each known customer looks correct, the ReviewItem queue is reasonable (mostly genuine edge cases, not systemic failures).

This gives us 1000+ data points of cascade verification, surfaces edge cases the design didn't anticipate, hydrates the constellation for many customers naturally as a side-effect, and produces concrete material for the TD-3 UI to render.

#### Dependencies

- **TD-1 complete** — adapters running, data available in dev OS, Bug #36 + #37 cleanup done.
- **ReviewItem entity + Reviewer role** — pre-flight infrastructure. Created before any associate activation.
- **Hard Rule #1 inversion** — already done in EC v9 (Session 12).
- **LangSmith tracing** — already wired (Session 10).
- **Reprocess primitive** — already shipped (Bug #10 closeout, commit `662dc2d`).
- **Sources need to be fully ingested** — Email + Meeting + Slack adapters from TD-1, plus Drive ingestion for documents that get linked to Touchpoints.

#### Out of scope for TD-2

- **Artifact Generator** — TD-5. The cascade ends with the Proposal entity hydrated; producing draft artifacts (follow-up emails, recaps, proposal decks) is downstream.
- **UI** — TD-3. The cascade populates the entity graph; visualizing it for the team is downstream.
- **Manual entity creation paths** — TD-1 (UI form + voice/talk-to-add). The cascade handles autonomous ingestion; manual paths bypass Classifier+TS but still trigger IE.
- **External-customer multi-tenancy** — TD-11. The cascade is built for Indemn-the-company in the `_platform` org.

---

### TD-3 — Customer constellation queryable + per-customer UI

**Delivers:** A custom UI layer that visualizes the constellation around any Company. The team can open a customer page and see the full picture in seconds. Replaces "ask Kyle" for understanding any customer.

**Sub-pieces:**
- UI layer over OS API (custom React/Astro/etc. — not auto-generated entity views; possibly an adapter pattern where the UI hooks natively into the OS)
- Per-customer page: timeline of all Touchpoints (chronological, expandable), entity sub-sections (Contacts, Operations, Opportunities, Documents, Decisions, Commitments, Signals, Phases, Proposal), constellation summary
- Visual language matches the GR Little / Alliance trace-showcase HTMLs Kyle and Cam validated
- Internal + external Touchpoints interleaved on the timeline
- Linked Documents accessible per Touchpoint and per Company
- Proposal-fill state visible — populated vs. empty fields signal next-actions
- AI assistant surfaced in the UI (using OS base-UI assistant pattern — every human actor has a default assistant pre-provisioned)
- Authentication / org-scoping via existing OS auth

**Done-test:** Any team member opens the UI, picks any customer, gets the full constellation in seconds. Can interact via the AI assistant ("what's the status with Alliance?"). The page looks like the trace-showcase HTMLs. Internal interactions visible alongside external.

**Dependencies:** TD-2 must be running (data flowing into entities for the UI to visualize). At least 3-5 customers hydrated for the UI to be meaningful in dev.

**Open questions to resolve:**
- UI tech stack — React + Vite (matches OS UI)? Astro? Something else?
- Hosted where — Railway alongside OS UI? Separate domain? `customer.os.indemn.ai`?
- API access pattern — direct OS API hits? Adapter pattern (a "customer-system UI adapter" in `kernel/integration/adapters/`)?
- AI assistant in the UI — reuses OS chat-deepagents harness? Or a new dedicated harness for customer-system queries?
- Page-level vs. component-level architecture — single-page-app with routing, or per-customer Astro pages?
- Real-time updates when new Touchpoints arrive — WebSocket subscription? Polling?
- Mobile responsiveness — scope decision

---

### TD-4 — Playbook stages defined from history

**Delivers:** Six grounded Playbook records (one per Stage: CONTACT, DISCOVERY, DEMO, PROPOSAL, NEGOTIATION, VERBAL/SIGNED), each defining `entry_signals`, `required_entities`, `expected_next_moves`, `artifact_intent` from observed historical patterns. Resolves the long-running open design questions.

**Sub-pieces:**
- Mine hydrated data across customers per stage — what does each stage actually look like?
- Refine DISCOVERY (GR Little + Armadillo) and PROPOSAL (Alliance) Playbooks based on Kyle/Cam feedback
- Define CONTACT, DEMO, NEGOTIATION, VERBAL/SIGNED Playbook records from historical examples
- Resolve open design questions:
  - Opportunity vs. Problem entity
  - Document-as-artifact pattern for emails
  - 12 sub-stages with archetype multi-select (Kyle's Apr 24 ask)
  - Origin/referrer tracking (Pat Klene → GR Little, Matan → David → Armadillo)
  - Playbook hydration mechanism — manual vs. scheduled associate vs. human-in-the-loop
- Internal docs spanning multiple prospects — how they attach in the entity graph (Kyle's Apr 8 Warranty Prep covering Amynta + Fair + Armadillo)

**Done-test:** Six Playbook records exist, each grounded in observed historical patterns from at least 2-3 customers. The Artifact Generator (TD-5) can produce stage-appropriate artifacts for any stage by consulting the right Playbook record.

**Dependencies:** TD-1, TD-2, TD-3 — need hydrated data + visibility before we can mine patterns.

**Open questions to resolve:**
- How is each Playbook's `required_entities` defined? From the entity model + observed pattern intersection?
- 12 sub-stages — does this become a `parent_stage` field on Stage, or a separate `qualification_state` field on Deal, or sub-stage records?
- Playbook hydration mechanism — once defined, does the Playbook refine automatically as more data accrues, or is each version a manual update?

---

### TD-5 — Per-interaction artifact generation

**Delivers:** Every Touchpoint that completes processing produces a stage-appropriate draft artifact — follow-up email at DISCOVERY, recap at DEMO, objection response at NEGOTIATION, kickoff at SIGNED, etc. Drafts surface to the OS queue for human review with one-click send.

**Sub-pieces:**
- Artifact Generator associate built (the role Claude played in GR Little + Alliance traces)
- Watches Touchpoint→processed → produces draft when fully extracted
- Reads `Playbook[Deal.stage].artifact_intent` for the spec
- Reads `(Deal + recent Touchpoints + extracted intelligence + Playbook + raw source content)` for materials
- Drafts surface to OS queue for human review
- One-click send via existing Email integration (Gmail) and Slack integration
- Document-as-artifact pattern resolved — drafted email entity location (Email with status=drafting? Document with mime_type=rfc822? Hybrid?)
- Push-to-talk integration for sales rep voice updates of fields (Kyle's Apr 24 ask)

**Done-test:** A new meeting happens → within minutes a draft artifact appears in the OS queue for the appropriate human → review and one-click send.

**Dependencies:** TD-4 (Playbook records define what to render).

**Open questions to resolve:**
- Artifact Generator skill structure — same pattern as EC/TS/IE? Different harness (it produces drafts, doesn't transition data)?
- One-click send mechanism — direct Gmail integration, or queued for human approval first?
- Drafted email storage — Email entity with status=drafting? Document with rfc822 mime? Hybrid? (Open Q from Apr 24.)

---

### TD-6 — Proposal deck generation autonomous

**Delivers:** At PROPOSAL stage, the proposal deck renders automatically from the live entity graph — Operations, Opportunities, Phases, AssociateTypes, all pulled from the constellation. Cam reviews + sends with edits. Replaces Cam's manual proposal authoring.

**Sub-pieces:**
- Artifact Generator handles PROPOSAL stage (special case of TD-5 mechanism)
- Pulls from live entity graph (not Claude-in-conversation)
- Uses existing `templates/proposal/` rendering pipeline (Handlebars + CSS + puppeteer-core)
- Cam validates v3 of Alliance generated autonomously, OR first proposal of TFG / Arches
- Proposal state machine `superseded` transition added (open from Sessions 6-9)
- Drive ingestion of historical proposals (Cam's portfolio context, already in TD-1)

**Done-test:** A Deal transitions to PROPOSAL stage → Artifact Generator produces a styled PDF rendered from the live entity graph → uploaded to Cam's Drive folder → Cam reviews and sends with edits, or pushes back with feedback that informs the next iteration.

**Dependencies:** TD-1 (Drive ingestion), TD-4 (PROPOSAL Playbook), TD-5 (Artifact Generator wired).

**Open questions to resolve:**
- Trigger — is it automatic on stage transition, or human-initiated (Cam clicks "generate v3")?
- v1 → v2 → v3 versioning — auto-supersede prior versions? Keep all versions queryable?
- Drive upload — automatic on render? Or human-approved?
- Proposal state machine — add `superseded` transition path

---

### TD-7 — System visibility (sales pipeline + per-meeting view + flow diagram)

**Delivers:** Team-facing dashboards that surface what the OS is doing. The pieces Kyle has been asking for since Apr 24.

**Sub-pieces:**
- **Sales pipeline list view (Kyle's V0 ask)** — flat table of all customers/prospects with columns: customer value, success path, days to next step, next step, owner. Hydrated with real pipeline data.
- **Per-meeting view** (vision §2 thread A) — every meeting Indemn has, customer + internal, autogenerated and live. Entity trace + extracted intel + draft artifact + suggested next steps.
- **Flow diagram of actors + data flow** — what's running, on what, why. Real-time visibility into the cascade.
- **Push-to-talk for sales reps** to update fields via voice (Kyle's Apr 24 ask, originally folded in TD-5; surfaces here as the use-case integration)
- **Drafts review surface** — the OS queue for the current human, with all draft artifacts ready to review

**Done-test:** Cam opens the dashboard daily, sees customers needing proposals, reviews drafts inline, sends with edits. George prep is 5 minutes not 20. Kyle sees the live state of every prospect and feels confident he can step away.

**Dependencies:** TD-3 (UI infrastructure), TD-5 (drafts exist to review), TD-6 (proposals to review).

**Open questions to resolve:**
- Are these separate pages or unified into one team dashboard?
- How are stale Deals / missed Commitments surfaced? Watches → notification, or visible-by-default?
- Push-to-talk wiring — voice harness extension or new harness?

---

### TD-8 — Team adoption (daily mode of work)

**Delivers:** The team uses the OS as their daily mode of work. Behavior change is real but low-ceremony.

**Sub-pieces:**
- Per-role onboarding flow: Cam (proposals + customer prep), George (meeting prep), Ganesha (delivery tracking), Peter (technical handoffs), Kyle (everything but lighter)
- Operational learnings captured continuously (per Kyle's Apr 24 ask)
- Light ceremony — no formal training program. "Here's how you check on a customer" / "how to respond to a draft" / "how to log an interaction."
- Daily-driver practices (e.g., morning queue review, end-of-day commitments check)

**Done-test:** A new team member is onboarded into the OS as their daily mode in a single sit-down session. Existing team members use it without prompting.

**Dependencies:** TD-3 + TD-7 (UI is usable). TD-5 (drafts surface). TD-6 (proposals working).

**Open questions to resolve:**
- Per-role flows — what does a Cam day look like in the OS? A George day?
- Documentation surface — in-product help? Wiki? Inline UI hints?

---

### TD-9 — Evaluations + continuous improvement loop

**Delivers:** Every autonomous associate has rubric + test set. Quality measured continuously. Regressions caught automatically.

**Sub-pieces:**
- Path 3 architecture executed — existing `evaluations` repo becomes a kernel adapter (`system_type: evaluation`, provider: `langsmith` or `indemn-evals`)
- Per-associate rubrics (EC, TS, IE, Artifact Generator, future associates)
- Per-associate test sets (capture real failure modes from LangSmith traces; multi-turn-replay + multi-turn-simulated)
- Continuous evaluation runs — when an associate behaves wrong, run an eval on the segment to pinpoint why and refine
- Eval results visible in the dashboard (TD-7 extension)

**Done-test:** Every autonomous associate has a rubric + test set. Evaluation results visible. Regressions caught automatically. Combined with deep tracing (LangSmith already wired, Session 10), this is the verification layer that lets us trust autonomous work.

**Dependencies:** TD-2 (associates running). LangSmith already wired (Session 10). Path 3 evaluations design (defer until needed).

**Open questions to resolve:**
- When does evaluation become first-class — is it a continuous thread from Session 12 onwards (running on an as-needed basis), or a dedicated TD that ships when the eval set is mature?
- Native OS evaluations primitive vs. external evaluations service vs. hybrid (Path 3 chosen, but timing of full kernel-adapter integration is open)

---

### TD-10 — Persistent-AI loops (Commitment-tracking pattern)

**Delivers:** Commitments tracked end-to-end. The "Walker → Peter → Ganesha → Kyle" pattern Kyle described Apr 24. When a Commitment is created in a meeting/email/Slack, the system watches it, notifies the assignee, tracks fulfillment, escalates up the chain when needed.

**Sub-pieces:**
- Commitment-tracker associate
- Watches on Commitment entity (created, transitioned)
- Notifies assignees (via Slack/email integration) when Commitments come due
- Tracks fulfillment events (e.g., "Walker said yes" → emit Commitment fulfilled)
- Escalation when overdue (Walker → Peter → Ganesha → Kyle)
- UI surface — Commitments per customer, per assignee, overdue items

**Done-test:** A Commitment created during a meeting flows through to the assignee, gets tracked, notifies up the chain when fulfilled or when overdue.

**Dependencies:** TD-2 (Commitment entity gets populated by IE). TD-3 (UI surface). TD-5 (artifacts include Commitment-related drafts).

**Open questions to resolve:**
- Commitment-tracker associate — what's its trigger pattern? Schedule-based (cron) for due-date checks, or event-based (watch Commitment transitions)?
- Escalation rules — time-based (overdue by N days), or signal-based (no activity)?
- Notification surface — Slack DM? Email? OS queue? All of the above?

---

### TD-11 — External-customer ready (Horizon 3)

**Delivers:** The OS is production-ready for external customers (non-Indemn). The kernel is hardened, the capability library is mature, the customer-onboarding playbook is real, a second domain can be modeled in days not weeks. The white paper's Phase 6 → Phase 7 transition becomes operable.

**Sub-pieces:**
- Kernel hardening — production-grade error handling, rate limiting, observability
- Customer-onboarding playbook — the 8-step domain modeling process with worked examples
- Second domain modelable — proven by either a fork attempt or planned next domain (e.g., delivery tracking, evaluations) coming online quickly
- Multi-tenancy edge cases resolved
- Compliance + audit trail surface (changes collection, hash-chain verification)

**Done-test:** A non-Indemn business modeled on the OS in <1 week. The customer-onboarding playbook is real and follows the 8-step process. Multi-tenancy holds.

**Dependencies:** TD-1 through TD-10 (Indemn fully running on the OS first).

**Open questions to resolve:**
- Second domain target — what's the first non-customer-system domain to prove generality? Delivery tracking? Evaluations as a domain? Conferences?
- Hardening checklist — what specifically needs to be production-grade before external customer onboarding?

---

## Continuous threads (run alongside every TD)

These are not deliverables — they run continuously across every TD.

### OS bug convergence (always-active)

**Operational discipline.** When customer-system work surfaces an OS-relevant finding, log it in `os-learnings.md`. If it blocks current TD work and is non-trivial, fork a parallel session to fix it. The customer-system development work doesn't block on bug fixes — they run in parallel.

- **Bug list lives in `os-learnings.md`** — ranked by impact (critical/blocking → high → medium → open design questions).
- **Top priorities at any time** — pulled from `os-learnings.md`'s "Critical / blocking the next phase" section. As of Session 12 close: most load-bearing work is done; remaining is mostly customer-system domain work + a handful of CLI papercuts.
- **Forking pattern** — when something blocks current TD work, fork to a separate git worktree, fix the OS-side bug in the OS repo, merge back. Coordinate with main session via shared context (`os-learnings.md` + `CURRENT.md`).
- **Fix-inline pattern** — when an OS fix is small and on the path of current work, do it inline. Don't fork unnecessarily.
- **Bugs are not pre-allocated to TDs** — they surface as we work; we fix them where they surface.

### OS-side milestones

As we build, the OS itself accumulates milestones beyond bug fixes. Track them so they don't drift.

- **Architecture docs reflect what we built** — `/Users/home/Repositories/indemn-os/docs/architecture/*.md` updated when patterns change.
- **Capability library expands** — each new kernel capability (entity-resolution, etc.) registered in `kernel/capability/` with docs.
- **Second domain modelable in days** — proven by either a fork attempt or a planned next domain (e.g., delivery tracking, evaluations) coming online quickly after customer-system is autonomous.
- **`product-vision/` project tracks design-level updates** to the OS (where OS design discussions land before becoming OS implementation work).

### Shared-context-update mechanism

**Critical operational discipline.** Multiple parallel sessions need shared context. Without a mechanism for this, the parallel work fragments and we lose the coherence the OS repo's documentation system gives us.

- **The mechanism today** — `CLAUDE.md` (always-loaded orientation), `INDEX.md` (append-only history), `vision.md` (slow-changing end-state), `roadmap.md` (living, where-we-are + path), `os-learnings.md` (running OS-finding register).
- **Per-session updates** — every session that completes work updates `roadmap.md` "Where we are now" + appends to `INDEX.md` Decisions/Open Questions/Artifacts. Every session that surfaces an OS-relevant finding appends to `os-learnings.md`. Per the discipline in `CLAUDE.md`.
- **Per-fork updates** — when a fork fixes a bug, the bug row in `os-learnings.md` is updated to fixed; the OS architecture doc (if affected) is updated; CLAUDE.md "Where we are now" reflects state.
- **Open question** — does this mechanism scale to N parallel sessions? Probably not as-is. Refinement is its own work item that surfaces during Phase B as parallel sessions multiply. May need: a session-state tracker (already exists at `systems/session-manager/`); a more structured handoff protocol; agent-based reconciliation. This is a meta-thread that runs throughout.

---

## Out of scope (for this roadmap)

This roadmap covers everything Indemn-the-company will run on the OS, plus the readiness for external customers (TD-11 / Horizon 3). What's explicitly NOT in this roadmap:

- **External-customer-specific domain modeling** — once TD-11 lands, modeling a non-Indemn business on the OS is a new project. Each external customer is its own domain configuration.
- **Voice agent products** for external customers (EventGuard-style autonomous voice flows) — different product, different system, not customer-system scope.
- **Mobile UI** — not in TD-3 scope. Web-first; mobile is a future consideration after team adoption (TD-8) proves the desktop experience works.
- **Inbound webhook from external customers' systems** — not in scope until TD-11.

Note: Persistent-AI loops (Walker → Peter → Ganesha → Kyle pattern, Kyle's Apr 24 ask) are now TD-10 — folded back in. They were previously deferred but the Commitment-tracking work belongs in this roadmap because the Commitment + Task + assignee-notification mechanism is part of the customer system's foundation.

---

## References

| File | What's in it |
|---|---|
| `vision.md` | What we're building, why, the breakthrough as the lens. |
| `os-learnings.md` | Running register of OS bugs, capability gaps, design questions. |
| `INDEX.md` | Append-only project history. Status, Decisions, Open Questions, full Artifacts table. |
| `CLAUDE.md` | Cumulative thinking, journey, principles, start-of-session protocol. **Always read first.** |
| `CURRENT.md` | Fast-changing state (parallel sessions, blockers, in-flight). Read after CLAUDE.md every session. |
| `SESSIONS.md` | Append-only per-session log of objectives + outcomes. |
| `PROMPT.md` | The session-start prompt template — pasteable into N parallel + N sequential sessions. |
| `artifacts/2026-04-22-entity-model-brainstorm.md` | Entity field-level specs. |
| `artifacts/2026-04-22-entity-model-design-rationale.md` | Why the entity model is shaped this way. The Alliance test. |
| `artifacts/2026-04-23-playbook-as-entity-model.md` | The breakthrough articulated. |
| `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` | Latest design refinements (Apr 24). |
| `artifacts/2026-04-24-extractor-pipeline-gap.md` | Why the Extractor failed Apr 24; Option B is the chosen fix. |
| `artifacts/2026-04-24-extractor-procedure-and-requirements.md` | Procedure for autonomous Extractor + 9 OS capability gaps. |
| `artifacts/2026-04-24-information-flow-v2.html` | The GR Little visual demo (open in browser). |
| `artifacts/2026-04-27-alliance-trace-showcase.html` | The Alliance trace-showcase visual (the language for TD-3 UI). |
| `artifacts/2026-04-24-grlittle-followup-email-draft.md` | The GR Little artifact + entity-to-line mapping. |
| `artifacts/2026-04-24-os-bugs-and-shakeout.md` | Bug-level deep detail. |
| `/Users/home/Repositories/indemn-os/docs/white-paper.md` | The OS canonical vision. |
| `/Users/home/Repositories/indemn-os/CLAUDE.md` | The OS builder's manual. |

---

*This document is updated every session that moves the work forward. When state changes, update "Where we are now"; when a phase completes, mark it done; when scope shifts, append a Decision in `INDEX.md` first, then revise here.*
