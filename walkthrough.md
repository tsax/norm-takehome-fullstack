# Code Walkthrough

## Architecture Overview

```
┌─────────────────┐     HTTP      ┌─────────────────┐
│   Next.js UI    │ ────────────▶ │   FastAPI       │
│   (port 3000)   │               │   (port 8000)   │
└─────────────────┘               └────────┬────────┘
                                           │
                                  ┌────────▼────────┐
                                  │  QdrantService  │
                                  │  (in-memory)    │
                                  └────────┬────────┘
                                           │
                         ┌─────────────────┼─────────────────┐
                         ▼                 ▼                 ▼
                  ┌──────────┐      ┌──────────┐      ┌──────────┐
                  │ HuggingFace│    │  Qdrant  │      │   Groq   │
                  │ Embeddings │    │  Vector  │      │   LLM    │
                  │  (local)   │    │  Store   │      │  (cloud) │
                  └──────────┘      └──────────┘      └──────────┘
```

## Request Flow

1. User submits query via frontend
2. Frontend calls `GET /query?q=...`
3. `QdrantService.query()`:
   - Embeds query using HuggingFace (`BAAI/bge-small-en-v1.5`)
   - Retrieves top-k similar document chunks from Qdrant
   - Sends chunks + query to Groq LLM with citation prompt
   - Returns response with citations and relevance scores
4. Frontend displays answer with clickable citations

---

## Key Files

| File | Purpose |
|------|---------|
| `app/utils.py` | Core RAG logic: `DocumentService`, `QdrantService`, data models |
| `app/main.py` | FastAPI endpoints (`/query`, `/health`), CORS, lifespan |
| `frontend/app/page.tsx` | Main page, state management, API calls |
| `frontend/components/*.tsx` | UI components (SearchInput, ResponseCard, CitationList, etc.) |

---

## Architectural Decisions & Tradeoffs

### 1. PDF Parsing: Section-Based vs Fixed-Size Chunking

**Chose:** Section-based parsing (regex: `\d+(?:\.\d+)+\.`)

| Approach | Pros | Cons |
|----------|------|------|
| Section-based | Semantic coherence, accurate citations, legal traceability | Assumes consistent numbering format |
| Fixed-size (512 tokens) | Works on any document | Breaks mid-sentence, vague citations |

**Production consideration:** Real legal docs may have inconsistent formatting. Consider hybrid approach with fallback to sentence-based chunking.

---

### 2. Vector Store: In-Memory vs Persistent

**Chose:** Qdrant in-memory (`:memory:`)

| Approach | Pros | Cons |
|----------|------|------|
| In-memory | Simple, no setup, fast for demo | Data lost on restart, rebuilds index every startup |
| Persistent (Qdrant server) | Data survives restarts, scalable | Requires separate service, more infra |

**Production consideration:** Use persistent Qdrant with Docker Compose or managed Qdrant Cloud. Add index versioning for document updates.

---

### 3. Embeddings: Local vs API

**Chose:** HuggingFace local (`BAAI/bge-small-en-v1.5`)

| Approach | Pros | Cons |
|----------|------|------|
| Local (HuggingFace) | Free, no API limits, works offline, data stays local | Slower, uses container memory (~500MB) |
| API (OpenAI, Cohere) | Fast, high quality | Costs money, rate limits, data leaves your infra |

**Production consideration:** For sensitive legal data, local embeddings may be required for compliance. Consider GPU acceleration for scale.

---

### 4. LLM: Cloud API vs Self-Hosted

**Chose:** Groq cloud API (`llama-3.3-70b-versatile`)

| Approach | Pros | Cons |
|----------|------|------|
| Cloud API (Groq) | Fast, powerful models, no GPU needed | Costs at scale, data leaves your infra, rate limits |
| Self-hosted (Ollama) | Data stays local, no API costs | Requires GPU, slower, smaller models |

**Production consideration:** For legal compliance, may need self-hosted or SOC2-compliant provider. Implement retry logic, fallback models, and rate limiting.

---

### 5. Query Engine: CitationQueryEngine vs Custom

**Chose:** LlamaIndex `CitationQueryEngine`

| Approach | Pros | Cons |
|----------|------|------|
| CitationQueryEngine | Built-in citation formatting, less code | Black box, re-chunks nodes internally |
| Custom (VectorRetriever + prompt) | Full control, transparent, easier debugging | More code to maintain |

**Production consideration:** CitationQueryEngine works but can be opaque. For complex requirements, custom pipeline gives more control over citation formatting and score preservation.

---

### 6. Frontend: Local vs Containerized

**Chose:** Frontend runs locally (per requirements)

| Approach | Pros | Cons |
|----------|------|------|
| Local dev server | Hot reload, fast iteration | Different from prod |
| Containerized | Consistent with prod | Slower dev cycle |

**Production consideration:** Containerize frontend for deployment. Use multi-stage Docker build. Consider SSR vs static export based on SEO needs.

---

## Production Checklist

### Security
- [ ] Move API keys to secrets manager (not env vars)
- [ ] Add authentication (JWT, OAuth)
- [ ] Rate limiting on `/query` endpoint
- [ ] Input sanitization (query length limits)
- [ ] CORS: restrict to specific origins (not `*`)

### Reliability
- [ ] Health checks with dependency status (Qdrant, Groq)
- [ ] Retry logic for Groq API calls
- [ ] Circuit breaker for external services
- [ ] Graceful degradation if LLM unavailable

### Scalability
- [ ] Persistent vector store (Qdrant server/cloud)
- [ ] Redis cache for repeated queries
- [ ] Horizontal scaling (stateless API containers)
- [ ] CDN for frontend static assets

### Observability
- [ ] Structured logging (JSON)
- [ ] Request tracing (correlation IDs)
- [ ] Metrics (latency, error rates, cache hits)
- [ ] Alerting on error spikes

### Data Pipeline
- [ ] Document versioning (track which PDF version)
- [ ] Incremental index updates (don't rebuild everything)
- [ ] Index validation (ensure all sections parsed)
- [ ] Backup/restore for vector store

---

## Local Development

```bash
# Backend (Docker)
docker build -t westeros-laws .
docker run -p 8000:8000 -e GROQ_API_KEY=xxx westeros-laws

# Frontend (local)
cd frontend && pnpm dev

# Test
curl "http://localhost:8000/query?q=theft"
open http://localhost:3000
```

---

## LlamaIndex Migration Notes

Original imports (2024) → Updated imports (2025):

```python
# OLD
from llama_index import VectorStoreIndex

# NEW
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
```

Requires modular packages: `llama-index-core`, `llama-index-vector-stores-qdrant`, etc.
