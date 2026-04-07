# 5. Table-Aware PDF Extraction

## Summary

pypdf extracts PDF tables as raw text, losing all structure. Legal documents frequently contain tables (payment schedules, obligation matrices, party lists). RAG-Anything uses MinerU for table region detection and TableModalProcessor for semantic table summaries.

## Current State

- PDF text extraction via pypdf: tables become jumbled text
- DOCX tables: preserved with cell escaping (`document_routes.py:1032-1108`)
- No table region detection in PDFs
- No semantic table understanding

## What Changes

Two-layer approach:
1. **Table detection**: Identify table regions in PDFs (before text extraction)
2. **Table processing**: Convert detected tables to structured format, then optionally generate LLM summaries

### Option A: MinerU Integration
- Layout-aware parsing that detects table regions natively
- Heavy dependency (PyTorch, model downloads)
- May lack Hebrew layout models

### Option B: Camelot/Tabula
- Lightweight Python libraries for PDF table extraction
- `camelot-py` or `tabula-py` detect and extract tables as DataFrames
- No ML dependencies
- Works alongside existing pypdf pipeline

### Option C: Docling Table Extraction
- Already partially integrated as optional engine
- Handles table detection and structure preservation
- Markdown output preserves table format

## Impact

**High for table-heavy documents** -- Enables:
- "What are the payment terms in schedule B?" (currently impossible)
- Accurate extraction of party lists, obligation matrices
- Structured data preserved in knowledge graph

## Risk

**Medium** -- Considerations:
- Table detection accuracy varies by PDF generation method
- Scanned PDFs with tables need OCR + layout analysis (hardest case)
- LLM table summarization adds cost per table
- Integration complexity depends on chosen approach

## Decision

- [ ] Approved (Option: ___)
- [x] Deferred
- [ ] Rejected

Notes: Discussed 2026-04-06. Recommended Option B (pdfplumber). Impact analysis: only affects text-layer pages with tables, no regression on scanned/OCR/mixed PDFs. User deferred — revisit when table-heavy documents become a priority.
