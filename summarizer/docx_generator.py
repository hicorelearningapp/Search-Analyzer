from typing import Dict, Any, Optional
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime
from pathlib import Path

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

        # Initialize document
        doc = Document()
        
        # Set up document margins
        section = doc.sections[0]
        section.top_margin = section.bottom_margin = section.left_margin = section.right_margin = Inches(0.9)
        
        # Extract content and metadata
        doc_title = title or content.get('title', 'Document')
        doc_type = doc_type or content.get('doc_type', 'Document')
        author = author or content.get('author', self.default_author)
        
        # Add cover page
        self._add_cover_page(doc, doc_title, doc_type, author)
        
        # Add content
        self._add_content(doc, content, doc_type)
        
        # Ensure output directory exists
        output_path = str(Path(output_path).absolute())
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save document
        doc.save(output_path)
        return output_path
    
    def _add_cover_page(self, doc: Document, title: str, doc_type: str, author: str) -> None:
        """Add a cover page to the document."""
        # Title
        cover = doc.add_paragraph()
        cover.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = cover.add_run(f"{doc_type}: {title}")
        run.font.name = "Calibri"
        run.font.size = Pt(26)
        run.bold = True
        run.font.color.rgb = RGBColor(0, 51, 153)
        
        # Metadata
        doc.add_paragraph("")
        meta = doc.add_paragraph()
        meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
        meta.add_run(f"Author: {author}").italic = True
        meta.add_run(f"    •    Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}").italic = True
        doc.add_page_break()
    
    def _add_content(self, doc: Document, content: Dict[str, Any], doc_type: str) -> None:

        if 'content' in content and isinstance(content['content'], str):
            # Simple text content
            self._add_text_content(doc, content['content'], doc_type)
        elif 'sections' in content and isinstance(content['sections'], dict):
            # Structured content with sections
            for section_title, section_text in content['sections'].items():
                doc.add_heading(section_title, level=1)
                doc.add_paragraph(section_text)
    
    def _add_text_content(self, doc: Document, text: str, doc_type: str) -> None:
        """Add plain text content with basic formatting."""
        from ..document_system import document_system
        
        # Get document type headings if available
        headings = document_system.get("DocumentTypes", {}).get(doc_type, [])
        
        # Process each line
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check for headings
            if ":" in line:
                potential_heading = line.split(":")[0].strip()
                if potential_heading in headings:
                    doc.add_heading(potential_heading, level=1)
                    content = line[len(potential_heading) + 1:].strip()
                    if content:
                        para = doc.add_paragraph(content)
                        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    continue
            
            # Regular paragraph
            para = doc.add_paragraph(line)
            para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
