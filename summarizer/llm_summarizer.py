# summarizer/llm_summarizer.py
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

from document_system import document_system
from sources.retriever import VectorRetriever


class SummaryResult(BaseModel):
    """Result of text summarization."""
    summary: str
    metadata: dict = {}


class LLMSummarizer:
    """
    Summarizer that:
      1. Retrieves relevant chunks using VectorRetriever
      2. Builds a structured prompt based on DocumentSystem
      3. Summarizes text using a HuggingFace model
    """

    def __init__(
        self,
        model_name: str = "facebook/bart-large-cnn",
        max_length: int = 200,
        min_length: int = 50
    ):
        self.model_name = model_name
        self.max_length = max_length
        self.min_length = min_length
        self.tokenizer = None
        self.model = None
        self._initialized = False
        self.retriever = VectorRetriever()

    def _initialize_model(self):
        """Lazy initialization of the model."""
        if not self._initialized:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self._initialized = True

    def _hf_summarize(self, text: str) -> str:
        """Summarize text with HuggingFace seq2seq model."""
        self._initialize_model()
        inputs = self.tokenizer(
            text,
            max_length=1024,
            return_tensors="pt",
            truncation=True
        )
        with torch.no_grad():
            summary_ids = self.model.generate(
                inputs["input_ids"],
                max_length=self.max_length,
                min_length=self.min_length,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True
            )
        return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    def summarize_with_structure(self, text: str, doc_type: str, pages: int = 1) -> Dict[str, Any]:
        """
        Summarize input text according to document type structure.
        Retrieval → Chunks → Prompt → Summarizer
        """

        # 1. Get template (headings) from document system
        doc_type_obj = document_system.get_document_type(doc_type)
        if not doc_type_obj:
            raise ValueError(f"Unknown document type '{doc_type}'")
        headings = doc_type_obj.structure

        # 2. Use retriever to get relevant chunks (pdf first, then video)
        query = f"{doc_type}. Relevant sections: {'; '.join(headings)}"
        chunks = self.retriever.get_top_chunks(query, "pdf", top_k=3)
        if not chunks:
            chunks = self.retriever.get_top_chunks(query, "video", top_k=3)

        # 3. If no chunks, fallback to raw text
        if chunks:
            chunk_text = "\n\n".join(chunks)
        else:
            chunk_text = text if len(text) < 12000 else text[:12000]

        # 4. Build pseudo-prompt (not GPT-style, but structured guidance)
        structured_input = (
            f"Write a '{doc_type}' document with the following sections:\n"
            + "\n".join(f"- {h}" for h in headings)
            + f"\n\nBase material:\n{chunk_text}"
        )

        # 5. Run HuggingFace summarizer
        summary_text = self._hf_summarize(structured_input)

        return {
            "document_type": doc_type,
            "headings": headings,
            "content": summary_text,
            "model": self.model_name,
            "metadata": {
                "max_length": self.max_length,
                "min_length": self.min_length,
            }
        }


# For backward compatibility
def summarize_with_structure(text: str, doc_type: str, pages: int = 1, **kwargs) -> Dict[str, Any]:
    summarizer = LLMSummarizer()
    return summarizer.summarize_with_structure(text, doc_type, pages)
