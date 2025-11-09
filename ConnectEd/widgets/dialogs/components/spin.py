from typing import Self

from PyQt6.QtWidgets import QWidget, QSpinBox


class CustomSpinBox(QSpinBox):
    """
    A QSpinBox that displays "N/A" (or any custom text) when disabled.
    """
    # class attributes
    _DISABLED_TEXT = "N/A"

    # instance attributes
    _value   : int | None

    def __init__(
        self   : Self,
        value  : int | None = None,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._value = self.value()

    def setEnabled(self : Self, enabled : bool) -> None:
        if enabled and not self.isEnabled():
            super().setEnabled(enabled)
            self.lineEdit().setText(str(self._value))
        elif self.isEnabled() and not enabled:
            super().setEnabled(enabled)
            self._value = self.value()
            self.lineEdit().setText(self._DISABLED_TEXT)

    def textFromValue(self, value: int) -> str:
        """
        Override to return custom text when the widget is disabled.
        """
        if not self.isEnabled():
            return self._DISABLED_TEXT
        return super().textFromValue(value)
