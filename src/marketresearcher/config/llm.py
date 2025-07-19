# llm_config.py
from crewai import LLM
import os
from retry_llm import RetryLLM

# Using models that are currently available and working
# Based on the debug output, these models are responding properly

research_llm = RetryLLM(
    model="mistralai/mistral-small-3.2-24b-instruct:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

comparison_llm = RetryLLM(
    model="moonshotai/kimi-k2:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

narrative_llm = RetryLLM(
    model="google/gemma-3n-e2b-it:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

strategic_llm = RetryLLM(
    model="tngtech/deepseek-r1t2-chimera:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

formatting_llm = RetryLLM(
    model="moonshotai/kimi-dev-72b:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
