from typing import Self

from PyQt6.QtWidgets import QWidget, QComboBox

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...properties import DisplayChoice


class DisplayChoiceComboBox(QComboBox):
    def __init__(
        self    : Self,
        initial : "DisplayChoice",
        parent  : QWidget | None = None
    ) -> None:
        from ...properties import DisplayChoice
        super().__init__(parent)
        self.addItems([d.value for d in DisplayChoice])
        self.setCurrentText(initial.value)

    def getChoice(self : Self) -> "DisplayChoice":
        from ...properties import DisplayChoice
        return DisplayChoice(self.currentText())
