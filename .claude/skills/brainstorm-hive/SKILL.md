---
name: brainstorm-hive
description: Extends brainstorming sessions with Hive decision checkpointing. After each validated decision during brainstorming, creates a Hive decision record with rationale and alternatives. Use this skill during design and brainstorming sessions that produce architectural decisions.
user-invocable: false
---

# Brainstorming with Hive Checkpointing

This skill extends brainstorming sessions with systematic decision capture in the Hive. It does NOT replace the brainstorming workflow — it adds checkpointing as a byproduct.

## When to Checkpoint

After each **validated decision** during brainstorming — a decision that has been discussed, alternatives considered, and the user has confirmed the choice. Not every thought or exploration — only resolved decisions.

**Signals a decision has been validated:**
- The user confirms a choice ("yes, let's go with that", "agreed", "that's the approach")
- A trade-off is explicitly resolved
- An alternative is explicitly rejected with reasoning
- A design question gets a definitive answer

## How to Checkpoint

After each validated decision:

```bash
hive create decision "<concise statement of what was decided>" \
  --domains <domain> \
  --refs workflow:<workflow-id>,project:<project-id> \
  --tags brainstorming \
  --rationale "<full reasoning — why this choice, what makes it better>" \
  --alternatives "<what was considered and rejected, comma-separated>"
```

**Example:**
```bash
hive create decision "Use two-layer architecture: entities in MongoDB, knowledge as markdown files" \
  --domains indemn \
  --refs workflow:hive,project:os-development \
  --tags brainstorming,architecture \
  --rationale "Entities need structured queries as starting points for context assembly. Knowledge is prose discovered through traversal and search. Keeping them in separate layers avoids sync complexity." \
  --alternatives "All records as files with MongoDB index, All records in MongoDB only, Flat wiki-style notes without types"
```

## What to Include

- **Rationale:** The full reasoning, not a summary. Why this choice over the alternatives. What constraints drove the decision. What would change if assumptions change.
- **Alternatives:** Every option that was seriously considered. Brief note on why each was rejected.
- **Tags:** Always include `brainstorming`. Add topic tags (e.g., `architecture`, `ui`, `voice`).
- **Refs:** Link to the workflow and project being brainstormed.

## Volume

A good brainstorming session produces 10-20+ decisions. This is normal. Each one is a node in the reasoning trail that future sessions will use for context.

## Integration

This skill is invoked automatically by the code-dev system's design phase. It can also be used standalone during any brainstorming session that produces decisions worth preserving.

The Hive's context assembly will read these decisions (with full rationale and alternatives) when preparing context for future sessions on the same workflow.
