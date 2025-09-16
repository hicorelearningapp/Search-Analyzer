# sources/pdf_loader.py
import io
import os
from typing import Optional
from fastapi import UploadFile
from PyPDF2 import PdfReader

REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

class PDFExtractor:
    @staticmethod
    def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
        text_parts = []
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                try:
                    t = page.extract_text() or ""
                    text_parts.append(t)
                except Exception:
                    # skip pages we cannot parse
                    continue
        except Exception as e:
            raise RuntimeError(f"Error reading PDF: {e}")
        return "\n".join(text_parts)

class PDFSummarizer:
    def __init__(self, reports_dir: Optional[str] = None):
        self.reports_dir = reports_dir or REPORTS_DIR

    async def summarize_pdf(self, file: UploadFile, doc_type: str, pages: int, download: bool = False) -> dict:
        """
        Save uploaded PDF, extract text, and return a pipeline summary response.
        The actual summarization is delegated to SummarizerPipeline in summarizer.common
        (imported lazily to avoid circular imports).
        """
        file_bytes = await file.read()
        filename = file.filename or "uploaded.pdf"
        output_path = os.path.join(self.reports_dir, filename)
        with open(output_path, "wb") as f:
            f.write(file_bytes)

        from summarizer.common import SummarizerPipeline  # lazy import
        pipeline = SummarizerPipeline()
        text = PDFExtractor.extract_text_from_pdf_bytes(file_bytes)
        return pipeline.run(text=text, doc_type=doc_type, pages=pages, label=filename, outfile_name=os.path.splitext(filename)[0], download=download)
