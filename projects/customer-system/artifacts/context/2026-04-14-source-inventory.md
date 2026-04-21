---
ask: "Inventory all source materials for the customer system project"
created: 2026-04-14
workstream: customer-system
session: 2026-04-14-a
sources:
  - type: google-drive
    description: "Search of Google Drive for customer delivery/success documents and meeting transcripts"
  - type: slack
    description: "Search of Slack for shared documents and context"
  - type: google-sheets
    description: "Kyle's CRM InsurTechNY spreadsheet"
---

# Source Inventory: Customer System Project

## 1. Kyle's Customer Success Context Package

28 files shared April 10 via DM. Folder ID: `12qo6eicpSvKNuJyafUs9qn1kdJY0OkC7`

### 01 - Customer Profiles
| Document | ID | Key Content |
|----------|-----|-------------|
| Portfolio Overview | `1y98S7T9nCHSbvLM936FwfhGD7hVxE61qJ-PFJlADNrA` | 18 customers, 3 cohorts (Core/Graduating/AI Investments), $273K ARR Core |
| Customer Profile - GIC | `1xmTWBOvAF04fM-moy18P_xG5NTl0fv1Vdcgc18Rt8jo` | Core, email intelligence + portal |
| Customer Profile - Jewelers Mutual | `1l8Fid8uEGDVQmRoylZwGSHeH8eN6ImMhQg8_V2p28J8` | Core, EventGuard, 351 venues |
| Customer Profile - INSURICA | `1JfM7b0TjaoAJWpbsUs1QZ_2R-wsijRDazkvjDm0wYm0` | Core, renewals + CSR |
| Customer Profile - Union General | `14oieQ9jv-gw3BL22-h4f9lgGsfo0tUi76jcSqClch4w` | Core |
| Customer Profile - Distinguished Programs | `1OgXqi6cuYBIhaxDg2SG_MuoUFz7H4QGnbiCOlmkC3yc` | Core, $12K/mo (corrected from $250K) |
| Customer Profile - Johnson Insurance | `1CAeHtGK9Vw5SgkCibBffQDLdK158qYsNlqQ0yJdrGnA` | Graduating, $2.5K/mo signed |
| Customer Profile - O'Connor Insurance | `1OLJo7fzI0Jyi_bzXtGZy2O8hg1TkSGnGGQPhy0mGnEg` | Graduating, multi-channel |
| Customer Profile - Tillman Insurance | `1Us1mnPALJ5m-5R474AkdRNl9lZZ8oZtw1UurDp2qx9U` | Graduating, bilingual |
| Customer Profile - Rankin Insurance | `1R63d-9YdEADBVtN8iLfRVDuxsTYW-FAtlA4I9rUGRig` | Graduating, voice quote |

### 02 - Product Framework
| Document | ID |
|----------|-----|
| Four Outcomes Framework | `1rZlcH281IYg6zT9iJWBoCA-WFztROH_KnWxsl7ZHjWs` |
| Four Outcomes Product Map - 24 Associates | `1cnQObEWyrgnTkuJGZEY0lKVIuF68ApVqbOZmS3cpZRg` |
| Products - Engine Definitions | `1wj3-ruYk4XrUULljuupx9hF6m5HnUzBgS8qsLl5soz0` |
| Language Rules | `1mc125GdgW7rTWvazntIPW6pCKOUngLih2VZyH3a7ugc` |

### 03 - Data Models
| Document | ID | Key Content |
|----------|-----|-------------|
| Pipeline Schema - Customer Models (Prisma) | `1Fim6_FYmmPdx4Ww_df1TvCIWh48oA8e6pNbRofFGFbI` | Company, Deal, Implementation, Task, Playbook models |
| Immutable Ledger Patterns | `1wOPsJF6U3dg6ggABUkZ6BQnf0DMP-WhM84exdtZ6des` | 5 patterns already in codebase |
| API Endpoints for Customer Success | `1m7FN7v-T6x4QQZ1pAxyN3P4humCtb70G444eyZKMdXs` | Pipeline API, Meetings API, Gmail API |

### 04 - Customer Success Plans
| Document | ID | Key Content |
|----------|-----|-------------|
| Customer Success Plan - Apr 1-3 Decisions | `16uOFigIPFsQ_gf93HZ9gK8KS1I9x41DVhe0hAlrtzOE` | Key decisions from Kyle+Cam sessions |
| Customer Operating System - 3-Layer Design | `13o64qOhO-0SZP0kkLlti0_31bOsKL73qo8HCk45sCkU` | Master Sheet + Primary Doc + Communication Cadence |
| Customer Health Monitor - Design | `16iYF7UFNZhgSSYgcivvN58YJGEap2lObHDgeEElLLeY` | Weighted scoring, cohort multipliers |
| Capacity Model - 18 to 100 Customers | `1ZjzHo5OSd8t4e3lc4ujNxj3nrVcjhiq7sRUanpjefLs` | 9-month projection, staffing ratios |
| Pipeline Source of Truth - Tab Structure | `14L6goa_P-j3bT0-YeD8qVviFHJv4nJ4wIWFGJE0tyGI` | 6-tab spec for THE spreadsheet |

### 05 - Evaluation System
| Document | ID |
|----------|-----|
| AI Associate Evaluation Framework | `1MOir6H1FkNoy8Vb4bES12Ykw4tqqspMxyFRAzR6ATMc` |

### 06 - Team and Operations
| Document | ID | Key Content |
|----------|-----|-------------|
| Team Allocation - Customer Success | `1jhemNR2ArbSs_I55aDMHwcqps6OffNju4MP5bOE3aZY` | Deep/Batch/Platform/Long-term delivery models |
| Meeting Intelligence System | `1aAIBMC-8bZb-P9gouADIHrHn_TgH6lBjPwAasHpOZFw` | 22K+ extractions from 3,130 meetings |

### 07 - Reference
| Document | ID |
|----------|-----|
| Google Sheets Reference | `1Ag8F2H7W1KITiOhZwRf6v6vuWjS_ejWOFTg5W2QiEEc` |

---

## 2. The Keystone Document

**"Customer Operating System -- Where We Are and Where We Need to Go"**
ID: `1dAtib-y9d5I-O9WzW8PON2ofxVKEkzhI7cXwZyk9Kxk` (March 2026)

The most important document. States the core problem: if anyone needs to understand a customer, they have to ask Kyle. Johnson Insurance went 10+ days without an email response. 67% of WON customers showed "Never" for last contact. 6 of 18 had no assigned owner.

Proposes 3-layer system:
- Layer 1: Master Sheet (one row per customer — ARR, owner, health, days since contact, next action)
- Layer 2: Primary Doc per customer (5-min context brief)
- Layer 3: Communication Cadence System (rules for contact frequency + alerts)

---

## 3. Kyle's CRM InsurTechNY Sheet

ID: `1B3QnzfS8IEM7cMN3ar9gSFRw8K8_viFmH-dEajQ9tQg` (shared today, April 14)

5-tab relational model:
- **Companies** (40 rows): pipeline tracker with stage, category (Cat 1/2A/2B/2C), owner, follow-up dates, staleness tracking
- **Contacts** (43 rows): people linked by company name, title, email, how-met channel
- **Ledger** (16 rows): activity log with date, action, actor (includes "Claude"), source provenance
- **Stages** (7 rows): CONTACT → DISCOVERY → DEMO → PROPOSAL → NEGOTIATION → VERBAL → SIGNED with probability
- **Company Profiles** (39 rows): enrichment — description, industry, size, type, ICP fit

Kyle's stated goal: "define an initial data model for our customer CRM that is useful now and scalable into the future" + "build a dashboard view focused on ongoing ROI"

---

## 4. Related Strategic Documents

| Document | ID | Modified |
|----------|-----|----------|
| Customer Delivery System -- Branch as Template | `1yYLRgfk1TbSNraNW9aoJ0yp6j7lCdcf8h2l8xwRSFdA` | 2026-04-06 |
| Customer Success System -- Portfolio Tracker | `1etsZyXfES6cx-acTHja_29EKh1xK2eFkjyw4JSujYa4` | 2026-03-27 |
| Cam Bridge -- Context Layer Design Doc | `1TjyiXxHvTmgZQC84SqlgKjytISa3Kc2gHcg8Kz_1NKg` | 2026-03-22 |
| BIB -- Context Bundle | `1wG0bTcODb6vBM6ntMbe1InwNeJCi5PomrXO9sTa7c7o` | 2026-04-10 |

---

## 5. Ganesh's Implementation Playbook

**Repo:** `ganesh-iyer/implementation-playbook` (private, on Ganesh's personal GitHub)
**Live:** https://implementation-playbook.vercel.app
**Created:** 2026-04-05, last pushed: 2026-04-10
**Type:** TypeScript application for internal customer implementation management

Kyle showed Craig this UI and asked him to lead the project plan and system design. Ganesh confirmed Craig has access.

---

## 6. Meeting Transcripts (Google Drive — Gemini Notes)

### Directly About Customer System
| Date | Title | Notes ID | Has Recording |
|------|-------|----------|---------------|
| 2026-04-06 | Craig / Kyle - Customer Source of Truth | `1KbexUyb8SIbQHifsgeUfJjEAleO1-AIUoWpNCYIGTuQ` | Yes |
| 2026-04-06 | Customer Success (group) | `1S_z3EC5oqqq1ybB0vm_gnyzo0Dm_eBW-UUOw8s0dAOg` | Yes (130KB — large) |
| 2026-04-09 | Customer Success System (group) | `1zBnrAlADTvxl5O4rURANRX1mWAp13FFzLMkQZVqYnVY` | Yes (37KB) |
| 2026-04-09 | Craig / Kyle Sync | `1d7DuzusCO0sW2BEgKWZ5Y2eM_dmjEpJtq6VEQ0SL9ao` | Yes |
| 2026-04-01 | Meeting Takeaways -- Kyle + Cam Customer Review | `1zOphTUqy_w87C1EmPWpT3_Uks9dgkmPKoAi8giJMfYI` | Doc only |

### Individual Meetings (relevant context)
| Date | Title | Notes ID | Has Recording |
|------|-------|----------|---------------|
| 2026-04-09 | Peter / Craig | `1zLoZRrc6k01zONpy5Nnf3NfkH-DFPHGXeJv9_e49g9o` | Yes |
| 2026-04-08 | Rem / Craig sync | `1ZfwhDMCAfbkZ0cYNZzFqDCg2vG2YvL9Ang-gEtn_v94` | Yes (44KB — large) |
| 2026-04-10 | Craig / Ryan | `1lzVmPXs6OUnvD1gKhi4msaFilWP_F7ITu7NmL-U0faM` | Yes |
| 2026-04-07 | Ryan / Craig | `1FKs_7LB9iTa-dgQy6r3c5M99TaDootwfhDKsQ3ENOG0` | Yes (217KB — very large) |
| 2026-04-03 | Craig / Ryan | `1PcfBn8Tj9ziLQqNYQGFY4tfI5vEVQuWiFSHAWh2gYik` | Yes |
| 2026-04-10 | O'Connor Insurance | `1kkhoxVaPqDaGm3NFoyrQxRLd9EvyacpmDS6gk3IHTqQ` | Yes |
| 2026-04-13 | Customer Status: CDD | `1BWUAbX4FgjZ-PGwIWrtpL8dr9ObkjCrcR5ZAfwUEZOU` | No |

### Recurring Status Meetings
| Date | Title | Notes ID |
|------|-------|----------|
| 2026-04-13 | Customer Status: CDD | `1BWUAbX4FgjZ-PGwIWrtpL8dr9ObkjCrcR5ZAfwUEZOU` |
| 2026-04-06 | Customer Status: CDD | `1lwkZplXfI5uf74AjCxTh3rUibYk6Gdd2YUUWL4_QDsc` |
| 2026-03-30 | Customer Status: CDD | `1I_Ar8JilUZCEMPOQTMhTR3HbT2riWJuCfgPGd1-WS1A` |

### Other Relevant
| Date | Title | Notes ID |
|------|-------|----------|
| 2026-04-13 | Meeting with Craig Certo (689KB — huge) | `1cV3dRLUZT49dixc7v_j7Fc4ho2QwcUImsUG3XYTqEr0` |
| 2026-04-10 | 101 Weston Accounts Update | `1Rf-aS6X4YlS9n56cwc9eqEZdZjmHyDm0yfBbR166T_8` |
| 2026-04-07 | Cycle retrospective | `1RDArorQ9WyqEXmCPLuIqr0pc_LIuT83ixvxosysTMT4` |
| 2026-04-03 | Craig <> Dhruv | `1onY_xjVz6Lc9SKlDAeTeY_-sFDbTkie12eMBdYqWHXE` |

---

## 7. Not Yet Located

- Craig's direct conversations with **Cam** (no "Craig + Cam" titled meeting found — may be in "Customer Success" group meetings or under different title)
- Craig's direct conversations with **George** (may be participant in group meetings)
- Craig's direct conversations with **Ian** (most recent found is Feb 27)
- Craig's direct conversations with **Ganesh** (likely a Slack/Zoom call, not recorded in Drive)
- **Ganesh's implementation-playbook repo contents** (not yet cloned/read)
