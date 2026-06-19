import httpx
from librarian.adapter.base import LLMAdapter
from librarian.exceptions import RateLimitError, ProviderUnavailableError
from librarian.utils.config import OPENROUTER_API_KEY

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "qwen/qwen3-coder:free"
HEADERS = {
    "HTTP-Referer": "https://github.com/Humble-Librarian/librarian-code",
    "X-Title": "librarian",
}


class OpenRouterAdapter(LLMAdapter):
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.tokens_used = 0

    def complete(self, system: str, prompt: str) -> str:
        if not self.api_key:
            raise ProviderUnavailableError("OPENROUTER_API_KEY not set")
        headers = {**HEADERS, "Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 4096,
        }
        try:
            with httpx.Client(timeout=60) as client:
                resp = client.post(ENDPOINT, headers=headers, json=payload)
            if resp.status_code == 429:
                raise RateLimitError("OpenRouter rate limit exceeded")
            resp.raise_for_status()
            data = resp.json()
            self.tokens_used += data.get("usage", {}).get("total_tokens", 0)
            return data["choices"][0]["message"]["content"]
        except httpx.ConnectError:
            raise ProviderUnavailableError("Cannot connect to OpenRouter")
        except httpx.TimeoutException:
            raise ProviderUnavailableError("OpenRouter request timed out")

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            headers = {**HEADERS, "Authorization": f"Bearer {self.api_key}"}
            with httpx.Client(timeout=10) as client:
                resp = client.get("https://openrouter.ai/api/v1/models", headers=headers)
            return resp.status_code == 200
        except Exception:
            return False
