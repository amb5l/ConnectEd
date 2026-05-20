from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtGui     import QColor

from .....app import logger

from .....core.check import checked
from .....core.types import NoChange

from ..combo.color      import ColorComboBox
from ..combo.fill_style import FillStyleComboBox


class FillAppearanceLayout(QVBoxLayout):
    _default_color : QColor
    _default_style : Qt.BrushStyle
    color_layout   : QHBoxLayout
    color_label    : QLabel
    color_combo    : ColorComboBox
    style_layout   : QHBoxLayout
    style_label    : QLabel
    style_combo    : FillStyleComboBox

    @checked
    def __init__(self : Self,
        initial_color : QColor        | None | NoChange,
        initial_style : Qt.BrushStyle | None | NoChange,
        default_color : QColor,
        default_style : Qt.BrushStyle,
        parent        : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._default_color = default_color
        self._default_style = default_style
        self.color_layout = QHBoxLayout()
        self.color_label = QLabel("Color:")
        self.color_layout.addWidget(self.color_label)
        self.color_combo = ColorComboBox(initial_color, default_color)
        self.color_layout.addWidget(self.color_combo)
        self.addLayout(self.color_layout)
        self.style_layout = QHBoxLayout()
        self.style_label = QLabel("Style:")
        self.style_layout.addWidget(self.style_label)
        self.style_combo = FillStyleComboBox(initial_style, default_style)
        self.style_layout.addWidget(self.style_combo)
        self.addLayout(self.style_layout)
        self.color_combo.activated.connect(self._onColorChanged)

    def _onColorChanged(self : Self, _index : int = 0) -> None:
        """Set style to ensure visibility when color is specified."""
        color = self.color_combo.value()
        if not isinstance(color, QColor): return
        style = self.style_combo.value()
        if style is None: style = self._default_style
        if style != Qt.BrushStyle.NoBrush: return
        auto_style = None if self._default_style != Qt.BrushStyle.NoBrush else \
            Qt.BrushStyle.SolidPattern
        for i in range(self.style_combo.count()):
            if auto_style == self.style_combo.itemData(i, Qt.ItemDataRole.UserRole):
                self.style_combo.setCurrentIndex(i)
                break
        else:
            logger().warning("Fill style not found")

    @checked
    def getColorChoice(self : Self) -> QColor | None | NoChange:
        return self.color_combo.value()

    @checked
    def getStyleChoice(self : Self) -> Qt.BrushStyle | None | NoChange:
        return self.style_combo.value()
