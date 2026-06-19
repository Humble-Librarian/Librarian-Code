from groq import Groq, RateLimitError as GroqRateLimitError, APIConnectionError
from librarian.adapter.base import LLMAdapter
from librarian.exceptions import RateLimitError, ProviderUnavailableError
from librarian.utils.config import GROQ_API_KEY


class GroqAdapter(LLMAdapter):
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
        self.model = "llama-3.3-70b-versatile"
        self.tokens_used = 0

    def complete(self, system: str, prompt: str) -> str:
        if not self.client:
            raise ProviderUnavailableError("GROQ_API_KEY not set")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=4096,
            )
            self.tokens_used += response.usage.total_tokens
            return response.choices[0].message.content
        except GroqRateLimitError:
            raise RateLimitError("Groq rate limit exceeded")
        except APIConnectionError:
            raise ProviderUnavailableError("Cannot connect to Groq")

    def is_available(self) -> bool:
        if not self.client:
            return False
        try:
            self.client.models.list()
            return True
        except Exception:
            return False
