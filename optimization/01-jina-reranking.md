# 1. Enable Jina Reranking

## Summary

Reranking is already implemented in LightRAG (`lightrag/rerank.py`) but disabled (`RERANK_BINDING=null`). Enabling it with `jina-reranker-v2-base-multilingual` is a config-only change that typically improves retrieval precision by 15-30%.

## Current State

- Three reranker providers supported: Jina, Cohere, Aliyun
- Generic API interface at `lightrag/rerank.py:182` supports any compatible endpoint
- Document chunking for rerank (480-token max per chunk) with score aggregation
- Currently disabled in production

## What Changes

| Setting | Current | Proposed |
|---|---|---|
| `RERANK_BINDING` | null | `jina` |
| `RERANK_MODEL` | - | `jina-reranker-v2-base-multilingual` |
| `JINA_API_KEY` | not set | (your API key) |
| `RERANK_TOP_K` | - | 10 (tunable) |

## Cost

- Jina free tier: 1M tokens/month
- ~10K tokens per query (query + 20 chunks at ~500 tokens)
- ~100 queries/month on free tier
- Paid: ~$0.02/1M tokens (negligible for legal workloads)

## Impact

**High** -- Reranking re-scores retrieved chunks using a cross-encoder model, which is significantly more accurate than vector cosine similarity alone. The multilingual model handles Hebrew natively.

## Risk

**Low** -- Config change only. Adds ~200-500ms latency per query (API round-trip). Fallback: if Jina is down, queries still work without reranking.

## How to Test

1. Run the same query with and without reranking
2. Compare retrieved chunk relevance (use `only_need_context=true` to see raw retrieval)
3. Check if answers cite more relevant sections

## Decision

- [ ] Approved
- [ ] Deferred
- [ ] Rejected

Notes:
