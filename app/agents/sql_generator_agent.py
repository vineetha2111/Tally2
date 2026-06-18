"""SQL generation agent."""

from app.config.logging import get_logger
from app.config.settings import Settings, get_settings
from app.database.schema_repository import SchemaRepository
from app.database.session import get_session_factory
from app.schemas.state import GraphState
from app.services.ollama_service import OllamaService

logger = get_logger("sql_generator_agent")

SQL_SYSTEM_PROMPT = """You are an expert PostgreSQL query writer for business analytics.
Generate a single optimized SELECT query to answer the user's question.

Rules:
- Return ONLY the SQL query. No explanation, no markdown, no comments.
- Use only tables and columns from the provided schema context.
- Use proper JOINs when multiple tables are needed.
- Use meaningful column aliases.
- Add ORDER BY when ranking or trends are requested.
- Add LIMIT when returning top-N results (default LIMIT 100 if unspecified).
- Use PostgreSQL syntax.
- Never use INSERT, UPDATE, DELETE, DROP, or other DDL/DML.
- Prefer aggregations (SUM, COUNT, AVG) for analytical questions."""


class SQLGeneratorAgent:
    """Converts natural language questions into PostgreSQL SELECT queries."""

    def __init__(
        self,
        ollama_service: OllamaService,
        settings: Settings | None = None,
    ) -> None:
        self._ollama = ollama_service
        self._settings = settings or get_settings()

    def run(self, state: GraphState) -> GraphState:
        """Generate SQL from question, intent, and schema context."""
        if state.get("error"):
            return state

        question = state["question"]
        intent = state["intent"]
        schema_context = state["schema_context"]
        logger.info("Generating SQL for intent=%s", intent)

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
                f"Relevant schema analysis:\n{schema_context}\n\n"
                f"Full schema catalog for reference:\n{catalog}\n\n"
                f"Generate the PostgreSQL SELECT query."
            )
            raw_sql = self._ollama.invoke(prompt=prompt, system_prompt=SQL_SYSTEM_PROMPT)
            sql_query = self._ollama.extract_sql(raw_sql)
            logger.info("Generated SQL: %s", sql_query[:120])
            return {**state, "sql_query": sql_query}
        except Exception as exc:
            logger.error("SQL generation failed: %s", exc)
            return {**state, "error": f"SQL generator failed: {exc}"}
