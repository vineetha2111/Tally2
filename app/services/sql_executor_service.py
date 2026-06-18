"""Service for executing validated SQL and returning Pandas DataFrames."""

import pandas as pd
from sqlalchemy.engine import Engine

from app.config.logging import get_logger
from app.config.settings import Settings, get_settings
from app.database.session import get_engine
from app.exceptions.errors import DatabaseError

logger = get_logger("sql_executor")


class SQLExecutorService:
    """Executes read-only SQL queries against PostgreSQL."""

    def __init__(
        self,
        settings: Settings | None = None,
        engine: Engine | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._engine = engine or get_engine(self._settings)

    def execute(self, sql_query: str) -> pd.DataFrame:
        """Execute a validated SELECT query and return results as a DataFrame."""
        try:
            logger.info("Executing SQL query")
            df = pd.read_sql_query(sql_query, self._engine)
            logger.info("Query returned %d rows, %d columns", len(df), len(df.columns))
            return df
        except Exception as exc:
            logger.error("SQL execution failed: %s", exc)
            raise DatabaseError(f"SQL execution failed: {exc}") from exc

    @staticmethod
    def dataframe_preview(df: pd.DataFrame, max_rows: int = 10) -> str:
        """Return a string preview of DataFrame for LLM consumption."""
        if df.empty:
            return "No rows returned."
        preview = df.head(max_rows)
        stats = (
            f"Shape: {df.shape[0]} rows x {df.shape[1]} columns\n"
            f"Dtypes:\n{df.dtypes.to_string()}\n\n"
            f"Preview (first {min(max_rows, len(df))} rows):\n"
            f"{preview.to_string(index=False)}"
        )
        if len(df) > max_rows:
            numeric = df.select_dtypes(include="number")
            if not numeric.empty:
                stats += f"\n\nNumeric summary:\n{numeric.describe().to_string()}"
        return stats
