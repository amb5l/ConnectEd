"""Exclusive editing lease — one AI chat agent loop at a time."""

from typing import TYPE_CHECKING, Self

from PyQt6.QtCore import QObject, pyqtSignal

from ..core.check import checked

if TYPE_CHECKING:
    from .session import AiChatSession


class AiEditLock(QObject):
    lockChanged = pyqtSignal()

    _holder : "AiChatSession | None"

    @checked
    def __init__(self : Self, parent : QObject | None = None) -> None:
        super().__init__(parent)
        self._holder = None

    @checked
    def holder(self : Self) -> "AiChatSession | None":
        return self._holder

    @checked
    def isLocked(self : Self) -> bool:
        return self._holder is not None

    @checked
    def acquire(self : Self, session : "AiChatSession") -> bool:
        if self._holder is session:
            return True
        if self._holder is not None:
            return False
        self._holder = session
        self.lockChanged.emit()
        return True

    @checked
    def release(self : Self, session : "AiChatSession") -> None:
        if self._holder is not session:
            return
        self._holder = None
        self.lockChanged.emit()
