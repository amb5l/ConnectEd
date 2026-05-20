from typing  import Self, TypeAlias
from inspect import signature

from PyQt6.QtCore    import QModelIndex
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
    EditorType : TypeAlias = \
        EnumComboBox[DataKind]          | \
        StrEditor                       | \
        TextEditor                      | \
        IntEditor                       | \
        FloatEditor                     | \
        SizeEditor                      | \
        BoolEditor                      | \
        EnumComboBox[Display]           | \
        EnumComboBox                    | \
        EnumComboBox[RectHandleId]      | \
        EnumComboBox[LineHandleId]      | \
        EnumComboBox[BlockPinHandleId]  | \
        EnumComboBox[SymbolPinHandleId] | \
        EnumComboBox[AlignH]            | \
        EnumComboBox[AlignV]            | \
        EnumComboBox[Edge]              | \
        EnumComboBox[Direction]         | \
        ColorComboBox                   | \
        LineStyleComboBox               | \
        LineWidthComboBox               | \
        FillStyleComboBox               | \
        FontFamilyComboBox              | \
        FontSizeComboBox                | \
        FontBoolComboBox


class PropertiesDelegate(QStyledItemDelegate):
    _dialog : "PropertiesDialog"

    @checked
    def __init__(self : Self, dialog : QWidget) -> None:
        super().__init__(dialog)
        self._dialog = dialog

    def createEditor(
        self   : Self,
        parent : QWidget,
        option : QStyleOptionViewItem,
        index  : QModelIndex
    ) -> QWidget | None:
        model : QStandardItemModel = index.model()
        item : PropertiesItem = model.itemFromIndex(index)
        if item.value() is None:
            return None
        kind = item.kind()
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
    def setEditorData(self : Self, editor : EditorType, index : QModelIndex) -> None:
        item : PropertiesItem = index.model().item(index.row(), index.column())
        if item.initial() is not None:
            editor.setValue(item.initial())

    @checked
    def setModelData(
        self   : Self,
        editor : "EditorType",
        model  : QStandardItemModel,
        index  : QModelIndex
    ) -> None:
        if isinstance(editor, QLineEdit) \
                and not editor.hasAcceptableInput():
            return
        value = editor.value()
        if value is None:
            return
        item: PropertiesItem = model.itemFromIndex(index)
        item.setValue(value)
