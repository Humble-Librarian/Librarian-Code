from typing import Iterator
from librarian.adapter.groq_adapter import GroqAdapter
from librarian.adapter.openrouter_adapter import OpenRouterAdapter
from librarian.exceptions import RateLimitError, ProviderUnavailableError
from librarian.utils.logger import log_warning


def get_response(system: str, prompt: str) -> tuple[str, str, int]:
    primary = GroqAdapter()
    fallback = OpenRouterAdapter()

    try:
        response = primary.complete(system, prompt)
        return response, "groq", primary.tokens_used
    except (RateLimitError, ProviderUnavailableError) as e:
        log_warning(f"{e} — switching to OpenRouter")
        response = fallback.complete(system, prompt)
        return response, "openrouter", fallback.tokens_used


def get_response_stream(system: str, prompt: str) -> tuple[Iterator[str], str]:
    primary = GroqAdapter()
    fallback = OpenRouterAdapter()

    try:
        _ = primary.complete_stream(system, prompt)
        return primary.complete_stream(system, prompt), "groq"
    except (RateLimitError, ProviderUnavailableError) as e:
        log_warning(f"{e} — switching to OpenRouter")
        return fallback.complete_stream(system, prompt), "openrouter"
