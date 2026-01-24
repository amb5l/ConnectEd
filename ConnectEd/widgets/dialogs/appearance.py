from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QDialog, QGroupBox, QVBoxLayout
from PyQt6.QtGui     import QShowEvent, QColor

from ..graphics.items import Default, NoChange

from ..graphics.items.mixin.line  import ItemLineMixin
from ..graphics.items.mixin.fill  import ItemFillMixin
from ..graphics.items.mixin.quill import ItemQuillMixin

from .components.layout.line_appearance import LineAppearanceLayout
from .components.layout.fill_appearance import FillAppearanceLayout
from .components.layout.text_appearance import TextAppearancePreviewLayout
from .components.layout.ok_cancel       import OkCancelLayout

from .private import _combinedValue


class AppearanceDialog(QDialog):
    _dialog_layout    : QVBoxLayout
    _line_group_box   : QGroupBox | None
    _line_layout      : LineAppearanceLayout | None
    _fill_group_box   : QGroupBox | None
    _fill_layout      : FillAppearanceLayout | None
    _text_group_box   : QGroupBox | None
    _text_layout      : TextAppearancePreviewLayout | None
    _ok_cancel_layout : OkCancelLayout

    def __init__(
        self   : Self,
        items  : list[ItemLineMixin | ItemFillMixin | ItemQuillMixin],
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        item_count = len(items)
        category_counts = {
            "line" : sum(1 for i in items if isinstance(i, ItemLineMixin)),
            "fill" : sum(1 for i in items if isinstance(i, ItemFillMixin)),
            "text" : sum(1 for i in items if isinstance(i, ItemQuillMixin)),
        }
        category_count = sum(1 for count in category_counts.values() if count > 0)
        if category_counts["line"] > 0:
            if category_count > 1:
                line_group_title = f"Line ({category_counts['line']} item" \
                    "{'s' if category_counts['line'] > 1 else ''})"
                self.line_group_box = QGroupBox(line_group_title)
            else:
                self.line_group_box = None
            self._line_layout = LineAppearanceLayout(
                _combinedValue(items, "lineColor"),
                _combinedValue(items, "lineWidth"),
                _combinedValue(items, "lineStyle"),
                _combinedValue(items, "defaultLineColor"),
                _combinedValue(items, "defaultLineWidth"),
                _combinedValue(items, "defaultLineStyle")
            )
            if category_count > 1:
                self.line_group_box.setLayout(self._line_layout)
                self._dialog_layout.addWidget(self.line_group_box)
            else:
                self._dialog_layout.addLayout(self._line_layout)
        else:
            self.line_group_box = None
            self._line_layout   = None
        if category_counts["fill"] > 0:
            self._fill_group_box = QGroupBox("Fill") if category_count > 1 else None
            self._fill_layout = FillAppearanceLayout(
                _combinedValue(items, "fillColor"),
                _combinedValue(items, "fillStyle"),
                _combinedValue(items, "defaultFillColor"),
                _combinedValue(items, "defaultFillStyle")
            )
            if category_count > 1:
                self._fill_group_box.setLayout(self._fill_layout)
                self._dialog_layout.addWidget(self._fill_group_box)
            else:
                self._dialog_layout.addLayout(self._fill_layout)
        else:
            self._fill_group_box = None
            self._fill_layout    = None
        if category_counts["text"] > 0:
            self._text_group_box = QGroupBox("Text") if category_count > 1 else None
            self._text_layout = (
                _combinedValue(items, "textColor"),
                _combinedValue(items, "textFont"),
                _combinedValue(items, "textSize"),
                _combinedValue(items, "textBold"),
                _combinedValue(items, "textItalic"),
                _combinedValue(items, "textUnderline"),
                _combinedValue(items, "defaultTextColor"),
                _combinedValue(items, "defaultTextFont"),
                _combinedValue(items, "defaultTextSize"),
                _combinedValue(items, "defaultTextBold"),
                _combinedValue(items, "defaultTextItalic"),
                _combinedValue(items, "defaultTextUnderline")
            )
            if category_count > 1:
                self._text_group_box.setLayout(self._text_layout)
                self._dialog_layout.addWidget(self._text_group_box)
            else:
                self._dialog_layout.addLayout(self._text_layout)
        else:
            self._text_group_box = None
            self._text_layout    = None
        self._ok_cancel_layout = OkCancelLayout(self)
        self._dialog_layout.addLayout(self._ok_cancel_layout)
        self.setLayout(self._dialog_layout)
        if item_count > 1:
            title = "Appearance"
        else:
            title = "Line Appearance" if category_counts["line"] > 0 else \
                    "Fill Appearance" if category_counts["fill"] > 0 else \
                    "Text Appearance"
        self.setWindowTitle(title)

    def _adjustComboBoxWidths(self : Self) -> None:
        """Find all combo boxes and set them to the width of the widest one."""
        combo_boxes = []
        # Collect all combo boxes from all layouts
        if self._line_layout is not None:
            for attr_name in ['color_combo', 'width_combo', 'style_combo']:
                if hasattr(self._line_layout, attr_name):
                    combo_boxes.append(getattr(self._line_layout, attr_name))
        if self._fill_layout is not None:
            for attr_name in ['color_combo', 'style_combo']:
                if hasattr(self._fill_layout, attr_name):
                    combo_boxes.append(getattr(self._fill_layout, attr_name))
        if self._text_layout is not None:
            for attr_name in ['color_combo', 'family_combo', 'size_combo',
                            'bold_combo', 'italic_combo', 'underline_combo']:
                if hasattr(self._text_layout, attr_name):
                    combo_boxes.append(getattr(self._text_layout, attr_name))
        if not combo_boxes:
            return
        # Find the maximum width
        max_width = 0
        for combo in combo_boxes:
            # Get the minimum size hint and actual size
            size_hint = combo.sizeHint()
            current_width = max(size_hint.width(), combo.width())
            max_width = max(max_width, current_width)
        # Set all combo boxes to the maximum width
        for combo in combo_boxes:
            combo.setMinimumWidth(max_width)

    def showEvent(self : Self, event : QShowEvent):
        """Override showEvent to adjust combo box widths after layout is complete."""
        super().showEvent(event)
        # Use QTimer.singleShot to defer the width adjustment until after the event loop
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, self._adjustComboBoxWidths)

    def getLineColorChoice(self : Self) -> QColor | Default | NoChange:
        return self._line_layout.getColorChoice()

    def getLineWidthChoice(self : Self) -> float | NoChange | Default:
        return self._line_layout.getWidthChoice()

    def getLineStyleChoice(self : Self) -> Qt.PenStyle | NoChange | Default:
        return self._line_layout.getStyleChoice()

    def getFillColorChoice(self : Self) -> QColor | Default | NoChange:
        return self._fill_layout.getColorChoice()

    def getFillStyleChoice(self : Self) -> Qt.BrushStyle | NoChange | Default:
        return self._fill_layout.getStyleChoice()

    def getTextColorChoice(self : Self) -> QColor | Default | NoChange:
        return self._text_layout.getColor()

    def getTextFontChoice(self : Self) -> str | Default | NoChange:
        return self._text_layout.getFamily()

    def getTextSizeChoice(self : Self) -> float | NoChange | Default:
        return self._text_layout.getSize()

    def getTextBoldChoice(self : Self) -> bool | Default | NoChange:
        return self._text_layout.getBold()

    def getTextItalicChoice(self : Self) -> bool | Default | NoChange:
        return self._text_layout.getItalic()

    def getTextUnderlineChoice(self : Self) -> bool | Default | NoChange:
        return self._text_layout.getUnderline()
