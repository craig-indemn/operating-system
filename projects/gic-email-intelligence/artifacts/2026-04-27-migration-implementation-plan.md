# GIC Email Intelligence Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate `gic-email-intelligence` from Railway + `craig-indemn` personal GitHub onto Indemn's standard stack (`indemn-ai` org, `dev-services` and `prod-services` EC2 with Docker Compose, AWS Secrets Manager + Parameter Store, AWS Amplify) with zero downtime to live customer operations.

**Architecture:** Clean-rebuild approach. Phase 1.0 code work (signal handling, pause flags, stale-claim recovery, healthcheck split, env-var-ization) ships in the personal repo first under a feature branch (so Railway prod is untouched), gets squashed and force-pushed as the initial commit to `indemn-ai/gic-email-intelligence`, then the EC2 stack stands up in dev side-by-side with Railway. After 24–48h dev soak, prod cuts over with paused Railway as instant rollback. Atlas database stays in place; Phase 2 (cluster relocation) is a separate workstream.

**Tech Stack:** Python 3.12 (uv), FastAPI, Typer, deepagents (LangChain), MongoDB Atlas, Google Vertex AI (Gemini), Anthropic, Docker Compose, GitHub Actions self-hosted runners, AWS Secrets Manager + Parameter Store, AWS Amplify, AWS EC2 (Ubuntu 22.04), Datadog.

**Reference:** Design doc at `projects/gic-email-intelligence/artifacts/2026-04-27-migration-to-indemn-infrastructure-design.md`. Reviewed across four rounds; eight reviewer-passes total. Read it before starting.

**Production-safety rule:** Tasks marked **[NEEDS USER APPROVAL]** modify production state (Atlas allowlist, security groups, Secrets Manager prod entries, Railway prod, DNS, etc.). Stop and confirm with Craig before executing those steps. Tasks marked **[COORDINATE WITH MONITORING SESSION]** touch the live `craig-indemn/gic-email-intelligence` repo or its Railway services and need to be sequenced with the other session's bug-fix work.

---

## Pre-flight Checklist

Run all of these before starting Phase A. Each must pass.

```bash
# AWS auth
aws sts get-caller-identity | jq -r '.Account'
# Expected: 780354157690

# GitHub auth + org membership
gh auth status
gh api user/orgs --jq '.[].login' | grep -q indemn-ai && echo OK || echo MISSING_ORG

# Railway auth
railway whoami
# Expected: craig@indemn.ai

# MongoDB Atlas reachable
mongosh "mongodb+srv://dev-indemn:wJnKmz4P0q39GpXZ@dev-indemn.mifra5.mongodb.net/gic_email_intelligence" --eval 'db.runCommand({ping:1})'
# Expected: { ok: 1, ... }

# Personal repo present
test -d /Users/home/Repositories/gic-email-intelligence && echo OK

# Indemn-ai target repo exists and is empty
gh api repos/indemn-ai/gic-email-intelligence --jq '{size, default_branch}'
# Expected: {size: 0, default_branch: "main"}

# uv installed
uv --version

# Docker daemon running locally (B.12 smoke-tests an image build)
docker info >/dev/null && echo OK

# Atlas backup tier supports on-demand snapshots
# Open Atlas UI → dev-indemn cluster → Backup → confirm "Continuous Cloud Backup" enabled
# (M0 free tier does NOT support snapshots; must be M10+)

# Amplify app d244t76u9ej8m0 exists in this AWS account
aws amplify get-app --app-id d244t76u9ej8m0 --query 'app.name' --output text
# Expected: gic-email-intelligence

# Production currently stable (no active incidents)
mongosh "..." --eval '
  var t = db.emails.countDocuments({received_at:{$gte: new Date(Date.now()-3600000)}});
  var f = db.emails.countDocuments({received_at:{$gte: new Date(Date.now()-3600000)}, automation_status:"failed"});
  print("Last hour: " + t + " emails, " + f + " automation failures");
'
# Expected: failure rate well under 20%
```

If any of these fail, fix before proceeding.

---

## Phase A: Workspace Setup

### Task A.1: Create isolated worktree of personal repo

Run all migration code work in a separate workdir so the live `main` branch (which Railway auto-deploys from) is undisturbed and the other session's bug-fix work doesn't collide.

**Step 1:** Create the worktree on a new branch.

```bash
cd /Users/home/Repositories/gic-email-intelligence
git fetch origin
git worktree add ../gic-email-intelligence-migration -b migration/indemn-infra origin/main
cd ../gic-email-intelligence-migration
```

**Step 2:** Verify the worktree is on the new branch and clean.

```bash
git status
git branch --show-current
# Expected: clean working tree on branch migration/indemn-infra
```

**Step 3:** Add `indemn-ai/gic-email-intelligence` as a second remote so we can push the squashed initial commit later without renaming origins.

```bash
git remote add indemn https://github.com/indemn-ai/gic-email-intelligence.git
git remote -v
# Expected: origin → craig-indemn/gic-email-intelligence, indemn → indemn-ai/gic-email-intelligence
```

**Step 4:** Verify uv environment.

```bash
uv sync --frozen
uv run gic --help
# Expected: Typer help output with 8 command groups
```

No commit yet — this task is workspace setup.

---

### Task A.2: Verify baseline test suite is green

**Step 1:** Run the full test suite.

```bash
uv run pytest -q
# Expected: 108 passed (or whatever the current count is). Note the number.
```

**Step 2:** Note the current commit SHA so we can roll back if anything goes off the rails during cleanup.

```bash
git rev-parse HEAD > /tmp/migration-baseline-sha.txt
cat /tmp/migration-baseline-sha.txt
```

If the test suite is red on `main`, **stop**: this isn't a migration problem, it's an existing problem to fix first.

---

## Phase B: Phase 1.0 Code Work (TDD)

All work in `/Users/home/Repositories/gic-email-intelligence-migration` on branch `migration/indemn-infra`. Frequent commits.

### Task B.1: Create SIGTERM-aware loop helper

**Files:**
- Create: `src/gic_email_intel/cli/loop.py`
- Test: `tests/test_loop.py`

**Step 1:** Write the failing test.

```python
# tests/test_loop.py
import os
import signal
import threading
import time

import pytest

from gic_email_intel.cli.loop import run_loop


def test_run_loop_calls_tick_then_sleeps():
    calls = []
    def tick(_settings):
        calls.append(time.monotonic())

    # Run for 2 ticks at 1s interval, then signal shutdown
    def stop_after():
        time.sleep(2.5)
        os.kill(os.getpid(), signal.SIGTERM)

    threading.Thread(target=stop_after, daemon=True).start()
    run_loop(interval=1, single_tick=tick)

    assert len(calls) >= 2
    # Inter-tick spacing roughly 1s
    assert 0.8 <= (calls[1] - calls[0]) <= 1.4


def test_run_loop_swallows_tick_exceptions():
    calls = []
    def tick(_settings):
        calls.append(1)
        raise RuntimeError("boom")

    def stop_after():
        time.sleep(2.5)
        os.kill(os.getpid(), signal.SIGTERM)

    threading.Thread(target=stop_after, daemon=True).start()
    run_loop(interval=1, single_tick=tick)

    # Loop kept ticking after exception
    assert len(calls) >= 2


def test_run_loop_interruptible_sleep():
    calls = []
    def tick(_settings):
        calls.append(time.monotonic())

    def stop_after():
        time.sleep(0.3)
        os.kill(os.getpid(), signal.SIGTERM)

    t0 = time.monotonic()
    threading.Thread(target=stop_after, daemon=True).start()
    run_loop(interval=60, single_tick=tick)  # Long interval
    elapsed = time.monotonic() - t0

    # Loop exits within ~1s of SIGTERM, not after the 60s sleep
    assert elapsed < 2.0
    assert len(calls) == 1
```

**Step 2:** Run the test; confirm `ImportError`.

```bash
uv run pytest tests/test_loop.py -v
# Expected: FAIL with "ModuleNotFoundError: No module named 'gic_email_intel.cli.loop'"
```

**Step 3:** Implement `src/gic_email_intel/cli/loop.py`.

```python
"""Long-running loop helper for crons inside Docker containers."""
import logging
import signal
import time
from typing import Callable

from gic_email_intel.config import Settings

logger = logging.getLogger(__name__)

_shutdown = False


def _handle_shutdown(_signum, _frame):
    global _shutdown
    _shutdown = True
    logger.info("Shutdown signal received; exiting loop after current tick.")


def run_loop(interval: int, single_tick: Callable[[Settings], None]) -> None:
    """Run `single_tick` repeatedly, sleeping `interval` seconds between ticks.

    - SIGTERM and SIGINT cause a graceful exit after the current tick finishes.
    - Settings are reloaded before each tick so PAUSE_* env changes take effect
      on the next tick boundary (not delayed by the sleep window).
    - Tick exceptions are caught and logged; the loop keeps running.
    """
    global _shutdown
    _shutdown = False
    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)

    while not _shutdown:
        try:
            settings = Settings()  # reload from env
            single_tick(settings)
        except Exception:
            logger.exception("Loop tick failed; continuing.")
        # Interruptible sleep — break early on shutdown
        for _ in range(interval):
            if _shutdown:
                break
            time.sleep(1)
```

**Step 4:** Run the test; confirm pass.

```bash
uv run pytest tests/test_loop.py -v
# Expected: 3 passed
```

**Step 5:** Commit.

```bash
git add src/gic_email_intel/cli/loop.py tests/test_loop.py
git commit -m "feat(loop): add SIGTERM-aware run_loop helper for cron containers"
```

---

### Task B.2: Wire `--loop --interval` into `gic sync`

**Files:**
- Modify: `src/gic_email_intel/cli/commands/sync.py`
- Test: `tests/test_cli_sync_loop.py`

**Step 1:** Read the current `sync.py` to find the entry point.

```bash
grep -n "^def\|@app\." src/gic_email_intel/cli/commands/sync.py
```

The current `sync_command` is a Typer callback that runs once per invocation. We're adding optional `--loop` and `--interval` flags that wrap the existing logic in `run_loop`.

**Step 2:** Write the failing test. Note: `run_loop` must be imported at module level in `sync.py` (`from gic_email_intel.cli.loop import run_loop`) for the patch path to work. Patching the import binding at `gic_email_intel.cli.commands.sync.run_loop` only intercepts module-level imports.

```python
# tests/test_cli_sync_loop.py
from typer.testing import CliRunner
from unittest.mock import patch

from gic_email_intel.cli.main import app

runner = CliRunner()

def test_sync_supports_loop_flag():
    """--loop --interval N must be accepted by the CLI."""
    with patch("gic_email_intel.cli.commands.sync.run_loop") as mock_loop:
        result = runner.invoke(app, ["sync", "run", "--loop", "--interval", "1"])
    assert result.exit_code == 0
    mock_loop.assert_called_once()
    _, kwargs = mock_loop.call_args
    assert kwargs.get("interval") == 1
```

**Step 3:** Run; confirm fail.

```bash
uv run pytest tests/test_cli_sync_loop.py -v
# Expected: FAIL — flags not recognized
```

**Step 4:** Refactor `sync.py`: import `run_loop` at module top, refactor existing single-shot body into `_sync_tick(settings)`, accept `--loop` and `--interval` flags. **Do NOT add a `settings.pause_sync` reference yet — that's B.5's job.** Keep `_sync_tick` as a pure refactor of the current behavior.

```python
# Top of sync.py
from gic_email_intel.cli.loop import run_loop
# ...

def _sync_tick(settings: Settings) -> None:
    """Single tick of the sync loop. Existing single-shot logic moves here verbatim."""
    # ... existing sync body unchanged ...

@app.command("run")
def run(
    loop: bool = typer.Option(False, "--loop", help="Run continuously, sleeping between ticks."),
    interval: int = typer.Option(300, "--interval", help="Seconds between ticks (loop mode only)."),
):
    """Sync new emails from Outlook into Mongo."""
    if loop:
        run_loop(interval=interval, single_tick=_sync_tick)
    else:
        _sync_tick(Settings())
```

(The exact diff depends on the current shape of `sync.py`. Read it carefully and refactor the existing single-shot body into `_sync_tick`.)

**Step 5:** Run all tests; confirm pass.

```bash
uv run pytest tests/test_cli_sync_loop.py tests/test_cli_emails.py -v
# Expected: all pass
```

**Step 6:** Commit.

```bash
git add src/gic_email_intel/cli/commands/sync.py tests/test_cli_sync_loop.py
git commit -m "feat(sync): support --loop --interval for long-running container mode"
```

---

### Task B.3: Wire `--loop --interval` into `gic automate run`

Same pattern as B.2, applied to `cli/commands/automate.py:30`'s `run` command.

**Files:**
- Modify: `src/gic_email_intel/cli/commands/automate.py`
- Test: `tests/test_cli_automate_loop.py`

**Steps:** Mirror B.2 exactly with `automate run` instead of `sync run`. Refactor existing body into `_automate_tick(settings)`. Test that `--loop --interval` are accepted and `run_loop` is called.

**Commit:**

```bash
git commit -m "feat(automate): support --loop --interval for long-running container mode"
```

---

### Task B.4: Wire `--loop --interval` into `gic automate process`

Same pattern, applied to the processing command at `agent/harness.py:422`'s `process` command (registered under `gic automate process`).

**Files:**
- Modify: `src/gic_email_intel/agent/harness.py`
- Test: `tests/test_cli_process_loop.py`

**Commit:**

```bash
git commit -m "feat(process): support --loop --interval for long-running container mode"
```

---

### Task B.5: Add `PAUSE_SYNC` config field + enforcement

**Files:**
- Modify: `src/gic_email_intel/config.py`
- Modify: `src/gic_email_intel/cli/commands/sync.py` (add `if settings.pause_sync: return` to `_sync_tick` — this is the first introduction of the pause check)
- Test: `tests/test_pause_sync.py`

**Step 1:** Failing test.

```python
# tests/test_pause_sync.py
from unittest.mock import patch
from typer.testing import CliRunner

from gic_email_intel.cli.main import app
from gic_email_intel.config import Settings

runner = CliRunner()

def test_pause_sync_setting_exists():
    s = Settings(pause_sync=True)
    assert s.pause_sync is True

def test_sync_tick_skips_when_paused():
    """When pause_sync=True, the tick should return early without running the sync body."""
    with patch("gic_email_intel.cli.commands.sync._do_sync") as mock_do:  # _do_sync = the actual sync body
        from gic_email_intel.cli.commands.sync import _sync_tick
        _sync_tick(Settings(pause_sync=True))
    mock_do.assert_not_called()
```

**Step 2:** Run; confirm fail.

**Step 3:** Add to `config.py`:

```python
pause_sync: bool = False
```

In `sync.py`, add to the top of `_sync_tick` (before any work):

```python
def _sync_tick(settings: Settings) -> None:
    if settings.pause_sync:
        console.print("[yellow]Sync paused via PAUSE_SYNC=true. Skipping tick.[/yellow]")
        return
    # ... existing body ...
```

**Step 4:** Run; confirm pass.

**Step 5:** Commit.

```bash
git commit -m "feat(config): add PAUSE_SYNC and enforce in sync tick"
```

---

### Task B.6: Add `/healthz` endpoint + rate-limit exemption

**Files:**
- Modify: `src/gic_email_intel/api/routes/health.py`
- Modify: `src/gic_email_intel/api/main.py:76` (rate-limit exemption)
- Test: `tests/test_healthz.py`

**Step 1:** Failing test.

```python
# tests/test_healthz.py
from fastapi.testclient import TestClient

from gic_email_intel.api.main import app

client = TestClient(app)

def test_healthz_returns_200_unconditionally():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_healthz_does_not_call_mongo():
    """Even with no MongoDB connection, /healthz returns 200."""
    # If health.py's existing /api/health hangs/fails when DB is down, /healthz must not.
    # Pure in-process check; nothing to mock.
    r = client.get("/healthz")
    assert r.status_code == 200
```

**Step 2:** Run; confirm fail.

**Step 3:** Add `/healthz` to `health.py`:

```python
@router.get("/healthz")
async def liveness():
    """Process-alive check for Docker healthcheck. No DB calls."""
    return {"status": "ok"}
```

Update `api/main.py:76` rate-limit exemption to also exempt `/healthz`.

**Step 4:** Run; confirm pass.

**Step 5:** Commit.

```bash
git commit -m "feat(api): add /healthz process-alive endpoint for Docker healthcheck"
```

---

### Task B.7: Add stale-claim recovery for `automation_status`

**Files:**
- Modify: `src/gic_email_intel/cli/commands/submissions.py` (extract `_find_duplicate_by_name` helper)
- Create: `src/gic_email_intel/automation/recovery.py`
- Modify: `src/gic_email_intel/cli/commands/automate.py` (call recovery at top of `_automate_tick`)
- Test: `tests/test_automation_recovery.py`

**Step 0 (precondition): Extract `_find_duplicate_by_name` helper.** Today, the duplicate-check logic lives inside the `check_duplicate` Typer command at `cli/commands/submissions.py:575`. The recovery function needs to call this in-process (not via subprocess), so move the actual matching logic into a private helper that BOTH the CLI command and `recovery.py` can call.

```python
# In cli/commands/submissions.py, refactor:
def _find_duplicate_by_name(name: str) -> Optional[dict]:
    """Return the most recent submission doc matching `name` (fuzzy) that has a
    unisoft_quote_id. None if no match."""
    # ... extracted from existing check_duplicate body ...

@app.command("check-duplicate")
def check_duplicate(name: str = typer.Option(...), compact: bool = typer.Option(False)):
    match = _find_duplicate_by_name(name)
    # ... existing output formatting unchanged ...
```

Run existing tests after the refactor to confirm no behavior change:

```bash
uv run pytest tests/test_cli_submissions.py -v
# Expected: existing pass count unchanged
```

Commit the refactor on its own:

```bash
git add src/gic_email_intel/cli/commands/submissions.py
git commit -m "refactor(submissions): extract _find_duplicate_by_name helper for in-process callers"
```

**Step 1:** Failing tests covering the four scenarios:

```python
# tests/test_automation_recovery.py
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from gic_email_intel.automation.recovery import reset_stale_automation


def test_resets_orphaned_email_with_no_existing_quote(test_db):
    # Insert an email with automation_status=processing, automation_started_at > 60min ago
    eid = test_db.emails.insert_one({
        "automation_status": "processing",
        "automation_started_at": datetime.now(timezone.utc) - timedelta(minutes=70),
        "named_insured": "Acme Test Inc",
    }).inserted_id

    # Mock check_duplicate to return None (no existing Quote)
    with patch("gic_email_intel.automation.recovery._check_existing_quote", return_value=None):
        result = reset_stale_automation(timeout_minutes=60)

    assert result["reset"] == 1
    assert result["flagged_for_review"] == 0
    doc = test_db.emails.find_one({"_id": eid})
    assert doc["automation_status"] is None


def test_flags_orphaned_email_with_existing_quote(test_db):
    eid = test_db.emails.insert_one({
        "automation_status": "processing",
        "automation_started_at": datetime.now(timezone.utc) - timedelta(minutes=70),
        "named_insured": "Acme Test Inc",
    }).inserted_id

    with patch("gic_email_intel.automation.recovery._check_existing_quote", return_value="Q:99999"):
        result = reset_stale_automation(timeout_minutes=60)

    assert result["reset"] == 0
    assert result["flagged_for_review"] == 1
    doc = test_db.emails.find_one({"_id": eid})
    assert doc["automation_status"] == "failed_recovery_review"


def test_skips_recent_processing_emails(test_db):
    """Recent claims (within timeout) are not touched."""
    test_db.emails.insert_one({
        "automation_status": "processing",
        "automation_started_at": datetime.now(timezone.utc) - timedelta(minutes=5),
    })
    result = reset_stale_automation(timeout_minutes=60)
    assert result["reset"] == 0
    assert result["flagged_for_review"] == 0


def test_fails_closed_when_duplicate_check_errors(test_db):
    """If the duplicate check raises (e.g., Mongo unreachable), do NOT reset."""
    test_db.emails.insert_one({
        "automation_status": "processing",
        "automation_started_at": datetime.now(timezone.utc) - timedelta(minutes=70),
        "named_insured": "Acme Test Inc",
    })
    with patch("gic_email_intel.automation.recovery._check_existing_quote",
               side_effect=RuntimeError("Mongo unreachable")):
        result = reset_stale_automation(timeout_minutes=60)
    # Email left untouched — fail-closed
    assert result["reset"] == 0
    assert result["flagged_for_review"] == 0
    assert result["errors"] == 1
```

(`test_db` fixture connects to a test Mongo collection — copy the pattern from existing tests like `tests/test_emails.py`.)

**Step 2:** Run; confirm fail.

**Step 3:** Implement `automation/recovery.py`.

```python
"""Stale-claim recovery for orphaned automation_status=processing emails."""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from gic_email_intel.core.db import EMAILS, get_sync_db
# Import the underlying duplicate-check helper from the submissions CLI
from gic_email_intel.cli.commands.submissions import _find_duplicate_by_name

logger = logging.getLogger(__name__)


def _check_existing_quote(named_insured: str) -> Optional[str]:
    """Return a unisoft_quote_id if a recent submission already has one for this name; else None.

    Wraps the same logic used by `gic submissions check-duplicate` so we can call it in-process.
    Raises on Mongo errors (caller should fail-closed).
    """
    match = _find_duplicate_by_name(named_insured)
    return match.get("unisoft_quote_id") if match else None


def reset_stale_automation(timeout_minutes: int = 60) -> dict:
    """Reset or flag emails stuck in automation_status=processing past the timeout.

    Behaviour:
      - If named_insured has no existing Quote in our records → reset to null (re-queueable)
      - If named_insured already has a Quote → flag as failed_recovery_review (human review)
      - If the duplicate check raises → leave email as-is (fail-closed)
    """
    db = get_sync_db()
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)
    candidates = list(db[EMAILS].find({
        "automation_status": "processing",
        "automation_started_at": {"$lt": cutoff},
    }, {"_id": 1, "named_insured": 1}))

    counts = {"reset": 0, "flagged_for_review": 0, "errors": 0}
    for c in candidates:
        try:
            existing = _check_existing_quote(c.get("named_insured", ""))
        except Exception:
            logger.exception("Duplicate check failed for %s; leaving as-is (fail-closed).", c["_id"])
            counts["errors"] += 1
            continue

        if existing:
            db[EMAILS].update_one(
                {"_id": c["_id"]},
                {"$set": {"automation_status": "failed_recovery_review",
                          "automation_recovery_note": f"possible duplicate of {existing}"}},
            )
            counts["flagged_for_review"] += 1
            logger.warning("Email %s flagged for review — possible duplicate of %s",
                           c["_id"], existing)
        else:
            db[EMAILS].update_one(
                {"_id": c["_id"]},
                {"$set": {"automation_status": None, "automation_started_at": None}},
            )
            counts["reset"] += 1
            logger.info("Reset stale automation claim for email %s", c["_id"])

    return counts
```

In `automate.py`, call `reset_stale_automation()` at the top of `_automate_tick` (the function from B.3).

**Step 4:** Refactor `submissions.py:check-duplicate` if needed to expose `_find_duplicate_by_name` as a callable helper (the CLI command should call this helper, not the other way around).

**Step 5:** Run; confirm pass.

**Step 6:** Commit.

```bash
git commit -m "feat(automation): add stale-claim recovery with fail-closed duplicate check"
```

---

### Task B.8: Env-var-ize CORS_ORIGINS with Pydantic validator

**Files:**
- Modify: `src/gic_email_intel/config.py`
- Modify: `src/gic_email_intel/api/main.py:54-61` (replace hardcoded list)
- Test: `tests/test_cors_config.py`

**Step 1:** Failing test for whitespace stripping.

```python
# tests/test_cors_config.py
from gic_email_intel.config import Settings

def test_cors_origins_strips_whitespace():
    s = Settings(cors_origins="https://a.com, https://b.com ,https://c.com")
    assert s.cors_origins == ["https://a.com", "https://b.com", "https://c.com"]

def test_cors_origins_handles_empty_entries():
    s = Settings(cors_origins="https://a.com,,https://b.com")
    assert s.cors_origins == ["https://a.com", "https://b.com"]

def test_cors_origins_default():
    s = Settings()
    assert "http://localhost:5173" in s.cors_origins
```

**Step 2:** Run; confirm fail.

**Step 3:** Add to `config.py`:

```python
from pydantic import field_validator

class Settings(BaseSettings):
    # ... existing fields ...
    cors_origins: list[str] = ["http://localhost:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v
```

In `api/main.py`, replace lines 54–61 with:

```python
import logging
logger = logging.getLogger(__name__)
logger.info(f"CORS allow_origins: {settings.cors_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Step 4:** Run; confirm pass.

**Step 5:** Commit.

```bash
git commit -m "feat(api): env-var-ize CORS_ORIGINS with whitespace stripping and startup log"
```

---

### Task B.9: Env-var-ize `GRAPH_USER_EMAIL` + parameterize skill prompts

**Files:**
- Modify: `src/gic_email_intel/config.py:13` (remove default)
- Modify: `src/gic_email_intel/agent/skills/email_classifier.md` (add `{graph_user_email}` placeholders)
- Modify: `src/gic_email_intel/automation/agent.py:60` (`_load_skill` to substitute placeholders)
- Modify: `src/gic_email_intel/agent/harness.py:151,156` (use `settings.graph_user_email`)
- Modify: `src/gic_email_intel/agent/agent.py:76` (use `settings.graph_user_email` in system prompt)
- Modify: `src/gic_email_intel/api/routes/stats.py:346` (use `settings.graph_user_email`)
- Modify: `src/gic_email_intel/cli/commands/emails.py:364` (use `settings.graph_user_email`)
- Test: `tests/test_skill_loading.py`

**Step 1:** Failing test for skill prompt substitution.

```python
# tests/test_skill_loading.py
import os
from unittest.mock import patch
from gic_email_intel.automation.agent import _load_skill

def test_load_skill_substitutes_graph_user_email():
    with patch.dict(os.environ, {"GRAPH_USER_EMAIL": "test@example.com"}):
        text = _load_skill("email_classifier")
    assert "test@example.com" in text
    assert "quote@gicunderwriters.com" not in text
    assert "{graph_user_email}" not in text
```

**Step 2:** Run; confirm fail.

**Step 3:**
- In `email_classifier.md`, replace literal `quote@gicunderwriters.com` with `{graph_user_email}` (the two known occurrences plus any others — grep `email_classifier.md` first).
- Update `_load_skill()`:

```python
def _load_skill(name: str) -> str:
    settings = Settings()
    path = SKILLS_DIR / f"{name}.md"
    text = path.read_text()
    return text.format(graph_user_email=settings.graph_user_email)
```

- Replace each Python hardcoded reference with `settings.graph_user_email`.
- In `config.py:13`, remove the default and make required:

```python
graph_user_email: str  # required; no default
```

**Step 4:** Run all tests; confirm pass.

```bash
uv run pytest -q
```

**Step 5:** Commit.

```bash
git commit -m "feat(config): env-var-ize GRAPH_USER_EMAIL and parameterize skill prompts"
```

---

### Task B.10: Env-var-ize task group IDs and PUBLIC_BASE_URL

**Files:**
- Modify: `src/gic_email_intel/config.py` (add 3 new fields)
- Modify: `src/gic_email_intel/automation/skills/create-quote-id.md` (parameterize GroupId references)
- Audit `src/` and `unisoft-proxy/client/` for hardcoded `gic.indemn.ai` → use `settings.public_base_url`
- Test: `tests/test_task_group_routing.py` (if not already covered)

**Step 1:** Add to `config.py`:

```python
unisoft_task_group_id_newbiz: int  # required
unisoft_task_group_id_wc: int  # required
public_base_url: str = "https://gic.indemn.ai"  # default for dev convenience
```

**Step 2:** In `create-quote-id.md`, replace hardcoded `GroupId 3` (prod NEW BIZ) and `GroupId 4` (prod WC) with `{unisoft_task_group_id_newbiz}` and `{unisoft_task_group_id_wc}`. Update `_load_skill()` to substitute these too:

```python
def _load_skill(name: str) -> str:
    settings = Settings()
    path = SKILLS_DIR / f"{name}.md"
    text = path.read_text()
    return text.format(
        graph_user_email=settings.graph_user_email,
        unisoft_task_group_id_newbiz=settings.unisoft_task_group_id_newbiz,
        unisoft_task_group_id_wc=settings.unisoft_task_group_id_wc,
    )
```

**Step 3:** Grep for `gic.indemn.ai` in `src/` (excluding the CORS list, which is now env-driven). Replace with `settings.public_base_url` where it's outbound-link generation.

```bash
grep -rn "gic\.indemn\.ai" src/ unisoft-proxy/client/
```

**Step 4:** Run tests.

```bash
uv run pytest -q
```

**Step 5:** Commit.

```bash
git commit -m "feat(config): env-var-ize task group IDs and PUBLIC_BASE_URL"
```

---

### Task B.11: Remove `UNISOFT_PROXY_URL` hardcoded fallbacks

**Files:**
- Modify: `src/gic_email_intel/cli/commands/emails.py:272`
- Modify: `unisoft-proxy/client/cli.py:46`

**Step 1:** Read both files; confirm the current fallbacks are `54.83.28.79:5001` and `54.83.28.79:5000` respectively.

**Step 2:** Replace with required-env behavior:

```python
proxy_url = os.environ.get("UNISOFT_PROXY_URL")
if not proxy_url:
    raise RuntimeError("UNISOFT_PROXY_URL must be set; no default")
proxy_url = proxy_url.rstrip("/")
```

(Or have it read from `Settings`. Whichever is lighter.)

**Step 3:** Run tests; confirm nothing depended on the fallback.

```bash
uv run pytest -q
```

**Step 4:** Commit.

```bash
git commit -m "feat(config): require UNISOFT_PROXY_URL env var (remove hardcoded fallbacks)"
```

---

### Task B.12: Update Dockerfile healthcheck path

**Files:**
- Modify: `Dockerfile`

**Step 1:** Read the current Dockerfile healthcheck (line 49 per design).

**Step 2:** Change `curl -f http://localhost:8080/api/health` to `curl -f http://localhost:8080/healthz`.

**Step 3:** Smoke-test by building locally:

```bash
docker build -t gic-test:local .
docker run --rm -d --name gic-test -p 8080:8080 -e MONGODB_URI=... -e GRAPH_USER_EMAIL=quote@gicunderwriters.com -e GOOGLE_CLOUD_PROJECT=prod-gemini-470505 gic-test:local
sleep 5
docker inspect --format='{{.State.Health.Status}}' gic-test
docker stop gic-test
```

Expected health status `healthy` (or `starting` for the first 15s — wait and re-check).

**Step 4:** Commit.

```bash
git commit -m "fix(docker): point healthcheck at /healthz (process-alive, no DB)"
```

---

## Phase C: Cleanup (delete dead code)

### Task C.1: Delete `addin-test/` and `data/` and root HTML diagrams

**Files:**
- Delete: `addin-test/` (entire dir)
- Delete: `data/` (entire dir, ~6.4 MB of exploration corpus)
- Delete: `indemn-conversational-intake-workflow.html`, `indemn-cross-sell-workflow.html`, `indemn-email-intelligence-workflow.html`, `indemn-intake-manager-workflow.html`, `indemn-quote-bind-workflow.html`
- Delete: `src/gic_email_intel/agent/skills/stage_detector.md.deprecated`

**Step 1:** Confirm nothing imports from these (sanity grep).

```bash
grep -rn "addin-test\|stage_detector" src/ tests/ scripts/ ui/src/ || echo "no refs"
```

**Step 2:** Delete.

```bash
git rm -r addin-test/ data/
git rm indemn-*.html
git rm src/gic_email_intel/agent/skills/stage_detector.md.deprecated
```

**Step 3:** Run tests.

```bash
uv run pytest -q
```

**Step 4:** Commit.

```bash
git commit -m "chore: delete dead code (addin-test, data exploration corpus, design HTMLs, deprecated skill)"
```

---

### Task C.2: Triage `scripts/` and delete one-off historical scripts

**Files:**
- Review each file in `scripts/`
- Delete: scripts that are clearly historical one-offs (per round-1 review: `backfill_march.py`, `delete_orphans.py`, `reset_failed.py`, `test_extraction.py`, `run_with_primary.py`)
- Keep + document: any script that's genuinely useful for ongoing ops; move usage notes into `docs/runbook.md` (created later)
- Ambiguous (`clean_slate.py`, `full_resync.py`, `migrate_stages.py`, `seed_entities.py`, `seed_outlook.py`): for each, decide keep-or-delete based on whether ongoing ops needs it. When in doubt, delete — git history preserves them.

**Step 1:** Read each file and tag.

**Step 2:** Delete the one-offs.

**Step 3:** Run tests.

**Step 4:** Commit.

```bash
git commit -m "chore: triage scripts/ — delete historical one-offs"
```

---

### Task C.3: Strip `entrypoint.sh` Mongo-primary detection

**Files:**
- Modify: `entrypoint.sh`

**Step 1:** Read the current script (60 lines).

**Step 2:** Replace lines 13–56 (the Mongo primary detection block) with no-op behavior. The whole script becomes:

```bash
#!/bin/bash
# Container entrypoint. We're on Atlas SRV; no proxy primary detection needed.
set -e
exec "$@"
```

**Step 3:** Smoke-test by building and running the image:

```bash
docker build -t gic-test:local .
docker run --rm gic-test:local --help
```

**Step 4:** Run pytest.

**Step 5:** Commit.

```bash
git commit -m "chore(docker): strip entrypoint.sh Mongo primary detection (Atlas SRV makes it unreachable)"
```

---

## Phase D: Infrastructure-as-Code

### Task D.1: Write `docker-compose.yml`

**Files:**
- Create: `docker-compose.yml` (verbatim per design section 1.5, with the `stop_grace_period: 60s` and `/healthz` corrections from round 3/4)

**Step 1:** Copy the YAML from the design doc section 1.5 to a new `docker-compose.yml` in repo root.

**Step 2:** Lint the YAML.

```bash
docker compose config -q
# Expected: no output (valid)
```

**Step 3:** Smoke-test (with stub env file) that all four services parse correctly.

```bash
echo "MONGODB_URI=mongodb://test" > .env.aws
echo "GRAPH_USER_EMAIL=test@x.y" >> .env.aws
echo "UNISOFT_PROXY_URL=http://test" >> .env.aws
echo "UNISOFT_TASK_GROUP_ID_NEWBIZ=1" >> .env.aws
echo "UNISOFT_TASK_GROUP_ID_WC=2" >> .env.aws
echo "GOOGLE_CLOUD_PROJECT=test" >> .env.aws
docker compose config | head -50
rm .env.aws
```

**Step 4:** Commit.

```bash
git commit -m "feat(docker): add docker-compose.yml with 4 services (api, sync, processing, automation)"
```

---

### Task D.2: Copy and extend `aws-env-loader.sh`

**Files:**
- Create: `scripts/aws-env-loader.sh` (copied from `bot-service/scripts/aws-env-loader.sh`)

**Step 1:** Copy the bot-service version.

```bash
mkdir -p scripts
cp /Users/home/Repositories/bot-service/scripts/aws-env-loader.sh scripts/aws-env-loader.sh
chmod +x scripts/aws-env-loader.sh
```

**Step 2:** Edit `PARAM_MAP` (around line 166) to add the GIC-specific entries from the design doc (annotated with `# existing` and `# NEW (Phase 1.0 ...)` markers — keep them verbatim from the design).

**Step 3:** Smoke-test against AWS dev (read-only).

```bash
AWS_ENV=dev AWS_SERVICE=gic-email-intelligence bash scripts/aws-env-loader.sh /tmp/test.env
cat /tmp/test.env | grep -E "PIPELINE_STAGES|PAUSE_SYNC|UNISOFT_PROXY_URL"
# After Phase E populates the params, this will show real values. For now, may be empty — that's OK.
rm /tmp/test.env
```

**Step 4:** Commit.

```bash
git commit -m "feat(deploy): add aws-env-loader.sh with GIC-specific PARAM_MAP entries"
```

---

### Task D.3: Write `.github/workflows/build.yml`

**Files:**
- Create: `.github/workflows/build.yml` (modeled on `bot-service/.github/workflows/build.yml`)

**Step 1:** Read bot-service's build.yml as template.

```bash
cat /Users/home/Repositories/bot-service/.github/workflows/build.yml
```

**Step 2:** Create the GIC version, swapping `bot-service` → `gic-email-intelligence` everywhere. Keep:
- Triggers: push to `main`, `workflow_dispatch`
- Jobs: build (ubuntu-latest, push to Docker Hub `indemneng/gic-email-intelligence:main` and `:main-${{ github.run_number }}`), deploy (`[self-hosted, linux, x64, dev]`, runs `aws-env-loader.sh`, copies compose+env, `docker compose pull && up -d`)
- Slack notifications on failure

**Step 3:** Validate the YAML.

```bash
gh workflow view build.yml --repo indemn-ai/gic-email-intelligence 2>/dev/null || echo "workflow not yet pushed — that's expected"
yamllint .github/workflows/build.yml || echo "(yamllint optional; manual review)"
```

**Step 4:** Commit.

```bash
git commit -m "ci: add build.yml for dev branch (build + push + deploy to dev-services)"
```

---

### Task D.4: Write `.github/workflows/build-prod.yml`

Same as D.3 but for the `prod` branch and `prod` runner labels.

**Step 1:** Copy `build.yml` to `build-prod.yml`.

**Step 2:** Replace `main` → `prod`, `dev` → `prod`, label `[self-hosted, linux, x64, dev]` → `[self-hosted, linux, x64, prod]`.

**Step 3:** Commit.

```bash
git commit -m "ci: add build-prod.yml for prod branch (deploy to prod-services)"
```

---

### Task D.5: Add Trivy image-scanning workflow

**Files:**
- Create: `.github/workflows/docker-image-scanning.yml`

**Step 1:** Copy from `/Users/home/Repositories/bot-service/.github/workflows/docker-image-scanning.yml`.

**Step 2:** Replace service-name references.

**Step 3:** Commit.

```bash
git commit -m "ci: add Trivy image vulnerability scanning workflow"
```

---

### Task D.6: Add `.github/dependabot.yml` and `CODEOWNERS`

**Files:**
- Create: `.github/dependabot.yml`
- Create: `.github/CODEOWNERS`

**Step 1:** `dependabot.yml` covering Python (uv lock), GitHub Actions, Docker base images. Weekly schedule.

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
```

**Step 2:** `CODEOWNERS` listing Craig and Dhruv on all files.

```
* @craig-indemn @dhruv-indemn
```

(adjust GitHub usernames as appropriate)

**Step 3:** Commit.

```bash
git commit -m "chore(repo): add dependabot config and CODEOWNERS"
```

---

### Task D.7: Add `README.md` and `docs/runbook.md`

**Files:**
- Modify or create: `README.md` (replace existing if too sparse)
- Create: `docs/runbook.md`

**Step 1:** README covers: what the service is, local dev quickstart, env var reference (with link to AWS Secrets Manager paths), how to run tests, how deploy works.

**Step 2:** `docs/runbook.md` covers the day-2 ops playbooks listed in the design's Operational Readiness section: failed-automation triage, single-email re-process, skill prompt change, LLM provider failover, Unisoft proxy down, Atlas pool exhausted, stale-claim recovery reconciliation. Use the exact CLI commands verified in round 4 (positional `email_id`, `gic submissions check-duplicate`, etc.).

**Step 3:** Commit.

```bash
git commit -m "docs: add README and operational runbook"
```

---

## Phase E: AWS Infrastructure

**[NEEDS USER APPROVAL]** All steps in Phase E modify AWS state. Pause and confirm with Craig before each one. Production-touching steps are in Phase I (cutover); Phase E is dev-only.

### Task E.1: Populate AWS Secrets Manager (dev)

For each entry in the design doc's Secrets Manager table under `indemn/dev/gic-email-intelligence/*`:

**Step 1:** Pull the current Railway dev value (audit step):

```bash
cd /Users/home/Repositories/gic-email-intelligence
railway variables --environment development --service api | grep -i mongodb_uri
# Note the value; we'll write it to Secrets Manager
```

**Step 2:** Create or update the secret in AWS — idempotent helper so partial-failures are safe to retry.

```bash
upsert_secret() {
  local name="$1"
  local value="$2"
  if aws secretsmanager describe-secret --secret-id "$name" >/dev/null 2>&1; then
    aws secretsmanager put-secret-value --secret-id "$name" --secret-string "$value"
  else
    aws secretsmanager create-secret --name "$name" --secret-string "$value"
  fi
}

upsert_secret indemn/dev/gic-email-intelligence/mongodb-uri "<value-from-railway>"
```

Repeat with the same `upsert_secret` helper for: `graph-credentials` (JSON), `anthropic-api-key`, `google-cloud-sa-json`, `unisoft-api-key`, `jwt-secret`, `tiledesk-db-uri`, `api-token`, `langsmith-api-key`.

**Step 3:** Verify all secrets are retrievable:

```bash
aws secretsmanager list-secrets --filters Key=name,Values=indemn/dev/gic-email-intelligence | jq '.SecretList[].Name'
```

(no commit; AWS state)

---

### Task E.2: Populate AWS Parameter Store (dev)

For each entry in the design doc's Parameter Store table under `/indemn/dev/gic-email-intelligence/*`:

**Step 1:** Create or update each param. **Always pass `--overwrite`** so retries are safe.

```bash
aws ssm put-parameter \
  --name /indemn/dev/gic-email-intelligence/llm-provider \
  --value google_vertexai \
  --type String \
  --overwrite
```

Repeat for all entries in the design doc's PARAM_MAP table (17 GIC-specific + verify shared `mongodb-db`, `llm-provider`, etc. already exist at `/indemn/dev/`). Note: Parameter Store uses **leading slash** (`/indemn/dev/...`); Secrets Manager does NOT (`indemn/dev/...`). Two different conventions — get them right.

**Step 2:** Verify with the loader script:

```bash
AWS_ENV=dev AWS_SERVICE=gic-email-intelligence bash scripts/aws-env-loader.sh /tmp/check.env
grep -E "PIPELINE_STAGES|PAUSE_SYNC|UNISOFT_PROXY_URL|GRAPH_USER_EMAIL" /tmp/check.env
# Expected: all expected env vars present with correct values
rm /tmp/check.env
```

---

### Task E.3: Update Atlas allowlist (dev EIPs)

**[NEEDS USER APPROVAL]**

**Step 1:** Log into Atlas → Network Access on the `dev-indemn` project.

**Step 2:** Add `44.196.55.84/32` (dev-services) and `98.88.11.14/32` (prod-services) — even though only dev is being soaked, prod-services entry needs to be in place before prod cutover, and Atlas allowlist propagation can take minutes.

**Step 3:** Verify from a dev-services session:

```bash
aws ssm start-session --target i-0fde0af9d216e9182
# inside the session:
sudo docker run --rm mongo:6 mongosh "mongodb+srv://dev-indemn:wJnKmz4P0q39GpXZ@dev-indemn.mifra5.mongodb.net/gic_email_intelligence" --eval 'db.runCommand({ping:1})'
# Expected: { ok: 1, ... }
```

---

### Task E.4: Update Unisoft proxy SG (`sg-04cc0ee7a09c15ffb`)

**[NEEDS USER APPROVAL]**

**Step 1:** Find the SGs of dev-services and prod-services:

```bash
aws ec2 describe-instances --instance-ids i-0fde0af9d216e9182 i-00ef8e2bfa651aaa8 \
  --query 'Reservations[].Instances[].{Id:InstanceId, Sg:SecurityGroups[0].GroupId}'
```

**Step 2:** Add SG-reference rules to `sg-04cc0ee7a09c15ffb`:

```bash
DEV_SG=<from step 1>
PROD_SG=<from step 1>

aws ec2 authorize-security-group-ingress \
  --group-id sg-04cc0ee7a09c15ffb \
  --protocol tcp --port 5000 --source-group $DEV_SG
aws ec2 authorize-security-group-ingress \
  --group-id sg-04cc0ee7a09c15ffb \
  --protocol tcp --port 5001 --source-group $DEV_SG
aws ec2 authorize-security-group-ingress \
  --group-id sg-04cc0ee7a09c15ffb \
  --protocol tcp --port 5000 --source-group $PROD_SG
aws ec2 authorize-security-group-ingress \
  --group-id sg-04cc0ee7a09c15ffb \
  --protocol tcp --port 5001 --source-group $PROD_SG
```

**Step 3:** Verify connectivity from dev-services:

```bash
aws ssm start-session --target i-0fde0af9d216e9182
# inside session:
curl -v http://172.31.23.146:5001/api/health
# Expected: 200 with proxy health response
```

---

### Task E.5: Verify GitHub OIDC role permissions

**[NEEDS USER APPROVAL]** (read-only verification, but also amend if needed)

**Step 1:** Find the GitHub OIDC role.

```bash
aws iam list-roles --query "Roles[?contains(RoleName,'github-actions')].RoleName"
```

**Step 2:** Inspect attached policies for read access to `indemn/dev/gic-email-intelligence/*` and `indemn/prod/gic-email-intelligence/*`.

**Step 3:** If missing, add a policy that grants those actions. (May be covered by an existing wildcard like `indemn/dev/*`.)

---

### Task E.6: Verify self-hosted runners online

**Step 1:** Query GitHub for runners on the GIC repo (which is empty — the runners are at the org level or repo level).

```bash
gh api repos/indemn-ai/gic-email-intelligence/actions/runners --jq '.runners[] | {name, status, busy, labels: [.labels[].name]}'
```

If no runners are registered to this specific repo, register the dev-services and prod-services runners to it (they may need to be added through the GitHub UI under Settings → Actions → Runners).

**Step 2:** Test by queuing a no-op workflow once Phase F's initial commit is pushed.

---

## Phase F: Push to `indemn-ai/gic-email-intelligence`

### Task F.1: Squash and push initial commit

**Step 0 (precondition): Verify the worktree branch contains only our migration work, not new commits from the other session.** If the monitoring session pushed bug-fixes to `main` of the personal repo while we were doing Phase B–D, we want to (a) know, and (b) decide whether to merge them in or cherry-pick later.

```bash
cd /Users/home/Repositories/gic-email-intelligence-migration
git fetch origin main
# Check what's on origin/main that's NOT on migration/indemn-infra
git log --oneline origin/main ^migration/indemn-infra
# Expected: empty. If non-empty, those are new commits from the other session.
```

If non-empty:
- For small bug-fixes, merge `origin/main` into `migration/indemn-infra`, retest, then proceed to F.1 Step 1.
- For larger changes, pause and discuss with Craig before squashing.

**Step 1:** Confirm all Phase B/C/D commits are present and tests pass.

```bash
cd /Users/home/Repositories/gic-email-intelligence-migration
git log --oneline | head -30
uv run pytest -q
```

**Step 2:** Soft-reset to baseline and squash into one commit.

```bash
BASELINE=$(cat /tmp/migration-baseline-sha.txt)
git reset --soft $BASELINE
git commit -m "chore: initial commit (migration from craig-indemn/gic-email-intelligence)

Squashed from migration/indemn-infra branch. See projects/gic-email-intelligence/artifacts/2026-04-27-migration-to-indemn-infrastructure-design.md for context.

Includes Phase 1.0 code work:
- SIGTERM-aware loop wrapper (cli/loop.py)
- --loop --interval flags on sync, automate run, automate process
- PAUSE_SYNC config + enforcement
- /healthz endpoint + rate-limit exemption
- Stale-claim recovery for automation_status (with fail-closed duplicate check)
- CORS_ORIGINS env-driven with whitespace stripping
- GRAPH_USER_EMAIL env-driven + skill prompt placeholder substitution
- Task group IDs and PUBLIC_BASE_URL env-driven
- UNISOFT_PROXY_URL hardcoded fallbacks removed (now required env)
- Healthcheck path moved to /healthz in Dockerfile and docker-compose

Cleanup:
- Removed addin-test/, data/, root *.html, *.deprecated, one-off scripts
- Stripped entrypoint.sh dead code (Mongo primary detection)

Infrastructure:
- docker-compose.yml with 4 services
- .github/workflows/{build,build-prod,docker-image-scanning}.yml
- aws-env-loader.sh with GIC PARAM_MAP entries
- dependabot.yml + CODEOWNERS
- README.md + docs/runbook.md
"
```

**Step 3:** Push to indemn remote.

```bash
git push indemn migration/indemn-infra:main
```

**Step 4:** Verify on GitHub.

```bash
gh repo view indemn-ai/gic-email-intelligence
gh api repos/indemn-ai/gic-email-intelligence/commits --jq '.[0].commit.message' | head -10
```

---

### Task F.2: Set branch protection on `main` and `prod`

**[NEEDS USER APPROVAL]** for production-touching settings.

**Step 1:** Branch protection on `main`. Use `--input` with a JSON file because nested `--field` arrays are unreliable.

```bash
cat > /tmp/branch-protection.json <<'EOF'
{
  "required_status_checks": {"strict": true, "contexts": ["build"]},
  "enforce_admins": false,
  "required_pull_request_reviews": {"required_approving_review_count": 1, "dismiss_stale_reviews": false},
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

gh api -X PUT repos/indemn-ai/gic-email-intelligence/branches/main/protection --input /tmp/branch-protection.json
```

**Step 2:** Create `prod` branch from `main`, then apply the same protection.

```bash
MAIN_SHA=$(gh api repos/indemn-ai/gic-email-intelligence/branches/main --jq '.commit.sha')
gh api -X POST repos/indemn-ai/gic-email-intelligence/git/refs \
  -f "ref=refs/heads/prod" -f "sha=$MAIN_SHA"

gh api -X PUT repos/indemn-ai/gic-email-intelligence/branches/prod/protection --input /tmp/branch-protection.json
```

---

### Task F.3: Rewire Amplify dev branch

**Step 1:** In the Amplify console (or CLI), update `d244t76u9ej8m0` GitHub source from `craig-indemn/gic-email-intelligence` to `indemn-ai/gic-email-intelligence`.

```bash
aws amplify update-app --app-id d244t76u9ej8m0 \
  --repository https://github.com/indemn-ai/gic-email-intelligence
# May need to re-auth GitHub OAuth in console.
```

**Step 2:** Set `VITE_API_BASE` env var on the `main` branch (Amplify env vars are scoped per-branch).

```bash
aws amplify update-branch --app-id d244t76u9ej8m0 --branch-name main \
  --environment-variables VITE_API_BASE=https://api-dev.gic.indemn.ai
```

If the Phase G ingress (ALB / Caddy) hasn't been wired yet, point at the dev-services EIP directly: `VITE_API_BASE=http://44.196.55.84:8080` — and update once the canonical hostname is live.

**Step 3:** Trigger a build of the `main` branch.

```bash
aws amplify start-job --app-id d244t76u9ej8m0 --branch-name main --job-type RELEASE
```

**Step 4:** Wait, then verify build is green.

```bash
aws amplify list-jobs --app-id d244t76u9ej8m0 --branch-name main | jq '.jobSummaries[0]'
```

---

## Phase G: Dev Deployment & Soak

### Task G.1: First CI deploy to dev-services

**Step 1:** Push to `main` of `indemn-ai/gic-email-intelligence` triggers `build.yml`.

```bash
gh run watch
# Wait for build → push to Docker Hub → deploy to dev-services
```

**Step 2:** Verify on dev-services.

```bash
aws ssm start-session --target i-0fde0af9d216e9182
# inside:
cd /opt/gic-email-intelligence
docker compose ps
# Expected: api, sync-cron, processing-cron, automation-cron all "running"
docker compose logs api | tail -50
docker compose logs sync-cron | tail -50
```

**Step 3:** Hit the API.

```bash
# from dev-services:
curl -v http://localhost:8080/healthz
# Expected: 200 {"status":"ok"}
curl -v http://localhost:8080/api/health
# Expected: 200 with status: ok and DB stats
```

---

### Task G.2: Verify pause flags fire (PAUSE_*=true initially)

**Step 1:** In Parameter Store, ensure `pause-sync`, `pause-processing`, `pause-automation` are all set to `true` for dev:

```bash
aws ssm put-parameter --name /indemn/dev/gic-email-intelligence/pause-sync --value true --type String --overwrite
aws ssm put-parameter --name /indemn/dev/gic-email-intelligence/pause-processing --value true --type String --overwrite
aws ssm put-parameter --name /indemn/dev/gic-email-intelligence/pause-automation --value true --type String --overwrite
```

**Step 2:** Restart the cron containers to pick up the change.

```bash
cd /opt/gic-email-intelligence
docker compose restart sync-cron processing-cron automation-cron
```

**Step 3:** Watch logs — each cron should log "paused, skipping tick" every 300/900 seconds.

```bash
docker compose logs -f sync-cron processing-cron automation-cron
```

---

### Task G.3: Pause Railway dev sync, unpause EC2 dev sync

**[COORDINATE WITH MONITORING SESSION]** — make sure no manual sync invocations are running on Railway during the swap.

**Step 1:** Pause Railway dev sync.

```bash
cd /Users/home/Repositories/gic-email-intelligence
railway variables set PAUSE_SYNC=true --environment development --service sync
# Wait 5+ minutes for any in-flight Railway tick to drain
sleep 360
```

**Step 2:** Unpause EC2 dev sync.

```bash
aws ssm put-parameter --name /indemn/dev/gic-email-intelligence/pause-sync --value false --type String --overwrite
# EC2 cron's settings reload picks it up on next tick
```

**Step 3:** Watch sync_state advance.

```bash
mongosh "mongodb+srv://dev-indemn:..." --eval '
  setInterval(() => {
    var s = db.sync_state.findOne({_id:"outlook_sync"});
    print(new Date(), s.last_sync_at);
  }, 30000);
'
```

Pass criterion: `last_sync_at` advances on every tick (every 5 min). Soak 24h.

---

### Task G.4: Verify no duplicates over the soak window

```bash
mongosh "mongodb+srv://..." --eval '
  var dupes = db.emails.aggregate([
    {$match: {received_at: {$gte: new Date(Date.now()-24*3600000)}}},
    {$group: {_id: "$graph_message_id", n: {$sum: 1}}},
    {$match: {n: {$gt: 1}}},
    {$count: "duplicates"}
  ]).toArray();
  print(JSON.stringify(dupes));
'
# Expected: [] or {duplicates: 0}
```

If duplicates appear, sync was double-running. **Abort + rollback procedure:**

```bash
# 1. Pause EC2 dev sync IMMEDIATELY
aws ssm put-parameter --name /indemn/dev/gic-email-intelligence/pause-sync --value true --type String --overwrite

# 2. Confirm Railway dev sync is also paused (may have been un-paused by mistake)
railway variables --environment development --service sync | grep PAUSE_SYNC

# 3. Identify the duplicates and the time window
mongosh "..." --eval '
  db.emails.aggregate([
    {$match: {received_at: {$gte: new Date(Date.now()-24*3600000)}}},
    {$group: {_id: "$graph_message_id", n: {$sum: 1}, ids: {$push: "$_id"}}},
    {$match: {n: {$gt: 1}}}
  ]).forEach(d => printjson(d));
'

# 4. Decide remediation: keep the older _id (first sync), delete the newer.
#    Do NOT bulk-delete without inspecting a sample first.

# 5. Investigate the root cause before unpausing either side.
```

Common root causes: (a) Railway pause flag didn't take effect (cron container in mid-tick), (b) settings reload race in EC2 sync, (c) `sync_state` rewind from clobbered token.

---

### Task G.5: Unpause processing on EC2 dev

**Step 1:** Pause Railway dev processing first (defensive — same atomic-claim story should protect us, but pause-first is the rule).

```bash
railway variables set PAUSE_PROCESSING=true --environment development --service processing
```

**Step 2:** Unpause EC2 dev processing.

```bash
aws ssm put-parameter --name /indemn/dev/gic-email-intelligence/pause-processing --value false --type String --overwrite
```

**Step 3:** Watch the processing backlog drain.

```bash
mongosh "..." --eval '
  setInterval(() => {
    var p = db.emails.countDocuments({processing_status:"pending"});
    var c = db.emails.countDocuments({processing_status:"complete", processing_completed_at:{$gte: new Date(Date.now()-300000)}});
    print(new Date(), "pending:", p, "completed last 5min:", c);
  }, 30000);
'
```

Pass criterion: backlog trends to zero, no stuck `processing_status: processing` past 5 min.

---

### Task G.6: Unpause automation on EC2 dev (UAT Unisoft)

**Step 1:** Pause Railway dev automation.

```bash
railway variables set PAUSE_AUTOMATION=true --environment development --service automation
```

**Step 2:** Unpause EC2 dev automation. Cron points at UAT Unisoft (port 5000).

```bash
aws ssm put-parameter --name /indemn/dev/gic-email-intelligence/pause-automation --value false --type String --overwrite
```

**Step 3:** Watch automation throughput.

```bash
mongosh "..." --eval '
  setInterval(() => {
    var c = db.emails.countDocuments({automation_status:"complete", automation_completed_at:{$gte: new Date(Date.now()-3600000)}});
    var f = db.emails.countDocuments({automation_status:"failed", automation_completed_at:{$gte: new Date(Date.now()-3600000)}});
    print(new Date(), "completed last hour:", c, "failed:", f);
  }, 60000);
'
```

Pass criterion: at least 3 emails complete with populated `unisoft_quote_id` within 30 min of arrival; corresponding Quotes visible in UAT Unisoft with attachments + activity + notification email delivered.

---

## Phase H: Operational Readiness (parallel with G)

### Task H.1: Wire Datadog alerts **[NEEDS USER APPROVAL on routing decision]**

**Step 0 (blocking):** Confirm with Craig which alert-routing channel to use. Options:
- **PagerDuty** — does Indemn have a PagerDuty account / integration set up? If yes, get the integration key and the on-call schedule.
- **Slack-to-phone** — Slack channel + Slack's "call when mentioned" feature, scoped to Craig.
- **Email-only** — fallback for non-critical alerts. Not appropriate for P1.

Block H.1 progress on this decision; do not proceed with monitor creation until decided.

**Step 1:** Create each monitor in the design's alert table via Datadog UI or terraform-equivalent. Capture each monitor URL.

**Step 2:** Wire each to the routing decision from Step 0.

**Step 3:** Smoke-test by deliberately triggering one (e.g., scale `automation-cron` to 0 in dev briefly to fire the "container down" alert), confirm the page lands.

**Step 4:** Record the dashboard URLs in the runbook (`docs/runbook.md`) and add them to the cutover Slack thread so on-call has them in I.10.

---

### Task H.2: Verify Atlas backup tier

**Step 1:** Check the cluster tier and backup config in Atlas UI for `dev-indemn`.

**Step 2:** Confirm continuous backup is enabled with at least 30-day retention. If not, **[NEEDS USER APPROVAL]** to upgrade.

---

### Task H.3: Document encryption posture

**Files:**
- Create: `docs/security.md`

Document: in transit (HTTPS everywhere), at rest (Atlas SSE, S3 SSE-S3 — verify and enable if not). One page.

---

### Task H.4: Wire S3 versioning + lifecycle on `indemn-gic-attachments`

```bash
aws s3api get-bucket-versioning --bucket indemn-gic-attachments
# If not enabled:
aws s3api put-bucket-versioning --bucket indemn-gic-attachments \
  --versioning-configuration Status=Enabled
```

---

## Phase I: Prod Cutover

**[NEEDS USER APPROVAL]** for every step in this phase.

Follow the exact runbook in the design doc's "Cutover Runbook" section. Each numbered step there is a task here.

### Task I.1: T-24h customer comms

Email JC + Maribel: window, expected zero downtime, what to look for, Craig's phone.

---

### Task I.2: Populate AWS Secrets Manager + Parameter Store (prod)

Same as E.1 + E.2 but for `indemn/prod/gic-email-intelligence/*` and `/indemn/prod/...`. Pull values from `railway variables --environment production`.

**Audit step:** Screenshot all Railway prod env vars and diff against the populated Secrets Manager + Parameter Store layout. Any mismatch is a pre-cutover blocker.

---

### Task I.3: Atlas + Unisoft SG (already covered in E.3, E.4)

Verify the prod-services EIP is in the Atlas allowlist and the SG-reference rule for `prod-services` SG is on `sg-04cc0ee7a09c15ffb`.

---

### Task I.4: Push `prod` branch, deploy to prod-services

```bash
cd /Users/home/Repositories/gic-email-intelligence-migration
git push indemn migration/indemn-infra:prod
gh run watch
```

Containers come up with all `pause-*=true` initially.

---

### Task I.5: Atlas snapshot

In Atlas UI: Backups → On-Demand Snapshot of the `gic_email_intelligence` database. Note the snapshot ID + timestamp in the cutover Slack thread.

---

### Task I.6: T+0 customer comms

Slack: "Migration starting now. Expected ~1 hour. No downtime expected."

---

### Task I.7: Pause Railway prod (all 3 cron services)

```bash
railway variables set PAUSE_SYNC=true PAUSE_PROCESSING=true PAUSE_AUTOMATION=true --environment production --service sync
railway variables set PAUSE_PROCESSING=true --environment production --service processing
railway variables set PAUSE_AUTOMATION=true --environment production --service automation
sleep 360  # wait one full sync interval for any in-flight tick to drain
```

---

### Task I.8: DNS flip on `api.gic.indemn.ai`

**Pre-set TTL to 60s 24h prior.** Cutting TTL during the cutover window doesn't help because resolvers are already caching at the old TTL.

**Step 1 (T-24h, run during pre-cutover prep):** Lower the TTL to 60s.

```bash
ZONE_ID=$(aws route53 list-hosted-zones --query "HostedZones[?Name=='indemn.ai.'].Id" --output text)
# Get the current record value to preserve it
CURRENT=$(aws route53 list-resource-record-sets --hosted-zone-id "$ZONE_ID" \
  --query "ResourceRecordSets[?Name=='api.gic.indemn.ai.']" --output json)
echo "$CURRENT" > /tmp/api-gic-record-pre-cutover.json   # save for rollback

# Build a CHANGE batch that lowers TTL to 60 (do not change the value yet)
# (The exact JSON depends on whether it's an ALIAS or CNAME; inspect /tmp/api-gic-record-pre-cutover.json)
```

**Step 2 (T-0):** Stage the new value pointing at prod-services. The exact target depends on the ingress decision in the open items (ALB vs Caddy on host vs direct EIP). For an ALB target:

```bash
# Pre-write the change batch JSON
cat > /tmp/api-gic-cutover.json <<'EOF'
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "api.gic.indemn.ai.",
      "Type": "A",
      "AliasTarget": {
        "HostedZoneId": "<ALB-zone-id>",
        "DNSName": "<ALB-dns-name>",
        "EvaluateTargetHealth": true
      }
    }
  }]
}
EOF

# Pre-write the rollback change batch (back to the prior value, captured in step 1)
cat > /tmp/api-gic-rollback.json <<EOF
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": $(jq '.[0]' /tmp/api-gic-record-pre-cutover.json)
  }]
}
EOF

# Both files staged — only execute the cutover at the right moment in the runbook
```

**Step 3:** Execute the cutover.

```bash
aws route53 change-resource-record-sets --hosted-zone-id "$ZONE_ID" --change-batch file:///tmp/api-gic-cutover.json
# Note the ChangeId in the output
```

**Step 4:** Confirm propagation.

```bash
dig +short api.gic.indemn.ai @8.8.8.8
dig +short api.gic.indemn.ai @1.1.1.1
# Expected: resolves to the new ALB / EIP within ~60s of the change
```

**Rollback (if needed):**

```bash
aws route53 change-resource-record-sets --hosted-zone-id "$ZONE_ID" --change-batch file:///tmp/api-gic-rollback.json
```

---

### Task I.9: Unpause EC2 prod crons one at a time

Same sequence as G.3, G.5, G.6 but on prod-services + Parameter Store prod scope. 5-minute soak between each.

---

### Task I.10: Verify end-to-end (success criterion from design)

- Real `agent_submission` arrives within window OR send a controlled test
- `processing_status: complete` within 5 min
- `automation_status: complete` with `unisoft_quote_id` within 30 min
- Quote in Unisoft prod with attachments + activity + notification
- Datadog clean

If any fail and 90-min window approaching: roll back per the runbook (pause EC2 first, flip DNS, unpause Railway).

---

### Task I.11: Remove Railway IPs from allowlists

```bash
# Atlas: remove 162.220.234.15 from allowlist (via Atlas UI on the dev-indemn project)

# Unisoft proxy SG: revoke rules for 162.220.234.15
# Use `|| true` so re-running is harmless if the rule is already gone
aws ec2 revoke-security-group-ingress --group-id sg-04cc0ee7a09c15ffb \
  --protocol tcp --port 5000 --cidr 162.220.234.15/32 || true
aws ec2 revoke-security-group-ingress --group-id sg-04cc0ee7a09c15ffb \
  --protocol tcp --port 5001 --cidr 162.220.234.15/32 || true

# Verify the rules are gone
aws ec2 describe-security-groups --group-ids sg-04cc0ee7a09c15ffb \
  --query "SecurityGroups[].IpPermissions[?ToPort==\`5000\` || ToPort==\`5001\`].IpRanges[].CidrIp"
# Expected: 162.220.234.15/32 not present
```

---

### Task I.12: T+0 done customer comms

Slack: "Migration complete. System on new infra. Flag anything unusual."

---

## Phase J: 7-day Soak + Tear-down

### Task J.1: Daily monitoring

For 7 days, daily check:
- Datadog dashboard
- `automation_status: failed` count
- `failed_recovery_review` count (must be 0)
- Atlas connection-pool utilization
- Container restart count

---

### Task J.2: Destroy Railway services

**[NEEDS USER APPROVAL]**

After 7 clean days. Note: Railway CLI command names have changed over versions — verify with `railway --help` first. As of Railway CLI v3+, deletion is via `railway service delete <name>` (or the dashboard's Settings → Danger Zone for safety). `railway down` only stops, doesn't destroy.

```bash
cd /Users/home/Repositories/gic-email-intelligence
railway --version  # confirm v3+ syntax
railway link --environment production --project gic-email-intelligence

# Verify what's running before destroying
railway service list

# Destroy each service. Prefer the dashboard for the final confirm step
# given how irreversible this is.
railway service delete api
railway service delete sync
railway service delete processing
railway service delete automation
# Repeat for development environment if no longer needed
```

---

### Task J.3: Archive `craig-indemn/gic-email-intelligence`

**[NEEDS USER APPROVAL]**

```bash
gh api -X PATCH repos/craig-indemn/gic-email-intelligence \
  --field archived=true
```

Update the personal repo's README to point at `indemn-ai/gic-email-intelligence` as the new home.

---

## Phase K: Post-cutover Follow-ups (separate workstream)

These are the items from the design's "Out of Scope" section. Track each as a separate ticket; do not bundle into this migration.

1. Phase 2: Atlas cluster relocation (`dev-indemn` → `prod-indemn`)
2. Outlook add-in to Amplify under `addin.gic.indemn.ai`
3. Skill prompt registry / versioning
4. Deepagents `LocalShellBackend` stdin patch — upstream PR or fork
5. LangSmith tracing fix
6. Multi-tenancy refactor (when customer #2 is real)
7. Repo rename to `email-intelligence` (only if 6)
8. Atlas posture review — IAM, audit logs
9. Datadog APM (`ddtrace`) for GIC services
10. Image vulnerability scanning beyond Dependabot
11. Private container registry (ECR) as Docker Hub fallback
12. Unisoft proxy HA (second instance + failover)

---

## Plan Summary

| Phase | Task count | User approval needed | Estimated time |
|-------|-----------|----------------------|----------------|
| A | 2 | No | 30 min |
| B | 12 | No | 1.5–2 days (TDD code work) |
| C | 3 | No | 2 hours |
| D | 7 | No | 4 hours |
| E | 6 | Yes (dev AWS state) | 4 hours |
| F | 3 | Yes (Amplify rewire, branch protection) | 2 hours |
| G | 6 | No (dev) | 24–48h soak |
| H | 4 | Mixed | 1 day, parallel with G |
| I | 12 | Yes (every step is prod) | 1.5 hours window + 24h soak |
| J | 3 | Yes (Railway tear-down) | 7-day delay then 30 min |
| K | 12 | n/a (separate workstream) | post-cutover |

**Critical path:** A → B → C → D → E → F → G (24h soak) → I (cutover window) → J (7-day soak + tear-down).

**Parallelizable:** H runs alongside G. K is post-migration.

**Total wall-clock estimate:** ~10 days end to end, dominated by the 24h dev soak and 7-day prod soak. Active hands-on time: ~4 days spread out.
