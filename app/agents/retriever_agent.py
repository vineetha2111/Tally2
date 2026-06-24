"""Data retrieval agent — executes validated SQL and returns a DataFrame."""

import pandas as pd

from app.config.config_manager import ConfigManager
from app.config.logging import get_logger
from app.schemas.state import GraphState
from app.services.sql_executor_service import SQLExecutorService


AGENT_CONFIG = ConfigManager.get_agent_config(
    "retriever"
)

WARN_ON_EMPTY_RESULT = AGENT_CONFIG[
    "retrieval"
]["warn_on_empty_result"]

logger = get_logger(
    AGENT_CONFIG["logging"]["logger_name"]
)


class RetrieverAgent:
    """Executes SQL against PostgreSQL and populates query_results."""

    def __init__(
        self,
        sql_executor: SQLExecutorService | None = None,
    ) -> None:
        self._executor = (
            sql_executor
            or SQLExecutorService()
        )

    def run(
        self,
        state: GraphState,
    ) -> GraphState:
        """Execute SQL and store results in state."""

        if state.get("error"):
            return state

        sql_query = state["sql_query"]

        logger.info(
            "Retrieving data"
        )

        try:
            df = self._executor.execute(
                sql_query
            )

            if (
                WARN_ON_EMPTY_RESULT
                and df.empty
            ):
                logger.warning(
                    "Query returned empty result set"
                )

            return {
                **state,
                "query_results": df,
            }

        except Exception as exc:
            logger.error(
                "Data retrieval failed: %s",
                exc,
            )

            return {
                **state,
                "query_results": pd.DataFrame(),
                "error": (
                    f"Data retrieval failed: {exc}"
                ),
            }