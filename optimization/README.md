# Optimization Plan

GAP analysis: Light-RAG (local) vs RAG-Anything, tailored for Hebrew legal document RAG.

Dimensions evaluated: feature completeness, token efficiency, RAG accuracy (English + Hebrew), OCR accuracy.

## Status Dashboard

| # | Action | Impact | Risk | Effort | Status | Commits | Rollback |
|---|---|---|---|---|---|---|---|
| 1 | [Enable Jina reranking](01-jina-reranking.md) | High | Low | Minutes | Pending | — | — |
| 2 | [Add legal entity types](02-legal-entity-types.md) | High | Low | Minutes | **Done** | `36b68c14`, `7d320527` | `git revert 7d320527 36b68c14` |
| 3 | [Hebrew few-shot prompts](03-hebrew-prompts.md) | High | Low | Hours | **Done** | `9096a357`, `7d320527` | `git revert 7d320527 9096a357` |
| 4 | [Paragraph-aware chunking](04-section-aware-chunking.md) | High | Medium | Days | **Done** | `61c8c1aa` | `git revert 61c8c1aa` |
| 5 | [Table-aware PDF extraction](05-table-extraction.md) | High | Medium | Days | Deferred | — | — |
| 6 | [Circuit breaker](06-circuit-breaker.md) | Medium | Low | Hours | Deferred | — | — |
| 7 | [Layout-aware OCR](07-layout-aware-ocr.md) | High | High | Weeks | Deferred | — | — |
| 8 | [Content-type chunk templates](08-chunk-templates.md) | Medium | Low | Hours | Deferred | — | — |

### What Was Implemented

**#2 Legal entity types** — 11 domain-specific types (ContractParty, LegalClause, Obligation, Deadline, Court, Statute, LegalTerm, Monetary + Person, Organization, Location). Configured via `domain.md`. Affects ingestion only. Re-ingestion required for existing docs.

**#3 Hebrew few-shot prompts** — 3 Hebrew legal extraction examples (rental agreement, court ruling, statement of claim) replacing English defaults. Configured via `domain.md`. Entity types and examples are coupled — both must match the domain.

**#4 Paragraph-aware chunking** — `chunking_by_paragraph_aware()` in `operate.py`. Splits on `\n\n` paragraph boundaries instead of arbitrary token positions. Falls back to token splitting for oversized paragraphs. Set as default in `lightrag.py`.

### What Was Deferred

**#5 Table extraction** — Recommended pdfplumber (Option B). No regression on any PDF type. Revisit when table-heavy documents become priority.

**#6 Circuit breaker** — Retry decorators spread across 17+ files. Revisit when service outages become a problem.

**#7 Layout-aware OCR** — Heavy dependencies (MinerU/PyTorch), uncertain Hebrew layout model support. Revisit for multi-column court decisions.

**#8 Chunk templates** — Depends on #5 (table extraction). Revisit after #5.

## Not Recommended (low value for legal use case)

- Image/equation modal processing -- legal docs are text-heavy
- VLM-enhanced queries -- users query with text
- Cross-modal graph schema -- high complexity, marginal legal benefit
- Markdown-to-PDF output -- trivial to add later if needed
- Per-document parser selection -- single domain, single pipeline is fine

## Light-RAG Advantages (already ahead of RAG-Anything)

- Full REST API + WebUI (RAG-Anything is library-only)
- Pipeline cancellation and status tracking
- Selective page OCR (cost-efficient)
- OpenAI prompt caching optimization
- RAGAS evaluation framework
- Hallucination prevention prompts
