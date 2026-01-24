from typing import Self

from PyQt6.QtCore    import QTimer
from PyQt6.QtWidgets import QWidget, QDialog, QColorDialog, QLineEdit, \
                            QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtGui     import QColor

from .layout.ok_cancel import OkCancelLayout


class CustomColorDialog(QColorDialog):
    def __init__(
        self   : Self,
        color  : QColor  | None,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Color")
        self.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        if isinstance(color, QColor):
            self.setCurrentColor(color)
        self._html_box = None
        self._find_html_box()
        self.currentColorChanged.connect(self._on_color_changed)

    def _find_html_box(self : Self) -> None:
        for line_edit in self.findChildren(QLineEdit):
            if line_edit.text().startswith("#"):
                self._html_box = line_edit
                line_edit.textChanged.connect(self._on_html_text_changed)
                self._make_uppercase()
                return
        # If not found yet, try again after a short delay
        # (dialog might still be initializing)
        if self._html_box is None:
            QTimer.singleShot(100, self._find_html_box)

    def _make_uppercase(self : Self) -> None:
        if self._html_box:
            current_text = self._html_box.text()
            if current_text.startswith("#") and current_text != current_text.upper():
                self._html_box.textChanged.disconnect(self._on_html_text_changed)
                self._html_box.setText(current_text.upper())
                self._html_box.textChanged.connect(self._on_html_text_changed)

    def _on_color_changed(self : Self, color : QColor) -> None:
        QTimer.singleShot(10, self._make_uppercase)

    def _on_html_text_changed(self : Self, text : str) -> None:
        if text.startswith("#") and text != text.upper():
            self._make_uppercase()

    def getChoice(self : Self) -> QColor | None:
        return self.currentColor()


class CustomLineWidthDialog(QDialog):
    def __init__(
        self    : Self,
        initial : float | int | None = None,
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Line Width")
        self.dialog_layout = QVBoxLayout()
        # width section
        self.width_layout = QHBoxLayout()
        self.width_label = QLabel("Width:")
        self.width_layout.addWidget(self.width_label)
        self.width_input = QLineEdit("" if initial is None else str(initial))
        self.width_layout.addWidget(self.width_input)
        self.dialog_layout.addLayout(self.width_layout)
        # ok/cancel section
        self._ok_cancel_layout = OkCancelLayout(self)
        self.dialog_layout.addLayout(self._ok_cancel_layout)
        # set layout
        self.setLayout(self.dialog_layout)

    def getChoice(self : Self) -> float | None:
        try:
            return float(self.width_input.text())
        except ValueError:
            return None
