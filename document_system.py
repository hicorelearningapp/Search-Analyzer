# document_system.py
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class DocumentType:
    name: str
    structure: List[str]
    description: str = ""

class DocumentSystem:
    def __init__(self):
        self._types: Dict[str, DocumentType] = {
            "Research Paper Summary": DocumentType(
                name="Research Paper Summary",
                structure=["Abstract", "Introduction", "Methodology", "Results", "Conclusion"],
                description="Academic research paper summary template"
            ),
            "Blog Post": DocumentType(
                name="Blog Post",
                structure=["Title", "Hook", "Body", "Conclusion", "Call-to-Action"],
                description="Short blog post template"
            ),
            "Executive Summary": DocumentType(
                name="Executive Summary",
                structure=["Executive Summary"],
                description="Short executive summary"
            ),
        }

    def get_document_type(self, key: str) -> Optional[DocumentType]:
        return self._types.get(key)

    def add_document_type(self, key: str, name: str, structure: List[str], description: str = ""):
        self._types[key] = DocumentType(name=name, structure=structure, description=description)

    def list_document_types(self) -> List[str]:
        return list(self._types.keys())

# exported instance
document_system = DocumentSystem()
