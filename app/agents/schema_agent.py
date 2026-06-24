"""Schema discovery agent."""

from app.config.config_manager import ConfigManager
from app.config.logging import get_logger

from app.schemas.state import GraphState
from app.services.ollama_service import OllamaService
from app.services.schema_cache_service import SchemaCacheService

from app.config.settings import Settings, get_settings
from app.schemas.state import GraphState
from app.services.ollama_service import OllamaService
from app.services.schema_cache_service import get_schema_cache



PROMPT_CONFIG = ConfigManager.get_prompt(
    "schema"
)

AGENT_CONFIG = ConfigManager.get_agent_config(
    "schema"
)

SYSTEM_PROMPT = PROMPT_CONFIG[
    "system_prompt"
]

logger = get_logger(
    AGENT_CONFIG["logging"]["logger_name"]
)


class SchemaAgent:
    """
    Discovers relevant schema context from the
    cached schema catalog.
    """

    def __init__(
        self,
        ollama_service: OllamaService,
    ) -> None:
        self._ollama = ollama_service

    def run(
        self,
        state: GraphState,
    ) -> GraphState:
        """
        Build schema context for SQL generation.
        """

        if state.get("error"):
            return state

        question = state["question"]
        intent = state["intent"]

        logger.info(
            "Discovering schema for intent=%s",
            intent,
        )

        try:

            catalog = (
                SchemaCacheService.get_catalog()
            )

            # Use cached schema instead of fetching every time
            schema_cache = get_schema_cache()
            catalog = schema_cache.get_schema_catalog(self._settings)


            prompt = (
                f"User question: {question}\n"
                f"Business intent: {intent}\n\n"
                f"Database schema catalog:\n"
                f"{catalog}"
            )

            schema_context = (
                self._ollama.invoke(
                    prompt=prompt,
                    system_prompt=SYSTEM_PROMPT,
                )
            )

            logger.info(
                "Schema context built (%d chars)",
                len(schema_context),
            )

            return {
                **state,
                "schema_context": schema_context,
                "schema_catalog": catalog,
            }

        except Exception as exc:
            logger.error(
                "Schema discovery failed: %s",
                exc,
            )

            return {
                **state,
                "error": (
                    f"Schema agent failed: {exc}"
                ),
            }