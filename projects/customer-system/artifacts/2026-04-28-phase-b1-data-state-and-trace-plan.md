---
ask: "Plan for Phase B1 entity-resolution skill propagation — captures live OS data state (the cumulative result of the Apr 23 Email Classifier auto-create wave + the Apr 27 trace work), the structural gaps in current entity_resolve activations, the lightweight cleanup pass that runs before the trace (Path A), and the trace plan for the Email Classifier + Touchpoint Synthesizer skills following the trace-as-build-method principle (CLAUDE.md #20, vision §4)."
created: 2026-04-28
workstream: customer-system
session: 2026-04-28-b1-entity-resolution
sources:
  - type: mongodb
    description: "Direct queries against dev OS indemn_os.companys / contacts / emails / touchpoints / actors / entity_definitions"
  - type: cli
    ref: "/Users/home/Repositories/indemn-os/.venv/bin/indemn"
    description: "indemn entity get Company / Contact / actor list --type associate"
  - type: local
    ref: "projects/customer-system/os-learnings.md"
    description: "Bug #16 root + entity-resolution kernel capability ship status"
  - type: local
    ref: "projects/customer-system/CLAUDE.md"
    description: "Foundational design principle #20 — trace-as-build-method"
  - type: local
    ref: "projects/customer-system/vision.md"
    description: "Section 4 — How we build"
  - type: local
    ref: "projects/customer-system/roadmap.md"
    description: "Phase B preamble — building method"
---

# Phase B1 — Entity-Resolution Skill Propagation: Data State + Trace Plan

## Why this artifact exists

Phase A is closed. Phase B (build to autonomous) opens with the most direct unblock: getting the Email Classifier and Touchpoint Synthesizer skills to call the kernel's `entity_resolve` capability before creating, so Bug #16 (the 446-Company auto-create explosion that became 314 Companies + 424 Contacts in dev OS) is closed end-to-end.

This artifact is the working plan. It captures:
1. The live state of dev OS (so the next session doesn't have to re-derive it)
2. The structural gaps we have to fix in entity_resolve activations before any skill work happens
3. The lightweight cleanup pass (Path A) that gets the data into a tractable state
4. The trace plan that follows — Email Classifier + Touchpoint Synthesizer built via trace-as-build-method
5. What's explicitly deferred from this scope so it doesn't creep in

We work to this artifact. When state changes, we update it. It's the project memory for Phase B1.

---

## 1. Data state inventory (verified 2026-04-28)

### Companies — 314 total

| Origin | Count | Status |
|---|---|---|
| Apr 18 hand-seeded (cohort set: 8 AI_Investments + 5 Core_Platform + 5 Graduating + 66 Prospect) | 84 | ✅ Canonical |
| Apr 21-22 (manual, Prospect) | 2 | ✅ Canonical |
| Apr 23 (Email Classifier wave: 197 cohort=null + 5 cohort) | 202 | ⚠️ Mostly noise |
| Apr 24 (continuation of EC wave) | 22 | ⚠️ Mostly noise |
| Apr 27 (Alliance trace + cleanup) | 4 | ✅ Real |

**Critical specific findings:**
- **Alliance:** 1 canonical (`69e41a82b5699e1b9d7e98eb`, "Alliance Insurance", Apr 18 Prospect) + 3 wrong auto-creates (`69ea833cff375a32fa259c6e` "MetroHartford Alliance", `69ea9ebeff375a32fa25a3ae` "Alliance", `69eaa20dff375a32fa25a9aa` "MetroHartford Alliance")
- **GR Little:** 2 records — `69e9464a23eefe641ea13eb7` ("GR Little Insurance", Apr 22 Prospect, no domain) + `69eaa554ff375a32fa25ac8e` ("GR Little", Apr 23 cohort=null, has `grlittle.com` domain). Need to merge — preferred canonical is the trace-era one (`69eb95f2…3977` per Apr 25 handoff; verify exact ID before merging).
- **30+ dupe groups by exact name** — Vercel ×3, LinkedIn ×3, Jewelers Mutual ×3, Apollo.io ×2, Tillman Insurance Advisors ×2, MetroHartford Alliance ×2, etc. Mix of vendor-noise and real prospects.
- **125 pure orphans:** Companies with cohort=null, created Apr 23+, with **zero emails pointing at them**. Pure auto-create noise. Bulk-deletable.

### Contacts — 424 total (worse state than Companies)

| Origin | Count | Status |
|---|---|---|
| Apr 18-19 hand-seeded | 92 | ✅ Canonical |
| Apr 23-24 (Email Classifier wave) | 329 | ⚠️ Heavy dupes |
| Apr 27 (Alliance trace) | 3 | ✅ |

**The dupe state on Contacts is materially worse than Companies:**
- **92 Contacts with empty email** — auto-created from name parsing without email capture
- **`service@eventguard.ai` × 37** — single service email created as 37 different Contacts
- **`jcdp@gicunderwriters.com` × 15** — JC × 15
- **`schyzhov@family-first.com` × 12** — Serhii × 12
- **`kyle@indemn.ai` × 7** — Kyle × 7
- **`raqueltillman@tillmaninsadv.com` × 6** — Raquel × 6
- **`{nick.atwood,landon.roeming,simon.roberts,kyle.deperty}@ourbranch.com` × 5 each** — Branch team × 5 each
- **`cam@indemn.ai` × 4** — Cam × 4

The pattern: every Email Classifier run that saw a sender/recipient email created a NEW Contact rather than finding the existing one. This is **Bug #16's Contact-axis manifestation** — same root cause, never solved on Contact because `entity_resolve` was never activated on Contact.

### Emails — 1,138 total (much better state than I'd remembered as "~930")

| Status | Count |
|---|---|
| received | 322 |
| irrelevant | 289 |
| processed | 271 |
| classified | 136 |
| needs_review | 116 |
| (null) | 4 |

**Email-to-Company classification is mostly correct.** The high-volume Companies that emails point at are canonicals: Jewelers Mutual 17 / GIC 17 / Family First 11 / Alliance 4 / Tillman 3 / Union General 3 / Branch 2. The 46 emails attributed to org_id `69e23d586a448759a34d3823` are internal/Indemn emails (not wrong). The vendor-noise auto-created Companies have 1-3 emails each.

### Touchpoints — 78 total

- 35 logged + 43 processed
- **Only 6 of 78 carry Option B source pointers** (created post-Apr-27 deploy). The other 72 lack `source_entity_type` + `source_entity_id`, so the Intelligence Extractor can't navigate from them to the source Email/Meeting. Backfill is its own work; **not blocking the B1 trace** since new Touchpoints created during the trace populate the pointers correctly.

### Pipeline associates — current state

| Associate | Status | Notes |
|---|---|---|
| Email Classifier | suspended | The skill that produced the data mess; needs the entity-resolve update |
| Touchpoint Synthesizer | suspended | Skill v3 from Apr 27 (Option B aware); needs Contact entity-resolve added |
| Intelligence Extractor | active | Was activated Apr 24 to test; can stay active |
| OS Assistant | active | Different role, not pipeline |

---

## 2. Structural gaps in entity_resolve activations

The kernel `entity_resolve` capability shipped Apr 27. Its current per-entity activation state is incomplete for what the Email Classifier + Touchpoint Synthesizer flows actually need.

### Gap 1: Contact `entity_resolve` is NOT activated

```
Contact.activated_capabilities = []   ← verified empty
```

Without this, Email Classifier can't query "is `kyle@indemn.ai` already a Contact?" — explains the 7×Kyle / 15×JC / 37×EventGuard duplication.

**Required activation:**
- `field_equality` strategy on `email` (with `lowercase_trim` normalizer) — primary identity for Contact
- `field_equality` strategy on `name` (with `lowercase_trim` normalizer) — secondary fallback

### Gap 2: Company `entity_resolve` lacks a `domain` strategy

Current activation:
```json
{
  "strategies": [
    {"type": "field_equality", "field": "name", "normalizer": "lowercase_trim"},
    {"type": "fuzzy_string",   "field": "name", "threshold": 0.85}
  ]
}
```

Email Classifier in practice matches via sender domain (an email from `walker.ross@grlittle.com` should resolve to the GR Little Company even when the Email's "From" name is "Walker Ross"). The current activation has no domain strategy.

**Required addition:**
- `field_equality` strategy on `domain` (with `lowercase_trim` normalizer)

### Gap 3: Touchpoint Option B backfill (deferred, not blocking)

72 of 78 historical Touchpoints lack `source_entity_type` + `source_entity_id`. New Touchpoints created during/after the B1 trace will populate them correctly. Historical backfill is separate work — file under "ingestion durability" follow-on.

---

## 3. Path A — lightweight cleanup before trace

Goal: get the data into a tractable state so the trace operates on a recognizable system, not a mess. Time-box: **30-60 minutes**.

### Step A1 — Capability activations

```bash
# Add domain strategy to Company entity_resolve
indemn entity enable Company entity_resolve --config '{
  "strategies": [
    {"type": "field_equality", "field": "name",   "normalizer": "lowercase_trim"},
    {"type": "field_equality", "field": "domain", "normalizer": "lowercase_trim"},
    {"type": "fuzzy_string",   "field": "name",   "threshold": 0.85}
  ]
}'

# Activate entity_resolve on Contact
indemn entity enable Contact entity_resolve --config '{
  "strategies": [
    {"type": "field_equality", "field": "email", "normalizer": "lowercase_trim"},
    {"type": "field_equality", "field": "name",  "normalizer": "lowercase_trim"}
  ]
}'
```

Verify each activation by re-fetching the entity definition and confirming `activated_capabilities` lists `entity_resolve` with the expected strategies. Hit the `entity-resolve` CLI sub-command on a known case to confirm working.

### Step A2 — Bulk delete pure-orphan Companies (125 records)

Pure-orphans = `cohort=null` AND `created_at >= 2026-04-23` AND no emails reference the Company AND no Contacts reference it.

```bash
# Get the list of Company IDs that have any references (emails or contacts)
# Then bulk-delete the complement that match the orphan filter
indemn company bulk-delete --filter '{
  "cohort": null,
  "created_at": {"$gte": {"$date": "2026-04-23T00:00:00Z"}},
  "_id": {"$nin": <list of referenced company ids>}
}'
```

Pre-deletion: dry-run via `--dry-run` to confirm count ≈ 125. If higher, narrow the filter; if lower, accept.

### Step A3 — Resolve obvious dupe Contacts (high-volume groups first)

Hard targets, in order:
1. `service@eventguard.ai` × 37 — pick oldest; reclassify references; delete others
2. `jcdp@gicunderwriters.com` × 15 — pick oldest; reclassify; delete
3. `schyzhov@family-first.com` × 12 — pick oldest; reclassify; delete
4. `kyle@indemn.ai` × 7 — pick the actor-linked one; reclassify; delete
5. `raqueltillman@tillmaninsadv.com` × 6 — pick oldest; reclassify; delete
6. The four `*@ourbranch.com` × 5 each — same pattern
7. `cam@indemn.ai` × 4 — pick the actor-linked one; reclassify; delete

For each group:
- Find canonical (heuristic: oldest record OR most populated fields OR has `actor_id` set)
- Find Email entities with `sender_contact ∈ <dupe_ids>` and `recipients_contacts ∈ <dupe_ids>`; reclassify those references to canonical
- Find Touchpoints with `participants_contacts ∈ <dupe_ids>`; reclassify
- Bulk-delete the non-canonical IDs

This step exercises the same operations the cleanup of dupe Companies will later (when we handle the harder Alliance/MetroHartford/GR Little ambiguity inside the trace).

**Defer:** Contacts with empty email (92 records). These need richer matching to safely merge — leave for now.

### Step A4 — Verify

Re-run the inventory queries from Section 1 and confirm:
- Companies: ~189 (314 - 125 orphans)
- Contacts: substantially fewer dupes for the targeted addresses
- No canonical Companies/Contacts touched
- entity_resolve on Company resolves "Alliance Insurance" cleanly
- entity_resolve on Contact resolves `kyle@indemn.ai` to a single canonical

If verify passes, proceed to Phase B1 trace (Section 4). If not, stop and reconcile.

---

## 4. Phase B1 trace — Email Classifier + Touchpoint Synthesizer

Following the trace-as-build-method (CLAUDE.md #20). Claude acts as each associate; runs `indemn` CLI on real data; the skill writeup IS what worked.

### Step B1.1 — Pick scenarios

Four scenarios cover the decision tree:

1. **Known canonical Contact + Company match** — pick a recent email from `jcdp@gicunderwriters.com`. Expected: Contact resolve returns single 1.0 → link to canonical JC; Company resolve on `gicunderwriters.com` returns single 1.0 → link to canonical GIC. Email transitions classified.
2. **Known Company, new Contact at that Company** — pick an email from a never-before-seen sender at `@ourbranch.com`. Expected: Contact resolve returns 0 matches → per current skill design, Contact CAN be auto-created on email arrival (this is a discovery point for the system); Company resolve on `ourbranch.com` returns single 1.0 → link to canonical Branch.
3. **Truly new prospect** — email from a sender at a never-before-seen domain. Expected: Contact resolve = 0; Company resolve = 0; Email transitions to `needs_review`. Skill explicitly does NOT auto-create Company.
4. **Ambiguity** — pick a case where the Company resolve returns multiple candidates (e.g., a "Foxquilt"/"Fox Quilt"/"FoxQuilt" situation if it exists, or "Alliance" with the 3 wrong auto-creates if Path A leaves any). Expected: skill detects ambiguity → `needs_review` with the candidates listed.

### Step B1.2 — Trace as Email Classifier

For each scenario, Claude runs the procedure end-to-end via CLI:

```bash
# Load the email
indemn email get <id> --include-related

# Resolve sender Contact
indemn contact entity-resolve --data '{"candidate": {"email": "<sender_email>", "name": "<sender_name>"}}'

# Resolve Company by domain (and fallback by name if domain not in result)
indemn company entity-resolve --data '{"candidate": {"domain": "<sender_domain>", "name": "<extracted_company_name>"}}'

# Decision tree:
# - Both resolve to single 1.0 → link both, transition email to classified
# - Contact 0 + Company 1.0 → create Contact attached to Company, link, classified
# - Contact 1.0 + Company 0 → link Contact, transition email to needs_review (Company decision needs human)
# - Multiple Company 1.0 (ambiguity) → needs_review with candidate list in notes
# - Both 0 → needs_review

indemn email update <id> --data '{...links...}'
indemn email transition <id> --to classified  # or needs_review
```

Document at each step: what resolve returned, what decision was made, why. This is the skill content.

### Step B1.3 — Trace as Touchpoint Synthesizer

Email transitions to `classified` → Touchpoint Synthesizer fires. Procedure:

```bash
# Read the email + thread context
indemn email get <id>
indemn email list --data '{"thread_id": "<thread_id>"}'

# Resolve participants (sender + recipients) as Contacts
indemn contact entity-resolve --data '{"candidate": {"email": "<participant_email>"}}'  # for each

# Look for existing Touchpoint for this thread
indemn touchpoint list --data '{"source_entity_type": "Email", "thread_id": "<thread>"}'

# If none exists, create new Touchpoint with Option B pointers populated
indemn touchpoint create --data '{
  "company": "<co_id>",
  "type": "email",
  "scope": "<external|internal>",
  "date": "<email date>",
  "participants_contacts": [...],
  "participants_employees": [...],
  "source_entity_type": "Email",
  "source_entity_id": "<email_id>",
  "summary": "<one-liner>"
}'

# Update Email to point at the Touchpoint (Option A back-reference)
indemn email update <id> --data '{"touchpoint": "<touchpoint_id>"}'

# Transition email to processed
indemn email transition <id> --to processed
```

Same documentation discipline: what was resolved, what was created/linked, why.

### Step B1.4 — Write the skills

Once the four scenarios traced cleanly, the skills are the writeup of what worked:

- **Email Classifier skill (update):** add a "Resolve before create" section with the decision tree from B1.2. Explicit CLI commands. Explicit branches.
- **Touchpoint Synthesizer skill (update from v3):** add Contact resolution call into the participant loop. Confirm Option B pointers are still populated.

Verify content hashes change after update. Reference the skill files in this artifact.

### Step B1.5 — Reactivate Email Classifier

```bash
indemn actor transition <Email Classifier id> --to active
```

Drain a small batch of `received` emails (probably from the queue or by reprocessing a few historical ones via Bug #10's reprocess primitive). Watch traces for the first 5-10 — confirm:
- entity_resolve calls happen
- linking is correct
- no auto-create of Companies
- needs_review path exercised correctly
- `effective_actor_id` shows Email Classifier (Bug #22 fix verification in production)

Kill switch ready: `indemn actor transition <id> --to suspended` if anything looks wrong.

### Step B1.6 — Reactivate Touchpoint Synthesizer

After Email Classifier is producing clean classifications, activate the Synth. Same drain + watch + kill-switch pattern. Confirm:
- Touchpoints created with Option B pointers
- Contact resolution working
- Document creation from email attachments correct
- Email transitions to `processed`

### Step B1.7 — Watch the cascade

With both active, the next inbound email should produce the full chain:
- Email created → Email Classifier classifies → Email Synthesizer creates Touchpoint → Intelligence Extractor reads Touchpoint via Option B pointers → entities extracted

If this works end-to-end on a new email, B1 is done.

---

## 5. What is explicitly OUT of scope for this trace

Resist scope creep. These items live in B1 elsewhere or in later phases:

- **Touchpoint Option B backfill** for the 72 historical Touchpoints. Defer until they actually need to be reprocessed.
- **Hard dupe resolution** (Alliance vs. MetroHartford vs. plain "Alliance"; GR Little 2-record merge; Jewelers Mutual ×3). These need judgment and may be informed by what the skill does — handle in a follow-on cleanup pass after the skills work.
- **Bug #18 Synth back-reference enforcement** (Synth doesn't reliably set Meeting.touchpoint). Subsumed structurally by Option B; skill enforcement is a follow-on if not naturally captured.
- **Email entity rename `interaction` → `touchpoint`** + `interactions` collection cleanup. Pre-Apr-23 rename gap; structural cleanup, do after pipeline is reliable.
- **Document-as-artifact pattern for emails** (Email entity with status=drafting? Document with mime_type=rfc822?) — open design question; not blocking the resolve-before-create work.
- **Bug #9** dicts vs ObjectId strings — likely subsumed by the entity-skill JSON examples shipped Apr 27; verify during the trace and decide.
- **`--include-related` reverse refs** — kernel feature, not blocking for B1.
- **Slack ingestion** — foundational per the Apr 27 trace, but a separate adapter build. Comes after B1 + B2 hydration.
- **Stale entity-skill rendering** — ergonomics; on the medium register.
- **Proposal state machine `superseded` transition** — needed for v1→v2 cleanly but doesn't gate the resolve work.

Each of these gets its own follow-on; none belong in this trace.

---

## 6. Decisions log

*(Append as decisions are made during execution.)*

- 2026-04-28: Path A chosen over trace-as-cleanup. Light cleanup pass → then trace on cleaner data. Rationale: Contact dupes are heavy enough (37×EventGuard, 15×JC) that the trace on dirty data spends most of its time disambiguating noise instead of producing skill content.
- 2026-04-28: Capability activations expand on what shipped Apr 27 — Contact gets `entity_resolve` activated for the first time; Company gets `domain` strategy added.
- 2026-04-28: Hard prospect dupes (Alliance auto-creates, GR Little 2-record merge, Jewelers Mutual ×3) deferred. They require judgment that the trace will inform.
- 2026-04-28 (after the trace): Path A executed cleanly. 79 orphan Companies deleted; 91 high-volume Contact dupes resolved + canonical preserved.
- 2026-04-28 (during B1 trace): JLI ×3 + Level Equity ×4 dupes surfaced inline (below the volume threshold I targeted in A3) — resolved as part of the trace.
- 2026-04-28: Email.interaction → Email.touchpoint rename completed as root-cause fix (not workaround). 1139 docs migrated; relationship_target updated; audited all 26 entities (only Email had the leftover); `interactions` MongoDB collection kept (it's the kernel chat/voice session log, different entity).
- 2026-04-28: Three skills updated — Email Classifier v3, Touchpoint Synthesizer v6 (with Step 1a idempotency via Email.touchpoint back-reference), Intelligence Extractor v3 (Option B navigation, mandatory transition).
- 2026-04-28 (B1.5 single-email reactivation test — KILL SWITCH FIRED): Reactivated Email Classifier and reprocessed Diana@CKSpecialty's email. EC processed 3 messages (3 prior pending + the reprocess one). Justin Li's email (single 1.0 match for both Contact + Company) classified correctly — clean ✅. Diana's email (multi-candidate case — 2 1.0 Contacts + 1 1.0 Company by domain) **violated the skill rule**: EC auto-created a NEW Company despite "Never auto-create a Company" being explicit, did NOT mark needs_review on multi-match ambiguity, and did NOT transition the email. Suspended EC immediately, rolled back the auto-created Company, reset Diana's email to received. **The agent has a skill-compliance gap on the harder multi-candidate branch.** Skill content is correct in the database (verified content_hash matches v3, "Never auto-create" + "Multiple 1.0 candidates → needs_review" both present). This is research-level — needs deeper investigation before reactivation. Possible remedies: more explicit decision-tree language; force_reasoning rule that vetoes any Company create from EC; eval-driven fine-tuning of skill compliance. **Reactivation halted until this is resolved.**

---

## 7. Execution checklist

**Phase A cleanup (Path A):**
- [ ] A1.1 — Add `domain` strategy to Company entity_resolve
- [ ] A1.2 — Activate entity_resolve on Contact (email + name strategies)
- [ ] A1.3 — Verify activations via CLI
- [ ] A2 — Bulk-delete 125 orphan Companies (with dry-run first)
- [ ] A3.1 — Resolve `service@eventguard.ai` × 37 dupes
- [ ] A3.2 — Resolve `jcdp@gicunderwriters.com` × 15 dupes
- [ ] A3.3 — Resolve `schyzhov@family-first.com` × 12 dupes
- [ ] A3.4 — Resolve `kyle@indemn.ai` × 7 dupes
- [ ] A3.5 — Resolve `raqueltillman@tillmaninsadv.com` × 6 dupes
- [ ] A3.6 — Resolve four `*@ourbranch.com` × 5 each
- [ ] A3.7 — Resolve `cam@indemn.ai` × 4 dupes
- [ ] A4 — Verify clean state

**Phase B1 trace:**
- [ ] B1.1 — Pick 4 scenarios (canonical match / new Contact / new prospect / ambiguity) — capture exact email IDs
- [ ] B1.2 — Trace as Email Classifier through all 4
- [ ] B1.3 — Trace as Touchpoint Synthesizer through the resulting state
- [ ] B1.4 — Update Email Classifier skill (writeup of what worked)
- [ ] B1.4 — Update Touchpoint Synthesizer skill (Contact resolve added to v3)
- [ ] B1.5 — Reactivate Email Classifier; drain 5-10 messages; verify
- [ ] B1.6 — Reactivate Touchpoint Synthesizer; drain; verify
- [ ] B1.7 — Watch full cascade end-to-end on next live email

**Closeout:**
- [ ] Update INDEX.md Status + Decisions
- [ ] Update os-learnings.md (Bug #16, Bug #17 close)
- [ ] Update CLAUDE.md "Where we are now"
- [ ] Update roadmap.md Phase B1 progress
- [ ] Commit
