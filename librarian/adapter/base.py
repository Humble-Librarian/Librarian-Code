from abc import ABC, abstractmethod
from typing import Iterator


class LLMAdapter(ABC):
    @abstractmethod
    def complete(self, system: str, prompt: str) -> str:
        pass

    @abstractmethod
    def complete_stream(self, system: str, prompt: str) -> Iterator[str]:
        yield ""

    @abstractmethod
    def is_available(self) -> bool:
        pass
