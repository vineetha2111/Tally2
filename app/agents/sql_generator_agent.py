"""SQL generation agent."""

from app.config.config_manager import ConfigManager
from app.config.logging import get_logger
from app.schemas.state import GraphState
from app.services.ollama_service import OllamaService


PROMPT_CONFIG = ConfigManager.get_prompt(
    "sql_generator"
)

AGENT_CONFIG = ConfigManager.get_agent_config(
    "sql_generator"
)

SYSTEM_PROMPT = PROMPT_CONFIG["system_prompt"]

SQL_PREVIEW_LENGTH = AGENT_CONFIG[
    "sql_generation"
]["sql_preview_length"]

logger = get_logger(
    AGENT_CONFIG["logging"]["logger_name"]
)


class SQLGeneratorAgent:
    """Converts natural language questions into PostgreSQL SELECT queries."""

    def __init__(
        self,
        ollama_service: OllamaService,
    ) -> None:
        self._ollama = ollama_service

    def run(
        self,
        state: GraphState,
    ) -> GraphState:
        """Generate SQL from question, intent, and schema context."""

        if state.get("error"):
            return state

        question = state["question"]
        intent = state["intent"]
        schema_context = state["schema_context"]

        # Loaded once by SchemaAgent
        catalog = state["schema_catalog"]

        logger.info(
            "Generating SQL for intent=%s",
            intent,
        )

        try:
            prompt = (
                f"User question: {question}\n"
                f"Business intent: {intent}\n\n"
                f"Relevant schema analysis:\n"
                f"{schema_context}\n\n"
                f"Full schema catalog:\n"
                f"{catalog}\n\n"
                f"Generate the PostgreSQL SELECT query."
            )

            raw_sql = self._ollama.invoke(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
            )

            sql_query = self._ollama.extract_sql(
                raw_sql
            )

            logger.info(
                "Generated SQL: %s",
                sql_query[:SQL_PREVIEW_LENGTH],
            )

            return {
                **state,
                "sql_query": sql_query,
            }

        except Exception as exc:
            logger.error(
                "SQL generation failed: %s",
                exc,
            )

            return {
                **state,
                "error": (
                    f"SQL generator failed: {exc}"
                ),
            }