# LightRAG Interactive Setup Guide

> Follow each step in order. Every step has a **Verify** command — run it before moving on.
> If verification fails, check the **Checkpoint** section before proceeding.

---

## Step 0: Prerequisites Check

Run each command. If any fails, install the missing tool before continuing.

```bash
python --version    # Need 3.10+
pip --version       # Any recent version
git --version       # Any version
node --version      # Need 18+ (for Supabase CLI)
npm --version       # Comes with Node.js
```

**Install links (if missing):**
| Tool | Install |
|------|---------|
| Python 3.10+ | [python.org/downloads](https://python.org/downloads) |
| Node.js 18+ | [nodejs.org](https://nodejs.org) |
| Git | [git-scm.com](https://git-scm.com) |

### Verify
```bash
python --version && pip --version && git --version && node --version
```

**Checkpoint:**
- All four commands return version numbers? Proceed to Step 1.
- Any command fails? Install it first, then re-verify.

---

## Step 1: Clone & Install

### 1a. Clone the repository

```bash
git clone https://github.com/HKUDS/LightRAG.git
cd LightRAG
```

### 1b. Install Python dependencies

```bash
pip install -e ".[api]"
pip install asyncpg pgvector psycopg2-binary
```

What you're installing:
| Package | Purpose |
|---------|---------|
| `.[api]` | LightRAG core + FastAPI server + OpenAI SDK + document processing (PDF, DOCX) |
| `asyncpg` | PostgreSQL async driver (needed for Supabase) |
| `pgvector` | PostgreSQL vector extension support |
| `psycopg2-binary` | PostgreSQL sync driver (for connection testing) |

### Verify
```bash
lightrag-server --help
```

**Checkpoint:**
- See help text with server options? Proceed to Step 2.
- `ModuleNotFoundError`? Re-run `pip install -e ".[api]"` and check for errors.
- `command not found`? Make sure pip's bin directory is in your PATH.

---

## Step 2: Choose Your LLM Provider

Pick one. **If unsure, use OpenAI** — it's the most tested and easiest to set up.

| Provider | Model | Cost | Setup |
|----------|-------|------|-------|
| **OpenAI** (default) | gpt-4o-mini | ~$0.15/1M input tokens | Get API key from dashboard |
| Ollama (local) | llama3, qwen3, etc. | Free (uses your GPU) | Install Ollama + pull model |
| Google Gemini | gemini-2.5-flash | Free tier available | Get API key from AI Studio |
| Azure OpenAI | gpt-4o (deployed) | Pay-as-you-go | Requires Azure subscription |
| AWS Bedrock | Claude, etc. | Pay-as-you-go | Requires AWS credentials |

### If you chose OpenAI (default):

**Do this:**
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Save it somewhere safe — you'll need it in Step 4

### Verify your API key works
```bash
python -c "
from openai import OpenAI
client = OpenAI(api_key='YOUR_KEY_HERE')
r = client.chat.completions.create(model='gpt-4o-mini', messages=[{'role':'user','content':'Say OK'}], max_tokens=5)
print('LLM works:', r.choices[0].message.content)
"
```

### If you chose Ollama (local):
```bash
# Install Ollama: https://ollama.ai
ollama pull qwen2.5:7b
ollama serve  # Keep running in background
```

### Verify (Ollama):
```bash
curl http://localhost:11434/api/tags
```

**Checkpoint:**
- Got a response from your LLM provider? Proceed to Step 3.
- `401 Unauthorized`? Check your API key.
- `429 Rate limited`? You may need to add billing to your OpenAI account.

---

## Step 3: Choose Your Storage Backend

Pick one row. **If unsure, start with Local** — you can switch to Supabase later without losing the setup.

| Backend | Best For | What You Need | Data Persistence |
|---------|----------|---------------|-----------------|
| **Local (JSON/NanoVectorDB)** | Testing, single user | Nothing — works out of the box | Local files only |
| **Supabase (PostgreSQL)** (recommended) | Team use, cloud backup | Free Supabase account | Cloud database |
| Self-hosted PostgreSQL | Full control | Docker or PostgreSQL install | Your server |
| MongoDB | Document-heavy workloads | MongoDB Atlas or Docker | Depends on setup |

---

### Path A: Local Storage (simplest)

No setup needed. Skip to **Step 4** and use the **Local Storage** `.env` template.

---

### Path B: Supabase Setup (recommended for teams)

#### B1. Create a Supabase Project

**Do this:**
1. Go to [supabase.com/dashboard](https://supabase.com/dashboard) and sign in
2. Click **New Project**
3. Choose a name and region (pick one close to you)
4. Set a **database password** — save it, you'll need it later
5. Wait until status shows **ACTIVE_HEALTHY** (1-2 minutes)

#### B2. Enable pgvector Extension

**Do this:**
1. In the Supabase dashboard, go to **SQL Editor**
2. Run this query:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

#### Verify
```sql
-- Run in the same SQL Editor:
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
```
You should see `vector` in the result.

#### B3. Get Your Connection String

This is the most critical step. The **exact hostname matters**.

**Do this:**
1. Go to **Settings > Database** in your Supabase project
2. Scroll to **Connection string**
3. Select **Session** mode (not Transaction, not Direct)
4. Copy the connection string. It looks like:

```
postgresql://postgres.ABCDEF:[YOUR-PASSWORD]@aws-X-eu-central-1.pooler.supabase.com:5432/postgres
```

5. Extract these values and save them:

| Value | Example | Where in the string |
|-------|---------|-------------------|
| **Host** | `aws-1-eu-central-1.pooler.supabase.com` | Between `@` and `:5432` |
| **Port** | `5432` | After the host |
| **User** | `postgres.ABCDEF` | Between `://` and `:` |
| **Password** | Your database password | Between user `:` and `@` |
| **Database** | `postgres` | After the last `/` |

> **WARNING:** The host starts with `aws-X-` where X is a number (0, 1, 2...). Copy it exactly. Using the wrong number causes "Tenant or user not found" errors.

#### B4. Apply the Supabase SSL Patch

Supabase's connection pooler uses certificates that Python's `asyncpg` rejects. We need to add a custom SSL mode.

**Do this:**

Open `lightrag/kg/postgres_impl.py` and find the `_create_ssl_context` method (around line 218).

Find this block:
```python
        if ssl_mode in ["disable", "allow", "prefer", "require"]:
            if ssl_mode == "disable":
                return None
            elif ssl_mode in ["require", "prefer", "allow"]:
                # Return None for simple SSL requirement, handled in initdb
                return None
```

Add this **immediately after** that block:
```python
        # SSL without certificate verification (e.g. Supabase pooler)
        if ssl_mode == "require-no-verify":
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return context
```

**If you installed with `pip install` (not editable `-e` mode):**
```bash
# Find where the file actually lives:
python -c "import lightrag.kg.postgres_impl as m; print(m.__file__)"

# Apply the same patch to THAT file too
```

#### Verify (patch applied)
```bash
python -c "
import lightrag.kg.postgres_impl as m
import inspect
src = inspect.getsource(m.PostgreSQLDB._create_ssl_context)
assert 'require-no-verify' in src, 'PATCH NOT FOUND'
print('SSL patch: OK')
"
```

#### B5. Test the Database Connection

Replace the placeholders with your actual values from Step B3:

```bash
python -c "
import psycopg2
conn = psycopg2.connect(
    host='aws-X-REGION.pooler.supabase.com',
    port=5432,
    user='postgres.YOUR_REF',
    password='YOUR_PASSWORD',
    database='postgres',
    sslmode='require'
)
cur = conn.cursor()
cur.execute('SELECT version()')
print('Connected:', cur.fetchone()[0])
conn.close()
"
```

**Checkpoint:**
- See `Connected: PostgreSQL 17.x ...`? Proceed to Step 4.
- `Tenant or user not found`? Double-check the **exact hostname** from the dashboard (Step B3). The number after `aws-` matters.
- `SSL: CERTIFICATE_VERIFY_FAILED`? The patch from Step B4 wasn't applied. Re-check.
- `connection refused`? Check that port is `5432` (Session mode), not `6543` (Transaction mode).
- `password authentication failed`? Reset the password in Dashboard > Settings > Database.

---

## Step 4: Create the `.env` File

Create a file called `.env` in the project root directory. Use the template matching your storage choice.

---

### Template A: Local Storage

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
### Storage (Local)
###########################
LIGHTRAG_KV_STORAGE=JsonKVStorage
LIGHTRAG_DOC_STATUS_STORAGE=JsonDocStatusStorage
LIGHTRAG_GRAPH_STORAGE=NetworkXStorage
LIGHTRAG_VECTOR_STORAGE=NanoVectorDBStorage
```

**Placeholders to fill:**
| Placeholder | Where to Get It |
|-------------|----------------|
| `<YOUR_OPENAI_API_KEY>` | From Step 2 |

---

### Template B: Supabase + OpenAI (recommended)

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
POSTGRES_HOST=<YOUR_POOLER_HOST>
POSTGRES_PORT=5432
POSTGRES_USER=<YOUR_POOLER_USER>
POSTGRES_PASSWORD='<YOUR_DB_PASSWORD>'
POSTGRES_DATABASE=postgres
POSTGRES_MAX_CONNECTIONS=5   # Must be ≤ 1/3 of Supabase pooler "Connection pool size" (default 15 for Nano)
POSTGRES_ENABLE_VECTOR=true
POSTGRES_VECTOR_INDEX_TYPE=HNSW_HALFVEC
POSTGRES_HNSW_M=16
POSTGRES_HNSW_EF=200
POSTGRES_STATEMENT_CACHE_SIZE=0
POSTGRES_SSL_MODE=require-no-verify

###########################
### Storage (Supabase)
### WARNING: Do NOT set WORKSPACE env var.
### LightRAG defaults to 'default' internally.
### Setting it causes a workspace mismatch.
###########################
LIGHTRAG_KV_STORAGE=PGKVStorage
LIGHTRAG_DOC_STATUS_STORAGE=PGDocStatusStorage
LIGHTRAG_GRAPH_STORAGE=NetworkXStorage
LIGHTRAG_VECTOR_STORAGE=PGVectorStorage
```

**Placeholders to fill:**
| Placeholder | Where to Get It |
|-------------|----------------|
| `<YOUR_OPENAI_API_KEY>` | From Step 2 |
| `<YOUR_POOLER_HOST>` | From Step B3 (e.g., `aws-1-eu-central-1.pooler.supabase.com`) |
| `<YOUR_POOLER_USER>` | From Step B3 (e.g., `postgres.abcdef123456`) |
| `<YOUR_DB_PASSWORD>` | From Step B3 |

---

### Template C: Ollama + Local Storage (fully offline)

```env
###########################
### Server Configuration
###########################
HOST=0.0.0.0
PORT=9621
WEBUI_TITLE='LightRAG'
WEBUI_DESCRIPTION='Graph Based RAG System'

###########################
### LLM Configuration (Ollama)
###########################
LLM_BINDING=ollama
LLM_BINDING_HOST=http://localhost:11434
LLM_MODEL=qwen2.5:7b
OLLAMA_LLM_NUM_CTX=32768

###########################
### Embedding Configuration (Ollama)
###########################
EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIM=768
OLLAMA_EMBEDDING_NUM_CTX=8192

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
### Storage (Local)
###########################
LIGHTRAG_KV_STORAGE=JsonKVStorage
LIGHTRAG_DOC_STATUS_STORAGE=JsonDocStatusStorage
LIGHTRAG_GRAPH_STORAGE=NetworkXStorage
LIGHTRAG_VECTOR_STORAGE=NanoVectorDBStorage
```

**Placeholders to fill:** None — fully self-contained. Just make sure Ollama is running with the models pulled.

---

### Verify (all templates)
```bash
# Check no unfilled placeholders remain:
grep -c "<" .env
```

**Checkpoint:**
- Returns `0`? Proceed to Step 5.
- Returns a number? You still have `<PLACEHOLDER>` values to fill in.

---

## Step 5: Start the Server

```bash
lightrag-server
```

### What to look for in the output

**If using Supabase**, you should see these lines (in order):
```
PostgreSQL, SSL configuration applied
PostgreSQL, Connected to database at aws-X-....pooler.supabase.com:5432/postgres with SSL
Application startup complete.
Uvicorn running on http://0.0.0.0:9621
```

**If using Local storage**, you should see:
```
Created new empty graph file: .../graph_chunk_entity_relation.graphml
Application startup complete.
Uvicorn running on http://0.0.0.0:9621
```

### Verify
```bash
curl -s http://localhost:9621/health | python -m json.tool
```

Look for `"status": "healthy"` and confirm the storage types match your choice.

**Checkpoint:**
- See `healthy` + correct storage? Proceed to Step 6.
- Server crashes on startup? Check the error against the Troubleshooting table below.
- `curl` fails? The server didn't start — check the terminal output for errors.

---

## Step 6: End-to-End Test

### 6a. Create a test document

Create a file called `test_doc.txt` with some content:
```
Artificial intelligence (AI) is the simulation of human intelligence by machines.
Machine learning is a subset of AI that enables systems to learn from data.
Deep learning is a subset of machine learning using neural networks with many layers.
```

### 6b. Upload it

Use the **WebUI** at http://localhost:9621 (easiest) or via API:

```bash
curl -X POST http://localhost:9621/documents/upload \
  -F "file=@test_doc.txt"
```

### 6c. Wait for processing

```bash
# Check status (repeat until status = "processed"):
curl -s -X POST http://localhost:9621/documents/paginated \
  -H "Content-Type: application/json" \
  -d '{"page":1,"page_size":10}' | python -c "
import sys,json
for d in json.load(sys.stdin)['documents']:
    print(f\"{d['status']:12} | {d.get('file_path','?')}\")
"
```

### 6d. Query it

```bash
curl -s -X POST http://localhost:9621/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the relationship between AI and deep learning?", "mode": "mix"}' | python -m json.tool
```

### 6e. Verify data is in storage

**If using Supabase:**
```bash
# Link project first (one-time):
npx supabase link --project-ref YOUR_PROJECT_REF

# Check tables:
npx supabase db query --linked \
  "SELECT 'docs' as tbl, count(*) as rows FROM lightrag_doc_full
   UNION ALL SELECT 'chunks', count(*) FROM lightrag_doc_chunks
   UNION ALL SELECT 'entities', count(*) FROM lightrag_full_entities
   UNION ALL SELECT 'relations', count(*) FROM lightrag_full_relations;" \
  -o table
```

**If using Local storage:**
```bash
ls -la rag_storage/
# Should contain: graph_chunk_entity_relation.graphml, vdb_*.json, kv_*.json
```

**Checkpoint:**
- Query returns a meaningful answer with references? **Setup is complete!**
- Empty response? Document may still be processing — wait and retry Step 6c.
- Error response? Check Troubleshooting below.

---

## Step 7: Enable OCR for Scanned PDFs (Optional)

LightRAG can extract text from text-based PDFs, but **scanned PDFs** (image-only) need OCR. This step adds Google Cloud Vision as an automatic fallback.

### 7a. Install dependencies

```bash
pip install google-cloud-vision pdf2image
```

### 7b. Install Poppler (system dependency for pdf2image)

| OS | Command |
|----|---------|
| **Windows** | Download from [github.com/ossamamehmood/Poppler-windows/releases](https://github.com/ossamamehmood/Poppler-windows/releases), extract, add `bin/` folder to PATH |
| **Linux** | `apt install poppler-utils` |
| **macOS** | `brew install poppler` |

### Verify
```bash
python -c "from pdf2image import convert_from_bytes; print('pdf2image: OK')"
python -c "from google.cloud import vision; print('google-cloud-vision: OK')"
```

### 7c. Set up Google Cloud Vision

**Option A: Quick setup via gcloud CLI (recommended for local dev)**

```bash
# 1. Install gcloud CLI if not already: https://cloud.google.com/sdk/docs/install
# 2. Login:
gcloud auth login

# 3. Create a project:
gcloud projects create lightrag-ocr --name="LightRAG OCR"

# 4. Set it as default:
gcloud config set project lightrag-ocr

# 5. Enable Vision API:
gcloud services enable vision.googleapis.com --project=lightrag-ocr

# 6. Set application default credentials (opens browser):
gcloud auth application-default login
```

**Option B: Service account key (for servers/CI)**

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project (or use existing)
3. Enable the **Cloud Vision API**: search "Cloud Vision API" in the console, click Enable
4. Create credentials: **APIs & Services > Credentials > Create Service Account**
5. Download the JSON key file
6. Set the path in your environment:

```bash
# Add to .env or set in your shell:
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-service-account-key.json
```

**Free tier:** 1,000 pages/month. Then $1.50 per 1,000 pages.

### Verify
```bash
# Upload a scanned PDF and check it processes:
curl -X POST http://localhost:9621/documents/upload -F "file=@scanned_doc.pdf"

# Check logs for OCR activity:
# Look for: [OCR] No text from pypdf for ..., trying Google Cloud Vision OCR
```

### How it works
No configuration switch needed. The system **automatically detects** scanned PDFs:
1. pypdf tries to extract text (existing behavior)
2. If text is empty → Google Vision OCR kicks in automatically
3. If google-cloud-vision is not installed → logs a warning and fails as before

**Checkpoint:**
- Scanned PDF processes successfully? OCR is working.
- `[OCR] Scanned PDF detected but OCR not available` in logs? Check the install steps above.

---

## Step 8: Next Steps (Optional)

- **Add authentication:** See `optimization/production-rollout-plan.md` Phase 1
- **Invite team members:** Share the URL (http://YOUR_IP:9621) and set up auth first
- **Upload real documents:** Use the WebUI at http://localhost:9621
- **Supported file types:** `.txt`, `.md`, `.pdf` (including scanned with OCR), `.docx`, `.pptx`, `.xlsx`, `.html`, `.csv`

---

## Document Processing: Who Handles What

### File Type → Library Mapping

| File Type | Library | What It Does |
|-----------|---------|-------------|
| `.txt`, `.md`, `.mdx`, `.html`, `.csv`, `.json`, `.xml`, `.yaml`, `.py`, `.js`, etc. | **Built-in** (UTF-8 read) | Reads file content directly as text |
| `.pdf` (text layer present) | **pypdf** | Extracts text from PDF structure, page by page |
| `.pdf` (encrypted) | **pypdf** + **pycryptodome** | Decrypts with `PDF_DECRYPT_PASSWORD`, then extracts |
| `.pdf` (signed, not encrypted) | **pypdf** | Ignores signature, extracts text normally |
| `.pdf` (scanned/image-only) | **Google Cloud Vision** + **pdf2image** | Converts pages to images, OCRs via Google API |
| `.docx` | **python-docx** | Extracts paragraphs + tables in document order |
| `.pptx` | **python-pptx** | Extracts text from all shapes across all slides |
| `.xlsx` | **openpyxl** | Extracts all sheets as tab-delimited text |

### Processing Flow

```
                         ┌──────────────────┐
                         │  Upload File     │
                         │  (WebUI or API)  │
                         └────────┬─────────┘
                                  │
                         ┌────────▼─────────┐
                         │  Check Extension  │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
     ┌────────▼──────┐  ┌────────▼──────┐  ┌────────▼────────┐
     │ Text files    │  │ .pdf          │  │ .docx/.pptx     │
     │ .txt .md .csv │  │               │  │ .xlsx           │
     │ .html .json   │  │               │  │                 │
     │ .py .js etc.  │  │               │  │                 │
     └───────┬───────┘  └───────┬───────┘  └────────┬────────┘
             │                  │                    │
             │           ┌──────▼───────┐            │
     ┌───────▼───────┐   │ pypdf        │   ┌───────▼────────┐
     │ Read as UTF-8 │   │ extract text │   │ python-docx /  │
     └───────┬───────┘   └──────┬───────┘   │ python-pptx /  │
             │                  │            │ openpyxl       │
             │           ┌──────▼───────┐   └───────┬────────┘
             │           │ Text found?  │           │
             │           └──┬───────┬───┘           │
             │           Yes│       │No             │
             │              │  ┌────▼──────────┐    │
             │              │  │ OCR available? │    │
             │              │  └──┬─────────┬──┘    │
             │              │  Yes│         │No     │
             │              │  ┌──▼───────┐ │       │
             │              │  │ pdf2image │ │       │
             │              │  │ → images  │ │       │
             │              │  └────┬─────┘ │       │
             │              │  ┌────▼──────┐│       │
             │              │  │ Google    ││       │
             │              │  │ Vision    ││       │
             │              │  │ OCR       ││       │
             │              │  └────┬─────┘│       │
             │              │       │      │       │
             ▼              ▼       ▼      ▼       ▼
        ┌─────────────────────────────────────────────┐
        │              Raw Text Content                │
        └──────────────────────┬──────────────────────┘
                               │
        ┌──────────────────────▼──────────────────────┐
        │           LightRAG Pipeline                  │
        │  1. Chunk text (~1200 tokens each)           │
        │  2. Generate embeddings (OpenAI)             │
        │  3. Extract entities & relations (LLM)       │
        │  4. Build knowledge graph                    │
        │  5. Store in Supabase + NetworkX             │
        └─────────────────────────────────────────────┘
```

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: fastapi` | Missing API extras | `pip install "lightrag-hku[api]"` |
| `Tenant or user not found` | Wrong Supabase pooler hostname | Copy the **exact** hostname from Dashboard > Settings > Database > Session mode. The `aws-X-` number matters. |
| `SSL: CERTIFICATE_VERIFY_FAILED` | Supabase SSL patch not applied | Apply the patch from Step B4 to `postgres_impl.py` |
| `column cannot have more than 2000 dimensions for hnsw index` | HNSW can't handle 3072-dim embeddings | Set `POSTGRES_VECTOR_INDEX_TYPE=HNSW_HALFVEC` in `.env` |
| `function create_graph(unknown) does not exist` | PGGraphStorage needs Apache AGE | Set `LIGHTRAG_GRAPH_STORAGE=NetworkXStorage` (Supabase doesn't have AGE) |
| `gaierror: getaddrinfo failed` | Direct DB host is IPv6-only | Use the pooler hostname (`aws-X-...pooler.supabase.com`), not `db.*.supabase.co` |
| `password authentication failed` | Wrong DB password | Reset in Supabase Dashboard > Settings > Database |
| `connection refused` on port 6543 | Using Transaction pooler port | Switch to port `5432` (Session mode) |
| Server shows "only whitespace" for PDF | Scanned image PDF, no text layer | Pre-process with OCR tool, then upload the text |
| `Unknown SSL mode: require-no-verify` | Patch applied to source but not site-packages | Run: `python -c "import lightrag.kg.postgres_impl as m; print(m.__file__)"` and patch that file too |
| Server starts but queries fail | OpenAI API key invalid or no credit | Test key: `curl https://api.openai.com/v1/models -H "Authorization: Bearer YOUR_KEY"` |
| WebUI shows "No Documents" but data exists in DB | Workspace mismatch — data has one workspace value, server queries another | **Do NOT set the `WORKSPACE` env var.** LightRAG defaults to `'default'` internally. Setting it to empty or a different value causes a mismatch. If you suspect this issue, check: `SELECT DISTINCT workspace FROM lightrag_doc_status;` |
| WebUI shows "No Documents", API hangs, health check works | `POSTGRES_MAX_CONNECTIONS` too high — pool exhausts Supabase pooler slots | Set `POSTGRES_MAX_CONNECTIONS` to ≤ 1/3 of Supabase pooler size. Default Nano pool is 15, so use `5`. Restart server after changing. |
| `Max client connections reached` during document processing | Same — connection pool exceeds Supabase pooler limit | Same fix as above |

---

## Architecture

```
┌─────────────────┐
│  You / WebUI     │
│  localhost:9621  │
└────────┬────────┘
         │
┌────────▼────────┐     ┌──────────────────────┐
│  LightRAG       │────▶│  LLM Provider        │
│  Server         │     │  (OpenAI / Ollama)    │
│                 │     └──────────────────────┘
│                 │     ┌──────────────────────┐
│                 │────▶│  Embedding Provider   │
│                 │     │  (OpenAI / Ollama)    │
│                 │     └──────────────────────┘
│                 │
│  Storage:       │     ┌──────────────────────┐
│  ├─ KV ─────────┼────▶│  Supabase PostgreSQL │
│  ├─ Vector ─────┼────▶│  (or local JSON)     │
│  ├─ DocStatus ──┼────▶│                      │
│  └─ Graph ──────┼──┐  └──────────────────────┘
└─────────────────┘  │  ┌──────────────────────┐
                     └─▶│  NetworkX local file  │
                        └──────────────────────┘
```
