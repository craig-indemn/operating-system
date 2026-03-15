"""Unified record access across entity and knowledge layers.

Thin import layer — pulls from entity_ops and knowledge_ops with try/except
so each module can be developed independently.
"""
from db import get_collection

# Import entity operations (Wave 1.3A)
try:
    from entity_ops import (
        create_entity,
        get_entity,
        update_entity,
        list_entities,
        get_entity_refs,
    )
except ImportError:
    create_entity = get_entity = update_entity = list_entities = get_entity_refs = None

# Import knowledge operations (Wave 1.3B)
try:
    from knowledge_ops import (
        create_knowledge,
        get_knowledge,
        update_knowledge,
        list_knowledge,
    )
except ImportError:
    create_knowledge = get_knowledge = update_knowledge = list_knowledge = None


def get_record(record_id: str) -> dict | None:
    """Get any record by ID, checking both layers.

    Entity layer checked first (faster — MongoDB only).
    """
    coll = get_collection()
    record = coll.find_one({"record_id": record_id}, {"_id": 0})
    return record


def _get_single_hop(record_id: str, direction: str, coll) -> dict:
    """Get single-hop references for a record.

    Returns: {"out": [record_ids], "in": [record_ids]}
    """
    result = {"out": set(), "in": set()}

    record = coll.find_one({"record_id": record_id})
    if not record:
        return result

    # Outbound: refs_out + wiki_links
    if direction in ("out", "both"):
        refs_out = record.get("refs_out", {})
        for ref_type, ref_ids in refs_out.items():
            ids = ref_ids if isinstance(ref_ids, list) else [ref_ids]
            for rid in ids:
                if rid != record_id:
                    result["out"].add(rid)

        for wl in record.get("wiki_links", []):
            if wl != record_id:
                result["out"].add(wl)

    # Inbound: records that reference this one
    if direction in ("in", "both"):
        ref_fields = [
            "refs_out.company", "refs_out.project", "refs_out.people",
            "refs_out.product", "refs_out.brand", "refs_out.platform",
            "refs_out.channel", "refs_out.meeting", "refs_out.workflow",
        ]
        for field in ref_fields:
            for doc in coll.find({field: record_id}, {"record_id": 1}):
                rid = doc["record_id"]
                if rid != record_id:
                    result["in"].add(rid)

        for doc in coll.find({"wiki_links": record_id}, {"record_id": 1}):
            rid = doc["record_id"]
            if rid != record_id:
                result["in"].add(rid)

    return result


def get_refs(record_id: str, direction: str = "both", depth: int = 1) -> dict:
    """Get references for a record across both layers with multi-hop support.

    Args:
        record_id: The starting record
        direction: "out", "in", or "both"
        depth: 1-3 hops (default 1)

    Returns: {
        "out": [records this record references (transitively)],
        "in": [records that reference this record (transitively)]
    }
    """
    coll = get_collection()
    visited = {record_id}  # Cycle detection
    all_out_ids = set()
    all_in_ids = set()

    # BFS traversal for outbound
    if direction in ("out", "both"):
        frontier = {record_id}
        for hop in range(depth):
            next_frontier = set()
            for rid in frontier:
                hop_refs = _get_single_hop(rid, "out", coll)
                for out_id in hop_refs["out"]:
                    if out_id not in visited:
                        visited.add(out_id)
                        all_out_ids.add(out_id)
                        next_frontier.add(out_id)
            frontier = next_frontier
            if not frontier:
                break

    # BFS traversal for inbound
    if direction in ("in", "both"):
        # Reset visited for inbound (outbound and inbound are independent traversals)
        in_visited = {record_id}
        frontier = {record_id}
        for hop in range(depth):
            next_frontier = set()
            for rid in frontier:
                hop_refs = _get_single_hop(rid, "in", coll)
                for in_id in hop_refs["in"]:
                    if in_id not in in_visited:
                        in_visited.add(in_id)
                        all_in_ids.add(in_id)
                        next_frontier.add(in_id)
            frontier = next_frontier
            if not frontier:
                break

    # Fetch full records for all discovered IDs
    result = {"out": [], "in": []}
    for rid in all_out_ids:
        rec = coll.find_one({"record_id": rid}, {"_id": 0, "content_embedding": 0})
        if rec:
            result["out"].append(rec)
    for rid in all_in_ids:
        rec = coll.find_one({"record_id": rid}, {"_id": 0, "content_embedding": 0})
        if rec:
            result["in"].append(rec)

    return result
