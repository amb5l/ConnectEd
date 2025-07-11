from typing import Self, Optional
from types  import SimpleNamespace

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QMdiSubWindow, QTabWidget, QWidget, QSizePolicy, \
                            QHBoxLayout, QVBoxLayout, \
                            QMenu, QPushButton, QLabel, \
                            QTableView, QAbstractItemView, QAbstractButton
from PyQt6.QtGui     import QFont, QAction, QUndoStack, \
                            QWheelEvent, QContextMenuEvent, QCloseEvent, \
                            QStandardItemModel, QStandardItem

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
    _headings   : dict[str, bool]
    _model      : QStandardItemModel
    #_proxy      : TransposeProxyModel
    _actions    : SimpleNamespace
    _font_size  : int
    _styled     : bool

    def __init__(
        self       : Self,
        scene      : "DrawingScene",
        elements   : list[ElementMixin],
        parent     : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self._undo_stack = scene.undo_stack
        self._elements = elements
        # headings
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
        self._headings = {h : False for h in sorted(properties)}
        self._headings.update({h : True for h in attributes})
        # rows
        rows = [
            [e.getPropAttr(h) for h in self._headings.keys()] for e in elements
        ]
        # model
        self._model = QStandardItemModel(
            len(rows), len(self._headings), self
        )
        for col, heading in enumerate(self._headings.keys()):
            item = QStandardItem(heading)
            font = QFont()
            font.setItalic(self._headings[heading])
            item.setData(font, Qt.ItemDataRole.FontRole)
            self._model.setHorizontalHeaderItem(col, item)
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                item = PropertiesCell(value)
                self._model.setItem(row_idx, col_idx, item)
            self._model.setVerticalHeaderItem(row_idx, QStandardItem(str(row_idx + 1)))
        self.setModel(self._model)
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
        self._actions.transpose.toggled.connect(self.toggleTranspose)
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

    def toggleTranspose(self : Self, checked: Optional[bool] = None) -> None:
        """Toggle the transposed view of the table."""
        #self._proxy.toggleTransposed(checked)
        self.resizeColumnsToContents()
        self.viewport().update()

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

class PropertiesWidget(QWidget):
    """Widget containing a PropertiesTable with buttons for managing properties."""
    _elements         : list[ElementMixin]
    _table            : PropertiesTable
    _transpose_button : QPushButton
    _toolbar          : QHBoxLayout
    _layout           : QVBoxLayout

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[ElementMixin],
        parent   : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self._table = PropertiesTable(scene, elements, self)
        self._transpose_button = QPushButton("Transpose")
        self._transpose_button.clicked.connect(self._table.toggleTranspose)
        self._toolbar = QHBoxLayout()
        self._toolbar.addWidget(self._transpose_button)
        self._toolbar.addStretch()
        self._layout = QVBoxLayout(self)
        self._layout.addLayout(self._toolbar)
        self._layout.addWidget(self._table)
        self.setLayout(self._layout)

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
