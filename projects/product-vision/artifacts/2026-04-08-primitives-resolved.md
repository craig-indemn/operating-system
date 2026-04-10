---
ask: "Can we resolve the four open questions about primitives — actor definition, wiring mechanism, entity/actor boundary, scheduled tasks?"
created: 2026-04-08
workstream: product-vision
session: 2026-04-08-a
sources:
  - type: conversation
    description: "Craig and Claude pressure-testing OS primitives against GIC email intelligence system, resolving the wiring question"
  - type: artifact
    description: "2026-04-08-actor-spectrum-and-primitives.md — the actor spectrum insight that led to this"
---

# Primitives Resolved — Watches, Actor Spectrum, Entity/Actor Boundary

## Question 1: What is the minimal definition of an Actor?

An actor is: **an identity that has a role and processes triggers by executing CLI commands against entities.**

What's common across ALL actors (human, reasoning associate, deterministic associate):
- **Identity** — who is this?
- **Role** — what can it access, what does it receive?
- **Queue** — what's waiting for its attention?
- **Output** — CLI commands that change entity state

What VARIES is only the execution engine — how the actor decides which CLI commands to run:
- Human: looks at UI, applies judgment, clicks/types
- Reasoning associate: reads skills, reasons via LLM, executes CLI
- Deterministic associate: follows a procedure, executes CLI
- Hybrid associate: tries deterministic first, falls back to LLM

**The OS should not care about this distinction.** The OS delivers a message to a role's queue. Whatever picks it up and processes it is an actor. The OS sees: message claimed → CLI commands executed → entity state changed → new messages generated. What happened in between is the actor's business.

For an associate specifically, the configuration beyond identity+role is:
- **Skills** — what it knows how to do (the "programs")
- **Execution mode** — deterministic, reasoning, or hybrid (which "interpreter" to use)
- **LLM config** — model, temperature (only if reasoning/hybrid)

The minimal associate is: role + skills + mode. That's it.

### The Actor-Skill-Interpreter Model

An associate's "skill" IS the specification of what to do — and the skill can be anywhere on the deterministic-to-reasoning spectrum.

**Fully Deterministic Skill:**
```
When Email is created from @usli.com:
1. indemn email classify {id} --type usli_quote --lob {from_usli_prefix}
2. indemn email link {id}
3. If submission.automation_level == auto_notified:
   indemn submission close {id} --resolution auto_notified
```

**Fully Reasoning Skill:**
```
When Email is created from an unknown sender:
Read the email content, all attachments, and any extraction data.
Determine what type of email this is, what line of business it relates to,
and who the named insured is. Use your judgment.
Then: indemn email classify {id} --type {your_determination} --lob {your_determination}
```

**Hybrid Skill:**
```
When Email is classified:
1. Search by reference number: indemn submission search --ref {refs}
2. If found → indemn email link {id} --submission {found_id}
3. If not found → search by insured name: indemn submission search --insured {name} --fuzzy
4. If fuzzy match confidence > 85% → link to match
5. If ambiguous or no match → create new: indemn submission create --insured {name} --lob {lob}
6. Use judgment for: which match to pick when multiple candidates are close
```

All three are skills. All three are read by an actor. The difference is execution:
- Skill 1 can be executed by a simple interpreter. No LLM needed.
- Skill 2 requires an LLM to reason.
- Skill 3 is mostly deterministic with LLM as fallback.

**The framing:** If a deterministic skill is "a sequence of CLI commands with conditions," it's basically a program. If a reasoning skill is "an LLM agent that reads instructions and executes CLI commands," the LLM is basically an interpreter for a more ambiguous program. Both are programs that execute CLI commands. One has a deterministic interpreter. The other has an LLM interpreter. Same input (skill + context), same output (CLI commands), different execution engine.

**The actor is the executor. The skill is the program. The interpreter can be deterministic or LLM-based. The OS doesn't care which — it just sees CLI commands being executed and entities changing.**

---

## Question 2: How does a Role declare "what comes to me"? — WATCHES

A watch is: **an entity type + an event + optional conditions.** It says "actors with this role care about this kind of entity change."

### GIC Example

```
classifier watches:
  - Email created (no attachments)
  - Email.processing_status → extracted

linker watches:
  - Email.processing_status → classified

assessor watches:
  - Email.processing_status → linked

draft_writer watches:
  - Assessment created WHERE draft_appropriate = true

underwriter watches:
  - Assessment created WHERE needs_review = true
  - Submission.stage → triaging

operations watches:
  - Submission.stage changed (any)
  - Draft created
  - Submission.is_stale → true
```

### Why Watches, Not Routing Rules

The computation is identical. But the mental model is different.

**Routing rules are system-centric:** "When X happens in the system, route to Y." You're thinking about the WIRING — the plumbing between things. The mental image is a diagram of pipes.

**Watches are actor-centric:** "This role cares about X." You're thinking about the ACTOR — what does this person or associate need to see? The mental image is a person's desk with their inbox.

When you set up a new org, you don't think "I need to create 15 routing rules." You think "what does each role need to see?" That's watches.

### Watches Give Full Visibility

```
indemn role list --show-watches
```

Shows the entire system behavior at a glance — every role, what each watches, how many actors per role, current queue depth. The "wiring" is visible because it IS the role definitions.

### Watches Handle All Patterns

| Pattern | Watch Expression |
|---------|-----------------|
| Sequential pipeline | classifier watches Email:created → linker watches Email:classified → ... |
| Conditional routing | draft_writer watches Assessment:created WHERE draft_appropriate=true; underwriter watches Assessment:created WHERE needs_review=true |
| Fan-out | Both underwriter AND operations watch Submission:stage_changed |
| Specific conditions | underwriter watches Submission:stage → triaging (not all stage changes) |

One mechanism. Simple cases and complex cases. Same thing.

### Configurable via CLI

```
indemn role add-watch underwriter --entity Assessment --on created --when "needs_review=true"
```

Per-org — different organizations can have different watches on the same role name, because watches are scoped by org_id.

### Watches Live on Roles, Not Actors

All actors with the same role get the same messages. The role defines what you see. The individual actor claims specific messages from the queue. Individual filtering ("I only want GL submissions") is a UI-level filter on the queue, not a watch.

---

## Question 3: Where does the entity end and the actor begin?

### The Principle

**Entity behavior is what's true for ALL instances of that entity type across ALL organizations. Actor behavior is what varies by org, by configuration, by workflow.**

The entity is the PLATFORM. Universal. The same Submission entity exists in every org. Its state machine, its computed fields, its validation — universal.

The actors are the APPLICATIONS. Per-org. Different organizations configure different watches, different associates, different skills. The same Submission entity gets processed by different actors in different ways.

### Applied to GIC

| Logic | Entity or Actor? | Why |
|-------|-------------------|-----|
| Ball holder = f(stage) | **Entity** (computed field) | True for ALL submissions in ALL orgs. Intrinsic to what a Submission is. |
| State machine enforcement | **Entity** | Universal. A Submission can't go from "received" to "closed" without valid transitions. |
| Field validation (insured name required) | **Entity** | Universal data integrity. |
| USLI auto-close when auto_notified | **Actor** (deterministic) | GIC-specific business rule. Another org might review auto-notified submissions. |
| Hard rules (@usli.com → USLI type) | **Actor** (in classifier skill) | GIC-specific. Another org might classify USLI emails differently. |
| "Premium > $50K → also notify senior UW" | **Actor** (watch condition) | Org-specific routing threshold. |
| Stale detection (7 days, 2+ followups) | **Actor** (scheduled) | The thresholds are org-configurable. |

### The Clean Separation

**Entity behavior:** validation, computed fields, state machines, relationship integrity. The entity is dumb infrastructure that maintains data integrity.

**Actor behavior:** business rules, processing logic, routing decisions, anything that varies by org or configuration. The actors are the smart layer that makes business decisions.

This means:
- Building a new entity is simple — fields, state machine, relationships, computed fields. No business logic.
- All business logic customization happens at the actor/role layer — configurable per org.
- The same entity framework works for insurance, CRM, or anything else. The domain specificity is in the actors, not the entities.

### Edge Case: Org-Aware Entity Validation

Some validations feel like entity behavior but depend on org configuration. Example: "A Draft can only transition to 'sent' if the organization has an email integration configured."

Answer: Entity validation CAN reference org configuration. The validation rule is universal (all Drafts check this), but the result varies by org. The entity is still the platform — it's just a platform that's aware of its configuration context.

---

## Question 4: Is a scheduled task just an actor with a time-based trigger?

### Simple Scheduled Tasks: CLI Commands on a Timer

The email sync: `indemn email fetch-new` runs every minute. It creates Email entities. Those entity creations generate messages. The classifier's watch matches. The pipeline starts churning. The sync itself isn't an actor — it's infrastructure that feeds entities into the system.

The stale checker: `indemn submission check-stale` runs every hour. It finds stale submissions and marks them (`is_stale → true`). That state change generates messages. The operations role's watch matches. Operations sees stale submissions in their queue.

**The scheduled CLI command is the trigger. The messaging system is the consequence. Clean separation.**

### Complex Scheduled Tasks: Associates with Time-Based Triggers

If the scheduled task needs to do something complex — find stale submissions, check each one's agent history, generate personalized follow-up drafts, route them for approval — that's not a simple CLI command. That's a multi-step process potentially requiring judgment.

In that case, the scheduled task IS an associate — a reasoning or hybrid actor triggered by schedule instead of by message.

### Associate Trigger Types

An associate's trigger can be:
- **Message** — a watch matched, message appeared in the role's queue
- **Schedule** — a cron expression, the associate is invoked periodically
- **External event** — a webhook, a channel opening (voice/chat)

All three trigger the same actor framework. Same skills, same CLI access, same entity changes, same message generation.

---

## The Resolved Primitive Set

**Entity** — data with structure, lifecycle, CLI, self-describing skills. Includes provider-specific implementations (Outlook email IS an email). Universal across orgs. Entity behavior: validation, computed fields, state machines. The platform.

**Message** — generated by entity changes (state transitions + @exposed methods + creation/deletion). Contains what changed and context. Delivered to actors whose role watches match.

**Actor** — identity + role. Processes triggers by executing CLI commands. Trigger types: message, schedule, external event. Execution modes: human (UI), reasoning (LLM + skills), deterministic (procedure + skills), hybrid. The OS treats all modes identically — signal in, CLI commands out.

**Role** — defines permissions (what entities you can access) AND watches (what entity changes you care about). Automatically generates: queue view, UI, CLI scope. Per-org configurable. **The wiring IS the set of watches across all roles.**

### The Wiring Question — Answered

The wiring question was: "How does the system wire entity changes to consequences?"

Answer: **Roles have watches. Watches declare what entity changes matter to actors with that role. When an entity changes, the system evaluates watches and delivers messages to matching roles' queues. Actors process messages by executing CLI commands. Entity changes generate more messages. The system churns.**

Not routing rules. Not connections. Not subscriptions. Watches — an intrinsic part of what a Role IS. A role isn't just access control. It's the complete specification of how an actor participates in the system: what it can do (permissions) and what comes to it (watches).

### Integration Collapse

The integration layer (previously Layer 4) collapses into the entity framework (Layer 1). An Outlook email IS an Email entity with Outlook-specific implementation. `indemn email fetch-new` dispatches to the right implementation based on org configuration. The CLI stays the same. The associate's skill stays the same. The external system detail is encapsulated in the entity implementation.

The entity framework IS the integration framework. One primitive, not two.

### How GIC Looks on the OS

```bash
# Create roles with watches
indemn role create classifier --watches "Email:created, Email:status_changed[processing_status=extracted]"
indemn role create linker --watches "Email:status_changed[processing_status=classified]"
indemn role create assessor --watches "Email:status_changed[processing_status=linked]"
indemn role create draft_writer --watches "Assessment:created[draft_appropriate=true]"
indemn role create underwriter --watches "Assessment:created[needs_review=true]" "Submission:stage_changed[stage=triaging]"
indemn role create operations --watches "Submission:stage_changed" "Draft:created" "Submission:is_stale_changed[is_stale=true]"

# Create associates with roles and skills
indemn associate create --name "Email Classifier" --role classifier --skills email-classification --mode hybrid
indemn associate create --name "Submission Linker" --role linker --skills submission-linking --mode hybrid
indemn associate create --name "Assessor" --role assessor --skills situation-assessment --mode reasoning
indemn associate create --name "Draft Writer" --role draft_writer --skills draft-generation --mode reasoning

# Assign humans to roles
indemn actor assign jc@gicunderwriters.com --role underwriter
indemn actor assign maribel@gicunderwriters.com --role operations

# Schedule infrastructure
indemn schedule create --name "email-sync" --command "indemn email fetch-new" --cron "*/1 * * * *"
indemn schedule create --name "stale-check" --command "indemn submission check-stale" --cron "0 * * * *"
```

The entire GIC email intelligence system — configured via CLI, visible at a glance, running on four primitives.
