"""Unit tests for edit lock behaviour on AiChatSession."""

import pytest

from PyQt6.QtWidgets import QApplication

from ConnectEd.ai.lock import AiEditLock


@pytest.fixture
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_second_session_rejected_while_lock_held(qapp) -> None:
    lock = AiEditLock()
    session_a = object()
    session_b = object()

    assert lock.acquire(session_a)  # type: ignore[arg-type]
    assert not lock.acquire(session_b)  # type: ignore[arg-type]

    lock.release(session_a)  # type: ignore[arg-type]
    assert lock.acquire(session_b)  # type: ignore[arg-type]


def test_release_on_destroy_clears_holder(qapp) -> None:
    lock = AiEditLock()
    session = object()

    lock.acquire(session)  # type: ignore[arg-type]
    lock.release(session)  # type: ignore[arg-type]

    assert not lock.isLocked()
