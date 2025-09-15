# api.py
import os
from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse

from sources.web_search import WebSearchManager
from sources.pdf_loader import PDFSummarizer  
from sources.video_transcript import YouTubeTranscriptManager
from summarizer.common import SummarizerPipeline

app = APIRouter()

# Initialize services
pdf_summarizer = PDFSummarizer()
youtube_manager = YouTubeTranscriptManager(max_results=10)
web_search_manager = WebSearchManager(max_results=10, max_snippet_length=600)
summarizer_pipeline = SummarizerPipeline()

@app.get("/web")
def summarize_web(topic: str, doc_type: str, pages: int = 2, download: bool = False):
    try:
        llm_input = web_search_manager.run(topic)
        return summarizer_pipeline.run(
            text=llm_input,
            doc_type=doc_type,
            pages=pages,
            label=topic,
            outfile_name=topic,
            download=download
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/pdf")
async def summarize_pdf_route(file: UploadFile, doc_type: str = Form(...), pages: int = Form(2), download: bool = Form(False)):
    try:
        return await pdf_summarizer.summarize_pdf(file, doc_type, pages, download)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/youtube")
def summarize_youtube(query: str = Form(...), doc_type: str = Form(...), pages: int = Form(2), download: bool = Form(False)):
    try:
        text = youtube_manager.get_transcripts_from_search(query)
        return summarizer_pipeline.run(
            text=text,
            doc_type=doc_type,
            pages=pages,
            label="YouTube Videos",
            outfile_name="youtube",
            download=download
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/text")
def summarize_text(content: str = Form(...), doc_type: str = Form(...), pages: int = Form(2), download: bool = Form(False)):
    try:
        return summarizer_pipeline.run(
            text=content,
            doc_type=doc_type,
            pages=pages,
            label="User Text",
            outfile_name="text",
            download=download
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
