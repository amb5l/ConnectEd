from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from ....core.types import DEFAULT, AlignH, AlignV, \
                           RectHandleId, DataKind, \
                           Color, FontFamily, FontSize, FontBool
from ....core.utils import val2str

from ..properties import InherentProperty

from .text   import TextItem
from .handle import HandleItem
from .tether import TextTetherItem

from .mixin.transform import ItemTransformMixin
from .mixin.quill     import ItemQuillMixin


class PropertyLabelTetherItem(TextTetherItem):
    """
    Tether line from the origin of a PropertyTextItem to its parent cleat.
    """

    _text_item : "PropertyLabelItem"

    def anchor(self : Self) -> "HandleItem | None":
        return self._text_item.parentItem()


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
        ItemTransformMixin._PROPERTIES_POS | \
        ItemTransformMixin._PROPERTIES_ROTATE | \
        ItemTransformMixin._PROPERTIES_RECT_ORIGIN | \
        TextItem._PROPERTIES_ALIGN | \
        TextItem._PROPERTIES_SIZE | \
        ItemQuillMixin._PROPERTIES_QUILL

    # instance attributes
    _name   : str
    _value : str
    _tether : PropertyLabelTetherItem | None

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
