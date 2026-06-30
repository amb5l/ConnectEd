from typing import Self

from PyQt6.QtWidgets import QWidget, QSpinBox

from ....core.check import checked


class CustomSpinBox(QSpinBox):
    """
    A QSpinBox that displays "N/A" (or any custom text) when disabled.
    """
    # class attributes
    _DISABLED_TEXT = "N/A"

    # instance attributes
    _value   : int | None

    @checked
    def __init__(
        self   : Self,
        value  : int | None = None,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._value = self.value()

    @checked
    def setEnabled(self : Self, a0 : bool) -> None:
        line_edit = self.lineEdit()
        if line_edit is None:
            return
        if a0 and not self.isEnabled():
            super().setEnabled(a0)
            line_edit.setText(str(self._value))
        elif self.isEnabled() and not a0:
            super().setEnabled(a0)
            self._value = self.value()
            line_edit.setText(self._DISABLED_TEXT)

    def textFromValue(self, v: int) -> str:
        """
        Override to return custom text when the widget is disabled.
        """
        if not self.isEnabled():
            return self._DISABLED_TEXT
        return super().textFromValue(v)
