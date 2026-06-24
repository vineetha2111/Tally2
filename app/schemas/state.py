"""LangGraph workflow state and analytics domain schemas."""

from enum import Enum
from typing import Any

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import TypedDict


class BusinessIntent(str, Enum):
    """Supported business intent categories."""

    SALES = "SALES"
    CUSTOMERS = "CUSTOMERS"
    INVENTORY = "INVENTORY"
    FINANCE = "FINANCE"
    PURCHASES = "PURCHASES"
    VENDORS = "VENDORS"
    PROFIT = "PROFIT"
    GENERAL = "GENERAL"


class AnalyticsStateModel(BaseModel):
    """Strongly typed Pydantic model for the analytics pipeline state."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    question: str = ""
    rewritten_question: str = ""
    intent: str = ""

    schema_context: str = ""

    schema_catalog: dict[str, Any] = Field(
        default_factory=dict
    )

    sql_query: str = ""

    query_results: pd.DataFrame = Field(
        default_factory=pd.DataFrame
    )

    analysis: str = ""
    summary: str = ""

    error: str | None = None

    def to_display_dict(
        self,
    ) -> dict[str, Any]:
        """Serialize state for terminal display."""

        return {
            "question": self.question,
            "rewritten_question": self.rewritten_question,
            "intent": self.intent,
            "schema_context": self.schema_context,
            "schema_catalog": self.schema_catalog,
            "sql_query": self.sql_query,
            "row_count": len(
                self.query_results
            ),
            "analysis": self.analysis,
            "summary": self.summary,
            "error": self.error,
        }


def merge_error(
    existing: str | None,
    new: str | None,
) -> str | None:
    """Reducer: keep the first non-null error."""

    return existing or new


class GraphState(TypedDict):
    """LangGraph state dictionary."""

    question: str
    rewritten_question: str

    intent: str

    schema_context: str

    schema_catalog: dict[str, Any]

    sql_query: str

    query_results: pd.DataFrame

    analysis: str
    summary: str

    error: str | None


def initial_state(
    question: str,
) -> GraphState:
    """Create initial workflow state from a user question."""

    return GraphState(
        question=question,
        rewritten_question="",
        intent="",
        schema_context="",
        schema_catalog={},
        sql_query="",
        query_results=pd.DataFrame(),
        analysis="",
        summary="",
        error=None,
    )


def graph_state_to_model(
    state: GraphState,
) -> AnalyticsStateModel:
    """Convert LangGraph state to Pydantic model."""

    return AnalyticsStateModel(
        **state
    )