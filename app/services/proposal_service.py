# services/proposal_service.py
from typing import List, Dict, Optional
from openai import AzureOpenAI
from datetime import datetime
from utils.azure_client import call_azure_chat, _is_azure_configured

class ProposalService:
    def __init__(self):
        """Initialize the ProposalService."""
        pass

    async def proposal_writer(
        self,
        title: str,
        chosen_subtopics: Optional[List[str]] = None,
        expected_methods: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """
        Generate a research proposal.
        
        Args:
            title: The title of the research proposal
            chosen_subtopics: List of subtopics to include
            expected_methods: List of expected research methods
            
        Returns:
            Dictionary containing the generated proposal and metadata
        """
        # Default values if not provided
        chosen_subtopics = chosen_subtopics or []
        expected_methods = expected_methods or []

        # Prepare the prompt for the proposal
        prompt = self._build_proposal_prompt(title, chosen_subtopics, expected_methods)
        
        # Generate the proposal using Azure OpenAI
        proposal = await call_azure_chat(prompt, max_tokens=2000)
        
        # Return the result without session storage
        return {
            "title": title,
            "subtopics": chosen_subtopics,
            "methods": expected_methods,
            "proposal": proposal,
            "created_at": datetime.now().isoformat()
        }

    def _build_proposal_prompt(
        self,
        title: str,
        subtopics: List[str],
        methods: List[str]
    ) -> str:
        """Build the prompt for generating a research proposal."""
        subtopics_text = "\n- " + "\n- ".join(subtopics) if subtopics else "Not specified"
        methods_text = "\n- " + "\n- ".join(methods) if methods else "Not specified"
        
        return f"""
        Write a detailed research proposal with the following details:
        
        Title: {title}
        
        Subtopics to include:
        {subtopics_text}
        
        Expected Methods:
        {methods_text}
        
        The proposal should include the following sections:
        1. Introduction and Background
        2. Research Questions/Hypotheses
        3. Literature Review
        4. Methodology
        5. Expected Outcomes
        6. Timeline
        7. References
        
        Make the proposal detailed and well-structured.
        """.strip()