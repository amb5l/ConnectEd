"""Unit tests for AI chat display titles."""

from ConnectEd.widgets.window.ai.chat.manager import chatTitle, chatTitles


def test_chat_title_single_session() -> None:
    assert chatTitle("ollama") == "AI Chat [ollama]"
    assert chatTitle("no provider") == "AI Chat [no provider]"


def test_chat_title_indexed_session() -> None:
    assert chatTitle("ollama", 2) == "AI Chat [ollama] (2)"


def test_named_provider_uses_preset_label() -> None:
    assert chatTitles(["xAI/ConnectEdDev/grok-3"]) == [
        "AI Chat [xAI/ConnectEdDev/grok-3]"
    ]
    assert chatTitles(["Ollama/local"]) == ["AI Chat [Ollama/local]"]


def test_multiple_same_provider_get_index_suffix() -> None:
    assert chatTitles(["no provider", "no provider"]) == [
        "AI Chat [no provider] (1)",
        "AI Chat [no provider] (2)",
    ]


def test_mixed_providers_index_per_provider_group() -> None:
    assert chatTitles(["Ollama/local", "no provider", "Ollama/local"]) == [
        "AI Chat [Ollama/local] (1)",
        "AI Chat [no provider]",
        "AI Chat [Ollama/local] (2)",
    ]
