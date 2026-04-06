# System Configuration

## Display

- Title: LightRAG
- Description: Graph Based RAG System

## Language

- Summary Language: Hebrew

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

## User Prompt

You are answering questions about legal documents. Accuracy is paramount.
If uncertain about any detail, say so explicitly.
Never paraphrase legal clauses — quote them directly.
Always cite the specific document and section when possible.
