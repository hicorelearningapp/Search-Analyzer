# sources/web_search.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
from duckduckgo_search import DDGS

@dataclass
class WebSearchConfig:
    max_results: int = 10
    max_snippet_length: int = 600

class WebSearchManager:
    def __init__(self, max_results: int = 10, max_snippet_length: int = 600):
        self.max_results = max_results
        self.max_snippet_length = max_snippet_length

    def run(self, query: str) -> str:
        # perform DDG search and assemble a prompt-friendly string
        results = []
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
        lines = [
            f"Search query: {query}",
            f"Fetched at (UTC): {datetime.utcnow().isoformat()}",
            "",
            "Top search results:",
            ""
        ]
        for r in results:
            snippet = (r["body"] or "").strip()
            if len(snippet) > self.max_snippet_length:
                snippet = snippet[:self.max_snippet_length] + "..."
            lines.append(f"{r['rank']}. {r['title']} ({r['href']})")
            lines.append(f"Snippet: {snippet}")
            lines.append("")
        return "\n".join(lines)
