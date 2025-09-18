# summarizer/document_processor.py
from typing import Dict, List, Optional, Union
from pathlib import Path
import json
from sources.retriever import VectorRetriever
from .llm_summarizer import LLMSummarizer
from .docx_generator import DocxGenerator
from document_system import document_system

class DocumentProcessor:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.retriever = VectorRetriever(model_name=model_name)
        self.summarizer = LLMSummarizer()
        self.generator = DocxGenerator()

    def process_document(self, text: str, source_type: str, doc_type: Optional[str] = None, chunk_size: int = 500) -> Dict:
        headings = []
        if doc_type:
            dt = document_system.get_document_type(doc_type)
            if dt:
                headings = dt.structure
            if pages is None:
                # assume ~2000 characters per page -> tune as needed
                pages = max(1, len(text) // 2000)
        self.retriever.build_index(text, chunk_size=chunk_size)
        summary = self.summarizer.summarize_with_structure(text, doc_type=doc_type, pages=pages)
        num_chunks = max(1, (len(text) // chunk_size) + (1 if len(text) % chunk_size else 0))
        return {"source_type": source_type, "doc_type": doc_type, "structure": headings, "summary": summary, "num_chunks": num_chunks}

    def search_document(self, query: str, source_type: str, top_k: int = 3) -> List[Dict]:
        chunks = self.retriever.get_top_chunks(query, top_k=top_k)
        return [{"content": chunk, "relevance": i+1} for i, chunk in enumerate(chunks)]

    def generate_document(self, content: Union[str, Dict], output_path: str, format: str = "docx") -> str:
        if format.lower() == "docx":
            return self.generator.generate_docx(content=content if isinstance(content, dict) else {"content": content}, output_path=output_path)
        raise ValueError("Unsupported format")
