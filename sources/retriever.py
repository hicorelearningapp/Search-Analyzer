# sources/retriever.py
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

class RetrievalMethod(str, Enum):
    TFIDF = "tfidf"
    EMBEDDINGS = "embeddings"
    FAISS = "faiss"


class SearchResult(BaseModel):
    """Result of a search query."""
    text: str
    score: float
    metadata: dict = {}


class VectorRetriever:
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        retrieval_method: RetrievalMethod = RetrievalMethod.FAISS,
        chunk_size: int = 1000,
        chunk_overlap: int = 150
    ):
        self.model_name = model_name
        self.retrieval_method = retrieval_method
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embeddings = None
        self.vectorstore = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def _initialize_embeddings(self):
        """Initialize the embedding model."""
        if self.embeddings is None:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )

    def process_text(self, text: str, metadata: Optional[dict] = None) -> List[str]:
        """Process text into chunks and prepare for search."""
        if not text.strip():
            return []
            
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Initialize embeddings if using FAISS
        if self.retrieval_method == RetrievalMethod.FAISS:
            self._initialize_embeddings()
            self.vectorstore = FAISS.from_texts(
                chunks,
                embedding=self.embeddings,
                metadatas=[metadata or {}] * len(chunks) if metadata else None
            )
        
        return chunks

    def search(self, query: str, k: int = 3) -> List[SearchResult]:
        """Search for relevant text chunks."""
        if self.vectorstore is None:
            raise ValueError("No documents have been processed yet. Call process_text() first.")
            
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return [
            SearchResult(
                text=doc.page_content,
                score=float(score),
                metadata=doc.metadata
            )
            for doc, score in results
        ]
    def build_index(self, text: str, metadata: Optional[dict] = None, chunk_size: Optional[int] = None):

        if chunk_size:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=self.chunk_overlap
            )
        chunks = self.text_splitter.split_text(text)
        if not chunks:
            return []

        self._initialize_embeddings()
        # NOTE: depending on langchain version the factory arg name may be 'embeddings' or 'embedding'
        try:
            # try the common signature first
            self.vectorstore = FAISS.from_texts(
                chunks,
                embeddings=self.embeddings,
                metadatas=[metadata or {}] * len(chunks)
            )
        except TypeError:
            # fallback to different param name some versions use
            self.vectorstore = FAISS.from_texts(
                chunks,
                embedding=self.embeddings,
                metadatas=[metadata or {}] * len(chunks)
            )
        return chunks

    def get_top_chunks(self, query: str, top_k: int = 3):
        """Return the raw chunk strings (compatibility wrapper)."""
        if self.vectorstore is None:
            return []
        # similarity_search_with_score returns list[(Document, score)]
        results = self.vectorstore.similarity_search_with_score(query, k=top_k)
        return [doc.page_content if hasattr(doc, "page_content") else str(doc) for doc, _ in results]

    def get_relevant_documents(self, query: str, k: int = 3):
        """Return Document objects (langchain style)."""
        if self.vectorstore is None:
            return []
        return [doc for doc in self.vectorstore.similarity_search(query, k=k)]
