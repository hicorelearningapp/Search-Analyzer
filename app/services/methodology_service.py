# services/methodology_service.py
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

class MethodologyService:
    def __init__(self):
        """Initialize the MethodologyService."""
        pass

    async def extract_methodology_snippets(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract methodology snippets from a list of papers.
        
        Args:
            papers: List of paper dictionaries containing 'title' and 'text' or 'pdf_url'.
            
        Returns:
            Dictionary containing methodology snippets and analysis.
        """
        snippets = []
        steps = []
        
        for paper in papers:
            text = await self._get_paper_text(paper)
            snippet = self._extract_methodology_section(text)
            snippets.append({
                "title": paper.get("title", "Untitled"), 
                "snippet": snippet
            })
            steps.extend(re.split(r'(?<=[.!?])\s+', snippet)[:5])

        # Generate flowchart if graphviz is available
        flowchart_path = None
        if GRAPHVIZ_AVAILABLE and steps:
            flowchart_path = self._generate_flowchart(steps)

        return {
            "snippets": snippets,
            "flowchart_path": flowchart_path,
            "selected_papers": [s["title"] for s in snippets],
            "timestamp": datetime.datetime.now().isoformat()
        }

    async def compare_methodologies(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare methodologies across multiple papers.
        
        Args:
            papers: List of paper dictionaries to compare.
            
        Returns:
            Dictionary containing comparison results.
        """
        if len(papers) < 2:
            raise ValueError("At least 2 papers are required for comparison")

        # Extract methodologies from each paper
        comparisons = []
        for paper in papers:
            text = await self._get_paper_text(paper)
            methodology = self._extract_methodology_section(text)
            comparisons.append({
                "title": paper.get("title", "Untitled"),
                "methodology": methodology
            })

        # Generate comparison analysis
        comparison_analysis = await self._analyze_methodologies(comparisons)

        return {
            "comparison": comparison_analysis,
            "papers_compared": [c["title"] for c in comparisons],
            "timestamp": datetime.datetime.now().isoformat()
        }

    async def _get_paper_text(self, paper: Dict[str, Any]) -> str:
        """Extract text from a paper dictionary."""
        if paper.get("pdf_url"):
            return await download_pdf_to_text(paper["pdf_url"])
        return paper.get("text", paper.get("abstract", ""))

    def _extract_methodology_section(self, text: str) -> str:
        """Extract methodology section from text using regex."""
        if not text:
            return ""
        match = re.search(
            r'(?:Method(?:s|ology)| Materials and Methods)[\s\S]{0,2000}',
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
        """Generate a comparison analysis of methodologies using AI."""
        comparison_text = "\n\n".join(
            f"Paper: {c['title']}\nMethodology:\n{c['methodology']}" 
            for c in comparisons
        )
        
        prompt = (
            "Compare and contrast the methodologies used in these papers. "
            "Highlight similarity, differences, strengths, and weaknesses.\n\n"
            f"{comparison_text}\n\n"
            "Provide a detailed comparison in markdown format."
        )
        
        return await call_azure_chat(prompt, max_tokens=1000)

# Singleton instance for easy import
methodology_service = MethodologyService()