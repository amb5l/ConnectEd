from typing import Self

from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel

from .....core.check import checked
from .....core.types import DataKind

from ....graphics.properties import PropertiesMixin

from ..combo.property_name import PropertyNameComboBox
from ..combo.text_format   import TextFormatComboBox
from ..combo.cleat         import CleatComboBox

from ..edit import StrEditor, FloatEditor, BoolEditor, TextEditor


class PropertyLayout(QGridLayout):
    _name_label   : QLabel
    _name_combo   : PropertyNameComboBox
    _type_label   : QLabel
    _type_desc    : QLabel
    _value_label  : QLabel
    _value_widget : QWidget
    _owner_label  : QLabel
    _owner_desc   : QLabel
    _cleat_label  : QLabel
    _cleat_combo  : CleatComboBox



    @checked
    def __init__(
        self   : Self,
        owner  : PropertiesMixin,
        name   : str,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        kind = owner.getPropertyKind(name)
        value = owner.getPropertyValue(name)
        # name and type section,
        self._name_label = QLabel("Name:")
        self.addWidget(self._name_label, 0, 0)
        self._name_combo = PropertyNameComboBox(owner)
        self.addWidget(self._name_combo, 0, 1)
        # type
        self._type_label = QLabel(type)
        self.addWidget(self._type_label, 1, 0)
        self._type_desc = QLabel(kind.description)
        self.addWidget(self._type_desc, 1, 1)
        # value label
        self._value_label = QLabel("Value:")
        self.addWidget(self._value_label, 2, 0)
        # value widget - depends on type/kind
        match kind:
            case DataKind.STR   : w = StrEditor(value)
            case DataKind.FLOAT : w = FloatEditor(value)
            case DataKind.BOOL  : w = BoolEditor(value)
            case DataKind.TEXT  : w = TextEditor(value)
            case _       : w = QLabel(str(value))
        self._value_widget = w
        self.addWidget(self._value_widget, 2, 1)
        # owner
        self._owner_label = QLabel("Owner:")
        self.addWidget(self._owner_label, 3, 0)
        self._owner_desc = QLabel(owner.description())
        self.addWidget(self._owner_desc, 3, 1)
        # cleat
        self._cleat_label = QLabel("Cleat:")
        self.addWidget(self._cleat_label, 4, 0)
        self._cleat_combo = CleatComboBox(owner, owner.getPropertyTextItem(name).cleat())
        self.addWidget(self._cleat_combo, 4, 1)

    def getName(self : Self) -> str:
        return self._name_combo.currentText()

    def getType(self : Self) -> str: