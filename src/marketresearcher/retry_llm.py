# retry_llm.py
import time
import random
from crewai import LLM
import httpx
from openai import RateLimitError, APIError

class RetryLLM(LLM):
    def call(self, messages, **kwargs):
        max_retries = 2  # Reduced retries to avoid long waits
        base_delay = 15  # Increased base delay
        
        for attempt in range(max_retries):
            try:
                response = super().call(messages, **kwargs)
                if not response or response.strip() == "":
                    raise ValueError("Empty response")
                return response
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limit
                    # Exponential backoff with jitter for rate limits
                    delay = base_delay * (2 ** attempt) + random.uniform(1, 5)
                    print(f"⚠️ Rate limit hit. Retry {attempt+1}/{max_retries} in {delay:.1f}s")
                    time.sleep(delay)
                    continue
                else:
                    # For other HTTP errors, don't retry
                    raise e
                    
            except (RateLimitError, APIError) as e:
                # Handle OpenAI specific rate limits
                delay = base_delay * (2 ** attempt) + random.uniform(1, 5)
                print(f"⚠️ API limit hit. Retry {attempt+1}/{max_retries} in {delay:.1f}s")
                time.sleep(delay)
                continue
                
            except ValueError as e:
                if "Empty response" in str(e):
                    delay = base_delay + random.uniform(1, 3)
                    print(f"⚠️ Empty response. Retry {attempt+1}/{max_retries} in {delay:.1f}s")
                    time.sleep(delay)
                    continue
                else:
                    raise e
                    
            except Exception as e:
                print(f"❌ Unexpected error: {type(e).__name__}: {str(e)}")
                raise e
        
        raise RuntimeError(f"💥 Max retries ({max_retries}) exceeded on LLM call")
