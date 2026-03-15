"""Entity layer CRUD operations.

Entities live exclusively in MongoDB. They have schemas defined in
.registry/types/ and are the deterministic entry points for context assembly.
"""
import re
import sys
from datetime import datetime, timezone

from db import get_collection
from registry import get_registry


def _slugify(text: str) -> str:
    """Convert text to a URL-safe slug for record_id."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def _build_refs_out(entity_type: str, fields: dict, explicit_refs: dict) -> dict:
    """Build refs_out from typed ref fields and explicit --refs.

    Typed refs come from fields that have type=ref or ref_list in the schema.
    Explicit refs come from --refs key:value on the CLI.
    Both are merged into refs_out with list values.
    """
    registry = get_registry()
    ref_fields = registry.get_ref_fields(entity_type)
    refs_out = {}

    # Extract refs from typed fields (schema-defined ref/ref_list fields)
    for field_name, target_type in ref_fields.items():
        value = fields.get(field_name)
        if value:
            if isinstance(value, list):
                refs_out[target_type] = value
            else:
                refs_out.setdefault(target_type, []).append(value)

    # Merge explicit --refs (CLI-provided)
    for key, value in explicit_refs.items():
        if isinstance(value, list):
            refs_out.setdefault(key, []).extend(value)
        else:
            refs_out.setdefault(key, []).append(value)

    return refs_out


def _validate_required(entity_type: str, fields: dict) -> list[str]:
    """Validate that all required fields are present. Returns list of errors."""
    registry = get_registry()
    required = registry.get_required_fields(entity_type)
    errors = []
    for field_name in required:
        if field_name not in fields or not fields[field_name]:
            errors.append(f"Required field missing: {field_name}")
    return errors


def _validate_enum(entity_type: str, fields: dict) -> list[str]:
    """Validate enum fields have allowed values. Returns list of errors."""
    registry = get_registry()
    schema = registry.get_type_schema(entity_type)
    if not schema:
        return []
    errors = []
    for field_name, spec in schema.get("fields", {}).items():
        if isinstance(spec, dict) and spec.get("type") == "enum":
            value = fields.get(field_name)
            if value and value not in spec.get("values", []):
                errors.append(
                    f"Invalid value for {field_name}: '{value}'. "
                    f"Allowed: {spec['values']}"
                )
    return errors


def create_entity(
    entity_type: str,
    title: str,
    refs: dict | None = None,
    tags: list[str] | None = None,
    domains: list[str] | None = None,
    status: str | None = None,
    extra_fields: dict | None = None,
) -> dict:
    """Create a new entity in MongoDB.

    Args:
        entity_type: Registered entity type (person, company, etc.)
        title: Display name / title for the entity
        refs: Explicit references (key:value pairs from --refs)
        tags: Additional tags
        domains: Domain classification
        status: Initial status
        extra_fields: Additional type-specific fields (from --field value CLI args)

    Returns:
        The created record (without _id).
    """
    registry = get_registry()
    coll = get_collection()

    if not registry.is_entity_type(entity_type):
        print(f"Error: '{entity_type}' is not a registered entity type", file=sys.stderr)
        sys.exit(1)

    # Generate record_id from title
    record_id = _slugify(title)

    # Check for duplicates
    if coll.find_one({"record_id": record_id}):
        print(f"Error: record '{record_id}' already exists", file=sys.stderr)
        sys.exit(1)

    # Get display field name from schema
    display_field = registry.get_display_field(entity_type)

    # Build the document
    now = datetime.now(timezone.utc)
    doc = {
        "record_id": record_id,
        "type": entity_type,
        display_field: title,
        "domains": domains or [],
        "tags": tags or [],
        "status": status or "active",
        "created_at": now,
        "updated_at": now,
    }

    # Add extra fields (type-specific: --email, --role, --objective, etc.)
    if extra_fields:
        for key, value in extra_fields.items():
            doc[key] = value

    # Handle list fields that might come as comma-separated strings
    schema = registry.get_type_schema(entity_type)
    if schema:
        for field_name, spec in schema.get("fields", {}).items():
            if isinstance(spec, dict) and spec.get("type") == "list":
                val = doc.get(field_name)
                if isinstance(val, str):
                    doc[field_name] = [v.strip() for v in val.split(",")]

    # Validate required fields
    errors = _validate_required(entity_type, doc)
    if errors:
        for err in errors:
            print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

    # Validate enum fields
    errors = _validate_enum(entity_type, doc)
    if errors:
        for err in errors:
            print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

    # Build refs_out from ref fields + explicit refs
    refs_out = _build_refs_out(entity_type, doc, refs or {})
    if refs_out:
        doc["refs_out"] = refs_out

    # Insert
    coll.insert_one(doc)

    # Return without _id (not JSON serializable)
    doc.pop("_id", None)
    return doc


def get_entity(record_id: str) -> dict | None:
    """Get an entity by record_id."""
    coll = get_collection()
    doc = coll.find_one(
        {"record_id": record_id, "type": {"$ne": "knowledge"}},
        {"_id": 0},
    )
    return doc


def update_entity(
    record_id: str,
    add_tags: list[str] | None = None,
    add_refs: dict | None = None,
    status: str | None = None,
    extra_fields: dict | None = None,
) -> dict:
    """Update an entity in MongoDB.

    Returns the updated record.
    """
    coll = get_collection()

    record = coll.find_one({"record_id": record_id, "type": {"$ne": "knowledge"}})
    if not record:
        print(f"Error: entity '{record_id}' not found", file=sys.stderr)
        sys.exit(1)

    update_ops = {"$set": {"updated_at": datetime.now(timezone.utc)}}

    if status:
        update_ops["$set"]["status"] = status

    # Fields prefixed with add_ are list-append operations
    LIST_APPEND_FIELDS = {"add_sessions": "sessions", "add_artifacts": "artifacts"}

    if extra_fields:
        for key, value in extra_fields.items():
            if key in LIST_APPEND_FIELDS:
                target = LIST_APPEND_FIELDS[key]
                update_ops.setdefault("$addToSet", {})[target] = value
            else:
                update_ops["$set"][key] = value

    if add_tags:
        update_ops.setdefault("$addToSet", {})["tags"] = {"$each": add_tags}

    if add_refs:
        for ref_type, ref_id in add_refs.items():
            key = f"refs_out.{ref_type}"
            update_ops.setdefault("$addToSet", {})[key] = ref_id

    coll.update_one({"record_id": record_id}, update_ops)

    # Return updated record
    return coll.find_one({"record_id": record_id}, {"_id": 0})


def list_entities(
    entity_type: str,
    status: str | None = None,
    domain: str | None = None,
    recent: str | None = None,
    refs_to: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """List entities of a given type with optional filters."""
    coll = get_collection()

    query = {"type": entity_type}

    if status:
        query["status"] = status
    if domain:
        query["domains"] = domain
    if refs_to:
        # Find entities that reference this ID in any refs_out field
        query["$or"] = [
            {f"refs_out.{field}": refs_to}
            for field in ["company", "project", "people", "product",
                          "brand", "platform", "channel", "meeting", "workflow"]
        ]
    if recent:
        from cli import _parse_duration
        seconds = _parse_duration(recent)
        cutoff = datetime.now(timezone.utc).timestamp() - seconds
        cutoff_dt = datetime.fromtimestamp(cutoff, tz=timezone.utc)
        query["updated_at"] = {"$gte": cutoff_dt}

    results = list(
        coll.find(query, {"_id": 0, "content_embedding": 0})
        .sort("updated_at", -1)
        .limit(limit)
    )
    return results


def get_entity_refs(record_id: str) -> dict:
    """Get single-hop references for an entity.

    Returns: {"out": [...], "in": [...]}
    """
    coll = get_collection()
    result = {"out": [], "in": []}

    record = coll.find_one({"record_id": record_id}, {"_id": 0})
    if not record:
        return result

    # Outbound: follow refs_out
    refs_out = record.get("refs_out", {})
    for ref_type, ref_ids in refs_out.items():
        ids = ref_ids if isinstance(ref_ids, list) else [ref_ids]
        for rid in ids:
            ref_record = coll.find_one({"record_id": rid}, {"_id": 0})
            if ref_record:
                result["out"].append(ref_record)

    # Inbound: find records that reference this entity in refs_out
    ref_fields = [
        "refs_out.company", "refs_out.project", "refs_out.people",
        "refs_out.product", "refs_out.brand", "refs_out.platform",
        "refs_out.channel", "refs_out.meeting", "refs_out.workflow",
    ]
    seen = {record_id}
    for field in ref_fields:
        for doc in coll.find({field: record_id}, {"_id": 0}):
            if doc["record_id"] not in seen:
                seen.add(doc["record_id"])
                result["in"].append(doc)

    # Also check wiki_links (knowledge records linking to this entity)
    for doc in coll.find({"wiki_links": record_id}, {"_id": 0}):
        if doc["record_id"] not in seen:
            seen.add(doc["record_id"])
            result["in"].append(doc)

    return result
