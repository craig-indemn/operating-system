---
ask: "Capture the Intelligence Extractor pipeline failure we observed when tracing GR Little end-to-end on Apr 24, the root causes, and the structural fix options — this is the fundamental issue Craig predicted"
created: 2026-04-24
workstream: customer-system
session: 2026-04-24-roadmap
sources:
  - type: runtime-logs
    description: "indemn-runtime-async Railway logs during Intelligence Extractor invocation on Touchpoint 69ebbec5472952352cdfda4f (GR Little Apr 22 meeting)"
  - type: code
    ref: "harnesses/async-deepagents/main.py:107-108, agent.py DEFAULT_PROMPT"
    description: "How the async harness packages context for the agent"
  - type: code
    ref: "kernel/api/registration.py (--include-related parameter handling)"
    description: "How --include-related resolves related entities"
  - type: local
    ref: "projects/customer-system/skills/intelligence-extractor.md (via `indemn skill get intelligence-extractor`)"
    description: "The skill the agent was given"
---

# The Intelligence Extractor Is Structurally Missing Its Input

## Context

Today we ran the Intelligence Extractor against a single Touchpoint (GR Little Apr 22 meeting) to verify the pipeline works end-to-end. It failed. The failure is not a skill-wording problem, not an LLM capability problem, not a transient bug — it's a structural gap in what information the pipeline gives the agent at startup.

Craig flagged this class of issue earlier in the day: *"there's a fundamental issue that's causing the issues we were seeing before that has nothing to do with the LLM itself."* This is one concrete instance of it.

## What we observed

We manually created Touchpoint `69ebbec5472952352cdfda4f` from the GR Little Apr 22 meeting (id `69eb94a92b0a50861892382a`). The Touchpoint-`created` event fired the Intelligence Extractor role's watch. A message was queued. We activated the Extractor actor (it had been suspended). The harness picked up the message and ran the agent.

The agent's runtime log (trimmed to tool calls):

```
agent.invoke(messages=[{"role":"user","content":"Process this work:\n\n<touchpoint dump>"}])
tool: execute  →  indemn company list --filter ...                    (error: --filter not an option)
tool: execute  →  indemn company list --help                          (docs returned)
tool: execute  →  indemn company list --limit 100                     (too-large, saved to /large_tool_results/2edfaff1-...)
tool: read_file →  /large_tool_results/2edfaff1-...  limit=100         (partial)
tool: grep     →  pattern=INDEM path=/large_tool_results/2edfaff1-... (matched on /large_tool_results/3bc0edc5-..., a CACHED result from a prior agent invocation — Apr 17 Nick/FoxQuilt transcript)
tool: read_file →  /large_tool_results/2edfaff1-...  limit=null        (type error)
Agent response: (empty)
Agent completed: 17 messages
```

Outcome:
- **Zero entities created** (no Task, Decision, Commitment, or Signal for GR Little)
- Touchpoint still at `status: logged` (never transitioned to `processed`)
- Message still at `status: processing` in the queue (workflow never marked complete or failed)
- No error recorded on the message (`last_error: null`)

## Root cause — the agent had no source data

What the agent received as starting context:

```bash
indemn touchpoint get 69ebbec5472952352cdfda4f --depth 2 --include-related
```

Returns:

| Field | Value |
|---|---|
| `_id, org_id, created_at, ...` | scalar metadata |
| `company` | `69eb95f22b0a508618923977` (ObjectId only — not expanded) |
| `deal` | `69ebb7222b0a508618923c06` (ObjectId only — not expanded) |
| `type` | `meeting` |
| `scope` | `external` |
| `date, duration` | scalars |
| `participants_contacts` | `[<walker_id>, <heather_id>]` (ObjectIds only — not expanded) |
| `participants_employees` | `[<kyle_id>]` (ObjectId only — not expanded) |
| `summary` | our one-paragraph prose |
| `status` | `logged` |
| **`_related`** | **`[]` (EMPTY)** |

The agent has no Meeting reference. No Email reference. No transcript. No way to find the source content from the Touchpoint alone.

## Why `_related` is empty

**By entity design (correctly):** Source entities (Email, Meeting) point TO Touchpoint via a `touchpoint` field. Touchpoint has no reverse pointer back to its sources. The original design rationale (from `2026-04-22-entity-model-brainstorm.md`): *"Raw data links TO Interaction: Email has `interaction` field. Meeting has `interaction` field. The Interaction doesn't have source fields — sources point to it. This scales naturally as we add raw data entities."*

**The scaling argument is real** (new source types don't require Touchpoint schema changes). **But it creates an information-access asymmetry.**

**The kernel's `--include-related` behavior:** follows forward references on the entity itself (fields where `is_relationship: true`). For a Touchpoint, those are `company` and `deal` — which it returned. It does NOT follow reverse references (entities that point TO this Touchpoint). Meeting.touchpoint → Touchpoint is a reverse reference and is invisible to `--include-related`.

So the agent gets `company` and `deal` object IDs (expanded at depth 2 if configured) and nothing else. The actual content it's supposed to analyze — the Meeting transcript — is unreachable from the starting context.

## The skill doesn't bridge the gap

`intelligence-extractor` skill text:

> "For meeting Touchpoints: read the linked Meeting transcript and notes"

But the skill gives **no recipe** for how to find the Meeting from the Touchpoint. It assumes the agent can navigate `Touchpoint → Meeting`, but there's no such navigation path:
- No field on Touchpoint pointing to Meeting
- No CLI pattern in the skill for reverse lookup
- `indemn meeting list --filter` doesn't exist (the agent tried it and failed)
- The actual working CLI (`indemn meeting list --data '{"touchpoint": "<id>"}'`) is not taught anywhere in the skill

The agent is essentially told "read the linked Meeting" without being given the address.

## Why the agent drifted

Given an impossible task, the agent did what agents do — improvise toward the goal. It started listing Companies (perhaps trying to understand the space), hit a `--filter` option it assumed existed (which didn't), got a too-large list, tried to grep for "INDEM" (maybe trying to find context about Indemn or the company), and the grep matched a **cached tool result from a previous invocation** containing the Apr 17 Nick/FoxQuilt transcript. Completely unrelated to GR Little, but now the agent had a transcript in front of it. It couldn't use it. It gave up.

## Secondary issues discovered along the way

1. **Runtime tool-result cache leaks across agent invocations.** The grep matched content from a prior agent's cached results (`/large_tool_results/3bc0edc5-...`). This is a serious cross-task isolation problem — an agent processing one entity can be influenced by content an earlier agent pulled for something unrelated. Needs separate investigation in the harness (`harness_common/backend.py` probably).

2. **Silent workflow stuck-state.** The agent "completed" with zero output and no error, but the Temporal workflow never transitioned the message to `completed` or `failed`. The message sat in `processing` with `last_error: null` — indistinguishable from a genuinely-in-flight message. Visibility timeout was 5 minutes, so it would eventually requeue and retry the same broken flow indefinitely (up to `max_attempts`). This is a critical reliability bug — agents that run-but-produce-nothing should be detected and marked failed.

3. **`indemn company list --filter` doesn't exist.** The agent assumed a reasonable-looking filter option. The CLI doesn't have it. No hint in `--help` about how to actually filter other than `--status` / `--search`. This is both a CLI UX gap and a signal that our generated entity skill (`indemn skill get Company`) isn't teaching the agent the filter pattern.

## The fix options (by cost and correctness)

**Option A — Teach the reverse-lookup in the skill (cheapest, treats symptom):**

Add explicit instructions in the Intelligence Extractor skill:

> "Your Touchpoint does not contain the source content directly. To get the content:
> - For `type: meeting` Touchpoints: `indemn meeting list --data '{"touchpoint": "<touchpoint_id>"}'` → returns the Meeting, then read `transcript` and `summary`.
> - For `type: email` Touchpoints: `indemn email list --data '{"touchpoint": "<touchpoint_id>"}'` → returns the Emails in this thread, read their `body` and `subject`."

Plus fix the generated entity skill so it teaches the `--data` filter pattern (not `--filter`). Plus verify `list --data '{...}'` filter actually works on these fields.

Pros: immediate, no schema change.
Cons: every associate that needs upstream navigation has to teach itself. Doesn't generalize. Fragile as we add new source types.

**Option B — Add forward source pointer on Touchpoint (schema change, localised):**

Add `source_entity_type: str` and `source_entity_id: objectid` fields to Touchpoint. Touchpoint Synthesizer populates these when creating the Touchpoint. Then:

```bash
indemn touchpoint get <id>   # returns source_entity_type=meeting, source_entity_id=<meeting_id>
indemn meeting get <meeting_id>   # read transcript
```

Pros: information-access symmetry. Each Touchpoint carries its provenance forward. Works for any new source type. No reverse-lookup tooling needed.
Cons: denormalization (Meeting.touchpoint also exists). Must stay in sync. Minor schema addition.

**Option C — Make `--include-related` follow reverse relationships (kernel change, general):**

Kernel enhancement: when `--include-related` is invoked, also find entities that reference this one (fields where `is_relationship: true` and `relationship_target: <this entity type>`). For Touchpoint, this would include Meetings (because Meeting.touchpoint → Touchpoint), Emails (Email.touchpoint → Touchpoint), etc.

Pros: correct, general, works for any entity with reverse references. Self-describing — the entity definition already has the info.
Cons: biggest change. Needs careful index coverage to avoid full-collection scans. Needs opt-in control (don't always return all back-refs; scope by some config).

## Recommendation

**Option A is NOT sufficient on its own (tested)** — the list endpoint doesn't support arbitrary field filters. `indemn meeting list --data '{"touchpoint": "<id>"}'` fails: the CLI command has no `--data` option, and the underlying API route only accepts `status` / `search` / `limit` / `offset` / `sort`. Teaching the skill a reverse-lookup recipe requires first adding arbitrary-field filtering to both the API list endpoint and the CLI `list` command. That's multiple kernel surfaces to change.

**Option B is the minimum correct fix.** Add `source_entity_type: str` and `source_entity_id: objectid` fields to Touchpoint. Touchpoint Synthesizer populates them on create. Extractor calls `indemn meeting get <source_entity_id>` directly — no reverse lookup needed, no new kernel machinery. Denormalization cost is small (Meeting.touchpoint remains, source pointer is new); keeping them in sync is Synth's responsibility at create time and shouldn't change.

**Option C is the right long-term platform fix** but it's a kernel feature (make `--include-related` follow reverse relationships with proper scoping/limits). It's not the fastest path to an unblocked extractor.

## Recommendation — go with Option B

Add source pointers on Touchpoint, update the Synthesizer, teach the Extractor skill `indemn meeting get <touchpoint.source_entity_id>`. This is a self-contained fix that closes the information gap for the pipeline we actually have, and it sets up the Artifact Generator associate (future) for the same clean pattern.

Noted separately for follow-up:
- Kernel bug: `--include-related` claims to include related entities but returns empty for reverse references. Either fix the behavior or rename the option to something that accurately describes "forward only."
- List-endpoint gap: arbitrary field filters are not supported. This will bite any associate that needs to query by non-standard fields. Should be an OS feature.
- Runtime cross-invocation cache leak: a bug in the harness backend that affects ALL agents, not just this one.
- Silent workflow stuck-state: agents that complete with no output don't mark their message failed. Any future reliability work on the pipeline must address this.

## What this means for the GR Little trace today

For the two-hour demo window, we do option A for this one agent run (either by updating the skill and re-dispatching, or by me acting as the agent with the correct navigation). Either way, the observation stays captured here so the pattern gets fixed properly later.

This is the kind of finding the one-meeting trace was supposed to surface. It did.
