"""Unit tests for provider default API key names."""

from ConnectEd.ai.providers import defaultApiKeyName, defaultBaseUrl


def test_default_api_key_names() -> None:
    assert defaultApiKeyName("xai") == "$XAI_API_KEY"
    assert defaultApiKeyName("anthropic") == "$ANTHROPIC_API_KEY"
    assert defaultApiKeyName("openai") == "$OPENAI_API_KEY"
    assert defaultApiKeyName("ollama") == ""
    assert defaultApiKeyName("openai_compatible") == "$OPENAI_API_KEY"


def test_default_base_urls() -> None:
    assert defaultBaseUrl("xai") == "https://api.x.ai/v1"
    assert defaultBaseUrl("ollama") == "http://localhost:11434/v1"
