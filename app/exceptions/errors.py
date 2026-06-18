"""Custom exception hierarchy for the analytics pipeline."""


class AnalyticsError(Exception):
    """Base exception for analytics application errors."""


class SQLValidationError(AnalyticsError):
    """Raised when generated SQL fails safety validation."""


class DatabaseError(AnalyticsError):
    """Raised when database operations fail."""


class OllamaServiceError(AnalyticsError):
    """Raised when the local Ollama LLM service fails."""
