from typing import Self

from PyQt6.QtCore import Qt, QPoint, QPointF

from .base  import qkm, DrawingViewStateBase


class DrawingViewStateViewPan1(DrawingViewStateBase):
    STATUS = "Pan: pick the first point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.pan = v
        self.view.setCursor(Qt.CursorShape.ClosedHandCursor)
        self.view.state.go(self.view.stateViewPan2)


class DrawingViewStateViewPan2(DrawingViewStateBase):
    STATUS = "Pan: pick the second point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        delta = v - self.view.pan
        self.view.horizontalScrollBar().setValue(
            self.view.horizontalScrollBar().value() - delta.x()
        )
        self.view.verticalScrollBar().setValue(
            self.view.verticalScrollBar().value() - delta.y()
        )
        self.view.pan = None
        self.view.setCursor(Qt.CursorShape.ArrowCursor)
        self.view.state.go(self.view.stateIdle)

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        delta = v - self.view.pan
        self.view.horizontalScrollBar().setValue(
            self.view.horizontalScrollBar().value() - delta.x()
        )
        self.view.verticalScrollBar().setValue(
            self.view.verticalScrollBar().value() - delta.y()
        )
        self.view.pan = v

    def mouseLeftDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseMove(v, s, m)

    def mouseLeftDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)

    def mouseMiddleDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseMove(v, s, m)

    def mouseMiddleDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStateViewZoomArea1(DrawingViewStateBase):
    STATUS = "Zoom Window: pick the first point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.marquee.begin(v)
        self.view.state.go(self.view.stateViewZoomArea2)

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStateViewZoomArea2(DrawingViewStateBase):
    STATUS = "Zoom Window: pick the second point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.marquee.end(v)
        self.view._zoomRect(self.view.marquee.rect())
        self.view.state.go(self.view.stateIdle)

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.marquee.resize(v)

    def mouseLeftDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseMove(v, s, m)

    def mouseLeftDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)

    def mouseMiddleDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseMove(v, s, m)

    def mouseMiddleDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)
