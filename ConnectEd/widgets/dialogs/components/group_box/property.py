from typing import Self

from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QGridLayout, \
                            QLabel, QComboBox, QWidget

from .....core.check import checked
from .....core.types import Text

from ....graphics.properties import PropertiesMixin

from ..combo.cleat         import CleatComboBox
from ..combo.property_name import PropertyNameComboBox

from ..edit import TextLineEditor, FloatEditor, BoolEditor, TextEditor


ValueWidgetType : TypeAlias = QComboBox | TextLineEditor | TextBlockEditor

class PropertyGroupBox(QGroupBox):
    _layout       : QGridLayout
    _owner_label  : QLabel
    _owner_desc   : QLabel
    _cleat_label  : QLabel
    _cleat_combo  : CleatComboBox
    _name_label   : QLabel
    _name_combo   : PropertyNameComboBox
    _type_label   : QLabel
    _type_widget  : QLabel | QComboBox
    _value_label  : QLabel
    _value_widget : QWidget


    @checked
    def __init__(
        self  : Self,
        owner : PropertiesMixin,
        name  : str
    ) -> None:
        super().__init__(name)
        kind = owner.getPropertyKind(name)
        value = owner.getPropertyValue(name)
        # layout
        self._layout = QGridLayout()
        # name and type section,
        self._name_label = QLabel("Name:")
        self._layout.addWidget(self._name_label, 0, 0)
        self._name_combo = PropertyNameComboBox(owner)
        self._layout.addWidget(self._name_combo, 0, 1)
        # type
        self._type_label = QLabel(type)
        self._layout.addWidget(self._type_label, 1, 0)
        if kind == "Text" and isinstance(value, Text):
            self._type_widget = QComboBox()
            self._type_widget.addItem("Text Line", False)
            self._type_widget.addItem("Text Block", True)
            self._type_widget.setCurrentIndex(1 if value.block else 0)
        else:
            self._type_widget = QLabel(kind)
        self._layout.addWidget(self._type_widget, 1, 1)
        # value label
        self._value_label = QLabel("Value:")
        self._layout.addWidget(self._value_label, 2, 0)
        # value widget - depends on type/kind
        match kind:
            case "str"   : w = TextLineEditor(value)
            case "float" : w = FloatEditor(value)
            case "bool"  : w = BoolEditor(value)
            case "Text"  : w = TextEditor(value)
            case _       : w = QLabel(str(value))
        self._value_widget = w
        self._layout.addWidget(self._value_widget, 2, 1)


        # owner
        self._owner_label = QLabel("Owner:")
        self._layout.addWidget(self._owner_label, 3, 0)
        self._owner_desc = QLabel(owner.description())
        self._layout.addWidget(self._owner_desc, 3, 1)
        # cleat
        self._cleat_label = QLabel("Cleat:")
        self._layout.addWidget(self._cleat_label, 4, 0)
        self._cleat_combo = CleatComboBox(owner, owner.getPropertyText(name).cleat())
        self._layout.addWidget(self._cleat_combo, 4, 1)
        # put it all together
        self.setLayout(self._layout)

