from typing import Self

from PyQt6.QtCore    import Qt, QTimer
from PyQt6.QtWidgets import QGraphicsItem, QWidget, QTableView, QVBoxLayout, QHeaderView
from PyQt6.QtGui     import QStandardItemModel, QStandardItem

from .items.grip import Grip


class QueryWindow(QWidget):
    _model  : QStandardItemModel
    _view   : QTableView
    _layout : QVBoxLayout
    _timer  : QTimer

    def __init__(self : Self, element : QGraphicsItem, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Window           |
            Qt.WindowType.WindowTitleHint  |
            Qt.WindowType.WindowStaysOnTopHint
        )
        element_type = element.__class__.__name__
        title = f"Query - {element_type}"
        self.setWindowTitle(title)
        # create model
        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(["Property", "Value"])
        # populate model with element properties if available
        self._populateModel(element)
        # create table view
        self._view = QTableView()
        self._view.setModel(self._model)
        self._view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._view.verticalHeader().setVisible(False)
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

    def _populateModel(self : Self, element : QGraphicsItem) -> None:
        """Populate the model with element properties."""
        if isinstance(element, Grip):
            self._model.appendRow([
                QStandardItem("Position X"),
                QStandardItem(f"{element.scenePos().x()}")
            ])
            self._model.appendRow([
                QStandardItem("Position Y"),
                QStandardItem(f"{element.scenePos().y()}")
            ])
        else:
            for prop_name, prop_value in \
                element.getPropertyNamesAndValues().items():
                self._model.appendRow([
                    QStandardItem(prop_name),
                    QStandardItem(prop_value)
                ])

    def leaveEvent(self, event):
        # Close when mouse leaves the window (with reasonable delay)
        self._timer.start(1000)  # 1 second delay
        super().leaveEvent(event)

    def enterEvent(self, event):
        # Cancel close timer when mouse re-enters
        self._timer.stop()
        super().enterEvent(event)

    def show(self):
        super().show()

    def move(self, *args):
        super().move(*args)

    def closeEvent(self, event):
        super().closeEvent(event)
