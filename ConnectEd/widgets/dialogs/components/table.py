from __future__ import annotations

from typing          import Self, Any
from types           import SimpleNamespace

from PyQt6.QtCore    import Qt, QTransposeProxyModel
from PyQt6.QtWidgets import QWidget, QHeaderView, QTableView, \
                            QTreeView, QAbstractItemView
from PyQt6.QtGui     import QStandardItem, QStandardItemModel, \
                            QAction, QWheelEvent, QFont, QBrush

from ....app import settings

from ....core.check import checked
from ....core.types import NoChange
from ....core.utils import val2str


class TableItem(QStandardItem):
    _IDX_INITIAL = 0
    _IDX_CURRENT = 1
    _IDX_DELETED = 2

    @checked
    def __init__(
        self     : Self,
        value    : Any,
        new      : bool = False,
        editable : bool = True,
        enabled  : bool = True
    ) -> None:
        super().__init__()
        self.setDeleted(False)
        self.setInitial(None if new else value)
        self.setEnabled(enabled)
        self.setEditable(editable)
        self.setValue(value)

    @checked
    def initial(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_INITIAL)

    @checked
    def setInitial(self : Self, value : Any) -> None:
        self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_INITIAL)

    @checked
    def value(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_CURRENT)

    @checked
    def setValue(self : Self, value : Any | NoChange) -> None:
        if isinstance(value, NoChange):
            return
        self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_CURRENT)
        super().setText("" if value is None else val2str(value))
        self._updateAppearance()

    @checked
    def new(self : Self) -> bool:
        return self.initial() is None

    @checked
    def changed(self : Self) -> bool:
        return self.initial() != self.value()

    @checked
    def deleted(self : Self) -> bool:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_DELETED)

    @checked
    def setDeleted(self : Self, deleted : bool) -> None:
        self.setData(deleted, Qt.ItemDataRole.UserRole + self._IDX_DELETED)
        self._updateAppearance()

    @checked
    def setEnabled(self : Self, enabled : bool) -> None:
        super().setEnabled(enabled)
        self._updateAppearance()

    @checked
    def setEditable(self : Self, editable : bool) -> None:
        super().setEditable(editable)
        self._updateAppearance()

    def _updateAppearance(self : Self) -> None:
        font = self.font()
        font.setItalic(not self.isEditable())
        font.setStrikeOut(self.deleted())
        self.setFont(font)
        bg_args = []
        if self.isEnabled():
            if self.deleted():
                bg_args.append(settings().get("theme/properties/deleted/color"))
            elif self.new():
                bg_args.append(settings().get("theme/properties/added/color"))
            elif self.changed():
                bg_args.append(settings().get("theme/properties/changed/color"))
            if not self.isEditable():
                bg_args.append(Qt.BrushStyle.Dense5Pattern)
        bg_brush = QBrush(*bg_args) if bg_args else None
        self.setData(bg_brush, Qt.ItemDataRole.BackgroundRole)


class TableModel(QStandardItemModel):
    pass


class TableProxy(QTransposeProxyModel):
    pass


class TableViewMixin:
    _actions   : SimpleNamespace
    _font_size : int

    def _initTableViewMixin(self : Self) -> None:
        if not isinstance(self, QAbstractItemView):
            raise TypeError("Bad view")
        self._actions = SimpleNamespace()
        a = self._actions
        a.increaseTextSize = QAction("Increase Text Size", self)
        a.increaseTextSize.triggered.connect(self.increaseFontSize)
        a.decreaseTextSize = QAction("Decrease Text Size", self)
        a.decreaseTextSize.triggered.connect(self.decreaseFontSize)
        self.setFontSize(settings().get("display/font_size"))

    def _header(self : Self) -> QHeaderView | None:
        if isinstance(self, QTableView):
            return self.horizontalHeader()
        if isinstance(self, QTreeView):
            return self.header()
        return None

    def wheelEvent(self : Self, a0 : QWheelEvent | None) -> None:
        """Handle mouse wheel events to adjust font size when Ctrl is pressed."""
        if a0 is None:
            return
        modifiers = a0.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            delta = a0.angleDelta().y()
            if delta > 0:
                self.increaseFontSize()
            elif delta < 0:
                self.decreaseFontSize()
            a0.accept()
            return
        if isinstance(self, QTableView):
            QTableView.wheelEvent(self, a0)
        elif isinstance(self, QTreeView):
            QTreeView.wheelEvent(self, a0)

    @checked
    def setFontSize(self : Self, size : int) -> None:
        """Set the font size for all items in the table."""
        if not isinstance(self, QAbstractItemView):
            raise TypeError("Bad view")
        font = QFont()
        font.setPointSizeF(size)
        self.setFont(font)
        header = self._header()
        if header is not None:
            header.setFont(font)
            header.updateGeometries()
        self._font_size = size

    def increaseFontSize(self : Self) -> None:
        """Increase the font size."""
        self.setFontSize(min(self._font_size + 1, 20)) # TODO: max from settings

    def decreaseFontSize(self : Self) -> None:
        """Decrease the font size."""
        self.setFontSize(max(self._font_size - 1, 6)) # TODO: min from settings


class TableView(TableViewMixin, QTableView):
    @checked
    def __init__(
        self   : Self,
        model  : TableModel,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setModel(model)
        self.resizeColumnsToContents()
        self._initTableViewMixin()


class TreeTableView(TableViewMixin, QTreeView):
    @checked
    def __init__(
        self   : Self,
        model  : TableModel,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setUniformRowHeights(True)
        self.setAllColumnsShowFocus(True)
        self.setRootIsDecorated(True)
        self.setModel(model)
        self.expandAll()
        self.resizeColumnsToContents()
        self._initTableViewMixin()

    def resizeColumnsToContents(self : Self) -> None:
        model = self.model()
        if model is None:
            return
        for col in range(model.columnCount()):
            self.resizeColumnToContents(col)
