from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.utils import Output, DocumentService, QdrantService
import logging

logger = logging.getLogger(__name__)

# Global service instance
qdrant_service: QdrantService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    global qdrant_service

    # Load documents and create index
    doc_service = DocumentService()
    docs = doc_service.create_documents()

    qdrant_service = QdrantService(k=3)
    qdrant_service.connect()
    qdrant_service.load(docs)

    yield


app = FastAPI(
    title="Westeros Laws API",
    description="Query the Laws of the Seven Kingdoms using natural language",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "service": "westeros-laws-api"}


@app.get("/query", response_model=Output)
async def query_laws(q: str = Query(..., description="Your question about the laws")) -> Output:
    """
    Query the laws using natural language.

    Example: "What happens if I steal from the Sept?"
    """
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if qdrant_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        return qdrant_service.query(q)
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")