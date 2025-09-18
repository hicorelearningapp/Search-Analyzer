# summarizer/docx_generator.py
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

class DocxGenerator:
    def __init__(self, default_author: str = "Automated Report"):
        self.default_author = default_author

    def generate_docx(
        self,
        content: Dict[str, Any],
        output_path: str,
        doc_type: Optional[str] = None,
        title: Optional[str] = None,
        author: Optional[str] = None
    ) -> str:
        doc = Document()

        # Page margins
        section = doc.sections[0]
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)

        # Title
        doc_title = title or content.get("title", "Summary")
        heading = doc.add_heading(doc_title, level=1)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Metadata
        author = author or self.default_author
        meta = doc.add_paragraph()
        meta.add_run(f"Author: {author}    ").italic = True
        meta.add_run(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}").italic = True
        doc.add_paragraph("")

        # Content
        text = content.get("content", "")
        for paragraph in text.split("\n\n"):
            if paragraph.strip():
                para = doc.add_paragraph()
                run = para.add_run(paragraph.strip())
                run.font.size = Pt(11)

        # Save file
        output_path = str(Path(output_path).absolute())
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        doc.save(output_path)
        return output_path
