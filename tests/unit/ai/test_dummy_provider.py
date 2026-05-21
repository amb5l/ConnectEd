"""Unit tests for the dummy AI provider and driver scaffolding."""

import json

from ConnectEd.ai.driver import AiDriver
from ConnectEd.ai.providers.dummy import DummyProvider
from ConnectEd.ai.types import ChatEventType, ChatMessage
from ConnectEd.ai.welcome import settingsUrl, welcomeHtml


def test_nobody_home_returns_fixed_payload() -> None:
    driver = AiDriver.__new__(AiDriver)
    result = driver.nobodyHome()
    assert result == {"ok": True, "message": "Nobody home."}


def test_welcome_includes_settings_link_and_vendors() -> None:
    html = welcomeHtml()
    assert settingsUrl() in html
    assert "https://ollama.com/" in html
    assert "https://platform.openai.com/" in html
    assert "demo" in html


def test_dummy_provider_replies_with_configure_hint() -> None:
    provider = DummyProvider()
    events = list(provider.chat([ChatMessage("user", "hello")], []))
    tokens = [e.content for e in events if e.type == ChatEventType.TOKEN]
    assert len(tokens) == 1
    assert "AI Settings" in tokens[0]
    assert not any(e.type == ChatEventType.TOOL_CALL for e in events)


def test_dummy_provider_demo_invokes_nobody_home_then_replies() -> None:
    provider = DummyProvider()
    tools = []

    first_turn = list(provider.chat([ChatMessage("user", "demo")], tools))
    tool_events = [e for e in first_turn if e.type == ChatEventType.TOOL_CALL]
    assert len(tool_events) == 1
    assert tool_events[0].tool_call is not None
    assert tool_events[0].tool_call.name == "nobodyHome"

    tool_result = json.dumps({"ok": True, "message": "Nobody home."})
    second_turn = list(
        provider.chat(
            [
                ChatMessage("user", "demo"),
                ChatMessage("tool", tool_result, tool_name="nobodyHome"),
            ],
            tools,
        )
    )
    tokens = [e.content for e in second_turn if e.type == ChatEventType.TOKEN]
    assert any("Nobody home." in token for token in tokens)
