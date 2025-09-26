# services/summary_service.py
from typing import List, Dict, Any, Optional
from datetime import datetime
from app_state import AppState
from utils.parsing import parse_structured_sections
from utils.azure_client import call_azure_chat

class SummaryService:
    def __init__(self, app_state: Optional[AppState] = None):
        """Initialize with optional app state injection."""
        self.app_state = app_state or AppState()

    async def generate_structured_summaries(
        self,
        selected_indices: List[int],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate structured summaries for selected papers.
        
        Args:
            selected_indices: List of paper indices to summarize
            session_id: Optional session ID for tracking
            
        Returns:
            Dictionary containing structured summaries and session info
        """
        # Initialize session if needed
        if session_id:
            session_data = self.app_state.get_user_state(session_id)
            if not session_data:
                raise ValueError("No session data found for the provided session ID")
        else:
            session_id = f"summary_{int(datetime.now().timestamp())}"
            session_data = self.app_state.get_user_state(session_id)
            session_data.synthesis_storage.update({
                "created_at": datetime.now().isoformat(),
                "type": "structured_summary"
            })

        # Validate selected indices
        if not selected_indices:
            selected_indices = session_data.selected_indices or []
            if not selected_indices:
                raise ValueError("No papers selected for summarization")

        # Generate summaries
        outputs = []
        for i in selected_indices:
            if 0 <= i < len(session_data.search_results):
                paper = session_data.search_results[i]
                full_text = paper.get("abstract", "")
                prompt = (
                    f"Extract structured summary from this abstract:\n{full_text}\n\n"
                    "Use headers ### Abstract ### Methods ### Results ### Conclusion and include citations where possible."
                )
                llm_output = await call_azure_chat(prompt, max_tokens=1000)
                structured = parse_structured_sections(llm_output)
                structured["title"] = paper.get("title")
                outputs.append(structured)

        # Store results in session
        result = {
            "session_id": session_id,
            "summaries": outputs,
            "papers_summarized": [session_data.search_results[i].get("title") for i in selected_indices if i < len(session_data.search_results)],
            "timestamp": datetime.now().isoformat()
        }
        
        session_data.synthesis_storage["latest_summaries"] = result
        session_data.synthesis_storage["last_activity"] = datetime.now().isoformat()
        
        return result

    async def generate_overall_synthesis(
        self,
        selected_indices: Optional[List[int]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an overall synthesis across selected papers.
        
        Args:
            selected_indices: List of paper indices to include in synthesis
            session_id: Optional session ID for tracking
            
        Returns:
            Dictionary containing synthesis and session info
        """
        # Initialize session if needed
        if session_id:
            session_data = self.app_state.get_user_state(session_id)
            if not session_data:
                raise ValueError("No session data found for the provided session ID")
        else:
            session_id = f"synthesis_{int(datetime.now().timestamp())}"
            session_data = self.app_state.get_user_state(session_id)
            session_data.synthesis_storage.update({
                "created_at": datetime.now().isoformat(),
                "type": "overall_synthesis"
            })

        # Validate selected indices
        if not selected_indices:
            selected_indices = session_data.selected_indices or []
            if not selected_indices:
                raise ValueError("No papers selected for synthesis")

        # Combine text from selected papers
        combined_text = ""
        for i in selected_indices:
            if 0 <= i < len(session_data.search_results):
                paper = session_data.search_results[i]
                combined_text += f"Title: {paper.get('title')}\nAbstract: {paper.get('abstract')}\n\n"

        # Generate synthesis
        prompt = (
            f"Synthesize across these papers, providing an overall summary and including citations.\n{combined_text}"
            "Focus on key findings, methodologies, and conclusions across the papers."
        )
        synthesis = await call_azure_chat(prompt, max_tokens=1500)

        # Store results in session
        result = {
            "session_id": session_id,
            "synthesis": synthesis,
            "papers_synthesized": [session_data.search_results[i].get("title") for i in selected_indices if i < len(session_data.search_results)],
            "timestamp": datetime.now().isoformat()
        }
        
        session_data.synthesis_storage["latest_synthesis"] = result
        session_data.synthesis_storage["last_activity"] = datetime.now().isoformat()
        
        return result

# Singleton instance for easy import
summary_service = SummaryService()