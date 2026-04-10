---
ask: "How does the OS entity system work — the generator, building blocks, skills as docs, and build vs. buy decision?"
created: 2026-03-30
workstream: product-vision
session: 2026-03-30-a
sources:
  - type: conversation
    description: "Craig and Claude working through the architecture, 2026-03-30"
  - type: research
    description: "Open source CRM/ERP/AMS framework landscape research"
---

# Entity System and Generator

## The Core Concept

The OS is composed of building blocks. Every building block (entity) is exposed through API and CLI. A generator creates the full stack from a declarative entity definition. A skill is auto-generated as both the AI interface and developer documentation.

## Build vs. Buy Decision

### Research Findings
- **No open source AMS exists.** The insurance-specific domain model must be built from scratch. This is also a market opportunity — nobody has built the AI-native insurance management system.
- **Open source CRM frameworks** (Twenty CRM, ERPNext/Frappe, Odoo) provide generic CRM capabilities (contacts, orgs, pipeline, tasks) with auto-generated APIs.
- **The valuable pattern** from these frameworks isn't the framework itself — it's the concept of "define an entity declaratively → auto-generate everything."

### Decision: Build from Scratch with the Generator Pattern
- Build the domain model from scratch on Postgres — full control, CLI-native from day one
- Build the entity-to-API-to-CLI generator as a core OS capability
- Don't adopt a CRM/ERP framework — the insurance domain is too specialized, the CLI-first requirement demands full control, and the UI layer isn't a priority
- Use existing libraries and managed services for infrastructure (Amplify, Pinecone, Stripe, Twilio)
- The generator IS the framework — purpose-built for insurance, agent-accessible, CLI-first

### What the Team Already Has (Don't Rebuild)
- Workflow engine — building as part of the vision
- Chat infrastructure — exists (middleware-socket-service)
- Voice infrastructure — exists (voice-service, LiveKit)
- Email infrastructure — building (GIC email intelligence pattern)
- RAG/knowledge/search — exists (Pinecone)
- Payment processing — exists (Stripe)
- Evaluation framework — exists (rubrics, test sets)
- CLI and MCP server — exists (Indemn CLI)

### Specific Open Source Components Worth Considering
| Component | What | When |
|-----------|------|------|
| Paperless-ngx | Document OCR, classification, search | When document management pipeline is needed |
| Lago | Usage-based billing/metering | When Tier 3 API pricing is designed |
| Payload CMS | Headless CMS for content/KB management | When product catalog or KB needs content management |

## The Generator

### Input: Entity Definition (Declarative)

```yaml
name: Policy
sub_domain: policy-lifecycle
description: "The insurance contract. The single most important entity in the domain."

fields:
  policy_number:
    type: string
    unique: true
    generated: true
    pattern: "POL-{sequence}"
  effective_date:
    type: date
    required: true
  expiration_date:
    type: date
    required: true
  written_premium:
    type: currency
  status:
    type: enum
    values: [issued, active, endorsed, renewed, cancelled, expired]
    default: issued

state_machine:
  issued:
    transitions: [active]
  active:
    transitions: [endorsed, renewed, cancelled, expired]
  endorsed:
    transitions: [active]  # returns to active after endorsement applied
  renewed:
    terminal: false
    note: "Creates new PolicyTerm"
  cancelled:
    terminal: true
  expired:
    terminal: true

relationships:
  belongs_to:
    - entity: Insured
      required: true
    - entity: Carrier
      required: true
    - entity: Product
      required: true
  has_many:
    - entity: PolicyTransaction
    - entity: Coverage
      note: "Instances materialized from Product coverage templates"
    - entity: PolicyTerm

aggregate_children:
  - PolicyTransaction
  - Coverage
  - PolicyTerm

permissions:
  read: [agent, underwriter, admin, associate]
  create: [underwriter, admin, associate]
  update: [underwriter, admin, associate]
  transition: [underwriter, admin, associate]
  delete: [admin]

events:
  - policy.created
  - policy.updated
  - policy.status_changed
  - policy.coverage_added
  - policy.coverage_removed
```

### Output: The Generator Produces

**1. Database Schema**
- Postgres table with all fields, types, constraints
- Indexes on common query patterns (status, carrier, insured, dates)
- Migration files for schema evolution

**2. REST API**
- `GET /api/policies` — list with filtering, pagination, sorting
- `GET /api/policies/:id` — get by ID with optional includes
- `POST /api/policies` — create
- `PUT /api/policies/:id` — update
- `POST /api/policies/:id/transition` — state machine transition
- `GET /api/policies/:id/transactions` — aggregate children
- `GET /api/policies/:id/coverages` — aggregate children
- Validation, error handling, auth middleware

**3. CLI Commands**
```bash
indemn policy list [--status active] [--carrier CARR-001] [--insured INS-001] [--limit 20]
indemn policy get POL-001 [--include insured,coverages,transactions]
indemn policy create --product PROD-001 --insured INS-001 --carrier CARR-001 --effective 2026-04-01
indemn policy update POL-001 --written-premium 5000
indemn policy transition POL-001 --to endorsed --reason "Coverage limit increase"
indemn policy transactions POL-001
indemn policy coverages POL-001
```

**4. Skill Document** (the dual-purpose artifact)
```markdown
# Policy

The insurance contract — the single most important entity in the domain.
Everything upstream (submissions, quotes) leads here.
Everything downstream (endorsements, renewals, claims) flows from here.

## Quick Reference

| Command | Description |
|---------|-------------|
| `indemn policy list` | List policies with filters |
| `indemn policy get <id>` | Get policy details |
| `indemn policy create` | Create a new policy |
| `indemn policy update <id>` | Update policy fields |
| `indemn policy transition <id>` | Change policy status |

## Lifecycle

issued → active → endorsed → renewed → cancelled/expired

## Common Operations

### Find all active policies for a carrier
indemn policy list --status active --carrier CARR-001

### Get a policy with its coverages and insured details
indemn policy get POL-001 --include insured,coverages

### Endorse a policy (add coverage)
indemn policy transition POL-001 --to endorsed --reason "Added umbrella coverage"
indemn coverage create --policy POL-001 --type umbrella --limit 1000000

### Check policies expiring this month
indemn policy list --expiring-before 2026-04-30 --status active

## Relationships

- **Insured**: `indemn policy get POL-001 --include insured`
- **Carrier**: `indemn policy get POL-001 --include carrier`
- **Product**: the product definition this policy was issued from
- **Coverages**: `indemn policy coverages POL-001`
- **Transactions**: `indemn policy transactions POL-001` (endorsements, renewals, cancellations)

## Events

Subscribe to policy events for workflow automation:
- `policy.created` — new policy issued
- `policy.status_changed` — status transition occurred
- `policy.coverage_added` — new coverage added to policy
- `policy.updated` — any field changed

## Permissions

| Role | Read | Create | Update | Transition |
|------|------|--------|--------|-----------|
| Agent | Yes | No | No | No |
| Underwriter | Yes | Yes | Yes | Yes |
| Admin | Yes | Yes | Yes | Yes |
| Associate | Yes | Yes | Yes | Yes |
```

**5. Webhook Events**
- Event bus integration for each defined event
- Associates and external systems can subscribe to entity events
- Events drive workflow execution

**6. Permissions Model**
- Role-based access control auto-generated from the definition
- Enforced at both API and CLI level
- Associates get permissions based on their configuration

## Why the Generator Is the Most Important Thing to Build

1. **It's how you build 44 entities in a week.** Build the generator first. Then each entity is a declaration, not an implementation. The generator produces the full stack.

2. **It's how Tier 3 works.** A developer defines a new entity → the generator produces API + CLI + skill + events + permissions. Their entity is immediately usable by associates and documented for other developers.

3. **It's self-documenting.** Every entity auto-generates its own skill/documentation. The platform documents itself as it grows. No separate documentation effort.

4. **It's how associates learn.** When an associate needs to interact with a Policy, it reads the Policy skill. The skill is generated from the entity definition. Always up to date. Always accurate.

5. **It enforces consistency.** Every entity follows the same patterns — same API structure, same CLI conventions, same event model, same permissions model. No drift between entities.

6. **It's the OS kernel.** The generator is to the Indemn OS what the kernel is to Linux. Everything else is built on top of it.

## Skills as Documentation

The auto-generated skill serves three audiences simultaneously:

| Audience | How They Use It |
|----------|----------------|
| **AI Associates** | Read the skill to know what CLI commands to call, what parameters to pass, what the entity lifecycle looks like |
| **Tier 3 Developers** | Read the skill as API/CLI reference documentation for building on the platform |
| **Indemn Engineers** | Read the skill to understand entity behavior, relationships, and operations |

This is the Claude Code pattern applied to the entire platform. In Craig's OS, skills describe how to use tools (Slack, Postgres, GitHub). In the Indemn OS, skills describe how to use entities (Policy, Submission, Quote). Same pattern, different scale.

## Connection to the OS Vision

The generator is what makes these claims true:
- **"Any insurance solution can be built on the OS"** — because any entity can be defined and the generator produces everything
- **"Implementation is trivially fast"** — because entities are declarations, not implementations
- **"Tier 3 developers can build their own products"** — because the generator gives them the same power Indemn has
- **"The platform documents itself"** — because skills are auto-generated
- **"Associates can interact with any entity"** — because every entity has a skill that teaches the associate how to use it

## CRM / AMS Implications

The OS with its entity generator IS the CRM and AMS:
- Contact/Party, Organization, Interaction, Task entities = CRM capabilities
- Policy, Submission, Quote, Coverage, Carrier entities = AMS capabilities
- The generator means both sets of entities are first-class citizens with full API + CLI + skills

For Kyle's internal CRM need: the first "customer" of the OS is Indemn itself. The team uses the same Contact/Party, Organization, and Interaction entities to manage their own customer relationships. Dog-fooding from day one.

For customer AMS replacement: the OS provides everything an AMS does (client management, policy management, carrier management, document management) PLUS the AI associate layer. Customers can use the OS as their primary system or integrate it with their existing AMS as a bridge.
