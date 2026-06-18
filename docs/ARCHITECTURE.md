# Architecture Overview

## System Components

### 1. FastAPI Application
- REST API for data management and processing
- CORS enabled for cross-origin requests
- Health check and status endpoints
- Automatic API documentation with Swagger/ReDoc

### 2. Database Layer
- PostgreSQL database for persistent storage
- SQLAlchemy ORM for database interactions
- Connection pooling for performance
- Automated schema creation with Alembic migrations

### 3. Tally Integration
- ODBC Extractor for connecting to Tally ERP
- Data retrieval from vouchers, ledgers, and invoices
- Support for custom SQL queries and stored procedures
- Scheduled data extraction via APScheduler

### 4. LangGraph Agents
- **Retriever Agent**: Fetches and retrieves relevant documents and data
- **Analyzer Agent**: Performs analysis on financial data and documents
- **Summarizer Agent**: Generates summaries and insights from analyzed data
- **Agent Orchestrator**: Coordinates workflow between agents

### 5. Twilio Integration
- SMS notifications for alerts
- Voice call initiation with TwiML
- Webhook callback handling
- Callback logging and tracking

### 6. Scheduler
- APScheduler for background job execution
- Cron-based job scheduling
- Jobs for:
  - Daily data extraction (02:00 AM)
  - Hourly data analysis
  - Daily report generation (08:00 AM)

### 7. Callback System
- Generic webhook handler for external systems
- Twilio-specific callback support
- Callback logging with request/response tracking

## Data Flow

```
External Data Sources
       ↓
ODBC Extractor → Tally Data
       ↓
PostgreSQL Database
       ↓
Agent Orchestrator
  ├→ Retriever Agent (fetch data)
  ├→ Analyzer Agent (analyze data)
  └→ Summarizer Agent (generate insights)
       ↓
FastAPI API
       ↓
Client Applications
```

## Architecture Decisions

### Database Choice
- PostgreSQL chosen for reliability and performance
- SQLAlchemy ORM provides ORM abstraction
- Alembic for schema versioning and migrations

### Message Queue
- APScheduler with SQLAlchemy job store
- Consider Celery + Redis for advanced use cases

### API Framework
- FastAPI chosen for async capabilities and auto-documentation
- Pydantic for request/response validation

### Agent Framework
- LangGraph for agent orchestration
- LangChain integration for LLM capabilities

## Security Considerations

1. **API Security**
   - Implement JWT authentication
   - API key management
   - Rate limiting

2. **Data Security**
   - Encryption at rest (database)
   - Encryption in transit (HTTPS/TLS)
   - Sensitive data masking in logs

3. **ODBC Connection**
   - Secure credential storage
   - Connection string encryption
   - Network security for Tally server

4. **Twilio Integration**
   - Secure credential management
   - Webhook signature verification
   - Phone number validation

## Scalability Considerations

1. **Database**
   - Connection pooling
   - Query optimization with indexes
   - Read replicas for scaling reads

2. **Application**
   - Horizontal scaling with multiple instances
   - Load balancing with Nginx/HAProxy
   - Caching layer (Redis) for frequently accessed data

3. **Jobs**
   - Distributed scheduler with multiple workers
   - Job queue for long-running tasks
   - Dead letter queue for failed jobs

4. **Agents**
   - Agent caching for common queries
   - Batch processing for efficiency
   - Parallel agent execution
