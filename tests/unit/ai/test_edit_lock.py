"""Unit tests for AiEditLock."""

import pytest

from PyQt6.QtWidgets import QApplication

from ConnectEd.ai.lock import AiEditLock


@pytest.fixture
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_acquire_and_release(qapp) -> None:
    lock = AiEditLock()
    session_a = object()
    session_b = object()

    assert lock.acquire(session_a)  # type: ignore[arg-type]
    assert lock.isLocked()
    assert lock.holder() is session_a

    assert not lock.acquire(session_b)  # type: ignore[arg-type]

    lock.release(session_a)  # type: ignore[arg-type]
    assert not lock.isLocked()
    assert lock.holder() is None

    assert lock.acquire(session_b)  # type: ignore[arg-type]
    assert lock.holder() is session_b


def test_release_ignores_non_holder(qapp) -> None:
    lock = AiEditLock()
    session_a = object()
    session_b = object()

    lock.acquire(session_a)  # type: ignore[arg-type]
    lock.release(session_b)  # type: ignore[arg-type]

    assert lock.isLocked()
    assert lock.holder() is session_a


def test_reacquire_by_holder_is_idempotent(qapp) -> None:
    lock = AiEditLock()
    session = object()

    assert lock.acquire(session)  # type: ignore[arg-type]
    assert lock.acquire(session)  # type: ignore[arg-type]
    assert lock.holder() is session

    lock.release(session)  # type: ignore[arg-type]
    assert not lock.isLocked()
