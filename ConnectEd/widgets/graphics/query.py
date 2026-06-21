from typing import Self, Any
from collections import defaultdict

from PyQt6.QtCore    import Qt, QTimer, QEvent
from PyQt6.QtWidgets import QGraphicsItem, QWidget, QVBoxLayout
from PyQt6.QtGui     import QStandardItemModel, QStandardItem, QCloseEvent

from ..window.tree_view import TreeView

from .properties import PropertiesMixin

from .items.grip import GripItem


class QueryWindow(QWidget):
    _model  : QStandardItemModel
    _view   : TreeView
    _layout : QVBoxLayout
    _timer  : QTimer

    def __init__(self : Self, items : list[QGraphicsItem], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Query")
        self.setWindowFlags(
            Qt.WindowType.Window           |
            Qt.WindowType.WindowTitleHint  |
            Qt.WindowType.WindowStaysOnTopHint
        )
        # create model
        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(["Item", "Property", "Value"])
        # populate model
        hdict = self._getHDict(items)
        self._populate(self._model, hdict)
        for i in range(self._model.rowCount()):
            item = self._model.item(i)
        # create table view
        self._view = TreeView(self._model, self)
        self._view._customizeAppearance()
        self._view.setModel(self._model)
        #self._view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        #self._view.verticalHeader().setVisible(False)
        self._view.setMinimumWidth(300)
        self._view.setMinimumHeight(150)
        self._view.setMaximumHeight(400)
        # Layout
        self._layout = QVBoxLayout()
        self._layout.addWidget(self._view)
        self.setLayout(self._layout)
        # adjust size to content
        self.adjustSize()
        # set up timer for delayed closing
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.close)

    def _getHDict(
        self: Self,
        items: list[QGraphicsItem]
    ) -> dict[QGraphicsItem, dict]:
        if not items:
            return {}
        item_set = set(items)
        child_map: defaultdict[QGraphicsItem, list[QGraphicsItem]] = defaultdict(list)
        roots: list[QGraphicsItem] = []
        for item in items:
            parent = item.parentItem()
            if parent in item_set:
                child_map[parent].append(item)
            else:
                roots.append(item)
        hierarchy: dict[QGraphicsItem, dict] = {}
        for root in roots:
            hierarchy[root] = self._getHDict(child_map[root])
        return hierarchy

    def _populate(
        self: Self,
        obj: QStandardItemModel | QStandardItem,
        hdict: dict[QGraphicsItem | PropertiesMixin, dict]
    ) -> None:
        """Populate the model or item row with hierarchical item data."""
        for item, child_item_dict in hdict.items():
            item_row = QStandardItem(item.__class__.__name__)
            obj.appendRow(item_row)
            # Add property rows
            if isinstance(item, GripItem):
                pos = item.scenePos()
                item_row.appendRow([
                    QStandardItem(),
                    QStandardItem("Position X"),
                    QStandardItem(str(pos.x()))
                ])
                item_row.appendRow([
                    QStandardItem(),
                    QStandardItem("Position Y"),
                    QStandardItem(str(pos.y()))
                ])
            elif isinstance(item, PropertiesMixin):
                for prop_name, prop_value in item.properties.items():
                    item_row.appendRow([
                        QStandardItem(),
                        QStandardItem(prop_name),
                        QStandardItem(prop_value)
                    ])
            # Recurse on children
            if child_item_dict:
                self._populate(item_row, child_item_dict)

    def leaveEvent(self : Self, event : QEvent):
        # Close when mouse leaves the window (with reasonable delay)
        self._timer.start(1000)  # 1 second delay
        super().leaveEvent(event)

    def enterEvent(self : Self, event : QEvent):
        # Cancel close timer when mouse re-enters
        self._timer.stop()
        super().enterEvent(event)

    def show(self : Self):
        super().show()

    def move(self : Self, *args : Any):
        super().move(*args)

    def closeEvent(self : Self, event : QCloseEvent):
        super().closeEvent(event)
