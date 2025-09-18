# sources/web_search.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, List
from duckduckgo_search import DDGS
import requests
import trafilatura


@dataclass
class WebSearchConfig:
    max_results: int = 5          # fewer is safer for demo
    max_snippet_length: int = 600
    fetch_full_text: bool = True  # toggle full page fetching


class WebSearchManager:
    def __init__(self, max_results: int = 5, max_snippet_length: int = 600, fetch_full_text: bool = True):
        self.max_results = max_results
        self.max_snippet_length = max_snippet_length
        self.fetch_full_text = fetch_full_text

    def fetch_page_text(self, url: str) -> Optional[str]:
        """Download and clean article text using trafilatura."""
        try:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                return None
            downloaded = trafilatura.extract(resp.text, include_comments=False, include_tables=False)
            return downloaded
        except Exception:
            return None

    def run(self, query: str) -> str:
        """Perform DDG search, fetch pages, and return a long text string."""
        results: List[Dict] = []
        full_texts: List[str] = []

        with DDGS() as ddgs:
            for i, r in enumerate(ddgs.text(query, max_results=self.max_results)):
                if i >= self.max_results:
                    break
                results.append({
                    "rank": i + 1,
                    "title": r.get("title", ""),
                    "href": r.get("href", ""),
                    "body": r.get("body", "")
                })

                # Try to fetch article text if enabled
                if self.fetch_full_text and r.get("href"):
                    page_text = self.fetch_page_text(r["href"])
                    if page_text:
                        full_texts.append(f"Source: {r['title']} ({r['href']})\n{page_text}")

        # Fallback: if no full texts, use snippets
        if not full_texts:
            for r in results:
                snippet = (r["body"] or "").strip()
                if len(snippet) > self.max_snippet_length:
                    snippet = snippet[:self.max_snippet_length] + "..."
                full_texts.append(f"{r['title']} ({r['href']})\nSnippet: {snippet}")

        lines = [
            f"Search query: {query}",
            f"Fetched at (UTC): {datetime.utcnow().isoformat()}",
            "",
            "Combined web content:",
            ""
        ]
        return "\n\n".join(lines + full_texts)
