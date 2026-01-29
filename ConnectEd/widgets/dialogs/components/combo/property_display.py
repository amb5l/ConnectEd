from typing import Self

from PyQt6.QtWidgets import QWidget, QComboBox

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...properties import PropertyDisplay


class PropertyDisplayComboBox(QComboBox):
    def __init__(
        self    : Self,
        initial : "PropertyDisplay",
        parent  : QWidget | None = None
    ) -> None:
        from ...properties import PropertyDisplay
        super().__init__(parent)
        self.addItems([d.value for d in PropertyDisplay])
        self.setCurrentText(initial.value)

    def getChoice(self : Self) -> "PropertyDisplay":
        from ...properties import PropertyDisplay
        return PropertyDisplay(self.currentText())
