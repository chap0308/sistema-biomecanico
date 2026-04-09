# PLANS.md

## Milestone 1: RAG Foundations

### Scope

- define `Source`, `Asset`, and `Segment`
- preserve YouTube ingestion
- add local-first processing direction
- keep Supabase and Qdrant roles separate

### Acceptance Criteria

- source model exists
- segment model exists
- architecture docs are present
- project guidance is present

### Validation

- docs exist in `docs/`
- repo-level guidance exists in `AGENTS.md`

## Milestone 2: Ingestion Layer

### Scope

- ingest YouTube URLs
- ingest local videos
- ingest webpages
- persist normalized source metadata

### Acceptance Criteria

- source normalization is stable
- duplicate sources can be skipped
- artifacts can be traced back to source ids

### Validation

- `pytest tests/test_ingestion*.py`

## Milestone 3: Segment Construction

### Scope

- ASR integration
- OCR integration
- scene detection
- retrieval text construction

### Acceptance Criteria

- each processed source yields segments
- each segment has timestamps
- each segment has retrieval text

### Validation

- `pytest tests/test_segments*.py`

## Milestone 4: Indexing

### Scope

- Qdrant collection creation
- dense embeddings
- sparse retrieval metadata
- upsert by stable `segment_id`

### Acceptance Criteria

- segments can be indexed incrementally
- reindexing does not duplicate points
- payload filters work

### Validation

- `pytest tests/test_indexing*.py`

## Milestone 5: Retrieval And Answering

### Scope

- hybrid retrieval
- reranking hook
- grounded answer generation
- citations by timestamp

### Acceptance Criteria

- query returns cited sources
- retrieval can filter by source type and language
- answer does not invent absent evidence

### Validation

- `pytest tests/test_retrieval*.py`
- `pytest tests/test_rag*.py`

## Milestone 6: Premium Video Route

### Scope

- Gemini premium path
- optional richer visual summaries
- fallback to local path when unavailable

### Acceptance Criteria

- router selects premium or local path
- quota exhaustion does not block ingestion

### Validation

- `pytest tests/test_router*.py`
