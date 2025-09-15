# sources/video_transcript.py
import re
from datetime import datetime
from typing import Optional
from ddgs import DDGS
from youtube_transcript_api import YouTubeTranscriptApi
from .retriever import VectorRetriever


class YouTubeSearcher:
    """Handles searching YouTube videos via DuckDuckGo."""

    def __init__(self, max_results: int = 10):
        self.max_results = max_results

    def search(self, query: str) -> dict:
        results = []
        with DDGS() as ddgs:
            search_results = list(ddgs.text(f"site:youtube.com {query}", max_results=self.max_results))
            print(f"Search results: {search_results}")  # Debug log
            
            for i, r in enumerate(search_results):
                if not isinstance(r, dict):
                    print(f"Unexpected result type: {type(r)}, value: {r}")
                    continue
                    
                href = r.get("href", "") or r.get("url", "")
                if not href or "youtube.com/watch" not in href:
                    continue
                    
                results.append({
                    "rank": i + 1,
                    "title": r.get("title", ""),
                    "href": href
                })

        return {
            "query": query,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "results": results
        }


class TranscriptFetcher:
    """Handles fetching transcripts from YouTube."""

    def __init__(self):
        self.api = YouTubeTranscriptApi()

    @staticmethod
    def get_video_id(url: str) -> Optional[str]:
        regex = r"(?:v=\/|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(regex, url)
        return match.group(1) if match else None

    @staticmethod
    def fetch_transcript(video_id: str) -> str:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([snippet["text"] for snippet in transcript])
        except Exception as e:
            return f"Transcript not available: {e}"


class YouTubeTranscriptManager:
    """Coordinates searching, transcript fetching, and indexing."""

    def __init__(self, max_results: int = 10, chunk_size: int = 500, retriever: Optional[VectorRetriever] = None):
        self.searcher = YouTubeSearcher(max_results=max_results)
        self.fetcher = TranscriptFetcher()
        self.chunk_size = chunk_size
        self.retriever = retriever or VectorRetriever()

    def get_transcripts_from_search(self, query: str) -> str:
        try:
            print(f"Starting search for query: {query}")
            search_out = self.searcher.search(query)
            print(f"Search completed. Found {len(search_out.get('results', []))} results")
            
            if not search_out or not isinstance(search_out.get('results'), list):
                print(f"Unexpected search results format: {search_out}")
                return "No results found or invalid response from search"
                
            combined = []
            for i, r in enumerate(search_out["results"]):
                try:
                    print(f"Processing result {i+1}: {r.get('title', 'No title')}")
                    if not isinstance(r, dict) or 'href' not in r:
                        print(f"Skipping invalid result format: {r}")
                        continue
                        
                    video_id = self.fetcher.get_video_id(r["href"])
                    if not video_id:
                        print(f"Could not extract video ID from: {r['href']}")
                        continue

                    print(f"Fetching transcript for video ID: {video_id}")
                    transcript_text = self.fetcher.fetch_transcript(video_id)
                    combined.append(f"[{r.get('title', 'No title')} - {r['href']}]\n{transcript_text}\n")
                except Exception as e:
                    print(f"Error processing result {i+1}: {str(e)}")
                    continue

            if not combined:
                return "No valid transcripts could be retrieved"
                
            all_text = "\n".join(combined)
            print(f"Successfully retrieved {len(combined)} transcripts")

            # Build YouTube index
            self.retriever.build_index(all_text, "video", chunk_size=self.chunk_size)
            return all_text
            
        except Exception as e:
            print(f"Error in get_transcripts_from_search: {str(e)}")
            raise
