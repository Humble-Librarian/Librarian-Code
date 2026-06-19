from librarian.adapter.base import LLMAdapter
from librarian.exceptions import RateLimitError, ProviderUnavailableError


class OpenRouterAdapter(LLMAdapter):
    def complete(self, system: str, prompt: str) -> str:
        raise NotImplementedError

    def is_available(self) -> bool:
        raise NotImplementedError
