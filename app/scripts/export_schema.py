import json

from app.config.settings import get_settings
from app.database.session import get_session_factory
from app.database.schema_repository import SchemaRepository


def export_schema():

    settings = get_settings()

    session_factory = get_session_factory(settings)

    session = session_factory()

    try:

        repo = SchemaRepository(session)

        catalog = repo.build_full_schema_catalog()

        with open(
            "app/data/schema_catalog.json",
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                catalog,
                file,
                indent=2,
                ensure_ascii=False,
            )

        print(
            "Schema exported successfully"
        )

    finally:
        session.close()


if __name__ == "__main__":
    export_schema()