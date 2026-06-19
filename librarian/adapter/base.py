from abc import ABC, abstractmethod


class LLMAdapter(ABC):
    @abstractmethod
    def complete(self, system: str, prompt: str) -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass
