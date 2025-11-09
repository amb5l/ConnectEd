from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel

from ....graphics.items import FillPrefChange, FillPref, NO_CHANGE, DEFAULT

from ..combo.color      import ColorComboBox
from ..combo.fill_style import FillStyleComboBox


class FillAppearanceLayout(QGridLayout):
    color_label : QLabel
    color_combo : ColorComboBox
    style_label : QLabel
    style_combo : FillStyleComboBox

    def __init__(self : Self,
        initial   : FillPrefChange,
        default   : FillPref,
        no_change : FillPrefChange | None = None,
        parent    : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        row = 0
        if initial.color is not None:
            self.color_label = QLabel("Color:")
            self.addWidget(self.color_label, row, 0)
            self.color_combo = ColorComboBox(
                initial.color,
                default.color,
                None if no_change is None else no_change.color,
            )
            self.addWidget(self.color_combo, row, 1)
            row += 1
        if initial.style is not None:
            self.style_label = QLabel("Style:")
            self.addWidget(self.style_label, row, 0)
            self.style_combo = FillStyleComboBox(
                initial.style,
                default.style,
                None if no_change is None else no_change.style,
            )
            self.addWidget(self.style_combo, row, 1)
        if hasattr(self, 'color_combo') and hasattr(self, 'style_combo'):
            self.color_combo.activated.connect(self._onColorChanged)
        if hasattr(self, 'width_combo') and hasattr(self, 'style_combo'):
            self.width_combo.activated.connect(self._onWidthChanged)

    def _onColorChanged(self : Self) -> None:
        """Automatically set SolidLine when color is specified and style is NoPen."""
        color = self.color_combo.getChoice()
        style = self.style_combo.getChoice()

        if color not in (NO_CHANGE, DEFAULT) and style in (DEFAULT, Qt.PenStyle.NoPen):
            for i in range(self.style_combo.count()):
                if self.style_combo.itemText(i) == "Solid":
                    self.style_combo.setCurrentIndex(i)
                    break

    def _onWidthChanged(self : Self) -> None:
        """Automatically set SolidLine when width is specified and style is NoPen."""
        width = self.width_combo.getChoice()
        style = self.style_combo.getChoice()

        if width not in (NO_CHANGE, DEFAULT) and style in (DEFAULT, Qt.PenStyle.NoPen):
            for i in range(self.style_combo.count()):
                if self.style_combo.itemText(i) == "Solid":
                    self.style_combo.setCurrentIndex(i)
                    break

    def getChoice(self : Self) -> FillPrefChange:
        r = FillPrefChange()
        if hasattr(self, "color_combo"):
            r.color = self.color_combo.getChoice()
        if hasattr(self, "style_combo"):
            r.style = self.style_combo.getChoice()
        return r
