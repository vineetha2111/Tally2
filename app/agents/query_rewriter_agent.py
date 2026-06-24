"""Query rewrite agent."""

from app.config.config_manager import ConfigManager
from app.config.logging import get_logger
from app.schemas.state import GraphState
from app.services.ollama_service import OllamaService


PROMPT_CONFIG = ConfigManager.get_prompt(
    "query_rewriter"
)

AGENT_CONFIG = ConfigManager.get_agent_config(
    "query_rewriter"
)

SYSTEM_PROMPT = PROMPT_CONFIG[
    "system_prompt"
]

QUESTION_PREVIEW_LENGTH = AGENT_CONFIG[
    "rewrite"
]["max_question_preview_length"]

logger = get_logger(
    AGENT_CONFIG["logging"]["logger_name"]
)


class QueryRewriterAgent:
    """Rewrites user questions into analytics-friendly form."""

    def __init__(
        self,
        ollama_service: OllamaService,
    ) -> None:
        self._ollama = ollama_service

    def run(
        self,
        state: GraphState,
    ) -> GraphState:

        if state.get("error"):
            return state

        question = state["question"]

        logger.info(
            "Rewriting query: %s",
            question[:QUESTION_PREVIEW_LENGTH],
        )

        try:
            rewritten_question = (
                self._ollama.invoke(
                    prompt=f"User question: {question}",
                    system_prompt=SYSTEM_PROMPT,
                )
                .strip()
            )

            logger.info(
                "Query rewritten successfully"
            )

            return {
                **state,
                "rewritten_question": rewritten_question,
                "question": rewritten_question,
            }

        except Exception as exc:
            logger.error(
                "Query rewrite failed: %s",
                exc,
            )

            return {
                **state,
                "error": (
                    f"Query rewrite failed: {exc}"
                ),
            }