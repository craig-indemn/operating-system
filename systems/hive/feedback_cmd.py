"""Hive feedback command — self-improvement signal.

Creates a knowledge note with auto-tags [feedback, hive-improvement]
and auto-links to the current session context if available.
"""
import glob
import json
import os
import sys
from pathlib import Path

from knowledge_ops import create_knowledge


def _find_current_session() -> dict | None:
    """Try to find the current session state from session state files.

    Looks for session files in the OS sessions/ directory and finds one
    whose worktree_path matches our current working directory.
    """
    os_root = os.environ.get("OS_ROOT", "/Users/home/Repositories/operating-system")
    sessions_dir = Path(os_root) / "sessions"

    if not sessions_dir.exists():
        return None

    cwd = os.getcwd()

    for state_file in sessions_dir.glob("*.json"):
        try:
            with open(state_file) as f:
                state = json.load(f)
            # Match by worktree path
            if state.get("worktree_path") and cwd.startswith(state["worktree_path"]):
                return state
            # Match by name in cwd
            name = state.get("name", "")
            if name and name in cwd:
                return state
        except (json.JSONDecodeError, PermissionError):
            continue

    return None


def create_feedback(message: str) -> dict:
    """Create a feedback knowledge record.

    Auto-tags: [feedback, hive-improvement]
    Auto-links: to current session's project if available
    """
    tags = ["feedback", "hive-improvement"]
    refs = {}
    domains = []

    # Try to auto-link to current session context
    session = _find_current_session()
    if session:
        project = session.get("project")
        if project:
            refs["project"] = project
        # Use session's domain if available
        # (session state doesn't have domain, but project name hints at it)

    result = create_knowledge(
        title=message,
        tags=tags,
        refs=refs,
        domains=domains,
        status="active",
        body=message,
    )

    return result
