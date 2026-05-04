# Email Fetcher

Scheduled deterministic CLI executor. Runs `indemn email fetch-new` on every cron tick to incrementally pull new Emails since the last watermark across all 11 team mailboxes. Capped at 100 saves per call so subprocess stays under visibility window.

## Command

```bash
indemn email fetch-new --data '{"limit": 100}'
```

## Why this exists

Per TD-1: each source adapter runs autonomously on its own schedule. Email-Fetcher fires every 5 minutes; the Google Workspace adapter handles incremental via per-mailbox `since` watermark. Fetched Emails sit at `received` for downstream classifiers (TD-2's Email Classifier).

Executed via Bug #40's `cron_runner` actor mode — no LLM, no deepagents agent. The harness shell-execs the `## Command` line directly, parses the JSON response, marks the message complete (or failed if the adapter returns errors). Content above the fence is human-readable context; only the fenced command is executed.

`limit: 100` per Bug #50 follow-on: bounds per-tick save loop so subprocess stays well under the 5-min visibility timeout. fetch_new sorts new items oldest-first before slicing, so the watermark advances cleanly (next tick picks up the next 100 oldest). On a backed-up watermark with 1000+ accumulated emails, the backlog drains over ~10 cron ticks (~50 min) instead of one stuck-and-failing tick.

Backfills go through a human-driven CLI invocation (`indemn email fetch-new --data '{"since": "..."}'`), not this scheduled actor. Manual backfills can omit `limit` to pull everything in the window.
