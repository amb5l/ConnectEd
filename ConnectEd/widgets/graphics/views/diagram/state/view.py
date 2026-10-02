from typing            import Self
from typing_extensions import override

from PyQt6.QtCore import Qt, QPoint, QPointF

from ..mouse import MouseModifier

from .base   import DiagramViewState


class DiagramViewStateViewPan1(DiagramViewState):
    STATUS = "Pan: pick the first point"

    @override
    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.view._pan_pos = vpos
        self.view.setCursor(Qt.CursorShape.ClosedHandCursor)
        self.view.state.go(self.view.stateViewPan2)


class DiagramViewStateViewPan2(DiagramViewState):
    STATUS = "Pan: pick the second point"

    @override
    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        if self.view._pan_pos is None:
            raise RuntimeError("No pan position")
        delta = vpos - self.view._pan_pos
        if (horizontal_scroll_bar := self.view.horizontalScrollBar()) is None:
            raise RuntimeError("No horizontal scroll bar")
        horizontal_scroll_bar.setValue(
            horizontal_scroll_bar.value() - delta.x()
        )
        if (vertical_scroll_bar := self.view.verticalScrollBar()) is None:
            raise RuntimeError("No vertical scroll bar")
        vertical_scroll_bar.setValue(
            vertical_scroll_bar.value() - delta.y()
        )
        self.view._pan_pos = None
        self.view.setCursor(Qt.CursorShape.ArrowCursor)
        self.view.state.go(self.view.stateIdle)

    @override
    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        if self.view._pan_pos is None:
            raise RuntimeError("No pan position")
        delta = vpos - self.view._pan_pos
        if (horizontal_scroll_bar := self.view.horizontalScrollBar()) is None:
            raise RuntimeError("No horizontal scroll bar")
        horizontal_scroll_bar.setValue(
            horizontal_scroll_bar.value() - delta.x()
        )
        if (vertical_scroll_bar := self.view.verticalScrollBar()) is None:
            raise RuntimeError("No vertical scroll bar")
        vertical_scroll_bar.setValue(
            vertical_scroll_bar.value() - delta.y()
        )
        self.view._pan_pos = vpos

    @override
    def mouseLeftDragCont(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.mouseMove(vpos, spos, modifiers)

    @override
    def mouseLeftDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.mouseLeftClick(vpos, spos, modifiers)

    @override
    def mouseMiddleDragCont(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.mouseMove(vpos, spos, modifiers)

    @override
    def mouseMiddleDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.mouseLeftClick(vpos, spos, modifiers)


class DiagramViewStateViewZoomArea1(DiagramViewState):
    STATUS = "Zoom Window: pick the first point"

    @override
    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.view.marquee.begin(vpos)
        self.view.state.go(self.view.stateViewZoomArea2)

    @override
    def mouseLeftDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.mouseLeftClick(vpos, spos, modifiers)


class DiagramViewStateViewZoomArea2(DiagramViewState):
    STATUS = "Zoom Window: pick the second point"

    @override
    def mouseLeftClick(self : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.view.marquee.end(vpos)
        self.view._zoomRect(self.view.marquee.rect())
        self.view.state.go(self.view.stateIdle)

    @override
    def mouseMove(self : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.view.marquee.resize(vpos)

    @override
    def mouseLeftDragCont(self : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.mouseMove(vpos, spos, modifiers)

    @override
    def mouseLeftDragEnd(self : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.mouseLeftClick(vpos, spos, modifiers)

    @override
    def mouseMiddleDragCont(self : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.mouseMove(vpos, spos, modifiers)

    @override
    def mouseMiddleDragEnd(self : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.mouseLeftClick(vpos, spos, modifiers)
