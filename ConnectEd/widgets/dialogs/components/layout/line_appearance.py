from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtGui     import QColor

from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE

from ..combo.color      import ColorComboBox
from ..combo.line_width import LineWidthComboBox
from ..combo.line_style import LineStyleComboBox


class LineAppearanceLayout(QVBoxLayout):
    color_layout : QHBoxLayout
    color_label  : QLabel
    color_combo  : ColorComboBox
    width_layout : QHBoxLayout
    width_label  : QLabel
    width_combo  : LineWidthComboBox
    style_layout : QHBoxLayout
    style_label  : QLabel
    style_combo  : LineStyleComboBox

    def __init__(
        self      : Self,
        initial_color : QColor      | Default | NoChange,
        initial_width : float       | Default | NoChange,
        initial_style : Qt.PenStyle | Default | NoChange,
        default_color : QColor      | Default,
        default_width : float       | Default,
        default_style : Qt.PenStyle | Default,
        parent        : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.color_layout = QHBoxLayout()
        self.color_label = QLabel("Color:")
        self.color_layout.addWidget(self.color_label)
        self.color_combo = ColorComboBox(initial_color, default_color)
        self.color_layout.addWidget(self.color_combo)
        self.addLayout(self.color_layout)
        self.width_layout = QHBoxLayout()
        self.width_label = QLabel("Width:")
        self.width_layout.addWidget(self.width_label)
        self.width_combo = LineWidthComboBox(initial_width, default_width)
        self.width_layout.addWidget(self.width_combo)
        self.addLayout(self.width_layout)
        self.style_layout = QHBoxLayout()
        self.style_label = QLabel("Style:")
        self.style_layout.addWidget(self.style_label)
        self.style_combo = LineStyleComboBox(initial_style, default_style)
        self.style_layout.addWidget(self.style_combo)
        self.addLayout(self.style_layout)
        self.color_combo.activated.connect(self._onColorChanged)
        self.width_combo.activated.connect(self._onWidthChanged)

    def _onColorChanged(self : Self) -> None:
        color = self.color_combo.value()
        style = self.style_combo.value()
        if color not in (NO_CHANGE, DEFAULT) and style in (DEFAULT, Qt.PenStyle.NoPen):
            for i in range(self.style_combo.count()):
                if self.style_combo.itemText(i) == "Solid":
                    self.style_combo.setCurrentIndex(i)
                    break

    def _onWidthChanged(self : Self) -> None:
        width = self.width_combo.value()
        style = self.style_combo.value()
        if width not in (NO_CHANGE, DEFAULT) and style in (DEFAULT, Qt.PenStyle.NoPen):
            for i in range(self.style_combo.count()):
                if self.style_combo.itemText(i) == "Solid":
                    self.style_combo.setCurrentIndex(i)
                    break

    def getColorChoice(self : Self) -> QColor | Default:
        return self.color_combo.value()

    def getWidthChoice(self : Self) -> float | NoChange | Default:
        return self.width_combo.value()

    def getStyleChoice(self : Self) -> Qt.PenStyle | NoChange | Default:
        return self.style_combo.value()
