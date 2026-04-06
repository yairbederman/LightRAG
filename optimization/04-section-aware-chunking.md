# 4. Section-Aware Chunking

## Summary

LightRAG chunks text purely by token count (1800 tokens, 200 overlap). This ignores document structure -- a chunk can split mid-clause, mid-sentence, or mid-table. Legal documents are structured by sections and clauses, so structure-aware chunking would preserve clause integrity and improve citation accuracy.

## Current State

- Token-based chunking at `operate.py:101-164`
- Configurable via `chunking_func` hook at `lightrag.py:332-365` (allows custom function without modifying core)
- 1800/200 tokens configured for Hebrew in `config.md`
- No awareness of: section headings, clause numbers, page boundaries, paragraph breaks

## What Changes

Implement a custom `chunking_func` that:
1. Detects Hebrew legal section patterns (e.g., `.1`, `1. סעיף`, numbered clauses)
2. Splits on section boundaries when possible
3. Falls back to token-based splitting for sections exceeding max chunk size
4. Preserves section header context in each chunk (prefix with section number/title)
5. Respects page boundaries as secondary split points

## RAG-Anything Approach

RAG-Anything uses page-boundary awareness with content-type-specific templates and token-aware truncation at sentence boundaries. We'd adapt this for Hebrew legal structure specifically.

## Impact

**High** -- Benefits:
- Chunks align with legal clause boundaries
- Better retrieval: "what does section 5 say?" retrieves the actual section
- Better citation: responses can reference specific clause numbers
- Reduced noise: no half-clauses confusing the LLM

## Risk

**Medium** -- Considerations:
- Hebrew section numbering patterns need careful regex design
- Some documents may have inconsistent formatting
- Custom function needs thorough testing across document types
- Implementable via `chunking_func` hook -- no core code changes needed

## Implementation Approach

1. Analyze sample Hebrew legal documents for section patterns
2. Build regex patterns for Hebrew legal section detection
3. Implement as custom `chunking_func`
4. Test with existing document corpus
5. Compare retrieval quality before/after

## Decision

- [x] Approved (Approach B — paragraph-aware)
- [ ] Deferred
- [ ] Rejected

Notes: Applied 2026-04-06. Implemented `chunking_by_paragraph_aware` in `operate.py` as drop-in replacement. Splits on `\n\n` paragraph boundaries, groups paragraphs up to token limit, falls back to token splitting for oversized paragraphs. Set as new default in `lightrag.py`. Works on all document types regardless of structure. Existing documents need re-ingestion to benefit.
