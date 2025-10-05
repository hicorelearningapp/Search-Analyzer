# services/suggestion_service.py
from typing import List, Dict
import re
from datetime import datetime

class SuggestionService:    
    def __init__(self):
        """Initialize the SuggestionService."""
        pass

    def generate_topic_suggestions(self, keywords: str, limit: int = 6) -> Dict[str, any]:
        """
        Generate topic suggestions based on input keywords.
        
        Args:
            keywords: Comma-separated or newline-separated keywords
            limit: Maximum number of suggestions to return (default: 6)
            
        Returns:
            Dictionary containing generated topic suggestions
        """
        words = [w.strip() for w in re.split(r'[,\n;]+', keywords) if w.strip()]
        if not words:
            return {"suggestions": [], "timestamp": datetime.now().isoformat()}
        
        # Topic generation templates
        base_templates = [
            "{kw}: a systematic review of techniques and gaps",
            "Novel approaches to {kw} in {kw2}",
            "Comparative study of algorithms for {kw}",
            "Application of {kw} to healthcare / industry",
            "Benchmarking {kw} datasets and metrics",
        ]
        
        # Generate suggestions
        suggestions = []
        for template in base_templates:
            if "{kw2}" in template and len(words) > 1:
                for i in range(len(words)):
                    for j in range(len(words)):
                        if i != j:
                            suggestion = template.format(kw=words[i], kw2=words[j])
                            suggestions.append(suggestion)
                            if len(suggestions) >= limit:
                                break
                    if len(suggestions) >= limit:
                        break
            else:
                for word in words:
                    suggestion = template.format(kw=word, kw2=word)
                    suggestions.append(suggestion)
                    if len(suggestions) >= limit:
                        break
            
            if len(suggestions) >= limit:
                break
                
        return {
            "suggestions": suggestions[:limit],
            "timestamp": datetime.now().isoformat()
        }