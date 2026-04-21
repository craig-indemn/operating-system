---
ask: "Capture domain model thinking for the customer system — entity criteria, entity candidates, and design principles"
created: 2026-04-14
workstream: customer-system
session: 2026-04-14-a
sources:
  - type: conversation
    description: "Craig and Claude working through domain modeling using the OS primitives"
  - type: local
    ref: "projects/product-vision/artifacts/2026-04-13-white-paper.md"
    name: "OS White Paper — domain modeling process and kernel primitives"
  - type: local
    ref: "projects/product-vision/artifacts/2026-03-25-domain-model-v2.md"
    name: "OS Domain Model v2 — DDD classification framework"
---

# Domain Model Thinking: Customer System

## Design Principle: Let the Kernel Do Its Job

The OS kernel provides mechanisms you don't rebuild as domain entities:

| Don't model this as an entity | The kernel already provides |
|-------------------------------|---------------------------|
| Activity log / interaction history | **Changes collection** — every entity mutation recorded automatically with field-level detail (who, what, when, from, to) |
| Notifications and awareness | **Watches on roles** — entity changes produce messages that flow to the right people automatically |
| Team member identity | **Actor** — kernel entity for all participants (human and AI) |
| Account ownership / assignment | **Role** assignments with watches — the account lead has a role with watches on that company's entities |
| Audit trail | **Changes collection** — tamper-evident, append-only, built into every entity by default |
| Communication as side effect | **Watches + Messages** — the wiring IS the communication system |
| Playbook procedures | **Skills** (partially) — but Playbook is its own entity because it's interactive data you add to, not a static procedure. Skills may be GENERATED from playbooks. |

The domain model covers BUSINESS DATA. The kernel covers CONNECTIVE TISSUE.

## Entity Criteria for the OS

When modeling a domain on the OS, apply these criteria to determine what should be its own entity:

1. **Identity** — Does it have a unique identity that matters to the business? Would you refer to it by name or ID?

2. **Lifecycle** — Does it have meaningful states that change over time, where those transitions matter to the business?

3. **Independence** — Can it exist on its own, not purely as a property of another entity?

4. **Not a kernel mechanism** — Is this business data, not something the kernel already provides (activity tracking, auth, role assignment, notifications)?

5. **CLI test** — Would someone want to `indemn <thing> list`, `indemn <thing> create`, `indemn <thing> get`? If you'd never interact with it directly, it's probably a field or embedded value on something else.

6. **Watchable** — Would changes to this thing need to flow to people via watches? If a meeting is created, should someone be notified? If a deal changes stage, should the account lead know?

7. **Multiplicity** — Can there be many of these per parent? If there's only ever one, it might be a section of the parent entity rather than its own thing.

This framework should become part of the OS domain modeling skill — it's the systematic process for step 2 ("Identify the entities") of the 8-step domain modeling process.

## Identified Entities

### Domain Entities (10)

| Entity | Identity | Lifecycle | Key Relationships | Why It's an Entity |
|--------|----------|-----------|-------------------|-------------------|
| **Company** | Yes — business name, ID | lead → contact → discovery → demo → proposal → negotiation → verbal → signed → onboarding → active → expanding → churned | Has many: Contacts, Deals, Implementations, Associate Deployments, Outcomes, Meetings | The root entity. Everything hangs off this. One entity from prospect through customer — Kyle's Pipeline Source of Truth spec says one system for pipeline AND customers. |
| **Contact** | Yes — person name, email | Minimal (active/inactive) | Belongs to: Company. Has: role, primary flag | A person at a company. Multiplicity: many per company. Independent: exists even if a deal is deleted. |
| **Deal** | Yes — opportunity ID | Stages with probability (contact through signed) | Belongs to: Company. Has many: Implementations | A specific business opportunity. A company can have multiple concurrent deals. Carries ARR, scoring, Four Outcomes mapping. |
| **Implementation** | Yes — impl ID | kickoff → configuration → testing → soft_launch → live → optimization → advocate | Belongs to: Deal, Company. Has many: Tasks. Links to: Associate Deployments | The delivery of a deal. Its own lifecycle independent of the deal stage. |
| **Task** | Yes — task ID | open → in_progress → completed → blocked | Belongs to: Implementation. Has: assignee (Actor), due date, effort | A unit of work. Many per implementation. Watchable: assignee needs to know when tasks are created or become blocked. |
| **Playbook** | Yes — playbook name | draft → active → archived | Has many: Playbook Steps. Used by: Implementations | A template for delivering a type of engagement. Interactive — you add to it, refine it over time. NOT a skill (skills are systematic procedures). Playbooks may generate skills for associates. |
| **Associate Deployment** | Yes — deployment ID | planned → building → testing → live → paused → retired | Belongs to: Company, Implementation. Links to: Associate Type | A specific associate deployed for a specific customer. Tracks status, usage metrics, success criteria. |
| **Outcome** | Yes — outcome mapping ID | Evolving (tracking value over time) | Belongs to: Company. Links to: Outcome Type, Associate Deployments | Per-customer mapping to the Four Outcomes with ROI tracking, proof points, value delivered vs potential. |
| **Meeting** | Yes — meeting ID | Minimal (scheduled → completed → intelligence_extracted) | Belongs to: Company. Has: transcript, decisions, action items, signals | A meeting with intelligence extraction. Many per company. Watchable: action items should flow to assignees. Connects to existing Meeting Intelligence DB via Integration. |
| **Conference** | Yes — conference name | planning → pre_event → active → follow_up → complete | Has many: Leads (→ Companies), Contacts. Has: cost, ROI tracking | A specific event Indemn attends. Tracks preparation, attendees, outreach, follow-up, and ROI. Links leads into the Company pipeline. |

### Reference / Lookup Entities

| Entity | Description |
|--------|-------------|
| **Associate Type** | The catalog of associates Indemn offers (24-48 from the product map). Has: standard playbook reference, required inputs, integration requirements, typical timeline, success metrics. This is an entity (not just a lookup) because it's edited over time as the product evolves. |
| **Outcome Type** | The Four Outcomes: Revenue Growth, Operational Efficiency, Client Retention, Strategic Control. With engine definitions and language rules. Small, stable, but referenced everywhere. |
| **Stage** | Reference table defining lifecycle stages with probability, staleness thresholds, definitions. Used by Company and Deal. |

### Handled by the Kernel (Not Domain Entities)

| Concept | Kernel Mechanism |
|---------|-----------------|
| Activity / interaction log | Changes collection (automatic on every entity) |
| Team members | Actor (kernel entity) |
| Account ownership | Role assignments + watches |
| Notifications | Watches on roles → Messages |
| Awareness of changes | Watches fire automatically on entity state changes |
| Audit trail | Changes collection (tamper-evident, append-only) |
| Version history | Changes collection (every mutation recorded) |

## Open Design Questions

1. **Company lifecycle stages** — Kyle's CRM has 7 sales stages (CONTACT through SIGNED) and his Prisma schema has implementation stages (KICKOFF through ADVOCATE). Are these one state machine on Company, or does the front half live on Deal and the back half on Implementation? Leaning toward: Company has a high-level lifecycle (prospect → customer → churned), Deal has the sales stages, Implementation has the delivery stages.

2. **Meeting as entity vs. Integration** — The Meeting Intelligence DB already has 22K+ meetings. Do we model Meeting as a domain entity and sync from the existing DB via Integration? Or do we treat meetings as coming through an Integration adapter that creates Meeting entities? Probably the latter — the Integration primitive handles the sync, Meeting is the domain entity.

3. **Conference → Company flow** — When a conference lead converts, it becomes a Company entity (or updates an existing one). The Conference entity tracks the event itself; the Company entity tracks the relationship. Need to define how leads flow from conference context into the main pipeline.

4. **Playbook → Implementation relationship** — An implementation is "created from" a playbook. Does this mean the playbook's steps are copied into the implementation as tasks? Or does the implementation reference the playbook and track progress against it? Copying is simpler and allows per-customer customization. Referencing keeps things in sync if the playbook updates.

5. **Usage data on Associate Deployment** — George's #1 ask. Where does usage data come from? Probably via Integration with the Observatory. The Associate Deployment entity carries usage fields that are updated via a scheduled sync.

6. **ROI/Value on Outcome** — How granular? Per-outcome-type per company? Per associate deployment? Kyle's Branch template has specific dollar amounts per outcome category. The Outcome entity probably carries: current_value_delivered, potential_value, projected_timeline, proof_points.

## What Informs the Entities

Craig's principle: what we're trying to DO should inform what entities we need, what attributes they need, and how they relate. The objectives (from the problem statement):

- **Source of truth** → Company, Contact, Deal, Associate Deployment, Outcome (the "look up any customer" use case)
- **Delivery tracking** → Implementation, Task, Playbook (the "what are we building and how far along" use case)
- **Communication/visibility** → Watches on all entities above (the "everyone knows what's happening" use case — kernel mechanism, not entities)
- **Pipeline/outreach** → Company (prospect stages), Conference, Deal (the "track leads through conversion" use case)
- **Value/intelligence** → Outcome, Meeting, Associate Deployment with usage (the "quantify what we're delivering" use case)

Every entity earns its place by serving at least one of these objectives.
