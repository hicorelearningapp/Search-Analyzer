# services/methodology_service.py
from typing import List, Dict, Any, Optional
import re
import tempfile
import asyncio

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
    def __init__(self, app_state: Optional[AppState] = None):
        """Initialize with optional app state injection."""
        self.app_state = app_state or AppState()

    async def extract_methodology_snippets(
        self, 
        indices: Optional[List[int]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract methodology snippets from selected papers.
        
        Args:
            indices: List of paper indices to process
            session_id: Optional session ID for tracking
            
        Returns:
            Dictionary containing methodology snippets and analysis
        """
        # Initialize session if needed
        if session_id:
            session_data = self.app_state.get_user_state(session_id)
            if not session_data:
                raise ValueError("No session data found for the provided session ID")
        else:
            session_id = f"methodology_{int(datetime.now().timestamp())}"
            session_data = self.app_state.get_user_state(session_id)
            session_data.synthesis_storage.update({
                "created_at": datetime.now().isoformat(),
                "type": "methodology_extraction"
            })

        # Get selected indices if not provided
        if indices is None:
            indices = session_data.selected_indices or list(range(len(session_data.search_results)))

        snippets = []
        steps = []
        selected_papers = []
        
        # Process each selected paper
        for i in indices:
            if 0 <= i < len(session_data.search_results):
                p = session_data.search_results[i]
                text = await self._get_paper_text(p)
                snippet = self._extract_methodology_section(text)
                snippets.append({"title": p.get("title"), "snippet": snippet})
                steps.extend(re.split(r'(?<=[.!?])\s+', snippet)[:5])
                selected_papers.append(p)

        # Generate flowchart if graphviz is available
        flowchart_path = None
        if GRAPHVIZ_AVAILABLE and steps:
            flowchart_path = self._generate_flowchart(steps)

        # Store results in session
        result = {
            "session_id": session_id,
            "snippets": snippets,
            "flowchart_path": flowchart_path,
            "selected_papers": [p.get("title") for p in selected_papers],
            "timestamp": datetime.now().isoformat()
        }
        
        session_data.synthesis_storage["latest_methodology"] = result
        session_data.synthesis_storage["last_activity"] = datetime.now().isoformat()
        
        return result

    async def compare_methodologies(
        self,
        paper_indices: Optional[List[int]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare methodologies across multiple papers.
        
        Args:
            paper_indices: List of paper indices to compare
            session_id: Optional session ID for tracking
            
        Returns:
            Dictionary containing methodology comparison
        """
        # Initialize session if needed
        if session_id:
            session_data = self.app_state.get_user_state(session_id)
            if not session_data:
                raise ValueError("No session data found for the provided session ID")
        else:
            session_id = f"methodology_compare_{int(datetime.now().timestamp())}"
            session_data = self.app_state.get_user_state(session_id)
            session_data.synthesis_storage.update({
                "created_at": datetime.now().isoformat(),
                "type": "methodology_comparison"
            })

        # Get selected indices if not provided
        if paper_indices is None:
            paper_indices = session_data.selected_indices or list(range(len(session_data.search_results)))

        if len(paper_indices) < 2:
            raise ValueError("At least 2 papers are required for comparison")

        # Extract methodologies from each paper
        comparisons = []
        for i in paper_indices:
            if 0 <= i < len(session_data.search_results):
                paper = session_data.search_results[i]
                text = await self._get_paper_text(paper)
                methodology = self._extract_methodology_section(text)
                comparisons.append({
                    "title": paper.get("title"),
                    "methodology": methodology
                })

        # Generate comparison analysis
        comparison_analysis = await self._analyze_methodologies(comparisons)

        # Store results in session
        result = {
            "session_id": session_id,
            "comparison": comparison_analysis,
            "papers_compared": [c["title"] for c in comparisons],
            "timestamp": datetime.now().isoformat()
        }
        
        session_data.synthesis_storage["latest_comparison"] = result
        session_data.synthesis_storage["last_activity"] = datetime.now().isoformat()
        
        return result

    async def _get_paper_text(self, paper: Dict[str, Any]) -> str:
        """Extract text from paper, either from PDF or abstract."""
        if paper.get("pdf_url"):
            return await download_pdf_to_text(paper["pdf_url"])
        return paper.get("abstract", "")

    def _extract_methodology_section(self, text: str) -> str:
        """Extract methodology section from text."""
        if not text:
            return ""
        match = re.search(
            r'(?:Method(?:s|ology)|Materials and Methods)[\s\S]{0,2000}',
            text,
            flags=re.I
        )
        return match.group(0).strip() if match else text[:800]

    def _generate_flowchart(self, steps: List[str]) -> Optional[str]:
        """Generate a flowchart from methodology steps."""
        if not GRAPHVIZ_AVAILABLE or not steps:
            return None
            
        try:
            dot = Digraph(format="png")
            for i, step in enumerate(steps):
                dot.node(f"n{i}", step[:160])
                if i > 0:
                    dot.edge(f"n{i-1}", f"n{i}")
            tmpf = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            dot.render(tmpf.name, format="png", cleanup=True)
            return tmpf.name + ".png"
        except Exception:
            return None

    async def _analyze_methodologies(self, comparisons: List[Dict[str, str]]) -> str:
        """Generate analysis of methodology comparisons using LLM."""
        comparison_text = "\n\n".join(
            f"Paper: {c['title']}\nMethodology:\n{c['methodology']}"
            for c in comparisons
        )
        
        prompt = (
            "Compare and contrast the methodologies used in these papers. "
            "Highlight similarities, differences, strengths, and weaknesses:\n\n"
            f"{comparison_text}\n\n"
            "Provide a detailed comparison in markdown format."
        )
        
        return await call_azure_chat(prompt, max_tokens=1000)

# Singleton instance for easy import
methodology_service = MethodologyService()