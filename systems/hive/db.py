"""MongoDB connection for the Hive."""
import pymongo

from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION


_client = None
_db = None


def get_client() -> pymongo.MongoClient:
    """Return the MongoDB client (lazy singleton)."""
    global _client
    if _client is None:
        _client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    return _client


def get_db():
    """Return the hive database."""
    global _db
    if _db is None:
        _db = get_client()[MONGO_DB]
    return _db


def get_collection():
    """Return the records collection."""
    return get_db()[MONGO_COLLECTION]


def check_connection() -> bool:
    """Check if MongoDB is reachable."""
    try:
        get_client().admin.command("ping")
        return True
    except Exception:
        return False
