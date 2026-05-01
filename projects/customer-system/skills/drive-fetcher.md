# Drive Fetcher

Scheduled deterministic CLI executor. Runs `indemn document fetch-new` on every cron tick to incrementally pull new and modified Drive Documents (the integration-owner sees everything in the org's shared Drive scope).

## Command

```bash
indemn document fetch-new
```

## Why this exists

Per TD-1: each source adapter runs autonomously on its own schedule. Drive-Fetcher fires hourly; the Google Workspace adapter queries by `modifiedTime > last_watermark` (Bug #46-corrected fall-through to `created_date`). Documents are created with `company = null` by default — lazy classification happens later (at IE touchpoint extraction or manual via UI).

Executed via Bug #40's `cron_runner` actor mode — no LLM, no deepagents agent. The harness shell-execs the `## Command` line directly, parses the JSON response, marks the message complete (or failed if the adapter returns errors). Content above the fence is human-readable context; only the fenced command is executed.

Backfills go through a human-driven CLI invocation (`indemn document fetch-new --data '{"since": "..."}'`), not this scheduled actor. Drive volume can be large; long fetches are expected on first crawl.
