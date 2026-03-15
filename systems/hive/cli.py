#!/usr/bin/env python3
"""Hive CLI — unified record management for the Indemn Operating System.

Usage: hive <command> [args]

Commands:
    get <id>              Get any record by ID
    create <type> "title" Create a record (entity or knowledge)
    update <id>           Update any record
    search "query"        Semantic + keyword search
    list <type-or-tag>    List records of a type or tag
    refs <id>             Everything referencing this record
    recent [duration]     Recent activity feed
    sync [system]         Sync operations
    feedback "message"    Self-improvement signal
    status                System overview
    init                  Initialize vault, MongoDB, seed registry
    types list|show       Entity type registry
    tags list             Knowledge tag registry
    domains list          Domain registry
    archive               Bulk archive stale records
    health                Graph health report
    ontology check|usage  Ontology analysis and management
    discover              Cross-domain connection discovery
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

# Ensure the hive system directory is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from registry import get_registry
from db import get_collection, check_connection
from config import HIVE_ROOT, MONGO_URI, MONGO_DB


def is_interactive() -> bool:
    """Check if stdout is a terminal (not piped)."""
    return sys.stdout.isatty()


def output(data, format_override=None):
    """Output data in the appropriate format.

    JSON when piped, text when interactive. format_override takes precedence.
    """
    fmt = format_override or ("text" if is_interactive() else "json")

    if fmt == "json":
        if isinstance(data, list):
            print(json.dumps(data, indent=2, default=str))
        elif isinstance(data, dict):
            print(json.dumps(data, indent=2, default=str))
        else:
            print(json.dumps({"message": str(data)}, default=str))
    elif fmt == "md":
        _output_markdown(data)
    else:
        _output_text(data)


def _output_text(data):
    """Format data as human-readable text."""
    if isinstance(data, str):
        print(data)
    elif isinstance(data, dict):
        _print_record_text(data)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                _print_record_text(item)
                print()
            else:
                print(item)
    else:
        print(str(data))


def _output_markdown(data):
    """Format data as markdown."""
    if isinstance(data, str):
        print(data)
    elif isinstance(data, dict):
        _print_record_md(data)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                _print_record_md(item)
                print()


def _print_record_text(record: dict):
    """Print a single record in text format."""
    rec_type = record.get("type", "unknown")
    record_id = record.get("record_id", "?")
    layer = "entity" if rec_type != "knowledge" else "knowledge"

    # Get display value
    title = record.get("title") or record.get("name") or record_id

    # Layer indicator
    if layer == "knowledge":
        tags = record.get("tags", [])
        kind = tags[0] if tags else "note"
        label = f"[knowledge:{kind}]"
    else:
        label = f"[entity:{rec_type}]"

    print(f"{label} {title} ({record_id})")

    # Status and domains
    status = record.get("status", "")
    domains = record.get("domains", [])
    if status or domains:
        parts = []
        if status:
            parts.append(f"status: {status}")
        if domains:
            parts.append(f"domains: {', '.join(domains)}")
        print(f"  {' | '.join(parts)}")

    # Tags (for knowledge records)
    tags = record.get("tags", [])
    if tags and layer == "knowledge":
        print(f"  tags: {', '.join(tags)}")

    # Key fields based on type
    for field in ("objective", "email", "role", "industry", "summary",
                   "current_context", "description"):
        val = record.get(field)
        if val:
            # Truncate long values
            display_val = val if len(val) <= 120 else val[:117] + "..."
            print(f"  {field}: {display_val}")

    # Refs
    refs_out = record.get("refs_out", {})
    if refs_out:
        ref_parts = []
        for k, v in refs_out.items():
            if isinstance(v, list):
                ref_parts.append(f"{k}: {', '.join(v)}")
            else:
                ref_parts.append(f"{k}: {v}")
        print(f"  refs: {'; '.join(ref_parts)}")

    # Timestamps
    updated = record.get("updated_at")
    if updated:
        if isinstance(updated, datetime):
            print(f"  updated: {updated.strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"  updated: {updated}")


def _print_record_md(record: dict):
    """Print a single record in markdown format."""
    title = record.get("title") or record.get("name") or record.get("record_id", "?")
    print(f"## {title}")
    print()
    for k, v in record.items():
        if k in ("_id", "content_embedding"):
            continue
        if k == "content":
            print(f"### Content\n{v}\n")
        else:
            print(f"- **{k}:** {v}")
    print()


# ─── Command handlers ───────────────────────────────────────────────

def cmd_get(args):
    """Get any record by ID."""
    try:
        from records import get_record
    except ImportError:
        print("Error: records module not available", file=sys.stderr)
        sys.exit(1)

    record = get_record(args.id)
    if not record:
        print(f"Record not found: {args.id}", file=sys.stderr)
        sys.exit(1)

    # Filter fields if requested
    if args.fields:
        fields = [f.strip() for f in args.fields.split(",")]
        record = {k: v for k, v in record.items() if k in fields}

    output(record, args.format)


def cmd_create(args):
    """Create a record (entity or knowledge based on type-or-tag routing)."""
    registry = get_registry()

    type_or_tag = args.type_or_tag

    # Parse --refs key:value,key:value
    refs = {}
    if args.refs:
        for pair in args.refs.split(","):
            if ":" in pair:
                k, v = pair.split(":", 1)
                k = k.strip()
                v = v.strip()
                if k in refs:
                    if isinstance(refs[k], list):
                        refs[k].append(v)
                    else:
                        refs[k] = [refs[k], v]
                else:
                    refs[k] = v

    # Parse --tags
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []

    # Parse --domains
    domains = [d.strip() for d in args.domains.split(",")] if args.domains else []

    # Route based on type or tag
    if registry.is_entity_type(type_or_tag):
        try:
            from entity_ops import create_entity
        except ImportError:
            print("Error: entity_ops module not yet implemented", file=sys.stderr)
            sys.exit(1)
        result = create_entity(
            entity_type=type_or_tag,
            title=args.title,
            refs=refs,
            tags=tags,
            domains=domains,
            status=args.status,
            extra_fields=args.extra,
        )
        output(result, args.format)

    elif registry.is_known_tag(type_or_tag):
        try:
            from knowledge_ops import create_knowledge
        except ImportError:
            print("Error: knowledge_ops module not yet implemented", file=sys.stderr)
            sys.exit(1)
        # Add the type_or_tag as primary tag
        if type_or_tag not in tags:
            tags.insert(0, type_or_tag)
        result = create_knowledge(
            title=args.title,
            tags=tags,
            refs=refs,
            domains=domains,
            status=args.status,
            extra_fields=args.extra,
            body=args.body,
        )
        output(result, args.format)

    else:
        print(
            f"Error: '{type_or_tag}' is not a registered entity type or knowledge tag.",
            file=sys.stderr,
        )
        print(f"Entity types: {', '.join(sorted(registry.get_all_types().keys()))}", file=sys.stderr)
        print(f"Knowledge tags: {', '.join(sorted(registry.get_all_tags().keys()))}", file=sys.stderr)
        sys.exit(1)


def cmd_update(args):
    """Update any record."""
    try:
        from records import get_record
    except ImportError:
        print("Error: records module not available", file=sys.stderr)
        sys.exit(1)

    record = get_record(args.id)
    if not record:
        print(f"Record not found: {args.id}", file=sys.stderr)
        sys.exit(1)

    rec_type = record.get("type", "")

    if rec_type == "knowledge":
        try:
            from knowledge_ops import update_knowledge
        except ImportError:
            print("Error: knowledge_ops module not yet implemented", file=sys.stderr)
            sys.exit(1)
        result = update_knowledge(
            record_id=args.id,
            add_tags=[t.strip() for t in args.add_tags.split(",")] if args.add_tags else None,
            add_refs=_parse_refs(args.add_refs) if args.add_refs else None,
            status=args.status,
            extra_fields=args.extra,
        )
    else:
        try:
            from entity_ops import update_entity
        except ImportError:
            print("Error: entity_ops module not yet implemented", file=sys.stderr)
            sys.exit(1)
        result = update_entity(
            record_id=args.id,
            add_tags=[t.strip() for t in args.add_tags.split(",")] if args.add_tags else None,
            add_refs=_parse_refs(args.add_refs) if args.add_refs else None,
            status=args.status,
            extra_fields=args.extra,
        )

    output(result, args.format)


def cmd_search(args):
    """Semantic + keyword search."""
    try:
        from search import search_records
    except ImportError:
        print("Error: search module not yet implemented", file=sys.stderr)
        sys.exit(1)

    results = search_records(
        query=args.query,
        tags=[t.strip() for t in args.tags.split(",")] if args.tags else None,
        domains=[d.strip() for d in args.domains.split(",")] if args.domains else None,
        types=[t.strip() for t in args.types.split(",")] if args.types else None,
        recent=args.recent,
        limit=args.limit,
        knowledge_only=args.knowledge_only,
        entities_only=args.entities_only,
    )
    output(results, args.format)


def cmd_list(args):
    """List records of a type or tag."""
    registry = get_registry()

    type_or_tag = args.type_or_tag

    if registry.is_entity_type(type_or_tag):
        try:
            from entity_ops import list_entities
        except ImportError:
            print("Error: entity_ops module not yet implemented", file=sys.stderr)
            sys.exit(1)
        results = list_entities(
            entity_type=type_or_tag,
            status=args.status,
            domain=args.domain,
            recent=args.recent,
            refs_to=args.refs_to,
            limit=args.limit,
        )
    elif registry.is_known_tag(type_or_tag):
        try:
            from knowledge_ops import list_knowledge
        except ImportError:
            print("Error: knowledge_ops module not yet implemented", file=sys.stderr)
            sys.exit(1)
        results = list_knowledge(
            tag=type_or_tag,
            status=args.status,
            domain=args.domain,
            recent=args.recent,
            refs_to=args.refs_to,
            limit=args.limit,
        )
    else:
        print(
            f"Error: '{type_or_tag}' is not a registered entity type or knowledge tag.",
            file=sys.stderr,
        )
        sys.exit(1)

    output(results, args.format)


def cmd_refs(args):
    """Show everything referencing this record."""
    try:
        from records import get_refs
    except ImportError:
        print("Error: records module not available", file=sys.stderr)
        sys.exit(1)

    refs = get_refs(
        record_id=args.id,
        direction=args.direction,
        depth=args.depth,
    )

    if is_interactive() and not args.format:
        record = get_collection().find_one({"record_id": args.id}, {"_id": 0})
        if record:
            title = record.get("title") or record.get("name") or args.id
            print(f"References for: {title} ({args.id})")
            print()

        if refs["out"]:
            print(f"─── Outbound ({len(refs['out'])}) ───")
            for r in refs["out"]:
                _print_record_text(r)
                print()

        if refs["in"]:
            print(f"─── Inbound ({len(refs['in'])}) ───")
            for r in refs["in"]:
                _print_record_text(r)
                print()

        if not refs["out"] and not refs["in"]:
            print("No references found.")
    else:
        output(refs, args.format)


def cmd_recent(args):
    """Recent activity feed."""
    try:
        from records import get_record
    except ImportError:
        pass

    coll = get_collection()

    # Parse duration
    duration = args.duration or "7d"
    seconds = _parse_duration(duration)
    cutoff = datetime.now(timezone.utc).timestamp() - seconds
    cutoff_dt = datetime.fromtimestamp(cutoff, tz=timezone.utc)

    query = {"updated_at": {"$gte": cutoff_dt}}

    # Optional filters
    if args.types:
        type_list = [t.strip() for t in args.types.split(",")]
        query["type"] = {"$in": type_list}
    if args.domains:
        domain_list = [d.strip() for d in args.domains.split(",")]
        query["domains"] = {"$in": domain_list}

    limit = args.limit or 20
    results = list(
        coll.find(query, {"_id": 0, "content_embedding": 0})
        .sort("updated_at", -1)
        .limit(limit)
    )

    output(results, args.format)


def cmd_sync(args):
    """Sync operations."""
    system = args.system

    if system is None:
        # Default: re-index knowledge files
        try:
            from sync_core import sync_knowledge_files
        except ImportError:
            print("Error: sync_core module not yet implemented", file=sys.stderr)
            sys.exit(1)
        result = sync_knowledge_files(
            re_embed=args.re_embed,
            no_embed=args.no_embed,
        )
        output(result)
    else:
        # Route to sync adapter
        try:
            from sync_core import sync_system
        except ImportError:
            print("Error: sync_core module not yet implemented", file=sys.stderr)
            sys.exit(1)
        result = sync_system(system)
        output(result)


def cmd_feedback(args):
    """Self-improvement signal."""
    try:
        from feedback_cmd import create_feedback
    except ImportError:
        print("Error: feedback_cmd module not yet implemented", file=sys.stderr)
        sys.exit(1)

    result = create_feedback(args.message)
    output(result)


def cmd_status(args):
    """System overview."""
    coll = get_collection()

    # MongoDB status
    connected = check_connection()
    if not connected:
        print("MongoDB: NOT CONNECTED", file=sys.stderr)
        sys.exit(1)

    # Count by type
    pipeline = [{"$group": {"_id": "$type", "count": {"$sum": 1}}}]
    type_counts = {r["_id"]: r["count"] for r in coll.aggregate(pipeline)}

    # Count by domain
    pipeline = [{"$unwind": "$domains"}, {"$group": {"_id": "$domains", "count": {"$sum": 1}}}]
    domain_counts = {r["_id"]: r["count"] for r in coll.aggregate(pipeline)}

    # Count by status
    pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]
    status_counts = {r["_id"]: r["count"] for r in coll.aggregate(pipeline)}

    total = coll.count_documents({})

    status_data = {
        "mongodb": f"connected ({MONGO_URI}/{MONGO_DB})",
        "total_records": total,
        "by_type": type_counts,
        "by_domain": domain_counts,
        "by_status": status_counts,
    }

    if is_interactive() and not args.format:
        print(f"Hive Status")
        print(f"  MongoDB: connected ({MONGO_URI}/{MONGO_DB})")
        print(f"  Total records: {total}")
        print()
        if type_counts:
            print("  By type:")
            for t, c in sorted(type_counts.items()):
                print(f"    {t}: {c}")
        if domain_counts:
            print("  By domain:")
            for d, c in sorted(domain_counts.items()):
                print(f"    {d}: {c}")
        if status_counts:
            print("  By status:")
            for s, c in sorted(status_counts.items()):
                print(f"    {s or '(none)'}: {c}")
    else:
        output(status_data, args.format)


def cmd_init(args):
    """Initialize vault, MongoDB, seed registry."""
    # Verify MongoDB
    if not check_connection():
        print("Error: MongoDB not reachable. Run: brew services start mongodb-community", file=sys.stderr)
        sys.exit(1)

    print("MongoDB: connected")

    # Verify indexes
    coll = get_collection()
    indexes = coll.index_information()
    print(f"Indexes: {len(indexes)}")

    # Verify vault directories
    from config import HIVE_ROOT
    dirs = ["notes", "decisions", "designs", "research", "sessions",
            ".registry", ".registry/types", ".templates", ".attachments", ".synced"]
    for d in dirs:
        p = HIVE_ROOT / d
        if not p.exists():
            p.mkdir(parents=True)
            print(f"  Created: {d}")
        else:
            print(f"  OK: {d}")

    # Run knowledge sync if available
    try:
        from sync_core import sync_knowledge_files
        result = sync_knowledge_files(no_embed=True)
        print(f"Sync: {result}")
    except ImportError:
        print("Sync: skipped (sync_core not yet available)")

    print("\nHive initialized.")


def cmd_types(args):
    """Entity type registry commands."""
    registry = get_registry()

    if args.types_cmd == "list":
        types = registry.get_all_types()
        if is_interactive() and not args.format:
            print("Entity Types:")
            for name, schema in sorted(types.items()):
                fields = schema.get("fields", {})
                required = [n for n, s in fields.items()
                            if isinstance(s, dict) and s.get("required")]
                print(f"  {name} ({len(fields)} fields, required: {', '.join(required) or 'none'})")
        else:
            output(types, args.format)

    elif args.types_cmd == "show":
        if not args.type_name:
            print("Error: specify a type name", file=sys.stderr)
            sys.exit(1)
        schema = registry.get_type_schema(args.type_name)
        if not schema:
            print(f"Error: type '{args.type_name}' not found", file=sys.stderr)
            sys.exit(1)
        output(schema, args.format)

    else:
        print("Usage: hive types list | hive types show <type>", file=sys.stderr)


def cmd_tags(args):
    """Knowledge tag registry."""
    registry = get_registry()
    tags = registry.get_all_tags()

    if is_interactive() and not args.format:
        print("Knowledge Tags:")
        # Group by category
        by_cat = {}
        for name, info in tags.items():
            cat = info.get("category", "other")
            by_cat.setdefault(cat, []).append((name, info.get("description", "")))
        for cat in sorted(by_cat.keys()):
            print(f"\n  [{cat}]")
            for name, desc in sorted(by_cat[cat]):
                print(f"    {name}: {desc}")
    else:
        output(tags, args.format)


def cmd_domains(args):
    """Domain registry."""
    registry = get_registry()
    domains = registry.get_domains()

    if is_interactive() and not args.format:
        print("Domains:")
        for name, info in sorted(domains.items()):
            desc = info.get("description", "")
            print(f"  {name}: {desc}")
    else:
        output(domains, args.format)


# ─── Phase 5: Graph Quality + Ontology ────────────────────────────────


def cmd_archive(args):
    """Bulk archive stale records."""
    coll = get_collection()
    stale_days = args.days
    cutoff = datetime.now(timezone.utc) - __import__("datetime").timedelta(days=stale_days)
    dry_run = args.dry_run

    # Find candidates: active/backlog records not updated since cutoff
    query = {
        "status": {"$in": ["active", "backlog", "ideating"]},
        "updated_at": {"$lt": cutoff},
    }

    if args.type:
        query["type"] = args.type
    if args.domain:
        query["domains"] = args.domain

    candidates = list(coll.find(query).sort("updated_at", 1))

    if not candidates:
        result = {"archived": 0, "message": f"No stale records older than {stale_days} days"}
        if is_interactive() and not args.format:
            print(f"No stale records found (cutoff: {stale_days} days)")
        else:
            output(result, args.format)
        return

    if dry_run:
        records = []
        for r in candidates:
            age_days = (datetime.now(timezone.utc) - r.get("updated_at", cutoff)).days
            records.append({
                "record_id": r["record_id"],
                "type": r["type"],
                "name": r.get("name", r.get("title", "")),
                "status": r["status"],
                "age_days": age_days,
            })
        result = {"would_archive": len(records), "records": records}
        if is_interactive() and not args.format:
            print(f"Would archive {len(records)} stale records (dry run):")
            for rec in records:
                print(f"  {rec['record_id']} ({rec['type']}) — {rec['age_days']}d stale")
        else:
            output(result, args.format)
        return

    # Actually archive
    result = coll.update_many(
        {"_id": {"$in": [r["_id"] for r in candidates]}},
        {"$set": {"status": "archived", "updated_at": datetime.now(timezone.utc)}},
    )
    archived_count = result.modified_count

    result_data = {"archived": archived_count, "cutoff_days": stale_days}
    if is_interactive() and not args.format:
        print(f"Archived {archived_count} stale records (older than {stale_days} days)")
    else:
        output(result_data, args.format)


def cmd_health(args):
    """Graph health report — stale records, orphans, coverage."""
    coll = get_collection()
    from datetime import timedelta

    now = datetime.now(timezone.utc)
    total = coll.count_documents({})

    # Stale: active/backlog not updated in 60+ days
    stale_cutoff = now - timedelta(days=60)
    stale_count = coll.count_documents({
        "status": {"$in": ["active", "backlog", "ideating"]},
        "updated_at": {"$lt": stale_cutoff},
    })

    # Recently active (7 days)
    recent_cutoff = now - timedelta(days=7)
    recent_count = coll.count_documents({"updated_at": {"$gte": recent_cutoff}})

    # Orphan entities: no inbound refs from any other record
    all_entity_ids = set()
    referenced_ids = set()
    for r in coll.find({"type": {"$ne": "knowledge"}}, {"record_id": 1, "refs_out": 1}):
        all_entity_ids.add(r["record_id"])
        for ref_list in (r.get("refs_out") or {}).values():
            if isinstance(ref_list, list):
                referenced_ids.update(ref_list)
            elif isinstance(ref_list, str):
                referenced_ids.add(ref_list)
    # Also check knowledge refs
    for r in coll.find({"type": "knowledge"}, {"refs_out": 1}):
        for ref_list in (r.get("refs_out") or {}).values():
            if isinstance(ref_list, list):
                referenced_ids.update(ref_list)
            elif isinstance(ref_list, str):
                referenced_ids.add(ref_list)
    orphan_ids = all_entity_ids - referenced_ids
    orphan_count = len(orphan_ids)

    # Status distribution
    pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]
    status_dist = {r["_id"] or "(none)": r["count"] for r in coll.aggregate(pipeline)}

    # Records without domains
    no_domain = coll.count_documents({"$or": [{"domains": {"$exists": False}}, {"domains": []}]})

    # Records without tags (knowledge only)
    no_tags = coll.count_documents({
        "type": "knowledge",
        "$or": [{"tags": {"$exists": False}}, {"tags": []}],
    })

    health = {
        "total_records": total,
        "recently_active_7d": recent_count,
        "stale_60d": stale_count,
        "orphan_entities": orphan_count,
        "no_domains": no_domain,
        "no_tags_knowledge": no_tags,
        "status_distribution": status_dist,
        "health_score": _compute_health_score(total, stale_count, orphan_count, no_domain),
    }

    if is_interactive() and not args.format:
        score = health["health_score"]
        emoji = "●" if score >= 80 else ("◐" if score >= 50 else "○")
        print(f"Graph Health: {emoji} {score}/100")
        print(f"  Total records: {total}")
        print(f"  Recently active (7d): {recent_count}")
        print(f"  Stale (60d+ inactive): {stale_count}")
        print(f"  Orphan entities (no inbound refs): {orphan_count}")
        print(f"  Missing domains: {no_domain}")
        print(f"  Knowledge without tags: {no_tags}")
        if stale_count > 0:
            print(f"\n  Recommendation: Run 'hive archive --days 60 --dry-run' to review stale records")
        if orphan_count > 0:
            top_orphans = list(orphan_ids)[:5]
            print(f"\n  Top orphan entities: {', '.join(top_orphans)}")
    else:
        output(health, args.format)


def _compute_health_score(total: int, stale: int, orphans: int, no_domain: int) -> int:
    """Compute a 0-100 health score for the graph."""
    if total == 0:
        return 100
    score = 100
    # Penalize for stale records (up to -30)
    stale_pct = stale / total
    score -= min(30, int(stale_pct * 100))
    # Penalize for orphans (up to -20)
    orphan_pct = orphans / max(total, 1)
    score -= min(20, int(orphan_pct * 100))
    # Penalize for missing domains (up to -15)
    no_domain_pct = no_domain / total
    score -= min(15, int(no_domain_pct * 50))
    return max(0, score)


def cmd_ontology(args):
    """Ontology management — analyze tag usage, detect drift, suggest merges."""
    coll = get_collection()
    registry = get_registry()

    if args.ontology_cmd == "check":
        _ontology_check(coll, registry, args)
    elif args.ontology_cmd == "usage":
        _ontology_usage(coll, registry, args)
    else:
        print("Usage: hive ontology check | hive ontology usage", file=sys.stderr)


def _ontology_check(coll, registry, args):
    """Check ontology health — unused tags, frequent unregistered tags, potential merges."""
    all_tags = set(registry.get_all_tags().keys())

    # Count actual tag usage
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    tag_usage = {r["_id"]: r["count"] for r in coll.aggregate(pipeline)}
    used_tags = set(tag_usage.keys())

    # Registered but never used
    unused_registered = all_tags - used_tags

    # Used but not registered
    unregistered_used = used_tags - all_tags

    # Rarely used (1-2 occurrences) — candidates for merge or removal
    rare_tags = {t: c for t, c in tag_usage.items() if c <= 2 and t in all_tags}

    # Simple similarity check for potential merges
    merge_suggestions = []
    tag_list = sorted(all_tags)
    for i, t1 in enumerate(tag_list):
        for t2 in tag_list[i + 1:]:
            # Check if tags are substrings of each other or very similar
            if t1 in t2 or t2 in t1:
                merge_suggestions.append({
                    "tags": [t1, t2],
                    "reason": "substring match",
                    "usage": [tag_usage.get(t1, 0), tag_usage.get(t2, 0)],
                })

    result = {
        "registered_tags": len(all_tags),
        "used_tags": len(used_tags),
        "unused_registered": sorted(unused_registered),
        "unregistered_used": sorted(unregistered_used),
        "rare_tags": rare_tags,
        "merge_suggestions": merge_suggestions,
    }

    if is_interactive() and not args.format:
        print("Ontology Health Check")
        print(f"  Registered tags: {len(all_tags)}")
        print(f"  Tags in use: {len(used_tags)}")

        if unused_registered:
            print(f"\n  Unused registered tags ({len(unused_registered)}):")
            for t in sorted(unused_registered):
                print(f"    - {t}")

        if unregistered_used:
            print(f"\n  Unregistered tags in use ({len(unregistered_used)}):")
            for t in sorted(unregistered_used):
                print(f"    - {t} (used {tag_usage[t]}x)")

        if rare_tags:
            print(f"\n  Rarely used tags (≤2 uses):")
            for t, c in sorted(rare_tags.items()):
                print(f"    - {t}: {c} use{'s' if c != 1 else ''}")

        if merge_suggestions:
            print(f"\n  Potential merges:")
            for s in merge_suggestions:
                print(f"    - {s['tags'][0]} ↔ {s['tags'][1]} ({s['reason']})")
    else:
        output(result, args.format)


def _ontology_usage(coll, registry, args):
    """Show tag usage statistics."""
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    tag_usage = list(coll.aggregate(pipeline))

    if is_interactive() and not args.format:
        print("Tag Usage:")
        for r in tag_usage:
            bar = "█" * min(r["count"], 40)
            print(f"  {r['_id']:25s} {r['count']:4d} {bar}")
    else:
        output([{"tag": r["_id"], "count": r["count"]} for r in tag_usage], args.format)


def cmd_discover(args):
    """Cross-domain discovery — find connections across domain boundaries."""
    coll = get_collection()

    # Get records from different domains
    domains_pipeline = [
        {"$unwind": "$domains"},
        {"$group": {"_id": "$domains", "records": {"$push": "$record_id"}}},
    ]
    domain_records = {r["_id"]: r["records"] for r in coll.aggregate(domains_pipeline)}

    if len(domain_records) < 2:
        if is_interactive():
            print("Need records in at least 2 domains for cross-domain discovery")
        else:
            output({"connections": [], "message": "insufficient domains"}, args.format)
        return

    # Find records that share refs across domains
    connections = []
    domain_names = list(domain_records.keys())

    for i, d1 in enumerate(domain_names):
        for d2 in domain_names[i + 1:]:
            # Find records in d1 that reference records in d2 (or vice versa)
            d2_ids = set(domain_records[d2])
            for rid in domain_records[d1]:
                rec = coll.find_one({"record_id": rid}, {"refs_out": 1, "type": 1, "name": 1, "title": 1})
                if not rec or not rec.get("refs_out"):
                    continue
                for ref_list in rec["refs_out"].values():
                    targets = ref_list if isinstance(ref_list, list) else [ref_list]
                    for target in targets:
                        if target in d2_ids:
                            connections.append({
                                "from": rid,
                                "from_domain": d1,
                                "to": target,
                                "to_domain": d2,
                                "from_label": rec.get("name", rec.get("title", rid)),
                            })

    # Also try semantic similarity across domains (if embeddings available)
    try:
        from embed import embed_text, cosine_similarity
        # Pick a sample from each domain and compare embeddings
        semantic_connections = []
        for d1_idx, d1 in enumerate(domain_names):
            for d2 in domain_names[d1_idx + 1:]:
                # Get embedded records from each domain
                d1_recs = list(coll.find(
                    {"domains": d1, "content_embedding": {"$exists": True}},
                    {"record_id": 1, "title": 1, "name": 1, "content_embedding": 1},
                ).limit(20))
                d2_recs = list(coll.find(
                    {"domains": d2, "content_embedding": {"$exists": True}},
                    {"record_id": 1, "title": 1, "name": 1, "content_embedding": 1},
                ).limit(20))

                for r1 in d1_recs:
                    for r2 in d2_recs:
                        sim = cosine_similarity(r1["content_embedding"], r2["content_embedding"])
                        if sim > 0.7:  # High similarity threshold
                            semantic_connections.append({
                                "from": r1["record_id"],
                                "from_domain": d1,
                                "to": r2["record_id"],
                                "to_domain": d2,
                                "similarity": round(sim, 3),
                                "from_label": r1.get("name", r1.get("title", r1["record_id"])),
                                "to_label": r2.get("name", r2.get("title", r2["record_id"])),
                            })
        connections.extend(semantic_connections)
    except (ImportError, Exception):
        pass  # Embeddings not available — ref-based connections only

    # Deduplicate
    seen = set()
    unique = []
    for c in connections:
        key = tuple(sorted([c["from"], c["to"]]))
        if key not in seen:
            seen.add(key)
            unique.append(c)

    result = {"connections": unique[:args.limit], "total": len(unique)}

    if is_interactive() and not args.format:
        if not unique:
            print("No cross-domain connections found")
        else:
            print(f"Cross-Domain Connections ({len(unique)} found):")
            for c in unique[:args.limit]:
                sim = f" (similarity: {c['similarity']})" if "similarity" in c else ""
                label = c.get("from_label", c["from"])
                to_label = c.get("to_label", c["to"])
                print(f"  {c['from_domain']}:{label} → {c['to_domain']}:{to_label}{sim}")
    else:
        output(result, args.format)


# ─── Utilities ───────────────────────────────────────────────────────

def _parse_refs(refs_str: str) -> dict:
    """Parse --add-refs key:value,key:value into dict."""
    refs = {}
    if not refs_str:
        return refs
    for pair in refs_str.split(","):
        if ":" in pair:
            k, v = pair.split(":", 1)
            refs[k.strip()] = v.strip()
    return refs


def _parse_duration(duration: str) -> int:
    """Parse duration string (7d, 30d, 3m, 1h) to seconds."""
    if not duration:
        return 7 * 86400  # default 7 days

    unit = duration[-1].lower()
    try:
        value = int(duration[:-1])
    except ValueError:
        return 7 * 86400

    multipliers = {"h": 3600, "d": 86400, "w": 604800, "m": 2592000}
    return value * multipliers.get(unit, 86400)


# ─── Argument parsing ────────────────────────────────────────────────

class ExtraFieldAction(argparse.Action):
    """Collect unknown --field value pairs into a dict."""

    def __call__(self, parser, namespace, values, option_string=None):
        extra = getattr(namespace, "extra", None) or {}
        key = option_string.lstrip("-").replace("-", "_")
        extra[key] = values
        namespace.extra = extra


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hive",
        description="Hive CLI — unified record management for the Indemn Operating System",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # get
    p_get = subparsers.add_parser("get", help="Get any record by ID")
    p_get.add_argument("id", help="Record ID")
    p_get.add_argument("--fields", help="Comma-separated fields to select")
    p_get.add_argument("--format", choices=["json", "text", "md"])

    # create
    p_create = subparsers.add_parser("create", help="Create a record")
    p_create.add_argument("type_or_tag", help="Entity type or knowledge tag")
    p_create.add_argument("title", help="Record title")
    p_create.add_argument("--refs", help="References (key:value,...)")
    p_create.add_argument("--tags", help="Additional tags (comma-separated)")
    p_create.add_argument("--domains", help="Domains (comma-separated)")
    p_create.add_argument("--status", help="Initial status")
    p_create.add_argument("--body", help="Body content (knowledge records)")
    p_create.add_argument("--format", choices=["json", "text", "md"])

    # update
    p_update = subparsers.add_parser("update", help="Update any record")
    p_update.add_argument("id", help="Record ID")
    p_update.add_argument("--add-tags", help="Tags to add (comma-separated)")
    p_update.add_argument("--add-refs", help="Refs to add (key:value,...)")
    p_update.add_argument("--status", help="New status")
    p_update.add_argument("--format", choices=["json", "text", "md"])

    # search
    p_search = subparsers.add_parser("search", help="Semantic + keyword search")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--tags", help="Filter by tags")
    p_search.add_argument("--domains", help="Filter by domains")
    p_search.add_argument("--types", help="Filter by types")
    p_search.add_argument("--recent", help="Time filter (7d, 30d, 3m)")
    p_search.add_argument("--limit", type=int, default=20)
    p_search.add_argument("--knowledge-only", action="store_true")
    p_search.add_argument("--entities-only", action="store_true")
    p_search.add_argument("--format", choices=["json", "text", "md"])

    # list
    p_list = subparsers.add_parser("list", help="List records of a type or tag")
    p_list.add_argument("type_or_tag", help="Entity type or knowledge tag")
    p_list.add_argument("--status", help="Filter by status")
    p_list.add_argument("--domain", help="Filter by domain")
    p_list.add_argument("--recent", help="Time filter (7d, 30d, 3m)")
    p_list.add_argument("--refs-to", help="Filter by reference to entity")
    p_list.add_argument("--limit", type=int, default=50)
    p_list.add_argument("--format", choices=["json", "text", "md"])

    # refs
    p_refs = subparsers.add_parser("refs", help="Everything referencing this record")
    p_refs.add_argument("id", help="Record ID")
    p_refs.add_argument("--types", help="Filter by types")
    p_refs.add_argument("--tags", help="Filter by tags")
    p_refs.add_argument("--direction", choices=["in", "out", "both"], default="both")
    p_refs.add_argument("--depth", type=int, default=1, choices=[1, 2, 3])
    p_refs.add_argument("--recent", help="Time filter")
    p_refs.add_argument("--format", choices=["json", "text", "md"])

    # recent
    p_recent = subparsers.add_parser("recent", help="Recent activity feed")
    p_recent.add_argument("duration", nargs="?", default="7d", help="Duration (default: 7d)")
    p_recent.add_argument("--types", help="Filter by types")
    p_recent.add_argument("--domains", help="Filter by domains")
    p_recent.add_argument("--limit", type=int, default=20)
    p_recent.add_argument("--format", choices=["json", "text", "md"])

    # sync
    p_sync = subparsers.add_parser("sync", help="Sync operations")
    p_sync.add_argument("system", nargs="?", help="System to sync (default: re-index knowledge)")
    p_sync.add_argument("--re-embed", action="store_true", help="Re-generate all embeddings")
    p_sync.add_argument("--no-embed", action="store_true", help="Skip embedding")

    # feedback
    p_feedback = subparsers.add_parser("feedback", help="Self-improvement signal")
    p_feedback.add_argument("message", help="Feedback message")

    # status
    p_status = subparsers.add_parser("status", help="System overview")
    p_status.add_argument("--format", choices=["json", "text", "md"])

    # init
    p_init = subparsers.add_parser("init", help="Initialize vault, MongoDB, seed registry")

    # types
    p_types = subparsers.add_parser("types", help="Entity type registry")
    p_types.add_argument("types_cmd", choices=["list", "show"], help="list or show")
    p_types.add_argument("type_name", nargs="?", help="Type name (for show)")
    p_types.add_argument("--format", choices=["json", "text", "md"])

    # tags
    p_tags = subparsers.add_parser("tags", help="Knowledge tag registry")
    p_tags.add_argument("tags_cmd", nargs="?", default="list", choices=["list"])
    p_tags.add_argument("--format", choices=["json", "text", "md"])

    # domains
    p_domains = subparsers.add_parser("domains", help="Domain registry")
    p_domains.add_argument("domains_cmd", nargs="?", default="list", choices=["list"])
    p_domains.add_argument("--format", choices=["json", "text", "md"])

    # archive (Phase 5)
    p_archive = subparsers.add_parser("archive", help="Bulk archive stale records")
    p_archive.add_argument("--days", type=int, default=60, help="Archive records stale for N days (default: 60)")
    p_archive.add_argument("--type", help="Only archive this entity type")
    p_archive.add_argument("--domain", help="Only archive this domain")
    p_archive.add_argument("--dry-run", action="store_true", help="Show what would be archived without doing it")
    p_archive.add_argument("--format", choices=["json", "text", "md"])

    # health (Phase 5)
    p_health = subparsers.add_parser("health", help="Graph health report")
    p_health.add_argument("--format", choices=["json", "text", "md"])

    # ontology (Phase 5)
    p_ontology = subparsers.add_parser("ontology", help="Ontology management")
    p_ontology.add_argument("ontology_cmd", choices=["check", "usage"], help="check or usage")
    p_ontology.add_argument("--format", choices=["json", "text", "md"])

    # discover (Phase 5)
    p_discover = subparsers.add_parser("discover", help="Cross-domain discovery")
    p_discover.add_argument("--limit", type=int, default=20, help="Max connections to show")
    p_discover.add_argument("--format", choices=["json", "text", "md"])

    return parser


def main():
    parser = build_parser()

    # Handle extra --field value args for create/update
    args, unknown = parser.parse_known_args()
    args.extra = {}
    i = 0
    while i < len(unknown):
        if unknown[i].startswith("--"):
            key = unknown[i].lstrip("-").replace("-", "_")
            if i + 1 < len(unknown) and not unknown[i + 1].startswith("--"):
                args.extra[key] = unknown[i + 1]
                i += 2
            else:
                args.extra[key] = True
                i += 1
        else:
            i += 1

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmd_map = {
        "get": cmd_get,
        "create": cmd_create,
        "update": cmd_update,
        "search": cmd_search,
        "list": cmd_list,
        "refs": cmd_refs,
        "recent": cmd_recent,
        "sync": cmd_sync,
        "feedback": cmd_feedback,
        "status": cmd_status,
        "init": cmd_init,
        "types": cmd_types,
        "tags": cmd_tags,
        "domains": cmd_domains,
        # Phase 5
        "archive": cmd_archive,
        "health": cmd_health,
        "ontology": cmd_ontology,
        "discover": cmd_discover,
    }

    handler = cmd_map.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
