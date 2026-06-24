# app/services/schema_cache_service.py

import json
from pathlib import Path


class SchemaCacheService:

    _catalog = None

    @classmethod
    def get_catalog(cls):
        if cls._catalog is None:

            schema_file = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "schema_catalog.json"
            )

            with open(schema_file, "r", encoding="utf-8") as f:
                cls._catalog = json.load(f)

        return cls._catalog