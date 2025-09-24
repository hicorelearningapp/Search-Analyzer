#researcher_service.py
from typing import List, Dict, Any
from utils.azure_client import call_azure_chat
from app_state import AppState
from fastapi import HTTPException, Depends
class ResearcherService:
    @staticmethod
    async def compare_selected_papers_endpoint(app_state: AppState) -> Dict[str, Any]:
        try:
            selected_indices = app_state.selected_indices
            search_results = app_state.search_results
            
            if len(selected_indices) < 2:
                raise HTTPException(status_code=400, detail="At least 2 papers must be selected for comparison")
                
            subset = [
                search_results[i] 
                for i in selected_indices 
                if i < len(search_results)
            ]
            
            combined = "\n\n".join([
                f"Title: {p.get('title', 'No title')}\n"
                f"Abstract: {p.get('abstract', 'No abstract available')}" 
                for p in subset
            ])
            
            prompt = (
                "Compare these research papers, highlighting their similarities and differences. "
                "Focus on:\n"
                "1. Research objectives and questions\n"
                "2. Methodologies used\n"
                "3. Key findings and conclusions\n"
                "4. Any notable similarities or contradictions\n\n"
                "Papers to compare:\n" + combined
            )
            
            comparison = call_azure_chat(prompt, max_tokens=1000)
            
            return {"comparison": comparison, "papers_compared": [p.get('title', 'Untitled') for p in subset]}
            
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error comparing papers: {str(e)}"
            )
