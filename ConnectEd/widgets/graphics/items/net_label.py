from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QColor

from ....core.types import AlignH, AlignV, RectHandleId, DataKind
from ....core.utils import val2str

from ..properties import InherentProperty

from .text   import TextItem
from .handle import HandleItem
from .tether import TextTetherItem


class NetLabelTetherItem(TextTetherItem):
    """
    Tether line from the origin of a PropertyTextItem to its parent cleat.
    """

    _text_item : "NetLabelItem"

    def anchor(self : Self) -> "HandleItem | None":
        return self._text_item.parentItem()


class NetLabelItem(TextItem):
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
        TextItem._PROPERTIES_POS         | \
        TextItem._PROPERTIES_ROTATE      | \
        TextItem._PROPERTIES_RECT_ORIGIN | \
        TextItem._PROPERTIES_ALIGN       | \
        TextItem._PROPERTIES_SIZE        | \
        TextItem._PROPERTIES_TEXT

    # instance attributes
    _name   : str
    _value : str
    _tether : NetLabelTetherItem | None

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
        color     : QColor | None        = None,
        font      : str    | None        = None,
        size      : float  | None        = None,
        bold      : bool   | None        = None,
        italic    : bool   | None        = None,
        underline : bool   | None        = None,
        fresh     : bool                 = True,
        parent    : QGraphicsItem | None = None
    ) -> None:
        pass

    def onPositionChanged(
        self : Self,
        pos  : QPointF | None = None
    ) -> None:
        ItemTransformMixin.onPositionChanged(self, pos)
        if hasattr(self, "_tether"):
            self._tether.onPositionChanged(pos)

    def onSelectionChanged(self : Self, selected : bool) -> None:
        if self._cleat is None or self._cleat == "":
            return
        cleat_valid = self._cleat is not None and self._cleat != ""
        self._tether.setVisible(selected and cleat_valid)
        self._tether.anchor().grip().setVisible(selected and cleat_valid)

    def onTextChanged(self : Self) -> None:
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
