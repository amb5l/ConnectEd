from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem, QMenu
from PyQt6.QtGui     import QAction, QColor

from ....core.defs  import PITCH, WIDTH
from ....core.check import checked
from ....core.types import AlignH, AlignV, RectHandleId, DataKind, NO_CHANGE
from ....core.utils import val2str

from ..properties import InherentProperty

from .text import TextItem
from .grip import GripShape

from .mixin.transform import ItemTransformMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...dialogs.items.net_label import NetLabelItemDialog
    from ..views.drawing import DrawingView


class NetLabelItem(TextItem):
    # class attributes
    _ORIGIN = RectHandleId.BOTTOM_LEFT
    _ORIGIN_GRIP_SHAPE = GripShape.STAR
    _PROPERTIES = \
        {
            "Name" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self.name(),
                setter = lambda self, value: self.setName(value)
            ),
            "Value" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self.value(),
                setter = lambda self, value: self.setValue(value)
            )
        } | \
        TextItem._PROPERTIES_POS         | \
        TextItem._PROPERTIES_ROTATE      | \
        TextItem._PROPERTIES_RECT_ORIGIN | \
        TextItem._PROPERTIES_ALIGN       | \
        TextItem._PROPERTIES_SIZE        | \
        TextItem._PROPERTIES_PADDING     | \
        TextItem._PROPERTIES_TEXT

    # instance attributes
    _name  : str
    _value : str

    @checked
    def __init__(
        self       : Self,
        name       : str                  = "",
        value      : str                  = "",
        pos        : QPointF       | None = None,
        rotation   : float                = 0.0,
        mirror_h   : bool                 = False,
        mirror_v   : bool                 = False,
        autoflip   : bool                 = True,
        origin     : RectHandleId         = RectHandleId.BOTTOM_LEFT,
        align_h    : AlignH               = AlignH.LEFT,
        align_v    : AlignV               = AlignV.TOP,
        width      : float                = -1.0,
        height     : float                = PITCH,
        pad_left   : float                = 2 * WIDTH,
        pad_right  : float                = 2 * WIDTH,
        pad_top    : float                = 0.0,
        pad_bottom : float                = 0.0,
        color      : QColor        | None = None,
        font       : str           | None = None,
        size       : float         | None = None,
        bold       : bool          | None = None,
        italic     : bool          | None = None,
        underline  : bool          | None = None,
        fresh      : bool                 = True,
        parent     : QGraphicsItem | None = None
    ) -> None:
        super().__init__(
            pos        = pos,
            rotation   = rotation,
            mirror_h   = mirror_h,
            mirror_v   = mirror_v,
            autoflip   = autoflip,
            origin     = origin,
            align_h    = align_h,
            align_v    = align_v,
            width      = width,
            height     = height,
            pad_left   = pad_left,
            pad_right  = pad_right,
            pad_top    = pad_top,
            pad_bottom = pad_bottom,
            color      = color,
            font       = font,
            size       = size,
            bold       = bold,
            italic     = italic,
            underline  = underline,
            fresh      = fresh,
            parent     = parent
        )
        self._name  = name
        self._value = value
        self.onTextChanged()

    def onPositionChanged(
        self : Self,
        pos  : QPointF | None = None
    ) -> None:
        ItemTransformMixin.onPositionChanged(self, pos)
        self._notifyNetlist()

    @checked
    def setOrigin(self : Self, id : RectHandleId) -> None:
        ItemTransformMixin.setOrigin(self, id)
        self._notifyNetlist()

    def onTextChanged(self : Self) -> None:
        text = val2str(self.value())
        if text == "":
            text = f"<{self._name}>"
        super().setText(text)

    def text(self : Self) -> str:
        raise NotImplementedError("text() is not implemented")

    @checked
    def setText(self : Self, text : str) -> None:
        raise NotImplementedError("setText() is not implemented")

    def block(self : Self) -> bool:
        raise NotImplementedError("block() is not implemented")

    @checked
    def setBlock(self : Self, _block : bool) -> None:
        raise NotImplementedError("setBlock() is not implemented")

    def name(self : Self) -> str:
        return self._name

    @checked
    def setName(self : Self, name : str) -> None:
        self._name = name
        self.onTextChanged()
        self._notifyNetlist()
        self.properties.signalChanges("Name")

    def value(self : Self) -> str:
        return self._value

    @checked
    def setValue(self : Self, value : str) -> None:
        self._value = value
        self.onTextChanged()
        self._notifyNetlist()
        self.properties.signalChanges("Value")

    @checked
    def applyDialog(self : Self, dialog : "NetLabelItemDialog") -> None:
        self._applyDialogCommon(dialog)
        name  = dialog.getName()
        value = dialog.getValue()
        if name  is not NO_CHANGE: self.setName(name)
        if value is not NO_CHANGE: self.setValue(value)

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView", _spos : QPointF) -> list[QAction | QMenu]:
        return [
            view.action(
                "Auto Width",
                lambda: self.setWidth(
                    self.boundingRect().width() if self._width < 0.0 else -1.0
                ),
                self._width < 0.0
            ),
            view.action(
                "Auto Height",
                lambda: self.setHeight(
                    self.boundingRect().height() if self._height < 0.0 else -1.0
                ),
                self._height < 0.0
            ),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]

    def _notifyNetlist(self : Self) -> None:
        scene = self.scene()
        if scene is None:
            return
        from ..scenes.diagram import DiagramScene
        if not isinstance(scene, DiagramScene):
            return
        netlist = scene.netlist
        if hasattr(netlist, "onNetLabelChanged"):
            netlist.onNetLabelChanged(self)
