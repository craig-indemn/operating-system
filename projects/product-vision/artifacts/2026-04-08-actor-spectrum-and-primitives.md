---
ask: "How do deterministic and reasoning actors coexist in one framework? What are the true primitives?"
created: 2026-04-08
workstream: product-vision
session: 2026-04-08-a
sources:
  - type: conversation
    description: "Craig and Claude pressure-testing OS primitives against GIC email intelligence system"
---

# The Actor Spectrum and Primitive Refinement

## The Core Insight

Everything is CLI. If it's in the CLI, an associate can do it. If an associate can do it, a deterministic process can do it too. The CLI is the universal interface. The distinction between "who invokes the CLI command" is an implementation detail, not an architectural one.

## What Craig Said That Matters

- The deterministic/reasoning split shouldn't be a separate mechanism. ONE framework where sometimes the actor reasons (LLM) and sometimes it follows a fixed procedure (no LLM), but the system around it — messages, queues, entities, CLI — is identical in both cases.
- Entity polymorphism for integrations. An Outlook email IS an email. The external system integration isn't a separate "adapter layer" — it's how the entity is implemented for that provider. `indemn email fetch-new` works regardless of whether the org uses Outlook or Gmail. The entity interface is universal; the implementation varies.
- Primitives must compose into everything. The messaging system, the queue, the role-based visibility — these aren't features bolted on. They're primitives that the entire system is built from.
- "I wonder if there's a way to package it into the associate while keeping it deterministic and being able to build that associate in a way that's both deterministic and not."
- "I don't want to waste LLM processing on things that can be done deterministically, and I want there to be deterministic behavior in situations where it makes sense."

## The Core Tension

The system needs actors that receive triggers, process them by executing CLI commands against entities, and produce entity state changes that propagate through the system. The tension: the actor that processes a trigger might need LLM reasoning, might need deterministic logic, or might need both — and we don't want three different systems for this.

## The Actor as Executor, the Skill as Program

An actor is: **something that receives a signal and executes CLI commands in response.** Whether it's a human reading a queue and clicking buttons, an LLM agent reasoning about what commands to run, or a script that runs a fixed sequence of commands — the OS sees the same thing: signal in, CLI commands out, entity changes as a result.

An associate's "skill" IS the specification of what to do — and the skill can be anywhere on the deterministic-to-reasoning spectrum.

### Fully Deterministic Skill
```
When Email is created from @usli.com:
1. indemn email classify {id} --type usli_quote --lob {from_usli_prefix}
2. indemn email link {id}
3. If submission.automation_level == auto_notified:
   indemn submission close {id} --resolution auto_notified
```

### Fully Reasoning Skill
```
When Email is created from an unknown sender:
Read the email content, all attachments, and any extraction data.
Determine what type of email this is, what line of business it relates to,
and who the named insured is. Use your judgment.
Then: indemn email classify {id} --type {your_determination} --lob {your_determination}
```

### Hybrid Skill
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

### The Framing

If a deterministic skill is "a sequence of CLI commands with conditions," then it's basically a program. If a reasoning skill is "an LLM agent that reads instructions and executes CLI commands," then the LLM is basically an interpreter for a more ambiguous program.

Both are programs that execute CLI commands. One has a deterministic interpreter. The other has an LLM interpreter. Same input (skill + context), same output (CLI commands), different execution engine.

**The actor is the executor. The skill is the program. The interpreter can be deterministic or LLM-based. The OS doesn't care which — it just sees CLI commands being executed and entities changing.**

## Integration Collapse: Layer 4 Into Layer 1

Instead of: Email entity + Integration entity + Adapter class + Adapter registry + `get_adapter()` resolution

Craig describes: Email entity with provider-specific implementations. `indemn email fetch-new` dispatches to the right implementation based on org configuration.

The integration layer isn't a layer at all. It's entity behavior. The CLI stays the same. The associate's skill stays the same. The external system detail is encapsulated in the entity implementation.

**This collapses Layer 4 into Layer 1.** The entity framework IS the integration framework. One primitive, not two.

## The System Churning

Entity changes → messages generated → actors receive messages in their queue → actors execute CLI commands → entity changes → more messages → the system churns like a well-oiled machine.

Every actor (human, LLM associate, deterministic associate) participates in the same cycle. The queue is universal. The CLI is universal. The messaging is universal.

## Open Questions (Must Resolve)

### 1. What is the minimal definition of an Actor?
Is it: trigger + skill + execution mode + role? What else?

### 2. How does a Role declare "what comes to me"?
This is the wiring question, framed from the role's perspective. A role says "I care about X" — what does X look like?

### 3. Where does the entity end and the actor begin?
Ball holder derivation is clearly entity behavior (computed from stage). USLI auto-close is... entity behavior? Actor behavior? Where's the line?

### 4. Is a scheduled task just an actor with a time-based trigger?
The stale-submission checker runs every hour. Is it an associate with a cron trigger instead of a message trigger? Same framework, different trigger type?

## GIC Pressure Test Context

This thinking emerged from mapping the GIC Email Intelligence production system onto OS primitives. GIC has:
- A sequential pipeline (extract → classify → link → assess → draft) that maps to actors processing messages in sequence
- Deterministic hard rules (USLI domain → USLI type) that shouldn't waste LLM cycles
- Hybrid logic (fuzzy matching with deterministic threshold + LLM judgment for ambiguous cases)
- External integration (Outlook via Graph API) that should be entity behavior, not a separate layer
- Ball holder tracking (deterministic derivation from stage) that's clearly entity behavior
- Time-based monitoring (stale detection) that needs a trigger mechanism beyond entity changes
- Human-in-the-loop (draft approval) that uses the same queue as AI actors

All of these should work naturally with the same set of primitives.
