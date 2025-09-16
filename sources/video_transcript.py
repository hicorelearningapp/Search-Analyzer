# sources/video_transcript.py
import re
from datetime import datetime
from typing import Optional, Dict, List
from ddgs import DDGS
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, NoTranscriptAvailable
from .retriever import VectorRetriever

class YouTubeSearcher:
    def __init__(self, max_results: int = 10):
        self.max_results = max_results

    def search(self, query: str) -> Dict:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(f"site:youtube.com {query}", max_results=self.max_results):
                href = r.get("href") or ""
                if "youtube.com/watch" not in href and "youtu.be/" not in href:
                    continue
                results.append({"title": r.get("title", ""), "href": href})
        return {"query": query, "timestamp": datetime.utcnow().isoformat() + "Z", "results": results}

class TranscriptFetcher:
    @staticmethod
    def get_video_id(url: str) -> Optional[str]:
        from urllib.parse import urlparse, parse_qs
        try:
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            if "v" in qs:
                return qs["v"][0]
            if parsed.netloc and parsed.netloc.endswith("youtu.be"):
                return parsed.path.lstrip("/")
            m = re.search(r"([0-9A-Za-z_-]{11})", url)
            return m.group(1) if m else None
        except Exception:
            return None

    @staticmethod
    def fetch_transcript(video_id: str, languages: Optional[List[str]] = None) -> str:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages or ["en"])
            return " ".join([t.get("text", "") for t in transcript])
        except (TranscriptsDisabled, NoTranscriptFound, NoTranscriptAvailable) as e:
            return f"Transcript not available: {e}"
        except Exception as e:
            return f"Transcript error: {e}"

class YouTubeTranscriptManager:
    def __init__(self, max_results: int = 10, chunk_size: int = 500, retriever: Optional[VectorRetriever] = None):
        self.searcher = YouTubeSearcher(max_results=max_results)
        self.fetcher = TranscriptFetcher()
        self.chunk_size = chunk_size
        self.retriever = retriever or VectorRetriever()

    def get_transcripts_from_search(self, query: str) -> str:
        search_out = self.searcher.search(query)
        combined = []
        for r in search_out["results"]:
            vid = self.fetcher.get_video_id(r["href"])
            if not vid:
                continue
            text = self.fetcher.fetch_transcript(vid)
            combined.append(f"[{r['title']} - {r['href']}]\n{text}\n")
        all_text = "\n".join(combined)
        if all_text.strip():
            self.retriever.build_index(all_text, chunk_size=self.chunk_size)
        return all_text
