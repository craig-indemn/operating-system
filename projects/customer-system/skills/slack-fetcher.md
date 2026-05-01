# Slack Fetcher

Scheduled deterministic CLI executor. Runs `indemn slackmessage fetch-new` on every cron tick to incrementally pull new SlackMessages since the last per-channel watermark across all channels the bot is invited to (public + private). DMs out of scope.

## Command

```bash
indemn slackmessage fetch-new
```

## Why this exists

Per TD-1: each source adapter runs autonomously on its own schedule. Slack-Fetcher fires every 5 minutes; the Slack adapter handles incremental via per-channel `since` watermark (Bug #46-corrected fall-through to `posted_at`). Fetched SlackMessages sit at `received` for downstream classifiers (TD-2's SlackClassifier).

Executed via Bug #40's `cron_runner` actor mode — no LLM, no deepagents agent. The harness shell-execs the `## Command` line directly, parses the JSON response, marks the message complete (or failed if the adapter returns errors). Content above the fence is human-readable context; only the fenced command is executed.

Backfills go through a human-driven CLI invocation (`indemn slackmessage fetch-new --data '{"since": "..."}'`), not this scheduled actor.
