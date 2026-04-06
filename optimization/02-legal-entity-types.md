# 2. Add Legal Entity Types

## Summary

LightRAG uses 11 general entity types (Person, Organization, Location, etc.). For Hebrew legal documents, adding domain-specific types would dramatically improve entity extraction precision. This is a pure configuration change via the `ENTITY_TYPES` env var.

## Current State

Default types: Person, Creature, Organization, Location, Event, Concept, Method, Content, Data, Artifact, NaturalObject

Problem: "Organization" is too broad -- it can't distinguish plaintiff from defendant from guarantor. A "LegalClause" entity would let the system extract and link specific contractual obligations.

## What Changes

Add to `ENTITY_TYPES` env var or config:

**Proposed legal types** (replace or extend defaults):

| Type | Purpose | Example |
|---|---|---|
| ContractParty | Parties to agreements (plaintiff, defendant, guarantor, landlord, tenant) | "ABC Ltd (the Tenant)" |
| LegalClause | Specific contractual provisions | "Section 5.2 - Termination Rights" |
| Obligation | Duties, responsibilities, commitments | "Tenant shall pay rent by the 5th" |
| Deadline | Time-bound requirements | "Within 30 days of notice" |
| Court | Courts, tribunals, arbitration bodies | "Tel Aviv Magistrate Court" |
| Statute | Laws, regulations, legal references | "Contract Law (General Part), 5733-1973" |
| LegalTerm | Domain-specific terminology | "Force Majeure", "Indemnification" |
| Person | Keep from defaults | Named individuals |
| Organization | Keep from defaults | Companies, agencies |
| Location | Keep from defaults | Addresses, jurisdictions |
| Monetary | Payment amounts, penalties, fees | "NIS 50,000 per month" |

## Impact

**High** -- Domain-specific entity types enable:
- Querying "what are the tenant's obligations?" (Obligation entities linked to ContractParty)
- Finding all deadlines in a contract (Deadline entities)
- Tracing legal references across documents (Statute entities)

## Risk

**Low** -- Pure configuration. No code changes. Existing data would need re-ingestion to benefit from new types.

## Trade-offs

- More types = more entities extracted = higher LLM token usage during indexing
- Too many types can confuse the LLM -- keep to ~11-12 total
- Re-ingestion required for existing documents

## Decision

- [x] Approved
- [ ] Deferred
- [ ] Rejected

Notes: Applied 2026-04-06. Entity types managed via config.md (Extraction section). Affects ingestion only (extraction prompt) — queries benefit indirectly via better entity descriptions and graph structure. Existing documents need re-ingestion to benefit. SETUP.md updated with per-client domain configuration phase (Phase 6b).

**Commits:** `36b68c14` (implementation + optimization plan), `7d320527` (coupling warning)
**Rollback:** `git revert 7d320527 36b68c14`
