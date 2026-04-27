# Customer System — Vision

> Slow-changing end-state articulation for the customer-system project. **What** we're building, **why**, and the **lens** through which we think about it. Read this with `roadmap.md` (how we get there + where we are now) and `os-learnings.md` (the running register of OS-relevant findings).
>
> Audience: us — Craig, future Claude sessions, parallel sessions working in forks. Voice is internal/peer. Cam, Kyle, and the team read it when they need the picture.

---

## 1. The frame: dual-track

The customer system is the **first build on the Indemn Operating System**. It is also the **mechanism by which the OS becomes capable of running all our systems**.

These are not separate efforts. We are not building a customer system that uses the OS. We are using the OS the way it was designed, while building. The customer system is the proving ground — the first real domain where every primitive (entities, watches, rules, associates, integrations, runtimes, attentions, sessions) gets exercised in production against real data. Patterns that were designed but never used get used. Gaps surface. The OS gets refined as we build, and what we build only works because the OS does.

**The end objective is not "ship the customer system."** It is to use the OS the way it was designed and have the customer system fall out as a consequence. Bug resolution is a means to that end. The OS bug list converges to zero on the items we choose to prioritize. Compute is not a constraint, so when something blocks the build we fork a parallel session and fix it. There is no reason the list has to stay long. Forking is a first-class operating mode, not an exceptional one.

By the time the customer system is achieving its own vision, the OS will be capable of running anything else Indemn does, and ready for the horizons below.

---

## 2. End-state

### Customer-system "done" — the in-scope target

The system runs itself. New emails and meetings flow in, become Touchpoints, get extracted into Tasks/Decisions/Commitments/Signals/Opportunities, hydrate Proposals continuously, and produce stage-appropriate artifacts for human review at every interaction. The team uses it as their daily mode. Cam manages proposal generation systematically. Kyle is no longer the single point of failure for "what's the story with X."

Two layers, both must be true.

#### Foundation (engineering layer)

The underlying system that runs behind the scenes. Not team-facing on its own, but everything on top depends on it.

1. **Entity model complete and accurate.** 27+ entity definitions live, all relationships modeled, Touchpoint carries forward source pointers (Option B), Playbook entity is consulted by both the Intelligence Extractor and the Artifact Generator. The model holds for any customer at any stage.
2. **Entity-resolution capability lives in the kernel.** Given (domain, name, email, similar description) → return likely existing matches with confidence scores. Associates call this before creating. Root fix for the 446-Companies / Bug #16 class. New Companies, Contacts, Documents do not proliferate as duplicates.
3. **Pipeline associates run hands-off.** Email Classifier, Touchpoint Synthesizer, Intelligence Extractor, Artifact Generator. They claim work from queues, do their job, mark complete. No silent stuck states. No cross-invocation cache leaks. No deterministic workarounds for LLM-capability work.
4. **Watch cascade is reliable end-to-end.** Email/meeting arrives → Touchpoint synthesized → intelligence extracted → opportunities created → proposal hydrates → artifact generated. Every link works. The cascade does not drop.
5. **The constellation is queryable.** For any customer, the full picture (Company + Contacts + Touchpoints + Operations + Opportunities + Proposal + Phases + Documents + Associates) loads via CLI/UI in seconds. This is the source-of-truth Kyle described in the original problem.
6. **Temporal workflows are manageable.** Observable, can intervene, can debug. We can see what is happening at any point in any workflow.
7. **OTEL spans are observable.** Deep tracing on every operation. Bug-fixing and behavior-debugging have first-class visibility. LangSmith on all harnesses for AI observability.
8. **The OS itself is dogfooded as designed.** If a pattern was designed but never used in practice, we use it. This is the test that the OS is what we believed it to be.
9. **OS bug list is converged on what we prioritize.** Not a permanent surface — an actually-clearable backlog. The list lives in `os-learnings.md`. Items we choose to prioritize get to zero.

#### Two threads on top (the team-facing wins)

These are the things the team interacts with. Each thread is shaken out by tracing through a real situation, then built out to run autonomously as part of the foundation.

A. **Meeting-level view.** For every meeting Indemn has — customer-facing AND internal — the same shape Kyle saw for GR Little: entity trace, extracted intelligence, draft artifact. Sales, success, and engineering use it to monitor, prepare, and react to what associates produce. Grows into a larger dashboard as the team uses it.

B. **Proposal generation.** Every Deal has a Proposal entity that hydrates from DISCOVERY onward. At PROPOSAL stage, the Artifact Generator renders it. Tangible deliverable the team currently does manually. The Alliance v2 proposal trace (this session) is the first.

Hydration of every customer and prospect — Alliance, Arches, FoxQuilt, the full roster — is **implied** in achieving the foundation, not a separate item.

### Horizons (visible, not in scope here)

Articulated so the work doesn't drift. Both inform sequencing without expanding scope.

- **(2) All Indemn operations on the OS.** Customer system is the largest chunk; once it's done, delivery tracking, playbooks, health monitoring, team capacity, conferences, value/ROI, evaluations, and the rest of the 17 functional areas from the 04-14 capabilities doc follow. Indemn-the-company runs on the OS.
- **(3) OS production-ready for external customers.** The kernel is hardened, the capability library is mature, the customer-onboarding playbook is real, a second domain can be modeled in days not weeks. The white paper's Phase 6 → Phase 7 transition becomes operable.

---

## 3. The lens: the breakthrough

How we think about the system, in one frame.

> **The entity model IS the playbook. The Proposal is the spine. Every stage produces an artifact via the same mechanism.**

The Proposal is the destination. The entities IN the Proposal — Operations, Opportunities, Phases, AssociateTypes, Commitments, Tasks — need to be filled out. The process of filling them out is the playbook. Empty fields are gaps. Gaps tell us what to do next. When the gaps are filled, we have a Proposal.

Every customer follows the same process. Same entities. Same fields. The data differs; the structure is universal. Progress is measurable by counting populated vs empty fields. Next steps are automatic — gaps generate Tasks. New team members have a guide. AI can drive it.

**The Proposal is created at DISCOVERY as an empty spine.** It hydrates continuously from every subsequent Touchpoint. Opportunities link to it. Phases form as the deal matures. At PROPOSAL stage, the Artifact Generator just renders it. Same mechanism every prior stage; only the Playbook record changes.

**The mechanism for every artifact:**

```
(Deal + recent Touchpoints + extracted intelligence + Playbook for Deal.stage + raw source content)
  → Artifact Generator
  → stage-appropriate draft (email at DISCOVERY, recap at DEMO, proposal doc at PROPOSAL, objection response at NEGOTIATION, kickoff at SIGNED)
  → human review → one-click send
```

The Playbook is consulted twice per Touchpoint: once by the Intelligence Extractor (`required_entities` becomes the extraction schema for that stage), once by the Artifact Generator (`artifact_intent` becomes the spec for what to render). Different stages produce different extraction categories and different artifacts. Same mechanism. One entity model. Universal pattern.

This is why the two threads (meeting view, proposal generation) are not separate features. They are the same system surfacing at different stages.

For depth on the breakthrough: `artifacts/2026-04-23-playbook-as-entity-model.md` (the load-bearing insight) and `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` (the architectural refinements).

---

## Where to go from here

| File | What's in it |
|---|---|
| `roadmap.md` | The phased path to achieving this vision. Where we are now. Pre-scoped phases A–F + continuous threads. |
| `os-learnings.md` | Running register of OS-relevant findings (bugs, capability gaps, design questions). The handoff queue between customer-system work and OS work. |
| `INDEX.md` | Append-only project history (Status, Decisions, Open Questions, full Artifacts table). |
| `CLAUDE.md` | Cumulative thinking, journey, principles, start-of-session protocol. **Read first in every session.** |
| `artifacts/2026-04-22-entity-model-design-rationale.md` | Why the entity model is shaped the way it is. The Alliance test. |
| `artifacts/2026-04-23-playbook-as-entity-model.md` | The breakthrough articulated. |
| `artifacts/2026-04-24-design-dialogue-playbook-artifact-proposal.md` | Latest entity-model refinements (Apr 24). |
| `artifacts/2026-04-24-information-flow-v2.html` | The visual demo Kyle validated. |
| `/Users/home/Repositories/indemn-os/docs/white-paper.md` | The OS canonical vision. The platform this is built on. |

---

*This document is slow-changing. When the end-state shifts, revise here and stamp a dated artifact (`artifacts/<date>-vision-revision-<descriptor>.md`) capturing what changed and why. Append to INDEX.md Decisions.*
