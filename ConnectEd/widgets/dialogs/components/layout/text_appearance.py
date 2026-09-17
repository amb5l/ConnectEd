from __future__ import annotations

from typing import Self

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt6.QtGui     import QColor

from .....core.check import checked
from .....core.types import RectHandleId

from ....graphics.quill import Quill

from ....graphics.items.text import TextAppearanceState, BaseTextItem

from ..group_box.text_orientation import TextOrientationGroupBox
from ..group_box.text_align       import TextAlignGroupBox
from ..group_box.text_padding     import TextPaddingGroupBox
from ..group_box.origin           import OriginGroupBox
from ..group_box.text_typography  import TextTypographyPreviewGroupBox

from .ok_cancel  import OkCancelLayout

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....graphics.views.diagram  import DiagramView
    from ....graphics.items.base_text import BaseTextAppearanceState
    from ...items.text import BaseTextItemDialog


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
        source : BaseTextItem | tuple[BaseTextAppearanceState, Quill],
        dialog : BaseTextItemDialog,
        view   : DiagramView
    ):
        # superclass init
        super().__init__(dialog)

        # get state
        if isinstance(source, BaseTextItem):
            state = BaseTextAppearanceState.fromItem(source)
            scene = view.scene()
            if scene is None:
                raise ValueError("Scene is None")
            theme = source.themeQuill(scene)
        else:
           state, theme = source
        self._enabled = True
        # middle left - rotation, alignment and origin
        self._left_layout = QVBoxLayout()
        self._orientation_group_box = TextOrientationGroupBox(
            state.rotation, state.mirror_h, state.mirror_v, state.autoflip
        )
        self._left_layout.addWidget(self._orientation_group_box)
        self._align_group_box = TextAlignGroupBox(state.align_h, state.align_v)
        self._left_layout.addWidget(self._align_group_box)
        if not isinstance(origin := state.origin, RectHandleId):
            raise TypeError("Bad origin")
        self._origin_group_box = OriginGroupBox(origin)
        self._left_layout.addWidget(self._origin_group_box)
        # middle right — padding and appearance
        self._right_layout = QVBoxLayout()
        self._padding_group_box = TextPaddingGroupBox(
            state.pad_top, state.pad_bottom, state.pad_left, state.pad_right
        )
        self._right_layout.addWidget(self._padding_group_box)
        self._typography_group_box = TextTypographyPreviewGroupBox(

            item.textColor(),
            item.textFont(),
            item.textSize(),
            item.textBold(),
            item.textItalic(),
            item.textUnderline(),
            default_color,
            default_font,
            default_size,
            default_bold,
            default_italic,
            default_underline
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

    # override replaces normal layout enable behaviour
    def isEnabled(self : Self) -> bool:
        return self._enabled

    # override replaces normal layout enable behaviour
    def setEnabled(self : Self, enabled : bool) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        self._enabled = enabled
        self._setItemsEnabled(self, enabled)

    def _setItemsEnabled(self, layout, enabled: bool) -> None:
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item is None:
                continue
            if (widget := item.widget()) is not None:
                widget.setEnabled(enabled)
            elif (child := item.layout()) is not None:
                self._setItemsEnabled(child, enabled)
