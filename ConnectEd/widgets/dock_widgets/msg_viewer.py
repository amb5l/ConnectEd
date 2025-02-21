from PyQt6.QtWidgets import QDockWidget, QWidget, QVBoxLayout

from ...core        import LOG_FILENAME
from ..text_viewer  import TextViewer
from ..find_bar     import FindBar


class MsgViewer(QDockWidget):
    main_widget : QWidget
    text_viewer : TextViewer
    find_bar    : FindBar

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Messages')
        self.text_viewer = TextViewer(self)
        self.find_bar = FindBar(self, self.text_viewer)
        self.main_widget = QWidget()
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.find_bar)
        layout.addWidget(self.text_viewer)
        self.main_widget.setLayout(layout)
        self.setWidget(self.main_widget)
