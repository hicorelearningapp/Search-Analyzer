# hicore_api_extended.py
# -*- coding: utf-8 -*-
"""
HICORE Research API - Extended & cleaned for Colab or local testing
Features:
 - Session + intent selection (start_session)
 - Topic suggestion (suggest_topics)
 - Project start (project_start)
 - Proposal writer (proposal_writer)
 - Methodology search + flowchart (methodology_search)
 - Review paper scaffolding (review_paper)
 - Visualization map (visualize_map using pyvis)
 - Paper search (Semantic Scholar, arXiv, OpenAlex)
 - Structured summary generation & synthesis (with Azure OpenAI if configured)
 - Compare papers, clear state
 - New: Find top researchers
"""

import os
import io
import re
import json
import time
import tempfile
import requests
import traceback
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# ---------- Optional libraries ----------
try:
    import pdfplumber
except Exception:
    pdfplumber = None

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

try:
    import networkx as nx
    from pyvis.network import Network
except Exception:
    nx = None
    Network = None

try:
    from graphviz import Digraph
except Exception:
    Digraph = None

try:
    from openai import AzureOpenAI
except Exception:
    AzureOpenAI = None

try:
    from langdetect import DetectorFactory, detect
    DetectorFactory.seed = 0
except Exception:
    detect = None

# ---------- App setup ----------
app = FastAPI(title="HICORE Research API (Extended)", description="Extended research & document processing API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ---------- Configuration ----------
AZURE_CFG = {
    "api_key": os.getenv("AZURE_OPENAI_API_KEY", "G3AKaFyet7mSiT9cDWoxol7bpTfQ9U91IrWUiD1mvgNtNL37KNfEJQQJ99BHACHYHv6XJ3w3AAAAACOGaDFv"),
    "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", "https://hicor-megtc6ig-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2025-01-01-preview"),
    "api_version": "2025-01-01-preview",
    "deployment_name": "gpt-4"
}

SERPAPI_KEY = os.getenv("SERPAPI_KEY","90b40f0b46cad75f193c8fcce5798793c27f7b79d70e8b22c351bbcf1268e3b6")
SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
SEMANTIC_SCHOLAR_AUTHOR_URL = "https://api.semanticscholar.org/graph/v1/author/search"

# ---------- Global state ----------
SESSIONS: Dict[str, Dict[str, Any]] = {}
SEARCH_RESULTS: List[Dict[str, Any]] = []
SELECTED_IDX: List[int] = []
SYNTHESIS_STORAGE: Dict[str, str] = {}

# ---------- Utilities ----------
def _is_azure_configured() -> bool:
    return bool(AZURE_CFG.get("api_key") and AZURE_CFG.get("endpoint") and AZURE_CFG.get("deployment_name") and AzureOpenAI)

def init_azure_client():
    if not _is_azure_configured():
        return None
    try:
        return AzureOpenAI(
            api_key=AZURE_CFG["api_key"],
            azure_endpoint=AZURE_CFG["endpoint"],
            api_version=AZURE_CFG["api_version"],
        )
    except Exception as e:
        print("Azure client init failed:", e)
        return None

def call_azure_chat(prompt: str, max_tokens: int = 1000, temperature: float = 0.2) -> str:
    if _is_azure_configured():
        try:
            client = init_azure_client()
            response = client.chat.completions.create(
                model=AZURE_CFG["deployment_name"],
                messages=[
                    {"role": "system", "content": "You are a helpful academic assistant. Provide citations where appropriate."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            print("Azure call error:", e)
            traceback.print_exc()

    # fallback summarizer
    lines = [l.strip() for l in re.split(r'\n+', prompt) if l.strip()]
    summary = " ".join(lines[:6])
    if len(summary) > 200:
        summary = summary[:200] + "..."
    return f"(Fallback summary — Azure not configured)\n{summary}"

def parse_structured_sections(text: str) -> Dict[str, str]:
    """Parses a string with section headers into a dictionary."""
    sections = re.split(r'###\s*', text)
    result = {}
    for section in sections:
        if not section.strip():
            continue
        header, *content = section.split('###', 1)
        header = header.strip().replace(' ', '_').lower()
        result[header] = '###'.join(content).strip()
    return result

def safe_request_get(url, timeout=15, headers=None):
    try:
        return requests.get(url, timeout=timeout, headers=headers or {"User-Agent": "hicore-bot/1.0"})
    except Exception as e:
        print("HTTP GET failed:", url, e)
        return None

# ---------- Paper search utilities ----------
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

# ---------- PDF extraction ----------
def download_pdf_to_text(url: str) -> str:
    if not url:
        return ""
    try:
        r = safe_request_get(url, timeout=30)
        if not r or r.status_code != 200:
            return ""
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.write(r.content)
        tmp.flush()
        tmp_path = tmp.name
        tmp.close()

        text = ""
        if pdfplumber:
            try:
                with pdfplumber.open(tmp_path) as pdf:
                    for p in pdf.pages:
                        t = p.extract_text()
                        if t:
                            text += t + "\n"
            except Exception:
                pass

        if not text:
            try:
                import fitz
                with fitz.open(tmp_path) as doc:
                    for page in doc:
                        text += page.get_text()
            except Exception:
                pass

        os.unlink(tmp_path)
        return text or ""
    except Exception as e:
        print("download_pdf_to_text failed:", e)
        return ""

# ---------- Endpoints: sessions, workflow ----------
@app.post("/start_session")
async def start_session(intent: str = Form(...), user_id: str = Form("default")):
    """Initializes a new session based on the user's research intent."""
    session_id = f"{user_id}_{int(time.time())}"
    SESSIONS[session_id] = {"intent": intent.lower(), "created": time.time(), "context": {}}
    return {"session_id": session_id, "intent": intent, "message": f"Session created for {intent}"}

@app.post("/suggest_topics")
async def suggest_topics(keywords: str = Form(...), limit: int = Form(6), session_id: str = Form(None)):
    """Suggests research topics based on provided keywords."""
    words = [w.strip() for w in re.split(r'[,\n;]+', keywords) if w.strip()]
    base_templates = [
        "{kw}: a systematic review of techniques and gaps",
        "Novel approaches to {kw} in {kw2}",
        "Comparative study of algorithms for {kw}",
        "Application of {kw} to healthcare / industry",
        "Benchmarking {kw} datasets and metrics",
    ]
    candidates = []
    for i, w in enumerate(words):
        for t in base_templates:
            kw2 = words[(i+1) % len(words)] if len(words) > 1 else "related domains"
            candidates.append(t.format(kw=w, kw2=kw2))
            if len(candidates) >= limit:
                break
    resp = {"keywords": words, "suggested_topics": candidates[:limit]}
    return resp

@app.post("/project_start")
async def project_start(topic: str = Form(...), limit: int = Form(5)):
    """Starts a research project by providing initial papers on a topic."""
    results = []
    results.extend(semantic_scholar_search(topic, limit))
    results.extend(arxiv_search(topic, limit))
    results.extend(openalex_search(topic, limit))
    return {"topic": topic, "papers": results[:limit]}

@app.post("/top_researchers")
async def top_researchers(topic: str = Form(...), limit: int = Form(5)):
    """Finds top labs and scientists in a given research topic."""
    results = semantic_scholar_author_search(topic, limit)
    return {"topic": topic, "researchers": results}

# ---------- Paper search + selection ----------
@app.post("/search_papers")
async def search_papers_endpoint(topic: str = Form(...), sources: str = Form("Semantic Scholar,arXiv,OpenAlex"), limit: int = Form(6)):
    """Searches for papers based on keywords, topics, and sources."""
    global SEARCH_RESULTS
    results = []
    for s in [x.strip().lower() for x in sources.split(",")]:
        if "semantic" in s:
            results.extend(semantic_scholar_search(topic, limit))
        elif "arxiv" in s:
            results.extend(arxiv_search(topic, limit))
        elif "openalex" in s:
            results.extend(openalex_search(topic, limit))
    SEARCH_RESULTS = results[:limit]
    return {"count": len(SEARCH_RESULTS), "results": SEARCH_RESULTS}

@app.post("/select_papers")
async def select_papers_endpoint(indices_csv: str = Form(...)):
    """Selects papers from the search results for further analysis."""
    global SELECTED_IDX
    idx = [int(x.strip())-1 for x in indices_csv.split(",") if x.strip().isdigit()]
    SELECTED_IDX = [i for i in idx if 0 <= i < len(SEARCH_RESULTS)]
    return {"selected_indices": SELECTED_IDX}

@app.post("/generate_structured_summaries")
async def generate_structured_summaries_endpoint():
    """Generates structured summaries for the selected papers."""
    outputs = []
    for i in SELECTED_IDX:
        paper = SEARCH_RESULTS[i]
        full_text = paper.get("abstract", "")
        prompt = f"Extract structured summary from this abstract:\n{full_text}\n\nUse headers ### Abstract ### Methods ### Results ### Conclusion and include citations where possible."
        llm_output = call_azure_chat(prompt, max_tokens=1000)
        structured = parse_structured_sections(llm_output)
        structured["title"] = paper.get("title")
        outputs.append(structured)
    return {"structured_summaries": outputs}

# ---------- Endpoints: workflow continuation ----------
@app.post("/proposal_writer")
async def proposal_writer(title: str = Form(...), chosen_subtopics: str = Form(""), expected_methods: str = Form("")):
    """Writes a research proposal draft based on user inputs and suggested topics."""
    subs = [s.strip() for s in re.split(r'[,\n;]+', chosen_subtopics) if s.strip()]
    methods = [m.strip() for m in re.split(r'[,\n;]+', expected_methods) if m.strip()]
    if not _is_azure_configured():
        return {
            "title": title,
            "background_and_novelty": f"(Fallback) Background for {title}",
            "abstract": f"(Fallback) Abstract for {title}",
            "review_of_literature_outline": "Fallback outline",
            "research_questions": "1) Primary\n2) Secondary",
            "aim_scope": "1) Aim\n2) Aim",
            "methodology_skeleton": f"Fallback methods: {methods}",
            "workplan_timeline_example": "Month 1-2: Literature; 3-6: Data; 7-9: Analysis; 10-12: Writing"
        }
    
    # Generate content for each section using Azure OpenAI
    background_prompt = f"Write a background and novelty section for a research proposal titled '{title}'. Focus on the subtopics: {', '.join(subs)}."
    abstract_prompt = f"Write a concise abstract (around 150 words) for a research proposal titled '{title}' with a focus on {', '.join(subs)}."
    review_prompt = f"Create an outline for a literature review on the topic '{title}'. The outline should be based on the subtopics: {', '.join(subs)}."
    questions_prompt = f"List 3-5 key research questions for a study titled '{title}' on the topics of {', '.join(subs)}."
    aims_prompt = f"Define the overall aim and scope of a research project titled '{title}' focusing on {', '.join(subs)}."
    methodology_prompt = f"Describe the methodology section for a proposal on '{title}'. The expected methods include: {', '.join(methods)}. Provide a step-by-step skeleton."
    workplan_prompt = f"Create a sample workplan and timeline for a 12-month research project on '{title}'."

    return {
        "title": title,
        "background_and_novelty": call_azure_chat(background_prompt),
        "abstract": call_azure_chat(abstract_prompt, max_tokens=200),
        "review_of_literature_outline": call_azure_chat(review_prompt),
        "research_questions": call_azure_chat(questions_prompt, max_tokens=150),
        "aim_scope": call_azure_chat(aims_prompt, max_tokens=150),
        "methodology_skeleton": call_azure_chat(methodology_prompt),
        "workplan_timeline_example": call_azure_chat(workplan_prompt)
    }

@app.post("/methodology_search")
async def methodology_search(paper_indices: str = Form(...)):
    """Extracts methodology snippets and creates a flowchart from selected papers."""
    if not SEARCH_RESULTS:
        raise HTTPException(status_code=400, detail="No search results available. Run /search_papers first.")
    idxs = [int(x.strip())-1 for x in paper_indices.split(",") if x.strip().isdigit()]
    snippets, steps = [], []
    for i in idxs:
        if 0 <= i < len(SEARCH_RESULTS):
            p = SEARCH_RESULTS[i]
            text = download_pdf_to_text(p.get("pdf_url")) if p.get("pdf_url") else p.get("abstract", "")
            m = re.search(r'(?:Method(?:s|ology)|Materials and Methods)[\s\S]{0,2000}', text or "", flags=re.I)
            snippet = m.group(0).strip() if m else (text[:800] if text else "")
            snippets.append({"title": p.get("title"), "snippet": snippet})
            steps.extend(re.split(r'(?<=[.!?])\s+', snippet)[:5])
    flowchart_path = None
    if Digraph and steps:
        dot = Digraph(format="png")
        for i, step in enumerate(steps):
            dot.node(f"n{i}", step[:160])
            if i > 0:
                dot.edge(f"n{i-1}", f"n{i}")
        tmpf = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        dot.render(tmpf.name, format="png", cleanup=True)
        flowchart_path = tmpf.name + ".png"
    return {"methodology_snippets": snippets, "flowchart_image": flowchart_path}

@app.post("/compare_methodologies")
async def compare_methodologies_endpoint():
    """Compares the methodology sections of the selected papers."""
    if len(SELECTED_IDX) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 papers selected to compare methodologies.")
    
    subset = [SEARCH_RESULTS[i] for i in SELECTED_IDX]
    combined = "\n\n".join([f"Title: {p.get('title')}\nAbstract: {p.get('abstract')}" for p in subset])
    prompt = f"Compare the methodologies of these papers. Focus on research design, sample size, and key steps. Include citations.\n{combined}"
    comparison = call_azure_chat(prompt, max_tokens=900)
    return {"methodology_comparison": comparison}

@app.post("/review_paper")
async def review_paper(subtopics: str = Form(""), selected_indices: str = Form("")):
    """Scaffolds a review paper draft based on selected papers and subtopics."""
    subs = [s.strip() for s in re.split(r'[,\n;]+', subtopics) if s.strip()] or ["Background","Methods","Results"]
    idxs = [int(x.strip())-1 for x in selected_indices.split(",") if x.strip().isdigit()]
    selected = [SEARCH_RESULTS[i] for i in idxs if 0 <= i < len(SEARCH_RESULTS)]
    draft = {"subtopics": subs, "papers_considered": len(selected)}
    
    # Combine abstracts of selected papers to provide context for the AI model
    combined_abstracts = "\n\n".join([f"Title: {p.get('title')}\nAbstract: {p.get('abstract')}" for p in selected])
    
    # Generate introduction and conclusion using Azure OpenAI
    intro_prompt = f"Write an introduction for a review paper based on the following topics and papers:\n\nTopics: {', '.join(subs)}\n\nPapers:\n{combined_abstracts}"
    conclusion_prompt = f"Write a conclusion for a review paper based on the following topics and papers:\n\nTopics: {', '.join(subs)}\n\nPapers:\n{combined_abstracts}"
    
    draft["introduction"] = call_azure_chat(intro_prompt)
    draft["conclusion"] = call_azure_chat(conclusion_prompt)
    
    return draft

@app.post("/visualize_map")
async def visualize_map(seed_indices: str = Form(...)):
    """Creates a visualization map of related papers. Note: This is a simplified representation of a full bibliometric tool."""
    if not nx or not Network:
        raise HTTPException(status_code=500, detail="Visualization libraries (pyvis, networkx) are missing. Please install them.")
    try:
        idxs = [int(x.strip())-1 for x in seed_indices.split(",") if x.strip().isdigit()]
        seeds = [SEARCH_RESULTS[i] for i in idxs if 0 <= i < len(SEARCH_RESULTS)]
        
        G = nx.Graph()
        for i, p in enumerate(seeds):
            nid = f"seed_{i}"
            authors = p.get('authors')
            first_author = authors[0] if authors and len(authors) > 0 else 'N/A'
            node_title = f"{p.get('title') or f'paper_{i}'}\n({first_author} et al., {p.get('year', 'N/A')})\nSource: {p.get('source', 'N/A')}"
            G.add_node(nid, label=p.get("title") or f"paper_{i}", title=node_title)
            
            # Add some mock related nodes for visualization
            for j in range(2):
                rid = f"rel_{i}_{j}"
                G.add_node(rid, label=f"{p.get('title')} related {j+1}")
                G.add_edge(nid, rid)
                
        net = Network(height="750px", width="100%")
        net.from_nx(G)
        
        # Save the visualization to a temporary file
        tmpdir = tempfile.mkdtemp()
        out_file = os.path.join(tmpdir, "visual_map.html")
        net.save_graph(out_file)
        
        return FileResponse(out_file, media_type="text/html", filename="visual_map.html")
    except Exception as e:
        print(f"Error during visualization map generation: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate visualization: {e}")
@app.post("/generate_overall_synthesis")
async def generate_overall_synthesis():
    """Synthesizes a general summary from all selected papers."""
    combined_text = ""
    for i in SELECTED_IDX:
        paper = SEARCH_RESULTS[i]
        combined_text += f"Title: {paper.get('title')}\nAbstract: {paper.get('abstract')}\n\n"
    prompt = f"Synthesize across these papers, providing an overall summary and including citations.\n{combined_text}"
    overall = call_azure_chat(prompt, max_tokens=1500)
    SYNTHESIS_STORAGE["latest"] = overall
    return {"synthesis": overall}

@app.get("/download_synthesis")
async def download_synthesis():
    """Downloads the most recent synthesis as a text file."""
    if "latest" not in SYNTHESIS_STORAGE:
        raise HTTPException(status_code=400, detail="No synthesis available")
    content = SYNTHESIS_STORAGE["latest"]
    return StreamingResponse(io.BytesIO(content.encode("utf-8")), media_type="text/plain",
                             headers={"Content-Disposition": "attachment; filename=synthesis.txt"})

@app.get("/compare_papers")
async def compare_selected_papers_endpoint():
    """Compares the abstracts of the selected papers."""
    if len(SELECTED_IDX) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 papers selected")
    subset = [SEARCH_RESULTS[i] for i in SELECTED_IDX]
    combined = "\n\n".join([f"Title: {p.get('title')}\nAbstract: {p.get('abstract')}" for p in subset])
    prompt = f"Compare these papers, highlighting their similarities and differences. Include citations.\n{combined}"
    comparison = call_azure_chat(prompt, max_tokens=900)
    return {"comparison": comparison}

@app.post("/clear_state")
async def clear_state_endpoint():
    """Resets all global variables and clears the session state."""
    global SEARCH_RESULTS, SELECTED_IDX, SYNTHESIS_STORAGE, SESSIONS
    SEARCH_RESULTS, SELECTED_IDX, SYNTHESIS_STORAGE, SESSIONS = [], [], {}, {}
    return {"message": "State cleared"}

# ---------- Entry ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
