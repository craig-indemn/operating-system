"""Hive configuration — paths, MongoDB URI, knowledge directory mapping."""
import os
from pathlib import Path

# Root paths — always resolve from cli.py location (works in worktrees)
# OS_ROOT env var points to main repo which doesn't work in worktrees,
# so we always derive from __file__ which Python resolves correctly.
_THIS_DIR = Path(__file__).resolve().parent  # systems/hive/
OS_ROOT = _THIS_DIR.parent.parent  # repo root
HIVE_ROOT = OS_ROOT / "hive"
REGISTRY_PATH = HIVE_ROOT / ".registry"
TYPES_PATH = REGISTRY_PATH / "types"
ONTOLOGY_PATH = REGISTRY_PATH / "ontology.yaml"

# MongoDB
MONGO_URI = os.environ.get("HIVE_MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.environ.get("HIVE_MONGO_DB", "hive")
MONGO_COLLECTION = "records"

# Systems path
SYSTEMS_ROOT = OS_ROOT / "systems"
HIVE_SYSTEM_ROOT = SYSTEMS_ROOT / "hive"

# Knowledge directory mapping: tag → directory name
# Knowledge-kind tags map to specific directories. Other tags don't have directories.
KNOWLEDGE_DIRS = {
    "note": "notes",
    "decision": "decisions",
    "design": "designs",
    "research": "research",
    "session_summary": "sessions",
    "feedback": "notes",          # feedback goes to notes/
    "context_assembly": "sessions",  # context notes go to sessions/
}

# Default directory for knowledge records with no matching tag
DEFAULT_KNOWLEDGE_DIR = "notes"


def get_knowledge_dir(tags: list[str]) -> str:
    """Return the directory name for a knowledge record based on its tags.

    Uses the first tag that maps to a directory.
    """
    for tag in tags:
        if tag in KNOWLEDGE_DIRS:
            return KNOWLEDGE_DIRS[tag]
    return DEFAULT_KNOWLEDGE_DIR
