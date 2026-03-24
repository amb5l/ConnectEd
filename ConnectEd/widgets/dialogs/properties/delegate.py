from typing  import Self, TypeAlias
from inspect import signature

from PyQt6.QtCore    import QModelIndex
from PyQt6.QtWidgets import QWidget, QLineEdit, \
                            QStyledItemDelegate, QStyleOptionViewItem
from PyQt6.QtGui     import QStandardItemModel

from ....core.types import AlignH, AlignV, Edge, Direction, Display, DataKind, \
                           RectHandleId, LineHandleId, \
                           BlockPinHandleId, SymbolPinHandleId


from ..components.edit import StrEditor, NameStrEditor, TextEditor, \
                            IntEditor, FloatEditor, BoolEditor

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
    EditorType : TypeAlias = \
        EnumComboBox[DataKind]          | \
        StrEditor                       | \
        NameStrEditor                 | \
        TextEditor                      | \
        IntEditor                       | \
        FloatEditor                     | \
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
    def createEditor(
        self   : Self,
        parent : QWidget,
        option : QStyleOptionViewItem,
        index  : QModelIndex
    ) -> QWidget | None:
        model : QStandardItemModel = index.model()
        item : PropertiesItem = model.itemFromIndex(index)
        kind = item.kind()
        editor = kind.editor()
        exclude = [
            model.item(r, index.column()).value()
            for r in range(model.rowCount()) if r != index.row()
        ]
        args = {
            "value"   : item.value(),
            "exclude" : exclude,
            "subset"  : (DataKind.STR, DataKind.TEXT),
            "default" : item.default(),
            "parent"  : parent,
        }
        sig_target = getattr(editor, '__origin__', editor)
        allowed = signature(sig_target).parameters.keys()
        args = {k: v for k, v in args.items() if k in allowed}
        return editor(**args)

    def setEditorData(self : Self, editor : EditorType, index : QModelIndex) -> None:
        item : PropertiesItem = index.model().item(index.row(), index.column())
        if item.initial() is not None:
            editor.setValue(item.initial())

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
