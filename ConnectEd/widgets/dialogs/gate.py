from typing import Self

from PyQt6.QtCore    import QSize
from PyQt6.QtWidgets import QWidget, QDialog, \
                            QVBoxLayout, QHBoxLayout, \
                            QLabel, QComboBox

from ...resources import getIconPath

from ...core.icon import SvgIconSingleton

from ..graphics.items.gate import GateFunc

from .components.spin import CustomSpinBox

from .components.layout.ok_cancel import okCancelLayout


class BufIcon(SvgIconSingleton):
    PATH = getIconPath("buf.svg")
    SIZE = QSize(16, 16)


class AndIcon(SvgIconSingleton):
    PATH = getIconPath("and.svg")
    SIZE = QSize(16, 16)


class OrIcon(SvgIconSingleton):
    PATH = getIconPath("or.svg")
    SIZE = QSize(16, 16)


class XorIcon(SvgIconSingleton):
    PATH = getIconPath("xor.svg")
    SIZE = QSize(16, 16)


_icons = [BufIcon(), AndIcon(), OrIcon(), XorIcon()]


class GateDialog(QDialog):
    _dialog_layout   : QVBoxLayout
    _function_layout : QHBoxLayout
    _function_label  : QLabel
    _function_combo  : QComboBox
    _width_layout    : QHBoxLayout
    _width_label     : QLabel
    _width_spinbox   : CustomSpinBox

    def __init__(
        self   : Self,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Gate")
        self._dialog_layout = QVBoxLayout(self)
        self._function_layout = QHBoxLayout()
        self._function_label = QLabel("Function:")
        self._function_layout.addWidget(self._function_label)
        self._function_combo = QComboBox()
        for i, function in enumerate(GateFunc):
            self._function_combo.addItem(_icons[i].get(), function.value)
        self._function_layout.addWidget(self._function_combo)
        self._dialog_layout.addLayout(self._function_layout)
        self._width_layout = QHBoxLayout()
        self._width_label = QLabel("Width:")
        self._width_layout.addWidget(self._width_label)
        self._width_spinbox = CustomSpinBox()
        self._width_spinbox.setRange(2, 99)
        self._width_layout.addWidget(self._width_spinbox)
        self._dialog_layout.addLayout(self._width_layout)
        okCancelLayout(self)
        self._function_combo.currentIndexChanged.connect(self._onFunctionChanged)
        self._onFunctionChanged()

    def getFunction(self : Self) -> GateFunc:
        return GateFunc(self._function_combo.currentText())

    def getWidth(self : Self) -> int:
        if self.getFunction() == GateFunc.BUF_INV:
            return 1
        return self._width_spinbox.value()

    def _onFunctionChanged(self : Self) -> None:
        is_buffer = self.getFunction() == GateFunc.BUF_INV
        self._width_spinbox.setEnabled(not is_buffer)
