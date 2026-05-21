"""Unit tests for AI chat display titles."""

from ConnectEd.widgets.window.ai_chat.manager import chatTitles


def test_single_chat_uses_provider_label_only() -> None:
    assert chatTitles(["no provider"]) == ["no provider"]
    assert chatTitles(["ollama"]) == ["ollama"]


def test_multiple_same_provider_get_index_suffix() -> None:
    assert chatTitles(["no provider", "no provider"]) == [
        "no provider (1)",
        "no provider (2)",
    ]


def test_mixed_providers_index_per_provider_group() -> None:
    assert chatTitles(["ollama", "no provider", "ollama"]) == [
        "ollama (1)",
        "no provider",
        "ollama (2)",
    ]
