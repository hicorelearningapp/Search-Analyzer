# summarizer/docx_generator.py
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime
from document_system import document_system  # import your existing document system


class DocxGenerator:
    @staticmethod
    def create_docx(
        topic: str,
        doc_type: str,
        summary_result: dict,
        output_path: str = None,
        author: str = None
    ) -> str:
        """
        Generate a DOCX file from summarization result.
        summary_result: dict from LLMSummarizer.summarize_with_structure()
        """
        doc = Document()

        # Set margins
        section = doc.sections[0]
        section.top_margin = section.bottom_margin = section.left_margin = section.right_margin = Inches(0.9)

        # --- Cover Page ---
        cover = doc.add_paragraph()
        cover.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = cover.add_run(f"{doc_type} on {topic}")
        run.font.name = "Calibri"
        run.font.size = Pt(26)
        run.bold = True
        run.font.color.rgb = RGBColor(0, 51, 153)

        doc.add_paragraph("")
        meta = doc.add_paragraph()
        meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
        authored = author or "Automated Report"
        meta.add_run(f"Author: {authored}").italic = True
        meta.add_run(f"    •    Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}").italic = True
        doc.add_page_break()

        # --- Content ---
        headings = summary_result.get("headings", [])
        content_text = summary_result.get("content", "")

        # Try splitting into sections using headings
        for heading in headings:
            if heading.lower() in content_text.lower():
                doc.add_heading(heading, level=1)
                # naive split: get text after heading
                parts = content_text.split(heading, 1)
                if len(parts) > 1:
                    para = doc.add_paragraph(parts[1].strip())
                    para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            else:
                # fallback: just dump content in order
                doc.add_heading(heading, level=1)
                doc.add_paragraph(content_text.strip())

        if not output_path:
            safe_topic = "".join(c if c.isalnum() or c in " _-" else "_" for c in topic)[:120]
            output_path = f"{safe_topic}_{doc_type.replace(' ', '_')}.docx"

        doc.save(output_path)
        return output_path


__all__ = ['DocxGenerator']
