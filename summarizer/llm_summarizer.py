from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from sources.retriever import VectorRetriever
from document_system import document_system
from config import Config

class LLMSummarizer:
    
    def __init__(self, model_name: str = "gpt-4", retriever: Optional[VectorRetriever] = None):
        # Verify configuration is loaded
        Config.verify_config()
        
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            openai_api_key=Config.OPENAI_API_KEY
        )
        self.retriever = retriever or VectorRetriever()
        self.cache: Dict[str, str] = {}
    
    def summarize(self, text: str, doc_type: Optional[str] = None, pages: int = 2) -> Dict[str, Any]:
        # Use cache if available
        cache_key = f"{hash(text)}_{doc_type}_{pages}"
        if cache_key in self.cache:
            return {"content": self.cache[cache_key], "cached": True}
        
        # Default headings if doc_type not specified
        if not doc_type:
            headings = ["Summary"]
        else:
            headings = document_system["DocumentTypes"].get(doc_type, ["Summary"])
        
        # Try retrieval from pdf index first, then youtube
        query = f"{doc_type}. Relevant sections: {'; '.join(headings)}"
        chunks = self.retriever.get_top_chunks(query, "pdf", top_k=3)
        if not chunks:
            chunks = self.retriever.get_top_chunks(query, "video", top_k=3)

        if chunks:
            chunk_text = "\n\n".join(chunks)
        else:
            chunk_text = text if len(text) < 15000 else text[:15000]

        # Prepare the prompt
        prompt = self._build_prompt(chunk_text, doc_type, pages, headings)
        
        # Generate the summary
        response = self.llm.invoke(prompt)
        summary = response.content
        
        # Cache the result
        self.cache[cache_key] = summary
        
        return {
            "content": summary,
            "headings": headings,
            "cached": False
        }
    
    def _build_prompt(self, text: str, doc_type: Optional[str], pages: int, headings: list) -> str:
        """Build the prompt for the language model."""
        return (
            f"You are tasked with writing a {doc_type or 'document'} based on the following material:\n\n"
            f"{text}\n\n"
            f"Structure the output into the following sections:\n"
            + "\n".join(f"- {h}" for h in headings) +
            f"\n\nWrite enough content so that the total length is about {pages} pages in a Word document."
            "\nBe clear, structured, and factual."
            "\nReturn plain text without Markdown symbols."
        )
    
    def clear_cache(self) -> None:
        """Clear the summary cache."""
        self.cache.clear()
