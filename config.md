# System Configuration
#
# Technical settings for the LightRAG server.
# For business-domain settings (language, entity types, extraction examples, user prompt),
# see domain.md.

## Display

- Title: LightRAG
- Description: Graph Based RAG System

## Model

- LLM Model: gpt-4.1-mini
- Rerank Binding: null

## Chunking

- Chunk Size: 1800
- Chunk Overlap Size: 200

## OCR

- Page Text Threshold: 50

## Concurrency

<!-- Supabase Nano pooler has 15 connection slots total.
     During document processing, the pipeline grabs DB connections for chunking,
     embeddings, and KG writes. If it takes too many, API endpoints (like document
     listing) hang because no connections are left.
     On paid plan (50+ pooler slots): raise to Max Parallel Insert: 4, Max DB Connections: 10 -->

- Max Parallel Insert: 1
- Max DB Connections: 3
