from typing import Self

from PyQt6.QtWidgets import \
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from ...core.check import checked


class UnsavedChangesDialog(QDialog):
    _dialog_layout  : QVBoxLayout
    _text_layout    : QHBoxLayout
    _text_label     : QLabel
    _buttons_layout : QHBoxLayout
    _commit_button  : QPushButton
    _discard_button : QPushButton
    _cancel_button  : QPushButton
    _decision       : bool | None  # True = commit, False = discard

    @checked
    def __init__(
        self   : Self,
        text   : str,
        parent : QWidget
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Unsaved Changes")
        self._decision = None
        self._dialog_layout = QVBoxLayout(self)
        self._text_layout = QHBoxLayout()
        self._text_label = QLabel(text)
        self._text_layout.addWidget(self._text_label)
        self._dialog_layout.addLayout(self._text_layout)
        self._buttons_layout = QHBoxLayout()
        self._commit_button = QPushButton("Commit")
        self._commit_button.setAutoDefault(False)
        self._commit_button.setDefault(False)
        self._commit_button.clicked.connect(self._onCommitClicked)
        self._buttons_layout.addWidget(self._commit_button)
        self._discard_button = QPushButton("Discard")
        self._discard_button.setAutoDefault(False)
        self._discard_button.setDefault(False)
        self._discard_button.clicked.connect(self._onDiscardClicked)
        self._buttons_layout.addWidget(self._discard_button)
        self._cancel_button = QPushButton("Cancel")
        self._cancel_button.setDefault(True)
        self._cancel_button.clicked.connect(self._onCancelClicked)
        self._buttons_layout.addWidget(self._cancel_button)
        self._dialog_layout.addLayout(self._buttons_layout)
        self.setLayout(self._dialog_layout)

    def commit(self : Self) -> bool:
        return self._decision is True

    def discard(self : Self) -> bool:
        return self._decision is False

    def _onCommitClicked(self : Self) -> None:
        self._decision = True
        self.accept()

    def _onDiscardClicked(self : Self) -> None:
        self._decision = False
        self.accept()

    def _onCancelClicked(self : Self) -> None:
        self._decision = None
        self.reject()
