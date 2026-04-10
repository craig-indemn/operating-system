---
ask: "What is the OS's data architecture? Where does everything live? How are entity definitions, skills, rules, files, and configuration stored, versioned, and managed?"
created: 2026-04-09
workstream: product-vision
session: 2026-04-08-a
sources:
  - type: conversation
    description: "Craig and Claude resolving the fundamental question: everything is data, managed through CLI, versioned by the OS"
  - type: artifact
    description: "2026-04-09-architecture-ironing-round-3.md"
---

# Data Architecture: Everything Is Data

## The Fundamental Decision

Everything in the OS — entity definitions, skills, rules, lookups, associate configurations, role configurations — is data stored in the database. Not files in a git repo. Data.

The OS codebase (git) is the PLATFORM. The database is the APPLICATION. You deploy the platform once. Everything else is data managed through the CLI.

## The Clean Split

### OS Codebase (Git) — The Platform
- The kernel (entity framework, condition evaluator, queue processor, Temporal integration)
- Kernel capabilities (reusable entity methods — auto-classify, fuzzy-search, etc.)
- CLI implementation
- API implementation
- UI implementation
- Deployed once. Updated via platform releases. This is the INFRASTRUCTURE.

### MongoDB — All Configuration and Business Data

**Per-org configuration (the APPLICATION):**
- Entity definitions (schema, state machine, relationships, computed fields, activated capabilities)
- Skills (markdown content — entity skills and associate skills)
- Rules (conditions + actions, per entity type)
- Lookups (mapping tables)
- Role configurations (permissions, watches)
- Associate configurations (role, skills, mode, trigger)
- Capability activations (which capabilities are enabled on which entities)

**Per-org business data:**
- Entity instances (the actual data — submissions, emails, policies, etc.)
- Message queue (pending work items)
- Message log (completed work items)
- Changes collection (version history for ALL of the above)

**Kernel data (cross-org):**
- Organization definitions (bootstrap entities)
- Actor definitions (bootstrap entities)
- Role definitions (bootstrap entities)

### S3 (Object Storage) — Unstructured Files
- PDFs, images, attachments, generated documents
- Scoped by org_id in path
- Referenced by entity fields in MongoDB
- Managed via CLI: `indemn file upload`, `indemn file download`

### Temporal Cloud — Execution
- Associate execution (durable workflows)
- Deployment orchestration (saga-compensated deployments)
- Scheduled tasks (multi-step)
- No application data stored — Temporal holds execution state only

### OTEL Backend (Jaeger/Grafana Tempo) — Observability
- Execution traces (spans for entity changes, rule evaluations, LLM calls, Temporal workflows)
- Performance monitoring
- Ephemeral (days-weeks retention)
- Linked to permanent records via correlation_id/trace_id

## Entity Definitions as Data

Entity definitions are no longer Python class files on disk. They are stored in MongoDB. The entity framework creates Python classes dynamically at runtime from stored definitions.

### Creating an entity
```bash
indemn entity create Submission \
  --fields '{"named_insured": "str", "stage": "str", "line_of_business": "str", "operating_mode": "str", "intake_channel": "str"}' \
  --state-machine '{"received": ["triaging"], "triaging": ["awaiting_agent_info", "awaiting_carrier_action", "processing"], "awaiting_agent_info": ["processing"], "awaiting_carrier_action": ["processing"], "processing": ["quoted", "declined"], "quoted": ["closed"], "declined": ["closed"]}' \
  --computed-field '{"ball_holder": {"map_from": "stage", "mapping": {"received": "queue", "triaging": "gic", "awaiting_agent_info": "agent", "awaiting_carrier_action": "carrier", "processing": "gic", "quoted": "agent", "declined": "gic", "closed": "done"}}}'
```

This writes a definition to MongoDB. The entity framework:
1. Reads the definition
2. Creates a Beanie Document subclass dynamically (using Pydantic's `create_model` + dynamic class creation)
3. Registers CLI commands (`indemn submission list`, `get`, `create`, `update`, `transition`)
4. Registers API routes (`GET /api/submissions`, `POST /api/submissions`, etc.)
5. Generates the entity skill (markdown documentation)

No Python file written. No git commit. No restart needed. The definition is data. The framework interprets it.

### Modifying an entity
```bash
indemn entity modify Submission --add-field '{"priority": "str"}'
indemn entity modify Submission --remove-field priority
indemn entity modify Submission --add-state '{"on_hold": {"transitions_from": ["processing"], "transitions_to": ["processing"]}}'
```

Changes take effect immediately (or after a hot-reload signal). The changes collection records every modification with before/after values. Existing MongoDB documents are handled gracefully — new fields have defaults, removed fields are ignored.

### Activating capabilities on entities
```bash
indemn entity enable Submission auto-classify --evaluates classification-rule --sets-field classification
indemn entity enable Submission fuzzy-search --on-field named_insured --threshold 85
indemn entity enable Submission stale-check --when '{"field": "last_activity_at", "op": "older_than", "value": "7d"}'
```

Capability activations are stored as part of the entity definition in MongoDB. The kernel capability code (in the platform codebase) is invoked when the entity method is called. The activation is data. The capability is code.

## Skills as Data

Skills are stored in MongoDB, not as markdown files on disk.

### Creating and updating skills
```bash
# Create from a file (reads the file, stores content in MongoDB)
indemn skill create email-classification --content-from-file ./email-classification.md

# Update
indemn skill update email-classification --content-from-file ./email-classification-v2.md

# View
indemn skill get email-classification

# List all skills for an org
indemn skill list --org gic
```

The skill content lives in MongoDB. Associates load skills at runtime from the database. Changes take effect immediately. The changes collection records every update with before/after content.

### Auto-generated entity skills
When an entity definition is created or modified, the framework automatically generates/regenerates the entity skill and stores it in MongoDB. The entity skill documents all CLI commands, fields, state machine, relationships, and activated capabilities for that entity.

### Associate skills
Created by developers/FDEs. Describe behavioral instructions for how an associate should process work. Reference entity skills for what operations are available.

Both types are stored the same way (MongoDB documents). Both are loaded the same way (into agent context). Both are versioned the same way (changes collection).

## Rules, Lookups, and Configuration as Data

All created and managed via CLI. All stored in MongoDB. All versioned by the changes collection.

```bash
# Rules
indemn rule create --entity Email --org gic \
  --when '{"all": [{"field": "from_address", "op": "ends_with", "value": "@usli.com"}]}' \
  --action set-fields --sets '{"type": "usli_quote"}'

# Lookups
indemn lookup create --org gic --name usli-prefix-lob \
  --data '{"MGL": "general_liability", "XPL": "excess_personal_liability", "MSE": "special_events"}'

# Watches (on roles)
indemn role add-watch underwriter --entity Assessment --on created \
  --when '{"field": "needs_review", "op": "equals", "value": true}'

# Associate configuration
indemn associate create --name "Email Classifier" --role classifier \
  --skills '["email-classification"]' --mode hybrid
```

## Unstructured Files

PDFs, images, attachments, and generated documents live in S3 with entity references in MongoDB.

```bash
# Upload and link to an entity
indemn file upload ./acord-form.pdf --entity email/EMAIL-001 --field attachments

# The entity stores a reference:
# {attachments: [{name: "acord-form.pdf", storage: "s3://indemn-files/gic/EMAIL-001/acord-form.pdf", size: 245000, uploaded_at: "..."}]}

# Download
indemn file download email/EMAIL-001 --attachment acord-form.pdf

# List files for an entity
indemn file list --entity email/EMAIL-001
```

Files are scoped by org (S3 path includes org_id). The entity framework manages the reference. The CLI handles upload/download. S3 handles storage and durability.

## Built-In Version Control

The OS is its own version control system for application configuration. The changes collection records every modification to every configuration object.

### History
```bash
# All recent changes for an org
indemn history --org gic --last 20

# History of a specific object
indemn history --org gic --entity-def Submission
indemn history --org gic --skill email-classification
indemn history --org gic --rule RULE-047

# History of all changes by a specific actor
indemn history --org gic --by jc@gicunderwriters.com
```

### Diffing
```bash
# Diff between two orgs (staging vs. production)
indemn org diff gic-staging gic

# Diff between a point in time and now
indemn org diff gic --since "2026-04-09 14:00"
```

### Rollback
```bash
# Roll back a specific change
indemn rollback --org gic --change CHANGE-047

# Roll back to a point in time
indemn rollback --org gic --to "2026-04-09 14:00"
# Shows preview of what would be rolled back. Requires confirmation.
```

### Export and Import
```bash
# Export org configuration as YAML (for backup, review, migration)
indemn org export gic > gic-config.yaml

# Import configuration into a new org
indemn org import --from-file gic-config.yaml --to gic-new
```

## Environments = Orgs

Dev, staging, and prod are just different organizations with the same or similar configuration.

```bash
# Create staging from production
indemn org clone gic --as gic-staging
# Copies: entity definitions, skills, rules, lookups, watches,
#         associate configs, role configs.
# Does NOT copy: entity instances (business data), message queue/log.

# Work in staging
indemn rule create --org gic-staging --entity Email --when '...' --then '...'
indemn skill update --org gic-staging email-classification --content-from-file ./v2.md

# Review changes
indemn org diff gic-staging gic

# Test
indemn rule test --org gic-staging --entity Email \
  --against '{"from_address": "quotes@newcarrier.com"}' --dry-run

# Promote to production (Temporal deployment workflow)
indemn deploy --from-org gic-staging --to-org gic
# Validates → applies → verifies → rolls back on failure

# Roll back the deployment
indemn deploy rollback DEPLOY-003
```

## What This Enables

**Multi-tenant by default.** Every org has its own entity definitions, skills, rules, configurations. Org cloning makes spinning up new tenants trivial.

**Environments as first-class.** Dev, staging, prod are just orgs. Promoting changes is a deployment command. Rolling back is a CLI command.

**Everything CLI-managed.** No git repos per tenant. No file editing. No restarts. An FDE, a Tier 3 developer, or an associate can set up and manage an entire system through the CLI.

**Versioned by default.** Every change is recorded. Every change is rollbackable. History is queryable. Diffs are available. Exports provide snapshots.

**Associates can build systems.** An associate can: create entity definitions, create rules, create skills, configure other associates, deploy changes — all through CLI commands. Agents building agents on a fully data-driven platform.

## The Complete Infrastructure Stack

```
┌─────────────────────────────────────────────┐
│ OS Codebase (git)                            │
│ Platform code: kernel, capabilities, CLI,    │
│ API, UI. Deployed once per release.          │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ MongoDB  │ │ S3       │ │ Temporal │
│          │ │          │ │ Cloud    │
│ Config:  │ │ Files:   │ │          │
│ entities │ │ PDFs     │ │ Assoc.   │
│ skills   │ │ images   │ │ execution│
│ rules    │ │ docs     │ │ deploy   │
│ roles    │ │ attach.  │ │ schedule │
│ assoc.   │ │          │ │          │
│          │ │ Ref'd by │ │          │
│ Data:    │ │ MongoDB  │ │          │
│ entities │ │ entities │ │          │
│ queue    │ │          │ │          │
│ log      │ │          │ │          │
│ changes  │ │          │ │          │
└──────────┘ └──────────┘ └──────────┘
                              │
                    ┌─────────┘
                    ▼
             ┌──────────┐
             │ OTEL     │
             │ Backend  │
             │          │
             │ Traces   │
             │ Metrics  │
             │ Spans    │
             └──────────┘
```
