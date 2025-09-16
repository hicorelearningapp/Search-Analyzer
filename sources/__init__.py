# sources/__init__.py

try:
    from .pdf_loader import PDFSummarizer
except ImportError:
    PDFSummarizer = None

try:
    from .video_transcript import YouTubeTranscriptManager
except ImportError:
    YouTubeTranscriptManager = None

try:
    from .web_search import WebSearchManager
except ImportError:
    WebSearchManager = None

__all__ = [
    "PDFSummarizer",
    "YouTubeTranscriptManager",
    "WebSearchManager"
]
