from __future__ import annotations

from typing import Self, Any

from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, \
                            QLabel, QLineEdit, QTextEdit

from .....core.check      import checked
from .....core.types      import NoChange, NO_CHANGE, DataKind, HandleId
from .....core.utils      import pascal2proper, str2val
from .....core.properties import _CUSTOM_PROPERTY_KINDS

from ....graphics.items.mixin.properties import PropertiesMixin

from ..edit import StrEditor

from ..combo.enum import EnumComboBox

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...items.property_text import PropertyTextItem


class PropertyTextLayout(QGridLayout):
    _NOT_FOUND = "<not found>"

    _owner_label        : QLabel
    _owner_value        : QLabel
    _cleat_label        : QLabel
    _cleat_value_layout : QHBoxLayout
    _cleat_value        : EnumComboBox
    _name_label         : QLabel
    _name_value         : QLabel | StrEditor
    _provenance_label   : QLabel
    _provenance_value   : QLabel
    _kind_label         : QLabel
    _kind_value_layout  : QHBoxLayout
    _kind_value         : QLabel | EnumComboBox
    _value_label        : QLabel
    _value_value        : QLabel | QLineEdit | QTextEdit

    @checked
    def __init__(self : Self, object : PropertyTextItem, name : str) -> None:
        super().__init__()
        owner_item = object.item()
        owner_desc = self._NOT_FOUND
        inherent   = None
        kind       = self._NOT_FOUND
        value      = self._NOT_FOUND
        if isinstance(owner_item, PropertiesMixin) \
        and owner_item.propertyExists(name):
            owner_desc = owner_item.__class__.__name__
            owner_desc = owner_desc.removesuffix("Item")
            owner_desc = owner_desc.removesuffix("Scene")
            owner_desc = pascal2proper(owner_desc)
            inherent   = owner_item.propertyInherent(name)
            kind       = owner_item.propertyKind(name)
            value      = owner_item.propertyValue(name)
        row = 0
        # owner
        self._owner_label = QLabel("Owner:")
        self.addWidget(self._owner_label, row, 0)
        self._owner_value = QLabel(owner_desc)
        self.addWidget(self._owner_value, row, 1)
        row += 1
        # cleat
        self._cleat_label = QLabel("Cleat:")
        self.addWidget(self._cleat_label, row, 0)
        self._cleat_value_layout = QHBoxLayout()
        if not isinstance(cleat := object.cleat(), HandleId):
            raise TypeError("Bad cleat")
        self._cleat_value = EnumComboBox(cleat)
        self._cleat_value_layout.addWidget(self._cleat_value)
        self._cleat_value_layout.addStretch(1)
        self.addLayout(self._cleat_value_layout, row, 1)
        row += 1
        # name
        self._name_label = QLabel("Name:")
        self.addWidget(self._name_label, row, 0)
        name_value_widget = StrEditor if inherent is False else QLabel
        self._name_value = name_value_widget(name)
        self.addWidget(self._name_value, row, 1)
        row += 1
        # provenance
        self._provenance_label = QLabel("Provenance:")
        self.addWidget(self._provenance_label, row, 0)
        self._provenance_value = QLabel("Inherent" if inherent else "Custom")
        self.addWidget(self._provenance_value, row, 1)
        row += 1
        # kind - static for inherent, combo for custom
        self._kind_label = QLabel("Type:")
        self.addWidget(self._kind_label, row, 0)
        self._kind_value_layout = QHBoxLayout()
        if not isinstance(kind, DataKind):
            raise TypeError("Bad kind")
        if inherent is False:
            self._kind_value = EnumComboBox[DataKind](kind, _CUSTOM_PROPERTY_KINDS)
        elif inherent is True:
            self._kind_value = QLabel(kind.value)
        else:
            self._kind_value = QLabel(self._NOT_FOUND)
        self._kind_value_layout.addWidget(self._kind_value)
        self._kind_value_layout.addStretch(1)
        self.addLayout(self._kind_value_layout, row, 1)
        row += 1
        # value - static or type specific editor
        self._value_label = QLabel("Value:")
        self.addWidget(self._value_label, row, 0)
        if isinstance(owner_item, PropertiesMixin) \
        and owner_item.propertyWriteable(name) is True:
            editor = kind.editor()
            args = {"value" : value}
            if inherent is False and kind is DataKind.KIND:
                args["subset"] = _CUSTOM_PROPERTY_KINDS
            self._value_value = editor(**args)
        else:
            self._value_value = QLabel(self._NOT_FOUND)
        self.addWidget(self._value_value, row, 1)
        row += 1

    @checked
    def getName(self : Self) -> str | NoChange:
        if isinstance(self._name_value, QLabel):
            return NO_CHANGE
        else:
            return self._name_value.value()

    @checked
    def getKind(self : Self) -> DataKind | NoChange:
        if isinstance(self._kind_value, QLabel):
            return NO_CHANGE
        else:
            return self._kind_value.value()

    @checked
    def getValue(self : Self) -> Any | NoChange:
        if isinstance(self._value_value, QLabel):
            return NO_CHANGE
        elif isinstance(self._value_value, QLineEdit):
            text = self._value_value.text()
        elif isinstance(self._value_value, QTextEdit):
            text = self._value_value.toPlainText()
        else:
            raise TypeError("Bad value widget")
        if isinstance(self._kind_value, QLabel):
            kind = DataKind(self._kind_value.text())
        else:
            kind = self._kind_value.value()
            if isinstance(kind, NoChange):
                kind = DataKind(self._kind_value.currentText())
        return str2val(text, kind.types()[0].__name__)
