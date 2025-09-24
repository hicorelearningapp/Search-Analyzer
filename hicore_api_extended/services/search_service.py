from typing import List, Dict, Any, Optional
import requests
from ..utils.search_utils import (
    semantic_scholar_search,
    arxiv_search,
    openalex_search,
    semantic_scholar_author_search
)

async def search_multiple_sources(query: str,sources: List[str],limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search for papers across multiple academic sources.
    """
    results = []
    
    if 'semantic' in sources:
        results.extend(await semantic_scholar_search(query, limit))
    if 'arxiv' in sources:
        results.extend(await arxiv_search(query, limit))
    if 'openalex' in sources:
        results.extend(await openalex_search(query, limit))
    
    return results

async def find_top_researchers(query: str,limit: int = 5) -> List[Dict[str, Any]]:
    return await semantic_scholar_author_search(query, limit)

async def select_papers(indices: List[int],search_results: List[Dict[str, Any]],session: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Select papers from search results."""
    selected = []
    for idx in indices:
        if 0 <= idx < len(search_results):
            selected.append(search_results[idx])
    
    if session is not None:
        session["selected_papers"] = selected
    
    return selected
