# 8. Content-Type Chunk Templates

## Summary

All text is chunked identically regardless of source (OCR output, table content, narrative text). RAG-Anything uses content-type-specific templates that prefix chunks with type metadata, helping the LLM distinguish between narrative text, table data, and OCR-extracted content.

## Current State

- Uniform chunking: no content-type awareness
- OCR text, table text, and narrative prose are indistinguishable after chunking
- No metadata indicating chunk origin (which page, which content type)

## What Changes

Add content-type prefixes to chunks during ingestion:

```
[Table | Page 5 | Schedule B - Payment Terms]
Date | Amount | Status
2024-01-01 | NIS 50,000 | Paid
...
```

```
[Narrative | Page 3 | Section 4 - Termination]
Either party may terminate this agreement with 30 days written notice...
```

```
[OCR | Page 12 | Scanned appendix]
The undersigned hereby confirms...
```

## Impact

**Medium** -- Benefits:
- LLM can distinguish content types during retrieval and generation
- Table chunks get appropriate interpretation ("this is structured data")
- OCR chunks flagged for potential quality issues
- Better source attribution in responses

## Risk

**Low** -- Additive change. Prefix templates are added during chunking. No core logic changes. Slight increase in token usage per chunk (prefix overhead ~20-50 tokens).

## Dependencies

- Best implemented alongside #4 (section-aware chunking) and #5 (table extraction)
- Content-type detection requires knowing the source during chunking

## Implementation

1. Define template prefixes per content type
2. Tag content with type during extraction (before chunking)
3. Apply templates during chunk creation
4. Preserve type metadata in chunk storage for filtering

## Decision

- [ ] Approved
- [x] Deferred
- [ ] Rejected

Notes: Skipped 2026-04-06. Depends on #5 (table extraction) for full value. Without table detection, only distinguishes pypdf vs OCR text. Revisit after #5 is implemented.
