# 3. Hebrew Few-Shot Prompts

## Summary

LightRAG's entity extraction prompts (`lightrag/prompt.py`) use English-only few-shot examples. LLMs perform better with in-language examples, especially for Hebrew which has unique morphological challenges (prefixed prepositions, construct state, gendered forms). RAG-Anything's `prompts_zh.py` (Chinese) demonstrates the pattern.

## Current State

- `prompt.py` has 3 English example texts for entity/relation extraction
- `{language}` parameter tells the LLM to output in a target language, but examples remain English
- Hebrew morphology causes extraction errors:
  - Prefixed prepositions: "from the company" = single Hebrew word
  - Construct state: "contract of the tenant" = different word form than standalone "contract"
  - Entity boundaries are harder to identify in Hebrew text

## What Changes

Create `prompts_he.py` with:
1. Hebrew example texts (legal domain)
2. Hebrew entity/relation extraction examples
3. Hebrew-specific instructions for handling morphological complexity
4. Keep the same template structure as `prompt.py`

## Example (conceptual)

English prompt example:
```
"The contract between ABC Ltd and John Smith was signed on January 1, 2024"
-> Entity: ABC Ltd (Organization), John Smith (Person)
-> Relation: ABC Ltd -> signed contract with -> John Smith
```

Hebrew equivalent needed:
```
Hebrew legal text example with prefixed articles, construct state, etc.
-> Entities extracted correctly despite morphological complexity
-> Relations preserving Hebrew legal terminology
```

## Impact

**High** -- Hebrew entity extraction accuracy improves significantly. The LLM learns from Hebrew examples how to:
- Identify entity boundaries in Hebrew text
- Handle prefixed prepositions correctly
- Extract legal terminology in its Hebrew forms
- Maintain consistent entity naming across documents

## Risk

**Low** -- Content task, not engineering. The prompt template structure is stable. Worst case: prompts need iteration to find optimal Hebrew examples.

## Dependencies

- Knowledge of Hebrew legal document structure
- Sample Hebrew legal text for examples
- Testing with actual Hebrew legal documents to validate improvement

## Decision

- [x] Approved
- [ ] Deferred
- [ ] Rejected

Notes: Applied 2026-04-06. Replaced 3 English examples (fiction, finance, sports) with 3 Hebrew legal examples: הסכם שכירות (agreement), החלטת בית משפט (court ruling), כתב תביעה (statement of claim). Examples use legal entity types from config.md. ~2500 tokens total. Affects ingestion only.
