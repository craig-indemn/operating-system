"""Hive search — semantic + keyword search across both layers.

Combines embedding-based semantic search (knowledge records) with MongoDB
$text keyword search, applies filters, deduplicates, and ranks by combined score.
"""
import sys
from datetime import datetime, timezone

from db import get_collection


def _parse_duration(duration: str) -> int:
    """Parse duration string to seconds."""
    if not duration:
        return 0
    unit = duration[-1].lower()
    try:
        value = int(duration[:-1])
    except ValueError:
        return 0
    multipliers = {"h": 3600, "d": 86400, "w": 604800, "m": 2592000}
    return value * multipliers.get(unit, 86400)


def search_records(
    query: str,
    tags: list[str] | None = None,
    domains: list[str] | None = None,
    types: list[str] | None = None,
    recent: str | None = None,
    limit: int = 20,
    knowledge_only: bool = False,
    entities_only: bool = False,
) -> list[dict]:
    """Search across both entity and knowledge layers.

    1. Semantic search: embed query, cosine similarity against knowledge embeddings
    2. Keyword search: MongoDB $text search across title + content
    3. Entity search: text search on entity name/title fields
    4. Merge, deduplicate, rank by combined score
    """
    coll = get_collection()
    results = {}  # record_id → {record, score}

    # Build base filter
    base_filter = {}
    if tags:
        base_filter["tags"] = {"$in": tags}
    if domains:
        base_filter["domains"] = {"$in": domains}
    if recent:
        seconds = _parse_duration(recent)
        if seconds > 0:
            cutoff = datetime.now(timezone.utc).timestamp() - seconds
            cutoff_dt = datetime.fromtimestamp(cutoff, tz=timezone.utc)
            base_filter["updated_at"] = {"$gte": cutoff_dt}

    # ─── Semantic search (knowledge only) ───
    if not entities_only:
        try:
            from embed import get_embedding, cosine_similarity

            query_embedding = get_embedding(query)
            if query_embedding:
                # Fetch all knowledge records with embeddings
                knowledge_filter = {"type": "knowledge", "content_embedding": {"$exists": True}}
                knowledge_filter.update(base_filter)

                knowledge_records = list(coll.find(
                    knowledge_filter,
                    {"_id": 0, "content_embedding": 1, "record_id": 1, "title": 1,
                     "tags": 1, "domains": 1, "status": 1, "type": 1, "refs_out": 1,
                     "wiki_links": 1, "file_path": 1, "created_at": 1, "updated_at": 1},
                ))

                for rec in knowledge_records:
                    embedding = rec.pop("content_embedding", None)
                    if embedding:
                        score = cosine_similarity(query_embedding, embedding)
                        if score > 0.3:  # Minimum threshold
                            results[rec["record_id"]] = {
                                "record": rec,
                                "semantic_score": score,
                                "keyword_score": 0.0,
                            }
        except ImportError:
            pass  # embed module not available — skip semantic search

    # ─── Keyword search ($text) ───
    if not entities_only:
        # Knowledge keyword search
        try:
            text_filter = {"$text": {"$search": query}, "type": "knowledge"}
            text_filter.update({k: v for k, v in base_filter.items() if k != "tags"})
            if tags:
                text_filter["tags"] = {"$in": tags}

            text_results = list(coll.find(
                text_filter,
                {"_id": 0, "content_embedding": 0, "score": {"$meta": "textScore"}},
            ).sort([("score", {"$meta": "textScore"})]).limit(limit * 2))

            for rec in text_results:
                rid = rec["record_id"]
                text_score = rec.pop("score", 0.0)
                normalized_score = min(text_score / 10.0, 1.0)  # Normalize to 0-1

                if rid in results:
                    results[rid]["keyword_score"] = normalized_score
                else:
                    results[rid] = {
                        "record": rec,
                        "semantic_score": 0.0,
                        "keyword_score": normalized_score,
                    }
        except Exception:
            pass  # $text search might fail if no text index

    if not knowledge_only:
        # Entity keyword search (name field, regex since entities don't have text index content)
        entity_filter = {"type": {"$ne": "knowledge"}}
        if types:
            entity_filter["type"] = {"$in": types}
        entity_filter.update({k: v for k, v in base_filter.items()
                              if k not in ("tags",) or not knowledge_only})

        # Search by name/title regex (case-insensitive)
        query_words = query.lower().split()
        if query_words:
            regex_patterns = [{"$or": [
                {"name": {"$regex": word, "$options": "i"}},
                {"record_id": {"$regex": word, "$options": "i"}},
            ]} for word in query_words]

            if regex_patterns:
                entity_filter["$and"] = regex_patterns

            try:
                entity_results = list(coll.find(
                    entity_filter,
                    {"_id": 0, "content_embedding": 0},
                ).limit(limit))

                for rec in entity_results:
                    rid = rec["record_id"]
                    # Score based on how many query words match
                    name = (rec.get("name") or rec.get("title") or "").lower()
                    match_count = sum(1 for w in query_words if w in name or w in rid)
                    score = match_count / len(query_words) if query_words else 0
                    results[rid] = {
                        "record": rec,
                        "semantic_score": 0.0,
                        "keyword_score": score,
                    }
            except Exception:
                pass

    # ─── Rank by combined score ───
    scored = []
    for rid, data in results.items():
        # Combined score: weighted average (semantic has higher weight)
        combined = (data["semantic_score"] * 0.7) + (data["keyword_score"] * 0.3)
        record = data["record"]
        record["_search_score"] = round(combined, 4)
        scored.append(record)

    # Sort by score descending
    scored.sort(key=lambda r: r.get("_search_score", 0), reverse=True)

    return scored[:limit]
