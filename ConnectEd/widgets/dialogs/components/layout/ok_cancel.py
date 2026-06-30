from typing import Self, Protocol

from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QDialog

from .....core.check import checked


class OkCancelLayout(QHBoxLayout):
    _ok_button     : QPushButton
    _cancel_button : QPushButton

    @checked
    def __init__(self : Self, dialog : QDialog) -> None:
        super().__init__()
        self.addStretch(1)
        self.initOkCancelButtons(dialog)

    @checked
    def initOkCancelButtons(self : Self, dialog : QDialog) -> None:
        self._ok_button = QPushButton("OK")
        self._ok_button.clicked.connect(dialog.accept)
        self.addWidget(self._ok_button)
        self._cancel_button = QPushButton("Cancel")
        self._cancel_button.clicked.connect(dialog.reject)
        self.addWidget(self._cancel_button)
