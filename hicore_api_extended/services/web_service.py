#services/web_service.py
from fastapi.responses import JSONResponse
from .base_manager import BaseAPIManager
from sources.web_search import WebSearchManager
from fastapi import Form
from services.types import DocumentTypeEnum

class WebClass(BaseAPIManager):
    async def process(self, query: str, doc_type: DocumentTypeEnum = Form(...), pages: int = 2):
        try:
            search_manager = WebSearchManager()
            text = search_manager.run(query)
            self.retriever.process_text(
                text,
                metadata={"source": "web", "query": query, "doc_type": doc_type.value}
            )
            summary = self.summarizer.summarize_with_structure(self.retriever, query, doc_type.value, pages)
            filename = self.save_docx(summary, "web", doc_type.value)
            return {
                "query": query,
                "raw_text": text[:1000] + "..." if len(text) > 1000 else text,
                "summary": summary,
                "download_link": f"/download/{filename}"
            }
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})
