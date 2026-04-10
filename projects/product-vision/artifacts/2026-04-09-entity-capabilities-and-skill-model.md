---
ask: "How do entity methods work without per-org code? How do skills, deterministic logic, and CLI-configurability coexist?"
created: 2026-04-09
workstream: product-vision
session: 2026-04-08-a
sources:
  - type: conversation
    description: "Craig and Claude resolving the skill format question — entity capabilities model"
  - type: artifact
    description: "2026-04-08-primitives-resolved.md, 2026-04-08-actor-references-and-targeting.md"
---

# Entity Capabilities and Skill Model

## The Problem

The OS promises everything is CLI-configurable. An FDE or associate can set up an entire system without writing code. But deterministic business logic (classification rules, fuzzy matching, pattern extraction) needs to execute without wasting LLM processing.

Previous approaches tried and rejected:
- **Custom DSL (GET/CHECK/RUN)**: Doesn't scale with complexity. "Silly to make our own language."
- **Python code as skills**: Requires writing and deploying code per org. Breaks CLI-configurable promise.
- **Embedded code in markdown**: Going against the grain of good software development. Two formats stapled together.
- **Always-LLM with markdown skills**: Wastes LLM processing on deterministic work. Principled objection.

## The Resolution: Kernel Capabilities + Per-Org Configuration + Markdown Skills

### Three Layers

| Layer | What | Format | Varies By |
|-------|------|--------|-----------|
| **Kernel capabilities** | Reusable operations built into the OS | Code (Python, maintained by Indemn/Tier 3 developers) | New capabilities = OS code additions |
| **Per-org configuration** | Rules, thresholds, patterns, mappings | Data (created via CLI, stored as entities) | Per org = CLI configuration |
| **Skills** | How associates orchestrate capabilities | Markdown (read by LLM, readable by humans) | Per associate type |

### How It Works

**Entity methods aren't custom code per entity.** They're kernel capabilities activated on an entity type and configured per org.

**Example: Email classification**

The kernel has an `auto-classify` capability. It evaluates configured rules against entity fields. Any entity can activate it.

```bash
# Activate the capability on the Email entity
indemn entity enable Email auto-classify \
  --evaluates classification-rule \
  --sets-field classification

# Create per-org rules (CLI, no code)
indemn rule create --entity Email --org gic \
  --when "from_address ends_with @usli.com" \
  --then '{"type": "usli_quote", "lob_from": "subject_prefix"}'

indemn rule create --entity Email --org gic \
  --when "from_address ends_with @hiscox.com" \
  --then '{"type": "hiscox_quote"}'

indemn rule create --entity Email --org gic \
  --when "subject matches POL-\\d+" \
  --then '{"type": "servicing_request"}'
```

Now `indemn email classify EMAIL-001 --auto` works:
1. Loads classification rules for this org
2. Evaluates email against each rule
3. If match → applies result → done (no LLM)
4. If no match → returns `needs_reasoning: true`

**The associate's skill stays simple markdown:**

```markdown
# Email Classification

When an email needs classification:
1. `indemn email classify {email.id} --auto`
2. Check the result. If needs_reasoning is true, the configured rules couldn't
   determine the type. Read the email content, attachments, and extraction data.
   Use your judgment to determine the email type and line of business.
3. `indemn email classify {email.id} --type {your_determination} --lob {lob}`
```

The skill doesn't contain classification logic. The kernel capability + org configuration handles the deterministic path. The skill orchestrates and provides the reasoning fallback.

## Kernel Capability Library

The kernel ships with a library of capabilities that any entity can activate:

| Capability | What It Does | Configuration (per org, via CLI) |
|------------|-------------|----------------------------------|
| `auto-classify` | Evaluate rules against entity fields, set classification | Classification rules |
| `fuzzy-search` | Text similarity search with configurable threshold | Target field, threshold, ambiguity gap |
| `pattern-extract` | Extract structured data from text using patterns | Regex patterns, field mappings |
| `stale-check` | Find entities past time/count/value thresholds | Time thresholds, count thresholds |
| `auto-route` | Determine routing/assignment based on field rules | Routing rules |
| `external-sync` | Push/pull entity data to/from external system | Provider config, field mappings |
| `auto-link` | Match entities across types using references/fuzzy match | Reference patterns, match thresholds |
| `rule-evaluate` | Generic rule evaluation — match conditions, return actions | Condition-action rules |

This library grows over time. Each new capability is a code addition to the OS kernel. But **activating and configuring** capabilities is always CLI. No code per entity, no code per org.

## How GIC's Full Pipeline Works in This Model

### Classification (deterministic + reasoning fallback)

**Configuration:**
```bash
indemn entity enable Email auto-classify --evaluates classification-rule --sets-field classification
indemn rule create --entity Email --org gic --when "from_address ends_with @usli.com" --then '{"type": "usli_quote", "lob_from": "subject_prefix"}'
indemn rule create --entity Email --org gic --when "from_address ends_with @hiscox.com" --then '{"type": "hiscox_quote"}'
indemn rule create --entity Email --org gic --when "subject matches POL-\\d+" --then '{"type": "servicing_request"}'
indemn rule create --entity Email --org gic --when "from_address in bind@gicunderwriters.com,backoffice@gicunderwriters.com,csr@gicunderwriters.com" --then '{"type": "gic_internal"}'

indemn lob-mapping create --org gic --prefix MGL --lob general_liability
indemn lob-mapping create --org gic --prefix XPL --lob excess_personal_liability
indemn lob-mapping create --org gic --prefix MSE --lob special_events
```

**Skill (markdown):**
```markdown
# Email Classification
1. `indemn email classify {email.id} --auto`
2. If needs_reasoning, analyze email content and determine type and LOB.
```

**Flow:** Email arrives → associate's watch matches → associate reads skill → calls `classify --auto` → kernel evaluates rules → @usli.com matches → classified deterministically. No LLM needed for the classification itself.

### Submission Linking (deterministic + reasoning fallback)

**Configuration:**
```bash
indemn entity enable Email auto-link --target-entity Submission --evaluates reference-pattern
indemn reference-pattern create --org gic --name usli_ref --regex "[A-Z]{2,3}\\d{3}[A-Z0-9]{3,}"
indemn reference-pattern create --org gic --name gic_number --regex "\\d{6}"
indemn entity enable Submission fuzzy-search --on-field named_insured --threshold 85 --ambiguity-gap 5
```

**Skill (markdown):**
```markdown
# Submission Linking
1. `indemn email link {email.id} --auto`
2. If needs_reasoning, you'll receive candidate matches with similarity scores.
   Evaluate based on name similarity, LOB match, date proximity, and thread context.
   Pick the best match or create a new submission.
```

**Flow:** Email classified → associate calls `link --auto` → kernel extracts references using configured patterns → searches submissions by reference → if found, links (deterministic). If not, fuzzy searches by insured name with configured threshold → if single match, links. If ambiguous → needs_reasoning → LLM picks the best candidate.

### Situation Assessment (mostly reasoning)

**Configuration:**
```bash
indemn entity enable Submission completeness-check --evaluates required-field-rule
indemn required-field-rule create --org gic --lob general_liability --fields "named_insured,effective_date,business_description,revenue,years_in_business"
```

**Skill (markdown):**
```markdown
# Situation Assessment
1. `indemn submission check-completeness {submission.id}`
2. Review all linked emails and extraction data
3. Determine the situation type (new submission, info response, carrier quote, etc.)
4. Assess what's known, what's missing, and what should happen next
5. `indemn assessment create --submission {id} --situation-type {type} --completeness {score} --next-action {action}`
```

**Flow:** More reasoning-heavy. The completeness check is deterministic (kernel capability). But determining situation type and next action requires LLM judgment. The skill is mostly reasoning with one deterministic step.

### Stale Detection (fully deterministic)

**Configuration:**
```bash
indemn entity enable Submission stale-check --when "last_activity_at older_than 7d AND followup_count >= 2" --sets-field is_stale
```

**Scheduled invocation:**
```bash
indemn associate create --name "Stale Checker" --trigger "schedule:0 * * * *" --role stale-checker --skill stale-check.md --mode deterministic
```

**Skill (markdown):**
```markdown
# Stale Submission Check
1. `indemn submission check-stale`
```

**Flow:** Fully deterministic. The kernel capability finds submissions matching the configured thresholds and marks them stale. No LLM needed. The associate is deterministic — reads the skill, executes the one command.

## Creating a New Entity Type (Full Example)

An FDE or associate setting up a new entity type for a customer — all through CLI:

```bash
# 1. Define the entity
indemn entity create Document \
  --fields "name:str, content:text, category:str, source:str, size:int" \
  --state-machine "uploaded,categorized,processed,archived"

# 2. Activate kernel capabilities
indemn entity enable Document auto-classify --evaluates classification-rule --sets-field category
indemn entity enable Document pattern-extract --from-field content

# 3. Configure per-org rules
indemn rule create --entity Document --org gic \
  --when "source contains @usli.com" --then '{"category": "carrier_document"}'
indemn rule create --entity Document --org gic \
  --when "name matches *.pdf AND content contains ACORD" --then '{"category": "application"}'

# 4. Create the role with watches
indemn role create doc-processor --watches "Document:created"

# 5. Create the associate
indemn associate create --name "Doc Processor" --role doc-processor --skill doc-processing.md

# 6. The skill (write a markdown file)
# doc-processing.md:
# 1. `indemn document classify {doc.id} --auto`
# 2. If needs_reasoning, analyze document content...
# 3. `indemn document transition {doc.id} --to categorized`
```

Everything through CLI. No Python code written. No deployment. The kernel capabilities do the deterministic work. The skill handles orchestration and reasoning fallback.

## When a Capability Doesn't Exist

If someone needs a capability the kernel doesn't have — for example, "compare two PDF documents for content overlap" — that's a new kernel capability. An Indemn engineer (or Tier 3 developer) builds it and adds it to the OS.

Once built, it's available to every entity in every org. Activating it is CLI. Configuring it is CLI. Using it in a skill is markdown.

**This is the AWS model:** New services (capabilities) are built by engineers. Using them is configuration + API/CLI. The capability library grows over time, covering more use cases without per-customer code.

## The Complete Stack

```
Skills (markdown)           ← Associate reads, orchestrates, reasons when needed
    ↓ calls
Entity CLI commands         ← `indemn email classify --auto`, `indemn submission search --fuzzy`
    ↓ invokes
Kernel capabilities         ← auto-classify, fuzzy-search, pattern-extract, stale-check (code, universal)
    ↓ parameterized by
Per-org configuration       ← Rules, patterns, thresholds, mappings (data, CLI-created)
    ↓ operates on
Entities                    ← Domain data with structure, state machine, relationships
```

**Skills stay markdown.** Always. They describe orchestration and reasoning.

**Deterministic logic is kernel capabilities.** Universal code, parameterized by per-org configuration.

**Everything is CLI-configurable.** Rules, mappings, thresholds, capabilities, skills, associates, roles, watches. An FDE or associate sets up a new org without writing code.

**The LLM is only invoked when kernel capabilities can't handle it.** The `--auto` pattern: try deterministic rules first, flag for reasoning if insufficient. The cost of LLM processing is proportional to the complexity of edge cases, not the volume of routine work.
