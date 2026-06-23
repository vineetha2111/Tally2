
from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.orchestrator import AgentOrchestrator
from app.config.settings import get_settings

router = APIRouter(tags=["Analytics"])

class QueryRequest(BaseModel):
    question: str

@router.post("/query")
async def query(request: QueryRequest):
    settings = get_settings()
    orchestrator = AgentOrchestrator(settings)

    result = orchestrator.invoke(request.question)

    return {
        "question": result.question,
        "intent": result.intent,
        "sql_query": result.sql_query,
        "analysis": result.analysis,
        "summary": result.summary,
        "error": result.error,
    }
