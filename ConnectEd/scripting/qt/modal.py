"""Blocking modal dialogs (schedule + opener + onModal callback)."""

from collections.abc import Callable
from typing import Any, Self

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QLabel, QMessageBox, QWidget


def processEvents() -> None:
    QApplication.processEvents()


def schedule(callback : Any) -> None:
    QTimer.singleShot(0, callback)


def activeModal() -> QWidget | None:
    return QApplication.activeModalWidget()


def modalBodyText(modal : QWidget) -> str:
    if isinstance(modal, QMessageBox):
        return modal.text()
    return " ".join(label.text() for label in modal.findChildren(QLabel))


def withModal(opener : Callable[[], None], onModal : Callable[[], None]) -> None:
    failures : list[BaseException] = []

    def wrapped() -> None:
        try:
            onModal()
        except BaseException as e:
            failures.append(e)

    schedule(wrapped)
    opener()
    processEvents()
    if failures:
        raise failures[0]


class ModalMixin:
    def activeModal(self : Self) -> QWidget | None:
        return activeModal()

    def modalBodyText(self : Self, modal : QWidget) -> str:
        return modalBodyText(modal)

    def withModal(
        self    : Self,
        opener  : Callable[[], None],
        onModal : Callable[[], None],
    ) -> None:
        withModal(opener, onModal)
