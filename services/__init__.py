# This file makes the directory a Python package
# It can be empty or contain package-level variables and imports

# Import all service classes to make them available at the package level
from .base_manager import BaseAPIManager
from .pdf_service import PDFClass
from .youtube_service import YouTubeClass
from .web_service import WebClass
from .text_service import TextClass

# Create a shared instance for the download endpoint
api_manager = BaseAPIManager()

__all__ = [
    'BaseAPIManager',
    'PDFClass',
    'YouTubeClass',
    'WebClass',
    'TextClass',
    'api_manager'
]
