from cachetools import TTLCache

# In-memory LRU + TTL cache for AI suggestions
# Key: "{label}:{language}:{country}", Value: SuggestionResponse dict
suggestion_cache: TTLCache = TTLCache(maxsize=1000, ttl=300)  # 5 min TTL


def get_cache_key(label: str, language: str, country: str) -> str:
    return f"{label.strip().lower()}:{language}:{country}"
