"""Unit tests for AI provider display labels."""

from ConnectEd.ai.providers import providerDisplayLabel


def test_dummy_provider_displays_as_no_provider() -> None:
    assert providerDisplayLabel("dummy") == "no provider"
    assert providerDisplayLabel("") == "no provider"


def test_named_provider_uses_registry_key() -> None:
    assert providerDisplayLabel("ollama") == "ollama"
