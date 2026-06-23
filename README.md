# Tally AI Analytics

AI-powered business analytics platform that converts natural language questions into SQL queries, retrieves data from PostgreSQL, analyzes results using local LLMs (Ollama), and generates executive summaries.

## Architecture

```text
User Question
      │
      ▼
Intent Agent
      │
      ▼
Schema Agent
      │
      ▼
SQL Generator Agent
      │
      ▼
SQL Validator Agent
      │
      ▼
Retriever Agent
      │
      ▼
Analyzer Agent
      │
      ▼
Summarizer Agent
      │
      ▼
Response
```

### Technology Stack

* Python
* FastAPI
* PostgreSQL
* Ollama
* LangGraph
* Pydantic

---

# Project Structure

```text
project/
│
├── main.py                     # CLI Entry Point
├── requirements.txt
│
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py             # FastAPI Entry Point
│   │
│   ├── agents/
│   │   ├── intent_agent.py
│   │   ├── schema_agent.py
│   │   ├── sql_generator_agent.py
│   │   ├── sql_validator_agent.py
│   │   ├── retriever_agent.py
│   │   ├── analyzer_agent.py
│   │   └── summarizer_agent.py
│   │
│   ├── config/
│   ├── database/
│   ├── schemas/
│   └── services/
│
└── .env
```

---

# Prerequisites

* Python 3.11+
* PostgreSQL
* Ollama

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

---

# Running in CLI Mode

Start the application:

```bash
python main.py
```

Ask questions interactively:

```text
Ask a business question:
show top 10 customers by sales
```

Or run a single question:

```bash
python main.py "show top 10 customers by sales"
```

---

# Running in FastAPI Mode

Start FastAPI server:

```bash
uvicorn app.api.main:app --reload
```

Server URL:

```text
http://127.0.0.1:8000
```

---

# API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

# Health Check

Request:

```http
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

---

# Query Endpoint

Request:

```http
POST /query
Content-Type: application/json
```

Body:

```json
{
  "question": "show top 10 customers by sales"
}
```

Example Response:

```json
{
  "question": "show top 10 customers by sales",
  "intent": "CUSTOMERS",
  "sql_query": "SELECT ...",
  "rows_retrieved": 10,
  "analysis": "...",
  "summary": "...",
  "error": null
}
```

---

# Testing with cURL

```bash
curl -X POST http://127.0.0.1:8000/query \
-H "Content-Type: application/json" \
-d "{\"question\":\"show top 10 customers by sales\"}"
```

---

# Workflow

```text
Client
  │
  ▼
FastAPI
  │
  ▼
AgentOrchestrator
  │
  ├── Intent Agent
  ├── Schema Agent
  ├── SQL Generator Agent
  ├── SQL Validator Agent
  ├── Retriever Agent
  ├── Analyzer Agent
  └── Summarizer Agent
  │
  ├── PostgreSQL
  └── Ollama
```
