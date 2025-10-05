import re, traceback
from config import Config
AZURE_CFG = Config.AZURE_CFG
from openai import AzureOpenAI
from fastapi import Form

def _is_azure_configured() -> bool:
    return bool(AZURE_CFG.get("api_key") and AZURE_CFG.get("endpoint") and AZURE_CFG.get("deployment_name"))

def init_azure_client():
    if not _is_azure_configured():
        return None
    try:
        return AzureOpenAI(
            api_key=AZURE_CFG["api_key"],
            azure_endpoint=AZURE_CFG["endpoint"],
            api_version=AZURE_CFG["api_version"],
        )
    except Exception as e:
        print("Azure client init failed:", e)
        return None

def call_azure_chat(prompt: str, max_tokens: int = 1000, temperature: float = 0.2) -> str:
    if _is_azure_configured():
        try:
            client = init_azure_client()
            response = client.chat.completions.create(
                model=AZURE_CFG["deployment_name"],
                messages=[
                    {"role": "system", "content": "You are a helpful academic assistant. Provide citations where appropriate."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            print("Azure call error:", e)
            traceback.print_exc()

    # fallback summarizer
    lines = [l.strip() for l in re.split(r'\n+', prompt) if l.strip()]
    summary = " ".join(lines[:6])
    if len(summary) > 200:
        summary = summary[:200] + "..."
    return f"(Fallback summary — Azure not configured)\n{summary}"
