# services/researcher_service.py
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from app_state import AppState, SessionState
from fastapi import HTTPException

class ComparisonResult(BaseModel):
    """Model for comparison results."""
    similarities: List[Dict[str, Any]]
    differences: List[Dict[str, Any]]
    summary: str
    timestamp: str = datetime.now().isoformat()

class ResearcherService:
    def __init__(self, app_state: Optional[AppState] = None):
        """Initialize with optional app state injection."""
        self.app_state = app_state or AppState()

    async def compare_selected_papers(
        self,
        session_data: SessionState
    ) -> Dict[str, Any]:
        """
        Compare selected papers in a session.
        
        Args:
            session_data: The session data containing selected papers
            
        Returns:
            Dictionary with comparison results
        """
        try:
            selected_indices = session_data.selected_indices
            search_results = session_data.search_results
            
            if len(selected_indices) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="At least 2 papers must be selected for comparison"
                )
                
            # Get the selected papers
            selected_papers = [
                search_results[i] 
                for i in selected_indices 
                if i < len(search_results)
            ]
            
            if len(selected_papers) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="Not enough valid papers selected for comparison"
                )
            
            # Your comparison logic here
            comparison_result = await self._compare_papers(selected_papers)
            
            return comparison_result.dict()
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error in paper comparison: {str(e)}"
            )

    async def compare_methodologies(
        self,
        session_data: SessionState
    ) -> Dict[str, Any]:
        """
        Compare methodologies of selected papers in a session.
        """
        try:
            selected_indices = session_data.selected_indices
            search_results = session_data.search_results
            
            if len(selected_indices) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="At least 2 papers must be selected for methodology comparison"
                )
                
            # Get the selected papers
            selected_papers = [
                search_results[i] 
                for i in selected_indices 
                if i < len(search_results)
            ]
            
            # Your methodology comparison logic here
            comparison_result = await self._compare_methodologies(selected_papers)
            
            return comparison_result.dict()
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error in methodology comparison: {str(e)}"
            )

    async def _compare_papers(self, papers: List[Dict[str, Any]]) -> ComparisonResult:
        """
        Internal method to compare papers.
        
        Args:
            papers: List of paper dictionaries to compare
            
        Returns:
            ComparisonResult object with comparison data
        """
        # Your comparison logic here
        # This is a placeholder implementation
        similarities = []
        differences = []
        
        # Example comparison logic
        if len(papers) >= 2:
            paper1 = papers[0]
            paper2 = papers[1]
            
            # Compare titles
            if paper1.get('title') and paper2.get('title'):
                if paper1['title'] == paper2['title']:
                    similarities.append({
                        "field": "title",
                        "value": paper1['title']
                    })
                else:
                    differences.append({
                        "field": "title",
                        "values": [paper1['title'], paper2['title']]
                    })
        
        return ComparisonResult(
            similarities=similarities,
            differences=differences,
            summary=f"Comparison of {len(papers)} papers completed"
        )

    async def _compare_methodologies(self, papers: List[Dict[str, Any]]) -> ComparisonResult:
        """
        Internal method to compare methodologies.
        """
        # Your methodology comparison logic here
        # This is a placeholder implementation
        similarities = []
        differences = []
        
        # Example methodology comparison
        if len(papers) >= 2:
            # Compare methodologies if available
            method1 = papers[0].get('methodology', 'Not specified')
            method2 = papers[1].get('methodology', 'Not specified')
            
            if method1 == method2:
                similarities.append({
                    "field": "methodology",
                    "value": method1
                })
            else:
                differences.append({
                    "field": "methodology",
                    "values": [method1, method2]
                })
        
        return ComparisonResult(
            similarities=similarities,
            differences=differences,
            summary=f"Methodology comparison of {len(papers)} papers completed"
        )