#services/youtube_service.py
from .base_manager import BaseAPIManager
from sources.video_transcript import YouTubeTranscriptFetcher
from fastapi import Form 
from services.types import DocumentTypeEnum

class YouTubeClass(BaseAPIManager):
    async def process_youtube(self, url: str, doc_type: DocumentTypeEnum = Form(...), pages: int = 2):
        try:
            text = YouTubeTranscriptFetcher().get_transcript_direct(url)
            self.retriever.process_text(
                text,
                metadata={"source": "video", "query": url, "doc_type": doc_type.value}
            )
            summary = self.summarizer.summarize_with_structure(self.retriever, text, doc_type.value, pages)
            filename = self.save_docx(summary, "youtube", doc_type.value)
            return {"raw_text": text, "summary": summary, "download_link": f"/download/{filename}"}
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})
