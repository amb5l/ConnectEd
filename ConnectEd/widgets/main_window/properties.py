from typing import Self, Optional
from types  import SimpleNamespace

from PyQt6.QtCore    import Qt, QModelIndex, QPoint, QRect
from PyQt6.QtWidgets import QMdiSubWindow, QTabWidget, QWidget, QSizePolicy, \
                            QHBoxLayout, QVBoxLayout, \
                            QMenu, QPushButton, QLabel, \
                            QTableView, QAbstractItemView, QAbstractButton, \
                            QHeaderView
from PyQt6.QtGui     import QFont, QAction, QUndoStack, \
                            QWheelEvent, QContextMenuEvent, QCloseEvent, \
                            QStandardItemModel, QStandardItem, \
                            QPen, QBrush, QColor, QPolygon

from ...core import logger

from .. import ElementMixin

from ... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class PropertiesCell(QStandardItem):
    """Custom item for spreadsheet cells, storing string values."""
    def __init__(self : Self, value: any) -> None:
        text_value = "" if value is None else str(value)
        super().__init__(text_value)
        self.setFlags(
            Qt.ItemFlag.ItemIsEditable |
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
        )

class PropertiesTable(QTableView):
    """Table for editing properties of scene elements of a single type."""

    _undo_stack : QUndoStack
    _elements   : list[ElementMixin]
    _transposed : bool
    _inherent   : dict[str, bool]  # field name : is inherent
    _headers    : dict[int, str]  # column # : field name
    _model      : QStandardItemModel
    _actions    : SimpleNamespace
    _font_size  : int
    _styled     : bool
    _sorting    : dict[int, Qt.SortOrder]

    def __init__(
        self       : Self,
        scene      : "DrawingScene",
        elements   : list[ElementMixin],
        transposed : bool,
        parent     : "PropertiesWidget",
        sorting    : Optional[dict[int, Qt.SortOrder]] = None
    ) -> None:
        super().__init__(parent)
        self._undo_stack = scene.undo_stack
        self._elements = elements
        self._transposed = transposed
        self._sorting = sorting if sorting is not None else {}
        # fields and headers
        attributes = None
        properties = set()
        for e in elements:
            if attributes is None:
                attributes = e.getAttributes()
            else:
                if attributes != e.getAttributes():
                    logger.error("Inconsistent inherent properties")
                    return
            for prop in e.getProperties():
                properties.add(prop)
        self._inherent = {h : False for h in sorted(properties)}
        self._inherent.update({h : True for h in attributes})
        self._fields = self._inherent.keys()
        self._headers = {i : h for i, h in enumerate(self._inherent.keys())}
        self.setSortingEnabled(False)  # Disable built-in sorting
        header = self.horizontalHeader()
        header.setSectionsClickable(True)
        header.setSectionsMovable(False)
        header.sectionClicked.connect(self._handleHeaderClick)
        # rows - get the raw data
        raw_rows = [
            [e.getPropAttr(h) for h in self._inherent.keys()] for e in elements
        ]
        # set model
        self._createModel(raw_rows)
        # appearance and behavior
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed
        )
        self.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.setFontSize(10)  # TODO: Get from settings
        self.resizeColumnsToContents()
        # actions
        self._actions = SimpleNamespace()
        self._actions.transpose = QAction("Transpose", self)
        self._actions.transpose.setCheckable(True)
        self._actions.transpose.setChecked(self._transposed)
        self.addAction(self._actions.transpose)
        self._styled = False

    def showEvent(self, event):
        super().showEvent(event)
        self.style_corner_button()

    def style_corner_button(self):
        if self._styled:
            return
        self._styled = True
        buttons = self.findChildren(QAbstractButton)
        if buttons:
            corner_button = buttons[0]
            corner_button.setStyleSheet('background-color: palette(mid);')

    def contextMenuEvent(self : Self, event: QContextMenuEvent) -> None:
        """Show context menu with copy/paste/transpose actions."""
        menu = QMenu(self)
        menu.addAction(self._actions.transpose)
        menu.exec(event.globalPos())

    def setFontSize(self : Self, size: int) -> None:
        """Set the font size for all items in the table."""
        font = QFont()
        font.setPointSize(size)
        self.setFont(font)
        self._font_size = size
        self.resizeColumnsToContents()

    def wheelEvent(self : Self, event: QWheelEvent) -> None:
        """Handle mouse wheel events to adjust font size when Ctrl is pressed."""
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.setFontSize(min(self._font_size + 1, 20))
            elif delta < 0:
                self.setFontSize(max(self._font_size - 1, 6))
            event.accept()
        else:
            super().wheelEvent(event)

    def _handleHeaderClick(self : Self, idx: int) -> None:
        """Handle header clicks for triple-state sorting (asc/desc/unsorted)."""
        match self._sorting.get(idx, None):
            case None:
                self._sorting[idx] = Qt.SortOrder.AscendingOrder
            case Qt.SortOrder.AscendingOrder:
                self._sorting[idx] = Qt.SortOrder.DescendingOrder
            case Qt.SortOrder.DescendingOrder:
                del self._sorting[idx]
        self.multiSort()
        self._updateHeaderText()

    def _updateHeaderText(self) -> None:
        """Update header text to include sort indicators."""
        for i, name in self._headers.items():
            text = name
            if i in self._sorting:
                order = self._sorting[i]
                arrow = "▲" if order == Qt.SortOrder.AscendingOrder else "▼"
                if len(self._sorting) > 1:
                    priority = list(self._sorting.keys()).index(i) + 1
                    text = f"{name}  {arrow}{priority}"
                else:
                    text = f"{name}  {arrow}"
            if self._transposed:
                header_item = self._model.verticalHeaderItem(i)
                if header_item is None:
                    header_item = QStandardItem(text)
                    self._model.setVerticalHeaderItem(i, header_item)
                else:
                    header_item.setText(text)
            else:
                header_item = self._model.horizontalHeaderItem(i)
                if header_item is None:
                    header_item = QStandardItem(text)
                    self._model.setHorizontalHeaderItem(i, header_item)
                else:
                    header_item.setText(text)

    def multiSort(self) -> None:
        """Apply multi-column sorting to the table."""
        if not self._sorting:
            self._restoreOriginalOrder()
            return
        rows = []
        for row_idx in range(self._model.rowCount()):
            row_data = []
            for col_idx in range(self._model.columnCount()):
                item = self._model.item(row_idx, col_idx)
                value = item.text() if item else ""
                row_data.append(value)
            rows.append((row_idx, row_data))

        def multi_column_compare(row1, row2):
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
        # Sort the rows
        from functools import cmp_to_key
        sorted_rows = sorted(rows, key=cmp_to_key(multi_column_compare))
        # Rebuild the model with sorted data
        sorted_data = [row_data for _, row_data in sorted_rows]
        self._model.clear()
        self._createModel(sorted_data)
        self._updateHeaderText()

    def _restoreOriginalOrder(self) -> None:
        """Restore the original order of the table by recreating it."""
        raw_rows = [
            [e.getPropAttr(h) for h in self._inherent.keys()] for e in self._elements
        ]
        self._model.clear()
        self._createModel(raw_rows)
        self._updateHeaderText()

    def _createModel(self, raw_rows: list[list]) -> None:
        """Create the model with the given data."""
        if self._transposed:
            num_properties = len(self._headers)
            num_elements = len(self._elements)
            self._model = QStandardItemModel(num_properties, num_elements, self)
            for i, name in self._headers.items():
                self._model.setVerticalHeaderItem(i, QStandardItem(name))
            for i in range(num_elements):
                self._model.setHorizontalHeaderItem(i, QStandardItem(str(i + 1)))
            for property_idx in range(num_properties):
                for element_idx in range(num_elements):
                    if element_idx < len(raw_rows) and property_idx < len(raw_rows[element_idx]):
                        value = raw_rows[element_idx][property_idx]  # transpose
                        self._model.setItem(property_idx, element_idx, PropertiesCell(value))
        else:
            num_elements = len(raw_rows)
            num_properties = len(self._inherent)
            self._model = QStandardItemModel(num_elements, num_properties, self)
            for i, name in self._headers.items():
                self._model.setHorizontalHeaderItem(i, QStandardItem(name))
            for i in range(num_elements):
                self._model.setVerticalHeaderItem(i, QStandardItem(str(i + 1)))
            for row_idx, row_data in enumerate(raw_rows):
                for col_idx, value in enumerate(row_data):
                    self._model.setItem(row_idx, col_idx, PropertiesCell(value))
        self.setModel(self._model)

class PropertiesWidget(QWidget):
    """Widget containing PropertiesTable instances with buttons for managing properties."""
    _elements         : list[ElementMixin]
    _table_normal     : PropertiesTable
    _table_transposed : PropertiesTable
    _current_table    : PropertiesTable
    _transpose_button : QPushButton
    _toolbar          : QHBoxLayout
    _layout           : QVBoxLayout
    _transposed       : bool
    _sorting          : dict[int, Qt.SortOrder]

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[ElementMixin],
        parent   : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self._elements = elements
        self._transposed = False
        self._sorting = {}
        self._table_normal = PropertiesTable(
            scene, elements, False, self, self._sorting
        )
        self._table_transposed = PropertiesTable(
            scene, elements, True, self, self._sorting
        )
        self._current_table = self._table_normal
        self._transpose_button = QPushButton("Transpose")
        self._transpose_button.setCheckable(True)
        self._transpose_button.clicked.connect(self._toggleTranspose)
        self._toolbar = QHBoxLayout()
        self._toolbar.addWidget(self._transpose_button)
        self._toolbar.addStretch()
        self._layout = QVBoxLayout(self)
        self._layout.addLayout(self._toolbar)
        self._layout.addWidget(self._table_normal)
        self._layout.addWidget(self._table_transposed)
        self._table_transposed.hide()
        self.setLayout(self._layout)

    def _toggleTranspose(self) -> None:
        """Toggle between normal and transposed table views."""
        self._transposed = not self._transposed
        if self._transposed:
            self._table_normal.hide()
            self._table_transposed.show()
            self._current_table = self._table_transposed
        else:
            # Switch to normal view
            self._table_transposed.hide()
            self._table_normal.show()
            self._current_table = self._table_normal
        # Update button state
        self._transpose_button.setChecked(self._transposed)
        # Ensure the visible table is properly sized
        self._current_table.resizeColumnsToContents()
        self._current_table.resizeRowsToContents()

    def getCurrentTable(self) -> PropertiesTable:
        """Get the currently visible table."""
        return self._current_table

class PropertiesTabWidget(QTabWidget):
    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[ElementMixin],
        parent   : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)
        elements_by_type = {}
        for element in elements:
            element_type_name = type(element).__name__
            if element_type_name not in elements_by_type:
                elements_by_type[element_type_name] = []
            elements_by_type[element_type_name].append(element)
        for element_type_name, type_elements in elements_by_type.items():
            tab = PropertiesWidget(scene, type_elements, self)
            self.addTab(tab, element_type_name)
        self.setCurrentWidget(self.widget(0))

    def closeTab(self, index: int) -> None:
        """Close the tab at the given index."""
        self.removeTab(index)
        if self.count() == 0:
            self.parent().close()

class PropertiesSubWindow(QMdiSubWindow):
    _scene      : "DrawingScene"
    _tab_widget : Optional[QTabWidget]

    def __init__(
            self     : Self,
            scene    : "DrawingScene",
            elements : list[ElementMixin]
        ) -> None:
        super().__init__()
        self._scene = scene
        element_scenes = set(element.scene() for element in elements)
        if elements:
            if len(element_scenes) > 1 or scene != element_scenes.pop():
                logger.error("Elements must belong to the specified scene")
                elements = []
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        if len(elements) > 0:
            self._tab_widget = PropertiesTabWidget(scene, elements, self)
            self.setWidget(self._tab_widget)
            self.setWindowTitle("Properties")
        else:
            self._tab_widget = None
            label = QLabel("NO ELEMENTS", self)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.setWidget(label)
            self.setWindowTitle("Properties")

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle subwindow close event."""
        hub.main_window.menu_bar.updateWindowMenu()
        super().closeEvent(event)

    def scene(self : Self) -> "DrawingScene":
        return self._scene
