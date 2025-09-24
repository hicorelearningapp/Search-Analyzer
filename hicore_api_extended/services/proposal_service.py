from typing import List, Dict, Optional
from openai import AzureOpenAI
import asyncio
from ..app_state import AppState

class ProposalService:
    @staticmethod
    async def proposal_writer(title: str = Form(...), chosen_subtopics: str = Form(""), expected_methods: str = Form("")):
        """Writes a research proposal draft based on user inputs and suggested topics."""
        subs = [s.strip() for s in re.split(r'[,\n;]+', chosen_subtopics) if s.strip()]
        methods = [m.strip() for m in re.split(r'[,\n;]+', expected_methods) if m.strip()]
        if not _is_azure_configured():
            return {
                "title": title,
                "background_and_novelty": f"(Fallback) Background for {title}",
                "abstract": f"(Fallback) Abstract for {title}",
                "review_of_literature_outline": "Fallback outline",
                "research_questions": "1) Primary\n2) Secondary",
                "aim_scope": "1) Aim\n2) Aim",
                "methodology_skeleton": f"Fallback methods: {methods}",
                "workplan_timeline_example": "Month 1-2: Literature; 3-6: Data; 7-9: Analysis; 10-12: Writing"
            }
        
        # Generate content for each section using Azure OpenAI
        background_prompt = f"Write a background and novelty section for a research proposal titled '{title}'. Focus on the subtopics: {', '.join(subs)}."
        abstract_prompt = f"Write a concise abstract (around 150 words) for a research proposal titled '{title}' with a focus on {', '.join(subs)}."
        review_prompt = f"Create an outline for a literature review on the topic '{title}'. The outline should be based on the subtopics: {', '.join(subs)}."
        questions_prompt = f"List 3-5 key research questions for a study titled '{title}' on the topics of {', '.join(subs)}."
        aims_prompt = f"Define the overall aim and scope of a research project titled '{title}' focusing on {', '.join(subs)}."
        methodology_prompt = f"Describe the methodology section for a proposal on '{title}'. The expected methods include: {', '.join(methods)}. Provide a step-by-step skeleton."
        workplan_prompt = f"Create a sample workplan and timeline for a 12-month research project on '{title}'."

        return {
            "title": title,
            "background_and_novelty": call_azure_chat(background_prompt),
            "abstract": call_azure_chat(abstract_prompt, max_tokens=200),
            "review_of_literature_outline": call_azure_chat(review_prompt),
            "research_questions": call_azure_chat(questions_prompt, max_tokens=150),
            "aim_scope": call_azure_chat(aims_prompt, max_tokens=150),
            "methodology_skeleton": call_azure_chat(methodology_prompt),
            "workplan_timeline_example": call_azure_chat(workplan_prompt)
        }

    @staticmethod
    async def _generate_fallback_proposal(title: str, methods: List[str]) -> Dict[str, str]:
        """Generate a fallback proposal when Azure client is not available."""
        return {
            "title": title,
            "background": f"Background for {title} (fallback mode)",
            "abstract": f"Abstract for {title}",
            "literature_review": "Literature review not available in fallback mode",
            "research_questions": ["Sample research question 1", "Sample research question 2"],
            "aims": f"Research aims for {title}",
            "methodology": f"Proposed methods: {', '.join(methods) if methods else 'Not specified'}"
        }