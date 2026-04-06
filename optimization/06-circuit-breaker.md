# 6. Circuit Breaker

## Summary

LightRAG uses tenacity-based retry with exponential backoff on all LLM and external service calls. Missing: circuit breaker pattern that stops calling a service after N consecutive failures, preventing cascading failures and wasted retries.

## Current State

- Retry logic: tenacity across 17+ files (LLM providers, rerank, storage)
- No circuit breaker: if GCV OCR or an LLM API is down, each document/chunk retries independently
- Failed requests accumulate, blocking the pipeline with futile retries

## What Changes

Add a circuit breaker decorator around external service calls:

```python
# Concept -- wraps existing retry logic
@circuit_breaker(failure_threshold=5, recovery_timeout=60)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(...))
async def call_external_service(...):
    ...
```

States:
- **Closed** (normal): requests pass through
- **Open** (tripped): after N failures, immediately reject requests for `recovery_timeout` seconds
- **Half-open**: after timeout, allow one test request to check if service recovered

## Impact

**Medium** -- Benefits:
- Fast failure when GCV/LLM is down (instead of 3 retries x exponential backoff per chunk)
- Pipeline fails gracefully instead of hanging
- Logs clearly indicate "service X circuit open" for debugging

## Risk

**Low** -- Small decorator change. Libraries: `aiobreaker` or custom ~30-line implementation. Non-breaking addition to existing retry chain.

## Implementation

1. Create `lightrag/circuit_breaker.py` utility
2. Apply to: LLM provider calls, GCV OCR calls, reranker API calls
3. Configure per-service thresholds (LLM: 5 failures/60s, OCR: 3 failures/120s)
4. Log state transitions

## Decision

- [ ] Approved
- [ ] Deferred
- [ ] Rejected

Notes:
