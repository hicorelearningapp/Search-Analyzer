# summarizer/common.py
import os
from fastapi.responses import FileResponse
from .llm_summarizer import LLMSummarizer
from .docx_generator import DocxGenerator


class SummarizerPipeline:
    """Pipeline to summarize text and optionally generate/download a docx report."""

    def __init__(self, reports_dir: str | None = None, model_name: str = "gpt-4"):
        self.reports_dir = reports_dir or os.path.join(os.getcwd(), "reports")
        self.summarizer = LLMSummarizer(model_name=model_name)
        os.makedirs(self.reports_dir, exist_ok=True)

    def run(
        self,
        text: str,
        doc_type: str,
        pages: int,
        label: str,
        outfile_name: str,
        download: bool = False,
    ):
        # Step 1: Summarize
        summary = self.summarizer.summarize(text, doc_type=doc_type, pages=pages)

        # Step 2: Generate Docx
        outfile = os.path.join(self.reports_dir, f"{outfile_name}_{doc_type}.docx")
        path = DocxGenerator().generate_docx(label, doc_type, summary["content"], outfile)

        # Step 3: Handle return type
        if download:
            return FileResponse(path, filename=os.path.basename(path))

        return {"summary": summary["content"], "docx": path, "cached": summary.get("cached", False)}
