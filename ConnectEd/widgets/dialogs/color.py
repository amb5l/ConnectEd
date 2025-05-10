__all__ = ["ColorDialog"]

from typing import Self, Optional

from PyQt6.QtCore    import Qt, QRect
from PyQt6.QtWidgets import QColorDialog, QWidget, \
                            QVBoxLayout, QHBoxLayout, \
                            QLabel, QCheckBox, QPushButton
from PyQt6.QtGui     import QColor, QPainter, QFont, QFontMetrics

class OverlayWidget(QWidget):
    def __init__(self : Self, parent : Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.label = QLabel("DEFAULT", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            color: black;
            font-weight: bold;
            background: transparent;
        """)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.updateFontSize()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(64, 64, 64, 224))
        painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateFontSize()

    def updateFontSize(self):
        font_size = int(self.height() * 0.5)
        font = QFont("Arial", font_size, QFont.Weight.Bold)
        metrics = QFontMetrics(font)
        text_width = metrics.boundingRect("DEFAULT").width()
        if text_width > self.width():
            scale_factor = self.width() / text_width * 0.9  # 95% to add padding
            font_size = int(font_size * scale_factor)
            font = QFont("Arial", font_size, QFont.Weight.Bold)
        self.label.setFont(font)

class ColorDialog(QColorDialog):
    def __init__(
        self   : Self,
        color  : tuple[Optional[QColor], QColor],
        parent : Optional[QWidget] = None
    ) -> None:
        specified_color, default_color = color
        super().__init__(parent)
        self.setWindowTitle("Color")
        self.setOption(QColorDialog.ColorDialogOption.NoButtons, True)
        self.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        self.setWindowTitle("Select Color")
        self.setCurrentColor(
            specified_color if specified_color is not None else default_color
        )
        self.default_check = QCheckBox("Default", self)
        self.default_check.setChecked(specified_color is None)
        self.default_check.toggled.connect(self.onDefaultToggled)
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.onOkClicked)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.onCancelClicked)
        layout = self.layout()
        self.xtra_row = QHBoxLayout()
        self.xtra_row.addWidget(self.default_check)
        self.xtra_row.addStretch()
        self.xtra_row.addWidget(self.ok_button)
        self.xtra_row.addWidget(self.cancel_button)
        layout.addLayout(self.xtra_row)
        self.overlay = OverlayWidget(self)
        self.updateOverlayGeometry()
        self.overlay.setVisible(specified_color is None)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateOverlayGeometry()

    def updateOverlayGeometry(self):
        dialog_rect = self.rect()
        custom_row_rect = self.xtra_row.geometry()
        overlay_rect = QRect(
            0, 0,
            dialog_rect.width(),
            custom_row_rect.y()
        )
        overlay_rect = overlay_rect.intersected(dialog_rect)
        self.overlay.setGeometry(overlay_rect)

    def onDefaultToggled(self : Self, checked : bool) -> None:
        self.defaultSelected = checked
        self.overlay.setVisible(checked)  # Show/hide overlay

    def onOkClicked(self : Self) -> None:
        self.accept()

    def onCancelClicked(self : Self) -> None:
        self.reject()

    def getColor(self : Self) -> QColor:
        return None if self.default_check.isChecked() else self.currentColor()

    def setColor(self : Self, color : Optional[QColor]) -> None:
        self.default_check.setChecked(color is None)
        self.setCurrentColor(color)
