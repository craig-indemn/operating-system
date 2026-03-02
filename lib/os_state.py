"""Shared utilities for OS session state management.

STDLIB ONLY — this module is imported by hook scripts that run with system python3.
No third-party dependencies allowed.

Verification notes (Task 0):
- --session-id: assumed honored; fallback lookup by cwd-to-worktree_path matching is implemented
- statusline input: assumed to contain session_id and context_window.remaining_percentage
"""
import json
import os
import tempfile
from datetime import datetime, timezone
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
