---
ask: "What is the implementation plan — what gets built, in what order, with what dependencies?"
created: 2026-04-02
workstream: product-vision
session: 2026-03-30-a
sources:
  - type: conversation
    description: "Craig and Claude implementation planning session, 2026-04-02"
---

# Implementation Plan

## The Arc

Craig's personal OS → Indemn's company OS → Customer's insurance OS.

Same framework at every scale. The company literally operates through the system it sells. Dog-fooding goes all the way down — not just "we use our CRM" but the development framework, team communication, project management, customer relationships, internal workflows — all on the OS.

## Implementation Phases

### Phase 0 — The Development Framework

**The OS for building the OS.** Before writing any entity code, establish the framework for how the system is developed and maintained. Every Claude Code session that works on this project needs the same conventions, the same patterns, the same skills.

**Deliverables:**
- Repository structure following the modular monolith design (core/, domains/, api/, cli/, skills/)
- CLAUDE.md for the OS codebase — what any session needs to know before touching anything
- Development skills:
  - "How to add a new entity" — create class, define fields, add domain methods, @exposed, register
  - "How to add a service" — create service class, add @exposed methods
  - "How to add an integration adapter" — implement interface, register
  - "How to test" — testing patterns, test structure, how to run
  - "How to deploy" — deployment process (AWS Amplify serverless)
- Coding conventions — naming, file organization, patterns to follow
- Git workflow — branching, commits, code review process for AI sessions
- Dependency management — pyproject.toml, package structure

**Why first:** 10+ parallel Claude Code sessions building entities need to follow identical patterns. Without this, you get 10 different approaches that don't fit together.

### Phase 1 — Core Framework

**The kernel.** Base Entity class and everything it provides.

**Deliverables:**
- Base Entity class extending Beanie Document
  - StateMachineMixin — lifecycle enforcement, transition validation, event emission on transition
  - EventMixin — domain event publishing to RabbitMQ
  - PermissionsMixin — role-based access checks, enforced at entity layer
  - AutoRegisterMixin — discovers entities, registers API routes + CLI commands + generates skills
- @exposed decorator — marks methods for API/CLI exposure
- Relationship handling — Beanie Link/BackLink patterns with lazy loading
- FlexibleData field — product-specific data validated against form_schema
- Multi-tenancy — org_id scoping on every query, enforced at base class
- FastAPI auto-registration — generic CRUD routes + @exposed method routes
- Typer CLI auto-registration — generic CRUD commands + @exposed method commands
- Skill auto-generation — produce SKILL.md from entity class introspection
- RabbitMQ event bus connection
- Auth middleware — JWT for users, service tokens for associates, API keys for Tier 3
- One working entity (Organization) proving the full stack end-to-end

**Dependency:** Phase 0 (conventions established)
**Proof point:** `indemn org create --name "Test"` works. API endpoint returns data. Skill file is auto-generated. Event fires on creation.

### Phase 2 — Complete Entity Vertical

**ALL Phase 1 domain entities, built in parallel.** The system comes up whole, not in pieces.

**Parallel sessions by sub-domain:**

| Session | Sub-Domain | Entities | Services |
|---------|-----------|----------|----------|
| A | Core Insurance | Product, PolicyForm | ProductService |
| B | Risk & Parties | Contact, Insured, Carrier, RetailAgent, Agency, DistributionPartner | PartyService |
| C | Submission & Quoting | Submission, Quote + children (SubmissionLine, SubmissionRequirement) | IntakeService, QuotingService |
| D | Policy Lifecycle | Policy, Certificate, Binder + children (PolicyTransaction, Coverage) | BindingService, RenewalService |
| E | Financial | Payment, Invoice, CommissionSchedule, CommissionTransaction | BillingService, CommissionService |
| F | Distribution & Delivery | Program, Deployment, CarrierAgreement | DeploymentService |
| G | Platform — Agents | Associate, Skill (entity), Workflow, KnowledgeBase | AssociateService |
| H | Platform — Operations | Organization (extend), Task, Template, Interaction, Correspondence, Document, Email, Draft | — |
| I | Reference Tables | LineOfBusiness, ClassCode, Channel, Rule, PaymentPlanTemplate | Seed data scripts |

**Each session delivers:**
- Entity classes with Pydantic fields, state machines, permissions, relationships
- Domain behavior methods (@exposed where applicable)
- Service classes for cross-entity operations
- Auto-generated: API routes, CLI commands, skills (from framework)

**Dependency:** Phase 1 (core framework working)
**Proof point:** `indemn policy list`, `indemn submission create`, `indemn carrier get` all work. Skills exist for every entity. Full API available.

### Phase 3 — Associate Runtime + Integration Adapters

**Deep agents connected to the OS CLI. External systems connected via adapters.**

**Associate Runtime:**
- Deep agent creation with OS CLI in sandbox
- Skill loading from auto-generated entity skills + workflow skills
- Trigger system: event-driven (RabbitMQ subscription), scheduled (cron), always-on (WebSocket/voice), API
- Sandbox provisioning (Daytona evaluation or local Docker)
- LangSmith evaluation framework connected for associate testing

**Integration Adapters:**
- Email: Outlook (Microsoft Graph API), Gmail
- Voice: Twilio, LiveKit (wrap existing voice-service)
- SMS: Twilio
- Chat: WebSocket (wrap existing middleware-socket-service)
- Payment: Stripe (wrap existing integration)
- AMS: adapter interface defined, first implementation (GIC's AMS — informed by Craig's current prototype)
- Carrier APIs: adapter interface defined, first implementations
- Document generation: Mint wrapped as entity operations

**Each adapter delivers:**
- Adapter class implementing the operation interface
- Mapping functions (external format ↔ OS entity format)
- Integration entity configuration (CLI-creatable)
- Integration test

**Dependency:** Phase 1 (core framework) + Phase 2 (entities exist for adapters to map to)
**Proof point:** `indemn email fetch-new --integration INT-001` pulls real emails. `indemn submission submit-to-carrier SUB-001` sends to a real carrier.

### Phase 4 — Indemn Runs on the OS

**The company operates through the system it sells.** Total dog-fooding.

**Customer Management:**
- Indemn's customers modeled as Organizations with Contacts
- Every interaction tracked (meetings, calls, emails, Slack messages)
- Tasks and follow-ups managed through the OS
- Customer health scoring, renewal tracking, expansion opportunities
- Connected to: email (team inboxes), Slack, calendar/meetings, pipeline data

**Team Communication:**
- How the team communicates with each other — tracked and organized
- Meeting intelligence integrated (Kyle's existing meetings database → OS entities)
- Slack integration (conversations flow into Interactions)

**Development Workflow:**
- How the OS itself is developed — managed through the OS
- Linear integration for engineering work
- GitHub integration for code
- Sessions and dispatch connected

**Associates for the Indemn Team:**
- Customer follow-up associate — monitors interactions, flags overdue follow-ups
- Meeting prep associate — gathers context before customer calls
- Weekly summary associate — compiles intelligence across all systems

**Auto-Generated Admin UI:**
- Entity list views, detail views, state machine visualization
- The team uses this alongside CLI + Claude Code
- Real-time updates via WebSocket

**Dependency:** Phase 2 (entities) + Phase 3 (integrations + associates)
**Proof point:** The Indemn team manages customer relationships, tracks communications, and uses associates for daily work — all on the OS. Kyle gets his CRM.

### Phase 5 — First External Customer

**With the system proven by internal use, put a customer on it.**

- Insurance-specific entities already built (Phase 2)
- Integration adapters already working (Phase 3)
- Workflow entity configured for customer's specific needs
- Associates configured with customer-specific skills
- Experience layer (admin UI + configurable views)
- Customer onboarding is configuration, not construction

**The candidate:** Potentially a new customer (not disrupting existing), or a specific workflow for an existing customer (like GIC's AMS automation migrating over).

**Dependency:** Phase 4 (system proven by internal use)
**Proof point:** A real insurance workflow running entirely on the OS. This is the Series A proof.

## Timeline Estimates

| Phase | Duration | Parallel Sessions | Notes |
|-------|----------|-------------------|-------|
| Phase 0 | 1-2 days | 1 (Craig) | Foundational — sets up everything |
| Phase 1 | 3-5 days | 1-2 | Critical path — framework must work before entities |
| Phase 2 | 3-5 days | 9 parallel | All sub-domains simultaneously |
| Phase 3 | 3-5 days | 5-6 parallel | Associate runtime + adapters in parallel |
| Phase 4 | 1-2 weeks | Multiple | Integrations, data migration, team onboarding |
| Phase 5 | 1-2 weeks | Multiple | First customer configuration + testing |
| **Total** | **~4-6 weeks** | | Foundation through first customer |

These estimates assume Craig + Claude Code parallel sessions (10+). The framework enables rapid development — each entity is a Python class following established patterns.

## What's NOT in the Initial Build

- Phase 2 and Phase 3 domain entities (middle market, carrier-grade) — built when needed
- Customer-facing UI beyond auto-generated admin — Ryan's wireframes built when needed
- Temporal workflow engine — custom runner for MVP, Temporal when scale demands
- Full competitive integration library — adapters built per customer need
- Mobile — not in scope
- Analytics/reporting beyond what entities provide — built when needed

## How Knowledge Is Maintained

The system documents itself:
- **Entity skills** — auto-generated, always current
- **CLAUDE.md** — updated as architecture evolves
- **Development skills** — how to work on the system
- **Convention docs** — patterns to follow
- **Git history** — decisions captured in commits

Any new Claude Code session can onboard by reading the CLAUDE.md and development skills. Any new team member can understand the system through the auto-generated skills. The system doesn't just run itself — it explains itself.

## The Series A Proof

"We built the operating system for insurance. We run our own company on it. Here's a customer running on it. Every entity has an API, a CLI, and a skill. Associates operate through the CLI. Integrations connect any external system. The whole thing was built in weeks by one architect with AI."

"Give us $10M and we put 50 companies on it."
