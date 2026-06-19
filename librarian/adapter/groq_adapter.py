from librarian.adapter.base import LLMAdapter
from librarian.exceptions import RateLimitError, ProviderUnavailableError


class GroqAdapter(LLMAdapter):
    def complete(self, system: str, prompt: str) -> str:
        raise NotImplementedError

    def is_available(self) -> bool:
        raise NotImplementedError
