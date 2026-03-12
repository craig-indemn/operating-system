# GIC Agent Improvements

Systematic improvement of the GIC Underwriters AI associate ("Fred") — identify opportunities, implement changes, evaluate impact, and monitor ongoing performance.

## Status
Research phase complete. Deep research on agent configuration, backend architecture, policy API, and quantified baselines documented in `artifacts/2026-03-12-agent-research.md`. 13 improvement opportunities identified with root cause and baseline metrics. Ready for prioritization and implementation planning.

**Key numbers:**
- 2,148 bot conversations (Jan-Mar 2026), ~1,500-1,800/month
- 21% failure rate in observatory outcomes (1,115 of 5,330)
- 46% handoff rate (999 of 2,148)
- 14% policy lookup failure rate (83 of 602 policy-related messages)
- 643 missed handoffs in observatory

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Ryan's UX Observation Report | Google Doc | [GIC UX Observations](https://docs.google.com/document/d/1oiVuIhvTYHTkHuyfeluFNibE-AR3UeOx_3c0uRhyvLQ/edit?usp=sharing) |
| Kyle's assignment message | Slack | mpdm-kwgeoghan--ryan--craig (ts=1773236602.449279) |
| GIC bot config | MongoDB | tiledesk.bot_configurations (bot_id: `66026a302af0870013103b1e`) |
| Policy API route | Code | operations_api/src/routes/gic-policy-details.ts |
| Policy API service | Code | operations_api/src/services/customers/gic_policy_details.ts |
| Tool execution | Code | bot-service/app/services/tools/agent_tools.py |
| Observatory data | MongoDB | tiledesk.observatory_conversations (scope.customer_id: `65eb3f19e5e6de0013fda310`) |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-03-12 | [ryan-gic-ux-observations](artifacts/ryan-gic-ux-observations.pdf) | Ryan's full UX analysis with 17 observations and 14 screenshots |
| 2026-03-12 | [agent-research](artifacts/2026-03-12-agent-research.md) | Deep research: agent config, backend architecture, policy API, knowledge bases, quantified baselines for all 13 improvement opportunities |

## Decisions
- 2026-03-12: Project created to track GIC agent improvement work per Kyle's directive
- 2026-03-12: Added Craig's item #18 — policy number parsing improvements in operations_api

## Open Questions
- Prioritization: which opportunities to implement first? (system prompt changes are fastest wins)
- Evaluation framework: how will we measure impact of changes? (observatory outcomes, conversation depth, handoff rate)
- KB content: what specific WC class code data and appetite information needs to be added?
- Policy number formats: what are all valid GIC policy number formats across carriers? (needed for format validation)
- AgencyCode: how is this populated in conversation attributes? (Redis external_conversation_variables)
