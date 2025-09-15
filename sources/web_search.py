# sources/web_search.py
from datetime import datetime
from ddgs import DDGS


class WebSearcher:
    """Handles performing a web search via DuckDuckGo."""

    def __init__(self, max_results: int = 10):
        self.max_results = max_results

    def search(self, query: str) -> dict:
        results = []
        with DDGS() as ddgs:
            for i, r in enumerate(ddgs.text(query, max_results=self.max_results)):
                results.append({
                    "rank": i + 1,
                    "title": r.get("title") or "",
                    "href": r.get("href") or "",
                    "body": r.get("body") or ""
                })
        return {
            "query": query,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "results": results
        }


class SearchResultFormatter:
    """Formats search output for use with an LLM."""

    def __init__(self, max_snippet_length: int = 600):
        self.max_snippet_length = max_snippet_length

    def assemble_for_llm(self, search_output: dict) -> str:
        lines = [
            f"Search query: {search_output['query']}",
            f"Fetched at (UTC): {search_output['timestamp']}",
            "",
            "Top search results:",
            ""
        ]
        for r in search_output["results"]:
            snippet = (r["body"] or "").strip()
            if len(snippet) > self.max_snippet_length:
                snippet = snippet[:self.max_snippet_length] + "..."
            lines.append(f"{r['rank']}. {r['title']} ({r['href']})")
            lines.append(f"Snippet: {snippet}")
            lines.append("")
        return "\n".join(lines)


class WebSearchManager:
    """Coordinates searching and formatting."""

    def __init__(self, max_results: int = 10, max_snippet_length: int = 600):
        self.searcher = WebSearcher(max_results=max_results)
        self.formatter = SearchResultFormatter(max_snippet_length=max_snippet_length)

    def run(self, query: str) -> str:
        search_output = self.searcher.search(query)
        return self.formatter.assemble_for_llm(search_output)
