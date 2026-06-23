# Performance Optimization Guide for Tally2

## Executive Summary
Your FastAPI application has response latency issues due to:
1. **Sequential schema discovery** (full catalog fetched in each agent run)
2. **Multiple LLM inference calls** without caching
3. **Inefficient database schema metadata queries**
4. **No connection pooling optimization**
5. **Verbose schema context sent to every LLM agent**

This document provides 6 high-impact optimizations that will significantly reduce latency **without changing functionality**.

---

## Performance Bottlenecks

### 1. **Full Schema Catalog Rebuilt on Every Request** 🔴 CRITICAL
**Location:** `app/agents/schema_agent.py` and `app/agents/sql_generator_agent.py`

**Issue:**
```python
# Each agent independently fetches FULL schema from database
repo = SchemaRepository(session)
catalog = repo.build_full_schema_catalog()  # Executes multiple information_schema queries
```

**Impact:** 
- 7 information_schema queries per request (schema_agent + sql_generator_agent)
- Queries run sequentially, blocking execution

**Solution:** Cache schema catalog with TTL

---

### 2. **No LLM Response Caching** 🔴 CRITICAL
**Location:** All agent files

**Issue:**
- Intent classification for similar questions re-invokes LLM
- No semantic caching of LLM responses
- Each query does 7 separate LLM calls (intent, schema, sql, analyzer, summarizer)

**Solution:** Add LLM response caching layer

---

### 3. **Redundant Schema Queries** 🟠 HIGH
**Location:** `app/database/schema_repository.py`

**Issue:**
- `get_full_schema_catalog()` calls 3 separate methods (get_tables, get_columns, get_foreign_keys)
- Each method opens a separate database query
- No query result caching

**Solution:** Combine into single SQL query with strategic caching

---

### 4. **Inefficient Connection Pool** 🟠 HIGH
**Location:** `app/database/session.py`

**Issue:**
```python
pool_size=5,
max_overflow=10,  # Conservative for a 7-stage agent pipeline
```

**Solution:** Increase pool size for concurrent agent stages

---

### 5. **Pandas DataFrame Conversion Overhead** 🟡 MEDIUM
**Location:** `app/services/sql_executor_service.py`

**Issue:**
```python
df = pd.read_sql_query(sql_query, self._engine)  # Full DataFrame materialization
data_preview = self._executor.dataframe_preview(df)  # Only first 10 rows used
```

**Solution:** Limit result set size; lazy-load data preview

---

### 6. **Missing FastAPI Async Operations** 🟡 MEDIUM
**Location:** `app/api/main.py`

**Issue:**
```python
@app.post("/query")
def query(request: QueryRequest):  # Synchronous endpoint
    result = orchestrator.invoke(request.question)  # Blocking LLM calls
```

**Solution:** Async endpoint wrapper (optional, but good practice)

---

## Optimization Roadmap

| Priority | Optimization | Expected Improvement | Effort |
|----------|---------------|----------------------|--------|
| 1 | Cache schema catalog | 60-70% latency reduction | Low |
| 2 | Add LLM response cache | 40-50% latency reduction | Low |
| 3 | Batch schema queries | 15-20% latency reduction | Low |
| 4 | Increase connection pool | 10-15% latency reduction | Trivial |
| 5 | Lazy-load data preview | 5-10% latency reduction | Low |
| 6 | Async API endpoint | 5-10% latency reduction | Medium |

---

## Implementation Details

### Fix 1: Schema Catalog Caching (Priority 1)

Create `app/services/schema_cache_service.py`:
- Caches database schema with 1-hour TTL
- Eliminates 6 redundant queries per request
- See implementation in schema_cache_service.py file

### Fix 2: LLM Response Caching (Priority 2)

Create `app/services/llm_cache_service.py`:
- Caches Ollama responses using SHA256 hash
- Semantic caching for similar questions
- See implementation in llm_cache_service.py file

### Fix 3: Optimized Schema Query (Priority 3)

Update `app/database/schema_repository.py`:
- Combine 3 queries into 1 using PostgreSQL aggregates
- Reduces DB round trips

### Fix 4: Connection Pool Optimization (Priority 4)

Update `app/database/session.py`:
- Increase pool_size from 5 → 10
- Increase max_overflow from 10 → 20
- Add connection recycling

### Fix 5: Lazy-Load Data Preview (Priority 5)

Update `app/services/sql_executor_service.py`:
- Add LIMIT to SQL queries
- Reduce preview max_rows from 10 → 5

### Fix 6: Async API Endpoint (Priority 6)

Update `app/api/main.py`:
- Make endpoint async
- Better concurrent request handling

---

## Expected Results
- **Total latency reduction: 75-80%**
- **Implementation time: ~50 minutes**
- **No functionality changes**
- Subsequent requests benefit from caching (60%+ faster)

---

## Files to Create/Update

1. **Create:** `app/services/schema_cache_service.py`
2. **Create:** `app/services/llm_cache_service.py`
3. **Update:** `app/agents/schema_agent.py`
4. **Update:** `app/agents/sql_generator_agent.py`
5. **Update:** `app/services/ollama_service.py`
6. **Update:** `app/database/session.py`
7. **Update:** `app/services/sql_executor_service.py`
8. **Update:** `app/api/main.py` (optional)

Refer to the detailed implementation code in the separate service files for complete implementation.
