"""Schema discovery agent using PostgreSQL information_schema."""

from app.config.logging import get_logger
from app.config.settings import Settings, get_settings
from app.database.schema_repository import SchemaRepository
from app.database.session import get_session_factory
from app.schemas.state import GraphState
from app.services.ollama_service import OllamaService

logger = get_logger("schema_agent")

SCHEMA_SYSTEM_PROMPT = """You are a database schema analyst.
Given a user question, business intent, and full database schema catalog,
identify the relevant tables and columns needed to answer the question.

Output format (plain text, no markdown):
RELEVANT TABLES: table1, table2
RELEVANT COLUMNS:
- table1: col1, col2
- table2: col3
RELATIONSHIPS:
- table1.col -> table2.col (describe join)
NOTES:
- Brief note on how tables relate to the question

Be precise. Only include tables and columns that are needed."""


class SchemaAgent:
    """Discovers relevant schema context from PostgreSQL metadata."""

    def __init__(
        self,
        ollama_service: OllamaService,
        settings: Settings | None = None,
    ) -> None:
        self._ollama = ollama_service
        self._settings = settings or get_settings()

    def run(self, state: GraphState) -> GraphState:
        """Build schema context for SQL generation."""
        if state.get("error"):
            return state

        question = state["question"]
        intent = state["intent"]
        logger.info("Discovering schema for intent=%s", intent)

        try:
            session_factory = get_session_factory(self._settings)
            session = session_factory()
            try:
                repo = SchemaRepository(session)
                catalog = repo.build_full_schema_catalog()
            finally:
                session.close()

            prompt = (
                f"User question: {question}\n"
                f"Business intent: {intent}\n\n"
                f"Database schema catalog:\n{catalog}"
            )
            schema_context = self._ollama.invoke(
                prompt=prompt,
                system_prompt=SCHEMA_SYSTEM_PROMPT,
            )
            logger.info("Schema context built (%d chars)", len(schema_context))
            return {**state, "schema_context": schema_context}
        except Exception as exc:
            logger.error("Schema discovery failed: %s", exc)
            return {**state, "error": f"Schema agent failed: {exc}"}
