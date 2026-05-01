# USLI Quote Automation — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

> ## Updates log (2026-05-01)
>
> Empirical findings from Phase B inverted several assumptions in the original plan. Key deltas, with pointers to the canonical reference for each:
>
> 1. **B.2 — name-search works after all.** Original conclusion ("returns empty arrays, pivot to ambiguous-folder fallback") was wrong. Root cause was Criteria DTO field-shape mismatch (modeled after the saved-search XML, not the SOAP wire). Canonical shape captured 2026-05-01: see `2026-05-01-unisoft-quote-search-canonical-shape.md`. **C.1 was implemented against this — references to `GetQuotesByName2` throughout the plan are stale; shipped op is `GetQuotesForLookupByCriteria`.** Shipped: commit `b2f0f27`.
> 2. **B.5 architectural pivot.** USLI ref is NOT stored anywhere on Unisoft side today (verified across 7 real linked Quotes: every `Quote.ConfirmationNumber` / `Source` / `OriginatingSystem` / `Submission.ConfirmationNo` for CarrierNo=2 is null). Name-search-as-primary with ambiguous-folder fallback would push 30–50% of daily volume to manual triage. New architecture: three-tier deterministic lookup with loop-closure stamping. **See `2026-05-01-usli-deterministic-lookup-architecture.md` — supersedes the original B.5 task and the design's "branched on lookup" diagram.** New task **C.7** added (deterministic-lookup helper + CLI). The `Indemn USLI Needs Review` folder is dropped — Tier 2 ambiguity uses tiebreak instead.
> 3. **B.1 — (action_id, letter_name) PAIR.** ActionId 67 ("Send offer to agent") has 25 templates in the UI dropdown; LetterName="USLI Quote" is the discriminator. **C.4 contains a real bug:** `_create_activity_and_notify` picks `templates[0]` blindly, which fires the wrong template for any ActionId with multiple templates. **C.4 spec revised below to thread `letter_name` and filter `GetActionNotifications` results.** B.6 Settings + Param Store thread both values, not just one. Shipped: commit `9f7e81d` (fixture only).
> 4. **B.3 — whitelist PDF policy** (not blacklist). Family 2 (Retail Web) attachments have no "customer" string in any filename, so blacklist-on-customer would miss the bare `{REF}.pdf` declaration page. Whitelist by `retailer` / `applicant` substring; default-skip everything else. Attachment field name is `name`, not `filename`. C.5/C.6/D.2 spec revised below. Shipped: commit `74cd768` (fixture only).
> 5. **B.4 — defaults match prod.** USLI=2, GIC BrokerId=1 in both UAT and prod; no code changes required. Shipped: commit `fa8d55a` (fixture only).
> 6. **C.0/C.1/C.2/C.3 already shipped.** Commit SHAs: `ea0fe75` (C.0), `b2f0f27` (C.1), `aec13fa` (C.2), `8608121` (C.3). 17 new tests, all green. Plan bodies for these tasks are preserved as historical record.
> 7. **K.5 superseded.** "Exact-match Quote lookup IF B.2 found a real ref field" — empirically no such field exists. The equivalent capability is now folded into C.7 + the loop-closure stamping (no longer post-launch deferred). New **K.8** added: backfill `Submission.ConfirmationNo` for the ~7 historical USLI-linked Quotes.
>
> **Summary of remaining work in execution order** (post-2026-05-01):
> 1. C.4 letter_name bug fix (critical, independent of architecture)
> 2. B.6 Settings + Param Store (action_id + letter_name pair)
> 3. C.5 whitelist + classify-usli-state CLI
> 4. C.7 deterministic-lookup helper
> 5. D.1, D.2, D.3 (skill loader, skill rewrite, factory test)
> 6. D.4 dispatch (unchanged)
> 7. E.1 folder routing (drop Needs Review folder)
> 8. G UAT soak with revised G.3 thresholds
> 9. H prod rollout (unchanged, gates on DEVOPS-158)
> 10. K post-launch (K.5 dropped, K.8 added)

**Goal:** Extend the existing email-to-Unisoft automation to handle `usli_quote` emails — for each one, create or enrich Unisoft Submission(s) under the appropriate Quote, attach the retailer + applicant copies, and create a USLI Quote Follow-Up activity that auto-fires the notification email to the retail agent. Three smaller cleanup PRs (task subject format, faster claim, .eml inline attachments) ship in parallel as sibling PRs, not bundled with USLI.

**Architecture:** New deep agent factory + skill markdown for `usli_quote` (parallel to today's `agent_submission`), three new CLI commands wrapping existing SOAP operations (`GetQuotesForLookupByCriteria`, `SetSubmission Action=Update`, plus a new `--confirmation-no` flag and Submission-bound activity wiring), one new automation cron container, one new `Settings` field. Hard rule: prod-touching merges (Phase H) gate on **DEVOPS-158 7-day soak completion** (target end ~2026-05-06). Build + UAT work (Phases A–G) can overlap with the prod soak — different infrastructure.

**Tech Stack:** Python 3.12 (uv), Typer + LangChain `deepagents`, MongoDB Atlas, Google Vertex AI Gemini, in-house Unisoft REST proxy on Windows EC2, Docker Compose on dev-services / prod-services EC2, GitHub Actions self-hosted runners.

**Reference docs:** Design at `projects/gic-email-intelligence/artifacts/2026-04-29-usli-quote-automation-design.md`. Cutover post-mortem at `projects/gic-email-intelligence/artifacts/2026-04-29-cutover-execution-handoff.md`. Read both before starting.

**Production-safety rule:** Tasks marked **[NEEDS USER APPROVAL]** modify production state (writes to prod EC2, prod Secrets, prod Atlas, live customer mailbox folder creates, prod cron unpause, DNS, etc.). Stop and confirm with Craig before executing.

**Mongo database topology (post-migration):** dev and prod EC2 connect to the **same** Atlas cluster (`dev-indemn-pl-0` PrivateLink endpoint) but write to **different databases**:

| Env | EC2 instance | Database |
|---|---|---|
| dev | `i-0fde0af9d216e9182` (dev-services) | `gic_email_intelligence_devsoak` |
| prod | `i-00ef8e2bfa651aaa8` (prod-services) | `gic_email_intelligence` |

dev-services has its own sync cron pulling from the same `quote@gicunderwriters.com` inbox into `_devsoak`, so the dev sandbox has fresh real emails arriving continuously. The `_devsoak` DB was originally the migration-soak DB (Phase G of the migration); post-cutover it stays in place as the dev sandbox. Tasks that read **real prod data** for inspection (B.3 PDF patterns) explicitly target `gic_email_intelligence`. Tasks that **write** during dev testing (G.x soak) write to `_devsoak` — completely isolated from prod. Customer Outlook inbox folders are shared between envs; **SOAK_MODE prevents dev from touching them** (see G.1).

---

## Plan map

| Phase | Scope | Gates on |
|---|---|---|
| **A** | Workspace + Linear + conftest setup | — |
| **B** | Build-time verification (read-only against UAT/prod Unisoft) | A |
| **B-exit** | Verify B outputs in `tests/fixtures/usli_config.json`; gate to C | B |
| **C** | New CLI commands + helper generalization (TDD, on feature branch) | B-exit |
| **D** | New skill + agent factory | C |
| **E** | Folder routing additions | — (parallel to C/D) |
| **F** | (skipped — see Sibling PRs) | — |
| **G** | UAT soak (dev-services + UAT Unisoft, SOAK_MODE), numerical thresholds gate H | C, D, E merged to main |
| **H** | **Prod rollout** | DEVOPS-158 7-day soak Done, G thresholds met |
| **K** | Post-launch follow-ups | H |
| **Sibling 1** | Task subject format `[LOB] - description` (DEVOPS-163, separate PR off `indemn/main`) | — |
| **Sibling 2** | Faster claim into "Indemn - Processing" (DEVOPS-164, separate PR off `indemn/main`) | DEVOPS-158 Done |
| **Sibling 3** | .eml inline attachments (DEVOPS-165, separate PR off `indemn/main`) | — |
| **Sibling 4** | Backfill historical .eml uploads | Sibling 3 merged |

---

## Pre-flight Checklist

```bash
# Cutover succeeded 2026-04-29 ~22:50 UTC. Soak gate is DEVOPS-158 (7-day).
linearis-proxy.sh issues list --filter '{"id":{"eq":"DEVOPS-158"}}' --json | jq -r '.[].state'
# Expected: "In Progress" — soak still active. Phase H waits.

# AWS auth + permission probe
aws sts get-caller-identity --query 'Account' --output text   # 780354157690
aws ssm describe-instance-information \
  --filters "Key=InstanceIds,Values=i-0fde0af9d216e9182,i-00ef8e2bfa651aaa8" \
  --query 'InstanceInformationList[].{id:InstanceId,ping:PingStatus}' --output table
# Expected: both Online. If AccessDeniedException, you don't have ssm:DescribeInstanceInformation —
# request permission before continuing.

# dev-services + prod-services running
aws ec2 describe-instance-status --instance-ids i-0fde0af9d216e9182 i-00ef8e2bfa651aaa8 \
  --query 'InstanceStatuses[].{id:InstanceId,state:InstanceState.Name}' --output table
# If dev-services is stopped: aws ec2 start-instances --instance-ids i-0fde0af9d216e9182

# GitHub auth
gh auth status
gh api repos/indemn-ai/gic-email-intelligence --jq '.permissions.push'  # true

# uv installed
uv --version

# Self-hosted runners online
gh api repos/indemn-ai/gic-email-intelligence/actions/runners --jq '.runners[] | {name, status}'
# Expected: both `online`

# Production stable on prod-services (read-only)
aws ssm send-command --instance-ids i-00ef8e2bfa651aaa8 --document-name AWS-RunShellScript \
  --parameters 'commands=["docker logs --tail 50 gic-email-automation 2>&1 | tail -30"]' \
  --query 'Command.CommandId' --output text
# Read the invocation; expect no recurring failures

# Confirm dev/prod Mongo DB split is as documented
aws secretsmanager get-secret-value --secret-id indemn/dev/gic-email-intelligence/mongodb-uri --query SecretString --output text | grep -q "dev-indemn-pl-0" && echo "dev URI: PrivateLink OK"
aws ssm get-parameter --name /indemn/dev/gic-email-intelligence/mongodb-database --query 'Parameter.Value' --output text
# Expected: gic_email_intelligence_devsoak
aws ssm get-parameter --name /indemn/prod/gic-email-intelligence/mongodb-database --query 'Parameter.Value' --output text
# Expected: gic_email_intelligence

# Confirm dev-services has SOAK_MODE=true (so it doesn't touch the customer inbox or fire emails)
aws ssm send-command --instance-ids i-0fde0af9d216e9182 --document-name AWS-RunShellScript \
  --parameters 'commands=["docker exec gic-email-api env | grep SOAK_MODE"]' \
  --query 'Command.CommandId' --output text
# Read the invocation; expected: SOAK_MODE=true
# If SOAK_MODE is false or unset, dev-services is racing prod-services on Outlook folder moves
# and may fire real emails to agents. STOP and set SOAK_MODE=true via Param Store before proceeding.

# Confirm dev-services containers are up
aws ssm send-command --instance-ids i-0fde0af9d216e9182 --document-name AWS-RunShellScript \
  --parameters 'commands=["docker ps --filter name=gic-email --format \"table {{.Names}}\\t{{.Status}}\""]' \
  --query 'Command.CommandId' --output text
# Read the invocation; expected: gic-email-{sync,api,processing,automation} all Up
# (Healthcheck status may show 'unhealthy' due to PR #19 pending — not a blocker)
```

If anything fails, fix before proceeding.

---

## Phase A: Workspace + Linear + Conftest Setup

### Task A.0: Create Linear epic and sub-issues — [NEEDS USER APPROVAL]

**Step 1:** Confirm with Craig before creating tickets. Parent epic is DEVOPS-151 ("GIC Email Intelligence — migrate to Indemn infra"). Add child issue **DEVOPS-162 USLI quote automation**, plus three sibling issues all under DEVOPS-151:
- DEVOPS-163 Task subject format → `[LOB] - Business description`
- DEVOPS-164 Faster claim into "Indemn - Processing"
- DEVOPS-165 .eml export includes attachments inline (+ historical backfill as a follow-up)

**Step 2:** Create.

```bash
linearis-proxy.sh issues create --title "USLI quote automation" --parent DEVOPS-151
linearis-proxy.sh issues create --title "Task subject format = [LOB] - Business description" --parent DEVOPS-151
linearis-proxy.sh issues create --title "Faster claim into Indemn - Processing folder" --parent DEVOPS-151
linearis-proxy.sh issues create --title ".eml export includes attachments inline (+ backfill)" --parent DEVOPS-151
```

Sub-tasks (160.1–160.7) are tracked as comments on DEVOPS-162; not formal sub-issues.

### Task A.1: Create feature worktree off indemn/main

**Step 1:** Fetch latest.

```bash
cd /Users/home/Repositories/gic-email-intelligence-migration
git fetch indemn
git log --oneline indemn/main -3
```

**Step 2:** Create worktree.

```bash
git worktree add ../gic-email-intelligence-usli -b feat/usli-quote-automation indemn/main
cd ../gic-email-intelligence-usli
git status
git branch --show-current  # feat/usli-quote-automation
```

Sibling PRs each get their own worktree off `indemn/main` (see "Sibling worktree setup" inside each sibling section).

**Step 3:** Verify uv environment.

```bash
uv sync --frozen
uv run gic --help
```

### Task A.2: Verify baseline tests pass

```bash
uv run pytest tests/ -q --tb=no
git rev-parse HEAD > /tmp/usli-baseline-sha.txt
```

If red on `indemn/main`, **stop** — pre-existing problem.

### Task A.3: Add pytest marker convention + conftest shim

**Files:**
- Modify: `pyproject.toml`
- Modify: `tests/conftest.py` (existing file — APPEND, do not replace)
- Create: `tests/fixtures/` directory

**Step 1: pyproject.toml** — add UAT marker:

```toml
[tool.pytest.ini_options]
markers = [
    "uat: smoke tests that hit live UAT Unisoft (skipped by default)",
]
addopts = "-m 'not uat'"
```

To run UAT tests explicitly: `uv run pytest -m uat`. Decorate with `@pytest.mark.uat`.

**Step 2: tests/conftest.py** — append the `sys.path` shim so Phase C tests can `from cli import app` and `from unisoft_client import UnisoftClient`. Read the existing file first; do not clobber its existing fixtures.

```python
# Append at the bottom of tests/conftest.py
import sys
from pathlib import Path
_UNISOFT_CLI_DIR = Path(__file__).parent.parent / "unisoft-proxy" / "client"
if str(_UNISOFT_CLI_DIR) not in sys.path:
    sys.path.insert(0, str(_UNISOFT_CLI_DIR))
```

**Step 3:** Create `tests/fixtures/` directory; placeholder gitkeep.

```bash
mkdir -p tests/fixtures
touch tests/fixtures/.gitkeep
```

This is where Phase B writes its empirical findings (as JSON), and where Phase C tests `json.load` them. Replaces the previous `/tmp/usli-config.txt` write-only artifact.

**Step 4: Commit.**

```bash
git add pyproject.toml tests/conftest.py tests/fixtures/.gitkeep
git commit -m "test: add 'uat' marker, sys.path shim for unisoft-proxy/client, fixtures/ dir"
```

---

## Phase B: Build-Time Verification (read-only)

Output: `tests/fixtures/usli_config.json` — checked into the feature branch, consumed by Phase C tests + the production code via `gic_email_intel.config.Settings`.

Schema:

```json
{
  "usli_quote_followup_action_id": 0,
  "quote_search_request_field": "SearchForValue",
  "quote_usli_ref_field": "ConfirmationNumber",
  "pdf_retailer_patterns": ["retailer", "Retailer Copy"],
  "pdf_applicant_patterns": ["applicant", "Applicant Copy"],
  "pdf_customer_patterns": ["customer", "Customer Copy"],
  "broker_id_gic": 1,
  "carrier_no_usli": 2,
  "agent_no_gic_office_quoted": 777,
  "ambiguous_match_folder": "Indemn USLI Needs Review",
  "uat_test_insured": "ABANOLAND LLC"
}
```

### Task B.1: Identify ActionId for "USLI Quote Follow-Up" + confirm template

> **UPDATE 2026-05-01 — SHIPPED + spec revised.** Final values: `usli_quote_action_id=67` ("Send offer to agent") + `usli_quote_letter_name="USLI Quote"`. Plan candidates 101/89/88 were wrong — final value 67 has 25 templates, requiring the LetterName discriminator. Fixture key `usli_quote_followup_action_id` (single int) is replaced by the pair `usli_quote_action_id` + `usli_quote_letter_name`. **C.4, B.6, D.1 spec revised below.** Shipped: commit `9f7e81d`.

**Step 1:** From dev-services:

```bash
aws ssm send-command --instance-ids i-0fde0af9d216e9182 --document-name AWS-RunShellScript \
  --parameters 'commands=["KEY=$(aws secretsmanager get-secret-value --secret-id indemn/dev/gic-email-intelligence/unisoft-api-key --query SecretString --output text); curl -4 -s -X POST http://172.31.23.146:5000/api/soap/GetQuoteActions -H \"X-Api-Key: $KEY\" -H \"Content-Type: application/json\" -d \"{}\""]' \
  --query 'Command.CommandId' --output text
# Read the invocation, parse ActionId/Description pairs.
```

Or via SSM session — type `exit` at the end:

```bash
aws ssm start-session --target i-0fde0af9d216e9182
# All commands below run inside the SSM session until 'exit'.
KEY=$(aws secretsmanager get-secret-value --secret-id indemn/dev/gic-email-intelligence/unisoft-api-key --query SecretString --output text)
curl -4 -s -X POST http://172.31.23.146:5000/api/soap/GetQuoteActions \
  -H "X-Api-Key: $KEY" -H 'Content-Type: application/json' -d '{}' \
  | python3 -c 'import sys,json,re,html; data=sys.stdin.read(); pairs=re.findall(r"<\w+:ActionId>(\d+)</\w+:ActionId>.*?<\w+:Description>([^<]+)</\w+:Description>", data, re.DOTALL); seen=set(); [print(f"{a:5} {html.unescape(d).strip()}") for a,d in pairs if (a,d) not in seen and not seen.add((a,d))]' \
  | grep -iE 'quote|offer|follow|usli'
exit
```

**Step 2:** Pick the action JC uses. Strong candidates:
- **101** — "Send offer follow up to agent"
- **89** — "Quote follow-up"
- **88** — "Submission follow-up"

**Step 3:** Verify the chosen ActionId has a configured notification template (UAT first, then prod). If empty, try the next candidate.

```bash
# Inside SSM session on dev-services, with KEY set:
for AID in 101 89 88; do
  echo "ActionId=$AID:"
  curl -4 -s -X POST http://172.31.23.146:5000/api/soap/GetActionNotifications \
    -H "X-Api-Key: $KEY" -H 'Content-Type: application/json' -d "{\"ActionId\":$AID}" \
    | python3 -m json.tool | head -20
  echo "---"
done
```

**Step 4 — fallback gate.** If NO candidate ActionId has a notification template configured, **stop**. The skill will fire empty emails. Ping JC to configure a template in the Unisoft admin UI. Phase C does not start until B.1 produces a non-zero `usli_quote_followup_action_id` with a non-empty notification.

**Step 5:** Repeat against prod (port 5001) for parity. Note divergences.

**Step 6:** Write to `tests/fixtures/usli_config.json` (start the file here):

```bash
cat > tests/fixtures/usli_config.json <<'EOF'
{
  "usli_quote_followup_action_id": 101
}
EOF
```

(Subsequent B tasks merge into the same file.)

### Task B.2: Confirm GetQuotesByName2 request shape + USLI ref candidate field

> **UPDATE 2026-05-01 — SUPERSEDED.** Op is `GetQuotesForLookupByCriteria` (not GetQuotesByName2). Original conclusion ("ops return empty arrays, pivot to ambiguous-folder fallback") was wrong — root cause was Criteria DTO field-shape mismatch. Canonical wire format captured 2026-05-01: see `2026-05-01-unisoft-quote-search-canonical-shape.md`. The `quote_usli_ref_field` probe found NO field on Unisoft side stores the USLI ref; the equivalent capability is built into C.7's deterministic-lookup architecture (`2026-05-01-usli-deterministic-lookup-architecture.md`). C.1 shipped against the canonical shape: commit `b2f0f27`. Plan body below preserved as historical record.

**Step 1:** WSDL shows `QuoteListRequest` has no `Name2` field. Real fields include `SearchForValue`, `Criteria` (a `QuoteSearchCriteriaDTO` with a nested `Name`), `AgentNumber`, `IsNewSystem`, `ItemsPerPage`, `MGANumber`, `PageNumber`, `SortExpression`. Probe empirically — start with a known UAT insured (the migration soak created Q:17373 ↔ Golden Hands Home Keeping; confirm before relying on it).

```bash
# Confirm Q:17373 still in UAT (read-only)
curl -4 -s -X POST http://172.31.23.146:5000/api/soap/GetQuote \
  -H "X-Api-Key: $KEY" -H 'Content-Type: application/json' -d '{"QuoteID":17373}' \
  | python3 -m json.tool | head -30
# Expected: a Quote with Name like "Golden Hands Home Keeping & Disinfectant Crew, LLC"
# If 404/empty: pick a different UAT-confirmed insured from agent_submission soak data.

# Now probe GetQuotesByName2 with SearchForValue
curl -4 -s -X POST http://172.31.23.146:5000/api/soap/GetQuotesByName2 \
  -H "X-Api-Key: $KEY" -H 'Content-Type: application/json' \
  -d '{"SearchForValue":"Golden Hands","PageNumber":1,"ItemsPerPage":10}' \
  | python3 -m json.tool | head -50

# If empty or fault, try Criteria.Name
curl -4 -s -X POST http://172.31.23.146:5000/api/soap/GetQuotesByName2 \
  -H "X-Api-Key: $KEY" -H 'Content-Type: application/json' \
  -d '{"Criteria":{"Name":"Golden Hands"},"PageNumber":1,"ItemsPerPage":10}' \
  | python3 -m json.tool | head -50

# If both empty: dump the WSDL <complexType name="QuoteListRequest"> definition and try every string field.
```

**Step 2:** When the search returns the expected Quote, pick the `UAT_TEST_INSURED` value (use the Quote's `Name` field verbatim — case + punctuation matters for downstream tests). Write to fixture:

```bash
python3 -c "
import json, pathlib
p = pathlib.Path('tests/fixtures/usli_config.json')
cfg = json.loads(p.read_text())
cfg['quote_search_request_field'] = 'SearchForValue'  # or whichever worked
cfg['uat_test_insured'] = 'Golden Hands Home Keeping & Disinfectant Crew, LLC'
p.write_text(json.dumps(cfg, indent=2))
"
```

**Step 3:** Inspect candidate USLI-ref fields on a known-good Quote.

```bash
curl -4 -s -X POST http://172.31.23.146:5000/api/soap/GetQuote \
  -H "X-Api-Key: $KEY" -H 'Content-Type: application/json' -d '{"QuoteID":17373}' \
  | python3 -m json.tool | grep -iE 'ConfirmationNumber|OriginatingSystem|Source|ApplicationNumber'
```

(`ApplicationNumber` is NOT on QuoteDTO — don't probe for it. `OriginatingSystem` is an enum — note its value.)

**Step 4:** Write finding:

```bash
python3 -c "
import json, pathlib
p = pathlib.Path('tests/fixtures/usli_config.json')
cfg = json.loads(p.read_text())
cfg['quote_usli_ref_field'] = 'ConfirmationNumber'  # or 'none' if no field
p.write_text(json.dumps(cfg, indent=2))
"
```

If `quote_usli_ref_field == "none"`, name search remains the v1 lookup. If a real field is found, **K.5 (post-launch)** can add an exact-match fast path; in v1 we proceed with name search.

### Task B.3: Confirm PDF version detection patterns

> **UPDATE 2026-05-01 — SHIPPED + policy revised.** Use whitelist policy (upload only on `retailer` or `applicant` substring; default-skip everything else), not blacklist on `customer`. Reason: Family 2 (Retail Web) attachments have a small bare `{REF}.pdf` declaration page with no "customer" string, so blacklist-on-customer would miss it. Two filename families captured: Family 1 `{REF}_Customer/Retailer/Applicant.pdf`, Family 2 `{REF}.pdf` / `{REF}_RetailerVersion/ApplicantVersion.pdf`. Schema gotcha: attachment field name is `name`, not `filename`. C.5 helper renamed to `should_upload_pdf()`; D.2 skill instructions revised. Shipped: commit `74cd768`.

**Step 1:** Pull 5 recent USLI quote emails with attachments from the **prod database** (read-only — that's where real recent USLI traffic lives; `_devsoak` only has Phase G migration data which is stale).

```bash
# Use the dev-services-resolvable URI (PrivateLink) but query the prod DB read-only.
URI=$(aws secretsmanager get-secret-value --secret-id indemn/prod/gic-email-intelligence/mongodb-uri --query SecretString --output text)
aws ssm send-command --instance-ids i-0fde0af9d216e9182 --document-name AWS-RunShellScript \
  --parameters "commands=[\"docker run --rm --network host mongo:6 mongosh '${URI}/gic_email_intelligence' --quiet --eval 'db.emails.find({\\\"classification.email_type\\\":\\\"usli_quote\\\", attachments:{\\\$exists:true,\\\$ne:[]}}, {_id:1, subject:1, \\\"attachments.filename\\\":1}).sort({received_at:-1}).limit(5)'\"]" \
  --query 'Command.CommandId' --output text
# Read the invocation. This is read-only against the prod gic_email_intelligence database.
```

**Step 2:** Eyeball filename patterns. Look for "retailer", "applicant", "customer" markers.

**Step 3:** Write findings:

```bash
python3 -c "
import json, pathlib
p = pathlib.Path('tests/fixtures/usli_config.json')
cfg = json.loads(p.read_text())
cfg['pdf_retailer_patterns'] = ['retailer', 'Retailer Copy']
cfg['pdf_applicant_patterns'] = ['applicant', 'Applicant Copy']
cfg['pdf_customer_patterns'] = ['customer', 'Customer Copy']
p.write_text(json.dumps(cfg, indent=2))
"
```

If filenames are inconsistent, note the fallback — content-pattern matching during PDF extraction (defer to D.2 skill instructions).

### Task B.4: Confirm BrokerId + CarrierNo in prod

> **UPDATE 2026-05-01 — SHIPPED.** USLI is `CarrierNumber=2` and GIC Underwriters is `BrokerId=1` in both UAT and prod. No code changes required. Schema gotcha: response uses `CarrierNumber` (not `CarrierNo`) and `Name1` (not `Name`). Shipped: commit `fa8d55a`.

```bash
# Inside SSM session, with prod KEY:
KEY=$(aws secretsmanager get-secret-value --secret-id indemn/prod/gic-email-intelligence/unisoft-api-key --query SecretString --output text)
curl -4 -s -X POST http://172.31.23.146:5001/api/soap/GetCarriersForLookup -H "X-Api-Key: $KEY" -H 'Content-Type: application/json' -d '{}' \
  | python3 -c 'import sys,json,re; print([m.group(1)+":"+m.group(2) for m in re.finditer(r"<\w+:CarrierNo>(\d+)</\w+:CarrierNo>.*?<\w+:Name>([^<]+)</\w+:Name>", sys.stdin.read(), re.DOTALL)])' | head
curl -4 -s "http://172.31.23.146:5001/api/1.0/brokers?forLookup=true" -H "X-Api-Key: $KEY"
```

Expected: USLI=2, GIC Underwriters=1.

```bash
python3 -c "
import json, pathlib
p = pathlib.Path('tests/fixtures/usli_config.json')
cfg = json.loads(p.read_text())
cfg['broker_id_gic'] = 1
cfg['carrier_no_usli'] = 2
cfg['agent_no_gic_office_quoted'] = 777
p.write_text(json.dumps(cfg, indent=2))
"
```

**If prod values differ from defaults: STOP.** `usli_helpers.USLI_CARRIER_NO` constant (added in C.5) and the C.3 / D.2 hardcoded `BrokerId: 1, CarrierNo: 2` payloads must be updated to read from `tests/fixtures/usli_config.json` AND from `Settings`. Add tasks B.4.1, B.4.2 dynamically if this happens.

### Task B.5: Confirm with JC — ambiguous-match folder

> **UPDATE 2026-05-01 — REPLACED by deterministic-lookup architecture.** The original B.5 task ("ask JC about ambiguous-match folder routing") was predicated on name-search being the primary lookup. Empirical Phase B.5 investigation (7 real linked Quotes inspected) showed **the USLI ref is not stored anywhere on Unisoft side**, AND **name-search alone produces ambiguous matches in 30–50% of real cases** (e.g., one insured had 5 distinct USLI refs against 1 Quote ID).
>
> The new B.5 is an architectural spec: see `2026-05-01-usli-deterministic-lookup-architecture.md`. Three-tier deterministic lookup (Mongo by ref → Unisoft search with agent+LOB+recency filter → create), with loop-closure stamping (every Submission we touch gets `ConfirmationNo=usli_ref`).
>
> The `Indemn USLI Needs Review` folder is **dropped** under this architecture — Tier 2 ambiguity uses tiebreak (highest QuoteId), not human triage. The folder constant removal lands in the revised E.1.
>
> JC sign-off is no longer the gate; the architecture lock IS the gate. Implementation lands in C.7 (helper) + revised D.2 (skill).

Send a one-line ask: when the system finds >1 matching Unisoft Quote for a USLI quote email, route to (a) new "Indemn USLI Needs Review" folder, or (b) Inbox with a flag? Default: (a).

```bash
python3 -c "
import json, pathlib
p = pathlib.Path('tests/fixtures/usli_config.json')
cfg = json.loads(p.read_text())
cfg['ambiguous_match_folder'] = 'Indemn USLI Needs Review'  # or 'Inbox'
p.write_text(json.dumps(cfg, indent=2))
"
```

### Task B.6: Add Settings field + Param Store wiring for the ActionId — [NEEDS USER APPROVAL] for prod

> **UPDATE 2026-05-01 — Two values, not one.** Settings + Param Store thread BOTH `usli_quote_action_id: int = 0` AND `usli_quote_letter_name: str = ""`. Param Store paths: `/indemn/{env}/gic-email-intelligence/usli-quote-action-id` and `.../usli-quote-letter-name`. The `aws-env-loader.sh` PARAM_MAP gets two entries. The B-exit gate's fixture-presence check asserts on both. Optional addition: `usli_lookup_recency_days: int = 60` for the C.7 deterministic-lookup helper's recency window.

**Files:**
- Modify: `src/gic_email_intel/config.py`
- Modify: `scripts/aws-env-loader.sh` (PARAM_MAP)
- Test: `tests/test_settings_usli.py` (NEW)
- AWS Param Store dev: `/indemn/dev/gic-email-intelligence/usli-quote-followup-action-id`
- AWS Param Store prod **[NEEDS USER APPROVAL]**: same path under `/indemn/prod/...`

**Step 1: Failing test.**

```python
# tests/test_settings_usli.py
def test_settings_usli_action_id():
    from gic_email_intel.config import Settings
    s = Settings(usli_quote_followup_action_id=101)
    assert s.usli_quote_followup_action_id == 101


def test_settings_usli_action_id_default_zero():
    from gic_email_intel.config import Settings
    s = Settings()
    assert s.usli_quote_followup_action_id == 0
```

(Use direct construction, not `monkeypatch.setenv` + module import — Pydantic Settings caches at module-load.)

**Step 2:** `uv run pytest tests/test_settings_usli.py -v` — expect FAIL.

**Step 3: Implement** in `config.py`. Add field with default 0 (mirroring `unisoft_task_group_id_*` pattern, but with default since it's optional until B.6 sets it):

```python
usli_quote_followup_action_id: int = 0
```

**Step 4:** `uv run pytest tests/test_settings_usli.py -v` — expect PASS.

**Step 5:** Add to `aws-env-loader.sh` PARAM_MAP. Verify:

```bash
bash scripts/aws-env-loader.sh /tmp/test.env
grep USLI_QUOTE_FOLLOWUP_ACTION_ID /tmp/test.env
```

**Step 6:** Set in dev Param Store:

```bash
aws ssm put-parameter --name /indemn/dev/gic-email-intelligence/usli-quote-followup-action-id \
  --value $(jq -r .usli_quote_followup_action_id tests/fixtures/usli_config.json) --type String
```

**Step 7: [NEEDS USER APPROVAL]** Set in prod:

```bash
aws ssm put-parameter --name /indemn/prod/gic-email-intelligence/usli-quote-followup-action-id \
  --value <value-from-fixture> --type String
```

**Step 8: Commit.**

```bash
git add src/gic_email_intel/config.py scripts/aws-env-loader.sh tests/test_settings_usli.py tests/fixtures/usli_config.json
git commit -m "feat(config): add usli_quote_followup_action_id Settings + Param Store wiring"
```

---

## Phase B-exit: Verify Phase B outputs before starting Phase C

**Hard gate. Don't start C until this passes.**

> **UPDATE 2026-05-01 — Assertion list revised.** The original assertions reference fixture keys that no longer exist (`usli_quote_followup_action_id`, `quote_search_request_field`, `quote_usli_ref_field`, `ambiguous_match_folder`). The revised gate is below; the original is preserved for historical record.

**Revised gate (2026-05-01):**

```bash
python3 -c "
import json
cfg = json.load(open('tests/fixtures/usli_config.json'))
required = ['usli_quote_action_id', 'usli_quote_letter_name',
            'pdf_retailer_patterns', 'pdf_applicant_patterns', 'pdf_default_action',
            'broker_id_gic', 'carrier_no_usli', 'agent_no_gic_office_quoted',
            '_b2_canonical_criteria_template', '_b2_canonical_search_op']
missing = [k for k in required if k not in cfg]
assert not missing, f'Missing fixture keys: {missing}'
assert cfg['usli_quote_action_id'] == 67, 'B.1 expected ActionId 67 (Send offer to agent)'
assert cfg['usli_quote_letter_name'] == 'USLI Quote', 'B.1 expected LetterName \"USLI Quote\"'
assert cfg['_b2_canonical_search_op'] == 'GetQuotesForLookupByCriteria', 'B.2 canonical op'
assert cfg['carrier_no_usli'] == 2, 'B.4 USLI CarrierNo divergence — update usli_helpers + C.3/D.2'
assert cfg['broker_id_gic'] == 1, 'B.4 GIC BrokerId divergence — update C.3/D.2'
assert cfg['pdf_default_action'] == 'skip', 'B.3 whitelist policy: default-skip required'
print('B-exit gate (revised 2026-05-01): PASS')
"
```

**Original gate (preserved as historical record):**

```bash
python3 -c "
import json
cfg = json.load(open('tests/fixtures/usli_config.json'))
required = ['usli_quote_followup_action_id', 'quote_search_request_field', 'quote_usli_ref_field',
            'pdf_retailer_patterns', 'pdf_applicant_patterns', 'pdf_customer_patterns',
            'broker_id_gic', 'carrier_no_usli', 'agent_no_gic_office_quoted',
            'ambiguous_match_folder', 'uat_test_insured']
missing = [k for k in required if k not in cfg]
assert not missing, f'Missing fixture keys: {missing}'
assert cfg['usli_quote_followup_action_id'] != 0, 'B.1 not done'
assert cfg['quote_search_request_field'] in ('SearchForValue','Criteria.Name'), 'B.2 search field unconfirmed'
assert cfg['carrier_no_usli'] == 2, 'B.4 USLI CarrierNo divergence — update usli_helpers + C.3/D.2'
assert cfg['broker_id_gic'] == 1, 'B.4 GIC BrokerId divergence — update C.3/D.2'
print('B-exit gate: PASS')
"
```

**Step 2:** Verify dev Param Store value matches:

```bash
aws ssm get-parameter --name /indemn/dev/gic-email-intelligence/usli-quote-followup-action-id --query 'Parameter.Value' --output text
# Should match the fixture value.
```

If anything fails, return to Phase B and complete the missing piece. Do not proceed.

---

## Phase C: New CLI Commands (TDD)

**Test pattern.** `unisoft-proxy/client/cli.py` is a standalone script (no `__init__.py`). The conftest shim added in A.3 puts `unisoft-proxy/client/` on `sys.path`, so tests can `from cli import app` and `from unisoft_client import UnisoftClient`. Mock `cli.get_client` (the function in that module).

### Task C.0: Fix `unisoft_client.get_submissions` PascalCase bug

> **UPDATE 2026-05-01 — SHIPPED.** Commit `ea0fe75`. `tests/test_unisoft_client.py::test_get_submissions_uses_camelcase_quote_id`. Verified empirically against UAT 2026-05-01: with camelCase fix, `GetSubmissions(QuoteId=17129)` returns the 1 known Submission.

**Pre-existing bug.** `unisoft_client.py:126` does `self.call("GetSubmissions", {"QuoteID": quote_id})`. The WSDL `SubmissionListRequest` and the captured SAZ payload both use camelCase `QuoteId`. WCF silently treats unknown elements as null → returns wrong/empty data. C.3 depends on this working.

**Files:**
- Modify: `unisoft-proxy/client/unisoft_client.py`
- Create: `tests/test_unisoft_client.py`

**Step 1: Failing test.**

```python
# tests/test_unisoft_client.py
from unittest.mock import patch
from unisoft_client import UnisoftClient


def test_get_submissions_uses_camelcase_quote_id():
    client = UnisoftClient("http://test", "key")
    with patch.object(client, "call") as mock_call:
        mock_call.return_value = {"Submissions": []}
        client.get_submissions(17129)
        mock_call.assert_called_once_with("GetSubmissions", {"QuoteId": 17129})
```

**Step 2: Run, expect fail.** `uv run pytest tests/test_unisoft_client.py -v`

**Step 3: Fix** at `unisoft_client.py:126`:

```python
def get_submissions(self, quote_id: int) -> dict:
    return self.call("GetSubmissions", {"QuoteId": quote_id})  # was QuoteID — WCF silently dropped
```

**Step 4: Run, pass.** `uv run pytest tests/test_unisoft_client.py -v`

**Step 5: UAT verification.** Pick a UAT Quote known to have Submissions. `Q:17373` from the migration soak has a known UAT Submission (15443/15505). Verify pre/post-fix:

```bash
# Inside SSM session on dev-services with UAT KEY:
curl -4 -s -X POST http://172.31.23.146:5000/api/soap/GetSubmissions \
  -H "X-Api-Key: $KEY" -H 'Content-Type: application/json' -d '{"QuoteId":17373}' \
  | python3 -m json.tool | head -30
# Expected post-fix: real Submissions array with at least one record.
```

**Step 6: Commit.**

```bash
git add unisoft-proxy/client/unisoft_client.py tests/test_unisoft_client.py
git commit -m "fix(unisoft_client): get_submissions sends QuoteId (camelCase) per WSDL"
```

### Task C.1: Wrap `GetQuotesByName2` as `unisoft quote search`

> **UPDATE 2026-05-01 — SHIPPED with revised op + canonical Criteria.** Op shipped is `GetQuotesForLookupByCriteria` (not GetQuotesByName2 — captured UI uses the former). Client method shipped as `search_quotes()` (not `get_quotes_by_name()`). Canonical Criteria shape captured from Fiddler SAZ session 115: see `2026-05-01-unisoft-quote-search-canonical-shape.md`. Tests shipped: `tests/test_unisoft_quote_search.py` (8 tests including canonical-shape regression guards). Plan body below preserved as historical record. Shipped: commit `b2f0f27`.

**Files:**
- Modify: `unisoft-proxy/client/cli.py` (add to `quote_app`)
- Modify: `unisoft-proxy/client/unisoft_client.py` (`get_quotes_by_name`)
- Create: `tests/test_unisoft_quote_search.py`

**Step 1:** Read the request-field name from the fixture (set in B.2):

```bash
python3 -c "import json; print(json.load(open('tests/fixtures/usli_config.json'))['quote_search_request_field'])"
# 'SearchForValue' or 'Criteria.Name' — use this in the implementation below.
```

**Step 2: Failing tests.**

```python
# tests/test_unisoft_quote_search.py
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from cli import app  # via conftest sys.path shim
import pytest

runner = CliRunner()
_FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "usli_config.json").read_text())


def test_quote_search_by_name():
    with patch("cli.get_client") as mock_get:
        client = MagicMock()
        client.get_quotes_by_name.return_value = {
            "Quotes": [{"QuoteID": 17129, "Name": "ABANOLAND LLC", "AgentNumber": 7406, "LOB": "PL", "EffectiveDate": "2026-04-29T00:00:00"}],
            "_meta": {"ReplyStatus": "Success"},
        }
        mock_get.return_value = client
        result = runner.invoke(app, ["quote", "search", "--name", "ABANOLAND", "--compact"])

    assert result.exit_code == 0
    assert "17129" in result.stdout


def test_quote_search_filter_by_lob():
    with patch("cli.get_client") as mock_get:
        client = MagicMock()
        client.get_quotes_by_name.return_value = {"Quotes": [
            {"QuoteID": 1, "Name": "A", "LOB": "CG"},
            {"QuoteID": 2, "Name": "A", "LOB": "PL"},
        ], "_meta": {}}
        mock_get.return_value = client
        result = runner.invoke(app, ["quote", "search", "--name", "A", "--lob", "CG", "--compact"])

    assert "1\t" in result.stdout
    assert "2\t" not in result.stdout


@pytest.mark.uat
def test_quote_search_uat_known_insured():
    """UAT smoke against the test insured discovered in B.2."""
    import subprocess, os
    env = {**os.environ, "PATH": f"{Path(__file__).parent.parent}/bin:" + os.environ.get("PATH", "")}
    result = subprocess.run(
        ["uv", "run", "unisoft", "quote", "search", "--name", _FIXTURE["uat_test_insured"], "--limit", "5", "--compact"],
        capture_output=True, text=True, env=env,
    )
    assert result.returncode == 0
    # At least one row, with a numeric QuoteID
    rows = [r for r in result.stdout.strip().split("\n") if r]
    assert len(rows) >= 1, f"No rows for known insured: {result.stdout}"
```

**Step 3: Run** `uv run pytest tests/test_unisoft_quote_search.py -v -m 'not uat'` — expect fail.

**Step 4: Implement.** Read the request-field name from the fixture at module load time so production code stays in sync:

```python
# unisoft_client.py
import json
from pathlib import Path

_FIXTURES_PATH = Path(__file__).parent.parent.parent / "tests" / "fixtures" / "usli_config.json"
_QUOTE_SEARCH_FIELD = "SearchForValue"
if _FIXTURES_PATH.exists():
    try:
        _QUOTE_SEARCH_FIELD = json.loads(_FIXTURES_PATH.read_text()).get("quote_search_request_field", "SearchForValue")
    except (json.JSONDecodeError, OSError):
        pass


class UnisoftClient:
    # ... existing ...
    def get_quotes_by_name(self, name: str, page: int = 1, per_page: int = 25) -> dict:
        """Search Quotes by insured name. Wraps GetQuotesByName2."""
        params = {"PageNumber": page, "ItemsPerPage": per_page}
        if _QUOTE_SEARCH_FIELD == "Criteria.Name":
            params["Criteria"] = {"Name": name}
        else:
            params[_QUOTE_SEARCH_FIELD] = name
        return self.call("GetQuotesByName2", params)
```

In `cli.py`, add to `quote_app`:

```python
@quote_app.command("search")
def quote_search(
    name: str = typer.Option(..., "--name"),
    lob: Optional[str] = typer.Option(None, "--lob"),
    limit: int = typer.Option(25, "--limit"),
    compact: bool = typer.Option(False, "--compact", "-c"),
):
    """Search Quotes by insured name."""
    client = get_client()
    try:
        result = client.get_quotes_by_name(name, page=1, per_page=limit)
        quotes = result.get("Quotes") or []
        if lob:
            quotes = [q for q in quotes if q.get("LOB") == lob]
        if compact:
            for q in quotes:
                typer.echo(f"{q.get('QuoteID')}\t{q.get('Name')}\t{q.get('AgentNumber')}\t{q.get('LOB')}\t{q.get('EffectiveDate')}")
        else:
            out({"Quotes": quotes, "_meta": result.get("_meta", {})}, compact)
    except UnisoftError as e:
        typer.echo(f"Error: {e.data}", err=True)
        raise typer.Exit(1)
```

**Step 5: Run, pass.** `uv run pytest tests/test_unisoft_quote_search.py -v -m 'not uat'`

**Step 6: UAT smoke.** `uv run pytest tests/test_unisoft_quote_search.py -m uat -v` (requires PATH to include `bin/`).

**Step 7: Commit.**

```bash
git add unisoft-proxy/client/cli.py unisoft-proxy/client/unisoft_client.py tests/test_unisoft_quote_search.py
git commit -m "feat(unisoft): quote search --name (wraps GetQuotesByName2 with fixture-driven request shape)"
```

### Task C.2: Add `--confirmation-no` flag to `unisoft submission create`

> **UPDATE 2026-05-01 — SHIPPED.** Commit `aec13fa`. Tests in `tests/test_unisoft_submission.py` cover with-flag, without-flag (omitted), and explicit empty-string (also omitted) cases.

**Files:**
- Modify: `unisoft-proxy/client/cli.py` (`submission_create`)
- Create: `tests/test_unisoft_submission.py`

**Step 1: Failing tests.**

```python
# tests/test_unisoft_submission.py
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from cli import app

runner = CliRunner()


def test_submission_create_with_confirmation_no():
    with patch("cli.get_client") as mock_get:
        client = MagicMock()
        client.create_submission.return_value = {"Submission": {"SubmissionId": 15443, "SubmissionNo": 15505, "ConfirmationNo": "MGL026A0EZ4"}, "_meta": {}}
        mock_get.return_value = client
        result = runner.invoke(app, ["submission", "create", "--quote-id", "17129", "--carrier", "2", "--confirmation-no", "MGL026A0EZ4", "--description", "USLI Quote — GL", "--compact"])
    assert result.exit_code == 0
    payload = client.create_submission.call_args[0][0]
    assert payload["ConfirmationNo"] == "MGL026A0EZ4"


def test_submission_create_without_confirmation_no_omits_field():
    """Backward compat — existing callers don't pass --confirmation-no."""
    with patch("cli.get_client") as mock_get:
        client = MagicMock()
        client.create_submission.return_value = {"Submission": {"SubmissionId": 1}, "_meta": {}}
        mock_get.return_value = client
        runner.invoke(app, ["submission", "create", "--quote-id", "17129", "--carrier", "2", "--compact"])
    payload = client.create_submission.call_args[0][0]
    assert "ConfirmationNo" not in payload
```

**Step 2: Run, fail.** `uv run pytest tests/test_unisoft_submission.py -v`

**Step 3: Implement.** Add `--confirmation-no` flag to `submission_create`; conditionally insert into `submission_data`.

**Step 4: Run, pass.**

**Step 5: Commit.**

```bash
git add unisoft-proxy/client/cli.py tests/test_unisoft_submission.py
git commit -m "feat(unisoft): submission create accepts --confirmation-no"
```

### Task C.3: Add `unisoft submission update` (`SetSubmission Action=Update`)

> **UPDATE 2026-05-01 — SHIPPED.** Commit `8608121`. `unisoft_client.update_submission()` + `unisoft submission update` CLI with fetch-then-modify pattern. Tests cover preserve-existing-fields, multi-field diff, unaffected-fields-untouched, and not-found error cases. **C.7 (new task above) and Tier 2 backfill in the deterministic-lookup architecture both depend on this.**

**Files:**
- Modify: `unisoft-proxy/client/cli.py`
- Modify: `unisoft-proxy/client/unisoft_client.py`
- Modify: `tests/test_unisoft_submission.py`

**Step 1: Failing tests.**

```python
def test_submission_update_preserves_fields_via_fetch_then_modify():
    existing = {
        "QuoteId": 17129, "SubmissionId": 15443, "SubmissionNo": 15505,
        "BrokerId": 1, "CarrierNo": 2, "Description": "USLI",
        "EffectiveDate": "2026-04-29T00:00:00", "ExpirationDate": "2027-04-29T00:00:00",
        "EnteredByUser": "indemnai", "MgaNo": 1,
    }
    with patch("cli.get_client") as mock_get:
        client = MagicMock()
        client.get_submissions.return_value = {"Submissions": [existing]}
        client.update_submission.return_value = {"Submission": {**existing, "ConfirmationNo": "MGL026A0EZ4"}, "_meta": {}}
        mock_get.return_value = client
        result = runner.invoke(app, ["submission", "update", "--submission-id", "15443", "--quote-id", "17129", "--confirmation-no", "MGL026A0EZ4", "--compact"])
    assert result.exit_code == 0
    payload = client.update_submission.call_args[0][0]
    assert payload["SubmissionId"] == 15443
    assert payload["BrokerId"] == 1  # preserved
    assert payload["ConfirmationNo"] == "MGL026A0EZ4"  # set


def test_submission_update_fails_when_submission_not_found():
    with patch("cli.get_client") as mock_get:
        client = MagicMock()
        client.get_submissions.return_value = {"Submissions": []}
        mock_get.return_value = client
        result = runner.invoke(app, ["submission", "update", "--submission-id", "999", "--quote-id", "1", "--confirmation-no", "X"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower()
```

**Step 2-5:** Implement, run, pass. In `unisoft_client.py`:

```python
def update_submission(self, submission_data: dict) -> dict:
    return self.call("SetSubmission", {"PersistSubmission": "Update", "Submission": submission_data})
```

In `cli.py`, fetch via `client.get_submissions(quote_id)` (now camelCase-correct after C.0), find by `SubmissionId`, apply diff, call `client.update_submission(updated)`.

**Step 6: Commit.**

```bash
git commit -am "feat(unisoft): submission update (wraps SetSubmission Action=Update with fetch-then-modify)"
```

### Task C.4: Generalize `_create_activity_and_notify` (no refactor — keep httpx)

> **UPDATE 2026-05-01 — REAL BUG, plan body revised below.** Original C.4 generalizes the function over `(quote_id, action_id, submission_id)` and adds body validation, but does **NOT** thread `letter_name` for filtering `GetActionNotifications` results. Today's `emails.py:311` does `template = templates[0] if templates and templates[0].get("IsActive") else None` — works for ActionId 6 (one template) but fires the WRONG template for ActionId 67 (which has 25 templates; `LetterName="USLI Quote"` is the discriminator we need). Without the filter, USLI quote emails would silently fire e.g. "Quote Pending" or another wrong-context template to the agent.
>
> **Required signature change:** `_create_activity_and_notify(quote_id, action_id=6, letter_name="", submission_id=0)`. After `GetActionNotifications`, filter `templates` by `LetterName == letter_name` if `letter_name` is non-empty; fall back to `templates[0]` only when `letter_name` is empty (preserves agent_submission backward compat).
>
> **CLI flag:** `gic emails complete <id> --letter-name "USLI Quote"` is added to thread the value through.
>
> **New required test** (in addition to the test sketches below): `test_letter_name_filter_picks_carrier_specific_template`. Mock `GetActionNotifications` to return a list of 25 templates with varied `LetterName` values; assert the chosen one matches the requested LetterName.
>
> The original C.4 sketch below (signature, body validation, existing tests) is otherwise intact — just augmented with `letter_name`. Implementation order: ship C.4 with letter_name first; it's an independent bug fix that improves the agent_submission flow's robustness too (any future ActionId with multiple templates will work correctly).

Decision: keep raw `httpx`. Tests mock `httpx.post`. Refactor to `UnisoftClient` is deferred to Phase K.

**Files:**
- Modify: `src/gic_email_intel/cli/commands/emails.py`
- Create: `tests/test_emails_complete.py`

**Step 1: Pre-flight grep.**

```bash
grep -rn "_create_activity_and_notify" src/ tests/
# Expected: one call site at emails.py:489.
```

**Step 2: Failing tests.**

```python
# tests/test_emails_complete.py
import pytest
from unittest.mock import patch, MagicMock
from gic_email_intel.cli.commands.emails import _create_activity_and_notify


def _mock_responses(action_id):
    """Returns a side_effect callable that mimics the SOAP responses for each operation."""
    def fake_post(url, **kwargs):
        body = kwargs.get("json", {})
        op = url.rsplit("/", 1)[-1]
        resp = MagicMock(status_code=200)
        if op == "GetQuote":
            resp.json.return_value = {"Quote": {"AgentNumber": 7406, "Name": "TEST", "AgentContactID": 12345, "Email": "a@b.com"}, "_meta": {"ReplyStatus": "Success"}}
        elif op == "GetActionNotifications":
            resp.json.return_value = {"Notifications": [{"Subject": "S", "Body": "B"}], "_meta": {"ReplyStatus": "Success"}}
        elif op == "GetContacts":
            resp.json.return_value = {"Contacts": [{"ContactId": 12345, "Email": "a@b.com"}], "_meta": {"ReplyStatus": "Success"}}
        elif op == "SetActivity":
            resp.json.return_value = {"Activity": {"ActivityId": 779999}, "_meta": {"ReplyStatus": "Success"}}
        elif op.endswith("send-activity-email"):
            resp.json.return_value = {"_meta": {"ReplyStatus": "Success"}}
        else:
            resp.json.return_value = {}
        return resp
    return fake_post


@patch("gic_email_intel.cli.commands.emails.httpx.post")
def test_default_action_id_6_for_agent_submission(mock_post):
    """Regression: existing agent_submission flow uses ActionId=6 by default."""
    mock_post.side_effect = _mock_responses(6)
    _create_activity_and_notify(quote_id=17129)
    # Find the SetActivity call
    set_activity_calls = [c for c in mock_post.call_args_list if "SetActivity" in c.args[0]]
    assert len(set_activity_calls) == 1
    payload = set_activity_calls[0].kwargs["json"]
    assert payload["Activity"]["ActionId"] == 6
    assert payload["Activity"]["SubmissionId"] == 0


@patch("gic_email_intel.cli.commands.emails.httpx.post")
def test_usli_action_id_and_submission_id_pass_through(mock_post):
    mock_post.side_effect = _mock_responses(101)
    _create_activity_and_notify(quote_id=17129, action_id=101, submission_id=15443)
    set_activity_calls = [c for c in mock_post.call_args_list if "SetActivity" in c.args[0]]
    payload = set_activity_calls[0].kwargs["json"]
    assert payload["Activity"]["ActionId"] == 101
    assert payload["Activity"]["SubmissionId"] == 15443
    assert payload["Activity"]["QuoteId"] == 17129


@patch("gic_email_intel.cli.commands.emails.httpx.post")
def test_send_activity_email_validates_template_body_not_empty(mock_post):
    """Defense: if rendered body < 100 chars or contains literal [Placeholder], fail-closed."""
    def empty_template(url, **kwargs):
        op = url.rsplit("/", 1)[-1]
        resp = MagicMock(status_code=200)
        if op == "GetActionNotifications":
            resp.json.return_value = {"Notifications": [{"Subject": "S", "Body": ""}], "_meta": {"ReplyStatus": "Success"}}
        else:
            return _mock_responses(101)(url, **kwargs)
        return resp
    mock_post.side_effect = empty_template
    with pytest.raises(ValueError, match="empty notification body"):
        _create_activity_and_notify(quote_id=17129, action_id=101, submission_id=15443)
```

**Step 3: Run, fail.**

**Step 4: Refactor signature + add validation.**

```python
def _create_activity_and_notify(
    quote_id: int,
    action_id: int = 6,
    submission_id: int = 0,
) -> None:
    """Create an activity (bound to Submission if submission_id != 0) and fire notification email."""
    # ... existing GetQuote, GetActionNotifications calls ...
    # NEW: pass action_id to GetActionNotifications instead of hardcoding 6
    # NEW: validate rendered body
    template = notif_resp.get("Notifications", [{}])[0]
    body = template.get("Body", "")
    rendered_body = _render_template(body, merge_fields)
    if len(rendered_body) < 100 or any(ph in rendered_body for ph in ("[ApplicantName]", "[QuoteId]", "[NoticeDate]")):
        raise ValueError(f"empty notification body or unrendered placeholders for ActionId={action_id}")
    # ... existing SetActivity call ...
    # NEW: pass action_id and submission_id to ActivityDTO
    # ... existing SendActivityEmail call ...
```

In `complete_email`:

```python
@app.command("complete")
def complete_email(
    email_id: str = typer.Argument(...),
    status: str = typer.Option("completed", "--status", "-s"),
    quote_id: Optional[int] = typer.Option(None, "--quote-id"),
    submission_id: Optional[int] = typer.Option(None, "--submission-id"),  # already exists
    activity_id: Optional[int] = typer.Option(None, "--activity-id"),
    action_id: int = typer.Option(6, "--action-id", help="ActionId for the activity. 6=Application received from agent (default), 101=USLI Quote Follow-Up."),  # NEW
    task_id: Optional[int] = typer.Option(None, "--task-id"),
    error: Optional[str] = typer.Option(None, "--error"),
    notes: Optional[str] = typer.Option(None, "--notes"),
    move_to: Optional[str] = typer.Option(None, "--move-to"),
):
    # ... existing logic ...
    if quote_id and status == "completed" and not is_duplicate:
        _create_activity_and_notify(quote_id, action_id=action_id, submission_id=submission_id or 0)
```

**Step 5: Run, pass.** All existing tests still green.

**Step 6: Commit.**

```bash
git add src/gic_email_intel/cli/commands/emails.py tests/test_emails_complete.py
git commit -m "feat(emails): generalize _create_activity_and_notify(quote_id, action_id=6, submission_id=0) + body validation"
```

### Task C.5: Idempotency classifier helper (3-layer + multi-LOB)

> **UPDATE 2026-05-01 — Helper rename + whitelist policy.** Replace `is_customer_copy(filename, customer_patterns)` with `should_upload_pdf(filename, retailer_patterns, applicant_patterns)` returning bool — whitelist policy (return True only if filename matches retailer or applicant; default False). Rationale: Family 2 (Retail Web) attachments have no "customer" string, so blacklist-on-customer would miss the bare `{REF}.pdf` declaration page. The `classify_submission_state()` 3-layer logic itself is unchanged; just update the docstring to clarify that empty-ref Submissions in the `update` branch are "legacy untracked, backfill" not "we know this needs an update" (under the deterministic-lookup architecture, every Submission we touch has ConfirmationNo set going forward). The CLI shim `gic submissions classify-usli-state` lands here as planned.

**Files:**
- Create: `src/gic_email_intel/automation/usli_helpers.py`
- Modify: `src/gic_email_intel/cli/commands/submissions.py` (add `classify-usli-state` subcommand)
- Create: `tests/test_usli_idempotency.py`

**Classifier semantics** (per design + decisions #7 #8):

| State of USLI Submissions on Quote | Classifier returns |
|---|---|
| No USLI Submission | `"create_new"` |
| Any USLI Submission with matching ConfirmationNo | `"duplicate_skip"` |
| Any USLI Submission(s) with empty ConfirmationNo | `("update", [list of submission IDs])` — update all empty-ref ones |
| All USLI Submissions have different non-empty ConfirmationNo | `"create_new"` (re-quote, both records preserved per #7) |

**Step 1: Failing tests.**

```python
# tests/test_usli_idempotency.py
from gic_email_intel.automation.usli_helpers import classify_submission_state


def test_no_usli_submission_means_create():
    assert classify_submission_state(submissions=[], usli_ref="MGL026A0EZ4") == "create_new"


def test_matching_ref_means_skip():
    assert classify_submission_state(
        submissions=[{"CarrierNo": 2, "ConfirmationNo": "MGL026A0EZ4", "SubmissionId": 15443}],
        usli_ref="MGL026A0EZ4",
    ) == "duplicate_skip"


def test_empty_ref_means_update_single():
    assert classify_submission_state(
        submissions=[{"CarrierNo": 2, "ConfirmationNo": None, "SubmissionId": 15443}],
        usli_ref="MGL026A0EZ4",
    ) == ("update", [15443])


def test_multi_lob_path1_updates_all_empty_ref():
    """Per design #8: multi-LOB Path 1 updates all empty-ref USLI Submissions."""
    state = classify_submission_state(
        submissions=[
            {"CarrierNo": 2, "ConfirmationNo": None, "SubmissionId": 15443, "LOBNo": 1},
            {"CarrierNo": 2, "ConfirmationNo": "", "SubmissionId": 15444, "LOBNo": 2},
        ],
        usli_ref="MGL026A0EZ4",
    )
    assert state == ("update", [15443, 15444])


def test_different_non_empty_ref_means_create_new():
    """Per design #7: re-quote with new ref → create new Submission, preserve old."""
    assert classify_submission_state(
        submissions=[{"CarrierNo": 2, "ConfirmationNo": "MGL026OLD", "SubmissionId": 15443}],
        usli_ref="MGL026A0EZ4",
    ) == "create_new"


def test_mixed_some_empty_some_different_updates_only_empty():
    """Empty-ref Submissions get updated; different-ref ones are left alone."""
    state = classify_submission_state(
        submissions=[
            {"CarrierNo": 2, "ConfirmationNo": "MGL026OLD", "SubmissionId": 15443},  # leave alone
            {"CarrierNo": 2, "ConfirmationNo": None, "SubmissionId": 15444},  # update
        ],
        usli_ref="MGL026A0EZ4",
    )
    assert state == ("update", [15444])


def test_non_usli_submissions_ignored():
    """Submissions for other carriers don't affect the decision."""
    assert classify_submission_state(
        submissions=[{"CarrierNo": 11, "ConfirmationNo": "AT1234", "SubmissionId": 99}],
        usli_ref="MGL026A0EZ4",
    ) == "create_new"
```

**Step 2: Run, fail.**

**Step 3: Implement.**

```python
# src/gic_email_intel/automation/usli_helpers.py
"""Deterministic helpers for the USLI quote skill — keep logic in code, not LLM prompts."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Literal, Tuple, Union, List

# Read carrier number from fixture; fall back to 2 (USLI canonical)
_FIXTURE = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures" / "usli_config.json"
USLI_CARRIER_NO = 2
if _FIXTURE.exists():
    try:
        USLI_CARRIER_NO = json.loads(_FIXTURE.read_text()).get("carrier_no_usli", 2)
    except (json.JSONDecodeError, OSError):
        pass


SubmissionState = Union[Literal["create_new", "duplicate_skip"], Tuple[Literal["update"], List[int]]]


def classify_submission_state(submissions: list[dict], usli_ref: str) -> SubmissionState:
    """Decide create/update/skip for a USLI Submission given the current Submissions on a Quote.

    Multi-LOB Path 1: if multiple USLI Submissions have empty ConfirmationNo, return all of them
    as update targets (one quote response stamps all empty-ref carrier offers).

    Re-quote: if existing USLI Submission has a different non-empty ref, return create_new
    so both records (old quote + re-quote) are preserved.
    """
    usli = [s for s in submissions if s.get("CarrierNo") == USLI_CARRIER_NO]
    if not usli:
        return "create_new"

    # Layer 1: any matching ref → already processed
    if any(s.get("ConfirmationNo") == usli_ref for s in usli):
        return "duplicate_skip"

    # Layer 2: empty-ref submissions are unstamped placeholders → update them all
    empty = [s for s in usli if not s.get("ConfirmationNo")]
    if empty:
        return ("update", sorted([s["SubmissionId"] for s in empty]))

    # Layer 3: all USLI submissions have different non-empty refs → re-quote, create new
    return "create_new"


def is_customer_copy(filename: str, customer_patterns: list[str]) -> bool:
    """Defense-in-depth: block upload if filename matches customer pattern, even if also matches retailer/applicant."""
    fn = filename.lower()
    return any(p.lower() in fn for p in customer_patterns)
```

**Step 4: Run, pass.**

**Step 5: Expose via `gic submissions classify-usli-state` CLI** so the skill can call it from shell. Use `httpx` directly (not the test-only `sys.path` shim) to keep production runtime clean:

```python
# src/gic_email_intel/cli/commands/submissions.py — new command
@app.command("classify-usli-state")
def classify_usli_state(
    quote_id: int = typer.Option(...),
    usli_ref: str = typer.Option(...),
):
    """Classify Quote's USLI Submissions for the deepagent. Returns JSON state."""
    import httpx, os, json
    from gic_email_intel.config import settings
    from gic_email_intel.automation.usli_helpers import classify_submission_state

    resp = httpx.post(
        f"{settings.unisoft_proxy_url}/api/soap/GetSubmissions",
        json={"QuoteId": quote_id},
        headers={"X-Api-Key": os.environ["UNISOFT_API_KEY"]},
        timeout=30,
    )
    resp.raise_for_status()
    submissions = resp.json().get("Submissions") or []
    state = classify_submission_state(submissions, usli_ref)

    if isinstance(state, str):
        out = {"state": state, "submission_ids": []}
    else:
        out = {"state": state[0], "submission_ids": state[1]}
    typer.echo(json.dumps(out))
```

**Step 6: Failing test for the CLI wrapper** (mock `httpx.post`):

```python
@patch("gic_email_intel.cli.commands.submissions.httpx.post")
def test_classify_usli_state_cli_returns_json_state(mock_post, monkeypatch):
    monkeypatch.setenv("UNISOFT_API_KEY", "test")
    mock_post.return_value = MagicMock(status_code=200, json=lambda: {"Submissions": []})
    runner = CliRunner()
    from gic_email_intel.cli.main import app as gic_app
    result = runner.invoke(gic_app, ["submissions", "classify-usli-state", "--quote-id", "17129", "--usli-ref", "MGL026A0EZ4"])
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    assert out == {"state": "create_new", "submission_ids": []}
```

**Step 7: Commit.**

```bash
git add src/gic_email_intel/automation/usli_helpers.py src/gic_email_intel/cli/commands/submissions.py tests/test_usli_idempotency.py
git commit -m "feat(usli): classify_submission_state helper + CLI (3-layer idempotency, multi-LOB updates all empty-ref Submissions)"
```

### Task C.6: Failure-mode + concurrent-claim + recovery + multi-LOB tests

**Files:**
- Create: `tests/test_usli_failure_modes.py`

**Step 1: Failing tests.**

```python
# tests/test_usli_failure_modes.py
import pytest
from unittest.mock import patch, MagicMock


def test_concurrent_claim_returns_one_winner(monkeypatch):
    """Two concurrent `gic emails next --type usli_quote` claim the same email exactly once."""
    # Use a real Mongo testcontainer or fake collection that supports findOneAndUpdate atomicity.
    # Simulate: insert 1 candidate email, run 2 claims in parallel, assert one returns the doc + other returns null.
    # Existing patterns in tests/test_automation_recovery.py — mirror those.
    pass  # implement using existing claim-test fixtures


def test_stale_claim_recovery_covers_usli_quote(monkeypatch):
    """Recovery loop resets automation_status=processing emails older than 60min for usli_quote type."""
    # Insert a test email with type=usli_quote, automation_status=processing, started_at=70min ago
    # Run recovery
    # Assert automation_status reset to None (or failed_recovery_review per migration design)
    pass


def test_quote_not_found_AND_create_fails_routes_to_inbox(monkeypatch):
    """Path 2 fallback: no Quote found, agency missing → fail to Inbox."""
    pass


def test_multi_match_routes_to_needs_review(monkeypatch):
    """quote search returns >1 → fail to Indemn USLI Needs Review folder."""
    pass


def test_customer_copy_pdf_blocked_even_if_also_matches_retailer():
    from gic_email_intel.automation.usli_helpers import is_customer_copy
    # Defense-in-depth: even if filename also contains "retailer", presence of "customer" wins
    assert is_customer_copy("customer_retailer_combined.pdf", customer_patterns=["customer"])
    assert is_customer_copy("Customer Copy.pdf", customer_patterns=["customer"])
    assert not is_customer_copy("retailer_only.pdf", customer_patterns=["customer"])


def test_activity_creation_failure_after_submission_marks_failed(monkeypatch):
    """If SetActivity fails, automation_status=failed and error includes SubmissionId."""
    pass


def test_email_send_failure_after_activity_marks_failed(monkeypatch):
    """SendActivityEmail failure → automation_status=failed, error includes ActivityId."""
    pass


def test_notification_template_drift_caught(monkeypatch):
    """If template returns unrendered [Placeholder] tokens or empty body, fail-closed."""
    # Already covered in C.4 test_send_activity_email_validates_template_body_not_empty;
    # this test exercises the integration path through the skill's command flow.
    pass
```

**Step 2-5:** Implement each test against the helpers + skill. Some require Mongo testcontainer fixtures.

**Step 6: Commit.**

```bash
git add tests/test_usli_failure_modes.py src/gic_email_intel/automation/usli_helpers.py
git commit -m "test(usli): failure-mode + concurrent-claim + recovery + customer-copy defense"
```

### Task C.7: Deterministic-lookup helper — NEW 2026-05-01

**Spec source:** `2026-05-01-usli-deterministic-lookup-architecture.md` (Tier 1 + Tier 2 + Tier 3 algorithm). This task implements the algorithm as a helper + CLI, which D.2 then calls instead of embedding lookup logic in skill prose.

**Files:**
- Create: `src/gic_email_intel/automation/usli_helpers.py::find_quote_for_usli_ref()`
- Create: `src/gic_email_intel/cli/commands/submissions.py::find_quote_for_usli` (new subcommand)
- Create: `tests/test_usli_lookup.py`

**Step 1: Mongo index.** Add a one-shot migration (or document a manual `db.submissions.createIndex({"reference_numbers": 1, "unisoft_quote_id": 1})` step in the runbook). Multi-key index over the `reference_numbers` array. Idempotent — Mongo handles re-runs gracefully.

**Step 2: Helper signature.**

```python
def find_quote_for_usli_ref(
    usli_ref: str,
    insured_name: str,
    agent_no: int,
    lob: str,
    *,
    skip_backfill: bool = False,
    mongo_only: bool = False,
) -> dict:
    """
    Returns:
      {"state": "found"|"ambiguous"|"create_new",
       "quote_id": int|None,
       "lookup_path": "tier_1_mongo"|"tier_2_name_search"|"tier_3_create_new",
       "candidates": [...],         # populated only on ambiguous
       "tiebreak_applied": str|None,
       "backfill_applied": dict|None}
    """
```

**Step 3: Failing tests** for each branch:

- `test_tier_1_mongo_hit_returns_directly` — seed Mongo with a submission having the ref linked; assert no Unisoft call is made.
- `test_tier_1_mongo_miss_falls_to_tier_2` — empty Mongo; assert `search_quotes` is called.
- `test_tier_2_single_match_after_filter_backfills` — mock `search_quotes` returning 1 hit after agent+LOB+date filter; assert state="found", lookup_path="tier_2_name_search", and BOTH backfill writes happen (Mongo `unisoft_quote_id` set + `unisoft submission update` called with the ref).
- `test_tier_2_zero_hits_returns_create_new` — assert state="create_new".
- `test_tier_2_multiple_hits_tiebreak_to_highest_quote_id` — mock 3 candidates; assert state="found", tiebreak_applied="highest_quote_id", chosen Quote is highest ID, backfill happens.
- `test_tier_2_lob_filter_applies` — multi-LOB candidates, only matching LOB returned.
- `test_tier_2_recency_filter_applies` — candidate older than 60d filtered out.
- `test_skip_backfill_flag_short_circuits_writes` — caller passes `skip_backfill=True` (used by the CLI's `--mongo-only` flag); no writes happen.
- `test_mongo_only_flag_returns_None_on_tier_1_miss` — caller passes `mongo_only=True`; if Mongo doesn't have it, returns `state="create_new", quote_id=None` without calling Unisoft.

**Step 4: Implement** following the algorithm in the architecture artifact. Key implementation notes:
- **LOB-prefix → Unisoft-LOB mapping:** `MGL→CG, MPL→CP, MSE→Special Events, NPP→CG, XSL→CU, ...` — fixture-driven, in `tests/fixtures/usli_config.json` as `usli_ref_prefix_to_lob` (a new fixture key, populated as observed in soak).
- **Recency window:** 60 days from `LastActivityDate` on the candidate; configurable via Settings (`usli_lookup_recency_days: int = 60`).
- **Active status:** `StatusId != 2` (2 = closed/declined per Q:17129's StatusId=2 we saw).
- **Backfill writes:** done via the existing `unisoft submission update` (C.3) and a direct Mongo update. Both are idempotent — re-running is safe.

**Step 5: CLI shim.**

```bash
gic submissions find-quote-for-usli \
    --usli-ref MGL026A6ER4 \
    --insured "Las Marias Properties LLC" \
    --agent-no 7406 \
    --lob CG \
    [--mongo-only] \
    [--skip-backfill]
```

Returns the JSON shape from Step 2 to stdout.

**Step 6: Commit.**

```bash
git add src/gic_email_intel/automation/usli_helpers.py \
        src/gic_email_intel/cli/commands/submissions.py \
        tests/test_usli_lookup.py \
        tests/fixtures/usli_config.json
git commit -m "feat(usli): deterministic Quote lookup (Tier 1 Mongo / Tier 2 search / Tier 3 create + backfill)"
```

---

## Phase D: New Skill + Agent Factory

### Task D.1: Extend `_load_skill` for new placeholder

> **UPDATE 2026-05-01 — Two placeholders, not one.** `_load_skill` adds BOTH `{usli_quote_action_id}` AND `{usli_quote_letter_name}` substitutions to the `text.format(...)` call. Test asserts both values land in the rendered skill prose.

**Files:**
- Modify: `src/gic_email_intel/automation/agent.py`
- Modify: `tests/test_skill_loading.py`

**Step 1: Failing test.**

```python
def test_load_skill_substitutes_usli_action_id(monkeypatch, tmp_path):
    skill_dir = tmp_path / "skills"
    skill_dir.mkdir()
    (skill_dir / "test-skill.md").write_text("Use action {usli_quote_followup_action_id}")
    monkeypatch.setattr("gic_email_intel.automation.agent.SKILLS_DIR", skill_dir)

    from gic_email_intel.automation import agent as agent_mod
    monkeypatch.setattr(agent_mod, "Settings", lambda: type("S", (), {
        "graph_user_email": "x@y", "unisoft_task_group_id_newbiz": 3, "unisoft_task_group_id_wc": 4,
        "usli_quote_followup_action_id": 101,
    })())

    assert "Use action 101" in agent_mod._load_skill("test-skill")
```

**Step 2: Run, fail.** `uv run pytest tests/test_skill_loading.py::test_load_skill_substitutes_usli_action_id -v`

**Step 3: Implement.** Add `usli_quote_followup_action_id=s.usli_quote_followup_action_id` to the `text.format(...)` call in `_load_skill`.

**Step 4: Run, pass. Step 5: Commit.**

```bash
git commit -am "feat(automation): _load_skill supports {usli_quote_followup_action_id} placeholder"
```

### Task D.2: Create `process-usli-quote.md` skill

> **UPDATE 2026-05-01 — Major rewrite.** The skill no longer embeds the lookup algorithm in prose. Instead Step 2 calls a single CLI shim wrapping the C.7 helper:
>
> ```
> gic submissions find-quote-for-usli --usli-ref REF --insured "..." --agent-no NNN --lob CG
> → returns JSON: {"state": "found"|"ambiguous"|"create_new", "quote_id": N|null, "lookup_path": ...}
> ```
>
> The skill branches on `state` only — no name-search, no agent-match, no recency-filtering done in skill prose (all in C.7). Step 6 (PDF upload) reads `pdf_retailer_patterns` + `pdf_applicant_patterns` from fixture and applies whitelist (NOT blacklist on customer). Step 7 (`gic emails complete`) passes both `--action-id` (67) AND `--letter-name` ("USLI Quote") via the C.4-revised CLI. Skill prose mentions both filename Families (Family 1 manual UW + Family 2 Retail Web) but doesn't try to distinguish — the whitelist works for both. The `Indemn USLI Needs Review` folder is removed from the skill's failure-routing decisions.

**Files:**
- Create: `src/gic_email_intel/automation/skills/process-usli-quote.md`

**Step 1:** Write the skill markdown. Mirror `create-quote-id.md` structure. Critical sections:

- **Business Context** — USLI as carrier; two upstream paths; system discovers which.
- **Sub-Patterns** — three subject shapes from B.3 corpus.
- **LOB Mapping** — USLI ref prefix → Unisoft LOB code (MGL→CG, MPL→CP, MSE→Special Events, etc.).
- **PDF Version Detection** — patterns from B.3. Upload retailer + applicant; **skip customer (PII risk — block upload even on overlap)**.
- **Step 1: Claim** — `gic emails next --type usli_quote --json`.
- **Step 2: Find Quote** — `unisoft quote search --name "..." [--lob ...]`. Disambiguation hierarchy: agent_no + LOB + effective-date within 60d.
  - 0 hits → Path 2 (Step 3a).
  - 1 hit → Path 1 (Step 3b).
  - >1 hits → fail to "{ambiguous_match_folder}" folder, STOP.
- **Step 3a (Path 2):** `unisoft quote create ...`.
- **Step 3b (Path 1):** Use existing Quote.
- **Step 4: Idempotency state** — `gic submissions classify-usli-state --quote-id N --usli-ref REF` returns JSON `{"state": "create_new"|"duplicate_skip"|"update", "submission_ids": [...]}`.
  - `duplicate_skip` → mark complete with notes, route to Duplicates, STOP.
  - `create_new` → Step 5a.
  - `update` → Step 5b (iterate `submission_ids`).
- **Step 5a:** `unisoft submission create --quote-id N --carrier 2 --confirmation-no <REF> --description "USLI Quote — {LOB}"`. Capture new SubmissionId.
- **Step 5b:** For each ID in `submission_ids`: `unisoft submission update --submission-id <ID> --quote-id N --confirmation-no <REF>`. Pick the highest SubmissionId as the activity binding target.
- **Step 6:** Upload retailer + applicant PDFs. Use `unisoft attachment upload --category offer` (NOT raw category IDs). Skip customer copies even if filename also matches retailer pattern.
- **Step 7: Record completion** — `gic emails complete <id> --quote-id N --submission-id M --action-id {usli_quote_followup_action_id} --notes "..." --move-to "Indemn USLI Processed"`.
- **Multi-LOB Path 1 with multiple existing Submissions** — Step 4's `update` state handles this: all empty-ref USLI Submissions get the new ref; activity binds to the most-recent SubmissionId; notes reference all updated IDs. PDFs upload at Quote level (once, regardless of Submission count).
- **When to Fail** — Quote not found AND quote create fails → Inbox; multi-match → Indemn USLI Needs Review; partial state → fail with full context.
- **Rules** — One email per invocation; never fabricate data; never skip the customer-copy block.

Use placeholders: `{graph_user_email}`, `{usli_quote_followup_action_id}`.

**Step 2:** Smoke-check skill loads + substitutes correctly.

```bash
USLI_QUOTE_FOLLOWUP_ACTION_ID=101 uv run python -c "
from gic_email_intel.automation.agent import _load_skill
result = _load_skill('process-usli-quote')
assert '101' in result, 'placeholder not substituted'
assert '{usli_quote_followup_action_id}' not in result
print('OK')
"
```

**Step 3: Commit.**

```bash
git add src/gic_email_intel/automation/skills/process-usli-quote.md
git commit -m "feat(automation): add process-usli-quote skill"
```

### Task D.3: Add `create_automation_agent_usli()` factory

**Files:**
- Modify: `src/gic_email_intel/automation/agent.py`
- Create: `tests/test_automation_agent_factories.py`

**Step 1: Failing test** with strong assertions on skill content.

```python
def test_create_automation_agent_usli_uses_usli_skill(monkeypatch):
    from gic_email_intel.automation import agent as agent_mod
    monkeypatch.setattr(agent_mod, "_resolve_model", lambda _m: MagicMock())
    captured = {}
    monkeypatch.setattr(agent_mod, "create_deep_agent", lambda **kw: captured.update(kw) or kw)
    monkeypatch.setenv("USLI_QUOTE_FOLLOWUP_ACTION_ID", "101")

    agent_mod.create_automation_agent_usli()

    prompt = captured["system_prompt"]
    assert "process-usli-quote" not in prompt  # filename, not content
    assert "USLI Quote" in prompt
    assert "broker = GIC" in prompt
    assert "carrier = USLI" in prompt
    assert "{usli_quote_followup_action_id}" not in prompt  # substituted
    assert "101" in prompt  # placeholder value substituted
```

**Step 2: Run, fail.** `uv run pytest tests/test_automation_agent_factories.py -v`

**Step 3: Implement** parallel `_build_usli_system_prompt()` and `create_automation_agent_usli()`.

**Step 4: Run, pass. Step 5: Commit.**

```bash
git commit -am "feat(automation): create_automation_agent_usli() factory"
```

### Task D.4: Wire dispatch + `pause-usli-automation` env

**Files:**
- Modify: `src/gic_email_intel/cli/commands/automate.py`
- Modify: `src/gic_email_intel/config.py` (add `pause_usli_automation` field, mirror `pause_sync` etc.)
- Modify: `tests/test_automate.py` (or create)

**Step 1: Failing tests** for both dispatch + pause-flag enforcement.

```python
def test_automate_run_dispatches_to_usli_factory(monkeypatch):
    from gic_email_intel.automation import agent as agent_mod
    calls = {"agent_submission": 0, "usli_quote": 0}
    monkeypatch.setattr(agent_mod, "create_automation_agent", lambda **kw: calls.__setitem__("agent_submission", calls["agent_submission"] + 1) or MagicMock())
    monkeypatch.setattr(agent_mod, "create_automation_agent_usli", lambda **kw: calls.__setitem__("usli_quote", calls["usli_quote"] + 1) or MagicMock())

    from gic_email_intel.cli.commands.automate import _get_agent_factory
    _get_agent_factory("usli_quote")()
    assert calls["usli_quote"] == 1


def test_automate_run_respects_pause_usli_automation(monkeypatch):
    """When pause_usli_automation=True, the loop tick is a no-op."""
    monkeypatch.setenv("PAUSE_USLI_AUTOMATION", "true")
    # ... call automate.run with type=usli_quote, assert no factory invocation
    pass
```

**Step 2: Run, fail. Step 3: Implement.**

```python
# automate.py
_AGENT_FACTORIES = {
    "agent_submission": "create_automation_agent",
    "usli_quote": "create_automation_agent_usli",
}

def _get_agent_factory(email_type: str):
    name = _AGENT_FACTORIES.get(email_type)
    if not name:
        raise typer.BadParameter(f"No automation agent registered for email_type={email_type}")
    from gic_email_intel.automation import agent as agent_mod
    return getattr(agent_mod, name)
```

In the loop tick body, mirror the existing `pause_processing` / `pause_automation` checks:

```python
settings = Settings()  # reload per tick
if email_type == "usli_quote" and settings.pause_usli_automation:
    return  # skip the tick
```

In `config.py`:

```python
pause_usli_automation: bool = False
```

**Step 4: Run, pass. Step 5: Commit.**

```bash
git commit -am "feat(automate): type→factory dispatch + PAUSE_USLI_AUTOMATION enforcement"
```

---

## Phase E: Folder Routing Additions

### Task E.1: Factor `ensure_folder_exists` + add new folder constants + behavioral test

> **UPDATE 2026-05-01 — Drop the `Indemn USLI Needs Review` folder.** Under the deterministic-lookup architecture, Tier 2 ambiguity uses tiebreak (highest QuoteId), not human triage — so there's no normal-flow case routing to a Needs Review folder. Only `INDEM_USLI_PROCESSED = "Indemn USLI Processed"` lands in the folder constants. Failure cases (Quote-creation fails, Activity-creation fails after Submission, Email-send fails) still route to `Inbox` per existing pattern. The `INDEM_USLI_NEEDS_REVIEW` constant is dropped from this task; the folder is not created in H.0 either.

**Files:**
- Modify: `src/gic_email_intel/core/email_mover.py`
- Modify: `tests/test_email_mover.py` (or create)

**Step 1:** Read `email_mover.py`. Confirm `move_email_to_folder` auto-creates inline.

**Step 2: Failing tests** — including a behavioral test of the factored helper.

```python
def test_indem_usli_folder_constants():
    from gic_email_intel.core.email_mover import INDEM_USLI_PROCESSED, INDEM_USLI_NEEDS_REVIEW
    assert INDEM_USLI_PROCESSED == "Indemn USLI Processed"
    assert INDEM_USLI_NEEDS_REVIEW == "Indemn USLI Needs Review"


def test_ensure_folder_exists_idempotent(monkeypatch):
    """Behavioral: calling twice should not raise; first call creates, second is a no-op."""
    from gic_email_intel.core.email_mover import ensure_folder_exists
    created = []
    fake_client = MagicMock()
    fake_client.list_folders.return_value = []  # initial: empty
    fake_client.create_folder.side_effect = lambda name, parent: created.append(name)

    with patch("gic_email_intel.core.email_mover.get_graph_client", return_value=fake_client):
        ensure_folder_exists("Test Folder")
        # Second call — folder now "exists"
        fake_client.list_folders.return_value = [{"displayName": "Test Folder"}]
        ensure_folder_exists("Test Folder")

    assert created == ["Test Folder"]  # only created once
```

**Step 3: Run, fail. Step 4: Implement.**

```python
# email_mover.py
INDEM_PROCESSING = "Indemn - Processing"
INDEM_PROCESSED = "indemn processed"
INDEM_DUPLICATES = "Duplicates"
INDEM_USLI_PROCESSED = "Indemn USLI Processed"
INDEM_USLI_NEEDS_REVIEW = "Indemn USLI Needs Review"


def ensure_folder_exists(folder_name: str, parent: str = "Inbox") -> None:
    """Idempotently create the named folder under parent if missing."""
    client = get_graph_client()
    existing = [f.get("displayName") for f in client.list_folders()]
    if folder_name not in existing:
        client.create_folder(folder_name, parent)
```

`move_email_to_folder` calls `ensure_folder_exists(folder_name)` instead of inline create.

**Step 5: [NEEDS USER APPROVAL]** Smoke against live mailbox.

```bash
uv run python -c "
from gic_email_intel.core.email_mover import ensure_folder_exists
ensure_folder_exists('Indemn USLI Processed')
ensure_folder_exists('Indemn USLI Needs Review')
"
```

**Step 6: Commit.**

```bash
git commit -am "refactor(email_mover): factor ensure_folder_exists + USLI folder constants + behavioral test"
```

---

## Phase G: UAT Soak

### Task G.0: Add `automation-usli-cron` container + verify recovery loop covers usli_quote

**Files:**
- Modify: `docker-compose.yml`
- Test: extend `tests/test_automation_recovery.py`

**Step 1: Failing test** — recovery covers `usli_quote` email type.

```python
def test_recovery_resets_stale_usli_quote_claims(seeded_mongo):
    # Seed an email with type=usli_quote, automation_status=processing, started_at=70min ago
    # Run the recovery function
    # Assert reset
    pass
```

**Step 2: Run, fail. Step 3: Implement** — confirm the existing recovery query doesn't filter by type, OR add `usli_quote` to its allowed list.

**Step 4: docker-compose entry.**

```yaml
automation-usli-cron:
  <<: *common
  container_name: gic-email-automation-usli
  command: python -m gic_email_intel.cli.main automate run --loop --interval 900 --type usli_quote --max 50
  cpus: "1.0"
  mem_limit: 2G
  environment:
    <<: *dd-env
    DD_SERVICE: gic-email-automation-usli
  labels:
    com.datadoghq.ad.logs: >-
      [{"source":"python","service":"gic-email-automation-usli","log_processing_rules":[{"type":"include_at_match","name":"include_app_logs_only","pattern":"\"app_log\":\\s*true"}]}]
```

**Step 5: Commit.**

```bash
git commit -am "infra: automation-usli-cron container + recovery coverage for usli_quote"
```

### Task G.1: Open PR + deploy to dev-services

**Step 1: SOAK_MODE wiring for USLI flow.** The flag is already present (`settings.soak_mode`, used at `emails.py:370` and `email_mover.py:37`) and dev-services should already have it enabled per the pre-flight check.

Confirm the new USLI flow respects it. In `complete_email`, when `soak_mode=true`:
- Skip `move_email_to_folder` (no Outlook inbox folder change — critical, since dev and prod share the customer inbox)
- Skip `_create_activity_and_notify`'s `SendActivityEmail` call (Submission + Activity are still created in UAT Unisoft, but no real email goes to the agent)

**Failing test:**

```python
# tests/test_emails_complete.py — add
@patch("gic_email_intel.cli.commands.emails.httpx.post")
@patch("gic_email_intel.cli.commands.emails.move_email_to_folder")
def test_soak_mode_skips_folder_move_and_email_send(mock_move, mock_post, monkeypatch):
    monkeypatch.setenv("SOAK_MODE", "true")
    mock_post.side_effect = _mock_responses(101)
    # Run complete_email with completed status + quote_id
    # ... invoke `gic emails complete <id> --quote-id 17129 --action-id 101 --submission-id 15443 --move-to "Indemn USLI Processed"` ...
    assert mock_move.call_count == 0
    # No SendActivityEmail call
    send_email_calls = [c for c in mock_post.call_args_list if "send-activity-email" in c.args[0]]
    assert len(send_email_calls) == 0
    # SetActivity STILL called (Submission + Activity get created in UAT)
    set_activity_calls = [c for c in mock_post.call_args_list if "SetActivity" in c.args[0]]
    assert len(set_activity_calls) == 1
```

Run, fail, implement (gate the calls on `settings.soak_mode`), run, pass, commit.

**Step 2: [NEEDS USER APPROVAL]** Push feature branch + open PR.

```bash
git push indemn feat/usli-quote-automation
gh pr create --repo indemn-ai/gic-email-intelligence --base main --head feat/usli-quote-automation \
  --title "feat: USLI quote automation" \
  --reviewer dolly45,dhruvrajkotia
```

**Step 3:** Once merged, dev-services container redeploys via `build.yml`.

### Task G.2: Process N real `usli_quote` emails into UAT — [NEEDS USER APPROVAL]

UAT writes (Submission/Activity creation in UAT Unisoft). Reads/writes against `_devsoak` Mongo DB. SOAK_MODE active so no Outlook folder changes + no real agent emails.

dev-services has its own sync cron pulling fresh real USLI quote emails into `_devsoak` continuously, so there's a live data feed. Verify before invoking:

```bash
URI=$(aws secretsmanager get-secret-value --secret-id indemn/dev/gic-email-intelligence/mongodb-uri --query SecretString --output text)
aws ssm send-command --instance-ids i-0fde0af9d216e9182 --document-name AWS-RunShellScript \
  --parameters "commands=[\"docker run --rm --network host mongo:6 mongosh '${URI}/gic_email_intelligence_devsoak' --quiet --eval 'db.emails.countDocuments({\\\"classification.email_type\\\":\\\"usli_quote\\\", automation_status: null})'\"]" \
  --query 'Command.CommandId' --output text
# Expected: at least 5 candidates available in _devsoak.
# If 0: dev sync may not be classifying yet; check container logs and seed manually if needed.
```

Then invoke the new USLI cron:

```bash
aws ssm send-command --instance-ids i-0fde0af9d216e9182 --document-name AWS-RunShellScript \
  --parameters 'commands=["docker exec gic-email-automation-usli python -m gic_email_intel.cli.main automate run --type usli_quote --max 10"]' \
  --query 'Command.CommandId' --output text
```

Verify in UAT Unisoft for each email:
- Quote exists / created
- USLI Submission added/enriched with ConfirmationNo (and for multi-LOB Path 1: ALL empty-ref Submissions enriched)
- Retailer + applicant PDFs uploaded; **0 customer copies**
- Activity logged with chosen ActionId
- (SOAK_MODE skipped real `SendActivityEmail` — verify via container logs, NOT by checking the agent's inbox)
- (SOAK_MODE skipped folder moves — verify the email's `folder` field unchanged in `_devsoak`, AND no folder change visible in the customer Outlook inbox)

### Task G.3: Soak metrics gate Phase H

> **UPDATE 2026-05-01 — Revised thresholds + new metrics.** Replace the original "ambiguous-match rate < 5%" with a tighter set reflecting the deterministic-lookup architecture. New metrics:
>
> | Metric | Soak threshold | Steady-state (≥ 2 weeks) | Notes |
> |---|---|---|---|
> | Successful end-to-end runs | ≥ 10 distinct usli_quote emails | n/a | unchanged |
> | Tier 1 hit rate | ≥ 0% (start) | ≥ 95% | new; index fills as we process emails |
> | Tier 2 ambiguous-tiebreak rate | < 5% | < 1% | replaces "ambiguous-match rate" |
> | **Stamping success rate** (every Submission ends with non-null `ConfirmationNo`) | **= 100%** | **= 100%** | new — non-negotiable; failure means loop-closure broken |
> | Customer-copy uploads to Unisoft | = 0 | = 0 | unchanged (whitelist policy) |
> | Notification template empty/unrendered | = 0 | = 0 | unchanged |
> | Stale-claim recovery activations | = 0 | = 0 | unchanged |
> | Path 1 enrichment correctness | All empty-ref Submissions on multi-LOB Quote received ref | n/a | unchanged |
>
> A failure on stamping success is a hard stop — every USLI Submission we touch MUST end with `ConfirmationNo` set, otherwise Tier 1 lookups can't function and the architecture degrades back to name-search-with-tiebreak. Document in `tests/fixtures/usli_soak_report.json` (committed); walk JC through the report.

**Numerical thresholds.** Phase H does not start until G.3 reports:

| Metric | Threshold |
|---|---|
| Successful end-to-end soak runs | ≥ 10 distinct usli_quote emails |
| Ambiguous-match rate (>1 quote search hit) | < 5% |
| Customer-copy uploads to Unisoft | **= 0** (defense passed) |
| Notification template empty/unrendered | **= 0** |
| Stale-claim recovery activations | = 0 |
| Path 1 enrichment correctness check | All empty-ref Submissions on multi-LOB Quote received ref |

Document in `tests/fixtures/usli_soak_report.json` (committed). Walk JC through the report.

### Task G.4: Validate with JC

Walk JC through 5 cases in UAT Unisoft directly (cover both Path 1 and Path 2). Get sign-off in writing.

### Task G.5: Draft customer comms — [NEEDS USER APPROVAL]

Craft the T-0 announcement to JC for Phase H. Mirror the 4/24 weekly recap voice. Save draft in Gmail Drafts; Craig reviews and sends at H.4.

---

## Phase H: Production Rollout — [NEEDS USER APPROVAL] (entire phase)

Verify DEVOPS-158 is **Done** AND G.3 thresholds met before starting.

### Task H.0: Create prod folders on quote@ inbox — [NEEDS USER APPROVAL]

Live customer mailbox write.

```bash
uv run python -c "
from gic_email_intel.core.email_mover import ensure_folder_exists
ensure_folder_exists('Indemn USLI Processed')
ensure_folder_exists('Indemn USLI Needs Review')
"
```

### Task H.1: Verify gates

```bash
linearis-proxy.sh issues list --filter '{"id":{"eq":"DEVOPS-158"}}' --json | jq -r '.[].state'
# Expected: "Done". If "In Progress", STOP.

# G.3 metrics file must exist + thresholds met
python3 -c "
import json
r = json.load(open('tests/fixtures/usli_soak_report.json'))
assert r['successful_runs'] >= 10
assert r['ambiguous_match_rate'] < 0.05
assert r['customer_copy_uploads'] == 0
assert r['template_empty_unrendered'] == 0
assert r['stale_recovery_activations'] == 0
print('G.3 gate: PASS')
"
```

### Task H.2: Wire baseline Datadog alerts (depends on DEVOPS-156 / PR #19) — [NEEDS USER APPROVAL]

Wire BEFORE deploy (alerting on a paused service is fine; alerting after unpause is too late).

Three minimum alerts:
- USLI automation failure rate > 10% over 1h
- `Indemn USLI Needs Review` folder count > 5
- `automation_status: failed_recovery_review` count > 0 (covered by migration alerting once PR #19 lands)

If DEVOPS-156 / PR #19 hasn't landed: STOP. Don't proceed to H.3 without alerting.

### Task H.3: Deploy to prod-services — [NEEDS USER APPROVAL]

PR `main` → `prod` (gated branch). Reviewers: Dolly + Dhruv. Push prod branch — `build-prod.yml` deploys with USLI gated by `pause-usli-automation=true`.

```bash
aws ssm put-parameter --name /indemn/prod/gic-email-intelligence/pause-usli-automation --value "true" --overwrite
```

### Task H.4: Verify alerts firing on test events — [NEEDS USER APPROVAL]

**Hard gate before H.5.** Trigger synthetic test events (e.g., manually mark a test email `automation_status=failed`, verify Datadog alert fires within expected window).

```bash
# Manually fire each baseline alert; observe Datadog receives + routes correctly.
# Document outcomes inline.
```

If any alert doesn't fire as expected, STOP — fix alerting before unpause.

### Task H.5: Send T-0 customer comms + flip the switch — [NEEDS USER APPROVAL]

Send the comms drafted in G.5. Then unpause:

```bash
aws ssm put-parameter --name /indemn/prod/gic-email-intelligence/pause-usli-automation --value "false" --overwrite
```

Container picks up next tick (settings reload per tick — confirm via logs). Watch first 5 real cases land.

### Task H.6: Post-cutover watch (24-hour hands-on)

Distinct from DEVOPS-158 soak. This is the immediate-after-unpause monitoring window.

Monitoring:
- `automation_status: failed` count for `usli_quote`
- Datadog alerts
- Container health
- Folder counts (Processed, Needs Review, Duplicates)
- Customer-copy uploads (must remain 0)

If any pattern, pause via env var.

---

## Phase K: Post-Launch Follow-ups

1. **K.1: Stranded usli_quote emails from cutover window** — query Mongo NOW (before H) to count:

   ```bash
   docker run --rm --network host mongo:6 mongosh "${URI}/gic_email_intelligence" --quiet --eval '
     db.emails.countDocuments({
       "classification.email_type": "usli_quote",
       received_at: {$lt: ISODate("2026-04-29T22:50:00Z")},
       received_at: {$gt: ISODate("2026-04-29T21:10:00Z")},
       automation_status: null
     })
   '
   ```

   Document count. Decide policy: one-shot manual run with lower cutoff, OR add to JC's manual-handle list. **[NEEDS USER APPROVAL]** to execute one-shot.

2. **K.2: Refactor `_create_activity_and_notify` to `UnisoftClient`** — code quality. Defer until prod stable ≥ 2 weeks.

3. **K.3: Pendings + declines automation** (`usli_pending`, `usli_decline`) — separate workstream.

4. **K.4: Multi-skill agent dispatch refactor** — when adding a 3rd email type.

5. ~~**K.5: Exact-match Quote lookup** — IF B.2 found a real `quote_usli_ref_field`, add a fast path that searches Unisoft by ref before falling to name search.~~ **SUPERSEDED 2026-05-01.** Empirically no Unisoft field stores the USLI ref. The equivalent capability is folded into v1 as the C.7 deterministic-lookup helper (Tier 1 = Mongo by ref, Tier 2 = Unisoft name-search-with-filter, Tier 3 = create + stamp). See `2026-05-01-usli-deterministic-lookup-architecture.md`.

6. **K.6: Datadog dashboards for USLI** — beyond H.2 baseline alerts.

7. **K.7: Doc updates** — `CLAUDE.md` (skills + flags), `docs/runbook.md` (USLI failure modes, folder taxonomy, ActionId reference). Single PR after H closes.

8. **K.8: Backfill `Submission.ConfirmationNo` for historical USLI Quotes** — NEW 2026-05-01. The deterministic-lookup architecture's loop closure stamps `Submission.ConfirmationNo = usli_ref` on every Submission we create or touch. The ~7 historical USLI-linked Quotes in our Mongo (verified 2026-05-01) currently have null `ConfirmationNo` on their USLI Submissions. One-shot script reads `db.submissions.find({unisoft_quote_id: {$ne: None}, intake_channel: "usli_retail_web"})`, fetches each Submission via `unisoft submission list --quote-id N`, and runs `unisoft submission update --confirmation-no <ref>` for each. **[NEEDS USER APPROVAL]** before running against prod (writes to Unisoft prod). Defer until 1 week post-launch when Tier 1 hit rate is observable.

---

## Sibling PR worktree setup

Each sibling PR gets its own worktree off `indemn/main`. None branch off the USLI feature branch.

```bash
cd /Users/home/Repositories/gic-email-intelligence-migration
git fetch indemn

# Sibling 1
git worktree add ../gic-eml-sibling-1 -b fix/devops-163 indemn/main
# Sibling 2
git worktree add ../gic-eml-sibling-2 -b fix/devops-164 indemn/main
# Sibling 3
git worktree add ../gic-eml-sibling-3 -b fix/devops-165 indemn/main
# Sibling 4 (after Sibling 3 merged)
git worktree add ../gic-eml-sibling-4 -b fix/devops-165-backfill indemn/main
```

**File overlap awareness:**
- `unisoft-proxy/client/cli.py` — modified by Sibling 1 (task subject) AND Phase C (USLI). Both add new code, low textual conflict, but rebase Sibling 1 last to be safe.
- `docker-compose.yml` — modified by Sibling 2 (cron intervals) AND Phase G.0 (new container). Both add YAML blocks. **Direct conflict risk** — recommend Sibling 2 lands first, USLI G.0 rebases on it.
- `src/gic_email_intel/cli/commands/emails.py` — modified by Sibling 3 (export) AND Phase C.4 (helper). Different functions, low conflict.

**Recommended merge order:** Sibling 2 → Sibling 1 → Sibling 3 → USLI feature → Sibling 4.

---

## Sibling PR 1 — Task subject format `[LOB] - description` (DEVOPS-163)

Worktree: `../gic-eml-sibling-1` off `indemn/main`. Independent of USLI.

**Files:**
- Modify: `src/gic_email_intel/automation/skills/create-quote-id.md` — Step 6 subject format
- Modify: `unisoft-proxy/client/cli.py` — add `_format_task_subject(lob, business_description)` sibling to existing `_truncate_subject`; `task_create` accepts `--business-description`
- Create: `tests/test_task_subject_format.py`

**Step 1: Failing tests.**

```python
def test_format_subject_basic():
    from cli import _format_task_subject
    assert _format_task_subject("CG", "Artisan contractors handyman services") == "CG - Artisan contractors handyman services"


def test_format_subject_truncates_at_50_word_boundary():
    from cli import _format_task_subject
    s = _format_task_subject("CG", "Restaurant food service operations company business")
    assert len(s) <= 50
    assert s.startswith("CG - ")
    # Truncation lands on word boundary (last char before "..." not a partial word)
    base = s.rstrip("...").rstrip()
    assert " " not in base[-1]  # last char of truncated portion isn't a fragment marker


def test_format_subject_empty_description():
    from cli import _format_task_subject
    s = _format_task_subject("CG", "")
    assert s == "CG -"


def test_format_subject_lob_too_long_raises():
    from cli import _format_task_subject
    with pytest.raises(ValueError):
        _format_task_subject("X" * 50, "Y")


def test_task_create_uses_format_subject_when_no_explicit_subject():
    """Integration: task_create with --lob and --business-description and no --subject auto-formats."""
    with patch("cli.get_client") as mock_get:
        client = MagicMock()
        client.set_task.return_value = {"Task": {"TaskId": 1}, "_meta": {}}
        mock_get.return_value = client
        runner.invoke(app, [
            "task", "create",
            "--quote-id", "1", "--agent-no", "1", "--lob", "CG",
            "--business-description", "Artisan contractors",
            "--group-id", "3", "--due-date", "2026-04-30",
        ])
    payload = client.set_task.call_args[0][0]
    assert payload["Subject"].startswith("CG - Artisan")


def test_task_create_explicit_subject_overrides_format():
    with patch("cli.get_client") as mock_get:
        client = MagicMock()
        client.set_task.return_value = {"Task": {"TaskId": 1}, "_meta": {}}
        mock_get.return_value = client
        runner.invoke(app, [
            "task", "create",
            "--quote-id", "1", "--agent-no", "1", "--lob", "CG",
            "--business-description", "Artisan contractors",
            "--subject", "Custom subject",
            "--group-id", "3", "--due-date", "2026-04-30",
        ])
    payload = client.set_task.call_args[0][0]
    assert payload["Subject"] == "Custom subject"
```

**Step 2-5:** Implement, run, pass.

**Step 6:** Update `create-quote-id.md` Step 6 to instruct: pass `--lob` + `--business-description`; let CLI auto-format.

**Step 7: Commit.**

```bash
git add unisoft-proxy/client/cli.py src/gic_email_intel/automation/skills/create-quote-id.md tests/test_task_subject_format.py
git commit -m "feat(unisoft): task subject = '{LOB} - {business description}' (DEVOPS-163)"
git push indemn fix/devops-163
gh pr create ...
```

---

## Sibling PR 2 — Faster claim into "Indemn - Processing" (DEVOPS-164)

Worktree: `../gic-eml-sibling-2` off `indemn/main`. Independent of USLI. **Merge gates on DEVOPS-158 closure** — the cron interval change would invalidate ongoing prod soak observations.

Two changes:

**(a) Tighten cron intervals** in `docker-compose.yml`:

```yaml
sync-cron:
  command: python -m gic_email_intel.cli.main sync run --loop --interval 60     # was 300
processing-cron:
  command: python -m gic_email_intel.agent.harness process --batch --loop --interval 120 --workers 3  # was 300
```

**(b) Claim-on-sync heuristic** in `sync.py`:

**Files:**
- Modify: `docker-compose.yml`
- Modify: `src/gic_email_intel/cli/commands/sync.py`
- Create: `tests/test_sync_claim_on_arrival.py`

**Step 1: Failing tests.**

```python
def test_claim_on_sync_moves_likely_agent_submission():
    e = make_email(from_address="paula@insuranceconnection.org", subject="New Application — Joe's Catering LLC", attachments=[{"filename": "ACORD-125.pdf"}])
    assert _is_likely_agent_submission(e) is True


def test_claim_on_sync_skips_usli():
    e = make_email(from_address="no-reply@usli.com", subject="USLI Retail Web Quote MGL...", attachments=[{"filename": "retailer_copy.pdf"}])
    assert _is_likely_agent_submission(e) is False


def test_claim_on_sync_skips_internal_gic():
    e = make_email(from_address="bind@gicunderwriters.com", subject="Re: Bound", attachments=[])
    assert _is_likely_agent_submission(e) is False


def test_claim_on_sync_skips_replies_in_thread():
    e = make_email(from_address="paula@insuranceconnection.org", subject="Re: Re: Re: previous thread", attachments=[])
    assert _is_likely_agent_submission(e) is False
```

**Step 2-5:** Implement, run, pass, commit.

**[NEEDS USER APPROVAL]** Don't merge until DEVOPS-158 closes.

```bash
git commit -am "feat(automation): tighten sync to 60s, processing to 120s (DEVOPS-164) — DO NOT MERGE during DEVOPS-158 soak"
git commit -am "feat(sync): claim-on-sync heuristic (DEVOPS-164)"
```

---

## Sibling PR 3 — `.eml` export includes attachments inline (DEVOPS-165)

Worktree: `../gic-eml-sibling-3` off `indemn/main`. Independent of USLI. Bug fix.

**Files:**
- Modify: `src/gic_email_intel/cli/commands/emails.py` — replace current `MIMEMultipart("alternative")` with `MIMEMultipart()` + attachment parts; factor `_build_eml`
- Modify: `tests/test_emails_export.py` (or create)

**Step 1:** Identify a real seed email to test against. Query Mongo for an email with multiple attachments + a non-ASCII filename (if possible).

```bash
docker run --rm --network host mongo:6 mongosh "${URI}/gic_email_intelligence" --quiet --eval '
  db.emails.find({attachments: {$exists: true, $not: {$size: 0}}}, {_id:1, "attachments.filename":1}).limit(20)
' | head -40
```

Pick concrete email IDs and document them in the test setup as fixture constants.

**Step 2: Failing tests** — strong assertions.

```python
import email as em
import pytest


def test_export_eml_is_multipart_mixed(tmp_path, real_email_id_with_attachments):
    out = tmp_path / "out.eml"
    runner.invoke(app, ["emails", "export", real_email_id_with_attachments, "--output", str(out)])
    msg = em.message_from_bytes(out.read_bytes())
    assert msg.is_multipart()
    assert msg.get_content_type() == "multipart/mixed"


def test_export_preserves_body_content(tmp_path, real_email_id_with_attachments):
    out = tmp_path / "out.eml"
    runner.invoke(app, ["emails", "export", real_email_id_with_attachments, "--output", str(out)])
    msg = em.message_from_bytes(out.read_bytes())
    body_parts = [p for p in msg.walk() if p.get_content_type() in ("text/plain", "text/html")]
    assert any(len(p.get_payload(decode=True) or b"") > 0 for p in body_parts)


def test_export_preserves_headers(tmp_path, real_email_id_with_attachments):
    out = tmp_path / "out.eml"
    runner.invoke(app, ["emails", "export", real_email_id_with_attachments, "--output", str(out)])
    msg = em.message_from_bytes(out.read_bytes())
    assert msg["From"] is not None
    assert msg["Subject"] is not None
    assert msg["Date"] is not None


def test_export_attachment_count_matches(tmp_path, real_email_id_with_3_attachments):
    out = tmp_path / "out.eml"
    runner.invoke(app, ["emails", "export", real_email_id_with_3_attachments, "--output", str(out)])
    msg = em.message_from_bytes(out.read_bytes())
    attachments = [p for p in msg.walk() if p.get_filename()]
    assert len(attachments) == 3


def test_build_eml_unit():
    """Direct unit test — used by Sibling 4 backfill too."""
    from datetime import datetime
    from gic_email_intel.cli.commands.emails import _build_eml
    eml = _build_eml({
        "from_address": "test@example.com",
        "to_addresses": ["dest@example.com"],
        "subject": "T",
        "received_at": datetime(2026, 4, 29),
        "body_text": "hello",
        "attachments": [{"filename": "a.pdf", "storage_path": "s3://test/a.pdf"}],
    }, _download=lambda path: b"PDF content")
    msg = em.message_from_bytes(eml)
    assert msg.is_multipart()
    assert msg["Subject"] == "T"
    files = [p.get_filename() for p in msg.walk() if p.get_filename()]
    assert files == ["a.pdf"]


def test_build_eml_handles_non_ascii_filenames():
    """RFC 2231 encoding — high-risk with USLI applicant names."""
    from gic_email_intel.cli.commands.emails import _build_eml
    eml = _build_eml({
        "from_address": "x@y", "to_addresses": ["a@b"], "subject": "T", "body_text": "x",
        "received_at": __import__("datetime").datetime.now(),
        "attachments": [{"filename": "Niño_Quote.pdf", "storage_path": "s3://x/y"}],
    }, _download=lambda _: b"\x00")
    msg = em.message_from_bytes(eml)
    files = [p.get_filename() for p in msg.walk() if p.get_filename()]
    assert any("Niño" in f for f in files)
```

**Step 3-5:** Implement `_build_eml` (factor out of `export_email`); `_download` is injectable for testing. Run, pass.

**Step 6: Commit.**

```bash
git add src/gic_email_intel/cli/commands/emails.py tests/test_emails_export.py
git commit -m "fix(emails): export rebuilds .eml with attachments inline (DEVOPS-165)"
git push indemn fix/devops-165
gh pr create ...
```

---

## Sibling PR 4 — Backfill historical .eml uploads — [NEEDS USER APPROVAL]

Worktree: `../gic-eml-sibling-4` off `indemn/main` after Sibling 3 merged.

**Files:**
- Create: `scripts/backfill_eml_uploads.py`

**Step 1: [NEEDS USER APPROVAL]** Confirm scope: target = `agent_submission` automation completions since 2026-04-23 go-live.

**Step 2: Script logic** — **upload-then-verify-then-delete with state checkpointing**:

```python
# Per quote:
# 1. Read state file /tmp/backfill-eml-state.json — skip if already done
# 2. Fetch existing email .eml from Unisoft (GetQuoteAttachments) — find by filename pattern
# 3. Rebuild via _build_eml (Sibling 3)
# 4. UPLOAD new .eml — capture new attachment ID
# 5. VERIFY new .eml present (GetQuoteAttachments) and matches expected size/filename
# 6. ONLY THEN delete old .eml
# 7. Append success to state file
# On any failure step 4-6: leave both files present (manual cleanup), log failure, don't update state
```

`--dry-run` flag (default true). `--start-date YYYY-MM-DD` filter. Batch size 10 with 1s sleep. Per-batch approval.

**Step 3:** Dry-run on prod, review report.

**Step 4: [NEEDS USER APPROVAL]** Run live, batch by batch.

**Step 5: Commit.**

```bash
git add scripts/backfill_eml_uploads.py
git commit -m "feat(scripts): backfill_eml_uploads — upload-verify-delete with checkpointing (DEVOPS-165)"
```

---

## Sequencing Summary

```
This week (overlapping with prod soak):
  Phase A  [setup, conftest shim, fixtures dir]
  Phase B  [verification, read-only — outputs to tests/fixtures/usli_config.json]
  Phase B-exit [hard gate before Phase C]
  Sibling 1 (DEVOPS-163) — small PR, ship anytime
  Sibling 3 (DEVOPS-165) — small PR, ship anytime

Then:
  Phase C, D, E [USLI feature build, on feature branch]
  Phase G [UAT soak, JC sign-off, numerical thresholds]
  Sibling 4 (after Sibling 3 merged) [backfill]

After DEVOPS-158 closes (~2026-05-06):
  Sibling 2 (DEVOPS-164) — was held back during soak; ship now
  Phase H [prod rollout, gated by G thresholds + Datadog alerts firing]

Post-launch:
  Phase K [follow-ups]
```
