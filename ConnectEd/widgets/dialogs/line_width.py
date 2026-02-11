from typing import Self

from PyQt6.QtWidgets import QWidget, QDialog, QLineEdit, \
                            QVBoxLayout, QHBoxLayout, QLabel

from .components.layout.ok_cancel import OkCancelLayout


class LineWidthDialog(QDialog):
    def __init__(
        self    : Self,
        initial : float | int | None = None,
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Line Width")
        self.dialog_layout = QVBoxLayout()
        # width section
        self.width_layout = QHBoxLayout()
        self.width_label = QLabel("Width:")
        self.width_layout.addWidget(self.width_label)
        self.width_input = QLineEdit("" if initial is None else str(initial))
        self.width_layout.addWidget(self.width_input)
        self.dialog_layout.addLayout(self.width_layout)
        # ok/cancel section
        self._ok_cancel_layout = OkCancelLayout(self)
        self.dialog_layout.addLayout(self._ok_cancel_layout)
        # set layout
        self.setLayout(self.dialog_layout)

    def getChoice(self : Self) -> float | None:
        try:
            return float(self.width_input.text())
        except ValueError:
            return None
