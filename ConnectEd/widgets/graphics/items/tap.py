from typing import Self

from PyQt6.QtCore    import QPointF, QLineF
from PyQt6.QtGui     import QAction
from PyQt6.QtWidgets import QGraphicsLineItem, QMenu

from ....core.defs  import PITCH
from ....core.types import NetState, DataKind, AlignH, AlignV, \
                           RectHandleId, TapHandleId
from ....core.check import checked

from ..properties import PropertiesMixin, InherentProperty, PropertyTextSpec

from ..scenes import withScene

from .node          import TapMajorNodeItem, TapMinorNodeItem

from .mixin import ItemMixin

from .mixin.transform import ItemTransformMixin
from .mixin.paint     import ItemPaintMixin
from .mixin.handle    import ItemHandlesMixin
from .mixin.change    import ItemChangeMixin
from .mixin.xml       import ItemXmlMixin
from .mixin.menu      import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.diagram  import DiagramView
    from ..scenes.diagram import DiagramScene


class TapItem(
    ItemMixin,
    ItemTransformMixin,
    ItemPaintMixin,
    ItemHandlesMixin[TapHandleId],
    ItemChangeMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin,
    QGraphicsLineItem
):
    # class attributes
    _LINE = QLineF(0, 0, PITCH, PITCH)
    _PROPERTIES = \
        {
            "Suffix" : InherentProperty(
                kind   = DataKind.STR,
                worthy = lambda self: self.suffix() != "",
                getter = lambda self: self.suffix(),
                setter = lambda self, value: self.setSuffix(value)
            )
        } | \
        ItemTransformMixin._PROPERTIES_POS | \
        ItemTransformMixin._PROPERTIES_ROTATE | \
        ItemTransformMixin._PROPERTIES_MIRROR
    _PROPERTY_TEXTS = {
        "Suffix" : PropertyTextSpec(
            cleat=TapHandleId.SUFFIX, origin=RectHandleId.MIDDLE_LEFT
        )
    }

    # instance attributes
    _line        : QLineF
    _major_node  : TapMajorNodeItem
    _minor_node  : TapMinorNodeItem
    _state       : NetState
    _index_width : float
    _range_width : float


    @checked
    def __init__(
        self  : Self,
        pos   : QPointF,
        fresh : bool = True
    ) -> None:
        QGraphicsLineItem.__init__(self)
        self.setPos(pos)
        self.setLine(self._LINE)
        self.initItem(fresh)
        self._major_node = TapMajorNodeItem(self)
        self._major_node.setPos(0, 0)
        self._minor_node = TapMinorNodeItem(self)
        self._minor_node.setPos(PITCH, PITCH)
        self._state = NetState.UNRESOLVED
        self._index_width = 15.0  # default fixed width
        self._range_width = -1.0  # auto width

    @checked
    def onSceneChange(self : Self, scene : "DiagramScene | None") -> None:
        self.onSettingsChange(scene)

    @withScene
    @checked
    def onSettingsChange(self : Self, scene : "DiagramScene | None") -> None:
        self.setPen(scene.resources["Tap"][self._state.value])

    @checked
    def onConnectivityChange(self : Self) -> None:
        # update self._state based on self._node1 and self._node2
        pass

    @checked
    def majorNode(self : Self) -> TapMajorNodeItem:
        return self._major_node

    @checked
    def minorNode(self : Self) -> TapMinorNodeItem:
        return self._minor_node

    @checked
    def suffix(self : Self) -> str:
        return self._suffix

    @checked
    def setSuffix(self : Self | PropertiesMixin, suffix : str) -> None:
        self._suffix = suffix
        pt = self.properties.text("Suffix")
        if ":" in suffix:
            # range
            pt.setOrigin(RectHandleId.MIDDLE_LEFT)
            pt.setWidth(-1.0)  # auto width
            pt.setAlignH(AlignH.LEFT)
            pt.setAlignV(AlignV.MIDDLE)
        else:
            # index
            pt.setOrigin(RectHandleId.MIDDLE_RIGHT)
            pt.setWidth(-1.0)  # auto width
            pt.setAlignH(AlignH.RIGHT)
            pt.setAlignV(AlignV.MIDDLE)


    @checked
    def ctxMenuItems(self : Self, view : "DiagramView") -> list[QAction | QMenu]:
        return [
            view.action("Rotate CW",  lambda: self.rotateCW(),  shortcut="]"),
            view.action("Rotate CCW", lambda: self.rotateCCW(), shortcut="["),
        ]
