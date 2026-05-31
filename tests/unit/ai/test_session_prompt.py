"""Unit tests for system prompt seeding in AiChatSession."""

import pytest

from PyQt6.QtWidgets import QApplication

from ConnectEd.ai.profiles import AiProfile
from ConnectEd.ai.session import AiChatSession


@pytest.fixture
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_connected_session_seeds_system_prompt(
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
    monkeypatch.setattr(
        "ConnectEd.ai.session.getProfile",
        lambda profile_id: profile if profile_id == "1" else None,
    )
    monkeypatch.setattr(
        "ConnectEd.ai.session.createProviderForProfile",
        lambda *args, **kwargs: object(),
    )

    class _FakeSettings:
        def get(self, path : str) -> str:
            return ""

    monkeypatch.setattr("ConnectEd.ai.prompt.settings", lambda: _FakeSettings())

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
    assert len(session._messages) == 1
    assert session._messages[0].role == "system"
    assert "ConnectEd" in session._messages[0].content
    assert "**ping**" in session._messages[0].content
