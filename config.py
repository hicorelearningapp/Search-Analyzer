# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")

    @classmethod
    def verify_config(cls):
        # Non-fatal: prefer warning - but keep simple check
        if not cls.OPENAI_API_KEY:
            # It's okay for the app to run without OPENAI in fallback mode, but warn.
            print("Warning: OPENAI_API_KEY not set. LLM-based summaries will use fallback summarizer.")
        # ensure reports directory exists
        os.makedirs(cls.REPORTS_DIR, exist_ok=True)
        return True
