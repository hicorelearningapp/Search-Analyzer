from enum import Enum
from document_system import document_system

# Create DocumentTypeEnum that can be used across the application
DocumentTypeEnum = Enum(
    "DocumentTypeEnum",
    {t.replace(" ", "_"): t for t in document_system.list_document_types()}
)

def get_doc_type_str(doc_type) -> str:
    """Helper to safely get string value from either enum or string."""
    return doc_type.value if hasattr(doc_type, 'value') else str(doc_type)
