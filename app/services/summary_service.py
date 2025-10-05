from typing import List, Dict, Any
from datetime import datetime
from utils.parsing import parse_structured_sections
from utils.azure_client import call_azure_chat

class SummaryService:
    def __init__(self):
        """Initialize the SummaryService."""
        pass

    async def generate_structured_summaries(
        self,
        papers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate structured summaries for the provided papers.
        
        Args:
            papers: List of paper dictionaries to summarize
            
        Returns:
            Dictionary containing structured summaries
        """
        if not papers:
            raise ValueError("No papers provided for summarization")

        # Generate summaries
        outputs = []
        for paper in papers:
            full_text = paper.get("abstract", "")
            prompt = (
                f"Extract structured summary from this abstract:\n{full_text}\n\n"
                "Use headers ### Abstract ### Methods ### Results ### Conclusion and include citations where possible."
            )
            llm_output = await call_azure_chat(prompt, max_tokens=1000)
            structured = parse_structured_sections(llm_output)
            structured["title"] = paper.get("title")
            outputs.append(structured)

        return {
            "summaries": outputs,
            "papers_summarized": [p.get("title") for p in papers],
            "timestamp": datetime.now().isoformat()
        }

    async def generate_overall_synthesis(
        self,
        papers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate an overall synthesis across the provided papers.
        
        Args:
            papers: List of paper dictionaries to include in synthesis
            
        Returns:
            Dictionary containing synthesis
        """
        if not papers:
            raise ValueError("No papers provided for synthesis")

        # Combine text from papers
        combined_text = ""
        for paper in papers:
            combined_text += f"Title: {paper.get('title')}\nAbstract: {paper.get('abstract', '')}\n\n"

        # Generate synthesis
        prompt = (
            f"Synthesize across these papers, providing an overall summary and including citations.\n{combined_text}"
            "Focus on key findings, methodologies, and conclusions across the papers."
        )
        synthesis = await call_azure_chat(prompt, max_tokens=1500)

        return {
            "synthesis": synthesis,
            "papers_synthesized": [p.get("title") for p in papers],
            "timestamp": datetime.now().isoformat()
        }