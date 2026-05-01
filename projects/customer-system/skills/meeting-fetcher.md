# Meeting Fetcher

Scheduled deterministic CLI executor. Runs `indemn meeting fetch-new` on every cron tick to incrementally pull new Google Meet conference records (with structured transcripts, Gemini smart notes, recordings, Calendar attendees) across all 11 team accounts.

## Command

```bash
indemn meeting fetch-new
```

## Why this exists

Per TD-1: each source adapter runs autonomously on its own schedule. Meeting-Fetcher fires every 15 minutes; the Google Workspace adapter handles incremental via per-account `since` watermark. Fetched Meetings sit at `logged` for downstream classifiers (TD-2's MeetingClassifier).

Executed via Bug #40's `cron_runner` actor mode — no LLM, no deepagents agent. The harness shell-execs the `## Command` line directly, parses the JSON response, marks the message complete (or failed if the adapter returns errors). Content above the fence is human-readable context; only the fenced command is executed.

Backfills go through a human-driven CLI invocation (`indemn meeting fetch-new --data '{"since": "..."}'`), not this scheduled actor.
