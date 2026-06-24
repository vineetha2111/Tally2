"""SQL validation agent."""

from app.config.config_manager import ConfigManager
from app.config.logging import get_logger
from app.schemas.state import GraphState
from app.services.sql_validator_service import SQLValidatorService


AGENT_CONFIG = ConfigManager.get_agent_config(
    "sql_validator"
)

logger = get_logger(
    AGENT_CONFIG["logging"]["logger_name"]
)


class SQLValidatorAgent:
    """Validates generated SQL before execution."""

    def __init__(
        self,
        validator: SQLValidatorService | None = None,
    ) -> None:
        self._validator = (
            validator
            or SQLValidatorService()
        )

    def run(
        self,
        state: GraphState,
    ) -> GraphState:
        """Validate SQL query before execution."""

        if state.get("error"):
            return state

        sql_query = state["sql_query"]

        logger.info(
            "Validating SQL query"
        )

        try:
            validated_query = (
                self._validator.validate(
                    sql_query
                )
            )

            logger.info(
                "SQL validation successful"
            )

            return {
                **state,
                "sql_query": validated_query,
            }

        except Exception as exc:
            logger.error(
                "SQL validation failed: %s",
                exc,
            )

            return {
                **state,
                "error": (
                    f"SQL validation failed: {exc}"
                ),
            }