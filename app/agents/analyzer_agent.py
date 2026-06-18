"""Data analysis agent."""

from app.config.logging import get_logger
from app.schemas.state import GraphState
from app.services.ollama_service import OllamaService
from app.services.sql_executor_service import SQLExecutorService

logger = get_logger("analyzer_agent")

ANALYZER_SYSTEM_PROMPT = """You are a senior business data analyst.
Analyze the query results and provide detailed business insights.

Include where applicable:
- Key trends and patterns
- Anomalies or outliers
- KPIs and metrics with specific numbers
- Revenue and sales insights
- Customer insights
- Inventory insights
- Financial observations
- Risks and opportunities
- Actionable recommendations

Be specific. Reference actual values from the data.
Write in clear, professional language suitable for business stakeholders.
If no data was returned, explain what that means and suggest next steps."""


class AnalyzerAgent:
    """Analyzes query results and generates detailed business insights."""

    def __init__(
        self,
        ollama_service: OllamaService,
        sql_executor: SQLExecutorService | None = None,
    ) -> None:
        self._ollama = ollama_service
        self._executor = sql_executor or SQLExecutorService()

    def run(self, state: GraphState) -> GraphState:
        """Analyze query results and update state."""
        if state.get("error"):
            return state

        question = state["question"]
        intent = state["intent"]
        df = state["query_results"]
        sql_query = state["sql_query"]
        logger.info("Analyzing %d rows", len(df))

        try:
            data_preview = self._executor.dataframe_preview(df)
            prompt = (
                f"User question: {question}\n"
                f"Business intent: {intent}\n"
                f"SQL query executed:\n{sql_query}\n\n"
                f"Query results:\n{data_preview}\n\n"
                f"Provide a detailed business analysis."
            )
            analysis = self._ollama.invoke(
                prompt=prompt,
                system_prompt=ANALYZER_SYSTEM_PROMPT,
            )
            logger.info("Analysis complete (%d chars)", len(analysis))
            return {**state, "analysis": analysis}
        except Exception as exc:
            logger.error("Analysis failed: %s", exc)
            return {**state, "error": f"Analyzer agent failed: {exc}"}
