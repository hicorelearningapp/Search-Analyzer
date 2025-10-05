# summarizer/llm_summarizer.py
from typing import Dict, Any, List
from openai import OpenAI
import os
import math

from utils.document_system_utils import document_system
from sources.retriever import VectorRetriever


class LLMSummarizer:
    def __init__(self, model_name="gpt-4o-mini"):
        # Use OpenAI client (needs OPENAI_API_KEY in environment or passed directly)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name

    def summarize_with_structure(
        self, retriever: VectorRetriever, query: str, doc_type: str, pages: int = 2
    ) -> Dict[str, Any]:
        """
        Retrieve chunks from retriever, build prompts, and call GPT-4o-mini.
        Optimized for producing long outputs (multi-page, multi-thousand word).
        """

        # Get the document type template
        dt = document_system.get_document_type(doc_type)
        headings = dt.structure if dt else []

        # Collect top chunks from retriever
        chunks = retriever.get_top_chunks_for_model(query, max_tokens=6000)

        # Word target (approx 500 words per page)
        target_words_total = pages * 500

        # Decide iterations
        pages_per_call = 8  # safe upper bound for one call (~4k words)
        iterations = math.ceil(pages / pages_per_call)
        words_per_iter = pages_per_call * 500

        all_outputs: List[str] = []
        for i in range(iterations):
            # Distribute chunks across iterations
            chunk_text = "\n\n".join(chunks[i::iterations]) if chunks else ""

            continuation_note = (
                f"This is Part {i+1} of {iterations}. Continue writing where the last part stopped. "
                "Do NOT repeat introductions or conclusions until the final part.\n\n"
                if i > 0 else ""
            )

            # Build prompt
            prompt = (
                f"Write a '{doc_type}' document with the following sections:\n"
                + "\n".join(f"- {h}" for h in headings)
                + "\n\n"
                f"{continuation_note}"
                f"Base your content on this material. Expand thoroughly with multiple paragraphs, "
                f"examples, analysis, and detailed explanations.\n"
                f"Write AT LEAST {words_per_iter} words (around {pages_per_call} pages). "
                f"Do not stop early. Do not summarize; fully elaborate.\n\n"
                f"Material:\n{chunk_text}\n\n"
                f"Ensure this part is cohesive and continues smoothly into the next one."
            )

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful writing assistant that produces detailed, structured, long-form documents."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=16000,  # enough for ~5k words
            )

            part_text = response.choices[0].message.content.strip()
            all_outputs.append(part_text)

        combined_text = "\n\n".join(all_outputs)

        return {
            "document_type": doc_type,
            "headings": headings,
            "content": combined_text,
            "model": self.model_name,
            "metadata": {
                "pages_requested": pages,
                "iterations": iterations,
                "pages_per_call": pages_per_call,
                "target_words": target_words_total,
                "max_tokens_per_call": 16000,
            },
        }


# For backward compatibility
def summarize_with_structure(
    retriever: VectorRetriever, query: str, doc_type: str, pages: int = 1, **kwargs
) -> Dict[str, Any]:
    summarizer = LLMSummarizer()
    return summarizer.summarize_with_structure(retriever, query, doc_type, pages)
