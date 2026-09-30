from __future__ import annotations

from typing import Self

from PyQt6.QtWidgets import QDialog, QLayout, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui     import QColor

from typing_extensions import override

from .....core.check              import checked
from .....core.types              import NoChange, AlignH, AlignV, RectHandleId

from ....graphics.presentation    import TextOverrides

from ....graphics.items.base_text import BaseTextItem, BaseTextAppearanceState

from ..group_box.text_orientation import TextOrientationGroupBox
from ..group_box.text_align       import TextAlignGroupBox
from ..group_box.text_padding     import TextPaddingGroupBox
from ..group_box.origin           import OriginGroupBox
from ..group_box.text_typography  import TextTypographyPreviewGroupBox

from .ok_cancel                   import OkCancelLayout

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....graphics.views.diagram import DiagramView


class TextAppearanceLayout(QVBoxLayout):
    _main_layout           : QHBoxLayout
    _left_layout           : QVBoxLayout
    _right_layout          : QVBoxLayout
    _orientation_group_box : TextOrientationGroupBox
    _align_group_box       : TextAlignGroupBox
    _origin_group_box      : OriginGroupBox
    _padding_group_box     : TextPaddingGroupBox
    _typography_group_box  : TextTypographyPreviewGroupBox
    _ok_cancel_layout      : OkCancelLayout
    _enabled               : bool

    @checked
    def __init__(
        self   : Self,
        item   : BaseTextItem,
        dialog : QDialog,
        view   : DiagramView
    ):
        super().__init__()
        state = BaseTextAppearanceState.fromItem(item)
        theme = item.textTheme(view)
        item_override = item.textOverride()
        overrides = TextOverrides(
            color     = item_override.color,
            font      = item_override.font,
            size      = item_override.size,
            bold      = item_override.bold,
            italic    = item_override.italic,
            underline = item_override.underline
        )
        self._enabled = True
        # middle left - rotation, alignment and origin
        self._left_layout = QVBoxLayout()
        self._orientation_group_box = TextOrientationGroupBox(
            state.rotation, state.mirror_h, state.mirror_v, state.autoflip
        )
        self._left_layout.addWidget(self._orientation_group_box)
        self._align_group_box = TextAlignGroupBox(state.align_h, state.align_v)
        self._left_layout.addWidget(self._align_group_box)
        self._origin_group_box = OriginGroupBox(state.origin)
        self._left_layout.addWidget(self._origin_group_box)
        # middle right — padding and appearance
        self._right_layout = QVBoxLayout()
        self._padding_group_box = TextPaddingGroupBox(
            state.pad_top, state.pad_bottom, state.pad_left, state.pad_right
        )
        self._right_layout.addWidget(self._padding_group_box)
        self._typography_group_box = TextTypographyPreviewGroupBox(
            theme, overrides
        )
        self._right_layout.addWidget(self._typography_group_box)
        # middle left and right combined
        self._main_layout = QHBoxLayout()
        self._main_layout.addLayout(self._left_layout)
        self._main_layout.addLayout(self._right_layout)
        self.addLayout(self._main_layout)
        # ok/cancel section
        self._ok_cancel_layout = OkCancelLayout(dialog)
        self.addLayout(self._ok_cancel_layout)

    def getRotation(self : Self) -> float | NoChange:
        return self._orientation_group_box.getRotation()

    def getMirrorH(self : Self) -> bool | NoChange:
        return self._orientation_group_box.getMirrorH()

    def getMirrorV(self : Self) -> bool | NoChange:
        return self._orientation_group_box.getMirrorV()

    def getAutoflip(self : Self) -> bool | NoChange:
        return self._orientation_group_box.getAutoflip()

    def getAlignH(self : Self) -> AlignH | NoChange:
        return self._align_group_box.getAlignH()

    def getAlignV(self : Self) -> AlignV | NoChange:
        return self._align_group_box.getAlignV()

    def getOrigin(self : Self) -> RectHandleId | NoChange:
        return self._origin_group_box.getOrigin()

    def getPadLeft(self : Self) -> float | NoChange:
        return self._padding_group_box.getPadLeft()

    def getPadRight(self : Self) -> float | NoChange:
        return self._padding_group_box.getPadRight()

    def getPadTop(self : Self) -> float | NoChange:
        return self._padding_group_box.getPadTop()

    def getPadBottom(self : Self) -> float | NoChange:
        return self._padding_group_box.getPadBottom()

    def getColor(self : Self) -> QColor | None | NoChange:
        return self._typography_group_box.getColor()

    def getFont(self : Self) -> str | None | NoChange:
        return self._typography_group_box.getFont()

    def getSize(self : Self) -> float | None | NoChange:
        return self._typography_group_box.getSize()

    def getBold(self : Self) -> bool | None | NoChange:
        return self._typography_group_box.getBold()

    def getItalic(self : Self) -> bool | None | NoChange:
        return self._typography_group_box.getItalic()

    def getUnderline(self : Self) -> bool | None | NoChange:
        return self._typography_group_box.getUnderline()

    # replaces QLayout enable behaviour with this layout's own flag
    @override
    def isEnabled(self : Self) -> bool:
        return self._enabled

    # replaces QLayout enable behaviour with this layout's own flag
    @override
    def setEnabled(self : Self, enabled : bool) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        self._enabled = enabled
        self._setItemsEnabled(self, enabled)

    def _setItemsEnabled(self : Self, layout : QLayout, enabled : bool) -> None:
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item is None:
                continue
            if (widget := item.widget()) is not None:
                widget.setEnabled(enabled)
            elif (child := item.layout()) is not None:
                self._setItemsEnabled(child, enabled)
