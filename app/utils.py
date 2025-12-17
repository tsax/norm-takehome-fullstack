from pydantic import BaseModel
import qdrant_client
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.schema import Document
from llama_index.core.query_engine import CitationQueryEngine
from llama_index.core.prompts import PromptTemplate
from dataclasses import dataclass

CITATION_QA_TEMPLATE = PromptTemplate(
    "You are an expert on the Laws of the Seven Kingdoms. "
    "Answer the question directly based on the sources provided. "
    "Cite sources using [1], [2], etc. Be specific and confident.\n\n"
    "Sources:\n"
    "{context_str}\n\n"
    "Question: {query_str}\n\n"
    "Answer: "
)
import fitz  # PyMuPDF
import re
import os

# Configuration
EMBED_MODEL = os.environ.get('EMBED_MODEL', 'BAAI/bge-small-en-v1.5')
GROQ_MODEL = os.environ.get('GROQ_MODEL', 'llama-3.3-70b-versatile')

@dataclass
class Input:
    query: str
    file_path: str

@dataclass
class Citation:
    source: str
    text: str
    relevance_score: float  # Similarity score from vector search (0-1)

class Output(BaseModel):
    query: str
    response: str
    citations: list[Citation]

class DocumentService:
    """Load PDF and create Document objects, one per law section."""

    def __init__(self, pdf_path: str = "docs/laws.pdf"):
        self.pdf_path = pdf_path

    def create_documents(self) -> list[Document]:
        # Extract text from PDF
        doc = fitz.open(self.pdf_path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()

        # Split by section numbers (e.g., "1.1.", "3.1.1.", "10.1.1.1.")
        # Pattern captures: section number and content until next section
        pattern = r'(\d+(?:\.\d+)+)\.\s*\n(.*?)(?=\d+(?:\.\d+)*\.\s*\n|$)'
        matches = re.findall(pattern, text, re.DOTALL)

        documents = []
        for section_num, content in matches:
            content = content.strip().replace('\n', ' ')
            if not content:
                continue

            documents.append(Document(
                text=content,
                metadata={"section": section_num}
            ))

        return documents

class QdrantService:
    def __init__(self, k: int = 2):
        self.index = None
        self.k = k
    
    def connect(self) -> None:
        client = qdrant_client.QdrantClient(location=":memory:")

        vstore = QdrantVectorStore(client=client, collection_name='temp')

        # Configure global settings
        Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)
        Settings.llm = Groq(model=GROQ_MODEL)

        self.index = VectorStoreIndex.from_vector_store(vector_store=vstore)

    def load(self, docs: list[Document]) -> None:
        self.index.insert_nodes(docs)
    
    def query(self, query_str: str) -> Output:
        """Query the index and return response with citations."""
        query_engine = CitationQueryEngine.from_args(
            self.index,
            similarity_top_k=self.k,
            citation_chunk_size=512,
            citation_qa_template=CITATION_QA_TEMPLATE,
        )

        response = query_engine.query(query_str)

        # Extract citations from source nodes with relevance scores
        citations = []
        for node in response.source_nodes:
            section = node.node.metadata.get("section", "Unknown")
            # CitationQueryEngine may store score differently - try multiple approaches
            score = None
            if hasattr(node, 'score') and node.score is not None:
                score = node.score
            elif hasattr(node, 'get_score'):
                try:
                    score = node.get_score()
                except:
                    pass
            # Default to 0.0 if no score available (CitationQueryEngine re-chunks nodes)
            score = score if score is not None else 0.0
            citations.append(Citation(
                source=f"Section {section}",
                text=node.node.text[:500],  # Truncate long texts
                relevance_score=round(float(score), 3)
            ))

        return Output(
            query=query_str,
            response=str(response),
            citations=citations
        )
       

if __name__ == "__main__":
    # Example workflow
    doc_serivce = DocumentService() # implemented
    docs = doc_serivce.create_documents() # NOT implemented

    index = QdrantService() # implemented
    index.connect() # implemented
    index.load() # implemented

    index.query("what happens if I steal?") # NOT implemented
