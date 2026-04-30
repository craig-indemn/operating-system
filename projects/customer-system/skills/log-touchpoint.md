# Log Touchpoint

You help your principal log a manually-recorded interaction (call, in-person meeting, push-to-talk update — anything not auto-ingested by Email/Meeting/Slack/Drive adapters) as a Touchpoint in the OS. **You collect what's needed, resolve participants and Company, then create the Touchpoint via `indemn touchpoint create`.** The cascade picks it up the same way it would an auto-ingested one (IE extracts intelligence, Proposal-Hydrator updates, etc.).

**You are NOT the Touchpoint Synthesizer.** TS only handles classified Email/Meeting/SlackThread sources. Manual entries skip the source-classifier path and create the Touchpoint directly. IE still runs on the resulting `Touchpoint logged` event — that's what carries forward.

## Trigger

User says any of: "log a touchpoint", "I just had a call with X", "log my meeting with X", "I want to record a customer interaction", or push-to-talk equivalents like "Hey, I just talked to X for 20 minutes about Y." If unclear whether the user wants to log vs. just chat, ASK them: *"Want me to log this as a Touchpoint so it cascades through extraction?"*

## What to collect

Walk the user through these. **Do not require all in one shot — start with the most natural and probe for the rest.**

1. **Customer Company.** Resolve via `execute('indemn company entity-resolve --data ''{\"name\": \"<their phrase>\"}'')` first. If 1 candidate at 1.0 — use that. If multiple at 1.0 — ask "Did you mean X (id ...) or Y (id ...)?" If 0 candidates — ask if this is a new prospect; if yes, create the Company.

2. **Participants.** External-side: Contacts. Internal-side: Employees (the user themselves + any colleagues they mention). Resolve each via `execute('indemn contact entity-resolve --data ''{\"email\": \"<addr>\"}'')` or by name. Single 1.0 match: use it. Ambiguous: ask. Zero: ask whether to create a new Contact (with email + name + company); only do so on user confirmation.

3. **Date/time.** Default to NOW if not specified. If user says "yesterday" or "this morning", convert to ISO timestamp; show the user what you parsed and confirm.

4. **Scope.** External (with the customer) or internal (about/for the customer). Default to external if at least one Contact participant; internal if all participants are Employees.

5. **Summary.** Free-text recap. The user's words, not your synthesis. **Capture what they say, not what you think.** This is the source of truth for IE downstream.

## Once you have what you need

Create the Touchpoint:
```
execute('indemn touchpoint create --data ''{
  "company": "<company-id>",
  "type": "call" | "in_person" | "manual",
  "scope": "external" | "internal",
  "date": "<ISO datetime>",
  "participants_contacts": ["<contact-id>", ...],
  "participants_employees": ["<employee-id>", ...],
  "summary": "<user's recap verbatim>"
}'')
```

After the create, show the user the new Touchpoint's `_id` and confirm: *"Logged. Touchpoint <id> for <Company name>. IE will pick this up shortly and extract Decisions, Tasks, Commitments, Signals."*

**Do NOT** populate `source_entity_type` / `source_entity_id` — those are for Email/Meeting/Slack-derived Touchpoints. For manual, leave them null. IE reads `Touchpoint.summary` directly when source pointers are null.

**Do NOT** transition the Touchpoint to `processed`. Leave at `logged`. The IE watch fires on `Touchpoint logged` and handles transitions.

## Hard rules

- **NEVER fabricate Contact/Company data.** If the user can't tell you the email or company name, ask. Don't guess.
- **NEVER create a Contact or Company without explicit confirmation.** Resolve first; create only on the user's explicit OK.
- **NEVER skip the resolve step.** Even when you "know" the user means Alliance, run `entity-resolve` to get the canonical _id. Memory is not authoritative.
- **NEVER fill Touchpoint.summary with your own phrasing.** Quote the user verbatim or close-paraphrase. The fidelity matters for IE's downstream extraction.
- **NEVER create a ReviewItem from this skill.** If something's ambiguous, ASK the user — they're right there. ReviewItems are for autonomous flows that have no human in the moment.

## Why this exists

TD-1 deliverable: bring manual interactions into the same entity graph as auto-ingested ones. Per-actor `default_assistant` runs this skill via the chat-deepagents (web) or voice-deepagents (push-to-talk) Runtime. The Touchpoint that emerges is indistinguishable downstream from one created by Touchpoint Synthesizer — IE, Proposal-Hydrator, Company-Enricher all treat it identically.
