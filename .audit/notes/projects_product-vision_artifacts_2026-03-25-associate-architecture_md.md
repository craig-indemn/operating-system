# Notes: 2026-03-25-associate-architecture.md

**File:** projects/product-vision/artifacts/2026-03-25-associate-architecture.md
**Read:** 2026-04-16 (full file — 186 lines)
**Category:** design-source (early)

## Key Claims

- "An associate is a LangChain deep agent configured with skills that operate on domain objects via CLI/API."
- Evolution: from V1 agents (bot-service, conversation-focused) to V2 (config-driven) to OS associates (full domain model access).
- Skills work like Claude Code skills: a markdown document describing how to use tools.
- Skills list CLI commands the associate uses.
- Example skill: "Submission Processing Skill" with `indemn email classify`, `indemn submission extract`, etc.
- Associates built via CLI: `indemn associate create/add-skill/configure/connect-channel/deploy`.
- At runtime, associate listens on channels, reads skills, executes CLI/API calls, produces outputs, surfaces HITL checkpoints.
- All observable via LangFuse; all evaluable via evaluation framework.
- 9 existing building blocks catalogued for evolution (Bot-service, Platform-v2, Jarvis, Web operators, CLI, Evaluation framework, LangFuse, Skills pattern, MCP server).
- 7 open architectural decisions listed (V2 redesign scope, Bot-service role, Skill format, Domain access control, Workflow execution, Multi-agent coordination, State management).

## Architectural Decisions

- **Skills = markdown documents** (like Claude Code). Tentative at this stage; later resolved in entity-capabilities-and-skill-model (2026-04-09) as markdown.
- **Associate = deep agent** with CLI/API tool access.
- **LangFuse** as observability — later superseded in white paper by OTEL-centric observability.
- **Evaluation framework** extends from conversation quality to workflow outcomes.
- **48 associates are configurations of one system** (reinforces earlier mapping's claim).

## Layer/Location Specified

- "Bot-service as deployment/hosting layer (or its evolution)" — tentative. The later 2026-04-10-realtime-architecture-design.md resolved this: bot-service is legacy, the OS uses harness images per kind+framework.
- "Jarvis as prototype of Tier 3 (agents building agents on the platform)" — informs tier model.
- "Indemn CLI expands from agent management to full OS control plane" — confirms CLI-first approach.
- MCP server mentioned but later rejected per CLI-first philosophy.

Early artifact — speculative about deployment. Later superseded by:
- 2026-03-30-design-layer-3-associate-system.md (resolves associate = deepagents + sandbox)
- 2026-04-10-realtime-architecture-design.md (resolves harness pattern)

## Dependencies Declared

- LangChain, deep agents framework
- LangFuse (later superseded by OTEL)
- Bot-service (legacy)
- Platform-v2 (legacy)
- Claude Code skill pattern

## Code Locations Specified

- None concrete. References existing Indemn codebases.

## Cross-References

- Succeeded by: 2026-03-30-design-layer-3-associate-system.md (more concrete architecture)
- 2026-04-10-realtime-architecture-design.md (harness pattern formalizes this)
- context/craigs-vision.md (thesis foundation)

## Open Questions or Ambiguities

Artifact itself lists 7 open decisions — all resolved in later artifacts:
1. V2 redesign scope → resolved: new codebase, not evolution of V2
2. Bot-service role → resolved: not evolved, new kernel image + harness images
3. Skill format → resolved: markdown (2026-04-09)
4. Domain access control → resolved: Role-based permissions (white paper, auth-design)
5. Workflow execution → resolved: watches + scheduled triggers + direct invocation
6. Multi-agent coordination → resolved: unified queue + watches
7. State management → resolved: Attention entity + Temporal workflow state

**Early artifact. No Finding 0-class deviations introduced here. The LLM-framework-specific framing (LangChain deep agents) later generalizes to "harness pattern" — each framework gets its own harness image.**
