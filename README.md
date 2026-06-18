# Tally AI Analytics

A production-ready **local** AI analytics application that answers business questions in natural language. The system discovers your PostgreSQL schema dynamically, generates validated SQL, executes queries, analyzes results, and produces executive summaries — all orchestrated by LangGraph agents powered by Ollama.

Everything runs locally. No cloud APIs, no vector databases, no web framework.

## Features

- Natural language business questions via terminal
- Dynamic schema discovery from `information_schema`
- AI-generated PostgreSQL SELECT queries with validation
- Pandas-based data retrieval and analysis
- LangGraph agent pipeline with 7 specialized agents
- Local LLM via Ollama (`qwen3:8b`, `llama3.1:8b`, `deepseek-r1:8b`)
- Structured logging, typed state, repository and service layers

## Architecture

```
User Question
     │
     ▼
Intent Agent → Schema Agent → SQL Generator → SQL Validator
     │
     ▼
Data Retrieval → Analyzer → Summarizer → Console Output
```

## Quick Start

### 1. Prerequisites

- Python 3.12+
- PostgreSQL 15+
- [Ollama](https://ollama.com/) with a model pulled:

```bash
ollama pull qwen3:8b
# or: ollama pull llama3.1:8b
# or: ollama pull deepseek-r1:8b
```

### 2. Start PostgreSQL

```bash
docker-compose up -d postgres
```

### 3. Install dependencies

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 4. Configure environment

```bash
copy .env.example .env
```

Edit `.env` and set `DATABASE_URL` and `OLLAMA_MODEL`.

### 5. Load sample schema and data

```bash
docker exec -i tally_postgres psql -U tally_user -d tally_db < sql/sample_schema.sql
docker exec -i tally_postgres psql -U tally_user -d tally_db < sql/sample_data.sql
```

Or with local `psql`:

```bash
psql -U tally_user -d tally_db -f sql/sample_schema.sql
psql -U tally_user -d tally_db -f sql/sample_data.sql
```

### 6. Run the application

Interactive mode:

```bash
python main.py
```

Single question:

```bash
python main.py "What are the top 10 customers by sales?"
```

## Example Questions

- What are the top 10 customers by sales?
- Which products have low inventory?
- Show monthly sales trends.
- Which customers contribute the most revenue?
- What are our most profitable products?

## Sample Output

```
==================================================
QUESTION
==================================================
Top 10 customers by sales

==================================================
INTENT
==================================================
SALES

==================================================
GENERATED SQL
==================================================
SELECT ...

==================================================
ROWS RETRIEVED
==================================================
10

==================================================
ANALYSIS
==================================================
...

==================================================
EXECUTIVE SUMMARY
==================================================
...
```

## Project Structure

```
app/
├── agents/              # LangGraph agents + orchestrator
│   ├── intent_agent.py
│   ├── schema_agent.py
│   ├── sql_generator_agent.py
│   ├── sql_validator_agent.py
│   ├── retriever_agent.py
│   ├── analyzer_agent.py
│   ├── summarizer_agent.py
│   └── orchestrator.py
├── config/              # Settings and logging
├── database/            # SQLAlchemy session + schema repository
├── exceptions/          # Custom exceptions
├── schemas/             # Pydantic models and LangGraph state
└── services/            # Ollama, SQL executor, SQL validator

sql/
├── sample_schema.sql    # Sample business tables
└── sample_data.sql      # Sample test data

main.py                  # Terminal application entry point
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://tally_user:tally_password@localhost:5432/tally_db` | PostgreSQL connection |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `qwen3:8b` | Model name |
| `OLLAMA_TEMPERATURE` | `0.1` | LLM temperature |
| `LOG_LEVEL` | `INFO` | Logging level |

## Sample Database Schema

Tables: `customers`, `vendors`, `products`, `inventory`, `sales`, `purchases`

Relationships are defined via foreign keys and discovered automatically at runtime.

## Running Tests

```bash
pytest tests/ -v
```

## Troubleshooting

**Database connection failed**
- Ensure PostgreSQL is running: `docker-compose ps`
- Verify `DATABASE_URL` in `.env`

**Ollama model not found**
- Pull the model: `ollama pull qwen3:8b`
- Confirm Ollama is running: `ollama list`

**SQL validation failed**
- The validator only allows `SELECT` / `WITH ... SELECT` queries
- Check logs in `logs/app.log`

## License

MIT
