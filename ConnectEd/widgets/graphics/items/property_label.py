from typing import Self, Any

from PyQt6.QtCore    import Qt, QPointF, QXmlStreamWriter
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsLineItem, \
                            QGraphicsSceneMouseEvent, QMenu
from PyQt6.QtGui     import QAction

from ....app import settings, logger

from ....core.types import DEFAULT, NO_CHANGE, AlignH, AlignV, \
                           HandleId, RectHandleId, DataKind, \
                           Color, FontFamily, FontSize, FontBool
from ....core.utils import val2str

from ..properties import InherentProperty, PropertiesMixin

from . import ItemType

from .text   import TextItem
from .handle import HandleItem


from .mixin.origin import ItemOriginMixin
from .mixin.pos    import ItemPosMixin
from .mixin.rotate import ItemRotateMixin
from .mixin.handle import ItemHandlesMixin
from .mixin.quill  import ItemQuillMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView
    from ..scenes.drawing import DrawingScene


class PropertyLabelItem(TextItem):
    # class attributes
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
            ),
            "Visible" : InherentProperty(
                kind   = DataKind.BOOL,
                worthy = lambda self: not self.isVisible(),
                getter = lambda self: self.isVisible(),
                setter = lambda self, value: self.setVisible(value)
            )
        } | \
        ItemPosMixin._PROPERTIES_POS | \
        ItemRotateMixin._PROPERTIES_ROTATE | \
        ItemOriginMixin._PROPERTIES_RECT_ORIGIN | \
        TextItem._PROPERTIES_ALIGN | \
        TextItem._PROPERTIES_SIZE | \
        ItemQuillMixin._PROPERTIES_QUILL

    # instance attributes
    _name  : str
    _value : str

    def __init__(
        self      : Self,
        name      : str                  = "",
        value     : str                  = "",
        pos       : QPointF | None       = None,
        rotation  : float                = 0.0,
        mirror_h  : bool                 = False,
        mirror_v  : bool                 = False,
        autoflip  : bool                 = True,
        origin    : RectHandleId         = RectHandleId.TOP_LEFT,
        align_h   : AlignH               = AlignH.LEFT,
        align_v   : AlignV               = AlignV.TOP,
        width     : float                = -1.0,
        height    : float                = -1.0,
        color     : Color                = DEFAULT,
        family    : FontFamily           = DEFAULT,
        size      : FontSize             = DEFAULT,
        bold      : FontBool             = DEFAULT,
        italic    : FontBool             = DEFAULT,
        underline : FontBool             = DEFAULT,
        fresh     : bool                 = True,
        parent    : QGraphicsItem | None = None
    ) -> None:
        pass

    def onSceneChange(self : Self, _scene : "DrawingScene | None") -> None:
        self.onSettingsChange()

    def onParentChange(self : Self, parent : QGraphicsItem | None) -> None:
        if parent is not None:
            self.onTextChange()
            self.quillSettingsChange()

    def onPositionChange(
        self : Self,
        pos  : QPointF | None = None
    ) -> None:
        ItemPosMixin.onPositionChange(self, pos)
        if hasattr(self, "_tether"):
            self._tether.onPositionChange(pos)

    def onSelectionChange(self : Self, selected : bool) -> None:
        if self._cleat is None or self._cleat == "":
            return
        cleat_valid = self._cleat is not None and self._cleat != ""
        self._tether.setVisible(selected and cleat_valid)
        self._tether.anchor().grip().setVisible(selected and cleat_valid)

    def onSettingsChange(self : Self) -> None:
        super().onSettingsChange()
        if hasattr(self, "_tether"):
            self._tether.onSettingsChange()

    def onTextChange(self : Self) -> None:
        text = val2str(self.value())
        if text == "":
            text = f"<{self._name}>"
        super().setText(text)

    def name(self : Self) -> str:
        return self._name

    def setName(self : Self, name : str) -> None:
        self._name = name

    def value(self : Self) -> str:
        return self._value

    def setValue(self : Self, value : str) -> None:
        self._value = value