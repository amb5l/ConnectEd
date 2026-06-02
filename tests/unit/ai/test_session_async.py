"""Async send / cancel behaviour for AiChatSession."""

import time

import pytest

from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QSignalSpy, QTest
from PyQt6.QtWidgets import QApplication

from ConnectEd.ai.profiles import AiProfile
from ConnectEd.ai.session import AiChatSession
from ConnectEd.ai.types import ChatEvent, ChatEventType, ChatMessage


def _spy_strings(spy : QSignalSpy) -> str:
    return "".join(args[0] for args in spy)


@pytest.fixture
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_send_is_non_blocking_and_finishes(
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

    class FakeProvider:
        def chat(self, messages, tools):
            yield ChatEvent(ChatEventType.TOKEN, content="Hello")
            yield ChatEvent(ChatEventType.DONE)

    monkeypatch.setattr(
        "ConnectEd.ai.session.getProfile",
        lambda profile_id: profile if profile_id == "1" else None,
    )
    monkeypatch.setattr(
        "ConnectEd.ai.chat_worker.getProfile",
        lambda profile_id: profile if profile_id == "1" else None,
    )
    monkeypatch.setattr(
        "ConnectEd.ai.chat_worker.createProviderForProfile",
        lambda *args, **kwargs: FakeProvider(),
    )

    class _FakeSettings:
        def get(self, path : str):
            if path == "ai/max_tool_rounds":
                return 4
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
    finished_spy = QSignalSpy(session.finished)
    token_spy    = QSignalSpy(session.assistantToken)

    session.send("hi")
    assert session.isBusy()

    timer_fired : list[bool] = []

    def on_timeout() -> None:
        timer_fired.append(True)

    QTimer.singleShot(10, on_timeout)
    deadline = time.time() + 2.0
    while time.time() < deadline:
        qapp.processEvents()
        if timer_fired:
            break
        time.sleep(0.01)

    assert timer_fired, "UI thread should process events during send"

    deadline = time.time() + 3.0
    while time.time() < deadline and len(finished_spy) == 0:
        qapp.processEvents()
        time.sleep(0.01)

    assert len(finished_spy) >= 1
    assert not session.isBusy()
    assert _spy_strings(token_spy) == "Hello"

    session.shutdown()


def test_cancel_releases_busy(
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

    class LongProvider:
        def chat(self, messages, tools):
            for _ in range(100):
                yield ChatEvent(ChatEventType.TOKEN, content="x")
                time.sleep(0.02)
            yield ChatEvent(ChatEventType.DONE)

    monkeypatch.setattr(
        "ConnectEd.ai.session.getProfile",
        lambda profile_id: profile if profile_id == "1" else None,
    )
    monkeypatch.setattr(
        "ConnectEd.ai.chat_worker.getProfile",
        lambda profile_id: profile if profile_id == "1" else None,
    )
    monkeypatch.setattr(
        "ConnectEd.ai.chat_worker.createProviderForProfile",
        lambda *args, **kwargs: LongProvider(),
    )

    class _FakeSettings:
        def get(self, path : str):
            if path == "ai/max_tool_rounds":
                return 4
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
    finished_spy = QSignalSpy(session.finished)

    session.send("hi")
    QTest.qWait(50)
    session.cancel()

    deadline = time.time() + 3.0
    while time.time() < deadline and len(finished_spy) == 0:
        qapp.processEvents()
        time.sleep(0.01)

    assert len(finished_spy) >= 1
    assert not session.isBusy()

    session.shutdown()
