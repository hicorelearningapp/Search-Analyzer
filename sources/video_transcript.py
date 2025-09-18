# sources/video_transcript.py
import re
from datetime import datetime
from ddgs import DDGS
from youtube_transcript_api import YouTubeTranscriptApi


class YouTubeSearch:
    """Handles searching for YouTube videos using DuckDuckGo."""

    def __init__(self, max_results: int = 10):
        self.max_results = max_results

    def search(self, query: str) -> list[dict]:
        results = []
        with DDGS() as ddgs:
            for i, r in enumerate(ddgs.text(f"site:youtube.com {query}", max_results=self.max_results)):
                href = r.get("href") or ""
                if "youtube.com/watch" not in href:
                    continue
                results.append({
                    "rank": i + 1,
                    "title": r.get("title") or "",
                    "href": href
                })
        return results


# class YouTubeTranscriptFetcher:
#     """Handles extracting transcript text from a single YouTube video."""

#     @staticmethod
#     def extract_video_id(url: str) -> str | None:
#         regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
#         match = re.search(regex, url)
#         return match.group(1) if match else None

#     def fetch_transcript(self, url: str) -> str:
#         video_id = self.extract_video_id(url)
#         if not video_id:
#             return ""
#         try:
#             transcript = YouTubeTranscriptApi.get_transcript(video_id)
#             return " ".join([snippet["text"] for snippet in transcript])
#         except Exception:
#             return ""

class YouTubeTranscriptFetcher:
    """Handles extracting transcript text from a single YouTube video."""

    @staticmethod
    def extract_video_id(url: str) -> str | None:
        regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(regex, url)
        return match.group(1) if match else None

    def fetch_transcript(self, url: str) -> str:
        video_id = self.extract_video_id(url)
        if not video_id:
            return ""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = None
            if "en" in [t.language_code for t in transcript_list]:
                transcript = transcript_list.find_transcript(["en"])
                self.last_lang_used = "en"
            else:
                transcript = next(iter(transcript_list), None)
                self.last_lang_used = getattr(transcript, "language_code", "unknown")
            if not transcript:
                return ""
            fetched = transcript.fetch()
            return " ".join([snippet["text"] for snippet in fetched if snippet["text"].strip()])
        except Exception:
            self.last_lang_used = "unknown"
            return ""
            

class YouTubeTranscriptManager:
    """Coordinates search and transcript fetching, outputs plain text only."""

    def __init__(self, max_results: int = 5):
        self.searcher = YouTubeSearch(max_results=max_results)
        self.fetcher = YouTubeTranscriptFetcher()

    def get_transcripts_from_search(self, query: str) -> str:
        results = self.searcher.search(query)
        transcripts = []

        for r in results:
            text = self.fetcher.fetch_transcript(r["href"])
            if text:
                transcripts.append(text)

        # Pure transcript text only, joined with spacing
        return "\n\n".join(transcripts)


