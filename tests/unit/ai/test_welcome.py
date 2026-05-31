"""Unit tests for AI chat welcome HTML."""

import pytest

from ConnectEd.ai.welcome import chatUrl, parseChatLink, settingsUrl, welcomeHtml


def test_welcome_includes_settings_link_and_vendors(
    monkeypatch : pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("ConnectEd.ai.welcome.loadProfiles", lambda: [])
    html = welcomeHtml()
    assert settingsUrl() in html
    assert "https://ollama.com/" in html
    assert "demo" not in html


def test_welcome_lists_configured_profiles(monkeypatch : pytest.MonkeyPatch) -> None:
    from ConnectEd.ai.profiles import AiProfile

    profiles = [
        AiProfile(
            id            = "1",
            provider      = "xai",
            api_key_name  = "$XAI_API_KEY",
            api_key_value = "",
            url           = "",
            cached_models = ["grok-3", "grok-2"],
        )
    ]
    monkeypatch.setattr("ConnectEd.ai.welcome.loadProfiles", lambda: profiles)
    monkeypatch.setattr("ConnectEd.ai.chat_mru._loadEntries", lambda: [])
    html = welcomeHtml()
    assert "xAI:XAI_API_KEY:grok-3" in html
    assert "xAI:XAI_API_KEY:grok-2" in html
    assert chatUrl("1", "grok-3") in html
    assert chatUrl("1", "grok-2") in html
    assert "AI Profiles" in html
    assert "Choose a model" in html


def test_chat_link_round_trip() -> None:
    url = chatUrl("profile-1", "grok-3")
    parsed = parseChatLink(url)
    assert parsed == ("profile-1", "grok-3")


def test_parse_chat_link_rejects_other_schemes() -> None:
    assert parseChatLink("https://example.com") is None
    assert parseChatLink("connected://ai/settings") is None
