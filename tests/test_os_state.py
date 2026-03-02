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
