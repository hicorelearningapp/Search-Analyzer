#services/pdf_service.py
from fastapi import UploadFile
from fastapi.responses import JSONResponse
from .base_manager import BaseAPIManager
from sources.pdf_loader import PDFManager
from services.types import DocumentTypeEnum
from fastapi import UploadFile, Form
from fastapi import Form
from services.types import DocumentTypeEnum
from app_state import AppState

class PDFClass(BaseAPIManager):
    async def process_pdf(self, file: UploadFile, doc_type: DocumentTypeEnum = Form(...), pages: int = 2):
        try:
            text = await PDFManager().extract_text(file=file)
            doc_type_str = doc_type.value if hasattr(doc_type, 'value') else doc_type
            
            self.retriever.process_text(
                text,
                metadata={"source": "pdf", "query": file.filename, "doc_type": doc_type_str}
            )
            summary = self.summarizer.summarize_with_structure(
                self.retriever, text, doc_type_str, pages
            )
            filename = self.save_docx(summary, "pdf", doc_type_str)
            return {
                "raw_text": text, 
                "summary": summary, 
                "download_link": f"/download/{filename}"
            }
        except Exception as e:
            return JSONResponse(
                status_code=500, 
                content={"error": str(e)}
            )
