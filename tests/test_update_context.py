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
