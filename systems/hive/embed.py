"""Embedding abstraction for the Hive.

Uses Ollama's local nomic-embed-text model via HTTP API.
Pure Python cosine similarity (no numpy dependency).
Graceful degradation when Ollama is not running.
"""
import json
import math
import sys
import urllib.error
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/embeddings"
OLLAMA_MODEL = "nomic-embed-text"


def get_embedding(text: str) -> list[float] | None:
    """Get embedding vector for text via Ollama.

    Returns None if Ollama is unavailable or the request fails.
    """
    if not text or not text.strip():
        return None

    # Truncate long text (nomic-embed-text has 8192 token context)
    # Keep conservative to avoid Ollama timeouts when other models are loaded
    if len(text) > 8000:
        text = text[:8000]

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": text,
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("embedding")
    except (urllib.error.URLError, ConnectionRefusedError, TimeoutError) as e:
        # Ollama not running — graceful degradation
        return None
    except Exception as e:
        print(f"  Embedding error: {e}", file=sys.stderr)
        return None


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors. Pure Python."""
    if not a or not b or len(a) != len(b):
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / (norm_a * norm_b)


def batch_embed(texts: list[str]) -> list[list[float] | None]:
    """Embed multiple texts. Returns list of embeddings (None for failures)."""
    return [get_embedding(text) for text in texts]
