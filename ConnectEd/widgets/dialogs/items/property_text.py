from __future__ import annotations

from typing import Self, Any

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox, \
                            QLabel, QLineEdit, QTextEdit, \
                            QGraphicsItem

from ....core.check import checked
from ....core.types import NoChange, NO_CHANGE, HandleId, DataKind
from ....core.utils import numtrim, pascal2proper, str2val

from ...utils import kind2dialogEditor

from ...graphics.properties import PropertiesMixin, PropertyChange, \
                                   PropertyAndTextsEdit

from ...graphics.items.property_text import PropertyTextItem, PropertyTextChange

from ...graphics.items.mixin.edge_loc import ItemEdgeLocMixin

from ..components.edit import StrEditor

from ..components.combo.enum import EnumComboBox

from .text import BaseTextItemDialog


class PropertyLayout(QVBoxLayout):
    _NOT_FOUND = "<not found>"

    _top_layout         : QHBoxLayout
    _name_layout        : QHBoxLayout
    _name_label         : QLabel
    _name_value         : QLabel | StrEditor
    _kind_layout        : QHBoxLayout
    _kind_label         : QLabel
    _kind_value         : QLabel | EnumComboBox
    _cleat_layout        : QHBoxLayout
    _cleat_label        : QLabel
    _cleat_value_layout : QHBoxLayout
    _cleat_value        : EnumComboBox
    _bottom_layout      : QHBoxLayout
    _value_label        : QLabel
    _value_value        : QLabel | QLineEdit | QTextEdit

    @checked
    def __init__(self : Self, item : PropertyTextItem, name : str) -> None:
        super().__init__()
        owner    = item.owner()
        if owner is None:
            raise TypeError("Bad owner")
        property = item.property()
        inherent = property.isInherent()
        kind     = property.kind()
        value    = property.value()
        # name
        self._name_label = QLabel("Name:")
        name_value_widget = StrEditor if inherent is False else QLabel
        self._name_value = name_value_widget(name)
        self._name_layout = QHBoxLayout()
        self._name_layout.addWidget(self._name_label)
        self._name_layout.addWidget(self._name_value)
        self._name_layout.addStretch(1)
        # kind - static for inherent, combo for custom
        self._kind_label = QLabel("Type:")
        if not isinstance(kind, DataKind):
            raise TypeError("Bad kind")
        if inherent is True:
            self._kind_value = QLabel(kind.value)
        else:
            self._kind_value = EnumComboBox[DataKind](
                kind, (DataKind.STR, DataKind.TEXT)
            )
        self._kind_layout = QHBoxLayout()
        self._kind_layout.addWidget(self._kind_label)
        self._kind_layout.addWidget(self._kind_value)
        self._kind_layout.addStretch(1)
        # cleat
        self._cleat_label = QLabel("Cleat:")
        if not isinstance(cleat := item.cleat(), HandleId):
            raise TypeError("Bad cleat")
        self._cleat_value = EnumComboBox(cleat)
        self._cleat_layout = QHBoxLayout()
        self._cleat_layout.addWidget(self._cleat_label)
        self._cleat_layout.addWidget(self._cleat_value)
        self._cleat_layout.addStretch(1)
        # value - static or type specific editor
        self._value_label = QLabel("Value:")
        if property.writeable():
            editor = kind2dialogEditor(kind)
            args = {"value" : value}
            if inherent is False and kind is DataKind.KIND:
                args["subset"] = (DataKind.STR, DataKind.TEXT)
            self._value_value = editor(**args)
        else:
            self._value_value = QLabel(self._NOT_FOUND)
        # put it all together
        self._top_layout = QHBoxLayout()
        self._top_layout.addLayout(self._name_layout)
        self._top_layout.addLayout(self._kind_layout)
        self._top_layout.addLayout(self._cleat_layout)
        self._bottom_layout = QHBoxLayout()
        self._bottom_layout.addWidget(self._value_label)
        self._bottom_layout.addWidget(self._value_value)
        self.addLayout(self._top_layout)
        self.addLayout(self._bottom_layout)

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


class PropertyGroupBox(QGroupBox):
    _layout : PropertyLayout

    @checked
    def __init__(self : Self, item : PropertyTextItem, name : str) -> None:
        super().__init__()
        # get property
        property = item.property()
        title = "Inherent " if property.isInherent() else "Custom "
        title += "Property of "
        # get owner description
        owner = item.owner()
        if not isinstance(owner, PropertiesMixin):
            raise TypeError("Bad owner")
        owner_name = pascal2proper(
            owner.__class__.__name__.removesuffix("Item").removesuffix("Scene")
        )
        title += owner_name
        # append label or name
        if "Label" in owner.properties:
            label = owner.properties["Label"].value()
            if label: title += f' labelled "{label}"'
        elif "Name" in owner.properties:
            name = owner.properties["Name"].value()
            if name: title += f' named "{name}"'
        # append position or edge location
        if isinstance(owner, QGraphicsItem):
            if isinstance(owner, ItemEdgeLocMixin):
                edge = owner.loc().edge
                offset = owner.loc().offset
                if edge is not None and offset is not None:
                    edge = edge.value.lower()
                    title += f" on {edge} edge at offset {numtrim(offset)}"
            else:
                pos_x = owner.pos().x()
                pos_y = owner.pos().y()
                if pos_x is not None and pos_y is not None:
                    title += f" at {numtrim(pos_x)},{numtrim(pos_y)}"
        self.setTitle(title)
        self._layout = PropertyLayout(item, name)
        self.setLayout(self._layout)

    @checked
    def getName(self : Self) -> str | NoChange:
        return self._layout.getName()

    @checked
    def getKind(self : Self) -> DataKind | NoChange:
        return self._layout.getKind()

    @checked
    def getValue(self : Self) -> Any | NoChange:
        return self._layout.getValue()


class PropertyTextItemDialog(BaseTextItemDialog[PropertyTextItem]):
    _TITLE = "Property Text"

    _item        : PropertyTextItem
    _top_section : PropertyGroupBox

    @checked
    def initTopSection(self : Self, item : PropertyTextItem) -> None:
        if not isinstance(name := item.name(), str):
            raise TypeError("Bad name")
        self._item = item
        self._top_section = PropertyGroupBox(item, name)
        self._layout.addWidget(self._top_section)

    @checked
    def getEdits(self : Self) -> list[PropertyAndTextsEdit]:
        item = self._item
        owner = item.owner()
        if not isinstance(owner, PropertiesMixin):
            raise TypeError("Bad owner")
        change = PropertyChange(
            name  = self.getName(),
            kind  = self.getKind(),
            value = self.getValue()
        )
        text = PropertyTextChange(
            item       = item,
            cleat      = self.getCleat(),
            rotation   = self.getRotation(),
            mirror_h   = self.getMirrorH(),
            mirror_v   = self.getMirrorV(),
            autoflip   = self.getAutoflip(),
            origin     = self.getOrigin(),
            align_h    = self.getAlignH(),
            align_v    = self.getAlignV(),
            pad_left   = self.getPadLeft(),
            pad_right  = self.getPadRight(),
            pad_top    = self.getPadTop(),
            pad_bottom = self.getPadBottom(),
            color      = self.getColor(),
            font       = self.getFont(),
            size       = self.getSize(),
            bold       = self.getBold(),
            italic     = self.getItalic(),
            underline  = self.getUnderline()
        )
        edit = None if change.noop() else change
        texts = [] if text.noop() else [text]
        if edit is None and len(texts) == 0:
            return []
        return [PropertyAndTextsEdit(owner, item.property(), edit, texts)]

    @checked
    def getName(self : Self) -> str | NoChange:
        return self._top_section.getName()

    @checked
    def getKind(self : Self) -> DataKind | NoChange:
        return self._top_section.getKind()

    @checked
    def getValue(self : Self) -> Any | NoChange:
        return self._top_section.getValue()

    @checked
    def getCleat(self : Self) -> HandleId | NoChange:
        return self._top_section._layout._cleat_value.value()

    @checked
    def _focusEditor(self : Self) -> None:
        if isinstance(value := self._top_section._layout._value_value, QLabel):
            return
        elif isinstance(value, QLineEdit | QTextEdit):
            value.setFocus(Qt.FocusReason.OtherFocusReason)
            value.selectAll()
