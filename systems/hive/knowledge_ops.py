"""Knowledge layer CRUD operations.

Knowledge records are markdown files with YAML frontmatter, stored in the
hive/ vault directories. MongoDB indexes them (derived) for search.
Files are the source of truth; MongoDB is rebuilt via `hive sync`.
"""
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from config import HIVE_ROOT, get_knowledge_dir
from db import get_collection


def _slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def _generate_record_id(title: str, date: str | None = None) -> str:
    """Generate YYYY-MM-DD-slugified-title record_id for knowledge records."""
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = _slugify(title)
    record_id = f"{date}-{slug}"
    return record_id


def _ensure_unique_id(record_id: str) -> str:
    """Ensure record_id is unique, appending -2, -3 etc. if needed."""
    coll = get_collection()
    if not coll.find_one({"record_id": record_id}):
        return record_id

    counter = 2
    while True:
        candidate = f"{record_id}-{counter}"
        if not coll.find_one({"record_id": candidate}):
            return candidate
        counter += 1


def _extract_wiki_links(content: str) -> list[str]:
    """Extract [[wiki-link]] targets from markdown content."""
    return re.findall(r"\[\[([^\]]+)\]\]", content)


def _build_refs_out(refs: dict) -> dict:
    """Build refs_out from frontmatter refs dict.

    Frontmatter refs look like:
        refs:
          project: hive
          people: [craig, cam]

    Normalized to refs_out with all values as lists.
    """
    refs_out = {}
    for key, value in refs.items():
        if isinstance(value, list):
            refs_out[key] = value
        else:
            refs_out[key] = [value]
    return refs_out


def _build_frontmatter(
    title: str,
    tags: list[str],
    domains: list[str],
    refs: dict,
    status: str,
    created: str,
    extra_fields: dict | None = None,
) -> dict:
    """Build the YAML frontmatter dict for a knowledge record."""
    fm = {
        "title": title,
        "tags": tags,
        "domains": domains,
        "status": status,
        "created": created,
    }
    if refs:
        fm["refs"] = refs
    if extra_fields:
        for k, v in extra_fields.items():
            fm[k] = v
    return fm


def _write_knowledge_file(file_path: Path, frontmatter: dict, body: str):
    """Write a knowledge record as markdown with YAML frontmatter."""
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w") as f:
        f.write("---\n")
        yaml.dump(frontmatter, f, default_flow_style=False, allow_unicode=True,
                  sort_keys=False)
        f.write("---\n\n")
        f.write(f"# {frontmatter['title']}\n\n")
        if body:
            f.write(body)
            if not body.endswith("\n"):
                f.write("\n")


def _parse_knowledge_file(file_path: Path) -> dict | None:
    """Parse a knowledge markdown file into frontmatter + content.

    Returns dict with frontmatter fields + 'content' key, or None on failure.
    """
    try:
        text = file_path.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError):
        return None

    # Split frontmatter from content
    if not text.startswith("---"):
        return None

    parts = text.split("---", 2)
    if len(parts) < 3:
        return None

    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None

    if not isinstance(frontmatter, dict):
        return None

    content = parts[2].strip()
    frontmatter["_content"] = content
    frontmatter["_file_path"] = str(file_path)

    return frontmatter


def _index_to_mongodb(record_id: str, file_path: Path, frontmatter: dict, content: str):
    """Index a knowledge record into MongoDB (upsert)."""
    coll = get_collection()
    now = datetime.now(timezone.utc)

    # Build refs_out from frontmatter refs
    refs = frontmatter.get("refs", {})
    refs_out = _build_refs_out(refs) if refs else {}

    # Extract wiki links
    wiki_links = _extract_wiki_links(content)

    # Parse created date
    created_str = frontmatter.get("created", "")
    if isinstance(created_str, str) and created_str:
        try:
            created_at = datetime.strptime(created_str, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            created_at = now
    elif hasattr(created_str, "isoformat"):
        created_at = created_str
    else:
        created_at = now

    # Relative file path from OS_ROOT
    from config import OS_ROOT
    try:
        rel_path = str(file_path.relative_to(OS_ROOT))
    except ValueError:
        rel_path = str(file_path)

    doc = {
        "record_id": record_id,
        "type": "knowledge",
        "title": frontmatter.get("title", record_id),
        "tags": frontmatter.get("tags", []),
        "domains": frontmatter.get("domains", []),
        "status": frontmatter.get("status", "active"),
        "refs_out": refs_out,
        "wiki_links": wiki_links,
        "content": content,
        "file_path": rel_path,
        "created_at": created_at,
        "updated_at": now,
    }

    # Embed content if possible, otherwise preserve existing embedding
    existing = coll.find_one({"record_id": record_id})
    if existing and "content_embedding" in existing:
        doc["content_embedding"] = existing["content_embedding"]
    elif content:
        try:
            from embed import get_embedding
            embedding = get_embedding(content)
            if embedding:
                doc["content_embedding"] = embedding
        except ImportError:
            pass  # embed module not available

    # Copy extra frontmatter fields (rationale, alternatives, etc.)
    skip_keys = {"title", "tags", "domains", "status", "created", "refs",
                 "_content", "_file_path"}
    for k, v in frontmatter.items():
        if k not in skip_keys and k not in doc:
            doc[k] = v

    coll.update_one(
        {"record_id": record_id},
        {"$set": doc},
        upsert=True,
    )

    return doc


def create_knowledge(
    title: str,
    tags: list[str] | None = None,
    refs: dict | None = None,
    domains: list[str] | None = None,
    status: str | None = None,
    extra_fields: dict | None = None,
    body: str | None = None,
) -> dict:
    """Create a new knowledge record (file + MongoDB index).

    Args:
        title: Record title
        tags: Tags (first tag determines directory)
        refs: References to entities (key:value pairs)
        domains: Domain classification
        status: Initial status
        extra_fields: Additional frontmatter fields (rationale, alternatives, etc.)
        body: Markdown body content

    Returns:
        The indexed record (without _id).
    """
    tags = tags or ["note"]
    domains = domains or []
    refs = refs or {}
    status = status or "active"
    body = body or ""

    # Generate record_id
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    record_id = _generate_record_id(title, today)
    record_id = _ensure_unique_id(record_id)

    # Determine directory from tags
    dir_name = get_knowledge_dir(tags)
    file_dir = HIVE_ROOT / dir_name
    file_path = file_dir / f"{record_id}.md"

    # Check file doesn't already exist
    if file_path.exists():
        print(f"Error: file already exists: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Build frontmatter
    frontmatter = _build_frontmatter(
        title=title,
        tags=tags,
        domains=domains,
        refs=refs,
        status=status,
        created=today,
        extra_fields=extra_fields,
    )

    # Write the file
    _write_knowledge_file(file_path, frontmatter, body)

    # Index to MongoDB
    doc = _index_to_mongodb(record_id, file_path, frontmatter, body)
    doc.pop("_id", None)

    return doc


def get_knowledge(record_id: str) -> dict | None:
    """Get a knowledge record by record_id from MongoDB."""
    coll = get_collection()
    doc = coll.find_one(
        {"record_id": record_id, "type": "knowledge"},
        {"_id": 0, "content_embedding": 0},
    )
    return doc


def update_knowledge(
    record_id: str,
    add_tags: list[str] | None = None,
    add_refs: dict | None = None,
    status: str | None = None,
    extra_fields: dict | None = None,
) -> dict:
    """Update a knowledge record (updates file frontmatter + re-indexes).

    Returns the updated record.
    """
    coll = get_collection()

    record = coll.find_one({"record_id": record_id, "type": "knowledge"})
    if not record:
        print(f"Error: knowledge record '{record_id}' not found", file=sys.stderr)
        sys.exit(1)

    # Read the actual file
    from config import OS_ROOT
    file_path = OS_ROOT / record.get("file_path", "")
    parsed = _parse_knowledge_file(file_path)
    if not parsed:
        print(f"Error: cannot read file for '{record_id}'", file=sys.stderr)
        sys.exit(1)

    content = parsed.pop("_content", "")
    parsed.pop("_file_path", None)

    # Apply updates to frontmatter
    if add_tags:
        existing_tags = parsed.get("tags", [])
        for t in add_tags:
            if t not in existing_tags:
                existing_tags.append(t)
        parsed["tags"] = existing_tags

    if add_refs:
        existing_refs = parsed.get("refs", {})
        for k, v in add_refs.items():
            existing_refs[k] = v
        parsed["refs"] = existing_refs

    if status:
        parsed["status"] = status

    if extra_fields:
        for k, v in extra_fields.items():
            parsed[k] = v

    # Rewrite the file
    _write_knowledge_file(file_path, parsed, content)

    # Re-index to MongoDB
    doc = _index_to_mongodb(record_id, file_path, parsed, content)
    doc.pop("_id", None)

    return doc


def list_knowledge(
    tag: str,
    status: str | None = None,
    domain: str | None = None,
    recent: str | None = None,
    refs_to: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """List knowledge records filtered by tag with optional filters."""
    coll = get_collection()

    query = {"type": "knowledge", "tags": tag}

    if status:
        query["status"] = status
    if domain:
        query["domains"] = domain
    if refs_to:
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
