from PyQt6.QtWidgets import QDockWidget, QWidget, QVBoxLayout

from ..text_view import TextView
from ..find_bar  import FindBar


class MsgViewer(QDockWidget):
    main_widget : QWidget
    text_view : TextView
    find_bar    : FindBar

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Messages')
        self.text_view = TextView(self)
        self.find_bar = FindBar(self, self.text_view)
        self.text_view.setFindBar(self.find_bar)
        self.main_widget = QWidget()
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.find_bar)
        layout.addWidget(self.text_view)
        self.main_widget.setLayout(layout)
        self.setWidget(self.main_widget)
        self.find_bar.hide()
