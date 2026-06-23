from fastapi import FastAPI  
from pydantic import BaseModel

from app.agents.orchestrator import AgentOrchestrator
from app.config.settings import get_settings
from app.database.session import check_database_connection

app = FastAPI()

settings = get_settings()
check_database_connection(settings)

orchestrator = AgentOrchestrator(settings)


class QueryRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/query")
def query(request: QueryRequest):

    result = orchestrator.invoke(request.question)

    return {
        "question": result.question,
        "intent": result.intent,
        "sql_query": result.sql_query,
        "analysis": result.analysis,
        "summary": result.summary,
        "error": result.error,
    }