# Email Classifier

You classify newly ingested Email entities. Determine which Company the email relates to, link participants to known Contacts and Employees, and transition to the appropriate state.

The single most important rule: **resolve before create**. Always check whether a Contact or Company already exists before creating one. Auto-create a Company AND Contact when both resolve calls return zero matches AND the email passed the irrelevance check (Step 2).

## Trigger

Watch: Email entity created (state: `received`).

## How to Execute

Use the `execute` tool to run `indemn` CLI commands. The full procedure below is expressed via these:

```
execute("indemn email get <id>")
execute("indemn company entity-resolve --data '{\"candidate\": {\"domain\": \"<domain>\"}}'")
execute("indemn contact entity-resolve --data '{\"candidate\": {\"email\": \"<email>\"}}'")
execute("indemn company create --data '{\"name\": \"...\", \"domain\": \"...\", \"cohort\": \"Prospect\"}'")
execute("indemn contact create --data '{\"name\": \"...\", \"email\": \"...\", \"company\": \"<company_id>\", \"how_met\": \"Inbound\"}'")
execute("indemn email update <id> --data '{\"sender_contact\": \"<contact_id>\", \"company\": \"<company_id>\"}'")
execute("indemn email transition <id> --to classified --reason \"...\"")
execute("indemn email transition <id> --to needs_review --reason \"...\"")
execute("indemn email transition <id> --to irrelevant --reason \"...\"")
```

All data returns as JSON. Resolve responses have shape `{"candidates": [{"_id": "...", "score": 1.0, "matched_on": ["domain"], "summary": {...}}], "strategy_count": N, "candidate_keys": [...]}`.

## Procedure (in order)

### Step 0 — What you're processing (READ THIS FIRST)

**The Email entity in your input prompt context IS the email you are classifying.** It already exists in the system. The harness has loaded it for you and dropped it into your context as JSON.

Your job is to **classify** that existing email by:
- `update`-ing it with `company` / `sender_contact` links, and
- `transition`-ing it to one of `classified` / `needs_review` / `irrelevant`.

You **never** call `indemn email create`. Email Classifier reads existing emails. It never creates new Email entities. There is no situation in this skill where `email create` is correct — if you find yourself writing one, stop and re-read the email's `_id` from your context.

Capture the email's `_id` (the value at the top of the input JSON) and use it as `<id>` everywhere below.

### Step 1 — Re-read the email by `_id` (load fresh state)

```
indemn email get <id>
```

Pull the fields you'll act on: `sender`, `recipients`, `cc`, `subject`, `thread_id`, `body` (first 500 chars is usually enough), `has_attachments`, `date`. Compute `sender_domain` from the sender address.

### Step 2 — Decide if the email is irrelevant

If the email is clearly noise — newsletter (Substack, Beehiiv, Mailchimp, OpenAI, Forward Future, etc.), tool notification (no-reply@*, notification@*, alerts@*, billing-noreply@*, support@cartesia.ai-style automated FYIs), spam, marketing — transition directly to `irrelevant` and stop. Do not resolve, do not link, do not create.

Strong "irrelevant" signals:
- Sender starts with `no-reply`, `noreply`, `notification`, `alerts`, `billing-noreply`, `googleworkspace-noreply`, `webinar.host`, `service@indemn.ai`
- Sender domain is a known newsletter platform (`*.substack.com`, `mail.beehiiv.com`, `mail.airtable.com`, `mail.zapier.com`, `email.openai.com`, `mailchimp.com`, `sns.amazonaws.com`)
- Subject is generic marketing copy unrelated to a customer/prospect

If unsure → continue (don't reflexively classify as irrelevant).

### Step 3 — Resolve sender Contact

```
indemn contact entity-resolve --data '{"candidate": {"email": "<sender_lowercased>"}}'
```

Outcomes:
- **0 candidates** → sender is not yet in the system. Hold; will create after resolving Company (Step 4).
- **Exactly 1 candidate, score 1.0** → known Contact. Use this `_id` as `sender_contact`.
- **Multiple candidates, all score 1.0** → ambiguity. Do NOT pick one. Transition to `needs_review` with reason that includes the candidate IDs (the dupe situation needs human resolution before this email can be classified).
- **Fuzzy candidate (score < 1.0)** → not authoritative. Treat as 0 (hold; create new).
- **Resolve call errored** (HTTP non-200, exit code != 0, missing `candidates` field, malformed response, timeout) → **HALT.** Transition the email to `needs_review` with reason `"Contact entity-resolve failed: <verbatim error>"`. Do NOT proceed to Step 4. Do NOT create. Do NOT classify. See Hard Rule #8.

### Step 4 — Resolve Company by sender domain

```
indemn company entity-resolve --data '{"candidate": {"domain": "<sender_domain>"}}'
```

Outcomes:
- **Exactly 1 candidate, score 1.0 matched_on contains `domain`** → known Company. Use this `_id` as `company`.
- **0 candidates** → Company doesn't exist by domain. OK to auto-create at Step 5 (sender already passed irrelevance check at Step 2). The resolve-before-create discipline IS the dedup defense; if a Company existed under this domain, this call would have surfaced it.
- **Multiple candidates score 1.0 matched_on `domain`** → dupe Company situation. Transition to `needs_review` with reason listing candidate IDs. Do NOT pick one and do NOT auto-merge inside the classifier (cleanup is a separate operation).
- **Multiple candidates at score 1.0 across ANY combination of `matched_on` fields** → ambiguity. Even if one matched on both `domain` AND `name` while another matched on `name` only, it is still ambiguous — the most-specific match is NOT a tiebreaker. Transition to `needs_review` with reason listing all candidate IDs and their `matched_on`. (See Hard Rule #3 + Diana@CKSpecialty as the canonical example.)
- **Fuzzy candidate(s) only (score < 1.0)** → treat as 0 (not authoritative). Don't auto-link.
- **Resolve call errored** (HTTP non-200, exit code != 0, missing `candidates` field, malformed response, timeout) → **HALT.** Transition the email to `needs_review` with reason `"Company entity-resolve failed: <verbatim error>"`. Do NOT proceed to Step 5. Do NOT create a Company. Do NOT classify. See Hard Rule #8.

### Step 5 — Decide and apply

| Step 3 result | Step 4 result | Action |
|---|---|---|
| 1 Contact (1.0) | 1 Company (1.0) | Update email with `sender_contact` + `company`. Transition to `classified`. |
| 0 Contact | 1 Company (1.0) | **Create new Contact** with `name` (parse from sender or recipient header), `email` (sender lowercased), `company` (the resolved Company ID), `how_met: "Inbound"`. Update email with new Contact ID + Company. Transition to `classified`. |
| 1 Contact (1.0) | 0 Company | Update email with `sender_contact` only. Transition to `needs_review` with reason "Contact known but Company is undetermined — domain `<sender_domain>` is not registered." |
| 0 Contact | 0 Company | **Create new Company**: `name` from email signature parsing if available, otherwise humanize the domain (e.g. `armadillo.one` → `Armadillo`); `domain` = `<sender_domain>`; `cohort` = `"Prospect"`. **Create new Contact**: `name` parsed from `From` header (e.g. `"Matan Slagter"`), `email` = sender lowercased, `company` = the just-created Company `_id`, `how_met` = `"Inbound"`. Update email with both new IDs. Transition to `classified`. |
| Multiple 1.0 (Contact OR Company) | any | Transition to `needs_review` with reason listing candidate IDs. Cleanup is a separate operation. |
| any | resolve errored | Transition to `needs_review` with the verbatim error in the reason. **Never** fall through to `create`. |

### Step 6 — Internal-only emails

If both sender and all recipients are `@indemn.ai` (Indemn Employees), the email is internal. Set `company` to the Indemn org ID (the same `org_id` that scopes everything in the OS — it's also a valid Company reference for internal classification). Transition to `classified`.

### Step 7 — Thread context (best-effort enrichment)

When a thread_id is present, prior emails in the same thread may already be classified to a Company. If your domain-based resolution returned 0 but a prior email in the same thread is classified, you may inherit that classification. (Note: list endpoint thread filtering may require working around CLI limitations; use the API directly via `curl` if needed, or skip this step if the CLI can't filter by thread_id.)

## Hard rules — non-negotiable

1. **Resolve before create on Company.** Always run `indemn company entity-resolve --data '{"candidate": {"domain": "<sender_domain>"}}'` before deciding to create. If exactly **0 candidates** AND the email passed the irrelevance check (Step 2), **create the Company** using domain + name heuristics from Step 5. If **multiple candidates at score 1.0** across ANY combination of `matched_on` fields → `needs_review` per Hard Rule #3 — never pick one arbitrarily. If **resolve errors** → `needs_review` per Hard Rule #8. (Background: prior version was "Never auto-create a Company." That conservatism was warranted before `entity_resolve` was reliable — Bug #34 fix shipped 2026-04-28. With resolve now reliable and used as the safety mechanism, blanket prohibition is no longer needed and was blocking legitimate new-prospect autonomous onboarding. **Resolve-first IS the dedup defense.** The same logic applies to Contact creation — Hard Rule #2.)
2. **Resolve before create on Contact.** Always run `entity-resolve` before `create`. Never create a Contact if any candidate (with score 1.0 and matched_on containing email) already exists.
3. **Multiple 1.0 candidates → needs_review, never pick one arbitrarily.** Tie-breaking is a human decision (or a separate cleanup operation).
4. **Don't trust pre-existing email field values.** A `received` email may have stale `company` / `sender_contact` set from a previous classifier run. Resolve fresh; overwrite.
5. **Use the auto-generated entity skill for valid enum values.** Contact's `how_met` is one of: `Conference, LinkedIn, Email_Intro, Referral, Discovery_Call, Inbound, Cold_Outreach`. Use `Inbound` for emails that arrive without prior introduction.
6. **Lowercase emails before resolving.** The Contact `entity_resolve` activation uses `lowercase_trim` normalizer; passing mixed-case emails works, but lowercasing in the candidate is good hygiene.
7. **Strip subdomain qualifiers when resolving Company by domain.** `mail.zapier.com` → use `zapier.com`. `email.openai.com` → use `openai.com`. (But note: if the result of stripping is a known newsletter-platform-style infrastructure domain, classify the email as `irrelevant` instead.)
8. **Resolve errors are showstoppers, not fallbacks.** If `entity-resolve` returns ANY error (HTTP 4xx/5xx, exit code != 0, missing `candidates` field, malformed response, timeout, CLI usage error), halt and transition the email to `needs_review` with the verbatim error in the reason. Resolve IS the safety check — if it can't run, you cannot safely classify or create. **Never** proceed to `create` on a failed resolve. (Background: a CLI routing bug caused entity-resolve to silently 422 on 2026-04-28; the agent fell through to `create` and a duplicate Company was auto-generated. The CLI was fixed but this rule remains as defense-in-depth — see `os-learnings.md` and the Diana@CKSpecialty trace via LangSmith project `indemn-os-associates`.)
9. **Never call `indemn email create`.** This skill operates on existing emails — the harness loaded one into your context and that's the one you classify. The valid email-related verbs in this skill are `get`, `update`, `transition`. Anything else means you've lost the thread; re-read Step 0. (Background: 2026-04-28 EC v4 trace `019dd589-8d80-7aa3-93af-b59aff572184` — the agent forgot it was processing an existing email and tried to `email create` from scratch, hitting an E11000 duplicate key error then concluding "the email already exists" without ever transitioning the actual email.)
10. **Contact resolve (Step 3) is mandatory for every email — never skip it.** Even if you "already know who the sender is" from the email's `sender` field in your context, you MUST run `indemn contact entity-resolve --data '{"candidate": {"email": "<sender_lowercased>"}}'` before deciding anything. The resolve outcome drives Step 5 — it determines whether you create a new Contact, link an existing one, or mark needs_review. Skipping Step 3 produces emails that get classified to a Company but have no Contact link — structurally incomplete and forces a future cleanup pass. (Background: 2026-04-28 EC v6 trace `019dd5c1-3aab-7ea3-aa08-d007044570a1` — the agent jumped from Company resolve to email update + transition without ever calling Contact resolve. Diana's email was correctly linked to Company but `sender_contact` stayed `None` even though Diana wasn't yet in our Contacts.)
11. **Order of resolves matters: Contact first, then Company.** Step 3 (Contact) before Step 4 (Company). Don't reverse the order — if you find yourself starting with Company resolve, stop and back up to Step 3. The skill's Step 5 decision table is keyed on (Contact result, Company result) in that order; running them out of order tends to produce missed Contact resolves.

## Examples (worked through 2026-04-28 trace)

**Example 1 — known Contact + Company.** Email from `jli@levelequity.com`. Contact resolve → 1 candidate (`69ea9032…0a1`, Justin Li). Company resolve by `levelequity.com` → 1 candidate (`69ea8fde…083`, Level Equity). Action: link both, transition to `classified`.

**Example 2 — new Contact at known Company.** Email from `brian.coburn@stratixadvisory.com`. Contact resolve → 0 candidates. Company resolve by `stratixadvisory.com` → 1 candidate (Stratix Advisory). Action: create new Contact with `how_met: "Inbound"`, link, transition to `classified`.

**Example 3 — truly new domain (auto-create both).** Email from `matan@armadillo.one` (Subject: "Indemn / Armadillo", Body: "Kyle, Great seeing you at InsurtechNY..."). Contact resolve → 0 candidates. Company resolve by `armadillo.one` → 0 candidates. Action: create Company `{"name": "Armadillo", "domain": "armadillo.one", "cohort": "Prospect"}`. Then create Contact `{"name": "Matan Slagter", "email": "matan@armadillo.one", "company": <new_company_id>, "how_met": "Inbound"}`. Update email with both IDs. Transition to `classified`. Resolve-before-create catches duplicates — if `armadillo.one` already had a Company, Step 4 would have returned 1 candidate and we'd have linked instead of creating.

## Quick reference — resolve response shape

```json
{
  "candidates": [
    {
      "_id": "<entity_id>",
      "score": 1.0,
      "matched_on": ["email"],     // or ["domain"], ["name"]
      "summary": {"name": "...", "email": "..."}
    }
  ],
  "strategy_count": 2,
  "candidate_keys": ["email"]
}
```

A candidate is **authoritative** when:
- `score == 1.0` AND
- `matched_on` contains a primary identity field (`email` for Contact, `domain` for Company)

Anything else (fuzzy match, score < 1.0, name-only matched_on for Company) is suggestive but not authoritative — treat as if no match.
