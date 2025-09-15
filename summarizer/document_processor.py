from typing import Dict, List, Optional, Union
from pathlib import Path
import json

from sources.retriever import VectorRetriever
from summarizer.llm_summarizer import LLMSummarizer
from summarizer.docx_generator import DocxGenerator
from document_system import DocumentSystem

class DocumentProcessor:
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):

        self.retriever = VectorRetriever(model_name=model_name)
        self.summarizer = LLMSummarizer()
        self.generator = DocxGenerator()
        
    def process_document(
        self, 
        text: str, 
        source_type: str, 
        doc_type: Optional[str] = None,
        chunk_size: int = 500
    ) -> Dict:

        self.retriever.build_index(text, source_type, chunk_size)
        
        # Get document structure based on type
        structure = []
        if doc_type:
            doc_system = DocumentSystem()
            structure = doc_system.get_document_type(doc_type)
        
        # Generate initial summary
        summary = self.summarizer.summarize(text)
        
        return {
            "source_type": source_type,
            "doc_type": doc_type,
            "structure": structure,
            "summary": summary,
            "num_chunks": len(text) // chunk_size + (1 if len(text) % chunk_size else 0)
        }
    
    def search_document(self, query: str, source_type: str, top_k: int = 3) -> List[Dict]:

        chunks = self.retriever.get_top_chunks(query, source_type, top_k)
        return [{"content": chunk, "relevance": i+1} for i, chunk in enumerate(chunks)]
    
    def generate_document(
        self, 
        content: Union[str, Dict], 
        output_path: str, 
        format: str = "docx"
    ) -> str:

        if format.lower() == "docx":
            return self.generator.generate_docx(content, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def export_metadata(self, data: Dict, output_path: str) -> str:

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return output_path
    
    def clear_resources(self) -> None:
        """Clear all resources and indices."""
        self.retriever.clear_index()
        self.summarizer.clear_cache()  # Assuming LLMSummarizer has a clear_cache method
