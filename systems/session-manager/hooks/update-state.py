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
