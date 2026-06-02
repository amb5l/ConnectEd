"""Handshake on AI chat connect."""

import pytest

from PyQt6.QtWidgets import QApplication

from ConnectEd.ai.prompt import connectionReadyMessage
from ConnectEd.ai.profiles import AiProfile
from ConnectEd.ai.session import AiChatSession


@pytest.fixture
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_connection_ready_message_uses_model_name() -> None:
    assert connectionReadyMessage("grok-3") == "grok-3 is ready."
    assert connectionReadyMessage("  ") == "AI is ready."


def test_run_handshake_shows_ready_without_provider_call(
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

    monkeypatch.setattr(
        "ConnectEd.ai.session.getProfile",
        lambda profile_id: profile if profile_id == "1" else None,
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
    assert tokens == ["grok-3 is ready."]
    assert len(session._messages) == 1
    assert session._messages[0].role == "system"
    session.shutdown()
