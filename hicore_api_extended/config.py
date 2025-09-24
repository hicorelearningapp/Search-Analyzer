import os

AZURE_CFG = {
    "api_key": os.getenv("AZURE_OPENAI_API_KEY", "G3AKaFyet7mSiT9cDWoxol7bpTfQ9U91IrWUiD1mvgNtNL37KNfEJQQJ99BHACHYHv6XJ3w3AAAAACOGaDFv"),
    "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", "https://hicor-megtc6ig-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2025-01-01-preview"),
    "api_version": "2025-01-01-preview",
    "deployment_name": "gpt-4"
}

SERPAPI_KEY = os.getenv("SERPAPI_KEY", "90b40f...")
SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
SEMANTIC_SCHOLAR_AUTHOR_URL = "https://api.semanticscholar.org/graph/v1/author/search"