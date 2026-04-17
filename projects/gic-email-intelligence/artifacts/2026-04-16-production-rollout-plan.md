---
ask: "Production rollout plan with decisions from post-demo session — what we're doing, in what order, with what constraints"
created: 2026-04-16
workstream: gic-email-intelligence
session: 2026-04-16a
sources:
  - type: google-doc
    ref: "https://docs.google.com/document/d/1cV3dRLUZT49dixc7v_j7Fc4ho2QwcUImsUG3XYTqEr0"
    name: "JC/Mike/Craig meeting 2026-04-13"
  - type: gmail
    description: "JC email 2026-04-16 with production credentials and group setup"
  - type: codebase
    description: "unisoft-proxy, automation agent, skill, WSDL spec"
---

# Production Rollout Plan — 2026-04-16

## Inputs

- **Demo done 2026-04-13** with JC + Mike Burke. Positive response.
- **JC's unblock email 2026-04-16:** prod URL, `indemnai` user, `New Biz` and `New Biz Workers Comp` task groups created and live.
- **Outstanding from JC:** Mike's endorsement rundown + no-brainer list.
- **Outstanding from Makul:** write access to quotes inbox (Grove Networks was supposed to reach out — hasn't).

## Decisions Made This Session

1. **Task assignment model: group-only.** `AssignedToUser` is empty, `GroupId` is set to the correct group. Team members pick up from the group task queue. This matches JC's "team picks it up from there" intent.
2. **Test in UAT first with a self-created test group.** Don't cut to prod until the flow is proven. Create a test group in UAT via `SetTaskGroup`, then wire the automation to use it.
3. **Build our own duplicate detection** (MongoDB-side), not relying on Unisoft's similar-name prompts. We have the submission records already — check before calling `CreateQuoteID`.
4. **Ordering:** (1) Task creation in UAT → (2) Agency search phone+address fallback → (3) Duplicate detection → (4) Prod cutover. Activity-step reliability and endorsements ingestion can run in parallel.
5. **Artifact discipline.** Save artifacts as we go so sessions can resume cleanly. Each sub-project gets its own artifact.

## Work Plan

### Phase 1 — Task creation in UAT (active)
- Add `SetTaskGroup` wiring to proxy + CLI; create a test group
- Add `SetTask` wiring to proxy + CLI (`unisoft task create`)
- Discover `GetTaskActions` and pick the right ActionId for "New business submission"
- Update `create-quote-id.md` skill: add Step 6 "Create Task" (group-assigned, linked to Quote ID, subject = "New submission: {insured} — {LOB}", due = +1 business day)
- Build LOB → group routing (WC → New Biz Workers Comp; else → New Biz)
- Run end-to-end in UAT, verify tasks appear correctly

### Phase 2 — Agency search improvements
- Add phone + address fallback when agency name doesn't match
- Producer code is still first priority, then name, then phone/address
- Measure effect on automation rate (baseline ~60%)

### Phase 3 — Duplicate detection
- MongoDB-side check before creating Quote ID: normalize name + address, search existing submissions
- Return existing Quote ID if match found rather than creating duplicate
- Log match reason (exact name, fuzzy name, address match, both) for debugging

### Phase 4 — Prod cutover
- Call `GetTaskGroups` as `indemnai` user to discover real group IDs
- Update proxy env vars: `UNISOFT_SOAP_URL`, credentials
- Update automation skill: switch from test group ID to real group IDs
- Run end-to-end against prod with a real email
- Monitor first batch closely

### Parallel work
- **Endorsements ingestion** — read-only access granted; connect the inbox, begin ingesting to understand volume and content. Waiting on Mike for automation rules.
- **Activity step reliability** — tighten skill so Step 6 (activity) isn't skipped ~20% of time.
- **Email move to subfolder** — blocked on Makul/Grove Networks. Ping the thread.

## Known Unknowns

- **Production agency/producer data** — may differ from UAT. The 37 missing agencies flagged in UAT may or may not exist in prod.
- **Real group IDs in prod** — can only be discovered after login with `indemnai`.
- **Unisoft's actual task action taxonomy** — `ActionId` for "new business submission via email" needs discovery via `GetTaskActions`.

## Principles

- **No ad-hoc scripts.** Everything goes through the pipeline.
- **Verify before claiming.** Check logs, check DB, check actual API responses.
- **Read the WSDL before guessing params.** 910 operations, 1668 data types. It's the source of truth.
- **Don't rapid-restart the Unisoft proxy.** Each startup authenticates; failed attempts risk account lockout.

## Files to Update

| File | What changes |
|------|--------------|
| `unisoft-proxy/client/cli.py` | Add `task_app` typer with `task create`, `group list`, `group create` |
| `unisoft-proxy/client/unisoft_client.py` | Add `set_task()`, `get_task_groups()`, `set_task_group()` methods |
| `unisoft-proxy/UniProxy.cs` on EC2 | Check if `SetTaskGroup` needs a namespace registration entry for `TaskGroup` DTO |
| `src/gic_email_intel/automation/skills/create-quote-id.md` | Add Step 6 "Create Task" with group routing logic |
| `src/gic_email_intel/automation/agent.py` | Nothing? Agent calls CLI — the skill tells it what to do |
| `src/gic_email_intel/core/duplicate_check.py` (NEW) | Name+address normalization + search logic |
| `src/gic_email_intel/agent/harness.py` | Call duplicate check before allowing automation claim |
