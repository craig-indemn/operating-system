# EA & Session Management Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the session management system (CLI, hooks, state files) and EA skill so Craig can create, monitor, and manage Claude Code sessions across projects from a central switchboard.

**Architecture:** Four components built bottom-up: shared library (`lib/os_state.py`) → hook scripts → session CLI → EA skill. Each layer depends on the one below it. Two early verification steps validate assumptions about `--session-id` and the statusline hook format before building on them.

**Tech Stack:** Python 3.12 (stdlib only for hooks/lib), tmux, Claude Code CLI, git worktrees

**Design doc:** `projects/os-development/artifacts/2026-03-01-ea-session-management-design.md`
**Internals reference:** `projects/os-development/artifacts/2026-03-01-claude-code-internals.md`

---

### Task 0: Verify Assumptions

Two design assumptions need validation before we build on them. These are quick manual tests.

**Files:**
- None created yet

**Step 1: Verify `--session-id` flag**

Run from a terminal (not inside Claude Code):

```bash
TEST_UUID=$(python3 -c "import uuid; print(uuid.uuid4())")
echo "Test UUID: $TEST_UUID"
claude --session-id "$TEST_UUID" --print "Say hello and exit" --output-format json 2>/dev/null | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        msg = json.loads(line)
        if 'session_id' in msg:
            print(f'Session ID in output: {msg[\"session_id\"]}')
            break
    except: pass
"
# Check if transcript was created with our UUID
ls -la ~/.claude/projects/-Users-home-Repositories-operating-system/${TEST_UUID}.jsonl 2>/dev/null && echo "PASS: session-id honored" || echo "FAIL: session-id not honored"
```

Expected: PASS. If FAIL, the hook script must use `cwd`-based lookup instead of `session_id` matching. Document the result.

**Step 2: Verify statusline input format**

Create a temporary test script:

```bash
cat > /tmp/test-statusline.py << 'PYEOF'
import sys, json
data = json.loads(sys.stdin.read())
with open("/tmp/statusline-input.json", "w") as f:
    json.dump(data, f, indent=2)
# Pass through empty string so Claude Code doesn't break
print("")
PYEOF
```

Temporarily set statusLine in a test session to capture what Claude Code sends:
```json
{"statusLine": {"type": "command", "command": "python3 /tmp/test-statusline.py"}}
```

Run a brief Claude Code session, then inspect `/tmp/statusline-input.json`. Note:
- Does it have `session_id`?
- Does it have `context_window.remaining_percentage`?
- What other fields are available?

Document the actual input JSON structure. Clean up the test script and restore the original statusLine setting.

**Step 3: Document results**

Record verification results as comments at the top of `lib/os_state.py` (created in Task 1).

---

### Task 1: Shared Library — `lib/os_state.py`

The foundation. Atomic file operations and state file helpers used by everything else.

**Files:**
- Create: `lib/os_state.py`
- Create: `tests/test_os_state.py`

**Step 1: Write the tests**

```python
"""Tests for lib/os_state.py — session state file utilities."""
import json
import os
import tempfile
import unittest
from pathlib import Path

# Add lib to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from os_state import (
    atomic_write_json,
    read_state_file,
    find_state_by_session_id,
    find_state_by_name,
    append_event,
    now_iso,
)


class TestAtomicWriteJson(unittest.TestCase):
    def test_writes_valid_json(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "test.json")
            data = {"key": "value", "number": 42}
            atomic_write_json(path, data)
            with open(path) as f:
                result = json.load(f)
            self.assertEqual(result, data)

    def test_no_temp_file_left_behind(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "test.json")
            atomic_write_json(path, {"a": 1})
            files = os.listdir(d)
            self.assertEqual(files, ["test.json"])

    def test_overwrites_existing(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "test.json")
            atomic_write_json(path, {"version": 1})
            atomic_write_json(path, {"version": 2})
            with open(path) as f:
                result = json.load(f)
            self.assertEqual(result["version"], 2)


class TestReadStateFile(unittest.TestCase):
    def test_reads_valid_state(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "abc.json")
            data = {"version": 1, "session_id": "abc", "name": "test", "status": "active"}
            with open(path, "w") as f:
                json.dump(data, f)
            result = read_state_file(path)
            self.assertEqual(result["session_id"], "abc")

    def test_returns_none_for_missing(self):
        result = read_state_file("/nonexistent/path.json")
        self.assertIsNone(result)

    def test_returns_none_for_corrupt(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "bad.json")
            with open(path, "w") as f:
                f.write("not json{{{")
            result = read_state_file(path)
            self.assertIsNone(result)


class TestFindState(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.state1 = {
            "version": 1, "session_id": "uuid-111", "name": "voice-evals",
            "status": "active", "worktree_path": "/tmp/wt1"
        }
        self.state2 = {
            "version": 1, "session_id": "uuid-222", "name": "platform-dev",
            "status": "idle", "worktree_path": "/tmp/wt2"
        }
        for s in [self.state1, self.state2]:
            path = os.path.join(self.tmpdir, f"{s['session_id']}.json")
            with open(path, "w") as f:
                json.dump(s, f)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir)

    def test_find_by_session_id(self):
        result = find_state_by_session_id(self.tmpdir, "uuid-111")
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "voice-evals")

    def test_find_by_session_id_miss(self):
        result = find_state_by_session_id(self.tmpdir, "uuid-999")
        self.assertIsNone(result)

    def test_find_by_name(self):
        path, data = find_state_by_name(self.tmpdir, "platform-dev")
        self.assertIsNotNone(data)
        self.assertEqual(data["session_id"], "uuid-222")

    def test_find_by_name_miss(self):
        path, data = find_state_by_name(self.tmpdir, "nonexistent")
        self.assertIsNone(data)


class TestAppendEvent(unittest.TestCase):
    def test_appends_event(self):
        state = {"events": []}
        append_event(state, "started")
        self.assertEqual(len(state["events"]), 1)
        self.assertEqual(state["events"][0]["type"], "started")
        self.assertIn("at", state["events"][0])

    def test_caps_at_50(self):
        state = {"events": [{"type": "active", "at": "t"} for _ in range(50)]}
        append_event(state, "idle")
        self.assertEqual(len(state["events"]), 50)
        self.assertEqual(state["events"][-1]["type"], "idle")
        self.assertEqual(state["events"][0]["type"], "active")  # oldest dropped was index 0

    def test_includes_summary_if_provided(self):
        state = {"events": []}
        append_event(state, "task_completed", summary="Fixed the bug")
        self.assertEqual(state["events"][0]["summary"], "Fixed the bug")
```

**Step 2: Run tests to verify they fail**

```bash
cd /Users/home/Repositories/operating-system && python3 -m pytest tests/test_os_state.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'os_state'`

**Step 3: Write the implementation**

```python
"""Shared utilities for OS session state management.

STDLIB ONLY — this module is imported by hook scripts that run with system python3.
No third-party dependencies allowed.

Verification results from Task 0:
- --session-id: [TO BE FILLED AFTER VERIFICATION]
- statusline input: [TO BE FILLED AFTER VERIFICATION]
"""
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def now_iso() -> str:
    """Return current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def atomic_write_json(path: str, data: dict) -> None:
    """Write JSON to a file atomically (temp file + rename).

    Prevents corruption if two processes write simultaneously —
    the file is never half-written.
    """
    dir_path = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        os.rename(tmp_path, path)
    except Exception:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def read_state_file(path: str) -> Optional[dict]:
    """Read a session state JSON file. Returns None if missing or corrupt."""
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        return None


def find_state_by_session_id(sessions_dir: str, session_id: str) -> Optional[dict]:
    """Find a state file by session UUID. Returns the state dict or None.

    Fast path: try {session_id}.json directly (O(1)).
    Fallback: scan all files (O(n)) in case filename doesn't match.
    """
    # Fast path — file named by UUID
    direct_path = os.path.join(sessions_dir, f"{session_id}.json")
    state = read_state_file(direct_path)
    if state and state.get("session_id") == session_id:
        return state

    # Fallback — scan all files
    try:
        for fname in os.listdir(sessions_dir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(sessions_dir, fname)
            state = read_state_file(fpath)
            if state and state.get("session_id") == session_id:
                return state
    except FileNotFoundError:
        pass
    return None


def find_state_by_name(sessions_dir: str, name: str) -> tuple[Optional[str], Optional[dict]]:
    """Find a state file by session name. Returns (path, state) or (None, None)."""
    try:
        for fname in os.listdir(sessions_dir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(sessions_dir, fname)
            state = read_state_file(fpath)
            if state and state.get("name") == name:
                return fpath, state
    except FileNotFoundError:
        pass
    return None, None


def find_state_by_cwd(sessions_dir: str, cwd: str) -> tuple[Optional[str], Optional[dict]]:
    """Find a state file by matching cwd to worktree_path. Returns (path, state) or (None, None).

    Fallback lookup for when --session-id is not honored by Claude Code.
    """
    try:
        for fname in os.listdir(sessions_dir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(sessions_dir, fname)
            state = read_state_file(fpath)
            if state and state.get("worktree_path") == cwd:
                return fpath, state
    except FileNotFoundError:
        pass
    return None, None


def get_sessions_dir() -> str:
    """Get the sessions directory path from OS_ROOT env var or default."""
    os_root = os.environ.get("OS_ROOT", "/Users/home/Repositories/operating-system")
    return os.path.join(os_root, "sessions")


def append_event(state: dict, event_type: str, summary: str = None) -> None:
    """Append an event to the state's events array, capping at 50.

    Modifies state in place.
    """
    event: dict[str, Any] = {"type": event_type, "at": now_iso()}
    if summary:
        event["summary"] = summary
    events = state.setdefault("events", [])
    events.append(event)
    # Cap at 50 — drop oldest
    if len(events) > 50:
        state["events"] = events[-50:]
```

**Step 4: Run tests to verify they pass**

```bash
cd /Users/home/Repositories/operating-system && python3 -m pytest tests/test_os_state.py -v
```

Expected: All 10 tests PASS

**Step 5: Commit**

```bash
git add lib/os_state.py tests/test_os_state.py
git commit -m "feat(session-manager): add shared state utilities — atomic writes, state file lookup, event management"
```

---

### Task 2: Hook Script — `update-state.py`

The event-driven state updater. Fires on every session event, updates the session's state file.

**Files:**
- Create: `systems/session-manager/hooks/update-state.py`
- Create: `tests/test_update_state.py`

**Step 1: Write the tests**

```python
"""Tests for the update-state hook script."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# We test by invoking the script as a subprocess with JSON on stdin,
# since that's how Claude Code hooks work.

SCRIPT_PATH = str(Path(__file__).parent.parent / "systems" / "session-manager" / "hooks" / "update-state.py")


def run_hook(event_name: str, session_id: str, sessions_dir: str, cwd: str = "/tmp") -> int:
    """Run the hook script with mock event JSON on stdin."""
    hook_input = json.dumps({
        "session_id": session_id,
        "hook_event_name": event_name,
        "cwd": cwd,
        "transcript_path": f"/tmp/{session_id}.jsonl",
    })
    env = os.environ.copy()
    env["OS_ROOT"] = str(Path(sessions_dir).parent)  # sessions/ is under OS_ROOT
    result = subprocess.run(
        [sys.executable, SCRIPT_PATH],
        input=hook_input, capture_output=True, text=True, env=env, timeout=5,
    )
    return result.returncode


def write_state(sessions_dir: str, session_id: str, state: dict) -> str:
    """Write a state file and return its path."""
    path = os.path.join(sessions_dir, f"{session_id}.json")
    with open(path, "w") as f:
        json.dump(state, f)
    return path


class TestUpdateStateHook(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.sessions_dir = os.path.join(self.tmpdir, "sessions")
        os.makedirs(self.sessions_dir)
        self.session_id = "test-uuid-123"
        self.base_state = {
            "version": 1,
            "session_id": self.session_id,
            "name": "test-session",
            "status": "started",
            "last_activity": "2026-01-01T00:00:00+00:00",
            "events": [],
        }

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir)

    def _read_state(self) -> dict:
        path = os.path.join(self.sessions_dir, f"{self.session_id}.json")
        with open(path) as f:
            return json.load(f)

    def test_session_start_sets_active(self):
        write_state(self.sessions_dir, self.session_id, self.base_state)
        rc = run_hook("SessionStart", self.session_id, self.sessions_dir)
        self.assertEqual(rc, 0)
        state = self._read_state()
        self.assertEqual(state["status"], "active")
        self.assertEqual(state["events"][-1]["type"], "active")

    def test_stop_sets_idle(self):
        self.base_state["status"] = "active"
        write_state(self.sessions_dir, self.session_id, self.base_state)
        rc = run_hook("Stop", self.session_id, self.sessions_dir)
        self.assertEqual(rc, 0)
        state = self._read_state()
        self.assertEqual(state["status"], "idle")
        self.assertEqual(state["events"][-1]["type"], "idle")

    def test_user_prompt_submit_sets_active(self):
        self.base_state["status"] = "idle"
        write_state(self.sessions_dir, self.session_id, self.base_state)
        rc = run_hook("UserPromptSubmit", self.session_id, self.sessions_dir)
        self.assertEqual(rc, 0)
        state = self._read_state()
        self.assertEqual(state["status"], "active")

    def test_session_end_sets_ended(self):
        write_state(self.sessions_dir, self.session_id, self.base_state)
        rc = run_hook("SessionEnd", self.session_id, self.sessions_dir)
        self.assertEqual(rc, 0)
        state = self._read_state()
        self.assertEqual(state["status"], "ended")

    def test_session_end_preserves_ended_dirty(self):
        self.base_state["status"] = "ended_dirty"
        write_state(self.sessions_dir, self.session_id, self.base_state)
        rc = run_hook("SessionEnd", self.session_id, self.sessions_dir)
        self.assertEqual(rc, 0)
        state = self._read_state()
        self.assertEqual(state["status"], "ended_dirty")

    def test_task_completed_appends_event(self):
        write_state(self.sessions_dir, self.session_id, self.base_state)
        rc = run_hook("TaskCompleted", self.session_id, self.sessions_dir)
        self.assertEqual(rc, 0)
        state = self._read_state()
        self.assertEqual(state["events"][-1]["type"], "task_completed")

    def test_unknown_session_exits_silently(self):
        # No state file exists for this session
        rc = run_hook("Stop", "nonexistent-uuid", self.sessions_dir)
        self.assertEqual(rc, 0)  # Should exit 0, not crash

    def test_updates_last_activity(self):
        write_state(self.sessions_dir, self.session_id, self.base_state)
        rc = run_hook("Stop", self.session_id, self.sessions_dir)
        self.assertEqual(rc, 0)
        state = self._read_state()
        self.assertNotEqual(state["last_activity"], "2026-01-01T00:00:00+00:00")
```

**Step 2: Run tests to verify they fail**

```bash
cd /Users/home/Repositories/operating-system && python3 -m pytest tests/test_update_state.py -v
```

Expected: FAIL — script doesn't exist yet

**Step 3: Create directory structure and write the hook script**

```bash
mkdir -p systems/session-manager/hooks
```

```python
#!/usr/bin/env python3
"""Hook script for updating session state files.

Called by Claude Code hooks (SessionStart, Stop, UserPromptSubmit,
TaskCompleted, SessionEnd). Receives JSON on stdin with session_id,
hook_event_name, cwd, transcript_path.

STDLIB ONLY — runs with system python3, not venv.
Target execution time: <100ms.
"""
import json
import os
import sys

# Add lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib"))
from os_state import (
    atomic_write_json,
    append_event,
    find_state_by_session_id,
    find_state_by_cwd,
    get_sessions_dir,
    now_iso,
    read_state_file,
)


def main():
    # Read hook input from stdin
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        return  # Bad input, exit silently

    session_id = hook_input.get("session_id", "")
    event_name = hook_input.get("hook_event_name", "")
    cwd = hook_input.get("cwd", "")

    sessions_dir = get_sessions_dir()
    if not os.path.isdir(sessions_dir):
        return  # No sessions directory, nothing to update

    # Find the state file for this session
    # Primary: by session_id (fast path — direct filename lookup)
    state_path = os.path.join(sessions_dir, f"{session_id}.json")
    state = read_state_file(state_path)

    # Fallback: by cwd matching worktree_path
    if state is None or state.get("session_id") != session_id:
        state_path_found, state = find_state_by_cwd(sessions_dir, cwd)
        if state is None:
            return  # Not a managed session, exit silently
        state_path = state_path_found

    # Update based on event
    if event_name == "SessionStart":
        state["status"] = "active"
        append_event(state, "active")

    elif event_name == "Stop":
        state["status"] = "idle"
        append_event(state, "idle")

    elif event_name == "UserPromptSubmit":
        state["status"] = "active"
        append_event(state, "active")

    elif event_name == "TaskCompleted":
        append_event(state, "task_completed")

    elif event_name == "SessionEnd":
        if state.get("status") != "ended_dirty":
            state["status"] = "ended"
        append_event(state, state["status"])

    else:
        return  # Unknown event, skip

    # Update last_activity
    state["last_activity"] = now_iso()

    # Write atomically
    atomic_write_json(state_path, state)


if __name__ == "__main__":
    main()
```

**Step 4: Run tests to verify they pass**

```bash
cd /Users/home/Repositories/operating-system && python3 -m pytest tests/test_update_state.py -v
```

Expected: All 8 tests PASS

**Step 5: Commit**

```bash
git add systems/session-manager/hooks/update-state.py tests/test_update_state.py
git commit -m "feat(session-manager): add update-state hook script — event-driven state file updates"
```

---

### Task 3: Context Tracking Hook — `update-context.py`

Wraps the GSD statusline and adds context window tracking to state files.

**Files:**
- Create: `systems/session-manager/hooks/update-context.py`
- Create: `tests/test_update_context.py`

**Step 1: Write the tests**

```python
"""Tests for the update-context statusline hook."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = str(Path(__file__).parent.parent / "systems" / "session-manager" / "hooks" / "update-context.py")


def run_context_hook(stdin_data: dict, sessions_dir: str, gsd_script: str = None) -> tuple[int, str]:
    """Run the context hook with mock statusline JSON. Returns (returncode, stdout)."""
    env = os.environ.copy()
    env["OS_ROOT"] = str(Path(sessions_dir).parent)
    if gsd_script:
        env["GSD_STATUSLINE_SCRIPT"] = gsd_script
    else:
        env["GSD_STATUSLINE_SCRIPT"] = ""  # Disable GSD for testing
    result = subprocess.run(
        [sys.executable, SCRIPT_PATH],
        input=json.dumps(stdin_data), capture_output=True, text=True, env=env, timeout=5,
    )
    return result.returncode, result.stdout


class TestUpdateContext(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.sessions_dir = os.path.join(self.tmpdir, "sessions")
        os.makedirs(self.sessions_dir)
        self.session_id = "ctx-test-uuid"
        self.state = {
            "version": 1,
            "session_id": self.session_id,
            "name": "test",
            "status": "active",
            "context_remaining_pct": 100,
            "worktree_path": "/tmp/wt-test",
            "events": [],
        }
        path = os.path.join(self.sessions_dir, f"{self.session_id}.json")
        with open(path, "w") as f:
            json.dump(self.state, f)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir)

    def _read_state(self) -> dict:
        path = os.path.join(self.sessions_dir, f"{self.session_id}.json")
        with open(path) as f:
            return json.load(f)

    def test_updates_context_pct(self):
        stdin = {
            "session_id": self.session_id,
            "context_window": {"remaining_percentage": 65.5},
        }
        rc, _ = run_context_hook(stdin, self.sessions_dir)
        self.assertEqual(rc, 0)
        state = self._read_state()
        self.assertEqual(state["context_remaining_pct"], 65)

    def test_context_low_event_at_10_pct(self):
        stdin = {
            "session_id": self.session_id,
            "context_window": {"remaining_percentage": 8.2},
        }
        rc, _ = run_context_hook(stdin, self.sessions_dir)
        self.assertEqual(rc, 0)
        state = self._read_state()
        self.assertEqual(state["context_remaining_pct"], 8)
        self.assertEqual(state["events"][-1]["type"], "context_low")

    def test_no_duplicate_context_low(self):
        self.state["status"] = "context_low"
        self.state["events"] = [{"type": "context_low", "at": "t"}]
        path = os.path.join(self.sessions_dir, f"{self.session_id}.json")
        with open(path, "w") as f:
            json.dump(self.state, f)

        stdin = {
            "session_id": self.session_id,
            "context_window": {"remaining_percentage": 5.0},
        }
        rc, _ = run_context_hook(stdin, self.sessions_dir)
        self.assertEqual(rc, 0)
        state = self._read_state()
        # Should not add another context_low event
        context_low_events = [e for e in state["events"] if e["type"] == "context_low"]
        self.assertEqual(len(context_low_events), 1)

    def test_unknown_session_exits_silently(self):
        stdin = {
            "session_id": "nonexistent",
            "context_window": {"remaining_percentage": 50.0},
        }
        rc, _ = run_context_hook(stdin, self.sessions_dir)
        self.assertEqual(rc, 0)

    def test_produces_output(self):
        """The script must produce some output for the statusline display."""
        stdin = {
            "session_id": self.session_id,
            "context_window": {"remaining_percentage": 50.0},
        }
        rc, stdout = run_context_hook(stdin, self.sessions_dir)
        self.assertEqual(rc, 0)
        # Should produce at least some output (even if GSD is disabled)
        self.assertIsInstance(stdout, str)
```

**Step 2: Run tests to verify they fail**

```bash
cd /Users/home/Repositories/operating-system && python3 -m pytest tests/test_update_context.py -v
```

Expected: FAIL — script doesn't exist

**Step 3: Write the implementation**

```python
#!/usr/bin/env python3
"""StatusLine hook that wraps GSD statusline and tracks context window usage.

Reads JSON from stdin (Claude Code statusline format), updates session state
file with context_remaining_pct, emits context_low event at 10%, then passes
through GSD statusline output.

STDLIB ONLY — runs with system python3, not venv.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib"))
from os_state import (
    atomic_write_json,
    append_event,
    find_state_by_session_id,
    find_state_by_cwd,
    get_sessions_dir,
    read_state_file,
)

CONTEXT_LOW_THRESHOLD = 10  # percent


def main():
    # Read statusline input
    try:
        raw_input = sys.stdin.read()
        data = json.loads(raw_input)
    except (json.JSONDecodeError, EOFError):
        print("")
        return

    session_id = data.get("session_id", "")
    context_window = data.get("context_window", {})
    remaining_pct = context_window.get("remaining_percentage")

    # Update session state file if we have context data
    if remaining_pct is not None:
        sessions_dir = get_sessions_dir()
        if os.path.isdir(sessions_dir):
            # Find state file
            state_path = os.path.join(sessions_dir, f"{session_id}.json")
            state = read_state_file(state_path)

            if state is None or state.get("session_id") != session_id:
                cwd = data.get("cwd", "")
                found_path, state = find_state_by_cwd(sessions_dir, cwd)
                if state is not None:
                    state_path = found_path

            if state is not None:
                state["context_remaining_pct"] = int(remaining_pct)

                # Emit context_low event at threshold (only once)
                if remaining_pct < CONTEXT_LOW_THRESHOLD:
                    if state.get("status") != "context_low":
                        state["status"] = "context_low"
                        append_event(state, "context_low")

                atomic_write_json(state_path, state)

    # Forward to GSD statusline
    gsd_script = os.environ.get(
        "GSD_STATUSLINE_SCRIPT",
        os.path.expanduser("~/.claude/hooks/gsd-statusline.js"),
    )

    if gsd_script and os.path.isfile(gsd_script):
        try:
            result = subprocess.run(
                ["node", gsd_script],
                input=raw_input, capture_output=True, text=True, timeout=5,
            )
            print(result.stdout, end="")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("")
    else:
        # Minimal fallback statusline
        print("")


if __name__ == "__main__":
    main()
```

**Step 4: Run tests to verify they pass**

```bash
cd /Users/home/Repositories/operating-system && python3 -m pytest tests/test_update_context.py -v
```

Expected: All 5 tests PASS

**Step 5: Commit**

```bash
git add systems/session-manager/hooks/update-context.py tests/test_update_context.py
git commit -m "feat(session-manager): add context-tracking statusline hook — wraps GSD, tracks context window"
```

---

### Task 4: Session CLI — `cli.py`

The main interface for creating, listing, attaching, and closing sessions.

**Files:**
- Create: `systems/session-manager/cli.py`
- Create: `systems/session-manager/SYSTEM.md`
- Create: `tests/test_session_cli.py`

**Step 1: Write the SYSTEM.md**

```markdown
# Session Manager

Manages Claude Code sessions running in tmux, each scoped to a project in the OS repo. Creates worktrees for isolation, tracks session state via hooks, and provides a CLI for lifecycle management.

## Capabilities

- Create new Claude Code sessions in tmux with git worktree isolation
- List all active sessions with status, context usage, and project info
- Attach to sessions for direct interaction
- Send commands to sessions via tmux send-keys
- Close sessions with defensive cleanup (commit, push, update INDEX.md)
- Force-destroy unresponsive sessions

## Skills

| Skill | Purpose |
|-------|---------|
| `/ea` | Intelligence layer — uses session CLI for orchestration |

## State

- **Session state files** — `sessions/{uuid}.json`, one per active session. Written by CLI at creation, updated by hooks during session life.
- **Hooks** — `update-state.py` (event tracking) and `update-context.py` (context window tracking) fire globally for all Claude Code sessions.

## Dependencies

- tmux — session multiplexer
- Claude Code CLI — `~/.local/bin/claude`
- Python 3.12+ (stdlib only for hooks, venv OK for CLI)
- Git — worktree management
- `lib/os_state.py` — shared utilities

## Integration Points

- **Reads from:** session state files, project INDEX.md
- **Produces:** tmux sessions running Claude Code, session state files
- **Reports to:** EA skill reads state files for briefings
```

**Step 2: Write CLI tests**

```python
"""Tests for the session CLI.

These test the CLI's Python functions directly, not via subprocess,
because the CLI interacts with tmux and claude which we mock.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "systems" / "session-manager"))
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))


class TestSessionCreate(unittest.TestCase):
    """Test the create command's state file writing and argument assembly."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.sessions_dir = os.path.join(self.tmpdir, "sessions")
        os.makedirs(self.sessions_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir)

    def test_build_claude_command(self):
        from cli import build_claude_command
        cmd = build_claude_command(
            session_id="test-uuid",
            model="opus",
            permission_mode="bypassPermissions",
            add_dirs=["/repos/bot-service"],
        )
        self.assertIn("--session-id", cmd)
        self.assertIn("test-uuid", cmd)
        self.assertIn("--model", cmd)
        self.assertIn("opus", cmd)
        self.assertIn("--dangerously-skip-permissions", cmd)
        self.assertIn("--add-dir", cmd)
        self.assertIn("/repos/bot-service", cmd)

    def test_build_claude_command_accept_edits(self):
        from cli import build_claude_command
        cmd = build_claude_command(
            session_id="test-uuid",
            model="sonnet",
            permission_mode="acceptEdits",
            add_dirs=[],
        )
        self.assertIn("--permission-mode", cmd)
        self.assertIn("acceptEdits", cmd)
        self.assertNotIn("--dangerously-skip-permissions", cmd)

    def test_create_initial_state(self):
        from cli import create_initial_state
        state = create_initial_state(
            session_id="test-uuid",
            name="voice-evals",
            project="voice-evaluations",
            worktree_path="/tmp/wt",
            tmux_session="os-voice-evals",
            model="opus",
            permission_mode="bypassPermissions",
            add_dirs=["/repos/bot-service"],
        )
        self.assertEqual(state["version"], 1)
        self.assertEqual(state["session_id"], "test-uuid")
        self.assertEqual(state["name"], "voice-evals")
        self.assertEqual(state["status"], "started")
        self.assertEqual(state["context_remaining_pct"], 100)
        self.assertEqual(state["additional_dirs"], ["/repos/bot-service"])
        self.assertEqual(len(state["events"]), 1)
        self.assertEqual(state["events"][0]["type"], "started")


class TestSessionList(unittest.TestCase):
    """Test the list command's state file reading and formatting."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.sessions_dir = os.path.join(self.tmpdir, "sessions")
        os.makedirs(self.sessions_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir)

    def test_list_active_sessions(self):
        from cli import list_sessions
        # Write two state files
        for name, status in [("voice-evals", "active"), ("platform", "idle")]:
            state = {
                "version": 1, "session_id": f"uuid-{name}", "name": name,
                "status": status, "project": name, "context_remaining_pct": 50,
                "last_activity": "2026-03-01T10:00:00+00:00",
                "model": "opus", "events": [],
            }
            with open(os.path.join(self.sessions_dir, f"uuid-{name}.json"), "w") as f:
                json.dump(state, f)

        sessions = list_sessions(self.sessions_dir)
        self.assertEqual(len(sessions), 2)
        names = {s["name"] for s in sessions}
        self.assertEqual(names, {"voice-evals", "platform"})

    def test_list_excludes_ended(self):
        from cli import list_sessions
        state = {
            "version": 1, "session_id": "uuid-done", "name": "done",
            "status": "ended", "project": "done", "context_remaining_pct": 0,
            "last_activity": "2026-03-01T10:00:00+00:00",
            "model": "opus", "events": [],
        }
        with open(os.path.join(self.sessions_dir, "uuid-done.json"), "w") as f:
            json.dump(state, f)

        sessions = list_sessions(self.sessions_dir)
        self.assertEqual(len(sessions), 0)
```

**Step 3: Run tests to verify they fail**

```bash
cd /Users/home/Repositories/operating-system && python3 -m pytest tests/test_session_cli.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'cli'`

**Step 4: Write the CLI implementation**

The CLI is a single Python file with `argparse` for command dispatch. Full implementation with all 7 commands: `create`, `list`, `attach`, `send`, `status`, `close`, `destroy`.

Create `systems/session-manager/cli.py`:

```python
#!/usr/bin/env python3
"""Session manager CLI for the Indemn Operating System.

Usage: session <command> [args]

Commands:
    create <name>    Create a new session with worktree + tmux
    list             List all active sessions
    attach <name>    Attach to a session's tmux pane
    send <name> msg  Send a message to a session via tmux send-keys
    status <name>    Show detailed session state
    close <name>     Gracefully close a session with cleanup
    destroy <name>   Force-kill a session
"""
import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lib"))
from os_state import (
    atomic_write_json,
    append_event,
    find_state_by_name,
    get_sessions_dir,
    now_iso,
    read_state_file,
)

OS_ROOT = os.environ.get("OS_ROOT", "/Users/home/Repositories/operating-system")
TMUX_PREFIX = "os-"
CLAUDE_BIN = os.path.expanduser("~/.local/bin/claude")


def create_initial_state(
    session_id: str,
    name: str,
    project: str,
    worktree_path: str,
    tmux_session: str,
    model: str,
    permission_mode: str,
    add_dirs: list[str],
) -> dict:
    """Create the initial session state dict."""
    now = now_iso()
    return {
        "version": 1,
        "session_id": session_id,
        "name": name,
        "project": project,
        "worktree_path": worktree_path,
        "tmux_session": tmux_session,
        "status": "started",
        "additional_dirs": add_dirs,
        "permissions": {"mode": permission_mode},
        "model": model,
        "created_at": now,
        "last_activity": now,
        "context_remaining_pct": 100,
        "git_branch": f"os-{name}",
        "events": [{"type": "started", "at": now}],
    }


def build_claude_command(
    session_id: str,
    model: str,
    permission_mode: str,
    add_dirs: list[str],
) -> str:
    """Build the claude CLI command string."""
    parts = [CLAUDE_BIN, f"--session-id {session_id}", f"--model {model}"]

    if permission_mode == "bypassPermissions":
        parts.append("--dangerously-skip-permissions")
    else:
        parts.append(f"--permission-mode {permission_mode}")

    for d in add_dirs:
        parts.append(f"--add-dir {d}")

    return " ".join(parts)


def list_sessions(sessions_dir: str, include_ended: bool = False) -> list[dict]:
    """List all sessions, optionally including ended ones."""
    sessions = []
    if not os.path.isdir(sessions_dir):
        return sessions
    for fname in sorted(os.listdir(sessions_dir)):
        if not fname.endswith(".json"):
            continue
        state = read_state_file(os.path.join(sessions_dir, fname))
        if state is None:
            continue
        if not include_ended and state.get("status") in ("ended", "ended_dirty"):
            continue
        sessions.append(state)
    return sessions


def tmux_session_exists(name: str) -> bool:
    """Check if a tmux session exists."""
    result = subprocess.run(
        ["tmux", "has-session", "-t", name],
        capture_output=True, timeout=5,
    )
    return result.returncode == 0


def cmd_create(args):
    """Create a new session."""
    name = args.name
    project = args.project or name
    model = args.model
    permission_mode = args.permissions
    add_dirs = args.add_dir or []
    tmux_name = f"{TMUX_PREFIX}{name}"
    sessions_dir = get_sessions_dir()

    # Check for existing session with same name
    _, existing = find_state_by_name(sessions_dir, name)
    if existing and existing.get("status") not in ("ended", "ended_dirty"):
        print(f"Error: session '{name}' already exists (status: {existing['status']})")
        sys.exit(1)

    # Check for existing tmux session
    if tmux_session_exists(tmux_name):
        print(f"Error: tmux session '{tmux_name}' already exists")
        sys.exit(1)

    # Create worktree
    worktree_path = os.path.join(OS_ROOT, ".claude", "worktrees", name)
    if not args.no_worktree:
        if os.path.exists(worktree_path):
            print(f"Worktree already exists at {worktree_path}, reusing it")
        else:
            branch = f"os-{name}"
            result = subprocess.run(
                ["git", "worktree", "add", worktree_path, "-b", branch],
                cwd=OS_ROOT, capture_output=True, text=True,
            )
            if result.returncode != 0:
                # Branch may already exist, try without -b
                result = subprocess.run(
                    ["git", "worktree", "add", worktree_path, branch],
                    cwd=OS_ROOT, capture_output=True, text=True,
                )
                if result.returncode != 0:
                    print(f"Error creating worktree: {result.stderr}")
                    sys.exit(1)
    else:
        worktree_path = OS_ROOT

    # Generate session ID and write state file
    session_id = str(uuid.uuid4())
    os.makedirs(sessions_dir, exist_ok=True)
    state = create_initial_state(
        session_id=session_id,
        name=name,
        project=project,
        worktree_path=worktree_path,
        tmux_session=tmux_name,
        model=model,
        permission_mode=permission_mode,
        add_dirs=add_dirs,
    )
    state_path = os.path.join(sessions_dir, f"{session_id}.json")
    atomic_write_json(state_path, state)

    # Create tmux session
    subprocess.run(
        ["tmux", "new-session", "-d", "-s", tmux_name, "-c", worktree_path],
        check=True, timeout=10,
    )

    # Launch Claude Code inside tmux
    claude_cmd = build_claude_command(session_id, model, permission_mode, add_dirs)
    subprocess.run(
        ["tmux", "send-keys", "-t", tmux_name, claude_cmd, "Enter"],
        check=True, timeout=10,
    )

    print(f"Session '{name}' created")
    print(f"  tmux: {tmux_name}")
    print(f"  worktree: {worktree_path}")
    print(f"  session_id: {session_id}")
    print(f"  model: {model}")
    print(f"  permissions: {permission_mode}")
    if add_dirs:
        print(f"  add_dirs: {', '.join(add_dirs)}")
    print(f"\nAttach: session attach {name}")


def cmd_list(args):
    """List all active sessions."""
    sessions = list_sessions(get_sessions_dir())
    if not sessions:
        print("No active sessions.")
        return

    # Header
    print(f"{'NAME':<25} {'STATUS':<15} {'CONTEXT':<10} {'MODEL':<8} {'PROJECT':<20}")
    print("-" * 78)

    for s in sessions:
        ctx = f"{s.get('context_remaining_pct', '?')}%"
        print(f"{s['name']:<25} {s['status']:<15} {ctx:<10} {s.get('model', '?'):<8} {s.get('project', '-'):<20}")


def cmd_attach(args):
    """Attach to a session's tmux pane."""
    name = args.name
    tmux_name = f"{TMUX_PREFIX}{name}"
    if not tmux_session_exists(tmux_name):
        print(f"Error: no tmux session '{tmux_name}'")
        sys.exit(1)
    os.execvp("tmux", ["tmux", "attach-session", "-t", tmux_name])


def cmd_send(args):
    """Send a message to a session via tmux send-keys."""
    name = args.name
    message = args.message
    tmux_name = f"{TMUX_PREFIX}{name}"
    if not tmux_session_exists(tmux_name):
        print(f"Error: no tmux session '{tmux_name}'")
        sys.exit(1)
    subprocess.run(
        ["tmux", "send-keys", "-t", tmux_name, message, "Enter"],
        check=True, timeout=10,
    )
    print(f"Message sent to '{name}'")


def cmd_status(args):
    """Show detailed session state."""
    name = args.name
    sessions_dir = get_sessions_dir()
    _, state = find_state_by_name(sessions_dir, name)
    if state is None:
        print(f"Error: no session named '{name}'")
        sys.exit(1)
    print(json.dumps(state, indent=2))


def cmd_close(args):
    """Gracefully close a session with cleanup."""
    name = args.name
    sessions_dir = get_sessions_dir()
    state_path, state = find_state_by_name(sessions_dir, name)
    if state is None:
        print(f"Error: no session named '{name}'")
        sys.exit(1)

    tmux_name = state["tmux_session"]

    # Check if tmux session exists
    if not tmux_session_exists(tmux_name):
        print(f"tmux session '{tmux_name}' not found. Marking as ended.")
        state["status"] = "ended"
        append_event(state, "ended")
        atomic_write_json(state_path, state)
        return

    # Wait for idle if active
    if state.get("status") == "active":
        print("Session is active, waiting for idle (30s timeout)...")
        for _ in range(30):
            time.sleep(1)
            state = read_state_file(state_path)
            if state and state.get("status") != "active":
                break
        else:
            print("Session still active after 30s.")
            response = input("Interrupt? [y/N] ").strip().lower()
            if response != "y":
                print("Aborted.")
                return

    # Send cleanup commands
    cleanup_cmds = [
        "Commit all changes with a descriptive message",
        "Push the current branch",
        "Update the project INDEX.md status section with what was accomplished this session",
    ]
    for cmd in cleanup_cmds:
        print(f"Sending: {cmd[:60]}...")
        subprocess.run(
            ["tmux", "send-keys", "-t", tmux_name, cmd, "Enter"],
            check=True, timeout=10,
        )
        # Wait for idle
        for _ in range(60):
            time.sleep(1)
            state = read_state_file(state_path)
            if state and state.get("status") == "idle":
                break

    # Send /exit
    print("Sending /exit...")
    subprocess.run(
        ["tmux", "send-keys", "-t", tmux_name, "/exit", "Enter"],
        timeout=10,
    )

    # Wait for tmux to end
    for _ in range(30):
        time.sleep(1)
        if not tmux_session_exists(tmux_name):
            break
    else:
        print("Session didn't exit, force-killing tmux...")
        subprocess.run(["tmux", "kill-session", "-t", tmux_name], timeout=10)

    # Check worktree state
    worktree_path = state.get("worktree_path", "")
    dirty = False
    if worktree_path and os.path.isdir(worktree_path) and worktree_path != OS_ROOT:
        # Check for uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"], cwd=worktree_path,
            capture_output=True, text=True, timeout=10,
        )
        if result.stdout.strip():
            print(f"Warning: worktree has uncommitted changes. Preserving at {worktree_path}")
            dirty = True
        else:
            # Check for unpushed commits
            result = subprocess.run(
                ["git", "log", "@{upstream}..HEAD", "--oneline"],
                cwd=worktree_path, capture_output=True, text=True, timeout=10,
            )
            if result.stdout.strip():
                print(f"Warning: worktree has unpushed commits. Preserving at {worktree_path}")
                dirty = True
            else:
                # Safe to remove
                subprocess.run(
                    ["git", "worktree", "remove", worktree_path],
                    cwd=OS_ROOT, capture_output=True, timeout=10,
                )
                print(f"Worktree removed: {worktree_path}")

    # Update state
    state = read_state_file(state_path) or state
    if dirty:
        state["status"] = "ended_dirty"
        append_event(state, "ended_dirty", summary="Worktree preserved — uncommitted or unpushed changes")
    else:
        state["status"] = "ended"
        append_event(state, "ended")
    atomic_write_json(state_path, state)
    print(f"Session '{name}' closed ({state['status']})")


def cmd_destroy(args):
    """Force-kill a session."""
    name = args.name
    sessions_dir = get_sessions_dir()
    state_path, state = find_state_by_name(sessions_dir, name)
    tmux_name = f"{TMUX_PREFIX}{name}"

    # Kill tmux session
    if tmux_session_exists(tmux_name):
        subprocess.run(["tmux", "kill-session", "-t", tmux_name], timeout=10)
        print(f"tmux session '{tmux_name}' killed")

    # Update state
    if state and state_path:
        state["status"] = "ended_dirty"
        append_event(state, "ended_dirty", summary="force_destroyed")
        atomic_write_json(state_path, state)

    print(f"Session '{name}' destroyed. Worktree preserved for inspection.")


def main():
    parser = argparse.ArgumentParser(description="Session manager for the Indemn OS")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create
    p_create = subparsers.add_parser("create", help="Create a new session")
    p_create.add_argument("name", help="Session name (used for tmux and worktree)")
    p_create.add_argument("--project", help="Project name (defaults to session name)")
    p_create.add_argument("--add-dir", action="append", help="Additional directories (repeatable)")
    p_create.add_argument("--model", default="opus", help="Claude model (default: opus)")
    p_create.add_argument("--permissions", default="bypassPermissions",
                          help="Permission mode (default: bypassPermissions)")
    p_create.add_argument("--no-worktree", action="store_true",
                          help="Run in OS repo directly without worktree")
    p_create.set_defaults(func=cmd_create)

    # list
    p_list = subparsers.add_parser("list", help="List active sessions")
    p_list.set_defaults(func=cmd_list)

    # attach
    p_attach = subparsers.add_parser("attach", help="Attach to a session")
    p_attach.add_argument("name", help="Session name")
    p_attach.set_defaults(func=cmd_attach)

    # send
    p_send = subparsers.add_parser("send", help="Send message to a session")
    p_send.add_argument("name", help="Session name")
    p_send.add_argument("message", help="Message to send")
    p_send.set_defaults(func=cmd_send)

    # status
    p_status = subparsers.add_parser("status", help="Show session status")
    p_status.add_argument("name", help="Session name")
    p_status.set_defaults(func=cmd_status)

    # close
    p_close = subparsers.add_parser("close", help="Gracefully close a session")
    p_close.add_argument("name", help="Session name")
    p_close.set_defaults(func=cmd_close)

    # destroy
    p_destroy = subparsers.add_parser("destroy", help="Force-kill a session")
    p_destroy.add_argument("name", help="Session name")
    p_destroy.set_defaults(func=cmd_destroy)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
```

**Step 4: Run tests to verify they pass**

```bash
cd /Users/home/Repositories/operating-system && python3 -m pytest tests/test_session_cli.py -v
```

Expected: All tests PASS

**Step 5: Set up the `session` alias**

Add to `.env`:
```bash
echo 'alias session="python3 /Users/home/Repositories/operating-system/systems/session-manager/cli.py"' >> /Users/home/Repositories/operating-system/.env
```

Verify:
```bash
source .env && session list
```

Expected: "No active sessions."

**Step 6: Commit**

```bash
git add systems/session-manager/ tests/test_session_cli.py
git commit -m "feat(session-manager): add session CLI and SYSTEM.md — create, list, attach, send, close, destroy"
```

---

### Task 5: Install Hooks in `~/.claude/settings.json`

Wire the hook scripts into Claude Code's global settings.

**Files:**
- Modify: `~/.claude/settings.json`

**Step 1: Read the current settings**

```bash
cat ~/.claude/settings.json | python3 -m json.tool
```

Note the existing hooks section. We need to ADD our hooks alongside existing ones without removing anything.

**Step 2: Add session manager hooks**

Add the following hook entries to the `hooks` key in `~/.claude/settings.json`. The hooks array for each event merges across scopes, so add new entries — don't replace existing ones.

Events to add hooks for: `SessionStart`, `Stop`, `UserPromptSubmit`, `TaskCompleted`, `SessionEnd`.

Each gets:
```json
{
  "matcher": "",
  "hooks": [
    {
      "type": "command",
      "command": "python3 /Users/home/Repositories/operating-system/systems/session-manager/hooks/update-state.py"
    }
  ]
}
```

Also update the `statusLine` to use our wrapper:
```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 /Users/home/Repositories/operating-system/systems/session-manager/hooks/update-context.py"
  }
}
```

**Step 3: Add `OS_ROOT` to `.env`**

```bash
echo 'export OS_ROOT="/Users/home/Repositories/operating-system"' >> /Users/home/Repositories/operating-system/.env
```

**Step 4: Verify hooks fire**

Start a new Claude Code session and check:
1. Does `update-state.py` exit cleanly? (check for errors in verbose mode: `claude --verbose`)
2. Does the statusline still render? (GSD wrapper working)
3. No noticeable delay in session startup?

**Step 5: Commit .env changes only**

```bash
# Don't commit ~/.claude/settings.json — it's outside the repo
git add .env
git commit -m "feat(session-manager): add OS_ROOT and session alias to .env"
```

---

### Task 6: EA Skill

The intelligence layer that reads state and orchestrates sessions.

**Files:**
- Create: `.claude/skills/ea/SKILL.md`

**Step 1: Write the EA skill**

```markdown
---
name: ea
description: Executive assistant for the operating system — manages Claude Code sessions across projects, provides briefings, handles session lifecycle. Use when the user asks about session status, wants to start/stop/switch sessions, or needs an overview of active work.
---

# Executive Assistant

## Overview

The EA is the management plane of the operating system. It reads session state, calls the session CLI, and understands projects. It orchestrates but does not do project work itself.

**Announce at start:** Run `source /Users/home/Repositories/operating-system/.env && session list` and read active project INDEX.md files. Present a conversational briefing.

## Startup Behavior

On activation, immediately:

1. Run: `source /Users/home/Repositories/operating-system/.env && session list`
2. For each active session, read its state file: `session status <name>`
3. Read `projects/*/INDEX.md` status sections for projects WITHOUT active sessions
4. Present a conversational briefing:

```
Here's where things stand:

ACTIVE SESSIONS
- <name> — <status> for <duration>, context <N>% remaining
- ...

NO ACTIVE SESSION
- <project> — <last known status from INDEX.md>

NEEDS ATTENTION
- <anything idle for >30min, context <20%, or ended_dirty>

What would you like to work on?
```

## Session Management

### Create a session

When the user wants to work on a project:

1. Check if a session already exists: `session list`
2. If not, read the project's INDEX.md for context and `--add-dir` hints
3. Run: `source .env && session create <name> [--add-dir <repos>] [--model <model>]`
4. Report the session details and offer to attach

### Switch to a session

Tell the user: "Run `session attach <name>` or in tmux: `Ctrl-b s` to pick the session."

Or run: `source .env && session attach <name>`

### Send a command to a session

Run: `source .env && session send <name> "<message>"`

### Close a session

Run: `source .env && session close <name>`

This triggers the defensive cleanup: commit, push, update INDEX.md, verify, exit.

### Destroy a session

For unresponsive sessions: `source .env && session destroy <name>`

### Check session details

Run: `source .env && session status <name>`

Or read the JSONL transcript directly: `~/.claude/projects/-Users-home-Repositories-operating-system/{session_id}.jsonl`

## What the EA Does NOT Do

- Project work (that's the session's job)
- Make decisions without the user's approval
- Automatically close or create sessions
- Replace project-level skills

## EA Continuity

The EA is a session like any other. When context runs low:
1. A new Claude Code session loads this skill
2. It reads `sessions/*.json` and `projects/*/INDEX.md`
3. Full picture immediately — no handoff needed

## Permission Guidance

Default: `bypassPermissions`. For production-touching sessions, recommend `--permissions acceptEdits`.

## Common Patterns

- "What's happening?" → `session list` + briefing
- "Let's work on X" → check for existing session, create if needed, offer to attach
- "Close up X" → `session close X`
- "Tell X to do Y" → `session send X "Y"`
- "Switch me to X" → `session attach X`
- "Kill X" → `session destroy X`
```

**Step 2: Test the skill**

Start a new Claude Code session in the OS repo and invoke:
```
/ea
```

Verify:
- The skill loads and runs `session list`
- It presents a briefing (even if "No active sessions")
- It responds to "Let's work on test-project" by offering to create a session

**Step 3: Commit**

```bash
git add .claude/skills/ea/SKILL.md
git commit -m "feat(ea): add EA skill — session management switchboard"
```

---

### Task 7: End-to-End Integration Test

Full lifecycle: create → verify hooks → send command → close.

**Files:**
- None created (manual test)

**Step 1: Create a test session**

```bash
source .env && session create test-integration --no-worktree
```

Verify:
- tmux session `os-test-integration` exists: `tmux list-sessions`
- State file created: `ls sessions/*.json`
- Claude Code is running in the tmux pane: `tmux capture-pane -t os-test-integration -p | tail -5`

**Step 2: Verify hooks update state**

Wait for Claude Code to finish initializing, then:
```bash
session status test-integration
```

Verify: `status` should be `idle` (the `Stop` hook fired after Claude's initial prompt).

**Step 3: Send a command**

```bash
session send test-integration "Say hello and tell me what project you are working in"
```

Wait a few seconds, then:
```bash
session status test-integration
```

Verify: `status` should cycle `active` → `idle`, `last_activity` updated.

**Step 4: Check context tracking**

```bash
session status test-integration | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Context: {d.get(\"context_remaining_pct\", \"?\")}%')"
```

Verify: should show a percentage (likely 95-100% for a fresh session).

**Step 5: Destroy the test session**

```bash
session destroy test-integration
```

Verify:
- tmux session gone: `tmux list-sessions`
- State file shows `ended_dirty`: `cat sessions/*.json | python3 -m json.tool | grep status`

**Step 6: Clean up**

```bash
# Move ended state files to archive
mkdir -p sessions/archive
mv sessions/*.json sessions/archive/ 2>/dev/null
```

**Step 7: Document results**

If everything passed, commit the integration test results as a note in the project INDEX.md.

---

### Task 8: Update CLAUDE.md and Conventions

Add the session manager and EA to the OS documentation.

**Files:**
- Modify: `CLAUDE.md`
- Modify: `projects/os-development/INDEX.md`

**Step 1: Add to CLAUDE.md**

Add the session manager to the Systems table and the EA to the System Skills table. Add the `session` CLI to the Tool Skills table.

**Step 2: Update project INDEX.md**

Refresh the status section with implementation complete, update the next steps.

**Step 3: Commit**

```bash
git add CLAUDE.md projects/os-development/INDEX.md
git commit -m "docs: add session manager and EA to CLAUDE.md, update project INDEX"
```

---

## Implementation Order Summary

| Task | Component | Depends On | Estimated Steps |
|------|-----------|-----------|----------------|
| 0 | Verify assumptions | Nothing | 3 |
| 1 | `lib/os_state.py` | Task 0 results | 5 |
| 2 | `hooks/update-state.py` | Task 1 | 5 |
| 3 | `hooks/update-context.py` | Task 1 | 5 |
| 4 | `cli.py` + `SYSTEM.md` | Tasks 1, 2, 3 | 6 |
| 5 | Install hooks | Tasks 2, 3 | 5 |
| 6 | EA skill | Task 4 | 3 |
| 7 | Integration test | Tasks 4, 5, 6 | 7 |
| 8 | Documentation | Task 7 | 3 |

Tasks 2 and 3 can be done in parallel (both depend only on Task 1).
