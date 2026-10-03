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


def _fix_groq_cache_breakpoint():
    """
    Work around a known CrewAI bug (github.com/crewAIInc/crewAI/issues/5886):
    CrewAI adds a 'cache_breakpoint' field to messages (an Anthropic-only feature)
    and Groq rejects it. We switch the marker off AND remove it right before the
    request is sent, so the fix holds even if CrewAI changes slightly.
    Safe to delete once CrewAI ships the official fix.
    """
    import crewai.llms.cache as crewai_cache
    import litellm

    crewai_cache.mark_cache_breakpoint = lambda message: message

    def clean(messages):
        return [{k: v for k, v in m.items() if k != "cache_breakpoint"}
                if isinstance(m, dict) else m for m in messages]

    for name in ("completion", "acompletion"):
        original = getattr(litellm, name)
        if getattr(original, "_proof_fixed", False):
            continue  # already patched (Streamlit reruns this file often)

        def wrapper(*args, _original=original, **kwargs):
            if kwargs.get("messages"):
                kwargs["messages"] = clean(kwargs["messages"])
            return _original(*args, **kwargs)

        wrapper._proof_fixed = True
        setattr(litellm, name, wrapper)


def get_llm(api_key: str, model_id: str = "openai/gpt-oss-120b"):
    """Return a CrewAI LLM object connected to Groq."""
    from crewai import LLM  # imported here so the app loads fast

    _fix_groq_cache_breakpoint()

    return LLM(
        model=f"groq/{model_id}",  # e.g. groq/openai/gpt-oss-120b
        api_key=api_key,
        temperature=0.4,           # lower = more factual, less creative
        max_tokens=1500,           # keeps each answer short (good for free tier)
        reasoning_effort="low",    # GPT-OSS "thinks" first; low saves tokens
        timeout=120,
    )
