"""Reusable local Ollama LLM service."""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from app.config.logging import get_logger
from app.config.settings import Settings, get_settings
from app.exceptions.errors import OllamaServiceError

logger = get_logger("ollama_service")


class OllamaService:
    """Wrapper around langchain-ollama for consistent LLM invocation."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._llm = ChatOllama(
            model=self._settings.ollama_model,
            base_url=self._settings.ollama_base_url,
            temperature=self._settings.ollama_temperature,
            timeout=self._settings.ollama_timeout,
        )

    @property
    def model_name(self) -> str:
        return self._settings.ollama_model

    def invoke(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:
        """Send a prompt to Ollama and return the text response."""
        messages: list[SystemMessage | HumanMessage] = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        try:
            logger.debug("Invoking Ollama model=%s", self.model_name)
            response = self._llm.invoke(messages)
            content = response.content
            if isinstance(content, str):
                return content.strip()
            return str(content).strip()
        except Exception as exc:
            logger.error("Ollama invocation failed: %s", exc)
            raise OllamaServiceError(
                f"Ollama model '{self.model_name}' failed: {exc}"
            ) from exc

    def extract_sql(self, raw_response: str) -> str:
        """Extract SQL from LLM response, stripping markdown fences if present."""
        text = raw_response.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
            if text.lower().startswith("sql"):
                text = text[3:].strip()
        return text.strip().rstrip(";") + ";"
