from __future__ import annotations

from typing import Self, Any
from types  import SimpleNamespace

from PyQt6.QtCore    import Qt, QModelIndex, QPoint, QSize, \
                            QTransposeProxyModel, QAbstractItemModel
from PyQt6.QtWidgets import QTabWidget, QWidget, QSizePolicy, \
                            QHBoxLayout, QVBoxLayout, QPushButton, QLabel, \
                            QTableView, QAbstractItemView, QAbstractButton, \
                            QHeaderView, QStyledItemDelegate, QComboBox, \
                            QStyleOptionViewItem, QGraphicsItem
from PyQt6.QtGui     import QBrush, QFont, QAction, QUndoStack, \
                            QWheelEvent, QContextMenuEvent, QCloseEvent, \
                            QStandardItemModel, QStandardItem, QFontMetrics, \
                            QShowEvent

from ...app import logger, settings, window

from ...core.check import checked
from ...core.icon  import getCharIcon

from ..menu import Menu

from .sub_window import DocSubWindow

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..graphics.items.mixin   import ItemMixin
    from ..graphics.views.diagram import DiagramScene


class SpreadsheetCell(QStandardItem):
    """Custom item for spreadsheet cells, storing string values."""
    @checked
    def __init__(self : Self, value : Any) -> None:
        text_value = "" if value is None else str(value)
        super().__init__(text_value)
        self.setFlags(
            Qt.ItemFlag.ItemIsEditable |
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
        )
        # set user data
        self.setData(value, Qt.ItemDataRole.UserRole) # initial value

    def changed(self : Self) -> bool:
        return self.data(Qt.ItemDataRole.UserRole) != self.text()

class SpreadsheetComboDelegate(QStyledItemDelegate):
    """Base delegate for combo box editing."""
    TOOLTIP : str
    ENTRIES : list[str]

    @checked
    def __init__(self : Self):
        super().__init__()

    def createEditor(
        self   : Self,
        parent : QWidget | None,
        option : QStyleOptionViewItem,
        index  : QModelIndex
    ) -> QComboBox | None:
        if not self.ENTRIES:
            logger().error(f"ENTRIES is None or empty for delegate {self.__class__.__name__}")
            return None
        try:
            editor = QComboBox(parent)
            editor.addItems(self.ENTRIES)
            if self.TOOLTIP:
                editor.setToolTip(self.TOOLTIP)
            return editor
        except Exception as e:
            logger().error(f"Error creating editor for delegate {self.__class__.__name__}: {e}")
            return None

    def setEditorData(self : Self, editor : QWidget | None, index : QModelIndex):
        if not isinstance(editor, QComboBox):
            raise ValueError("Editor is not a QComboBox")
        if (model := index.model()) is None:
            raise RuntimeError("No model")
        value = model.data(index, Qt.ItemDataRole.EditRole)
        value_str = str(value) if value is not None else ""
        if value_str in self.ENTRIES:
            editor.setCurrentText(value_str)
        else:
            logger().warning(f"Value '{value_str}' not in ENTRIES, defaulting to {self.ENTRIES[0]}")
            editor.setCurrentText(self.ENTRIES[0])

    def setModelData(
        self   : Self,
        editor : QWidget | None,
        model  : QAbstractItemModel | None,
        index : QModelIndex
    ):
        if not isinstance(editor, QComboBox):
            raise ValueError("Editor is not a QComboBox")
        if not isinstance(model, QStandardItemModel):
            raise ValueError("Model is not a QStandardItemModel")
        text = editor.currentText()
        model.setData(index, text, Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(
        self   : Self,
        editor : QWidget | None,
        option : QStyleOptionViewItem,
        index  : QModelIndex
    ):
        if not isinstance(editor, QComboBox):
            raise ValueError("Editor is not a QComboBox")
        editor.setGeometry(option.rect)

    def sizeHint(
        self   : Self,
        option : QStyleOptionViewItem,
        index  : QModelIndex
    ):
        from PyQt6.QtCore import QSize
        if hasattr(self, 'ENTRIES') and self.ENTRIES:
            from PyQt6.QtGui import QFontMetrics
            font_metrics = QFontMetrics(option.font)
            longest_entry = max(self.ENTRIES, key=len)
            width = font_metrics.horizontalAdvance(longest_entry) + 30
            height = font_metrics.height() + 4
            return QSize(width, height)
        return QSize(100, 25)

class SpreadsheetAPDelegate(SpreadsheetComboDelegate):
    """Delegate for handle enum values."""
    TOOLTIP = "Controls position of handle"
    ENTRIES = [  # TODO fix this to work with other handle names
        "Top Left",
        "Top Center",
        "Top Right",
        "Middle Left",
        "Middle Center",
        "Middle Right",
        "Bottom Left",
        "Bottom Center",
        "Bottom Right"
    ]

class SpreadsheetHeader(QHeaderView):
    """Custom header view that provides a context menu for sorting."""

    _table      : SpreadsheetTable
    _len        : int
    _transposed : bool

    @checked
    def __init__(
            self : Self,
            table       : SpreadsheetTable,
            orientation : Qt.Orientation,
            len         : int,
            transposed  : bool
        ) -> None:
        super().__init__(orientation, table)
        self._table = table
        self._len = len
        self._transposed = transposed
        self.setSectionsClickable(True)
        self.setSectionsMovable(False)

    def contextMenuEvent(self : Self, a0 : QContextMenuEvent | None) -> None:
        if a0 is None:
            logger().warning("No event")
            return
        o = Qt.Orientation
        if (self.orientation() == o.Horizontal and not self._transposed) \
        or (self.orientation() == o.Vertical and self._transposed):
            pos = a0.pos()
            if self.orientation() == o.Horizontal:
                section = self.logicalIndexAt(pos.x())
            else:
                section = self.logicalIndexAt(pos.y())
            if section >= 0 and section < self._len:
                self._showContextMenu(section, a0.globalPos())
            else:
                super().contextMenuEvent(a0)
        else:
            super().contextMenuEvent(a0)

    def _showContextMenu(self : Self, header_index : int, global_pos : QPoint):
        menu = Menu(self)
        menu_font = menu.font()
        font_metrics = QFontMetrics(menu_font)
        text_height = font_metrics.height()
        icon_size = QSize(text_height, text_height)
        if self._table._transposed:
            asc_arrow = "\u25c0"
            desc_arrow = "\u25b6"
        else:
            asc_arrow = "\u25b2"
            desc_arrow = "\u25bc"
        sort_asc = QAction("Sort Ascending", menu)
        sort_asc.setIcon(getCharIcon("Arial", asc_arrow, icon_size))
        sort_asc.triggered.connect(
            lambda: self._table._parent._sortAscending(header_index)
        )
        menu.addAction(sort_asc)
        sort_desc = QAction("Sort Descending", menu)
        sort_desc.setIcon(getCharIcon("Arial", desc_arrow, icon_size))
        sort_desc.triggered.connect(
            lambda: self._table._parent._sortDescending(header_index)
        )
        menu.addAction(sort_desc)
        unsorted = QAction("Reset Sorting", menu)
        unsorted.setIcon(getCharIcon("Arial", "-", icon_size))
        unsorted.triggered.connect(
            lambda: self._table._parent._sortNone(header_index)
        )
        menu.addAction(unsorted)
        menu.exec(global_pos)

class SpreadsheetTable(QTableView):
    """
    Table for editing properties and attributes of scene items of a single
    type.
    """

    _parent     : SpreadsheetWidget
    _undo_stack : QUndoStack
    _model      : QStandardItemModel | QTransposeProxyModel
    _transposed : bool
    _styled     : bool

    @checked
    def __init__(
        self       : Self,
        undo_stack : QUndoStack,
        model      : QStandardItemModel | QTransposeProxyModel,
        parent     : SpreadsheetWidget
    ) -> None:
        super().__init__(parent)
        self._parent = parent
        self.setModel(model)
        self._model = model
        self._undo_stack = undo_stack
        self._transposed = isinstance(model, QTransposeProxyModel)
        # custom headers
        self.setHorizontalHeader(SpreadsheetHeader(
            self,
            Qt.Orientation.Horizontal,
            self._model.columnCount(),
            self._transposed
        ))
        self.setVerticalHeader(SpreadsheetHeader(
            self,
            Qt.Orientation.Vertical,
            self._model.rowCount(),
            self._transposed
        ))
        # appearance and behavior
        self.setSortingEnabled(False)  # disable built-in sorting
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed
        )
        self.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.resizeColumnsToContents()
        # corner button styling
        self._styled = False

    def showEvent(self : Self, a0 : QShowEvent | None) -> None:
        if a0 is None:
            logger().warning("No event")
            return
        super().showEvent(a0)
        self.style_corner_button()

    def wheelEvent(self : Self, a0 : QWheelEvent | None) -> None:
        """Handle mouse wheel events to adjust font size when Ctrl is pressed."""
        if a0 is None:
            logger().warning("No event")
            return
        modifiers = a0.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            widget : SpreadsheetWidget = self._parent
            tab_widget : SpreadsheetTabWidget = widget._parent
            delta = a0.angleDelta().y()
            if delta > 0:
                tab_widget.increaseFontSize()
            elif delta < 0:
                tab_widget.decreaseFontSize()
            a0.accept()
        else:
            super().wheelEvent(a0)

    def contextMenuEvent(self : Self, a0 : QContextMenuEvent | None) -> None:
        """Show context menu for table cells."""
        if a0 is None:
            logger().warning("No event")
            return
        menu = Menu(self)
        menu.addAction(self._parent._actions.unsort)
        menu.addAction(self._parent._actions.transpose)
        menu.exec(a0.globalPos())

    def style_corner_button(self : Self) -> None:
        if self._styled:
            return
        self._styled = True
        buttons = self.findChildren(QAbstractButton)
        if buttons:
            corner_button = buttons[0]
            corner_button.setStyleSheet('background-color: palette(mid);')

class SpreadsheetWidget(QWidget):
    """
    Widget containing normal and transposed SpreadsheetTable instances and
    a toolbar.
    """

    _parent           : SpreadsheetTabWidget
    _model            : QStandardItemModel
    _proxy            : QTransposeProxyModel
    _transposed       : bool
    _sorting          : dict[int, Qt.SortOrder]
    _sorted_model     : QStandardItemModel
    _sorted_proxy     : QTransposeProxyModel
    _table_model      : SpreadsheetTable
    _table_proxy      : SpreadsheetTable
    _actions          : SimpleNamespace
    _transpose_button : QPushButton
    _unsort_button    : QPushButton
    _toolbar          : QHBoxLayout
    _layout           : QVBoxLayout

    @checked
    def __init__(
        self     : Self,
        model    : QStandardItemModel,
        proxy    : QTransposeProxyModel,
        parent   : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        if not isinstance(parent, SpreadsheetTabWidget):
            raise ValueError("Parent is not a SpreadsheetTabWidget")
        self._parent = parent
        self._undo_stack = QUndoStack()
        self._transposed = False
        # models and proxies
        self._model = model
        self._proxy = proxy
        self._sorted_model = QStandardItemModel()
        self._sorted_proxy = QTransposeProxyModel()
        self._sorted_proxy.setSourceModel(self._sorted_model)
        # tables
        self._table_model = SpreadsheetTable(self._undo_stack, self._model, self)
        self._table_proxy = SpreadsheetTable(self._undo_stack, self._proxy, self)
        # toolbar
        self._transpose_button = QPushButton("Transpose")
        self._transpose_button.setCheckable(True)
        self._transpose_button.clicked.connect(self._toggleTranspose)
        self._unsort_button = QPushButton("Reset Sorting")
        self._unsort_button.clicked.connect(self._resetSorting)
        self._toolbar = QHBoxLayout()
        self._toolbar.addWidget(self._transpose_button)
        self._toolbar.addWidget(self._unsort_button)
        self._toolbar.addStretch()
        # layout
        self._layout = QVBoxLayout(self)
        self._layout.addLayout(self._toolbar)
        self._layout.addWidget(self._table_model)
        self._layout.addWidget(self._table_proxy)
        self._table_proxy.hide()
        self.setLayout(self._layout)
        # highlighting
        self._model.dataChanged.connect(self.onDataChanged)
        # actions for context menu
        self._actions = SimpleNamespace()
        self._actions.unsort = QAction("Reset Sorting", self)
        self._actions.unsort.triggered.connect(self._resetSorting)
        self._actions.transpose = QAction("Transpose", self)
        self._actions.transpose.setCheckable(True)
        self._actions.transpose.setChecked(self._transposed)
        self._actions.transpose.triggered.connect(self._toggleTranspose)
        # initial sorting
        self._sorting = {}
        self._multiSort()

    def onDataChanged(
        self         : Self,
        top_left     : QModelIndex,
        bottom_right : QModelIndex,
        roles        : list[int]
    ) -> None:
        for row in range(top_left.row(), bottom_right.row() + 1):
            for col in range(top_left.column(), bottom_right.column() + 1):
                item = self._model.item(row, col)
                if not isinstance(item, SpreadsheetCell):
                    raise ValueError("Item is not a SpreadsheetCell")
                if item.changed():
                    item.setBackground(self._parent._highlight)
                else:
                    item.setBackground(self._parent._transparent)

    def _completeEditing(self : Self) -> None:
        """Complete any active cell editing in both table views."""
        for table in [self._table_model, self._table_proxy]:
            current_index = table.currentIndex()
            if current_index.isValid():
                table.closePersistentEditor(current_index)
                model = table.model()
                if model is None:
                    raise RuntimeError("No model")
                table.setCurrentIndex(model.createIndex(-1, -1))
        self._table_model.clearFocus()
        self._table_proxy.clearFocus()

    def _toggleTranspose(self : Self, checked : bool | None = None) -> None:
        """Toggle between normal and transposed table views."""
        self._completeEditing()
        if checked is None:
            self._transposed = not self._transposed
        else:
            self._transposed = checked
        if self._transposed:
            self._table_model.hide()
            self._table_proxy.show()
        else:
            self._table_proxy.hide()
            self._table_model.show()

    def _resetSorting(self : Self) -> None:
        """Reset all sorting."""
        self._completeEditing()
        self._sorting.clear()
        self._multiSort()
        self._updateHeaderText()

    def _sortAscending(self : Self, header_index : int) -> None:
        """Sort the selected header in ascending order."""
        self._completeEditing()
        self._sorting[header_index] = Qt.SortOrder.AscendingOrder
        self._multiSort()
        self._updateHeaderText()

    def _sortDescending(self : Self, header_index : int) -> None:
        """Sort the selected header in descending order."""
        self._completeEditing()
        self._sorting[header_index] = Qt.SortOrder.DescendingOrder
        self._multiSort()
        self._updateHeaderText()

    def _sortNone(self : Self, header_index : int) -> None:
        """Remove sorting from the selected header."""
        self._completeEditing()
        if header_index in self._sorting:
            del self._sorting[header_index]
            self._multiSort()
            self._updateHeaderText()

    def _updateHeaderText(self : Self) -> None:
        """Update header text to include sort indicators."""
        for i in range(self._model.columnCount()):
            if (horizontal_header_item := self._model.horizontalHeaderItem(i)) is None:
                raise RuntimeError("No horizontal header item")
            name = horizontal_header_item.text()
            if i in self._sorting:
                order = self._sorting[i]
                if self._transposed:
                    arrow = "\u25c0" if order == Qt.SortOrder.AscendingOrder else "\u25b6"
                else:
                    arrow = "\u25b2" if order == Qt.SortOrder.AscendingOrder else "\u25bc"
                if len(self._sorting) > 1:
                    priority = list(self._sorting.keys()).index(i) + 1
                    text = f"{name}  {arrow}{priority}"
                else:
                    text = f"{name}  {arrow}"
            else:
                text = name
            self._sorted_model.setHorizontalHeaderItem(i, QStandardItem(text))

    def _multiSort(self : Self) -> None:
        """Apply multi-column sorting."""
        def update():
            self._table_model.resizeColumnsToContents()
            self._table_model.resizeRowsToContents()
            self._table_proxy.resizeColumnsToContents()
            self._table_proxy.resizeRowsToContents()

        def multi_column_compare(row1 : tuple, row2 : tuple) -> int:
            """Compare two rows using multi-column sorting priority."""
            _, data1 = row1
            _, data2 = row2
            for column in reversed(self._sorting.keys()):
                if column >= len(data1) or column >= len(data2):
                    continue
                val1 = data1[column]
                val2 = data2[column]
                order = self._sorting[column]
                # Handle empty values
                if not val1 and not val2:
                    continue
                if not val1:
                    return -1 if order == Qt.SortOrder.AscendingOrder else 1
                if not val2:
                    return 1 if order == Qt.SortOrder.AscendingOrder else -1
                # Try numeric comparison first
                try:
                    num1 = float(val1)
                    num2 = float(val2)
                    if num1 != num2:
                        result = -1 if num1 < num2 else 1
                        return result if order == Qt.SortOrder.AscendingOrder else -result
                except ValueError:
                    # Fall back to string comparison
                    if val1 != val2:
                        result = -1 if val1 < val2 else 1
                        return result if order == Qt.SortOrder.AscendingOrder else -result
            return 0  # Equal on all columns

        # build self._sorted_model from self._model and self._sorting
        if not self._sorting:
            # No sorting applied, switch back to original models
            self._table_model.setModel(self._model)
            self._table_proxy.setModel(self._proxy)
            update()
            return
        # get rows from original model
        raw_rows = []
        for row in range(self._model.rowCount()):
            row_data = []
            for col in range(self._model.columnCount()):
                item = self._model.item(row, col)
                row_data.append(item.text() if item else "")
            raw_rows.append(row_data)
        # create indexed rows for sorting
        rows = {i: row_data for i, row_data in enumerate(raw_rows)}
        # sort the rows
        from functools import cmp_to_key
        sorted_rows = sorted(rows.items(), key=cmp_to_key(multi_column_compare))
        # create sorted model with same structure as original
        self._sorted_model.clear()
        self._sorted_model.setRowCount(self._model.rowCount())
        self._sorted_model.setColumnCount(self._model.columnCount())
        # copy headers from original model
        for col in range(self._model.columnCount()):
            header_item = self._model.horizontalHeaderItem(col)
            if header_item:
                self._sorted_model.setHorizontalHeaderItem(col, QStandardItem(header_item.text()))
        for row in range(self._model.rowCount()):
            header_item = self._model.verticalHeaderItem(row)
            if header_item:
                self._sorted_model.setVerticalHeaderItem(row, QStandardItem(header_item.text()))
        # populate sorted model with sorted data
        for sorted_row, (original_row, row_data) in enumerate(sorted_rows):
            for col in range(self._model.columnCount()):
                original_item = self._model.item(original_row, col)
                if original_item:
                    # create new cell with original data and formatting
                    new_item = SpreadsheetCell(original_item.data(Qt.ItemDataRole.UserRole))
                    new_item.setText(original_item.text())
                    new_item.setBackground(original_item.background())
                    self._sorted_model.setItem(sorted_row, col, new_item)
        # update proxy
        self._sorted_proxy.setSourceModel(self._sorted_model)
        # update tables
        self._table_model.setModel(self._sorted_model)
        self._table_proxy.setModel(self._sorted_proxy)
        update()

class SpreadsheetTabWidget(QTabWidget):
    _tab_items      : dict[str, list[QGraphicsItem]]
    _tab_headings   : dict[str, dict[str, bool]]
    _tab_htypenames : dict[str, dict[str, str]]
    _tab_models     : dict[str, QStandardItemModel]
    _tab_proxies    : dict[str, QTransposeProxyModel]
    _tabs           : dict[str, SpreadsheetWidget]
    _delegates      : dict[str, QStyledItemDelegate]
    _transparent    : QBrush
    _highlight      : QBrush
    _font_size      : int

    @checked
    def __init__(
        self   : Self,
        items  : list[QGraphicsItem],
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)
        # group items by type
        self._tab_items = {}
        scene = None
        for item in items:
            if scene is None:
                scene = item.scene()
            elif scene != item.scene():
                logger().error("Items must belong to the same scene")
                items = []
                break
            tab_name = type(item).__name__
            if tab_name not in self._tab_items:
                self._tab_items[tab_name] = []
            self._tab_items[tab_name].append(item)
        # create models
        self._tab_headings   = {}
        self._tab_htypenames = {}
        self._tab_models     = {}
        self._tab_proxies    = {}
        #for tab_name, tab_items in self._tab_items.items():
        #    self._tab_headings[tab_name] = {}
        #    self._tab_htypenames[tab_name] = {}
        #    tab_attributes = None
        #    tab_properties = set()
        #    for e in tab_items:
        #        if tab_attributes is None:
        #            tab_attributes = e.getAttributes()
        #            for a in tab_attributes:
        #                self._tab_htypenames[tab_name][a] = \
        #                    e.getAttributeKind(a)
        #        else:
        #            if tab_attributes != e.getAttributes():
        #                logger().error("Inconsistent inherent properties")
        #                self._tab_items.pop(tab_name)
        #                self._tab_headings.pop(tab_name)
        #                self._tab_htypenames.pop(tab_name)
        #                break
        #        for p in e.getProperties():
        #            tab_properties.add(p)
        #            self._tab_htypenames[tab_name][p] = "str"
        #    self._tab_headings[tab_name] = \
        #        {name : False for name in sorted(tab_properties)}
        #    self._tab_headings[tab_name].update(
        #        {name : True for name in tab_attributes}
        #    )
        #    num_items = len(tab_items)
        #    num_headings = len(self._tab_headings[tab_name])
        #    self._tab_models[tab_name] = QStandardItemModel(
        #        num_items, num_headings, self
        #    )
        #    self._tab_proxies[tab_name] = QTransposeProxyModel()
        #    self._tab_proxies[tab_name].setSourceModel(self._tab_models[tab_name])
        #    for i, name in enumerate(self._tab_headings[tab_name].keys()):
        #        self._tab_models[tab_name].setHorizontalHeaderItem(
        #            i, QStandardItem(name)
        #        )
        #    for i in range(num_items):
        #        self._tab_models[tab_name].setVerticalHeaderItem(
        #            i, QStandardItem(str(i + 1))
        #        )
        #    rows = [
        #        [e.getPropAttr(h) for h in self._tab_headings[tab_name].keys()] \
        #            for e in self._tab_items[tab_name]
        #    ]
        #    for row_idx, row in enumerate(rows):
        #        for col_idx, value in enumerate(row):
        #            self._tab_models[tab_name].setItem(
        #                row_idx, col_idx, SpreadsheetCell(value)
        #            )
        # highlight
        self._transparent = QBrush(Qt.GlobalColor.transparent)
        self.updateHighlight()
        settings().changed.connect(self.updateHighlight)
        # create tabs
        self._tabs = {}
        for tab_name, tab_items in self._tab_items.items():
            self._tabs[tab_name] = SpreadsheetWidget(
                model=self._tab_models[tab_name],
                proxy=self._tab_proxies[tab_name],
                parent=self
            )
            self.addTab(self._tabs[tab_name], tab_name)
        self.setCurrentWidget(self.widget(0))
        # setup delegates
        self._delegates = {}
        self._setupDelegates()
        # initialize font size
        self.setFontSize(settings().get("display/font_size"))

    def closeTab(self : Self, index : int) -> None:
        """Close the tab at the given index."""
        self.removeTab(index)
        if self.count() == 0:
            if not isinstance(parent := self.parent(), QWidget):
                raise TypeError("Bad parent")
            parent.close()

    def updateHighlight(self : Self) -> None:
        if settings().get("display/theme") == "dark":
            self._highlight = QBrush(Qt.GlobalColor.darkYellow)
        else:
            self._highlight = QBrush(Qt.GlobalColor.yellow)

    def _setupDelegates(self : Self) -> None:
        def _setupDelegate(
            tab_name : str,
            idx      : int,
            kind     : str,
            delegate : QStyledItemDelegate
        ) -> None:
            if kind not in self._delegates:
                self._delegates[kind] = delegate
                self._delegates[kind].destroyed.connect(
                    lambda: self.onDelegateDestroyed()
                )
            tab = self._tabs[tab_name]
            tab._table_model.setItemDelegateForColumn(idx, self._delegates[kind])
            tab._table_proxy.setItemDelegateForRow(idx, self._delegates[kind])

        for tab_name, tab_htypenames in self._tab_htypenames.items():
            for idx, name in enumerate(self._tab_headings[tab_name].keys()):
                kind = tab_htypenames[name]
                match kind:
                    case "APLoc":
                        _setupDelegate(
                            tab_name, idx, kind, SpreadsheetAPDelegate()
                        )
                    case _:
                        pass

    def onDelegateDestroyed(self : Self) -> None:
        """Workaround to fix delegate lifecycle issue (silent crash)."""
        pass

    def increaseFontSize(self : Self) -> None:
        self._font_size = min(self._font_size + 1, 20)
        self.setFontSize(self._font_size)

    def decreaseFontSize(self : Self) -> None:
        self._font_size = max(self._font_size - 1, 6)
        self.setFontSize(self._font_size)

    def setFontSize(self : Self, size : int) -> None:
        """Set the font size for all tables."""
        self._font_size = size
        font = QFont()
        font.setPointSizeF(size)
        for tab in self._tabs.values():
            tab._table_model.setFont(font)
            tab._table_model.resizeColumnsToContents()
            tab._table_model.resizeRowsToContents()
            tab._table_proxy.setFont(font)
            tab._table_proxy.resizeColumnsToContents()
            tab._table_proxy.resizeRowsToContents()


class SpreadsheetSubWindow(DocSubWindow):
    _scene      : DiagramScene
    _tab_widget : QTabWidget | None

    @checked
    def __init__(
            self  : Self,
            scene : DiagramScene,
            items : list[QGraphicsItem]
        ) -> None:
        super().__init__()
        self._scene = scene
        item_scenes = {item.scene() for item in items}
        if len(item_scenes) != 1:
            logger().error("Items must belong to the same scene")
            items = []
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        if len(items) > 0:
            self._tab_widget = SpreadsheetTabWidget(items, self)
            self.setWidget(self._tab_widget)
            self.setWindowTitle("Properties")
        else:
            self._tab_widget = None
            label = QLabel("NO ITEMS", self)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.setWidget(label)
            self.setWindowTitle("Properties")

    def closeEvent(self : Self, closeEvent : QCloseEvent | None) -> None:  # noqa: N803
        """Handle subwindow close event."""
        if closeEvent is None:
            logger().warning("No close event")
            return
        if (menu_bar := window().menuBar()) is None:
            raise RuntimeError("No menu bar")
        menu_bar.updateWindowMenu()
        super().closeEvent(closeEvent)

    def scene(self : Self) -> DiagramScene:
        """To play nicely with the MDI area."""
        return self._scene
