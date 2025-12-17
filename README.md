# Westeros Laws API

Query the Laws of the Seven Kingdoms using natural language.

## Quick Start

1. Get a free Groq API key at [console.groq.com](https://console.groq.com)

2. Run:
```bash
docker build -t westeros-laws .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key_here westeros-laws
```

3. Open `http://localhost:8000/docs` to use the API

### Example Query
```bash
curl "http://localhost:8000/query?q=What%20happens%20if%20I%20steal?"
```

---

## Design Choices & Assumptions

### Backend

**PDF Parsing (DocumentService)**
- Used **PyMuPDF (fitz)** for text extraction - it handles spacing and formatting better than pypdf
- Split documents by **section numbers** (regex: `\d+(?:\.\d+)+\.`) rather than fixed chunks
- Each law section becomes a separate Document with section number as metadata
- *Assumption:* The PDF follows a consistent `X.Y.Z.` numbering format

**Why Section-Based Parsing Matters for Legal RAG**

The instructions emphasize that *"working with legal data requires highly curated RAG pipelines—we cannot blindly load documents into a vector store."* Here's why section-based parsing is critical:

1. **Semantic coherence**: Legal sections are self-contained units of meaning. Fixed-size chunking (e.g., 512 tokens) would arbitrarily split mid-sentence or mid-clause, destroying legal context.

2. **Citation accuracy**: When a user asks "what's the penalty for theft?", we need to cite *Section 3.2.1* specifically—not "characters 1500-2000 of the PDF." Section metadata enables precise attribution.

3. **Retrieval quality**: Vector similarity works best when chunks represent complete thoughts. A section like "Theft from a Sept shall be punishable by..." is more semantically searchable than a fragment.

4. **Legal defensibility**: In compliance contexts, vague citations are unacceptable. Lawyers need to verify sources—section numbers provide that traceability.

**Vector Store & Retrieval (QdrantService)**
- **Qdrant in-memory** - simple setup, no persistence needed for this demo
- **HuggingFace embeddings** (`BAAI/bge-small-en-v1.5`) - runs locally in container, no external API needed
- **Groq LLM** (`llama-3.3-70b-versatile`) - fast inference, generous free tier
- `self.k=3` returns top 3 most relevant sections per query

**Query Engine**
- Used **CitationQueryEngine** from LlamaIndex for automatic source attribution
- Custom prompt template to ensure direct, confident answers (default was too hedgy)
- Citations include section numbers for traceability

**API Design**
- `/query` endpoint - main RAG interface with proper error handling
- `/health` endpoint - for container orchestration and monitoring
- CORS enabled for frontend integration
- Output model enforces consistent JSON structure

**Error Handling**
- Input validation (empty query check)
- Service availability check (503 if not initialized)
- Graceful error responses with meaningful messages (500 with details)
- Logging for debugging in production

### Frontend

**Component Structure**
- Modular design with reusable components:
  - `SearchInput` - form with query input and submit button
  - `ResponseCard` - displays query result and answer
  - `CitationList` - expandable accordion for sources
  - `LoadingState` - spinner with contextual message
  - `ErrorAlert` - error display with Chakra UI Alert
- Used existing **Chakra UI** components (consistent with starter code)
- TypeScript interfaces for type safety (`Citation`, `QueryResponse`)

**Information Visualization**
- **Expandable accordion** for citations - keeps UI clean while allowing deep-dive
- **Clickable citation references**: `[1]`, `[2]` in response text are interactive links that expand and scroll to the corresponding source
- **Relevance scores**: Each citation displays a color-coded match percentage (green ≥80%, yellow ≥60%, orange <60%)
- Loading spinner with contextual message ("Consulting the laws...")
- Error state with clear action item

**UX Decisions**
- Form submit on Enter key (natural search behavior)
- Disabled button during loading (prevents duplicate requests)
- Question echoed back in results (confirms what was asked)
- *Assumption:* API runs on `localhost:8000` (configurable via `NEXT_PUBLIC_API_URL`)

---

## Project Structure

```
├── app/
│   ├── main.py          # FastAPI endpoints (/query, /health) + CORS
│   └── utils.py         # DocumentService, QdrantService, models
├── docs/
│   └── laws.pdf         # Source document
├── frontend/
│   ├── app/page.tsx     # Main page (state management)
│   └── components/
│       ├── SearchInput.tsx
│       ├── ResponseCard.tsx
│       ├── CitationList.tsx
│       ├── LoadingState.tsx
│       └── ErrorAlert.tsx
├── Dockerfile
├── requirements.txt
└── README.md
```

## Running Frontend Locally

```bash
cd frontend
pnpm install
pnpm dev
```

Then open `http://localhost:3000` (backend must be running on port 8000).

---

## Technical Notes

### LlamaIndex Migration (2024 → 2025)

The original starter code used LlamaIndex imports from early 2024. LlamaIndex has since restructured into modular packages. Key changes made:

| Original Import | Updated Import |
|----------------|----------------|
| `from llama_index import ...` | `from llama_index.core import ...` |
| `from llama_index.vector_stores import QdrantVectorStore` | `from llama_index.vector_stores.qdrant import QdrantVectorStore` |
| `from llama_index.embeddings import ...` | `from llama_index.embeddings.huggingface import HuggingFaceEmbedding` |
| `from llama_index.llms import ...` | `from llama_index.llms.groq import Groq` |

The modular structure requires installing separate packages (`llama-index-core`, `llama-index-vector-stores-qdrant`, etc.) rather than a monolithic `llama-index` package.

### Dependency Pinning

Docker builds required careful version pinning to avoid resolution loops:
- `huggingface-hub>=0.24.0,<1.0.0` - newer versions removed the `[inference]` extra that `llama-index-embeddings-huggingface` expects
- `sentence-transformers>=2.6.0,<6.0.0` - compatibility with HuggingFace embeddings
