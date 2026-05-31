"""Unit tests for AI provider display labels."""

from ConnectEd.ai.providers import providerDisplayLabel


def test_empty_provider_displays_as_no_provider() -> None:
    assert providerDisplayLabel("") == "no provider"


def test_named_provider_uses_preset_label() -> None:
    assert providerDisplayLabel("xai") == "Grok (xAI)"
    assert providerDisplayLabel("ollama") == "Ollama (local)"
