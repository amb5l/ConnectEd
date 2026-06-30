from __future__ import annotations

from typing  import Self
from inspect import signature

from PyQt6.QtCore    import QModelIndex, QAbstractItemModel
from PyQt6.QtWidgets import QWidget, QLineEdit, \
                            QStyledItemDelegate, QStyleOptionViewItem
from PyQt6.QtGui     import QStandardItemModel

from ....core.check import checked
from ....core.types import AlignH, AlignV, Edge, Direction, Display, DataKind, \
                           RectHandleId, LineHandleId, \
                           BlockPinHandleId, SymbolPinHandleId

from ...graphics.properties import _CUSTOM_PROPERTY_KINDS

from ..components.edit import \
    StrEditor, TextEditor, IntEditor, FloatEditor, SizeEditor, BoolEditor

from ..components.combo.enum        import EnumComboBox
from ..components.combo.color       import ColorComboBox
from ..components.combo.line_width  import LineWidthComboBox
from ..components.combo.line_style  import LineStyleComboBox
from ..components.combo.fill_style  import FillStyleComboBox
from ..components.combo.font_family import FontFamilyComboBox
from ..components.combo.font_size   import FontSizeComboBox
from ..components.combo.font_bool   import FontBoolComboBox

from .item import PropertiesItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import PropertiesDialog
    EditorType = (
        StrEditor,
        TextEditor,
        IntEditor,
        FloatEditor,
        SizeEditor,
        BoolEditor,
        EnumComboBox,
        ColorComboBox,
        LineStyleComboBox,
        LineWidthComboBox,
        FillStyleComboBox,
        FontFamilyComboBox,
        FontSizeComboBox,
        FontBoolComboBox
    )


class PropertiesDelegate(QStyledItemDelegate):
    _dialog : PropertiesDialog

    @checked
    def __init__(self : Self, dialog : PropertiesDialog) -> None:
        super().__init__(dialog)
        self._dialog = dialog

    def createEditor(
        self   : Self,
        parent : QWidget | None,
        option : QStyleOptionViewItem,
        index  : QModelIndex
    ) -> QWidget | None:
        model = index.model()
        if not isinstance(model, QStandardItemModel):
            return None
        item = model.itemFromIndex(index)
        if not isinstance(item, PropertiesItem):
            return None
        if item.value() is None:
            return None
        kind = item.kind()
        if kind is None:
            return None
        editor = kind.editor()
        args = {
            "value"   : item.value(),
            "default" : item.default(),
            "parent"  : parent,
        }
        if kind is DataKind.KIND:
            args["subset"] = _CUSTOM_PROPERTY_KINDS
        sig_target = getattr(editor, '__origin__', editor)
        allowed = signature(sig_target).parameters.keys()
        args = {k: v for k, v in args.items() if k in allowed}
        e = editor(**args)
        if kind is DataKind.DISPLAY and isinstance(e, EnumComboBox):
            row = index.row()
            e.currentIndexChanged.connect(
                lambda: self._dialog._onDisplayChanged(e.raw(), row)
            )
            e.destroyed.connect(
                lambda: self._dialog._refreshDisplay(row)
            )
        return e

    @checked
    def setEditorData(
        self   : Self,
        editor : QWidget | None,
        index  : QModelIndex
    ) -> None:
        if not isinstance(editor, EditorType):
            return
        model = index.model()
        if not isinstance(model, QStandardItemModel):
            return
        item = model.itemFromIndex(index)
        if isinstance(item, PropertiesItem):
            if item.initial() is not None:
                editor.setValue(item.initial())

    @checked
    def setModelData(
        self   : Self,
        editor : QWidget | None,
        model  : QAbstractItemModel | None,
        index  : QModelIndex
    ) -> None:
        if not isinstance(editor, EditorType):
            return
        if isinstance(editor, QLineEdit) and not editor.hasAcceptableInput():
            return
        if not isinstance(model, QStandardItemModel):
            return
        value = editor.value()
        if value is None:
            return
        item = model.itemFromIndex(index)
        if not isinstance(item, PropertiesItem):
            return
        item.setValue(value)
