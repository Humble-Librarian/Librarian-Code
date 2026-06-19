import pytest
from unittest.mock import MagicMock, patch
from librarian.adapter.groq_adapter import GroqAdapter
from librarian.adapter.openrouter_adapter import OpenRouterAdapter
from librarian.exceptions import RateLimitError, ProviderUnavailableError


class TestGroqAdapter:
    @patch("librarian.adapter.groq_adapter.GROQ_API_KEY", "test-key")
    @patch("librarian.adapter.groq_adapter.Groq")
    def test_complete_success(self, mock_groq):
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="hello"))]
        mock_response.usage.total_tokens = 10
        mock_client.chat.completions.create.return_value = mock_response

        adapter = GroqAdapter()
        result = adapter.complete("system", "prompt")
        assert result == "hello"
        assert adapter.tokens_used == 10

    @patch("librarian.adapter.groq_adapter.GROQ_API_KEY", "test-key")
    @patch("librarian.adapter.groq_adapter.Groq")
    def test_rate_limit_raises(self, mock_groq):
        from groq import RateLimitError as GroqRateLimitError
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        mock_client.chat.completions.create.side_effect = GroqRateLimitError(
            message="rate limited", response=MagicMock(status_code=429), body=None
        )

        adapter = GroqAdapter()
        with pytest.raises(RateLimitError):
            adapter.complete("system", "prompt")

    def test_no_api_key_raises(self):
        with patch("librarian.adapter.groq_adapter.GROQ_API_KEY", None):
            adapter = GroqAdapter()
            with pytest.raises(ProviderUnavailableError):
                adapter.complete("system", "prompt")


class TestOpenRouterAdapter:
    @patch("librarian.adapter.openrouter_adapter.OPENROUTER_API_KEY", "test-key")
    @patch("librarian.adapter.openrouter_adapter.httpx.Client")
    def test_complete_success(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "response"}}],
            "usage": {"total_tokens": 20},
        }
        mock_client.post.return_value = mock_resp

        adapter = OpenRouterAdapter()
        result = adapter.complete("system", "prompt")
        assert result == "response"
        assert adapter.tokens_used == 20

    def test_no_api_key_raises(self):
        with patch("librarian.adapter.openrouter_adapter.OPENROUTER_API_KEY", None):
            adapter = OpenRouterAdapter()
            with pytest.raises(ProviderUnavailableError):
                adapter.complete("system", "prompt")
