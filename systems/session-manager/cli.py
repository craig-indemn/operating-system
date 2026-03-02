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
