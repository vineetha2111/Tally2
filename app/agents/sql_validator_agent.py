"""SQL validation agent."""

from app.config.logging import get_logger
from app.schemas.state import GraphState
from app.services.sql_validator_service import SQLValidatorService

logger = get_logger("sql_validator_agent")


class SQLValidatorAgent:
    """Validates generated SQL before execution."""

    def __init__(self, validator: SQLValidatorService | None = None) -> None:
        self._validator = validator or SQLValidatorService()

    def run(self, state: GraphState) -> GraphState:
        """Validate SQL query; set error if validation fails."""
        if state.get("error"):
            return state

        sql_query = state["sql_query"]
        logger.info("Validating SQL query")

        try:
            validated = self._validator.validate(sql_query)
            return {**state, "sql_query": validated}
        except Exception as exc:
            logger.error("SQL validation failed: %s", exc)
            return {**state, "error": f"SQL validation failed: {exc}"}
