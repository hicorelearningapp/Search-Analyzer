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
            "Business Report": DocumentType(
                name="Business Report",
                structure=["Executive Summary", "Market Analysis", "Opportunities", "Risks", "Recommendations"],
                description="Structured business report template"
            ),
            "Technical Whitepaper": DocumentType(
                name="Technical Whitepaper",
                structure=["Abstract", "Problem Statement", "Proposed Solution", "Architecture", "Future Work"],
                description="Technical whitepaper template for in-depth technical documentation"
            ),
            "Presentation Outline": DocumentType(
                name="Presentation Outline",
                structure=["Title Slide", "Key Sections", "Conclusion Slide"],
                description="Basic structure for creating presentation outlines"
            ),
            "News Brief": DocumentType(
                name="News Brief",
                structure=["Headline", "Key Points", "Quick Analysis"],
                description="Concise news brief template"
            ),
            "Educational Lesson Plan": DocumentType(
                name="Educational Lesson Plan",
                structure=["Learning Objectives", "Content Outline", "Examples", "Exercises"],
                description="Structured template for educational content"
            ),
            "Case Study": DocumentType(
                name="Case Study",
                structure=["Background", "Problem", "Solution", "Outcome", "Lessons Learned"],
                description="Template for creating detailed case studies"
            ),
            "FAQ / Knowledge Base Article": DocumentType(
                name="FAQ / Knowledge Base Article",
                structure=["Question", "Answer"],
                description="Template for creating FAQ or knowledge base content"
            ),
            "Press Release": DocumentType(
                name="Press Release",
                structure=["Headline", "Lead Paragraph", "Supporting Details", "Quote", "Boilerplate"],
                description="Standard press release template"
            ),
            "LinkedIn Post / Social Content": DocumentType(
                name="LinkedIn Post / Social Content",
                structure=["Short Post", "Hashtags"],
                description="Template for social media content creation"
            ),
            "Policy Brief": DocumentType(
                name="Policy Brief",
                structure=["Issue", "Background", "Analysis", "Recommendation"],
                description="Template for policy-related documents"
            ),
            "Project Proposal": DocumentType(
                name="Project Proposal",
                structure=["Objective", "Deliverables", "Timeline", "Cost Estimate"],
                description="Template for project proposals"
            ),
            "Executive Summary": DocumentType(
                name="Executive Summary",
                structure=["Condensed Report"],
                description="Concise executive summary template"
            ),
            "Custom User-Defined Template": DocumentType(
                name="Custom User-Defined Template",
                structure=["User Defined Headings"],
                description="Custom template with user-defined structure"
            )
        }

    def get_document_type(self, key: str) -> Optional[DocumentType]:
        return self._types.get(key)

    def add_document_type(self, key: str, name: str, structure: List[str], description: str = ""):
        self._types[key] = DocumentType(name=name, structure=structure, description=description)

    def list_document_types(self) -> List[str]:
        return list(self._types.keys())

# exported instance
document_system = DocumentSystem()
