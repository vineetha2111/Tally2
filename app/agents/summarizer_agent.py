"""Executive summary agent."""

from app.config.config_manager import ConfigManager
from app.config.logging import get_logger
from app.schemas.state import GraphState
from app.services.ollama_service import OllamaService


PROMPT_CONFIG = ConfigManager.get_prompt(
    "summarizer"
)

AGENT_CONFIG = ConfigManager.get_agent_config(
    "summarizer"
)

SYSTEM_PROMPT = PROMPT_CONFIG["system_prompt"]

logger = get_logger(
    AGENT_CONFIG["logging"]["logger_name"]
)


class SummarizerAgent:
    """Generates executive summaries from analysis output."""

    def __init__(
        self,
        ollama_service: OllamaService,
    ) -> None:
        self._ollama = ollama_service

    def run(
        self,
        state: GraphState,
    ) -> GraphState:
        """Generate executive summary and update state."""

        if state.get("error"):
            return state

        question = state["question"]
        intent = state["intent"]
        analysis = state["analysis"]

        logger.info(
            "Generating executive summary"
        )

        try:
            prompt = (
                f"Original question: {question}\n"
                f"Business intent: {intent}\n\n"
                f"Detailed analysis:\n"
                f"{analysis}\n\n"
                f"Write the executive summary."
            )

            summary = self._ollama.invoke(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
            )

            logger.info(
                "Summary complete (%d chars)",
                len(summary),
            )

            return {
                **state,
                "summary": summary,
            }

        except Exception as exc:
            logger.error(
                "Summarization failed: %s",
                exc,
            )

            return {
                **state,
                "error": (
                    f"Summarizer agent failed: {exc}"
                ),
            }