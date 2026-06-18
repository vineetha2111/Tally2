"""Executive summary agent."""

from app.config.logging import get_logger
from app.schemas.state import GraphState
from app.services.ollama_service import OllamaService

logger = get_logger("summarizer_agent")

SUMMARIZER_SYSTEM_PROMPT = """You are an executive briefing assistant for C-level management.
Create a short, concise executive summary based on the analysis provided.

Requirements:
- Business-friendly language (no technical jargon)
- Management focused
- 3-5 bullet points maximum
- Highlight the most important findings and recommended actions
- Include key numbers where relevant
- Keep it under 200 words"""


class SummarizerAgent:
    """Generates executive summaries from analysis output."""

    def __init__(self, ollama_service: OllamaService) -> None:
        self._ollama = ollama_service

    def run(self, state: GraphState) -> GraphState:
        """Generate executive summary and update state."""
        if state.get("error"):
            return state

        question = state["question"]
        intent = state["intent"]
        analysis = state["analysis"]
        logger.info("Generating executive summary")

        try:
            prompt = (
                f"Original question: {question}\n"
                f"Business intent: {intent}\n\n"
                f"Detailed analysis:\n{analysis}\n\n"
                f"Write the executive summary."
            )
            summary = self._ollama.invoke(
                prompt=prompt,
                system_prompt=SUMMARIZER_SYSTEM_PROMPT,
            )
            logger.info("Summary complete (%d chars)", len(summary))
            return {**state, "summary": summary}
        except Exception as exc:
            logger.error("Summarization failed: %s", exc)
            return {**state, "error": f"Summarizer agent failed: {exc}"}
