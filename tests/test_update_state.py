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

    def test_terminal_state_not_overwritten(self):
        """Hooks must not update sessions that are already ended or ended_dirty."""
        for terminal_status in ("ended", "ended_dirty"):
            self.base_state["status"] = terminal_status
            self.base_state["last_activity"] = "2026-01-01T00:00:00+00:00"
            write_state(self.sessions_dir, self.session_id, self.base_state)
            for event in ("SessionStart", "Stop", "UserPromptSubmit", "TaskCompleted"):
                rc = run_hook(event, self.session_id, self.sessions_dir)
                self.assertEqual(rc, 0)
                state = self._read_state()
                self.assertEqual(state["status"], terminal_status,
                                 f"{event} should not overwrite {terminal_status}")
                self.assertEqual(state["last_activity"], "2026-01-01T00:00:00+00:00",
                                 f"{event} should not update last_activity on {terminal_status}")
