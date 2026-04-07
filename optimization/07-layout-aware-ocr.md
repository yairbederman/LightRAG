# 7. Layout-Aware OCR

## Summary

Current OCR (GCV `document_text_detection`) returns raw text without layout information. Multi-column documents (common in court decisions) may get columns interleaved. RAG-Anything uses MinerU for reading-order preservation, column detection, and header/footer handling.

## Current State

- pypdf text extraction: page-by-page, no reading order analysis
- GCV OCR: returns text blocks but no column/region structure
- 300 DPI rendering for OCR via pdf2image
- Works well for single-column documents (most contracts)

## What Changes

### Option A: MinerU Integration
- Full layout analysis: columns, headers, footers, table regions, reading order
- Heavy: PyTorch + model downloads (~2GB)
- Uncertain Hebrew layout model support
- Would replace pypdf as primary parser

### Option B: GCV Layout API
- Google Cloud Vision has `document_text_detection` which returns bounding boxes
- Current implementation doesn't use the layout data from GCV response
- Could reconstruct reading order from GCV's block/paragraph/word coordinates
- No new dependencies -- uses existing GCV integration

### Option C: Docling Layout Engine
- Already partially integrated
- Handles multi-column detection
- Lighter than MinerU

## Impact

**High for complex layouts** (court decisions, multi-column docs)
**Low for standard contracts** (single-column, well-structured)

## Risk

**High** -- Considerations:
- MinerU: heavy dependency, Hebrew model uncertain
- GCV layout: requires significant coordinate processing logic
- Docling: macOS/gunicorn compatibility issues (documented in codebase)
- Any approach changes the extraction pipeline fundamentally
- Wrong reading order is worse than no reading order (garbage text)

## Decision

- [ ] Approved (Option: ___)
- [x] Deferred
- [ ] Rejected

Notes: Skipped 2026-04-06. High risk, heavy dependencies, uncertain Hebrew layout model support. Revisit when multi-column court decisions become a priority.
