"""Semantic caching for LLM responses."""

import hashlib
from time import time
from app.config.logging import get_logger

logger = get_logger("llm_cache")


class LLMCacheService:
    """Cache LLM responses based on system + prompt hash."""
    
    def __init__(self, ttl_seconds: int = 7200, max_entries: int = 1000):
        self._ttl = ttl_seconds
        self._max_entries = max_entries
        self._cache: dict = {}
        self._cache_time: dict = {}
    
    def _cache_key(self, system_prompt: str | None, prompt: str) -> str:
        """Generate cache key from system + user prompt."""
        combined = f"{system_prompt or ''}|{prompt}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def get(self, system_prompt: str | None, prompt: str) -> str | None:
        """Retrieve cached LLM response if available and fresh."""
        key = self._cache_key(system_prompt, prompt)
        now = time()
        
        if key in self._cache:
            if now - self._cache_time.get(key, 0) < self._ttl:
                logger.debug(f"LLM cache hit for prompt (hash={key[:8]})")
                return self._cache[key]
            else:
                logger.debug(f"LLM cache expired for prompt (hash={key[:8]})")
                del self._cache[key]
                del self._cache_time[key]
        
        return None
    
    def set(self, system_prompt: str | None, prompt: str, response: str) -> None:
        """Cache an LLM response."""
        key = self._cache_key(system_prompt, prompt)
        now = time()
        
        # Simple eviction: if cache too large, clear oldest entries
        if len(self._cache) >= self._max_entries:
            oldest_key = min(self._cache_time, key=self._cache_time.get)
            del self._cache[oldest_key]
            del self._cache_time[oldest_key]
            logger.debug(f"LLM cache evicted oldest entry")
        
        self._cache[key] = response
        self._cache_time[key] = now
        logger.debug(f"LLM cache stored response (hash={key[:8]})")


# Global singleton
_llm_cache: LLMCacheService | None = None


def get_llm_cache(ttl_seconds: int = 7200, max_entries: int = 1000) -> LLMCacheService:
    """Get or create singleton LLM cache."""
    global _llm_cache
    if _llm_cache is None:
        _llm_cache = LLMCacheService(ttl_seconds, max_entries)
    return _llm_cache
