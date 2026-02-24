"""Slack client initialization for Indemn OS.

Token resolution order:
1. SLACK_TOKEN env var (xoxp- OAuth user token)
2. macOS Keychain via agent-slack (xoxc- browser token) — preferred for security
3. SLACK_XOXC_TOKEN + SLACK_XOXD_COOKIE env vars (legacy fallback)

To set up: npx agent-slack auth import-desktop
"""

import os
import platform
import subprocess
import urllib.parse
from typing import Optional
from slack_sdk import WebClient


def _read_keychain(account: str) -> Optional[str]:
    """Read a value from macOS Keychain stored by agent-slack."""
    if platform.system() != "Darwin":
        return None
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "agent-slack", "-a", account, "-w"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def get_client() -> WebClient:
    # 1. Prefer OAuth token if available
    token = os.environ.get("SLACK_TOKEN")
    if token:
        return WebClient(token=token)

    # 2. Try macOS Keychain (agent-slack stores tokens here)
    xoxc = _read_keychain("xoxc:https://indemn.slack.com")
    xoxd = _read_keychain("xoxd")
    if xoxc and xoxd:
        return WebClient(
            token=xoxc,
            headers={"Cookie": f"d={urllib.parse.quote(xoxd, safe='')}"},
        )

    # 3. Fall back to env vars
    xoxc = os.environ.get("SLACK_XOXC_TOKEN")
    xoxd = os.environ.get("SLACK_XOXD_COOKIE")
    if xoxc and xoxd:
        return WebClient(
            token=xoxc,
            headers={"Cookie": f"d={urllib.parse.quote(xoxd, safe='')}"},
        )

    raise RuntimeError(
        "No Slack token found. Run 'npx agent-slack auth import-desktop' "
        "or set SLACK_TOKEN (xoxp-) in .env"
    )
