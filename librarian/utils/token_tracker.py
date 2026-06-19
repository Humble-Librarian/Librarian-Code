class TokenTracker:
    def __init__(self):
        self.session_tokens = {"groq": 0, "openrouter": 0}

    def add(self, provider: str, tokens: int):
        if provider in self.session_tokens:
            self.session_tokens[provider] += tokens

    def total(self) -> int:
        return sum(self.session_tokens.values())

    def report(self) -> str:
        return f"groq: {self.session_tokens['groq']} · openrouter: {self.session_tokens['openrouter']}"


tracker = TokenTracker()
