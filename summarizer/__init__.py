"""
Document summarization and processing functionality.

This package provides classes for document processing, summarization, and generation.
"""

from .document_processor import DocumentProcessor
from .llm_summarizer import LLMSummarizer
from .docx_generator import DocxGenerator

__all__ = ['DocumentProcessor', 'LLMSummarizer', 'DocxGenerator']
