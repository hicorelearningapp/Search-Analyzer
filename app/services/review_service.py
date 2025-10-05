# services/review_service.py
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from utils.azure_client import call_azure_chat
from datetime import datetime

class ReviewService:
    """Service for generating review papers from a collection of research papers."""
    
    def __init__(self):
        """Initialize the ReviewService."""
        pass

    async def scaffold_review(
        self,
        papers: List[Dict[str, Any]],
        subtopics: Optional[List[str]] = None,
        azure_client: Optional[AzureOpenAI] = None
    ) -> Dict[str, Any]:
        """
        Generate a structured review paper from a collection of research papers.
        
        Args:
            papers: List of paper dictionaries containing at least 'title' and 'abstract'
            subtopics: List of subtopics to include in the review (default: ["Background", "Methods", "Results"])
            azure_client: Optional AzureOpenAI client instance
            
        Returns:
            Dictionary containing the structured review paper
            
        Raises:
            ValueError: If no papers are provided
        """
        if not papers:
            raise ValueError("No papers provided for review")
            
        # Use default subtopics if none provided
        subs = subtopics or ["Background", "Methods", "Results"]
        
        # Initialize the review structure
        review = {
            "subtopics": subs,
            "papers_considered": len(papers),
            "sections": {},
            "paper_titles": [p.get("title", "Untitled") for p in papers],
            "created_at": datetime.now().isoformat()
        }
        
        # Combine paper information for the LLM
        combined_abstracts = "\n\n".join(
            f"Title: {p.get('title', 'Untitled')}\n"
            f"Abstract: {p.get('abstract', 'No abstract available')}"
            for p in papers
        )

        # Generate content for each section
        for subtopic in subs:
            subtopic_prompt = (
                f"Write a detailed section about '{subtopic}' for a review paper. "
                f"Base the content on these papers:\n{combined_abstracts}\n\n"
                "Focus on synthesizing information across papers rather than summarizing them individually. "
                "Highlight key findings, methodologies, and relationships between the papers."
            )
            
            review["sections"][subtopic] = await call_azure_chat(
                subtopic_prompt,
                max_tokens=1000,
                azure_client=azure_client
            )

        # Generate introduction and conclusion
        review["introduction"] = await call_azure_chat(
            f"Write an introduction for a review paper covering these topics: {', '.join(subs)}. "
            f"The review is based on these papers:\n{combined_abstracts}",
            max_tokens=1000,
            azure_client=azure_client
        )

        review["conclusion"] = await call_azure_chat(
            "Write a comprehensive conclusion that summarizes the key findings from the review and "
            "suggests future research directions based on these papers:\n" + combined_abstracts,
            max_tokens=1000,
            azure_client=azure_client
        )

        return review