from typing import Self
from types  import NoneType

from PyQt6.QtCore import QPoint, QPointF

from ......core.check import checked

from .....dialogs.items.port_pin import PortPinItemDialog
from .....dialogs.items.text     import TextItemDialog

from ....items.mixin      import ItemMixin
from ....items.symbol_pin import SymbolPinItem
from ....items.text       import TextItem

from ..interaction.place import DrawingPlaceSymbolPinInteraction, \
                                DrawingPlaceLineInteraction,      \
                                DrawingPlaceRectangleInteraction, \
                                DrawingPlaceEllipseInteraction,   \
                                DrawingPlacePolylineInteraction,  \
                                DrawingPlaceTextInteraction       \

from .base  import qkm, DrawingViewStateBase
from .mixin import ClickMixin, DragMixin, StartMixin


class DrawingViewStatePlaceSymbolPin(ClickMixin, DrawingViewStateBase):
    STATUS = "Place Symbol Pin: pick a location"

    @checked
    def entry(
        self : Self,
        v    : QPoint | None,
        s    : QPointF | None,
        i    : NoneType = None  # not used
    ) -> None:
        pin = SymbolPinItem()
        pin.setPos(self._snap(s))
        dialog = PortPinItemDialog("Pin", pin, self.view)
        if dialog.exec():
            pin.setName(dialog.getName())
            pin.setDirection(dialog.getDirection())
            self.interact(DrawingPlaceSymbolPinInteraction(self.view, self._snap(s), pin))
        else:
            self.view.state.go(self.view.stateIdle)


class DrawingViewStatePlaceLine1(StartMixin, ClickMixin, DrawingViewStateBase):
    STATUS = "Place Line: pick the first point"

    _INTERACTION_CLS = DrawingPlaceLineInteraction

    def _nextState(self : Self) -> DrawingViewStateBase:
        return self.view.statePlaceLine2

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self._start(self._snap(s))

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStatePlaceLine2(ClickMixin, DragMixin, DrawingViewStateBase):
    STATUS = "Place Line: pick the second point"


class DrawingViewStatePlaceRectangle1(StartMixin, DrawingViewStateBase):
    STATUS = "Place Rectangle: pick the first point"

    _INTERACTION_CLS = DrawingPlaceRectangleInteraction

    def _nextState(self : Self) -> DrawingViewStateBase:
        return self.view.statePlaceRectangle2

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self._start(self._snap(s))

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStatePlaceRectangle2(ClickMixin, DragMixin, DrawingViewStateBase):
    STATUS = "Place Rectangle: pick the second point"


class DrawingViewStatePlaceEllipse1(StartMixin, DrawingViewStateBase):
    STATUS = "Place Ellipse: pick the first point"

    _INTERACTION_CLS = DrawingPlaceEllipseInteraction

    def _nextState(self : Self) -> DrawingViewStateBase:
        return self.view.statePlaceEllipse2

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self._start(self._snap(s))

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStatePlaceEllipse2(ClickMixin, DragMixin, DrawingViewStateBase):
    STATUS = "Place Ellipse: pick the second point"


class DrawingViewStatePlacePolyline1(StartMixin, DrawingViewStateBase):
    STATUS = "Place Polyline: pick the first point"

    _INTERACTION_CLS = DrawingPlacePolylineInteraction

    def _nextState(self : Self) -> DrawingViewStateBase:
        return self.view.statePlacePolyline2

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self._start(self._snap(s))

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStatePlacePolyline2(ClickMixin, DragMixin, DrawingViewStateBase):
    STATUS = "Place Polyline: pick the next point"


class DrawingViewStatePlaceText(ClickMixin, DrawingViewStateBase):
    STATUS = "Place Text: pick a position"

    @checked
    def entry(
        self : Self,
        v    : QPoint | None,
        s    : QPointF | None,
        i    : list[ItemMixin] | None = None
    ) -> None:
        item = TextItem(pos=self._snap(s))
        dialog = TextItemDialog(item, self.view)
        if dialog.exec():
            item.applyDialog(dialog)
            self.interact(DrawingPlaceTextInteraction(self.view, self._snap(s), item))
        else:
            self.view.state.go(self.view.stateIdle)
