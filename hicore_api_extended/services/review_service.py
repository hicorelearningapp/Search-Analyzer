from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from ..utils.azure_client import call_azure_chat

class ReviewService:
    @staticmethod
    async def scaffold_review(papers: List[Dict[str, Any]],subtopics: Optional[List[str]] = None,azure_client: Optional[AzureOpenAI] = None) -> Dict[str, Any]:
        if not papers:
            raise ValueError("No papers provided for review")
            
        subs = subtopics or ["Background", "Methods", "Results"]
        draft = {
            "subtopics": subs,
            "papers_considered": len(papers),
            "sections": {}
        }
        
        combined_abstracts = "\n\n".join(
            f"Title: {p.get('title', 'Untitled')}\n"
            f"Abstract: {p.get('abstract', 'No abstract available')}"
            for p in papers
        )

        intro_prompt = (
            "Write an introduction for a review paper based on the following topics and papers. "
            f"Topics: {', '.join(subs)}\n\n"
            f"Papers:\n{combined_abstracts}"
        )
        
        conclusion_prompt = (
            "Write a comprehensive conclusion for a review paper based on the following topics and papers. "
            f"Topics: {', '.join(subs)}\n\n"
            f"Papers:\n{combined_abstracts}"
        )

        for subtopic in subs:
            subtopic_prompt = (
                f"Write a detailed section about '{subtopic}' for a review paper. "
                f"Base the content on these papers:\n{combined_abstracts}"
            )
            draft["sections"][subtopic] = await call_azure_chat(
                subtopic_prompt,
                max_tokens=1000,
                azure_client=azure_client
            )

        draft["introduction"] = await call_azure_chat(
            intro_prompt,
            max_tokens=1000,
            azure_client=azure_client
        )
        draft["conclusion"] = await call_azure_chat(
            conclusion_prompt,
            max_tokens=1000,
            azure_client=azure_client
        )
        
        return draft
