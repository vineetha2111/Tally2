"""Repository for PostgreSQL schema metadata via information_schema."""

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config.logging import get_logger

logger = get_logger("schema_repository")


@dataclass(frozen=True)
class ColumnInfo:
    table_schema: str
    table_name: str
    column_name: str
    data_type: str
    is_nullable: str
    column_default: str | None


@dataclass(frozen=True)
class TableInfo:
    table_schema: str
    table_name: str


@dataclass(frozen=True)
class ForeignKeyInfo:
    table_schema: str
    table_name: str
    column_name: str
    foreign_table_schema: str
    foreign_table_name: str
    foreign_column_name: str


class SchemaRepository:
    """Read-only access to PostgreSQL metadata."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_tables(self, schema: str = "public") -> list[TableInfo]:
        query = text(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema = :schema
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """
        )
        rows = self._session.execute(query, {"schema": schema}).mappings().all()
        return [TableInfo(**row) for row in rows]

    def get_columns(self, schema: str = "public") -> list[ColumnInfo]:
        query = text(
            """
            SELECT table_schema, table_name, column_name, data_type,
                   is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = :schema
            ORDER BY table_name, ordinal_position
            """
        )
        rows = self._session.execute(query, {"schema": schema}).mappings().all()
        return [ColumnInfo(**row) for row in rows]

    def get_columns_for_tables(
        self, table_names: list[str], schema: str = "public"
    ) -> list[ColumnInfo]:
        if not table_names:
            return []
        query = text(
            """
            SELECT table_schema, table_name, column_name, data_type,
                   is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = :schema
              AND table_name = ANY(:table_names)
            ORDER BY table_name, ordinal_position
            """
        )
        rows = self._session.execute(
            query, {"schema": schema, "table_names": table_names}
        ).mappings().all()
        return [ColumnInfo(**row) for row in rows]

    def get_foreign_keys(self, schema: str = "public") -> list[ForeignKeyInfo]:
        query = text(
            """
            SELECT
                tc.table_schema,
                tc.table_name,
                kcu.column_name,
                ccu.table_schema AS foreign_table_schema,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
             AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = :schema
            ORDER BY tc.table_name, kcu.column_name
            """
        )
        rows = self._session.execute(query, {"schema": schema}).mappings().all()
        return [ForeignKeyInfo(**row) for row in rows]

    def build_full_schema_catalog(self, schema: str = "public") -> str:
        """Build a compact text catalog of all tables, columns, and relationships."""
        tables = self.get_tables(schema)
        columns = self.get_columns(schema)
        foreign_keys = self.get_foreign_keys(schema)

        lines: list[str] = ["=== DATABASE SCHEMA CATALOG ===", ""]

        columns_by_table: dict[str, list[ColumnInfo]] = {}
        for col in columns:
            columns_by_table.setdefault(col.table_name, []).append(col)

        for table in tables:
            lines.append(f"TABLE: {table.table_schema}.{table.table_name}")
            for col in columns_by_table.get(table.table_name, []):
                nullable = "NULL" if col.is_nullable == "YES" else "NOT NULL"
                default = f" DEFAULT {col.column_default}" if col.column_default else ""
                lines.append(
                    f"  - {col.column_name} ({col.data_type}, {nullable}{default})"
                )
            lines.append("")

        if foreign_keys:
            lines.append("=== RELATIONSHIPS ===")
            for fk in foreign_keys:
                lines.append(
                    f"{fk.table_name}.{fk.column_name} -> "
                    f"{fk.foreign_table_name}.{fk.foreign_column_name}"
                )

        catalog = "\n".join(lines)
        logger.debug("Built schema catalog with %d tables", len(tables))
        return catalog
