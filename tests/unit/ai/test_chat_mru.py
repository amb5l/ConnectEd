"""Unit tests for AI chat MRU."""

import json

import pytest

from ConnectEd.ai.chat_mru import recordChatConnection
from ConnectEd.ai.profiles import AiProfile
from ConnectEd.ai.welcome import welcomeHtml


class _FakeSettings:
    def __init__(self) -> None:
        self._values : dict[str, str] = {"ai/chat_mru": "[]"}

    def get(self, path : str) -> str:
        return self._values.get(path, "")

    def set(self, path : str, value : str, *, emit : bool = True) -> None:
        self._values[path] = value


def test_record_chat_connection_prepends_and_dedupes(
    monkeypatch : pytest.MonkeyPatch,
) -> None:
    fake = _FakeSettings()
    monkeypatch.setattr("ConnectEd.ai.chat_mru.settings", lambda: fake)

    recordChatConnection("p1", "grok-3")
    recordChatConnection("p2", "gpt-4")
    recordChatConnection("p1", "grok-3")

    data = json.loads(fake.get("ai/chat_mru"))
    assert data == [
        {"profile_id": "p1", "model": "grok-3"},
        {"profile_id": "p2", "model": "gpt-4"},
    ]


def test_welcome_shows_recent_section(
    monkeypatch : pytest.MonkeyPatch,
) -> None:
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
    fake = _FakeSettings()
    fake.set(
        "ai/chat_mru",
        json.dumps([{"profile_id": "1", "model": "grok-3"}]),
    )
    monkeypatch.setattr("ConnectEd.ai.chat_mru.settings", lambda: fake)
    monkeypatch.setattr("ConnectEd.ai.welcome.loadProfiles", lambda: profiles)

    html = welcomeHtml()
    assert "Recent" in html
    assert "xAI:XAI_API_KEY:grok-3" in html
    assert "Choose a model" in html
