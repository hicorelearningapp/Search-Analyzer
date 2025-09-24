from typing import List, Dict, Any, Optional
import re
import tempfile

# Import graphviz only if available
try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    Digraph = None
    GRAPHVIZ_AVAILABLE = False

from utils.azure_client import call_azure_chat
from utils.pdf_utils import download_pdf_to_text
from app_state import AppState

class MethodologyService:
    @classmethod
    async def extract_methodology_snippets(
        cls, 
        app_state: AppState, 
        indices: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        snippets = []
        steps = []
        
        if indices is None:
            indices = app_state.state.selected_indices
        
        for i in indices:
            if 0 <= i < len(app_state.state.search_results):
                p = app_state.state.search_results[i]
                text = download_pdf_to_text(p.get("pdf_url")) if p.get("pdf_url") else p.get("abstract", "")
                m = re.search(r'(?:Method(?:s|ology)|Materials and Methods)[\s\S]{0,2000}', text or "", flags=re.I)
                snippet = m.group(0).strip() if m else (text[:800] if text else "")
                snippets.append({"title": p.get("title"), "snippet": snippet})
                steps.extend(re.split(r'(?<=[.!?])\s+', snippet)[:5])
        
        flowchart_path = None
        if GRAPHVIZ_AVAILABLE and steps:
            try:
                dot = Digraph(format="png")
                for i, step in enumerate(steps):
                    dot.node(f"n{i}", step[:160])
                    if i > 0:
                        dot.edge(f"n{i-1}", f"n{i}")
                tmpf = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                dot.render(tmpf.name, format="png", cleanup=True)
                flowchart_path = tmpf.name + ".png"
            except Exception as e:
                print(f"Error generating flowchart: {e}")
        
        return {"methodology_snippets": snippets, "flowchart_image": flowchart_path}

    @staticmethod
    def compare_selected_methodologies(app_state: AppState, selected_indices: Optional[List[int]] = None) -> str:
        if selected_indices is None:
            selected_indices = app_state.state.selected_indices
            
        if len(selected_indices) < 2:
            raise ValueError("Need at least 2 papers selected to compare methodologies.")
            
        subset = [app_state.state.search_results[i] for i in selected_indices 
                 if 0 <= i < len(app_state.state.search_results)]
        
        combined = "\n\n".join([f"Title: {p.get('title')}\nAbstract: {p.get('abstract')}" for p in subset])
        prompt = f"Compare the methodologies of these papers. Focus on research design, sample size, and key steps. Include citations.\n{combined}"
        
        # Note: This assumes call_azure_chat is synchronous. If it's async, you'll need to await it.
        return call_azure_chat(prompt, max_tokens=900)
