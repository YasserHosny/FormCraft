"""In-memory LRU cache for reference data dropdown queries."""

import time
from threading import Lock

_cache: dict[str, tuple[float, list[dict]]] = {}
_lock = Lock()

TTL_SECONDS = 300
MAX_SIZE = 200


def _cache_key(org_id: str, list_id: str, display: str, value: str) -> str:
    return f"{org_id}:{list_id}:{display}:{value}"


def get_cached(org_id: str, list_id: str, display: str, value: str) -> list[dict] | None:
    key = _cache_key(org_id, list_id, display, value)
    with _lock:
        entry = _cache.get(key)
        if entry is None:
            return None
        ts, data = entry
        if time.time() - ts > TTL_SECONDS:
            del _cache[key]
            return None
        return data


def set_cached(
    org_id: str, list_id: str, display: str, value: str, data: list[dict]
) -> None:
    key = _cache_key(org_id, list_id, display, value)
    with _lock:
        if len(_cache) >= MAX_SIZE:
            oldest_key = min(_cache, key=lambda k: _cache[k][0])
            del _cache[oldest_key]
        _cache[key] = (time.time(), data)


def invalidate(org_id: str, list_id: str) -> None:
    prefix = f"{org_id}:{list_id}:"
    with _lock:
        keys_to_delete = [k for k in _cache if k.startswith(prefix)]
        for k in keys_to_delete:
            del _cache[k]
