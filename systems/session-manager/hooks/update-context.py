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
