"""Unit tests for unbound AI chat docks (welcome state before model pick)."""

import pytest

from PyQt6.QtWidgets import QApplication

from ConnectEd.ai.session import AiChatSession
from ConnectEd.widgets.window.ai.chat.dock import AiChatDock


@pytest.fixture
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_unbound_dock_title_ignores_configured_profiles(
    qapp,
    monkeypatch : pytest.MonkeyPatch,
) -> None:
    from ConnectEd.ai.profiles import AiProfile

    profiles = [
        AiProfile(
            id            = "1",
            provider      = "xai",
            api_key_name  = "$XAI_API_KEY",
            api_key_value = "",
            url           = "",
            cached_models = ["grok-3"],
        )
    ]
    monkeypatch.setattr("ConnectEd.ai.profiles.loadProfiles", lambda: profiles)

    dock = AiChatDock.__new__(AiChatDock)
    dock._profile_id = ""
    dock._provider = ""
    dock._model = ""

    assert dock.providerLabel() == "no provider"
    assert not dock.isConnected()


def test_connected_dock_requires_profile_and_model(qapp) -> None:
    dock = AiChatDock.__new__(AiChatDock)
    dock._profile_id = "1"
    dock._provider = "xai"
    dock._model = "grok-3"
    assert dock.isConnected()

    dock._model = ""
    assert not dock.isConnected()


def test_unbound_session_has_no_provider(
    qapp,
    monkeypatch : pytest.MonkeyPatch,
) -> None:
    from ConnectEd.ai.profiles import AiProfile

    profiles = [
        AiProfile(
            id            = "1",
            provider      = "xai",
            api_key_name  = "$XAI_API_KEY",
            api_key_value = "secret",
            url           = "",
            cached_models = ["grok-3"],
        )
    ]
    monkeypatch.setattr("ConnectEd.ai.profiles.loadProfiles", lambda: profiles)

    class FakeDock:
        def profileId(self) -> str:
            return ""

        def providerKey(self) -> str:
            return ""

        def model(self) -> str:
            return ""

    class FakeWindow:
        def aiManager(self):
            return None

    session = AiChatSession(FakeWindow(), FakeDock())  # type: ignore[arg-type]
    assert session._provider is None
