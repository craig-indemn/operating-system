#!/usr/bin/env python3
"""Migrate sample artifacts from projects/*/artifacts/ to Hive knowledge records.

Reads existing artifact frontmatter (ask, created, workstream, session, sources)
and transforms to Hive format (title, tags, domains, refs, status, created).
Does NOT delete or modify originals.
"""
import os
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import HIVE_ROOT, OS_ROOT
from knowledge_ops import _parse_knowledge_file, _index_to_mongodb, _write_knowledge_file
from db import get_collection

# Selected artifacts to migrate (representative sample)
ARTIFACTS = [
    # Designs
    ("projects/audio-transcription/artifacts/2026-02-17-extraction-pipeline-design.md", "design", "indemn"),
    ("projects/gic-observatory/artifacts/2026-02-26-observatory-architecture.md", "design", "indemn"),
    ("projects/os-development/artifacts/2026-02-19-dispatch-system-design.md", "design", "indemn"),
    # Research
    ("projects/analytics-dashboard/artifacts/2026-02-24-research-and-spec-inputs.md", "research", "indemn"),
    ("projects/content-system/artifacts/2026-02-23-writing-psychology-reference.md", "research", "career-catalyst"),
    # Notes
    ("projects/devops/artifacts/2026-03-03-devops-architecture-context.md", "note", "indemn"),
    ("projects/nvidia-inception/artifacts/2026-02-24-indemn-company-intelligence.md", "research", "indemn"),
]


def infer_tags(filename: str, primary_tag: str) -> list[str]:
    """Infer tags from filename and primary tag."""
    tags = [primary_tag]
    name = filename.lower()
    if "architecture" in name:
        tags.append("architecture")
    if "pipeline" in name:
        tags.append("voice")
    if "ui" in name or "dashboard" in name:
        tags.append("ui")
    return tags


def transform_frontmatter(original: dict, primary_tag: str, domain: str, project_name: str) -> dict:
    """Transform artifact frontmatter to Hive format."""
    title = original.get("ask", "")
    if not title:
        # Derive from filename
        title = "Untitled artifact"

    # Truncate very long ask titles
    if len(title) > 120:
        title = title[:117] + "..."

    created = original.get("created", "")
    if hasattr(created, "strftime"):
        created = created.strftime("%Y-%m-%d")
    elif not isinstance(created, str):
        created = str(created)

    tags = [primary_tag]
    if primary_tag == "design":
        tags.append("architecture")

    refs = {"project": project_name}

    return {
        "title": title,
        "tags": tags,
        "domains": [domain],
        "refs": refs,
        "status": "active",
        "created": created,
    }


def migrate():
    coll = get_collection()
    migrated = 0
    skipped = 0

    for rel_path, primary_tag, domain in ARTIFACTS:
        source = OS_ROOT / rel_path
        if not source.exists():
            print(f"  SKIP (not found): {rel_path}")
            skipped += 1
            continue

        # Derive record_id from filename
        record_id = source.stem  # e.g., 2026-02-17-extraction-pipeline-design

        # Check if already migrated
        if coll.find_one({"record_id": record_id}):
            print(f"  EXISTS: {record_id}")
            skipped += 1
            continue

        # Read the original file
        text = source.read_text(encoding="utf-8")

        # Parse frontmatter
        original_fm = {}
        content = text
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                try:
                    original_fm = yaml.safe_load(parts[1]) or {}
                except yaml.YAMLError:
                    pass
                content = parts[2].strip()

        # Determine project from path
        project_name = rel_path.split("/")[1]  # projects/<name>/...

        # Transform frontmatter
        new_fm = transform_frontmatter(original_fm, primary_tag, domain, project_name)

        # Determine target directory from tag
        from config import get_knowledge_dir
        dir_name = get_knowledge_dir(new_fm["tags"])
        target_dir = HIVE_ROOT / dir_name
        target_path = target_dir / f"{record_id}.md"

        # Write the file
        _write_knowledge_file(target_path, new_fm, content)

        # Index to MongoDB
        _index_to_mongodb(record_id, target_path, new_fm, content)

        print(f"  MIGRATED: {record_id} → {dir_name}/")
        migrated += 1

    print(f"\nDone: {migrated} migrated, {skipped} skipped")


if __name__ == "__main__":
    migrate()
