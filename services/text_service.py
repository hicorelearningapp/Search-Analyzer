#services/text_service.py
from fastapi.responses import JSONResponse
from base_manager import BaseAPIManager
from fastapi import Form
from services.types import DocumentTypeEnum

class TextClass(BaseAPIManager):
    async def process_text(self, text: str, doc_type: DocumentTypeEnum = Form(...), pages: int = 2):
        try:
            self.retriever.process_text(     
                text,
                metadata={"source": "text", "query": text, "doc_type": doc_type.value}
            )
            summary = self.summarizer.summarize_with_structure(self.retriever, text, doc_type.value, pages)
            filename = self.save_docx(summary, "text", doc_type.value)
            return {"raw_text": text, "summary": summary, "download_link": f"/download/{filename}"}
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})
