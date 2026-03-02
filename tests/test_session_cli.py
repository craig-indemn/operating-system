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
