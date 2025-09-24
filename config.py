# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Azure OpenAI Configuration
    AZURE_CFG = {
        "api_key": os.getenv("AZURE_OPENAI_API_KEY", ""),
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
        "api_version": "2025-01-01-preview",
        "deployment_name": "gpt-4"
    }

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

    # API Endpoints
    SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
    SEMANTIC_SCHOLAR_AUTHOR_URL = "https://api.semanticscholar.org/graph/v1/author/search"

    # Application Settings
    REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")

    @classmethod
    def verify_config(cls):
        """Verify that all required configurations are set."""
        # Verify Azure OpenAI configuration
        if not cls.AZURE_CFG["api_key"] or not cls.AZURE_CFG["endpoint"]:
            print("Warning: Azure OpenAI API key or endpoint not set. Some features may not work.")

        # Verify other API keys
        if not cls.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set. LLM-based summaries will use fallback summarizer.")
        if not cls.SERPAPI_KEY:
            print("Warning: SERPAPI_KEY not set. Some features may not work.")

        # Ensure reports directory exists
        os.makedirs(cls.REPORTS_DIR, exist_ok=True)

        return True
