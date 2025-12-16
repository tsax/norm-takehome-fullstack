from pydantic import BaseModel
import qdrant_client
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.schema import Document
from dataclasses import dataclass
import os

# Ollama configuration (runs locally, no API key needed)
OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
LLM_MODEL = os.environ.get('LLM_MODEL', 'llama3')
EMBED_MODEL = os.environ.get('EMBED_MODEL', 'nomic-embed-text')

@dataclass
class Input:
    query: str
    file_path: str

@dataclass
class Citation:
    source: str
    text: str

class Output(BaseModel):
    query: str
    response: str
    citations: list[Citation]

class DocumentService:

    """
    Update this service to load the pdf and extract its contents.
    The example code below will help with the data structured required
    when using the QdrantService.load() method below. Note: for this
    exercise, ignore the subtle difference between llama-index's 
    Document and Node classes (i.e, treat them as interchangeable).

    # example code
    def create_documents() -> list[Document]:

        docs = [
            Document(
                metadata={"Section": "Law 1"},
                text="Theft is punishable by hanging",
            ),
            Document(
                metadata={"Section": "Law 2"},
                text="Tax evasion is punishable by banishment.",
            ),
        ]

        return docs

     """

class QdrantService:
    def __init__(self, k: int = 2):
        self.index = None
        self.k = k
    
    def connect(self) -> None:
        client = qdrant_client.QdrantClient(location=":memory:")

        vstore = QdrantVectorStore(client=client, collection_name='temp')

        # Configure global settings with Ollama (runs locally, no API key needed)
        Settings.embed_model = OllamaEmbedding(
            model_name=EMBED_MODEL,
            base_url=OLLAMA_BASE_URL
        )
        Settings.llm = Ollama(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            request_timeout=120.0
        )

        self.index = VectorStoreIndex.from_vector_store(vector_store=vstore)

    def load(self, docs = list[Document]):
        self.index.insert_nodes(docs)
    
    def query(self, query_str: str) -> Output:

        """
        This method needs to initialize the query engine, run the query, and return
        the result as a pydantic Output class. This is what will be returned as
        JSON via the FastAPI endpount. Fee free to do this however you'd like, but
        a its worth noting that the llama-index package has a CitationQueryEngine...

        Also, be sure to make use of self.k (the number of vectors to return based
        on semantic similarity).

        # Example output object
        citations = [
            Citation(source="Law 1", text="Theft is punishable by hanging"),
            Citation(source="Law 2", text="Tax evasion is punishable by banishment."),
        ]

        output = Output(
            query=query_str, 
            response=response_text, 
            citations=citations
            )
        
        return output

        """
       

if __name__ == "__main__":
    # Example workflow
    doc_serivce = DocumentService() # implemented
    docs = doc_serivce.create_documents() # NOT implemented

    index = QdrantService() # implemented
    index.connect() # implemented
    index.load() # implemented

    index.query("what happens if I steal?") # NOT implemented





