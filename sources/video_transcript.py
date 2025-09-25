# sources/video_transcript.py
import re
from datetime import datetime
from duckduckgo_search import DDGS
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


class YouTubeTranscriptFetcher:

    def get_video_id(self, url: str) -> str:
        """
        Extracts the video ID from a YouTube URL.
        """
        regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(regex, url)
        if match:
            return match.group(1)
        else:
            raise ValueError("Invalid YouTube URL")

    def get_transcript_direct(self, url: str) -> str:

        video_id = self.get_video_id(url)
        try:
            transcript_api = YouTubeTranscriptApi()
            result = transcript_api.fetch(video_id)
            
            # Let's inspect the object structure
            print(f"Object type: {type(result)}")
            print(f"Object attributes: {[attr for attr in dir(result) if not attr.startswith('_')]}")
            
            # Try to access the transcript data
            if hasattr(result, '_transcript_data'):
                transcript_data = result._transcript_data
                if isinstance(transcript_data, list):
                    return " ".join([entry.get('text', '') for entry in transcript_data])
            
            # If that doesn't work, try to convert to string and parse
            result_str = str(result)
            if 'FetchedTranscriptSnippet(text=' in result_str:
                # Extract text parts using regex
                text_matches = re.findall(r"text='(.*?)'", result_str)
                return " ".join(text_matches)
            
            return result_str
                
        except Exception as e:
            return f"Error: {e}"
            

class YouTubeTranscriptManager:
    """Coordinates search and transcript fetching, outputs plain text only."""

    def __init__(self, max_results: int = 5):
        self.searcher = YouTubeSearch(max_results=max_results)
        self.fetcher = YouTubeTranscriptFetcher()

    def get_transcripts_from_search(self, query: str) -> str:
        results = self.searcher.search(query)
        transcripts = []

        for r in results:
            text = self.fetcher.get_transcript_direct(r["href"])
            if text:
                transcripts.append(text)

        # Pure transcript text only, joined with spacing
        return "\n\n".join(transcripts)
