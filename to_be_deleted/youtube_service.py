#services/youtube_service.py
from .base_manager import BaseAPIManager
from sources.video_transcript import YouTubeTranscriptFetcher, YouTubeTranscriptManager
from fastapi import Form 
from services.types import DocumentTypeEnum
from fastapi.responses import JSONResponse

class YouTubeClass(BaseAPIManager):
    async def process_youtube(self, query: str, doc_type: DocumentTypeEnum = Form(...), pages: int = 2):
        try:
            text = YouTubeTranscriptManager().get_transcripts_from_search(query)
            self.retriever.process_text(
                text,
                metadata={"source": "video", "query": query, "doc_type": doc_type.value}
            )
            summary = self.summarizer.summarize_with_structure(self.retriever, text, doc_type.value, pages)
            filename = self.save_docx(summary, "youtube", doc_type.value)
            return {"raw_text": text, "summary": summary, "download_link": f"/download/{filename}"}
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})
