# services/review_service.py
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from utils.azure_client import call_azure_chat
from app_state import AppState
from datetime import datetime

class ReviewService:

    def __init__(self, app_state: Optional[AppState] = None):
        self.app_state = app_state or AppState()

    async def scaffold_review(self,papers: List[Dict[str, Any]],subtopics: Optional[List[str]] = None,session_id: Optional[str] = None,azure_client: Optional[AzureOpenAI] = None) -> Dict[str, Any]:

        if not papers:
            raise ValueError("No papers provided for review")

        if session_id:
            session_data = self.app_state.get_user_state(session_id)
            if not session_data:
                raise ValueError("No session data found for the provided session ID")
        else:
            session_id = f"review_{int(datetime.now().timestamp())}"
            session_data = self.app_state.get_user_state(session_id)
            session_data.synthesis_storage.update({
                "created_at": datetime.now().isoformat(),
                "type": "review_generation"
            })
            
        subs = subtopics or ["Background", "Methods", "Results"]
        draft = {
            "subtopics": subs,
            "papers_considered": len(papers),
            "sections": {},
            "paper_titles": [p.get("title", "Untitled") for p in papers],
            "session_id": session_id,
            "created_at": datetime.now().isoformat()
        }

        session_data.synthesis_storage.update(draft)
        session_data.search_results = papers
        
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
            
            draft["sections"][subtopic] = await call_azure_chat(
                subtopic_prompt,
                max_tokens=1000,
                azure_client=azure_client
            )

        # Generate introduction and conclusion
        draft["introduction"] = await call_azure_chat(
            f"Write an introduction for a review paper covering these topics: {', '.join(subs)}. "
            f"The review is based on these papers:\n{combined_abstracts}",
            max_tokens=1000,
            azure_client=azure_client
        )

        draft["conclusion"] = await call_azure_chat(
            "Write a comprehensive conclusion that summarizes the key findings from the review and "
            "suggests future research directions based on these papers:\n" + combined_abstracts,
            max_tokens=1000,
            azure_client=azure_client
        )

        session_data.synthesis_storage.update(draft)
        return draft

review_service = ReviewService()