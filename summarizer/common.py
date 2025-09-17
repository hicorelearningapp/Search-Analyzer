# summarizer/common.py
import os
from typing import Dict, Any, Optional
from fastapi.responses import FileResponse
from config import Config
from .llm_summarizer import LLMSummarizer

class SummarizerPipeline:
    def __init__(self, reports_dir: Optional[str] = None, llm=None, generator=None):
        self.reports_dir = reports_dir or Config.REPORTS_DIR
        os.makedirs(self.reports_dir, exist_ok=True)

        if llm:
            self.summarizer = llm
        else:
            self.summarizer = LLMSummarizer()

        if generator:
            self.generator = generator
        else:
            from .docx_generator import DocxGenerator
            self.generator = DocxGenerator()

    def run(self, text: str, doc_type: str, pages: int, label: str, outfile_name: str, download: bool = False) -> Dict[str, Any]:
        summary = self.summarizer.summarize(text, doc_type=doc_type, pages=pages)
        safe_name = "".join(c if c.isalnum() else "_" for c in outfile_name)[:200]
        outfile = os.path.join(self.reports_dir, f"{safe_name}_{doc_type}.docx")
        path = self.generator.generate_docx(content={"content": summary["content"]}, output_path=outfile, doc_type=doc_type, title=label)
        if download:
            return FileResponse(path, filename=os.path.basename(path))
        return {"summary": summary["content"], "docx": path, "cached": summary.get("cached", False)}
