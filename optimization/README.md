# Optimization Plan

GAP analysis: Light-RAG (local) vs RAG-Anything, tailored for Hebrew legal document RAG.

Dimensions evaluated: feature completeness, token efficiency, RAG accuracy (English + Hebrew), OCR accuracy.

## Prioritized Actions

| # | Action | Impact | Risk | Effort | Status |
|---|---|---|---|---|---|
| 1 | [Enable Jina reranking](01-jina-reranking.md) | High | Low | Minutes | Pending |
| 2 | [Add legal entity types](02-legal-entity-types.md) | High | Low | Minutes | Done |
| 3 | [Hebrew few-shot prompts](03-hebrew-prompts.md) | High | Low | Hours | Done |
| 4 | [Section-aware chunking](04-section-aware-chunking.md) | High | Medium | Days | Pending |
| 5 | [Table-aware PDF extraction](05-table-extraction.md) | High | Medium | Days | Pending |
| 6 | [Circuit breaker](06-circuit-breaker.md) | Medium | Low | Hours | Pending |
| 7 | [Layout-aware OCR](07-layout-aware-ocr.md) | High | High | Weeks | Pending |
| 8 | [Content-type chunk templates](08-chunk-templates.md) | Medium | Low | Hours | Pending |

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
