from __future__ import annotations

from typing  import Self
from inspect import signature

from PyQt6.QtCore    import Qt, QEvent, QRect, QSize, QModelIndex, \
                            QAbstractItemModel, pyqtSignal
from PyQt6.QtWidgets import QWidget, QLineEdit, QApplication, QStyle, \
                            QStyledItemDelegate, QStyleOptionViewItem
from PyQt6.QtGui     import QPainter, QMouseEvent, QStandardItemModel

from ....core.check import checked
from ....core.types import DataKind

from ...table.item import TableItem

from ...utils import kind2dialogEditor

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

    @checked
    def __init__(self : Self, parent : QWidget | None = None) -> None:
        super().__init__(parent)

    def createEditor(
        self   : Self,
        parent : QWidget | None,
        option : QStyleOptionViewItem,
        index  : QModelIndex
    ) -> QWidget | None:
        if not isinstance(model := index.model(), QStandardItemModel):
            return None
        if not isinstance(item := model.itemFromIndex(index), PropertiesItem):
            return None
        if item.value() is None:
            return None
        if (kind := item.kind()) is None:
            return None
        editor = kind2dialogEditor(kind)
        args = {
            "value"  : item.value(),
            "parent" : parent,
        }
        if kind is DataKind.KIND:
            args["subset"] = [DataKind.STR, DataKind.TEXT]
        sig_target = getattr(editor, '__origin__', editor)
        allowed = signature(sig_target).parameters.keys()
        args = {k: v for k, v in args.items() if k in allowed}
        return editor(**args)

    @checked
    def setEditorData(
        self   : Self,
        editor : QWidget | None,
        index  : QModelIndex
    ) -> None:
        if not isinstance(editor, EditorType):
            return
        if not isinstance(model := index.model(), QStandardItemModel):
            return
        if isinstance(item := model.itemFromIndex(index), PropertiesItem):
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
        if (value := editor.value()) is None:
            return
        if not isinstance(item := model.itemFromIndex(index), PropertiesItem):
            return
        item.setValue(value)


class ExpanderDelegate(QStyledItemDelegate):
    """
    Paints a tree branch in a dedicated gutter column.

    Cell value (TableItem.value / UserRole+current):
      True  — has extra children, expanded
      False — has extra children, collapsed
      None  — no extra children (blank)
    """

    toggled = pyqtSignal(QModelIndex, bool)

    @checked
    def __init__(self : Self, parent : QWidget | None = None) -> None:
        super().__init__(parent)

    def paint(
        self    : Self,
        painter : QPainter | None,
        option  : QStyleOptionViewItem,
        index   : QModelIndex
    ) -> None:
        super().paint(painter, option, index)
        if painter is None:
            return
        expanded = self._expanded(index)
        if expanded is None:
            return
        widget = option.widget
        style = widget.style() if widget is not None else QApplication.style()
        branch = QStyleOptionViewItem(option)
        branch.rect = self._indicatorRect(option, widget)
        branch.state |= QStyle.StateFlag.State_Children
        if expanded:
            branch.state |= QStyle.StateFlag.State_Open
        if style is None:
            return
        style.drawPrimitive(
            QStyle.PrimitiveElement.PE_IndicatorBranch,
            branch,
            painter,
            widget
        )

    def createEditor(
        self   : Self,
        parent : QWidget | None,
        option : QStyleOptionViewItem,
        index  : QModelIndex
    ) -> QWidget | None:
        return None

    def editorEvent(
        self   : Self,
        event  : QEvent             | None,
        model  : QAbstractItemModel | None,
        option : QStyleOptionViewItem,
        index  : QModelIndex
    ) -> bool:
        if event is None or model is None:
            return False
        expanded = self._expanded(index)
        if expanded is None:
            return False
        if event.type() != QEvent.Type.MouseButtonRelease:
            return False
        if not isinstance(event, QMouseEvent):
            return False
        if event.button() != Qt.MouseButton.LeftButton:
            return False
        if not option.rect.contains(event.pos()):
            return False
        if not isinstance(model, QStandardItemModel):
            return False
        item = model.itemFromIndex(index)
        if not isinstance(item, TableItem):
            return False
        item.setValue(not expanded)
        self.toggled.emit(index, not expanded)
        return True

    def sizeHint(
        self   : Self,
        option : QStyleOptionViewItem,
        index  : QModelIndex
    ) -> QSize:
        widget = option.widget
        style = widget.style() if widget is not None else QApplication.style()
        if style is None:
            return QSize(0, 0)
        width = style.pixelMetric(
            QStyle.PixelMetric.PM_IndicatorWidth, option, widget
        )
        height = super().sizeHint(option, index).height()
        return QSize(width + 4, height)

    def _expanded(self : Self, index : QModelIndex) -> bool | None:
        model = index.model()
        if isinstance(model, QStandardItemModel):
            item = model.itemFromIndex(index)
            if isinstance(item, TableItem):
                value = item.value()
                return value if isinstance(value, bool) else None
        value = index.data(Qt.ItemDataRole.UserRole + TableItem._IDX_CURRENT)
        return value if isinstance(value, bool) else None

    def _indicatorRect(
        self   : Self,
        option : QStyleOptionViewItem,
        widget : QWidget | None
    ) -> QRect:
        style = widget.style() if widget is not None else QApplication.style()
        if style is None:
            return QRect(0, 0, 0, 0)
        size = style.pixelMetric(
            QStyle.PixelMetric.PM_IndicatorWidth, option, widget
        )
        cell = option.rect
        return QRect(
            cell.x() + (cell.width()  - size) // 2,
            cell.y() + (cell.height() - size) // 2,
            size,
            size
        )
