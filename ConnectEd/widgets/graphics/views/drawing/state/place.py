from typing import Self
from types  import NoneType

from PyQt6.QtCore import QPoint, QPointF

from ......core.check import checked

from ......core.types import NO_CHANGE

from .....dialogs.items.port_pin import PortPinItemDialog
from .....dialogs.items.text     import TextItemDialog

from ....items.mixin      import ItemMixin
from ....items.symbol_pin import SymbolPinItem
from ....items.text       import TextItem

from ..interaction.place import PlaceSymbolPinInteraction, \
                                PlaceLineInteraction,      \
                                PlaceRectangleInteraction, \
                                PlaceEllipseInteraction,   \
                                PlacePolylineInteraction,  \
                                PlaceTextInteraction       \

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
            self.interact(PlaceSymbolPinInteraction(self.view, self._snap(s), pin))
        else:
            self.view.state.go(self.view.stateIdle)


class DrawingViewStatePlaceLine1(StartMixin, ClickMixin, DrawingViewStateBase):
    STATUS = "Place Line: pick the first point"

    _INTERACTION_CLS = PlaceLineInteraction

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

    _INTERACTION_CLS = PlaceRectangleInteraction

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

    _INTERACTION_CLS = PlaceEllipseInteraction

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

    _INTERACTION_CLS = PlacePolylineInteraction

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
            text       = dialog.getText()
            rotation   = dialog.getRotation()
            autoflip   = dialog.getAutoflip()
            mirror_h   = dialog.getMirrorH()
            mirror_v   = dialog.getMirrorV()
            align_h    = dialog.getAlignH()
            align_v    = dialog.getAlignV()
            origin     = dialog.getOrigin()
            pad_left   = dialog.getPadLeft()
            pad_right  = dialog.getPadRight()
            pad_top    = dialog.getPadTop()
            pad_bottom = dialog.getPadBottom()
            color      = dialog.getColor()
            font       = dialog.getFont()
            size       = dialog.getSize()
            bold       = dialog.getBold()
            italic     = dialog.getItalic()
            underline  = dialog.getUnderline()
            if text       is not NO_CHANGE: item.setText(text)
            if rotation   is not NO_CHANGE: item.setRotation(rotation)
            if mirror_h   is not NO_CHANGE: item.setMirrorH(mirror_h)
            if mirror_v   is not NO_CHANGE: item.setMirrorV(mirror_v)
            if autoflip   is not NO_CHANGE: item.setAutoflip(autoflip)
            if align_h    is not NO_CHANGE: item.setAlignH(align_h)
            if align_v    is not NO_CHANGE: item.setAlignV(align_v)
            if origin     is not NO_CHANGE: item.setOrigin(origin)
            if pad_left   is not NO_CHANGE: item.setPadLeft(pad_left)
            if pad_right  is not NO_CHANGE: item.setPadRight(pad_right)
            if pad_top    is not NO_CHANGE: item.setPadTop(pad_top)
            if pad_bottom is not NO_CHANGE: item.setPadBottom(pad_bottom)
            if color      is not NO_CHANGE: item.setTextColor(color)
            if font       is not NO_CHANGE: item.setTextFont(font)
            if size       is not NO_CHANGE: item.setTextSize(size)
            if bold       is not NO_CHANGE: item.setTextBold(bold)
            if italic     is not NO_CHANGE: item.setTextItalic(italic)
            if underline  is not NO_CHANGE: item.setTextUnderline(underline)
            self.interact(PlaceTextInteraction(self.view, self._snap(s), item))
        else:
            self.view.state.go(self.view.stateIdle)
