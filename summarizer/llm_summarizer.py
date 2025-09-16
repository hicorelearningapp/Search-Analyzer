# summarizer/llm_summarizer.py
from typing import Dict, Optional
import os
from config import Config

try:
    import openai
    _HAS_OPENAI = True
    # Set API key from environment or config
    openai.api_key = os.getenv("OPENAI_API_KEY") or Config.OPENAI_API_KEY
except Exception:
    _HAS_OPENAI = False


class LLMSummarizer:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model

    def summarize(self, text: str, doc_type: Optional[str] = None, pages: int = 2) -> Dict:
        """
        Summarize input text using OpenAI (if available) or fallback to truncation.
        """
        if not text:
            return {"content": "(No content provided)", "cached": False}

        if _HAS_OPENAI and openai.api_key:
            prompt = self._build_prompt(text, doc_type, pages)
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful summarizer."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=1200
                )
                content = response.choices[0].message["content"].strip()
                return {"content": content, "cached": False}
            except Exception as e:
                # Fallback with error info + excerpt
                excerpt = (text or "")[:3000]
                return {
                    "content": f"(⚠️ LLM error: {e})\n\nFallback excerpt:\n{excerpt}",
                    "cached": False
                }

        # If OpenAI not available → fallback
        excerpt = (text or "")[:3000]
        return {
            "content": f"(⚠️ OpenAI not available — showing excerpt)\n\n{excerpt}",
            "cached": False
        }

    def _build_prompt(self, text: str, doc_type: Optional[str], pages: int) -> str:
        """Builds a structured prompt for LLM summarization."""
        heading = doc_type or "Summary"
        return (
            f"Generate a {pages}-page {heading} from the following content:\n\n"
            f"{text}\n\n"
            "Format the output as a clear, structured report (no markdown), "
            "with section headings when appropriate."
        )
