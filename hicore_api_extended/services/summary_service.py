from typing import List, Dict, Any
from fastapi import Depends
from ..app_state import AppState
from ..utils.parsing import parse_structured_sections
from ..utils.azure_client import call_azure_chat

class SummaryService:
    @staticmethod
    def generate_structured_summaries(app_state: AppState, selected_idx: List[int]) -> List[Dict[str, Any]]:
        outputs = []
        for i in selected_idx:
            paper = app_state.search_results[i]
            full_text = paper.get("abstract", "")
            prompt = f"Extract structured summary from this abstract:\n{full_text}\n\nUse headers ### Abstract ### Methods ### Results ### Conclusion and include citations where possible."
            llm_output = call_azure_chat(prompt, max_tokens=1000)
            structured = parse_structured_sections(llm_output)
            structured["title"] = paper.get("title")
            outputs.append(structured)
        return outputs

    @staticmethod
    def generate_overall_synthesis(app_state: AppState, selected_idx: List[int]) -> str:
        combined_text = ""
        for i in selected_idx:
            paper = app_state.search_results[i]
            combined_text += f"Title: {paper.get('title')}\nAbstract: {paper.get('abstract')}\n\n"
        prompt = f"Synthesize across these papers, providing an overall summary and including citations.\n{combined_text}"
        overall = call_azure_chat(prompt, max_tokens=1500)
        app_state.synthesis_storage["latest"] = overall
        return overall
