# sources/web_search.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, List
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urlparse

@dataclass
class WebSearchConfig:
    max_results: int = 5          # fewer is safer for demo
    max_snippet_length: int = 600

class WebSearchManager:
    def __init__(self, max_results: int = 10, max_snippet_length: int = 600):
        self.max_results = max_results
        self.max_snippet_length = max_snippet_length

    def extract_page_content(self, url: str) -> str:
        """Extract main content from a webpage"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
                element.decompose()
            
            # Try to extract main content
            content_selectors = [
                'article',
                'main',
                '.content',
                '.main-content',
                '#content',
                '.post-content',
                '.entry-content',
                '.article-content',
                '.story-content',
                '.text-content',
                '#main-content',
                '.body-content'
            ]
            
            content = None
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text()
                    break
            
            if not content:
                # Fallback: get all paragraphs
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text() for p in paragraphs if len(p.get_text()) > 50])
            
            if not content or len(content.strip()) < 100:
                content = soup.body.get_text() if soup.body else soup.get_text()
            
            # Clean up the text
            content = re.sub(r'\s+', ' ', content)
            content = re.sub(r'\[.*?\]', '', content)  # Remove citations
            content = content.strip()
            
            return content[:10000] + '...' if len(content) > 10000 else content
            
        except Exception as e:
            return f"Error extracting content: {str(e)}"

    def run(self, query: str) -> str:
        """Perform search and return formatted results with full content"""
        results = []
        try:
            with DDGS() as ddgs:
                search_results = list(ddgs.text(query, max_results=self.max_results))
                
                for i, r in enumerate(search_results):
                    if i >= self.max_results:
                        break
                    
                    # Extract full page content instead of just using snippet
                    full_content = self.extract_page_content(r.get("href", ""))
                    time.sleep(1)  # Respectful delay between requests
                    
                    results.append({
                        "rank": i + 1,
                        "title": r.get("title", ""),
                        "href": r.get("href", ""),
                        "body": full_content  # Using full extracted content
                    })
                    
        except Exception as e:
            # Return error message in the same format
            return f"Search query: {query}\nError: {str(e)}\nFetched at (UTC): {datetime.utcnow().isoformat()}"
        
        # Format the output exactly as before but with full content
        lines = [
            f"Search query: {query}",
            f"Fetched at (UTC): {datetime.utcnow().isoformat()}",
            "",
            "Top search results:",
            ""
        ]
        
        for r in results:
            # Use the full content but truncate for display if needed
            content = r["body"]
            if len(content) > self.max_snippet_length:
                display_content = content[:self.max_snippet_length] + "..."
            else:
                display_content = content
            
            lines.append(f"{r['rank']}. {r['title']} ({r['href']})")
            lines.append(f"Content: {display_content}")
            lines.append("")
        
        return "\n".join(lines)
