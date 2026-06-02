"""Unit tests for async AI provider worker."""

import time

import pytest

from PyQt6.QtCore import Q_ARG, QMetaObject, Qt, QThread, QTimer
from PyQt6.QtTest import QSignalSpy, QTest
from PyQt6.QtWidgets import QApplication

from ConnectEd.ai.chat_worker import AiChatProviderWorker, copyMessages
from ConnectEd.ai.profiles import AiProfile
from ConnectEd.ai.types import ChatEvent, ChatEventType, ChatMessage, ToolCall


def _spy_strings(spy : QSignalSpy) -> str:
    return "".join(args[0] for args in spy)


@pytest.fixture
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_copy_messages_is_independent() -> None:
    original = [ChatMessage("user", "hello")]
    copied   = copyMessages(original)
    copied[0].content = "changed"
    assert original[0].content == "hello"


def test_worker_streams_tokens_off_main_thread(
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

    class SlowProvider:
        def chat(self, messages, tools):
            yield ChatEvent(ChatEventType.TOKEN, content="a")
            time.sleep(0.05)
            yield ChatEvent(ChatEventType.TOKEN, content="b")
            yield ChatEvent(ChatEventType.DONE)

    monkeypatch.setattr(
        "ConnectEd.ai.chat_worker.getProfile",
        lambda profile_id: profile if profile_id == "1" else None,
    )
    monkeypatch.setattr(
        "ConnectEd.ai.chat_worker.createProviderForProfile",
        lambda *args, **kwargs: SlowProvider(),
    )

    thread = QThread()
    worker = AiChatProviderWorker()
    worker.moveToThread(thread)
    thread.start()

    token_spy = QSignalSpy(worker.token)
    turn_spy  = QSignalSpy(worker.turnFinished)

    QMetaObject.invokeMethod(
        worker,
        "runTurn",
        Qt.ConnectionType.QueuedConnection,
        Q_ARG(str, "1"),
        Q_ARG(str, "grok-3"),
        Q_ARG(list, [ChatMessage("user", "hi")]),
        Q_ARG(list, []),
    )

    timer_fired : list[bool] = []

    def on_timeout() -> None:
        timer_fired.append(True)

    QTimer.singleShot(10, on_timeout)
    deadline = time.time() + 2.0
    while time.time() < deadline and not timer_fired:
        qapp.processEvents()
        time.sleep(0.01)

    assert timer_fired, "event loop should stay responsive while worker streams"

    deadline = time.time() + 3.0
    while time.time() < deadline and len(turn_spy) == 0:
        qapp.processEvents()
        time.sleep(0.01)

    assert len(turn_spy) == 1
    assert turn_spy[0][0] == "ab"
    assert turn_spy[0][1] == []
    assert _spy_strings(token_spy) == "ab"

    thread.quit()
    thread.wait(5000)


def test_worker_cancel_emits_cancelled(
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
            while True:
                yield ChatEvent(ChatEventType.TOKEN, content="x")
                time.sleep(0.05)

    monkeypatch.setattr(
        "ConnectEd.ai.chat_worker.getProfile",
        lambda profile_id: profile if profile_id == "1" else None,
    )
    monkeypatch.setattr(
        "ConnectEd.ai.chat_worker.createProviderForProfile",
        lambda *args, **kwargs: LongProvider(),
    )

    thread = QThread()
    worker = AiChatProviderWorker()
    worker.moveToThread(thread)
    thread.start()

    cancel_spy = QSignalSpy(worker.cancelled)
    token_spy  = QSignalSpy(worker.token)

    QMetaObject.invokeMethod(
        worker,
        "runTurn",
        Qt.ConnectionType.QueuedConnection,
        Q_ARG(str, "1"),
        Q_ARG(str, "grok-3"),
        Q_ARG(list, [ChatMessage("user", "hi")]),
        Q_ARG(list, []),
    )
    deadline = time.time() + 2.0
    while time.time() < deadline and len(token_spy) == 0:
        qapp.processEvents()
        time.sleep(0.01)

    worker.requestCancel()

    deadline = time.time() + 3.0
    while time.time() < deadline and len(cancel_spy) == 0:
        qapp.processEvents()
        time.sleep(0.01)

    assert len(cancel_spy) >= 1

    thread.quit()
    thread.wait(5000)
