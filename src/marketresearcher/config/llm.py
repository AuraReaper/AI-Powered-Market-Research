# llm_config.py
from crewai import LLM
import os


research_llm = LLM(
    model="openrouter/mistralai/mistral-small-3.2-24b-instruct:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

comparison_llm = LLM(
    model="openrouter/moonshotai/kimi-k2:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

narrative_llm = LLM(
    model="openrouter/meta-llama/llama-3.3-70b-instruct:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

strategic_llm = LLM(
    model="openrouter/tngtech/deepseek-r1t-chimera:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

formatting_llm = LLM(
    model="openrouter/moonshotai/kimi-dev-72b:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)