"""Sync core — knowledge file indexing and external system sync routing.

Handles:
- `hive sync` (no args): walk knowledge dirs, parse frontmatter, upsert to MongoDB
- `hive sync <system>`: route to registered sync adapters (Phase 3)
- `hive init`: verify MongoDB, create indexes if missing, run sync
"""
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from config import HIVE_ROOT, KNOWLEDGE_DIRS
from db import get_collection, check_connection


def _derive_record_id(file_path: Path) -> str:
    """Derive record_id from filename (strip .md extension)."""
    return file_path.stem


def sync_knowledge_files(re_embed: bool = False, no_embed: bool = False) -> dict:
    """Walk knowledge directories, parse frontmatter, upsert to MongoDB.

    Args:
        re_embed: Re-generate all embeddings (Phase 2)
        no_embed: Skip embedding entirely

    Returns:
        Summary dict with counts.
    """
    from knowledge_ops import _parse_knowledge_file, _index_to_mongodb

    coll = get_collection()
    stats = {"scanned": 0, "indexed": 0, "errors": 0, "skipped": 0}

    # Collect all unique knowledge dirs
    dirs_to_scan = set()
    for dir_name in KNOWLEDGE_DIRS.values():
        dirs_to_scan.add(HIVE_ROOT / dir_name)

    # Walk each directory
    for knowledge_dir in sorted(dirs_to_scan):
        if not knowledge_dir.exists():
            continue

        for md_file in sorted(knowledge_dir.glob("*.md")):
            stats["scanned"] += 1

            parsed = _parse_knowledge_file(md_file)
            if not parsed:
                print(f"  Warning: could not parse {md_file.name}", file=sys.stderr)
                stats["errors"] += 1
                continue

            content = parsed.pop("_content", "")
            file_path_str = parsed.pop("_file_path", str(md_file))

            record_id = _derive_record_id(md_file)

            try:
                doc = _index_to_mongodb(record_id, md_file, parsed, content)
                stats["indexed"] += 1
                print(f"  Indexed: {record_id}", file=sys.stderr)
            except Exception as e:
                print(f"  Error: {record_id}: {e}", file=sys.stderr)
                stats["errors"] += 1

    # Handle embeddings
    if re_embed and not no_embed:
        try:
            from embed import get_embedding
            _embed_all_knowledge(coll)
        except ImportError:
            print("  Embedding module not available (Phase 2)", file=sys.stderr)
    elif not no_embed:
        # Embed records that don't have embeddings yet
        try:
            from embed import get_embedding
            _embed_missing(coll)
        except ImportError:
            pass  # Silently skip — embedding is Phase 2

    # Clean up orphaned records (in MongoDB but file deleted)
    _clean_orphans(coll)

    return stats


def _embed_all_knowledge(coll):
    """Re-embed all knowledge records."""
    from embed import get_embedding

    records = list(coll.find({"type": "knowledge"}, {"record_id": 1, "content": 1}))
    total = len(records)
    for i, rec in enumerate(records, 1):
        content = rec.get("content", "")
        if content:
            print(f"  Embedding {i}/{total} records...", file=sys.stderr)
            embedding = get_embedding(content)
            if embedding:
                coll.update_one(
                    {"record_id": rec["record_id"]},
                    {"$set": {"content_embedding": embedding}},
                )


def _embed_missing(coll):
    """Embed knowledge records that lack embeddings."""
    from embed import get_embedding

    records = list(coll.find(
        {"type": "knowledge", "content_embedding": {"$exists": False}},
        {"record_id": 1, "content": 1},
    ))
    if not records:
        return

    total = len(records)
    for i, rec in enumerate(records, 1):
        content = rec.get("content", "")
        if content:
            print(f"  Embedding {i}/{total} records...", file=sys.stderr)
            embedding = get_embedding(content)
            if embedding:
                coll.update_one(
                    {"record_id": rec["record_id"]},
                    {"$set": {"content_embedding": embedding}},
                )


def _clean_orphans(coll):
    """Remove knowledge records from MongoDB whose files no longer exist."""
    from config import OS_ROOT

    knowledge_records = list(coll.find(
        {"type": "knowledge"},
        {"record_id": 1, "file_path": 1},
    ))

    for rec in knowledge_records:
        file_path = rec.get("file_path", "")
        if file_path:
            full_path = OS_ROOT / file_path
            if not full_path.exists():
                coll.delete_one({"record_id": rec["record_id"]})
                print(f"  Cleaned orphan: {rec['record_id']}", file=sys.stderr)


def list_adapters() -> list[str]:
    """List available sync adapter names."""
    from config import HIVE_SYSTEM_ROOT
    adapters_dir = HIVE_SYSTEM_ROOT / "sync_adapters"
    if not adapters_dir.exists():
        return []
    return [
        f.stem for f in sorted(adapters_dir.iterdir())
        if f.suffix == ".py" and f.stem not in ("__init__", "base")
    ]


def sync_system(system_name: str) -> dict:
    """Route sync to a registered system adapter."""
    try:
        adapter_module = __import__(f"sync_adapters.{system_name}", fromlist=[system_name])
        adapter = adapter_module.get_adapter()
        return adapter.sync()
    except ImportError:
        available = list_adapters()
        print(f"Error: no sync adapter for '{system_name}'", file=sys.stderr)
        if available:
            print(f"Available: {', '.join(available)}", file=sys.stderr)
        else:
            print("No adapters installed.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error syncing {system_name}: {e}", file=sys.stderr)
        sys.exit(1)
