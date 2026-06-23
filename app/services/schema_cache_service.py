"""Cache layer for database schema metadata with TTL."""

from time import time
from app.database.schema_repository import SchemaRepository
from app.database.session import get_session_factory
from app.config.settings import Settings, get_settings
from app.config.logging import get_logger

logger = get_logger("schema_cache")


class SchemaCacheService:
    """Thread-safe LRU cache for schema catalogs with TTL."""
    
    def __init__(self, ttl_seconds: int = 3600):
        self._ttl = ttl_seconds
        self._cache: dict = {}
        self._cache_time: dict = {}
    
    def get_schema_catalog(self, settings: Settings | None = None, schema: str = "public") -> str:
        """Get cached schema catalog, refresh if TTL expired."""
        cache_key = f"{schema}"
        now = time()
        
        # Return cached result if valid
        if cache_key in self._cache:
            if now - self._cache_time.get(cache_key, 0) < self._ttl:
                logger.debug(f"Schema cache hit for {cache_key}")
                return self._cache[cache_key]
            logger.debug(f"Schema cache expired for {cache_key}")
        
        # Fetch fresh schema
        logger.info(f"Rebuilding schema cache for {cache_key}")
        cfg = settings or get_settings()
        session_factory = get_session_factory(cfg)
        session = session_factory()
        try:
            repo = SchemaRepository(session)
            catalog = repo.build_full_schema_catalog(schema)
            self._cache[cache_key] = catalog
            self._cache_time[cache_key] = now
            return catalog
        finally:
            session.close()


# Global singleton
_schema_cache: SchemaCacheService | None = None


def get_schema_cache(ttl_seconds: int = 3600) -> SchemaCacheService:
    """Get or create singleton schema cache."""
    global _schema_cache
    if _schema_cache is None:
        _schema_cache = SchemaCacheService(ttl_seconds)
    return _schema_cache
