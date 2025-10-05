"""
services/researcher_service.py
"""
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from fastapi import HTTPException

class ComparisonResult(BaseModel):
    """Model for comparison results."""
    similarity: List[Dict[str, Any]]
    differences: List[Dict[str, Any]]
    summary: str
    timestamp: str = datetime.now().isoformat()

class ResearcherService:
    def __init__(self):
        """Initialize the ResearcherService."""
        pass

    async def compare_papers(
        self,
        papers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare a list of papers.
        
        Args:
            papers: List of paper dictionaries to compare
            
        Returns:
            Dictionary with comparison results
        """
        try:
            if len(papers) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="At least 2 papers must be provided for comparison"
                )
            
            comparison_result = await self._compare_papers(papers)
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
        papers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare methodologies of the provided papers.
        
        Args:
            papers: List of paper dictionaries to compare
            
        Returns:
            Dictionary with methodology comparison results
        """
        try:
            if len(papers) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="At least 2 papers must be provided for methodology comparison"
                )
                
            comparison_result = await self._compare_methodologies(papers)
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
        similarity = []
        differences = []
        
        # Example comparison logic
        if len(papers) >= 2:
            paper1 = papers[0]
            paper2 = papers[1]
            
            # Compare titles
            if paper1.get('title') and paper2.get('title'):
                if paper1['title'] == paper2['title']:
                    similarity.append({
                        "field": "title",
                        "value": paper1['title']
                    })
                else:
                    differences.append({
                        "field": "title",
                        "values": [paper1['title'], paper2['title']]
                    })
        
        return ComparisonResult(
            similarity=similarity,
            differences=differences,
            summary=f"Comparison of {len(papers)} papers completed"
        )

    async def _compare_methodologies(self, papers: List[Dict[str, Any]]) -> ComparisonResult:
        """
        Internal method to compare methodologies.
        
        Args:
            papers: List of paper dictionaries to compare
            
        Returns:
            ComparisonResult object with methodology comparison data
        """
        similarity = []
        differences = []
        
        # Example methodology comparison
        if len(papers) >= 2:
            # Compare methodologies if available
            method1 = papers[0].get('methodology', 'Not specified')
            method2 = papers[1].get('methodology', 'Not specified')
            
            if method1 == method2:
                similarity.append({
                    "field": "methodology",
                    "value": method1
                })
            else:
                differences.append({
                    "field": "methodology",
                    "values": [method1, method2]
                })
        
        return ComparisonResult(
            similarity=similarity,
            differences=differences,
            summary=f"Methodology comparison of {len(papers)} papers completed"
        )