"""Intent classification agent."""

from app.config.logging import get_logger
from app.schemas.state import BusinessIntent, GraphState
from app.services.ollama_service import OllamaService

logger = get_logger("intent_agent")

INTENT_SYSTEM_PROMPT = """You are a business intent classifier for an analytics system.
Analyze the user's question and classify it into exactly ONE category.

Categories:
- SALES: sales volume, revenue from sales, top selling products
- CUSTOMERS: customer behavior, customer rankings, customer segments
- INVENTORY: stock levels, low inventory, warehouse, product availability
- FINANCE: financial metrics, cash flow, expenses, budgets
- PURCHASES: procurement, purchase orders, buying activity
- VENDORS: supplier performance, vendor relationships
- PROFIT: margins, profitability, cost vs revenue
- GENERAL: questions that don't fit other categories

Respond with ONLY the category name in uppercase. No explanation."""

VALID_INTENTS = {intent.value for intent in BusinessIntent}


class IntentAgent:
    """Determines business intent from a natural language question."""

    def __init__(self, ollama_service: OllamaService) -> None:
        self._ollama = ollama_service

    def run(self, state: GraphState) -> GraphState:
        """Classify business intent and update state."""
        if state.get("error"):
            return state

        question = state["question"]
        logger.info("Classifying intent for question: %s", question[:80])

        try:
            raw = self._ollama.invoke(
                prompt=f"User question: {question}",
                system_prompt=INTENT_SYSTEM_PROMPT,
            )
            intent = raw.strip().upper().split()[0] if raw.strip() else "GENERAL"
            if intent not in VALID_INTENTS:
                intent = BusinessIntent.GENERAL.value

            logger.info("Detected intent: %s", intent)
            return {**state, "intent": intent}
        except Exception as exc:
            logger.error("Intent classification failed: %s", exc)
            return {**state, "error": f"Intent agent failed: {exc}"}
