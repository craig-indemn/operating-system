---
ask: "Document exactly what I did manually to extract intelligence from the GR Little Touchpoint, so when the Intelligence Extractor associate is fixed it can replicate this behavior. Also document what CLI/OS functionality needs to exist for the associate to do this reliably."
created: 2026-04-24
workstream: customer-system
session: 2026-04-24-roadmap
sources:
  - type: conversation
    description: "Session work 2026-04-24 — Claude acted as the Intelligence Extractor after the live associate failed structurally. Craig asked for durable documentation of the procedure + OS gaps."
  - type: local
    ref: "projects/customer-system/artifacts/2026-04-24-extractor-pipeline-gap.md"
    description: "Why the live Extractor failed — the structural gap this procedure works around"
---

# Intelligence Extractor — Procedure + Required OS Capabilities

Two parts.

1. **The procedure** — step-by-step what a working Intelligence Extractor associate must do when it picks up a `Touchpoint created` message. Written so the next session can either use it verbatim to update the Extractor skill, or use it as an acceptance test ("the live associate must produce output equivalent to this for the GR Little Touchpoint").
2. **The OS capabilities gap** — what the CLI and the kernel must expose for the associate to do this reliably. The live Extractor failed in large part because these capabilities don't exist or aren't surfaced.

---

## Part 1 — The procedure

### Input

The agent starts with a message that names a Touchpoint entity. The harness packages:

```bash
indemn touchpoint get <touchpoint_id> --depth 2 --include-related
```

as the initial context. The agent also has its skill loaded to filesystem.

### Step-by-step

**Step 1 — Load the Touchpoint's source content.**

Read the Touchpoint's `type` field. Branch:

- `type == "meeting"`: get the source Meeting. Today this requires a reverse lookup that the API doesn't support (see Part 2 / Required Capability #1). Workable-but-ugly fallback: `indemn meeting list --company <touchpoint.company> --limit 50` and filter client-side for `meeting.touchpoint == <touchpoint_id>` (limited to 50 per page — will miss meetings past page 1). The clean fix is to add `source_entity_id` / `source_entity_type` to Touchpoint.
- `type == "email"`: get the source Email(s). Same reverse-lookup problem. Same fix.

Read the source's content:
- Meeting: `meeting.transcript` (the full verbatim record) and `meeting.summary` (if present — a pre-summarized version from the conference provider).
- Email: `email.body` (and follow `email.thread_id` to get the full thread).

**Step 2 — Load company + deal context for disambiguation.**

```bash
indemn company get <touchpoint.company>
indemn deal get <touchpoint.deal>
```

The company tells you industry, existing operations on file, tech stack. The deal tells you current stage and what prior Signals / Commitments are already tracked. This context matters for:
- Duplicate detection (don't create a Task that already exists for this Company)
- Stage-aware extraction (a DISCOVERY call surfaces pain points; a DEMO call surfaces objections; a NEGOTIATION call surfaces commercial concerns — what you extract should be calibrated)

**Step 3 — Extract entities from the source content.**

Work through the content and identify four structured categories. Only extract what is clearly stated — no inference, no embellishment.

For each category, apply duplicate detection: before creating, query `indemn <entity> list --company <company_id>` and check if an equivalent record already exists for this Company. Don't recreate. (Required capability: list by company. Required capability gap: arbitrary field filtering — see Part 2.)

**Tasks** — "someone needs to do something":
- Who is the assignee? (Employee ObjectId, set only if it's clear who owns it.)
- What priority? (high / medium / low)
- What category? (delivery / follow_up / internal / technical)
- Due date if stated.

```bash
indemn task create --data '{
  "title": "<imperative-voice title>",
  "description": "<why + what + evidence from transcript>",
  "company": "<company_id>",
  "source_meeting": "<meeting_id if meeting-touchpoint>",
  "touchpoint": "<touchpoint_id>",
  "assignee": "<employee_id if known>",
  "due_date": "<YYYY-MM-DD if stated>",
  "priority": "high|medium|low",
  "category": "follow_up|delivery|internal|technical",
  "source": "meeting_extraction"
}'
```

**Decisions** — "something was decided, direction was set":
- `decided_by`: the name of whoever announced it.
- `participants`: list of names in the room.
- `rationale`: why, if stated.
- `impact`: downstream consequence, if stated.

```bash
indemn decision create --data '{
  "description": "<what was decided>",
  "company": "...",
  "source_meeting": "...",
  "touchpoint": "...",
  "decided_by": "<name>",
  "participants": ["<name>", ...],
  "rationale": "<why, quoting or paraphrasing>",
  "impact": "<downstream consequence>"
}'
```

**Commitments** — "X committed to Y":
- `made_by`: person name.
- `made_by_side`: "indemn" or "customer".
- `made_to`: person name.
- `due_date` if stated.
- One Commitment per distinct promise.

```bash
indemn commitment create --data '{
  "description": "<what was promised>",
  "company": "...", "source_meeting": "...", "touchpoint": "...",
  "made_by": "<name>",
  "made_by_side": "indemn|customer",
  "made_to": "<name>",
  "due_date": "<YYYY-MM-DD if stated>"
}'
```

**Signals** — "pattern to notice":
- `type`: champion / expansion / health / churn_risk / blocker / insight.
- `severity`: high / medium / low.
- `attributed_to`: person or role who exhibited the signal.

```bash
indemn signal create --data '{
  "description": "<what was observed, with quote if short and useful>",
  "company": "...", "source_meeting": "...", "touchpoint": "...",
  "type": "champion|expansion|health|churn_risk|blocker|insight",
  "severity": "high|medium|low",
  "attributed_to": "<person or role>"
}'
```

**Step 4 — Transition the Touchpoint to processed.**

```bash
indemn touchpoint transition <touchpoint_id> --to processed --reason "Intelligence extraction complete: N Tasks, N Decisions, N Commitments, N Signals"
```

**Step 5 — Mark the message complete.**

The harness handles this via `indemn queue complete <message_id>` at the end of the activity. The agent must return control cleanly to the harness (no silent empty responses — see Bug noted in `2026-04-24-extractor-pipeline-gap.md`).

### Quality bar

- Every entity has `company`, `source_meeting` (if meeting-touchpoint), and `touchpoint` fields populated. This is the graph spine — without it, entities are orphans.
- Extract what's stated, not what's implied. The LLM's natural tendency is to embellish. Resist.
- It's fine to produce zero entities for a Touchpoint with no substance (e.g. a scheduling-only email). Still transition the Touchpoint to `processed`.
- Short, factual descriptions. Quote when the quote is load-bearing. Don't write essays — downstream artifact generation will.

### Worked example

For GR Little Apr 22 Touchpoint `69ebbec5472952352cdfda4f`, this procedure produced:
- 2 Tasks (Kyle sends recap; Kyle scrapes site + builds personalized demo)
- 2 Decisions (positioning as agency-tier front-door-only; skip quick peek, do full demo)
- 4 Commitments (Kyle×2 send+build; Walker×2 book+loop-in)
- 5 Signals (Walker as champion candidate; expansion to outbound renewals; expansion to payment-taking; blocker from low-tech Principal; insight on wedge candidates)

All entities are linked to Company `69eb95f22b0a508618923977`, Meeting `69eb94a92b0a50861892382a`, Touchpoint `69ebbec5472952352cdfda4f`. Query the graph with `indemn company get 69eb95f22b0a508618923977 --depth 2 --include-related` to see the full state.

---

## Part 2 — Required OS capabilities (gaps)

For the Extractor (and eventually the Artifact Generator) to run this procedure reliably as an autonomous associate, the OS needs the following. These are gaps we HIT today.

### Required capability #1 — Navigate Touchpoint → source (Meeting / Email)

**Today:** broken. Touchpoint has no forward pointer to its source. Meeting/Email have `touchpoint` pointing back, but the list API doesn't support filtering by arbitrary fields, so there's no way to query "give me the Meeting where touchpoint = X."

**Fix (recommended — Option B from extractor-pipeline-gap.md):** Add two fields to Touchpoint — `source_entity_type: str` (e.g. "Meeting") and `source_entity_id: objectid`. Populated by the Touchpoint Synthesizer on create. Downstream associates call `indemn <source_entity_type> get <source_entity_id>` directly. Zero new CLI machinery needed.

**Alternative fixes:**
- Make `--include-related` follow reverse relationships (kernel feature — general but more work).
- Add arbitrary field filtering to the list endpoint (see Capability #2 below, needed anyway) and teach the skill to use it.

### Required capability #2 — List entities with arbitrary field filters

**Today:** broken. `indemn <entity> list` accepts only `--status`, `--search`, `--limit`, `--offset`, `--sort`. No `--data` or `--filter` or per-field query params on the API. `GET /api/<entity>/` ignores any non-documented query parameters.

This blocks:
- "List meetings where touchpoint = X" (the reverse-lookup fallback)
- "List tasks for this company with priority=high" (duplicate detection refinement)
- "List commitments where made_by_side = customer and stage = open" (cadence / follow-up queries)

**Fix:**
- API: extend list endpoint to accept a `filter` JSON query param (or separate query params for each field), with safelist of allowed fields from the EntityDefinition.
- CLI: expose as `--data '{"field": "value"}'` on list (matching the pattern already used on create/update).
- Skill generation: auto-include "you can filter by any field" in the generated entity skill once available.

### Required capability #3 — Generated entity skill teaches actual filter syntax

**Today:** the auto-generated `indemn skill get Meeting` lists fields and state transitions but doesn't teach the agent how to filter lists or how to navigate relationships. Agents improvise (e.g. `--filter` which doesn't exist) and fail.

**Fix:** `kernel/skill/generator.py` should emit concrete CLI recipes:
- "To filter: `indemn meeting list --data '{\"company\": \"<id>\", \"status\": \"classified\"}'` (once Capability #2 lands)"
- "Forward relationships: `indemn meeting get <id> --depth 2 --include-related` returns the related `company` and `touchpoint` inline."
- "Reverse relationships: see `source_entity_id` on related entities that were synthesized from this one."

### Required capability #4 — Workflow must detect "agent completed with empty output" as failure

**Today:** broken. The GR Little live Extractor run produced an empty `Agent response:` and `Agent completed: 17 messages, tools=[...]`, but the Temporal workflow never marked the message complete or failed. It sat in `processing` with `last_error: null`. Eventually visibility timeout will re-queue it and the same broken run will repeat until `max_attempts`.

**Fix:** in `harnesses/async-deepagents/main.py`, after `agent.ainvoke(...)` returns, inspect the final message. If the agent produced no meaningful content AND made no mutating CLI calls (no `indemn <entity> create/update/transition`), mark the message failed with `last_error: "agent completed without producing output or state changes"`. The visibility timeout then handles retry (with backoff / dead-letter) rather than silent re-dispatch.

### Required capability #5 — Per-invocation tool-result isolation in the harness

**Today:** broken. The `/large_tool_results/` path is shared across agent invocations in the same runtime container. A grep in one invocation matched content cached by a completely different prior invocation (Apr 17 FoxQuilt transcript appeared in the GR Little agent's grep output).

**Fix:** in `harnesses/_base/harness_common/backend.py`, scope the large-result cache per activity/message (e.g. `/large_tool_results/<message_id>/...`) and wipe on activity completion.

### Required capability #6 — Support re-triggering watches on historical entities (backfill)

**Today:** broken. Our GR Little Meeting was already created days ago, so linking `meeting.company` today doesn't re-fire the "Meeting created" watch. For the Synthesizer to process backfilled meetings, we have no mechanism — we had to manually create the Touchpoint as a workaround.

**Fix:** either a `indemn <entity> reprocess <id> --role <role_name>` CLI that synthesizes a `created`-equivalent event for a named role, or a role-level `backfill` capability ("for this role's watches, evaluate against all existing entities matching the condition"). This is Bug #10 from the shakeout artifact promoted to a real required capability.

### Required capability #7 — Duplicate entity detection

**Today:** not supported systemically. Every associate is told "don't duplicate" in its skill, but has no OS-level query to answer "does a similar Company / Contact / Task already exist." Forensics on the 446-Company explosion traces back to this.

This is the same underlying question as `project_customer_system_entity_identity.md` in memory. A kernel `entity_resolution` capability would serve this — given a candidate (domain, name, email, similar-description), return likely existing matches with a confidence score. Every intake-associate uses it before creating.

### Required capability #8 — Actor transition via CLI

**Today:** Bug #20. `indemn actor` has no `transition` subcommand. To suspend / resume / deprovision an associate you have to hit the API directly via curl. Minor but papercut-y.

### Required capability #9 — Singular `delete` CLI

**Today:** Bug #2. No `indemn <entity> delete <id>`. Only `bulk-delete`, which is also semi-broken (Bug #23). Cleanup of individual bad entities (the 446 Company dupes, the dead-letter messages) requires Mongo directly.

---

## Summary — priorities for making the Extractor autonomous

Rough prioritization if we're building this back out:

| # | Capability | Difficulty | Unblocks |
|---|---|---|---|
| 1 | Touchpoint `source_entity_*` fields + Synth populates them | S | The Extractor can find source content |
| 4 | Workflow detects empty-output agent as failure | S | Reliability — no silent stuck messages |
| 5 | Per-invocation tool-result isolation | S | No cross-task content leaks |
| 3 | Generated entity skill teaches filter syntax | S | Agents stop improvising `--filter` |
| 2 | Arbitrary field filter on list API/CLI | M | Duplicate detection, broader queries |
| 7 | Entity resolution capability (kernel) | M | Prevents future 446-Company explosions |
| 6 | Backfill / reprocess for historical entities | M | Onboarding new associates against existing data |
| 8 | `indemn actor transition` | XS | Papercut |
| 9 | Singular `delete` CLI | XS | Papercut |

Top four are small and together they take the Extractor from "structurally broken" to "works reliably on the happy path." Everything below that is quality-of-life or scale reliability.
