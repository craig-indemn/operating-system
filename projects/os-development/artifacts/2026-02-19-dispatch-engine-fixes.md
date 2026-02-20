---
ask: "Fix the dispatch engine bugs and get end-to-end test passing — anyio cancel scope crash, rate_limit_event parsing, dependency resolution, and agent configuration"
created: 2026-02-19
workstream: os-development
session: 2026-02-19-c
sources:
  - type: github
    description: "SDK Issue #583 — MessageParseError on rate_limit_event crashes receive_messages() generator"
    ref: "https://github.com/anthropics/claude-agent-sdk-python/issues/583"
  - type: web
    description: "Claude Agent SDK Python reference — ClaudeAgentOptions, PermissionMode, model selection"
  - type: web
    description: "Claude Agent SDK overview — query() lifecycle, sequential calls, subscription auth"
---

# Dispatch Engine Fixes — Session 2026-02-19-c

## Summary

Fixed three bugs in `systems/dispatch/engine.py` that prevented the dispatch system from completing an end-to-end run. Also upgraded the SDK to v0.1.39, configured agent sessions per user preferences, and updated the beads skill documentation with discovered gotchas.

**End result:** 2/2 test tasks passed autonomously. Full ralph loop confirmed working.

## Bugs Fixed

### 1. Anyio Cancel Scope Crash (sequential `query()` calls)

**Symptom:** First SDK `query()` call succeeds, second crashes with `RuntimeError: Attempted to exit cancel scope in a different task than it was entered in`.

**Root cause:** The `query()` function returns an async generator backed by an anyio task group. When iteration completes, Python's async generator protocol does NOT automatically call `aclose()` — the task group's cancel scope leaks and interferes with the next `query()` call.

**Fix:** Wrap every `query()` call in `contextlib.aclosing()`:

```python
from contextlib import aclosing

async with aclosing(query(prompt=prompt, options=options)) as messages:
    async for message in messages:
        ...
```

This guarantees `aclose()` runs on exit, properly tearing down the task group before the next query starts.

### 2. `rate_limit_event` Kills SDK Stream

**Symptom:** Verification sessions consistently fail with "Could not parse verification result from output" — the session produces no text output.

**Root cause:** The Claude Code CLI emits `rate_limit_event` messages in its JSON stream. The SDK's `parse_message()` function doesn't recognize this type and throws `MessageParseError`. Because the exception occurs inside a generator's `yield` expression (`yield parse_message(data)` in `client.py`), it terminates the generator entirely per Python spec. No further messages can be received.

**Known issue:** [anthropics/claude-agent-sdk-python#583](https://github.com/anthropics/claude-agent-sdk-python/issues/583) (open as of 2026-02-19).

**Fix:** Monkey-patch `parse_message` at import time to return `None` for unknown message types instead of throwing:

```python
import claude_agent_sdk._internal.message_parser as _mp
import claude_agent_sdk._internal.client as _client
_original_parse = _mp.parse_message

def _tolerant_parse(data):
    try:
        return _original_parse(data)
    except Exception as e:
        if "Unknown message type" in str(e):
            return None
        raise

_mp.parse_message = _tolerant_parse
_client.parse_message = _tolerant_parse
```

Consumer filters `None` messages: `if message is None: continue`.

**Note:** Remove this monkey-patch when SDK Issue #583 is resolved upstream.

### 3. `bd children` Excludes Closed Tasks

**Symptom:** After task 1 passes and is closed, task 2 (which depends on task 1) is never unblocked. Engine reports "No ready tasks (blocked by dependencies)."

**Root cause:** `bd children <epic-id>` only returns **open** children. Closed tasks are excluded from the output. The engine's `get_ready_children()` builds a `closed_ids` set from the children list — but since closed tasks aren't returned, `closed_ids` is always empty, so no dependencies are ever considered satisfied.

**Fix:** Switched from `bd children` to `bd list --parent <epic-id> --all`, which returns all children including closed ones.

## Additional Improvements

### Verification Retry Loop

Verification sessions sometimes produce unparseable output (rate_limit_event can still disrupt timing). Added a retry loop — up to 3 verification attempts per task before counting it as a failure.

### Max Retry Enforcement

The `MAX_RETRIES_PER_TASK` constant wasn't being enforced — the loop kept picking the same task. Fixed by filtering exhausted tasks out of the ready list before selection.

### SDK Upgrade

Updated `claude-agent-sdk` from v0.1.38 to v0.1.39 (added `rate_limit` as recognized `AssistantMessageError` type, though the `rate_limit_event` message type parser bug persists).

## Agent Configuration (decided with user)

| Setting | Value | Rationale |
|---------|-------|-----------|
| `permission_mode` | `bypassPermissions` | Fully autonomous — no prompts during dispatch |
| `model` | `opus` | Maximum capability for implementation tasks |
| `setting_sources` | `["user", "project"]` | Full OS framework — skills, CLAUDE.md, conventions |
| `add_dirs` | `[operating-system/]` | Access to OS context files from target repo |
| `system_prompt` | preset `claude_code` + task context | Standard Claude Code behavior + dispatch instructions |
| `allowed_tools` | not set (bypassPermissions grants all) | No restrictions |
| `max_turns` / `max_budget_usd` | not set | No hard limits — `MAX_RETRIES_PER_TASK=3` is the circuit breaker |

Verification sessions use the same `bypassPermissions` + `opus` config (can read AND write, enabling auto-fixes).

## Test Results

**Epic:** `os-development-26e` (2 children, target: `/tmp/test-dispatch-repo`)

```
Iteration 1: Create hello.txt  → implement ($0.16) → verify → PASSED → committed
Iteration 2: Create goodbye.txt → implement ($0.06) → verify → PASSED → committed
Iteration 3: All tasks passed!

Results: 2/2 tasks passed, 0 failed
```

- Dependencies respected (task 2 waited for task 1)
- Learnings accumulated across tasks
- Git commits clean in target repo
- Beads statuses updated correctly

## Beads Skill Updates

Added **Gotchas** section to `.claude/skills/beads/SKILL.md`:
- `bd children` only returns open children — use `bd list --parent --all` for complete picture
- `--repo` flag routes to a different beads database, not metadata — use `--notes "target_repo: /path"`

Fixed stale `--repo` references in dispatch flow and conventions sections.

## Files Modified

| File | Changes |
|------|---------|
| `systems/dispatch/engine.py` | All three bug fixes, agent config, SDK monkey-patch, retry logic |
| `.claude/skills/beads/SKILL.md` | Gotchas section, fixed `--repo` references, added `bd list --parent --all` |
| `projects/os-development/INDEX.md` | Updated status, new decisions, resolved open questions |
