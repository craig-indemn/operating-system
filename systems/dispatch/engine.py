#!/usr/bin/env python3
"""
Dispatch Engine — Ralph Loop

Executes beads epics by running fresh Claude Code sessions per task via the Agent SDK.
Each task gets its own context window. Verification runs in a separate session.

Usage:
    env -u CLAUDECODE python3 engine.py <epic-id> [--beads-dir <path>]

The engine:
1. Reads the epic and its children from beads
2. Picks the next ready child (open, deps satisfied)
3. Runs a Claude Code session via Agent SDK query()
4. Verifies results in a separate session
5. Updates beads status, appends learnings, git commits on pass
6. Loops until all children pass or nothing remains to try
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
from contextlib import aclosing
from datetime import datetime
from pathlib import Path

# Ensure we're not inside a nested Claude Code session
os.environ.pop("CLAUDECODE", None)

# Monkey-patch SDK to handle unknown message types (e.g., rate_limit_event)
# See: https://github.com/anthropics/claude-agent-sdk-python/issues/583
import claude_agent_sdk._internal.message_parser as _mp
import claude_agent_sdk._internal.client as _client
_original_parse = _mp.parse_message

def _tolerant_parse(data):
    try:
        return _original_parse(data)
    except Exception as e:
        if "Unknown message type" in str(e):
            return None
        raise

_mp.parse_message = _tolerant_parse
_client.parse_message = _tolerant_parse

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
)

OS_ROOT = Path(__file__).resolve().parent.parent.parent  # operating-system/
ACTIVE_DIR = Path(__file__).resolve().parent / "active"
MAX_RETRIES_PER_TASK = 3
MAX_VERIFY_RETRIES = 3


# ---------------------------------------------------------------------------
# Beads interaction (CLI-first)
# ---------------------------------------------------------------------------

def bd(*args, beads_dir: str | None = None) -> dict | list | None:
    """Run a beads command and return parsed JSON output."""
    cmd = ["bd", *args, "--json"]
    cwd = beads_dir or os.getcwd()
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"  [beads] error: {result.stderr.strip()}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def bd_update(bead_id: str, beads_dir: str | None = None, **kwargs) -> bool:
    """Update a bead's fields."""
    cmd = ["bd", "update", bead_id]
    for key, value in kwargs.items():
        cmd.extend([f"--{key.replace('_', '-')}", str(value)])
    cwd = beads_dir or os.getcwd()
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return result.returncode == 0


def bd_close(bead_id: str, beads_dir: str | None = None) -> bool:
    """Close a bead."""
    cmd = ["bd", "close", bead_id]
    cwd = beads_dir or os.getcwd()
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return result.returncode == 0


def get_epic(epic_id: str, beads_dir: str | None = None) -> dict | None:
    """Get epic details."""
    data = bd("show", epic_id, beads_dir=beads_dir)
    if data and isinstance(data, list) and len(data) > 0:
        return data[0]
    return None


def get_children(epic_id: str, beads_dir: str | None = None) -> list[dict]:
    """Get all children of an epic (including closed)."""
    data = bd("list", "--parent", epic_id, "--all", beads_dir=beads_dir)
    return data if isinstance(data, list) else []


def get_ready_children(children: list[dict]) -> list[dict]:
    """Filter children to those that are ready to execute (open, deps satisfied)."""
    closed_ids = {c["id"] for c in children if c.get("status") == "closed"}
    ready = []
    for child in children:
        if child.get("status") != "open":
            continue
        # Check if all non-parent dependencies are satisfied
        deps = child.get("dependencies", [])
        blocked = False
        for dep in deps:
            if dep.get("type") == "parent-child":
                continue  # Parent-child is structural, not blocking
            if dep.get("depends_on_id") not in closed_ids:
                blocked = True
                break
        if not blocked:
            ready.append(child)
    return ready


# ---------------------------------------------------------------------------
# Context assembly
# ---------------------------------------------------------------------------

def build_task_context(epic: dict, task: dict, learnings_path: Path) -> str:
    """Assemble the context string injected into the dispatched session."""
    lines = []
    lines.append("# Dispatch Context")
    lines.append("")
    lines.append(f"## Epic: {epic.get('title', 'Untitled')}")
    if epic.get("description"):
        lines.append(epic["description"])
    if epic.get("acceptance_criteria"):
        lines.append(f"\n**Backstop criteria:** {epic['acceptance_criteria']}")
    lines.append("")
    lines.append(f"## Your Task: {task.get('title', 'Untitled')}")
    if task.get("description"):
        lines.append(task["description"])
    if task.get("acceptance_criteria"):
        lines.append(f"\n**Acceptance criteria:** {task['acceptance_criteria']}")
    lines.append("")
    lines.append("## Instructions")
    lines.append("- Focus ONLY on this specific task")
    lines.append("- Make the minimal changes needed to satisfy the acceptance criteria")
    lines.append("- Do NOT commit — the dispatch engine handles commits")
    lines.append("")

    # Learnings from previous tasks
    if learnings_path.exists():
        learnings = learnings_path.read_text().strip()
        if learnings:
            lines.append("## Learnings from Previous Tasks")
            lines.append(learnings)
            lines.append("")

    return "\n".join(lines)


def build_verify_prompt(task: dict, epic: dict) -> str:
    """Build the verification prompt for a separate judge session."""
    acceptance = task.get("acceptance_criteria", "Task completed successfully")
    backstop = epic.get("acceptance_criteria", "")

    return f"""You are a verification judge. Review the recent changes in this repository and determine whether the following acceptance criteria are met.

**Task:** {task.get('title', 'Untitled')}
**Task Description:** {task.get('description', 'No description')}
**Acceptance Criteria:** {acceptance}
{"**Backstop Criteria:** " + backstop if backstop else ""}

Instructions:
1. Use Read, Glob, Grep to examine the changes
2. If there are tests, use Bash to run them
3. Determine whether the acceptance criteria are satisfied
4. Respond with your judgment as a JSON object:
   {{"passes": true/false, "reason": "brief explanation"}}

Be strict. Only pass if the criteria are clearly met."""


# ---------------------------------------------------------------------------
# SDK session execution
# ---------------------------------------------------------------------------

async def run_task_session(
    task: dict,
    epic: dict,
    target_repo: str,
    learnings_path: Path,
) -> tuple[bool, str]:
    """Run a Claude Code session for a single task. Returns (success, output)."""
    context = build_task_context(epic, task, learnings_path)
    prompt = f"{task.get('title', 'Untitled')}\n\n{task.get('description', '')}"

    options = ClaudeAgentOptions(
        cwd=target_repo,
        add_dirs=[str(OS_ROOT)],
        setting_sources=["user", "project"],
        permission_mode="bypassPermissions",
        model="opus",
        system_prompt={"type": "preset", "preset": "claude_code", "append": context},
    )

    output_parts = []
    try:
        async with aclosing(query(prompt=prompt, options=options)) as messages:
            async for message in messages:
                if message is None:
                    continue  # Skipped unknown message type (e.g., rate_limit_event)
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            output_parts.append(block.text)
                elif isinstance(message, ResultMessage):
                    cost = message.total_cost_usd
                    if cost is not None:
                        print(f"  [task] session cost: ${cost:.4f}")
    except Exception as e:
        print(f"  [task] session error: {type(e).__name__}: {e}", file=sys.stderr)
        return False, f"Session error: {e}"

    return True, "\n".join(output_parts)


async def run_verify_session(
    task: dict,
    epic: dict,
    target_repo: str,
) -> tuple[bool, str]:
    """Run a verification session. Returns (passes, reason)."""
    prompt = build_verify_prompt(task, epic)

    # Don't use output_format — rate_limit_event kills the stream before
    # ResultMessage arrives. Parse JSON from text output instead.
    options = ClaudeAgentOptions(
        cwd=target_repo,
        permission_mode="bypassPermissions",
        model="opus",
    )

    output_parts = []
    try:
        async with aclosing(query(prompt=prompt, options=options)) as messages:
            async for message in messages:
                if message is None:
                    continue  # Skipped unknown message type (e.g., rate_limit_event)
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            output_parts.append(block.text)
    except Exception as e:
        print(f"  [verify] error: {type(e).__name__}: {e}", file=sys.stderr)
        return False, f"Verification error: {e}"

    # Parse the verification result from text output
    full_output = "\n".join(output_parts)
    try:
        # Find JSON in the output (may be wrapped in markdown code blocks)
        json_str = full_output
        if "```" in json_str:
            # Extract from code block
            for block in json_str.split("```"):
                block = block.strip()
                if block.startswith("json"):
                    block = block[4:].strip()
                if "{" in block and "passes" in block:
                    json_str = block
                    break
        # Find the JSON object
        start = json_str.find("{")
        end = json_str.rfind("}") + 1
        if start >= 0 and end > start:
            result = json.loads(json_str[start:end])
            passes = result.get("passes", False)
            reason = result.get("reason", "No reason given")
            return passes, reason
    except (json.JSONDecodeError, KeyError):
        pass

    # Fallback: look for pass/fail keywords in output
    lower = full_output.lower()
    if "passes" in lower and "true" in lower:
        return True, f"Verification passed (parsed from text)"
    return False, f"Could not parse verification result from output"


def git_commit(target_repo: str, message: str) -> bool:
    """Stage all changes and commit in the target repo."""
    result = subprocess.run(
        ["git", "add", "-A"],
        capture_output=True, text=True, cwd=target_repo,
    )
    if result.returncode != 0:
        return False

    # Check if there's anything to commit
    status = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        capture_output=True, text=True, cwd=target_repo,
    )
    if status.returncode == 0:
        print("  [git] no changes to commit")
        return True  # Nothing to commit is not an error

    result = subprocess.run(
        ["git", "commit", "-m", message],
        capture_output=True, text=True, cwd=target_repo,
    )
    if result.returncode == 0:
        print(f"  [git] committed: {message}")
        return True
    else:
        print(f"  [git] commit failed: {result.stderr.strip()}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

async def dispatch(epic_id: str, beads_dir: str | None = None):
    """Main dispatch loop — the ralph loop."""
    print(f"\n{'='*60}")
    print(f"DISPATCH ENGINE")
    print(f"{'='*60}")

    # Load epic
    epic = get_epic(epic_id, beads_dir)
    if not epic:
        print(f"Error: epic '{epic_id}' not found", file=sys.stderr)
        sys.exit(1)

    # Parse target_repo from notes (format: "target_repo: /path/to/repo")
    target_repo = ""
    notes = epic.get("notes", "")
    for line in notes.split("\n"):
        if line.strip().startswith("target_repo:"):
            target_repo = line.split(":", 1)[1].strip()
            break
    if not target_repo:
        print(f"Error: epic '{epic_id}' has no target_repo in notes", file=sys.stderr)
        print('Create the epic with: bd create "Title" --type epic --notes "target_repo: /path/to/repo"', file=sys.stderr)
        sys.exit(1)

    if not Path(target_repo).is_dir():
        print(f"Error: target repo '{target_repo}' does not exist", file=sys.stderr)
        sys.exit(1)

    print(f"Epic: {epic.get('title', epic_id)}")
    print(f"Target: {target_repo}")
    if epic.get("acceptance_criteria"):
        print(f"Backstop: {epic['acceptance_criteria']}")

    # Set up active directory for learnings
    ACTIVE_DIR.mkdir(parents=True, exist_ok=True)
    learnings_path = ACTIVE_DIR / "learnings.md"
    if not learnings_path.exists():
        learnings_path.write_text("")

    # Track attempts per task
    attempts: dict[str, int] = {}
    iteration = 0

    while True:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")

        # Refresh children from beads
        children = get_children(epic_id, beads_dir)
        if not children:
            print("No children found for this epic.")
            break

        # Check completion
        all_done = all(c.get("status") == "closed" for c in children)
        if all_done:
            print("\nAll tasks passed!")
            break

        # Find ready tasks (excluding those that exhausted retries)
        ready = get_ready_children(children)
        ready = [t for t in ready if attempts.get(t["id"], 0) < MAX_RETRIES_PER_TASK]
        if not ready:
            open_tasks = [c for c in children if c.get("status") != "closed"]
            if not open_tasks:
                break  # All done
            exhausted = [c for c in open_tasks if attempts.get(c["id"], 0) >= MAX_RETRIES_PER_TASK]
            if exhausted:
                print(f"\n{len(exhausted)} task(s) exhausted retries.")
            blocked = [c for c in open_tasks if c not in exhausted]
            if blocked:
                print(f"{len(blocked)} task(s) blocked by dependencies.")
            break

        # Pick the first ready task
        task = ready[0]
        task_id = task["id"]
        attempts.setdefault(task_id, 0)
        attempts[task_id] += 1

        print(f"\nTask: {task.get('title', task_id)} (attempt {attempts[task_id]}/{MAX_RETRIES_PER_TASK})")

        # Mark in progress
        bd_update(task_id, beads_dir=beads_dir, status="in_progress")

        # Run implementation session
        print("  Running implementation session...")
        success, output = await run_task_session(task, epic, target_repo, learnings_path)

        if not success:
            print(f"  Implementation session failed: {output}")
            # Append failure to learnings
            with open(learnings_path, "a") as f:
                f.write(f"\n### Task: {task.get('title')} (attempt {attempts[task_id]}) — SESSION FAILED\n")
                f.write(f"{output}\n")
            bd_update(task_id, beads_dir=beads_dir, status="open")
            if attempts[task_id] >= MAX_RETRIES_PER_TASK:
                print(f"  Max retries reached for {task_id}")
            continue

        # Run verification session (retry if output can't be parsed)
        passes = False
        reason = "Verification not run"
        for verify_attempt in range(1, MAX_VERIFY_RETRIES + 1):
            print(f"  Running verification session (attempt {verify_attempt}/{MAX_VERIFY_RETRIES})...")
            passes, reason = await run_verify_session(task, epic, target_repo)
            if "Could not parse" not in reason:
                break  # Got a parseable result (pass or fail)
            print(f"  Verification output not parseable, retrying...")

        if passes:
            print(f"  PASSED: {reason}")
            bd_close(task_id, beads_dir=beads_dir)
            git_commit(target_repo, f"dispatch({epic.get('title', epic_id)}): {task.get('title', task_id)}")
            with open(learnings_path, "a") as f:
                f.write(f"\n### Task: {task.get('title')} — PASSED\n")
                f.write(f"Verification: {reason}\n")
        else:
            print(f"  FAILED: {reason}")
            bd_update(task_id, beads_dir=beads_dir, status="open")
            with open(learnings_path, "a") as f:
                f.write(f"\n### Task: {task.get('title')} (attempt {attempts[task_id]}) — FAILED\n")
                f.write(f"Reason: {reason}\n")
            if attempts[task_id] >= MAX_RETRIES_PER_TASK:
                print(f"  Max retries reached for {task_id}")

    # Summary
    children = get_children(epic_id, beads_dir)
    passed = sum(1 for c in children if c.get("status") == "closed")
    total = len(children)
    failed = total - passed

    print(f"\n{'='*60}")
    print(f"DISPATCH COMPLETE")
    print(f"{'='*60}")
    print(f"Epic: {epic.get('title', epic_id)}")
    print(f"Results: {passed}/{total} tasks passed, {failed} failed")

    if learnings_path.exists():
        print(f"Learnings: {learnings_path}")

    # Write summary
    summary_path = ACTIVE_DIR / "summary.md"
    summary_path.write_text(
        f"# Dispatch Summary\n\n"
        f"**Epic:** {epic.get('title', epic_id)}\n"
        f"**Target:** {target_repo}\n"
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"**Results:** {passed}/{total} passed\n\n"
        f"## Tasks\n"
        + "\n".join(
            f"- {'PASS' if c.get('status') == 'closed' else 'FAIL'}: {c.get('title', c['id'])}"
            for c in children
        )
        + "\n"
    )
    print(f"Summary: {summary_path}")

    return passed == total


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: engine.py <epic-id> [--beads-dir <path>]")
        print("\nRun from outside Claude Code:")
        print("  env -u CLAUDECODE python3 engine.py <epic-id>")
        sys.exit(1)

    epic_id = sys.argv[1]
    beads_dir = None

    if "--beads-dir" in sys.argv:
        idx = sys.argv.index("--beads-dir")
        if idx + 1 < len(sys.argv):
            beads_dir = sys.argv[idx + 1]

    success = asyncio.run(dispatch(epic_id, beads_dir))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
