from typing import Self

from PyQt6.QtCore    import Qt, QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ....app import settings

from ....core.defs  import WIDTH
from ....core.types import RectHandleId, SymbolPinHandleId, DataKind
from ....core.check import checked

from ..properties import PropertyTextSpec

from ..scenes import withScene

from .port_pin import PortPinMixin
from .base_pin import BasePinArrowItem, BasePinItem, \
                      BasePinDotMixin, BasePinClockMixin

from .mixin.transform import ItemTransformMixin
from .mixin.handle    import ItemHandlesMixin
from .mixin.line      import ItemLineMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView
    from ..scenes.drawing import DrawingScene


class SymbolPinArrowItem(BasePinArrowItem):
    pass


class SymbolPinItem(
    ItemTransformMixin,
    ItemHandlesMixin[SymbolPinHandleId],
    BasePinDotMixin,
    BasePinClockMixin,
    BasePinItem
):
    # class attributes
    _ARROW_CLASS = SymbolPinArrowItem
    _PROPERTIES = \
        PortPinMixin._PROPERTIES_NAME         | \
        PortPinMixin._PROPERTIES_DIR          | \
        PortPinMixin._PROPERTIES_COMMENT      | \
        BasePinDotMixin._PROPERTIES_DOT       | \
        BasePinClockMixin._PROPERTIES_CLOCK   | \
        ItemTransformMixin._PROPERTIES_POS    | \
        ItemTransformMixin._PROPERTIES_ROTATE | \
        ItemLineMixin._PROPERTIES_LINE
    _PROPERTY_TEXTS = {
            "Name" : PropertyTextSpec(
                cleat=SymbolPinHandleId.NAME, origin=RectHandleId.MIDDLE_LEFT
            )
        }

    @classmethod
    def handleIdType(cls) -> type[SymbolPinHandleId]:
        return SymbolPinHandleId

    @classmethod
    def handleIdKind(cls) -> DataKind:
        return DataKind.SYMBOL_PIN_HANDLE

    @checked
    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
        self.onSettingsChange(scene)

    @checked
    def onSettingsChange(self : Self, scene : "DrawingScene | None" = None) -> None:
        self._setPath(scene)

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action(
                "Dot",
                lambda: view.ui.editSymbolPinDot(self, not self._dot),
                checked=self._dot
            ),
            view.action(
                "Clock",
                lambda: view.ui.editSymbolPinClock(self, not self._clock),
                checked=self._clock
            )
        ]

    @withScene
    @checked
    def _setPath(self : Self, scene : "DrawingScene | None" = None) -> None:
        item_name = self.settingsName()
        # set path
        key = (self._dot, self._clock)
        self.setPath(scene.resources[item_name][key])
        # update name handle position
        pin_settings_path = f"theme/items/{item_name}"
        # standard offset
        name_offset = WIDTH
        # allow for pen width
        pen_style = settings().get(f"{pin_settings_path}/line/style")
        if pen_style != Qt.PenStyle.NoPen:
            pen_width = settings().get(f"{pin_settings_path}/line/width")
            name_offset += (pen_width / 2)
        # allow for clock
        if self._clock:
            clk_settings_path = f"{pin_settings_path}Clk"
            clk_size = settings().get(f"{clk_settings_path}/size")
            name_offset += clk_size
        # finalize
        self._handles[SymbolPinHandleId.NAME].setPos(QPointF(name_offset, 0))
