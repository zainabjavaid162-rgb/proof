"""
config.py - one place to set up the Groq LLM used by every agent.

Groq hosts open models behind a very fast API. CrewAI talks to Groq through
LiteLLM, which is why the model name starts with "groq/".
"""

# Groq retired llama-3.3-70b-versatile on 16 Aug 2026, so we use GPT-OSS.
AVAILABLE_MODELS = {
    "GPT-OSS 120B (best quality)": "openai/gpt-oss-120b",
    "GPT-OSS 20B (faster, lighter on rate limits)": "openai/gpt-oss-20b",
}
DEFAULT_MODEL_LABEL = "GPT-OSS 120B (best quality)"


def get_llm(api_key: str, model_id: str = "openai/gpt-oss-120b"):
    """Return a CrewAI LLM object connected to Groq."""
    from crewai import LLM  # imported here so the app loads fast

    return LLM(
        model=f"groq/{model_id}",  # e.g. groq/openai/gpt-oss-120b
        api_key=api_key,
        temperature=0.4,           # lower = more factual, less creative
        max_tokens=1500,           # keeps each answer short (good for free tier)
        reasoning_effort="low",    # GPT-OSS "thinks" first; low saves tokens
        timeout=120,
    )
