# summarizer/llm_summarizer.py
from typing import Dict, Optional
import os
from config import Config

try:
    import openai
    _HAS_OPENAI = True
    openai.api_key = os.getenv("OPENAI_API_KEY") or Config.OPENAI_API_KEY
except Exception:
    _HAS_OPENAI = False


class LLMSummarizer:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model

    def summarize(self, text: str, doc_type: Optional[str] = None, pages: int = 2) -> Dict:
        if _HAS_OPENAI and openai.api_key:
            prompt = self._build_prompt(text, doc_type, pages)
            try:
                resp = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful summarizer."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=1000
                )
                out = resp.choices[0].message["content"].strip()
                return {"content": out, "cached": False}
            except Exception as e:
                return {
                    "content": f"(LLM error: {e})\n\n" + (text[:4000] if text else ""),
                    "cached": False
                }

        # fallback if OpenAI not available
        excerpt = (text or "")[:4000]
        return {"content": excerpt, "cached": False}

    def _build_prompt(self, text: str, doc_type: Optional[str], pages: int) -> str:
        heading = doc_type or "Summary"
        return (
            f"Generate a {pages}-page {heading} from the following content.\n\n"
            f"Content:\n{text}\n\n"
            "Provide a clear, structured summary without markdown, with headings when appropriate."
        )
