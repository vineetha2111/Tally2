"""Unit tests for SQL validation."""

import pytest

from app.exceptions.errors import SQLValidationError
from app.services.sql_validator_service import SQLValidatorService


@pytest.fixture
def validator() -> SQLValidatorService:
    return SQLValidatorService()


def test_valid_select(validator: SQLValidatorService) -> None:
    sql = "SELECT customer_id, SUM(total_amount) FROM sales GROUP BY customer_id LIMIT 10;"
    result = validator.validate(sql)
    assert result.upper().startswith("SELECT")


def test_valid_with_cte(validator: SQLValidatorService) -> None:
    sql = """
    WITH top_sales AS (
        SELECT customer_id, SUM(total_amount) AS revenue FROM sales GROUP BY customer_id
    )
    SELECT * FROM top_sales ORDER BY revenue DESC LIMIT 5;
    """
    result = validator.validate(sql)
    assert "WITH" in result.upper()


def test_reject_delete(validator: SQLValidatorService) -> None:
    with pytest.raises(SQLValidationError, match="DELETE"):
        validator.validate("DELETE FROM sales WHERE sale_id = 1;")


def test_reject_insert(validator: SQLValidatorService) -> None:
    with pytest.raises(SQLValidationError, match="INSERT"):
        validator.validate("INSERT INTO sales (customer_id) VALUES (1);")


def test_reject_drop(validator: SQLValidatorService) -> None:
    with pytest.raises(SQLValidationError, match="DROP"):
        validator.validate("DROP TABLE sales;")


def test_reject_empty(validator: SQLValidatorService) -> None:
    with pytest.raises(SQLValidationError, match="empty"):
        validator.validate("")


def test_reject_multiple_statements(validator: SQLValidatorService) -> None:
    with pytest.raises(SQLValidationError, match="single"):
        validator.validate("SELECT 1; SELECT 2;")
