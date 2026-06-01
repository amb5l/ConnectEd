"""Handshake on AI chat connect."""

import pytest

from PyQt6.QtWidgets import QApplication

from ConnectEd.ai.prompt import CONNECTION_HANDSHAKE_USER
from ConnectEd.ai.profiles import AiProfile
from ConnectEd.ai.session import AiChatSession
from ConnectEd.ai.types import ChatEvent, ChatEventType


@pytest.fixture
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_run_handshake_delivers_system_prompt_and_greeting(
    qapp,
    monkeypatch : pytest.MonkeyPatch,
) -> None:
    profile = AiProfile(
        id            = "1",
        provider      = "xai",
        api_key_name  = "$XAI_API_KEY",
        api_key_value = "secret",
        url           = "",
    )
    tokens : list[str] = []

    class FakeProvider:
        def chat(self, messages, tools):
            assert tools == []
            assert messages[0].role == "system"
            assert "Available tools" in messages[0].content
            assert messages[-1].role == "user"
            assert messages[-1].content == CONNECTION_HANDSHAKE_USER
            yield ChatEvent(ChatEventType.TOKEN, content="I am ready to help with ConnectEd.")
            yield ChatEvent(ChatEventType.DONE)

    monkeypatch.setattr(
        "ConnectEd.ai.session.getProfile",
        lambda profile_id: profile if profile_id == "1" else None,
    )
    monkeypatch.setattr(
        "ConnectEd.ai.session.createProviderForProfile",
        lambda *args, **kwargs: FakeProvider(),
    )

    class _FakeSettings:
        def get(self, path : str) -> str:
            return ""

    monkeypatch.setattr("ConnectEd.ai.prompt.settings", lambda: _FakeSettings())
    monkeypatch.setattr("ConnectEd.ai.session.settings", lambda: _FakeSettings())

    class FakeDock:
        def profileId(self) -> str:
            return "1"

        def providerKey(self) -> str:
            return "xai"

        def model(self) -> str:
            return "grok-3"

    class FakeWindow:
        def aiManager(self):
            return None

    session = AiChatSession(FakeWindow(), FakeDock())  # type: ignore[arg-type]
    session.assistantToken.connect(tokens.append)
    session.runHandshake()
    assert "".join(tokens) == "I am ready to help with ConnectEd."
    assert session._messages[-1].role == "assistant"
    assert "ConnectEd" in session._messages[-1].content
