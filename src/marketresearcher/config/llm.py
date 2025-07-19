# llm_config.py
from crewai import LLM
import os
from retry_llm import RetryLLM

research_llm = RetryLLM(
    model="openrouter/google/gemini-2.0-flash-exp:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

comparison_llm = RetryLLM(
    model="openrouter/tngtech/deepseek-r1t2-chimera:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

narrative_llm = RetryLLM(
    model="openrouter/meta-llama/llama-3.3-70b-instruct:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

strategic_llm = RetryLLM(
    model="openrouter/tngtech/deepseek-r1t-chimera:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

formatting_llm = RetryLLM(
    model="openrouter/moonshotai/kimi-dev-72b:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)