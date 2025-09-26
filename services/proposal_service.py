# services/proposal_service.py
from typing import List, Dict, Optional
from openai import AzureOpenAI
from datetime import datetime
import asyncio
from app_state import AppState
from utils.azure_client import call_azure_chat, _is_azure_configured

class ProposalService:
    def __init__(self, app_state: Optional[AppState] = None):
        """Initialize with optional app state injection."""
        self.app_state = app_state or AppState()

    async def proposal_writer(
        self,
        title: str,
        chosen_subtopics: Optional[List[str]] = None,
        expected_methods: Optional[List[str]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, str]:
        if session_id:
            session_data = self.app_state.get_user_state(session_id)
            if not session_data:
                raise ValueError("No session data found for the provided session ID")
        else:
            session_id = f"proposal_{int(datetime.now().timestamp())}"
            session_data = self.app_state.get_user_state(session_id)
            session_data.synthesis_storage.update({
                "created_at": datetime.now().isoformat(),
                "type": "proposal_generation"
            })

        subs = chosen_subtopics or []
        methods = expected_methods or []
        
        proposal = {
            "title": title,
            "subtopics": subs,
            "methods": methods,
            "session_id": session_id,
            "created_at": datetime.now().isoformat()
        }
        
        session_data.synthesis_storage["current_proposal"] = proposal
        session_data.synthesis_storage["last_activity"] = datetime.now().isoformat()

        if not _is_azure_configured():
            fallback = {
                "title": title,
                "background_and_novelty": f"(Fallback) Background for {title}",
                "abstract": f"(Fallback) Abstract for {title}",
                "review_of_literature_outline": "Fallback outline",
                "research_questions": "1) Primary\n2) Secondary",
                "aim_scope": "1) Aim\n2) Aim",
                "methodology_skeleton": f"Fallback methods: {methods}",
                "workplan_timeline_example": "Month 1-2: Literature; 3-6: Data; 7-9: Analysis; 10-12: Writing"
            }
            proposal.update(fallback)
            session_data.synthesis_storage["latest_proposal"] = proposal
            return proposal

        background_prompt = self._create_background_prompt(title, subs)
        abstract_prompt = self._create_abstract_prompt(title, subs)
        review_prompt = self._create_review_prompt(title, subs)
        questions_prompt = self._create_questions_prompt(title, subs)
        aims_prompt = self._create_aims_prompt(title, subs)
        methodology_prompt = self._create_methodology_prompt(title, methods)
        workplan_prompt = self._create_workplan_prompt(title)

        sections = await asyncio.gather(
            call_azure_chat(background_prompt),
            call_azure_chat(abstract_prompt, max_tokens=200),
            call_azure_chat(review_prompt),
            call_azure_chat(questions_prompt, max_tokens=150),
            call_azure_chat(aims_prompt, max_tokens=150),
            call_azure_chat(methodology_prompt),
            call_azure_chat(workplan_prompt)
        )

        proposal.update({
            "background_and_novelty": sections[0],
            "abstract": sections[1],
            "review_of_literature_outline": sections[2],
            "research_questions": sections[3],
            "aim_scope": sections[4],
            "methodology_skeleton": sections[5],
            "workplan_timeline_example": sections[6]
        })

        session_data.synthesis_storage["latest_proposal"] = proposal
        return proposal

    def _create_background_prompt(self, title: str, subtopics: List[str]) -> str:
        return f"Write a background and novelty section for a research proposal titled '{title}'. Focus on the subtopics: {', '.join(subtopics)}."

    def _create_abstract_prompt(self, title: str, subtopics: List[str]) -> str:
        return f"Write a concise abstract (around 150 words) for a research proposal titled '{title}' with a focus on {', '.join(subtopics)}."

    def _create_review_prompt(self, title: str, subtopics: List[str]) -> str:
        return f"Create an outline for a literature review on the topic '{title}'. The outline should be based on the subtopics: {', '.join(subtopics)}."

    def _create_questions_prompt(self, title: str, subtopics: List[str]) -> str:
        return f"List 3-5 key research questions for a study titled '{title}' on the topics of {', '.join(subtopics)}."

    def _create_aims_prompt(self, title: str, subtopics: List[str]) -> str:
        return f"Define the overall aim and scope of a research project titled '{title}' focusing on {', '.join(subtopics)}."

    def _create_methodology_prompt(self, title: str, methods: List[str]) -> str:
        return f"Describe the methodology section for a proposal on '{title}'. The expected methods include: {', '.join(methods)}. Provide a step-by-step skeleton."

    def _create_workplan_prompt(self, title: str) -> str:
        return f"Create a sample workplan and timeline for a 12-month research project on '{title}'."

# Singleton instance for easy import
proposal_service = ProposalService()