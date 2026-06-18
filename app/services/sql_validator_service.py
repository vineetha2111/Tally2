"""SQL safety validation service."""

import re

import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import DML, Keyword

from app.config.logging import get_logger
from app.exceptions.errors import SQLValidationError

logger = get_logger("sql_validator")

FORBIDDEN_KEYWORDS = frozenset(
    {
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "GRANT",
        "REVOKE",
        "MERGE",
        "REPLACE",
        "EXEC",
        "EXECUTE",
        "CALL",
    }
)

ALLOWED_START_KEYWORDS = frozenset({"SELECT", "WITH"})


class SQLValidatorService:
    """Validates that generated SQL is read-only and safe to execute."""

    def validate(self, sql_query: str) -> str:
        """Validate SQL and return normalized query. Raises SQLValidationError on failure."""
        if not sql_query or not sql_query.strip():
            raise SQLValidationError("SQL query is empty.")

        normalized = sql_query.strip().rstrip(";") + ";"
        upper = normalized.upper()

        for keyword in FORBIDDEN_KEYWORDS:
            if re.search(rf"\b{keyword}\b", upper):
                raise SQLValidationError(
                    f"Forbidden SQL operation detected: {keyword}"
                )

        statements = sqlparse.parse(normalized)
        if not statements:
            raise SQLValidationError("Unable to parse SQL query.")

        if len(statements) > 1:
            raise SQLValidationError("Only a single SQL statement is allowed.")

        statement: Statement = statements[0]
        first_token = self._first_significant_token(statement)
        if first_token not in ALLOWED_START_KEYWORDS:
            raise SQLValidationError(
                f"Only SELECT queries are allowed. Found: {first_token or 'unknown'}"
            )

        if first_token == "WITH":
            if not self._with_contains_select(statement):
                raise SQLValidationError("WITH clause must contain a SELECT statement.")

        logger.info("SQL validation passed")
        return normalized

    @staticmethod
    def _first_significant_token(statement: Statement) -> str | None:
        for token in statement.tokens:
            if token.is_whitespace or token.ttype in (sqlparse.tokens.Comment,):
                continue
            if token.ttype is DML:
                return token.value.upper()
            if token.ttype is Keyword and token.value.upper() in ALLOWED_START_KEYWORDS:
                return token.value.upper()
            value = token.value.strip().upper()
            if value in ALLOWED_START_KEYWORDS:
                return value
        return None

    @staticmethod
    def _with_contains_select(statement: Statement) -> bool:
        sql_upper = statement.value.upper()
        return "SELECT" in sql_upper
