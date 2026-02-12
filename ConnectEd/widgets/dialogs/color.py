from typing import Self

from PyQt6.QtCore    import QTimer
from PyQt6.QtWidgets import QWidget, QColorDialog, QLineEdit
from PyQt6.QtGui     import QColor


class ColorDialog(QColorDialog):
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

    def value(self : Self) -> QColor | None:
        return self.currentColor()

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
