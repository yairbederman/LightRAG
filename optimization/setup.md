# LightRAG Setup Guide

> Step-by-step instructions for installing LightRAG on a fresh machine with Supabase + OpenAI.

---

## Prerequisites

| Requirement | Version | Check |
|-------------|---------|-------|
| Python | 3.10+ | `python --version` |
| pip | latest | `pip --version` |
| Git | any | `git --version` |
| Supabase CLI | latest | `npx supabase --version` |
| Node.js/npm | 18+ | `node --version` |

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/HKUDS/LightRAG.git
cd LightRAG
```

## Step 2: Install Python Dependencies

```bash
pip install -e ".[api]"
pip install asyncpg pgvector
```

The `[api]` extra includes: FastAPI, Uvicorn, OpenAI SDK, document processing (PDF, DOCX), authentication (JWT, bcrypt).

`asyncpg` and `pgvector` are needed for the Supabase PostgreSQL backend.

## Step 3: Apply Supabase Pooler SSL Patch

Supabase's connection pooler uses certificates that `asyncpg` rejects by default. A custom SSL mode (`require-no-verify`) must be added.

**File:** `lightrag/kg/postgres_impl.py`

Find the `_create_ssl_context` method (around line 218). After the block:

```python
        if ssl_mode in ["disable", "allow", "prefer", "require"]:
            if ssl_mode == "disable":
                return None
            elif ssl_mode in ["require", "prefer", "allow"]:
                # Return None for simple SSL requirement, handled in initdb
                return None
```

Add immediately after:

```python
        # SSL without certificate verification (e.g. Supabase pooler)
        if ssl_mode == "require-no-verify":
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return context
```

**Important:** If installed via pip (not editable mode), you must also patch the copy in `site-packages`:

```bash
# Find the site-packages location
python -c "import lightrag.kg.postgres_impl as m; print(m.__file__)"

# Copy the patched file there (if different from your repo)
```

## Step 4: Set Up Supabase

### Option A: Use Existing Supabase Project

Get the **Session pooler** connection string from:
`Supabase Dashboard > Project > Settings > Database > Connection string > Session mode`

It should look like:
```
postgresql://postgres.YOURREF:PASSWORD@aws-X-REGION.pooler.supabase.com:5432/postgres
```

Note these values:
- **Host**: `aws-X-REGION.pooler.supabase.com` (copy exactly — the `X` and region vary per project)
- **Port**: `5432` (session mode)
- **User**: `postgres.YOURREF`
- **Password**: your database password
- **Database**: `postgres`

### Option B: Create a New Supabase Project

1. Go to [supabase.com/dashboard](https://supabase.com/dashboard)
2. Create a new project (note the region)
3. Wait for it to become `ACTIVE_HEALTHY`
4. Enable pgvector: run `CREATE EXTENSION IF NOT EXISTS vector;` in the SQL Editor
5. Get the Session pooler connection string as described in Option A

### Enable pgvector Extension

Via SQL Editor in dashboard or via CLI:

```bash
npx supabase link --project-ref YOUR_PROJECT_REF
npx supabase db query "CREATE EXTENSION IF NOT EXISTS vector;"
```

## Step 5: Create the `.env` File

Copy this template to `.env` in the project root and fill in the values:

```env
###########################
### Server Configuration
###########################
HOST=0.0.0.0
PORT=9621
WEBUI_TITLE='LightRAG'
WEBUI_DESCRIPTION='Graph Based RAG System'

###########################
### LLM Configuration
###########################
LLM_BINDING=openai
LLM_BINDING_HOST=https://api.openai.com/v1
LLM_BINDING_API_KEY=<YOUR_OPENAI_API_KEY>
LLM_MODEL=gpt-4o-mini

###########################
### Embedding Configuration
###########################
EMBEDDING_BINDING=openai
EMBEDDING_BINDING_HOST=https://api.openai.com/v1
EMBEDDING_BINDING_API_KEY=<YOUR_OPENAI_API_KEY>
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIM=3072
EMBEDDING_TOKEN_LIMIT=8192
EMBEDDING_SEND_DIM=false

###########################
### Concurrency
###########################
MAX_ASYNC=4
MAX_PARALLEL_INSERT=2

###########################
### Document Processing
###########################
ENABLE_LLM_CACHE_FOR_EXTRACT=true
SUMMARY_LANGUAGE=English

###########################
### Reranking (disabled)
###########################
RERANK_BINDING=null

###########################
### PostgreSQL (Supabase)
###########################
POSTGRES_HOST=<aws-X-REGION.pooler.supabase.com>
POSTGRES_PORT=5432
POSTGRES_USER=<postgres.YOUR_PROJECT_REF>
POSTGRES_PASSWORD='<YOUR_DB_PASSWORD>'
POSTGRES_DATABASE=postgres
POSTGRES_MAX_CONNECTIONS=25
POSTGRES_ENABLE_VECTOR=true
POSTGRES_VECTOR_INDEX_TYPE=HNSW_HALFVEC
POSTGRES_HNSW_M=16
POSTGRES_HNSW_EF=200
POSTGRES_STATEMENT_CACHE_SIZE=0
POSTGRES_SSL_MODE=require-no-verify

###########################
### Storage Selection
###########################
LIGHTRAG_KV_STORAGE=PGKVStorage
LIGHTRAG_DOC_STATUS_STORAGE=PGDocStatusStorage
LIGHTRAG_GRAPH_STORAGE=NetworkXStorage
LIGHTRAG_VECTOR_STORAGE=PGVectorStorage
```

### Placeholders to Replace

| Placeholder | Where to Get It |
|-------------|----------------|
| `<YOUR_OPENAI_API_KEY>` | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `<aws-X-REGION.pooler.supabase.com>` | Supabase Dashboard > Settings > Database > Connection string (Session mode) |
| `<postgres.YOUR_PROJECT_REF>` | Same connection string — the user field |
| `<YOUR_DB_PASSWORD>` | Set during project creation, or reset in Dashboard > Settings > Database |

## Step 6: Verify Database Connection

```bash
python -c "
import psycopg2
conn = psycopg2.connect(
    host='YOUR_POOLER_HOST',
    port=5432,
    user='postgres.YOUR_REF',
    password='YOUR_PASSWORD',
    database='postgres',
    sslmode='require'
)
cur = conn.cursor()
cur.execute('SELECT version()')
print('Connected:', cur.fetchone())
conn.close()
"
```

If this fails with "Tenant or user not found", double-check the **exact hostname** from the Supabase dashboard — it varies per project (e.g., `aws-0-` vs `aws-1-`).

## Step 7: Start the Server

```bash
lightrag-server
```

You should see:
- `PostgreSQL, Connected to database at ... with SSL`
- `Application startup complete.`
- `Uvicorn running on http://0.0.0.0:9621`

## Step 8: Verify

```bash
# Health check
curl http://localhost:9621/health

# Open WebUI in browser
# http://localhost:9621
```

## Step 9: Upload a Test Document

Either use the WebUI at http://localhost:9621, or via API:

```bash
curl -X POST http://localhost:9621/documents/upload \
  -F "file=@path/to/your/document.txt"
```

Wait for processing, then query:

```bash
curl -X POST http://localhost:9621/query \
  -H "Content-Type: application/json" \
  -d '{"query": "your question here", "mode": "mix"}'
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: fastapi` | Missing API extras | `pip install "lightrag-hku[api]"` |
| `Tenant or user not found` | Wrong pooler hostname | Copy exact hostname from Supabase Dashboard > Settings > Database |
| `SSL: CERTIFICATE_VERIFY_FAILED` | Missing SSL patch | Apply Step 3 patch to `postgres_impl.py` |
| `column cannot have more than 2000 dimensions for hnsw index` | HNSW doesn't support 3072 dims | Set `POSTGRES_VECTOR_INDEX_TYPE=HNSW_HALFVEC` |
| `function create_graph(unknown) does not exist` | PGGraphStorage needs Apache AGE | Use `LIGHTRAG_GRAPH_STORAGE=NetworkXStorage` (Supabase doesn't support AGE) |
| `gaierror: getaddrinfo failed` | Direct DB host is IPv6-only, network is IPv4 | Use the pooler hostname instead of `db.*.supabase.co` |
| Server shows "only whitespace" for PDF | Scanned/image PDF, no text layer | Pre-process with OCR before uploading |

---

## Architecture Summary

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────────┐
│   WebUI /    │────▶│  LightRAG    │────▶│  OpenAI API         │
│   API Client │     │  Server      │     │  (LLM + Embeddings) │
└─────────────┘     │  :9621       │     └─────────────────────┘
                    │              │
                    │              │────▶ Supabase PostgreSQL
                    │              │      (KV, Vector, DocStatus)
                    │              │
                    │              │────▶ NetworkX (local file)
                    └──────────────┘      (Graph storage)
```

## What's NOT Included (See production-rollout-plan.md)

- Authentication (AUTH_ACCOUNTS, API keys)
- SSL/TLS for the server
- CORS configuration
- Logging setup
- Reranking
- Observability (Langfuse)
