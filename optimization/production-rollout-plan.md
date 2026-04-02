# LightRAG Production Rollout Plan

> **Target:** Local machine (Windows), small team (3-10 users), with path to cloud deployment.
> **Current state:** Dev setup — no auth, no SSL, single worker, free-tier Supabase, NetworkX graph.

---

## Phase 1: Security (Critical)

### 1.1 Enable Authentication

| | |
|---|---|
| **What** | Set `AUTH_ACCOUNTS` with bcrypt-hashed passwords, `TOKEN_SECRET` to a strong random value, `TOKEN_EXPIRE_HOURS=48` |
| **Motivation** | Currently anyone on the network can access, modify, and delete all data. Zero access control. |
| **Impact** | Only authenticated users can access the system. JWT-based session management via WebUI and API. |
| **Risk** | Low — additive change. Users need to log in via WebUI. If TOKEN_SECRET is lost, all sessions invalidate (recoverable by setting a new one). |

### 1.2 Set API Key

| | |
|---|---|
| **What** | Set `LIGHTRAG_API_KEY` for programmatic access, `WHITELIST_PATHS=/health` |
| **Motivation** | API endpoints are completely open. Any script can query, insert, or delete documents. |
| **Impact** | All API calls require `X-API-Key` header. Health endpoint stays public for monitoring. |
| **Risk** | Low — WebUI uses JWT auth (Task 1.1), API key is for external integrations only. Breaking change for any existing API consumers (none currently). |

### 1.3 Configure CORS

| | |
|---|---|
| **What** | Set `CORS_ORIGINS` to specific allowed origins (e.g., `http://localhost:9621`) |
| **Motivation** | Default is `*` (all origins). Any website could make requests to the API if a user is authenticated. |
| **Impact** | Only specified frontends can interact with the API. |
| **Risk** | Low — if origins are too restrictive, WebUI may break. Easy to adjust. |

### 1.4 Rotate Exposed Credentials

| | |
|---|---|
| **What** | Rotate OpenAI API key, reset Supabase DB password, update `.env` |
| **Motivation** | Current credentials were exposed in plaintext during setup. They should be considered compromised. |
| **Impact** | Old credentials stop working immediately. All systems use fresh secrets. |
| **Risk** | Medium — if `.env` is not updated correctly, server won't start. Verify connection after rotation. |

---

## Phase 2: Reliability

### 2.1 Increase Workers

| | |
|---|---|
| **What** | Set `WORKERS=2` |
| **Motivation** | Single worker means one slow query blocks all other requests. A team of 3-10 will experience timeouts during document processing. |
| **Impact** | Concurrent request handling. One slow document processing doesn't block queries. |
| **Risk** | Low — doubles memory usage. Monitor RAM. NetworkX graph is loaded per-worker (file-based), so graph mutations need care. At 2 workers this is manageable. |

### 2.2 Configure Timeouts

| | |
|---|---|
| **What** | Set `TIMEOUT=180`, `LLM_TIMEOUT=180` |
| **Motivation** | Default timeout may be too short for large document processing. Too long wastes resources on hung requests. |
| **Impact** | Predictable request lifecycle. Failed LLM calls don't hang indefinitely. |
| **Risk** | Low — if set too low, large documents may fail. 180s is a safe middle ground. |

### 2.3 Configure Logging

| | |
|---|---|
| **What** | Set `LOG_LEVEL=INFO`, `LOG_DIR=./logs`, `LOG_MAX_BYTES=10485760`, `LOG_BACKUP_COUNT=5` |
| **Motivation** | Logs currently go to default location with no rotation. Disk can fill up. No audit trail. |
| **Impact** | Structured, rotated logs. Easier debugging and monitoring. |
| **Risk** | Low — additive. Disk usage capped at ~50MB (5 x 10MB). |

### 2.4 PostgreSQL Connection Resilience

| | |
|---|---|
| **What** | Set `POSTGRES_CONNECTION_RETRIES=10`, `POSTGRES_CONNECTION_RETRY_BACKOFF=3.0`, `POSTGRES_CONNECTION_RETRY_BACKOFF_MAX=30.0` |
| **Motivation** | Supabase free tier can pause after inactivity. Without retries, any hiccup crashes the server. |
| **Impact** | Server auto-recovers from transient DB connection failures. |
| **Risk** | Low — already partially configured. Making it explicit. |

---

## Phase 3: Performance

### 3.1 Enable Reranking

| | |
|---|---|
| **What** | Set `RERANK_BINDING=cohere` or `jina`, configure model and API key, `MIN_RERANK_SCORE=0.0` |
| **Motivation** | Without reranking, retrieved chunks are ordered by vector similarity only. Reranking significantly improves answer relevance for ambiguous queries. |
| **Impact** | Better query results. +200-500ms latency per query. Additional API cost (~$0.001/query). |
| **Risk** | Medium — adds external dependency. If rerank service is down, queries may fail. Mitigate with `RERANK_BY_DEFAULT=False` and enable per-query. |

### 3.2 Tune Query Parameters

| | |
|---|---|
| **What** | Set `MAX_TOTAL_TOKENS=30000`, `MAX_ENTITY_TOKENS=6000`, `MAX_RELATION_TOKENS=8000`, `KG_CHUNK_PICK_METHOD=VECTOR` |
| **Motivation** | Default parameters are generic. Tuning improves relevance and reduces LLM costs for the team's specific document types. |
| **Impact** | More relevant context sent to LLM. Lower token usage for simple queries. |
| **Risk** | Low — all adjustable at runtime. If too restrictive, answers may miss context. Start with defaults and tune. |

### 3.3 Evaluate LLM Model Upgrade

| | |
|---|---|
| **What** | Consider switching `LLM_MODEL` from `gpt-4o-mini` to `gpt-4o` |
| **Motivation** | gpt-4o-mini is cheaper but produces lower quality entity extraction and query responses. |
| **Impact** | Better entity extraction, more accurate answers. ~10x cost increase per token. |
| **Risk** | Medium — significant cost increase. Monitor usage at platform.openai.com/usage. |

### 3.4 Tune Concurrency

| | |
|---|---|
| **What** | Set `MAX_ASYNC=8`, `EMBEDDING_FUNC_MAX_ASYNC=8`, `EMBEDDING_BATCH_NUM=20` |
| **Motivation** | Higher parallelism speeds up document ingestion when multiple team members upload concurrently. |
| **Impact** | Faster document processing. Higher burst API usage. |
| **Risk** | Medium — may hit OpenAI rate limits. Monitor 429 errors and reduce if needed. |

---

## Phase 4: Observability

### 4.1 Enable Langfuse Tracing

| | |
|---|---|
| **What** | Install `lightrag-hku[observability]`, configure Langfuse keys, set `LANGFUSE_ENABLE_TRACE=true` |
| **Motivation** | No visibility into LLM calls — cost, latency, token usage, error rates are invisible. Can't debug bad answers. |
| **Impact** | Full trace of every LLM call. Cost tracking. Latency monitoring. Query debugging. |
| **Risk** | Low — additive. Free tier at cloud.langfuse.com. Slight latency overhead for trace shipping. |

### 4.2 Enable Performance Timing Logs

| | |
|---|---|
| **What** | Set `LIGHTRAG_PERFORMANCE_TIMING_LOGS=true` |
| **Motivation** | Can't identify bottlenecks without timing data — is it the LLM, embedding, or DB? |
| **Impact** | Per-request timing breakdown in logs. |
| **Risk** | Low — increases log verbosity. Useful for tuning, can disable once stable. |

---

## Phase 5: Future-Proofing

### 5.1 Graph Storage Migration Path

| | |
|---|---|
| **What** | Plan migration from NetworkX to Neo4j (Aura free tier or self-hosted Docker). Note: PGGraphStorage requires Apache AGE, not available on Supabase. |
| **Motivation** | NetworkX stores the entire graph in memory and a single file. Not scalable, not safe for concurrent writes from multiple workers, no backup integration. |
| **Impact** | Graph survives restarts reliably. Multi-worker writes. Proper backup via Neo4j tools. |
| **Risk** | High — data migration required. Neo4j adds infrastructure complexity. Defer until hitting NetworkX limits or moving to Docker/K8s. |

### 5.2 Docker Deployment Preparation

| | |
|---|---|
| **What** | Run `make env-base`, `make env-storage`, `make env-server` to generate compose files. Run `make env-security-check`. Stage SSL certs in `./data/certs/`. |
| **Motivation** | Current setup is tied to the local machine. Docker enables reproducible, portable deployments. |
| **Impact** | One-command deployment. Portable across environments. |
| **Risk** | Medium — Docker adds complexity. Requires Docker Desktop on Windows. Test thoroughly before switching. |

### 5.3 Supabase Plan Evaluation

| | |
|---|---|
| **What** | Evaluate upgrade from Free to Pro tier ($25/month) |
| **Motivation** | Free tier: 500MB DB limit, pauses after 7 days inactivity. Pro: 8GB, always-on, daily backups. |
| **Impact** | Reliable, always-on database with proper backups. |
| **Risk** | Low — straightforward upgrade via Supabase dashboard. |

---

## Verification Checklist

After each phase, run:

```bash
# 1. Restart server
lightrag-server

# 2. Health check
curl http://localhost:9621/health

# 3. Auth test (should return 401 after Phase 1)
curl http://localhost:9621/query -X POST -H "Content-Type: application/json" -d '{"query":"test"}'

# 4. Query test (with auth)
curl http://localhost:9621/query -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"query":"Who created LightRAG?","mode":"mix"}'

# 5. Log check
ls -la ./logs/

# 6. DB check
npx supabase db query "SELECT count(*) FROM lightrag_doc_full"
```
