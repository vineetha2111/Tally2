"""Intent classification agent."""

from app.config.config_manager import ConfigManager
from app.config.logging import get_logger
from app.schemas.state import BusinessIntent, GraphState
from app.services.ollama_service import OllamaService


PROMPT_CONFIG = ConfigManager.get_prompt("intent")
AGENT_CONFIG = ConfigManager.get_agent_config("intent")

SYSTEM_PROMPT = PROMPT_CONFIG["system_prompt"]

DEFAULT_INTENT = AGENT_CONFIG["default_intent"]

QUESTION_PREVIEW_LENGTH = AGENT_CONFIG[
    "classification"
]["max_question_preview_length"]

logger = get_logger(
    AGENT_CONFIG["logging"]["logger_name"]
)

VALID_INTENTS = {
    intent.value
    for intent in BusinessIntent
}


class IntentAgent:
    """Determines business intent from a natural language question."""

    def __init__(
        self,
        ollama_service: OllamaService,
    ) -> None:
        self._ollama = ollama_service

    def run(
        self,
        state: GraphState,
    ) -> GraphState:
        """Classify business intent and update state."""

        if state.get("error"):
            return state

        question = state["question"]

        logger.info(
            "Classifying intent for question: %s",
            question[:QUESTION_PREVIEW_LENGTH],
        )

        try:
            raw_response = self._ollama.invoke(
                prompt=f"User question: {question}",
                system_prompt=SYSTEM_PROMPT,
            )

            intent = (
                raw_response.strip().upper().split()[0]
                if raw_response.strip()
                else DEFAULT_INTENT
            )

            if intent not in VALID_INTENTS:
                intent = DEFAULT_INTENT

            logger.info(
                "Detected intent: %s",
                intent,
            )

            return {
                **state,
                "intent": intent,
            }

        except Exception as exc:
            logger.error(
                "Intent classification failed: %s",
                exc,
            )

            return {
                **state,
                "error": f"Intent agent failed: {exc}",
            }