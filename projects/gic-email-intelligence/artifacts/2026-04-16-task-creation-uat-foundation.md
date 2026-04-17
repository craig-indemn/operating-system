---
ask: "Document what we built and discovered getting Unisoft task creation working end-to-end in UAT"
created: 2026-04-16
workstream: gic-email-intelligence
session: 2026-04-16a
sources:
  - type: codebase
    description: "UniProxy.cs on EC2 i-0dc2563c9bc92aa0e — two patches applied"
  - type: unisoft-uat
    description: "Test calls via proxy against Unisoft UAT (services.uat.gicunderwriters / ins-gic-service-uat-app)"
  - type: wsdl
    description: "research/unisoft-api/wsdl-complete.md — TaskDTO, TaskAssociationDTO, TaskPersistRequest"
---

# Task Creation — UAT Foundation

## What Works End-to-End

A task can now be created in Unisoft UAT, assigned to a group, and linked to a Quote ID, via our SOAP proxy.

**Verified task:** `TaskId 16853` against `QuoteId 17273` (Talavera Trucking / USA General Insurance / CG).

## Proxy Changes (C:\unisoft\UniProxy.cs on EC2 i-0dc2563c9bc92aa0e)

Two patches applied in sequence. Both backed up (`.bak-2026-04-16`, `.bak2-2026-04-16`).

### Patch 1 — Task DTOs registered in `dtoNamespaces`

Added 4 entries:
```
"Task"            → ...DTO.Tasks
"TaskAssociation" → ...DTO.Tasks
"TaskGroup"       → ...DTO.Tasks
"TaskAction"      → ...DTO.Tasks
```

Pattern matches the existing Criteria/Quote/Submission/Activity entries.

### Patch 2 — `AppendDtoField` now recurses into nested sub-DTOs

**Old behavior (bug):** any nested Dictionary inside a parent DTO was emitted as `<b:Key i:nil="true"/>` — data silently discarded.

**New behavior:** nested Dictionaries with content are recursively serialized with the `b:` prefix, maintaining alphabetical field order per WCF requirements. Empty dicts still emit nil (sub-DTO not provided).

This unlocked `TaskAssociation` as a nested sub-DTO of `Task`. It may also fix future nested cases — e.g., `ActivityReview` inside `Activity`.

## Unisoft UAT State

### Custom Task Action (created today)

| ActionId | Description | SectionId |
|----------|-------------|-----------|
| 40 | Review automated submission | 5 (Quotes) |

Created via `SetTaskAction` with `AssignedWorkDays: 1`. Visible to all users in the quote section. Purpose: distinguish tasks produced by our automation from manually-created ones.

### Custom Task Group (created today)

| GroupId | Title | IsActive |
|---------|-------|----------|
| 2 | Indemn Automation - New Biz | true |

Created via `SetTaskGroup`. Empty user list — we'll add ccerto or other testers if needed.

**Note:** GroupId 1 already existed as "test" before our work.

## Task Creation Pattern (reference payload)

```json
POST /api/soap/SetTask
{
  "Action": "Insert",
  "Task": {
    "ActionId": 40,
    "AssignedToUser": "",
    "DueDate": "2026-04-17T14:33:28",
    "EnteredByUser": "ccerto",
    "GroupId": 2,
    "PriorityId": 1,
    "SectionId": 5,
    "StatusId": 1,
    "Subject": "[Auto] {insured} — {LOB} via {agency}",
    "TaskAssociation": {
      "AgentNo": 5736,
      "LOB": "CG",
      "QuoteId": 17273
    },
    "TaskId": 0
  }
}
```

## Hard Constraints Discovered

1. **Subject max length: 50 characters.** Longer subjects get silently truncated by Unisoft. Plan truncation logic in the CLI/skill — e.g., truncate insured name first, then agency.
2. **Group assignment requires `AssignedToUser: ""` (empty string) AND `GroupId: <N>`.** If AssignedToUser is set to a username, the task is assigned to that user individually, not the group.
3. **WCF field order: alphabetical, case-sensitive (`StringComparer.Ordinal`).** Proxy handles this for parent DTOs and now nested sub-DTOs. CLI callers don't need to worry about ordering in their JSON input.
4. **Section 5 = Quotes.** For new-biz tasks linked to a QuoteId, always use SectionId 5. Section 2 exists with a "New Business" action but it's a different UI area.

## Validated Operations (all against UAT)

| Operation | Status | Notes |
|-----------|--------|-------|
| `GetTaskActions` | Works | Returns 40 actions (39 pre-existing + our ActionId 40) |
| `GetTaskGroups` | Works | Returns 2 groups (test + our Indemn Automation - New Biz) |
| `SetTaskAction` | Works | Created ActionId 40 |
| `SetTaskGroup` | Works | Created GroupId 2 |
| `SetTask` | Works | TaskIds 16851, 16852, 16853 created. 16853 has full association. |
| `GetTask` | Works | Fetches task back with all fields |

## What's Next

- Add `unisoft task` CLI subcommands: `create`, `list`, `get`, `groups list`, `actions list`
- Add `unisoft_client` methods: `set_task()`, `get_task()`, `get_task_groups()`, `get_task_actions()`
- Update automation skill `create-quote-id.md` Step 6: add task creation with LOB→Group routing (currently all LOBs → GroupId 2 in UAT; in prod we'll have New Biz + New Biz Workers Comp)
- Subject truncation helper: "[Auto] {insured (truncated)} — {LOB}" fitting 50 chars

## Test Tasks Created (safe to delete in UAT if needed)

- TaskId 16851 — "[TEST] Indemn SetTask transport test — safe to del" — QuoteId NOT associated (pre-fix)
- TaskId 16852 — "[TEST] Nested DTO fix verify" — QuoteId 17273 associated (post-fix 1st try)
- TaskId 16853 — "[Auto] Talavera Trucking — CG via USA Gen" — full end-to-end test, GroupId 2, ActionId 40
