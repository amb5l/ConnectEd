"""Unit tests for AI chat display titles."""

from ConnectEd.widgets.window.ai_chat.manager import chatTitle, chatTitles


def test_chat_title_single_session() -> None:
    assert chatTitle("ollama") == "AI Chat [ollama]"
    assert chatTitle("no provider") == "AI Chat [no provider]"


def test_chat_title_indexed_session() -> None:
    assert chatTitle("ollama", 2) == "AI Chat [ollama] (2)"


def test_single_chat_uses_provider_label_only() -> None:
    assert chatTitles(["no provider"]) == ["AI Chat [no provider]"]
    assert chatTitles(["ollama"]) == ["AI Chat [ollama]"]


def test_multiple_same_provider_get_index_suffix() -> None:
    assert chatTitles(["no provider", "no provider"]) == [
        "AI Chat [no provider] (1)",
        "AI Chat [no provider] (2)",
    ]


def test_mixed_providers_index_per_provider_group() -> None:
    assert chatTitles(["ollama", "no provider", "ollama"]) == [
        "AI Chat [ollama] (1)",
        "AI Chat [no provider]",
        "AI Chat [ollama] (2)",
    ]
