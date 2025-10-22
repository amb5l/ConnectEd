from typing import Self

from PyQt6.QtWidgets import QHBoxLayout, QPushButton


def okCancelLayoutStart(self : Self) -> None:
    self._ok_cancel_layout = QHBoxLayout()


def okCancelLayoutFinish(self : Self) -> None:
    self._ok_button = QPushButton("OK")
    self._ok_button.clicked.connect(self.accept)
    self._ok_cancel_layout.addWidget(self._ok_button)
    self._cancel_button = QPushButton("Cancel")
    self._cancel_button.clicked.connect(self.reject)
    self._ok_cancel_layout.addWidget(self._cancel_button)
    self._dialog_layout.addLayout(self._ok_cancel_layout)


def okCancelLayout(self : Self) -> None:
    okCancelLayoutStart(self)
    self._ok_cancel_layout.addStretch()
    okCancelLayoutFinish(self)


def okCancelNewLayout(self : Self) -> None:
    okCancelLayoutStart(self)
    self._new_button = QPushButton("New")
    self._new_button.clicked.connect(self.new)
    self._ok_cancel_layout.addWidget(self._new_button)
    self._ok_cancel_layout.addStretch()
    okCancelLayoutFinish(self)
