import requests
import re
from typing import List, Dict, Any

SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
SEMANTIC_SCHOLAR_AUTHOR_URL = "https://api.semanticscholar.org/graph/v1/author/search"

def semantic_scholar_search(topic: str, limit: int = 5) -> List[Dict[str, Any]]:
    out = []
    try:
        params = {"query": topic, "limit": limit, "fields": "title,year,authors,abstract,url,externalIds"}
        r = requests.get(SEMANTIC_SCHOLAR_URL, params=params, timeout=20)
        r.raise_for_status()
        for d in r.json().get("data", []):
            out.append({
                "source": "Semantic Scholar",
                "title": d.get("title"),
                "year": d.get("year"),
                "authors": [a.get("name") for a in d.get("authors", [])],
                "abstract": d.get("abstract"),
                "url": d.get("url"),
                "doi": (d.get("externalIds") or {}).get("DOI"),
                "pdf_url": None
            })
    except Exception as e:
        print("Semantic Scholar error:", e)
    return out

def semantic_scholar_author_search(topic: str, limit: int = 5) -> List[Dict[str, Any]]:
    out = []
    try:
        params = {"query": topic, "limit": limit, "fields": "name,affiliations,homepage,url,paperCount,citationCount,hIndex"}
        r = requests.get(SEMANTIC_SCHOLAR_AUTHOR_URL, params=params, timeout=20)
        r.raise_for_status()
        for d in r.json().get("data", []):
            out.append({
                "name": d.get("name"),
                "affiliations": d.get("affiliations"),
                "homepage": d.get("homepage"),
                "url": d.get("url"),
                "paperCount": d.get("paperCount"),
                "citationCount": d.get("citationCount"),
                "hIndex": d.get("hIndex")
            })
    except Exception as e:
        print("Semantic Scholar author search error:", e)
    return out

def arxiv_search(topic: str, limit: int = 5) -> List[Dict[str, Any]]:
    out = []
    try:
        url = f"http://export.arxiv.org/api/query?search_query=all:{requests.utils.quote(topic)}&start=0&max_results={limit}"
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        entries = re.split(r'<entry>|</entry>', r.text)
        for ent in entries:
            if "<title>" in ent:
                title = re.search(r'<title>(.*?)</title>', ent, re.S)
                pdf = re.search(r'href="(http[s]?://arxiv.org/pdf/[^"]+)"', ent)
                summary = re.search(r'<summary>(.*?)</summary>', ent, re.S)
                out.append({
                    "source": "arXiv",
                    "title": title.group(1).strip() if title else None,
                    "year": None,
                    "authors": [],
                    "abstract": summary.group(1).strip() if summary else None,
                    "url": None,
                    "doi": None,
                    "pdf_url": pdf.group(1) if pdf else None
                })
    except Exception as e:
        print("arXiv error:", e)
    return out

def openalex_search(topic: str, limit: int = 5) -> List[Dict[str, Any]]:
    out = []
    try:
        url = f"https://api.openalex.org/works?filter=title.search:{requests.utils.quote(topic)}&per-page={limit}"
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        for w in r.json().get("results", [])[:limit]:
            out.append({
                "source": "OpenAlex",
                "title": w.get("title"),
                "year": w.get("publication_year"),
                "authors": [auth.get("author", {}).get("display_name") for auth in w.get("authorships", [])],
                "abstract": None,
                "url": w.get("id"),
                "doi": w.get("doi"),
                "pdf_url": None
            })
    except Exception as e:
        print("OpenAlex error:", e)
    return out
