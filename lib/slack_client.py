"""Slack client initialization for Indemn OS.

Handles both token types:
- xoxp- (OAuth user token) — set SLACK_TOKEN in .env
- xoxc- (browser token) — set SLACK_XOXC_TOKEN + SLACK_XOXD_COOKIE in .env
"""

import os
import urllib.parse
from slack_sdk import WebClient


def get_client() -> WebClient:
    # Prefer OAuth token if available
    token = os.environ.get("SLACK_TOKEN")
    if token:
        return WebClient(token=token)

    # Fall back to browser token + cookie
    xoxc = os.environ.get("SLACK_XOXC_TOKEN")
    xoxd = os.environ.get("SLACK_XOXD_COOKIE")
    if not xoxc:
        raise RuntimeError(
            "No Slack token found. Set SLACK_TOKEN (xoxp-) or SLACK_XOXC_TOKEN + SLACK_XOXD_COOKIE in .env"
        )
    if not xoxd:
        raise RuntimeError(
            "SLACK_XOXC_TOKEN is set but SLACK_XOXD_COOKIE is missing. Browser tokens require both."
        )

    return WebClient(
        token=xoxc,
        headers={"Cookie": f"d={urllib.parse.quote(xoxd, safe='')}"},
    )
