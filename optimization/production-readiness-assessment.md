# LightRAG Production Readiness Assessment

## Context

Production readiness review of a LightRAG fork (upstream: https://github.com/hkuds/lightrag) to be deployed for a paying client. Requirements:
- All file types supported, especially PDFs (text, scanned/OCR, signed)
- Hebrew language support (legal documents)
- Grounded answers — only from ingested data, no hallucination
- Legal document accuracy

The system is a graph-based RAG framework: documents are ingested, entities/relationships extracted into a knowledge graph, and multi-modal retrieval (local/global/hybrid/mix/naive) is used to answer queries.

---

## Verdict: CONDITIONAL YES

The core RAG pipeline is architecturally sound and well-engineered. It **can** serve a paying client, but only after completing the blockers below. Total mandatory work: ~5-7 hours. Full hardening: ~1 week.

---

## Current State Summary

| Component | Current Config | Status |
|-----------|---------------|--------|
| **LLM Model** | `gpt-4o-mini` | Insufficient for Hebrew legal — upgrade to `gpt-4o` |
| **Embedding Model** | `text-embedding-3-large` (3072d) | Good — best OpenAI multilingual embedding |
| **Vector Storage** | `PGVectorStorage` (Supabase) | Good — HNSW_HALFVEC index configured |
| **KV Storage** | `PGKVStorage` (Supabase) | Good — production-grade |
| **Graph Storage** | `NetworkXStorage` (in-memory) | Risk — single file, no concurrent write safety |
| **Doc Status** | `PGDocStatusStorage` (Supabase) | Good — production-grade |
| **Language** | `SUMMARY_LANGUAGE=English` | Must change to Hebrew |
| **Auth** | Disabled | Must enable before deployment |
| **CORS** | Wildcard `*` | Must restrict |
| **OCR** | Commented out | Must configure for scanned PDFs |
| **Reranking** | `null` (disabled) | Should enable for legal accuracy |
| **Credentials** | Plaintext in `.env` (lines 14, 22, 59) | Must rotate — exposed in file |

---

## OpenAI Models In Use

| Purpose | Current Model | Recommendation | Why |
|---------|--------------|----------------|-----|
| **Embedding** | `text-embedding-3-large` (3072d) | **Keep** | Best multilingual embedding from OpenAI. 3072 dims = high precision. Already configured with HNSW_HALFVEC. |
| **LLM (extraction + query)** | `gpt-4o-mini` | **Upgrade to `gpt-4.1-mini`** | Better instruction following (10.5% improvement), 1M context window, $0.40/$1.60 per 1M tokens. API ends Oct 2026 — migrate to gpt-5-mini or gpt-5.1 before then. |
| **Reranking** | None | **Add `jina-reranker-v2-base-multilingual`** | Best multilingual reranker with Hebrew support. Adds ~200-500ms per query but significantly improves retrieval relevance. |

---

## Grounding / Hallucination Prevention — STRONG

The system already has excellent grounding. Key evidence from `lightrag/prompt.py`:

- **Line 245**: *"Strictly adhere to the provided context from the Context; DO NOT invent, assume, or infer any information not explicitly stated."*
- **Line 246**: *"If the answer cannot be found in the Context, state that you do not have enough information to answer. Do not attempt to guess."*
- **Line 239**: *"Your own knowledge must ONLY be used to formulate fluent sentences and connect ideas, NOT to introduce any external information."*
- **Line 220-222**: Returns `[no-context]` tag when no relevant data found
- **Line 270**: `{user_prompt}` injection point allows adding custom grounding rules

**Assessment**: This is best-in-class grounding for open-source RAG. No changes needed to the prompts themselves. Enhanced with a custom `user_prompt` for legal domain (see Improvement 2).

---

## PDF & File Support — GOOD

- **45+ file formats** supported (`document_routes.py` lines 804-845)
- **Text PDFs**: Extracted via pypdf (or DOCLING if configured)
- **Scanned PDFs**: Classified automatically → routed to Google Cloud Vision OCR (`ocr_processor.py`)
- **Mixed PDFs (text + image pages)**: Per-page hybrid extraction — pypdf for text pages, selective OCR for image pages (below configurable char threshold). Configured via `config.md` `OCR > Page Text Threshold` (default 50).
- **Signed PDFs**: PyPDF reads text from signed PDFs fine. Signature validation is not the system's job — acceptable.
- **Encrypted PDFs**: Supported via `PDF_DECRYPT_PASSWORD`
- **OCR dependency**: Google Cloud Vision — already configured (GCP auth active)

---

## Hebrew Support — GAPS TO FIX

| Area | Status | Action |
|------|--------|--------|
| Backend prompts | All have `{language}` placeholder | Set `SUMMARY_LANGUAGE=Hebrew` in `.env` |
| LLM (gpt-4o) | Strong Hebrew understanding | Upgrade from gpt-4o-mini |
| Embedding | text-embedding-3-large supports Hebrew via UTF-8 | No change needed |
| OCR | Google Cloud Vision has excellent Hebrew OCR | Configure (Blocker 4) |
| Tokenizer | tiktoken cl100k_base — Hebrew works but ~2-3x tokens/word vs English | Increase chunk size to compensate |
| WebUI | **No Hebrew locale** (ar.json exists for Arabic RTL) | Create `he.json` locale |
| Entity extraction | Prompts enforce output in `{language}`, proper nouns preserved in original | Works once language is set |

---

## BLOCKERS — Must Do Before Deployment

### 1. Rotate exposed credentials (1 hour) — SKIPPED (deferred)
- `.env` lines 14, 22: OpenAI API key in plaintext
- `.env` line 59: Supabase password in plaintext
- **Action**: Regenerate OpenAI key, reset Supabase password, update `.env`
- Verify `.env` is in `.gitignore`

### 2. Enable authentication + restrict CORS (1 hour)

**The problem**: Right now the API is wide open — anyone who discovers the URL can query the client's legal documents, upload files, or delete data without logging in. No username, no password, no API key required. Additionally, CORS is set to `*` which means any website on the internet can make requests to the API from a browser.

**The fix**: LightRAG already has a built-in auth system (JWT tokens + API keys) — it just needs to be turned on via `.env`:

| Setting | What it does |
|---------|-------------|
| `AUTH_ACCOUNTS=admin:{bcrypt_hashed_password}` | Creates a username + password login. Users get a JWT token after logging in via the WebUI. |
| `TOKEN_SECRET=<64-char-random-string>` | The secret key used to sign JWT tokens — must be a long random string so tokens can't be forged. |
| `CORS_ORIGINS=https://your-client-domain.com` | Restricts which websites can call the API. Instead of `*` (everyone), only your client's domain. |
| `LIGHTRAG_API_KEY=<random-api-key>` | An API key for programmatic access (scripts, integrations) that don't go through the login flow. |

No code changes needed — all config in `.env`.

**Decision: SKIPPED (deferred)**

### 3. Set language to Hebrew (5 minutes) — APPROVED
- **File**: `.env` line 38
- Change: `SUMMARY_LANGUAGE=Hebrew`
- This propagates to all prompts via `{language}` placeholder in `lightrag/prompt.py`

### ~~4. Configure Google Cloud Vision OCR~~ ALREADY DONE
- `google-cloud-vision` 3.13.0 and `pdf2image` 1.17.0 already installed
- GCP auth active via `gcloud auth application-default login`
- `.env` line 46 is commented out but not needed — Application Default Credentials work automatically
- **No action required**

### 5. Upgrade LLM to gpt-4.1-mini (5 minutes)
- **File**: `.env` line 15
- Change: `LLM_MODEL=gpt-4.1-mini`
- Better instruction following than gpt-4o-mini (10.5% improvement on MultiChallenge for 4.1 family), 1M token context
- Pricing: $0.40/$1.60 per 1M tokens (input/output) — modest increase from current gpt-4o-mini ($0.15/$0.60)
- **WARNING**: API ends Oct 14, 2026 — plan migration to gpt-5-mini or gpt-5.1 before then
- Fallback path if quality insufficient: upgrade to gpt-5.1 ($0.63/$5.00)

### 6. Customize entity types for legal domain (15 minutes) — SKIPPED
- Keeping generic defaults for reusability across clients
- LLM is smart enough to extract legal entities with generic types (categorized as Organization/Concept instead of Court/Law)
- Minimal impact on query answer quality — RAG retrieval uses semantic similarity, not entity type filtering
- Can revisit per-workspace if needed later

**Total blocker effort: ~5-7 hours**

---

## HIGH-IMPACT IMPROVEMENTS — Should Do

### 1. Add Hebrew locale to WebUI (4-8 hours) — SKIPPED
- WebUI labels stay English; backend Hebrew support works regardless
- Can revisit if client requests Hebrew UI

### 2. Add domain-specific grounding via config.md (1-2 hours) — APPROVED
- Create a `config.md` file at project root that the server reads at startup
- Content under a `## User Prompt` heading becomes the default `user_prompt` for all queries
- Per-query `user_prompt` still overrides when provided
- Swap `config.md` per deployment (legal, medical, generic, etc.)
- **Requires**: Small code change to read config.md + new step in SETUP.md
- **SETUP.md**: Add as a mandatory step (e.g., Step 4b) that asks the user to define their domain. Provide templates for common domains (legal, medical, finance, generic) and explain how this affects answer style and grounding.
- Example `config.md` for legal:
  ```markdown
  # System Configuration
  
  ## User Prompt
  You are answering questions about legal documents. Accuracy is paramount.
  If uncertain about any detail, say so explicitly.
  Never paraphrase legal clauses — quote them directly.
  Always cite the specific document and section when possible.
  ```

### 3. Enable reranking (2 hours) — SKIPPED
- Adds latency and external API dependency
- Revisit if retrieval quality proves insufficient after testing

### 4. Tune chunk size for Hebrew tokenization (15 minutes) — APPROVED
- **File**: `.env`
- Hebrew consumes ~2-3x more tokens per word than English in tiktoken cl100k_base
- Change: `CHUNK_SIZE=1800` (from 1200) and `CHUNK_OVERLAP_SIZE=200` (from 100)
- Optimized for Hebrew; English docs get slightly larger chunks (fine, within safe range)

### 5. Migrate graph storage from NetworkXStorage (1-2 days) — DEFERRED
- Current `NetworkXStorage` stores entire graph in memory as a single `.graphml` file
- **Investigation result**: PGGraphStorage requires Apache AGE extension — not available on Supabase
- **Options**: Neo4j Aura free tier (200K nodes, free) or self-hosted Neo4j Docker
- **Decision**: Keep NetworkXStorage for now. Acceptable risk for single-server, single-client deployment. Graph can be rebuilt from stored chunks by re-ingesting if data is lost.
- **Revisit when**: Multiple workers needed, or after a crash causes data loss

### 6. Add rate limiting via reverse proxy (2-4 hours) — SKIPPED
- Revisit when deploying to production with public access

---

## NICE TO HAVE

| Item | Effort | Impact |
|------|--------|--------|
| Langfuse observability (`env.example` lines 622-630) | Small (30min) | LLM call tracing, cost tracking, debugging |
| DOCLING PDF parser (`DOCUMENT_LOADING_ENGINE=DOCLING`) | Small (30min) | Better structural PDF parsing (tables, sections) |
| SSL/TLS encryption | Small (1h) | Encrypted transport |
| Supabase Pro tier ($25/mo) | Small (15min) | 8GB DB, always-on, daily backups |
| Page number preservation in chunks | Large (2-3 days) | Legal citation improvement ("found on page 7") |

---

## Architecture Strengths

- **20+ storage backends** — pluggable via abstract base classes
- **Async throughout** — asyncpg, aiohttp, asyncio
- **3-retry exponential backoff** on LLM and VDB operations
- **Document lifecycle tracking** — PENDING -> PROCESSING -> PROCESSED/FAILED
- **Pipeline cancellation** support
- **Streaming responses** via SSE
- **Reference tracking** with file_path and frequency-based prioritization
- **Entity extraction gleaning** — 2-pass extraction catches missed entities
- **5 query modes** for different retrieval strategies

## Known Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| NetworkX graph storage (single file, no concurrency) | Medium | Migrate to PGGraphStorage or Neo4j |
| Hebrew RTL rendering in graph visualization | Low | Test with sample data before go-live |
| tiktoken tokenization inefficiency for Hebrew | Low | Increase chunk size (Improvement 4) |
| No API-level rate limiting | Medium | Reverse proxy with rate limiting |
| Supabase free tier (500MB, pauses after 7d) | High | Upgrade to Pro |
| No horizontal scaling | Low | Acceptable for single-client deployment |

---

## Verification Plan

After implementing blockers:
1. **Auth test**: Verify `/health` returns 401 without token, 200 with valid token
2. **Hebrew extraction test**: Ingest a Hebrew legal document, verify entities extracted in Hebrew
3. **OCR test**: Ingest a scanned Hebrew PDF, verify text extracted via Google Cloud Vision
4. **Grounding test**: Ask a question not covered by ingested data, verify `[no-context]` response
5. **Reference test**: Query and verify response includes document citations
6. **Signed PDF test**: Ingest a digitally signed PDF, verify text extraction succeeds
7. **WebUI test**: Verify Hebrew locale renders correctly with RTL layout

---

## Impact Analysis Report

| Fix | Impact | Risk |
|-----|--------|------|
| Rotate credentials | Eliminates security exposure | Low — additive only |
| Enable auth + CORS | Prevents unauthorized access | Low — existing system, just needs config |
| Set Hebrew language | Enables Hebrew entity extraction and summaries | Low — single config change, well-tested pathway |
| Configure OCR | Enables scanned PDF ingestion | Medium — external dependency (Google Cloud) |
| Upgrade to gpt-4o | Better Hebrew + legal accuracy | Medium — 10x cost increase per token |
| Legal entity types | Domain-relevant knowledge graph | Low — config change only |
| Hebrew WebUI | Client can use interface in Hebrew | Low — follows existing i18n pattern |
| Enable reranking | Better retrieval relevance | Low — additive, external API dependency |
| Tune chunk size | Better Hebrew chunk density | Low — config change only |
| Graph storage migration | Concurrent safety + persistence | Medium — data migration required |
