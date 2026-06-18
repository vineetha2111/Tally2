from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TallyDataSchema(BaseModel):
    """Tally data schema."""

    model_config = ConfigDict(from_attributes=True)

    reference_id: str
    company_name: str
    document_type: str
    document_number: str
    document_date: datetime
    amount: float
    description: str
    status: str = "pending"
    metadata: dict[str, Any] | None = None


class ProcessingJobSchema(BaseModel):
    """Processing job schema."""

    model_config = ConfigDict(from_attributes=True)

    job_id: str
    job_type: str
    status: str = "pending"
    input_data: dict[str, Any]
    output_data: dict[str, Any] | None = None
    error_message: str | None = None


class CallbackPayloadSchema(BaseModel):
    """Callback payload schema."""

    callback_type: str
    source_system: str
    payload: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentExecutionSchema(BaseModel):
    """Tracks analytics agent pipeline execution."""

    model_config = ConfigDict(from_attributes=True)

    agent_type: str
    input_data: dict[str, Any]
    output_data: dict[str, Any] | None = None
    status: str = "pending"
    error_message: str | None = None
    execution_time_ms: float | None = None
