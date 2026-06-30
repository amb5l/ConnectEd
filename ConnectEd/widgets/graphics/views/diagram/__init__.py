from __future__ import annotations

from typing import Self
from math   import ceil

from PyQt6.QtCore    import Qt, QPoint, QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsView, QGraphicsTextItem
from PyQt6.QtGui     import QPen, QPainter, \
                            QKeyEvent, QShowEvent, QResizeEvent, QCloseEvent

from .....app import logger, settings

from .....core.check import checked
from .....core.doc   import DocBinding

from ....window.mdi_area   import MdiArea
from ....window.sub_window import DocSubWindow

from ....marquee import Marquee

from ...views.diagram.interaction import DiagramInteraction

from ...scenes.diagram import DiagramScene

from .api     import DiagramViewApiMixin
from .mouse   import DiagramViewMouseMixin
from .state   import DiagramViewStateMixin
from .menu    import DiagramViewMenuMixin
from .private import DiagramViewPrivateMixin
from .defs    import DiagramViewLayer, DiagramViewGrid

from .state.base import DiagramViewState


class DiagramView(
    DiagramViewApiMixin,
    DiagramViewMouseMixin,
    DiagramViewStateMixin,
    DiagramViewMenuMixin,
    DiagramViewPrivateMixin,
    QGraphicsView
):
    _shown      : bool
    _zoomed     : bool
    _pan_pos    : QPoint | None
    marquee     : Marquee
    layer       : DiagramViewLayer
    grid        : DiagramViewGrid
    state       : DiagramViewState
    interaction : DiagramInteraction | None

    @checked
    def __init__(self : Self, scene : DiagramScene) -> None:
        super().__init__(scene)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )
        self._shown      = False
        self._zoomed     = False
        self._pan_pos    = None
        self.marquee     = Marquee(self)
        self.layer       = DiagramViewLayer.Drawing
        self.grid        = DiagramViewGrid()
        self.interaction = None

        self.setMouseTracking(True)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        # uncomment to enable keypress events
        #self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._setLayer(DiagramViewLayer.Drawing)

        self.initMouse()
        self.initStates()
        self.state = self.stateIdle
        self.state.go(self.stateIdle)

    def scene(self : Self) -> DiagramScene | None:
        scene = super().scene()
        if scene is None:
            return None
        if not isinstance(scene, DiagramScene):
            raise TypeError("Bad scene")
        return scene

    def showEvent(self : Self, event : QShowEvent | None) -> None:
        super().showEvent(event)
        self.viewZoomSheet()
        self._shown = True

    def resizeEvent(self : Self, event : QResizeEvent | None) -> None:
        super().resizeEvent(event)
        if self._shown and not self._zoomed:
            self._zoomed = True
            self.viewZoomAll()

    def drawForeground(
        self    : Self,
        painter : QPainter | None,
        rect : QRectF
    ) -> None:
        if painter is None:
            return
        # draw grid
        def align(x : float, px : float) -> float:
            return px * int(x / px)
        if self.grid.display:
            pp = self.transform().map(self.grid.pitch)
            px = self.grid.pitch.x()
            if pp.x() < self.grid.min_pixels:
                px *= ceil(self.grid.min_pixels / pp.x())
            py = self.grid.pitch.y()
            if pp.y() < self.grid.min_pixels:
                py *= ceil(self.grid.min_pixels / pp.y())
            grect = QRectF(
                QPointF(rect.topLeft())     - QPointF(px, py),
                QPointF(rect.bottomRight()) + QPointF(px, py)
            ).toRect()
            color = settings().get("theme/grid/line")
            color.setAlpha(self.grid.alpha)
            painter.setPen(QPen(color, 0, Qt.PenStyle.SolidLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            if self.grid.dots:
                x = align(grect.left(), px)
                while x <= grect.right():
                    y = align(grect.top(), py)
                    while y <= grect.bottom():
                        painter.drawPoint(QPointF(x, y))
                        y += py
                    x += px
            else:
                x = align(grect.left(), px)
                while x <= grect.right():
                    painter.drawLine(
                        QPointF(x, grect.top()),
                        QPointF(x, grect.bottom())
                    )
                    x += px
                y = align(grect.top(), py)
                while y <= grect.bottom():
                    painter.drawLine(
                        QPointF(grect.left(), y),
                        QPointF(grect.right(), y)
                    )
                    y += py

    def keyPressEvent(self : Self, event : QKeyEvent | None) -> None:
        """Override default arrow key handling to prevent panning"""
        if event is None:
            logger().warning("No event")
            return
        if event.key() in (
            Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down
        ):
            scene = self.scene()
            if scene is None:
                return
            focus_item = scene.focusItem()
            if focus_item is None:
                return
            if isinstance(focus_item, QGraphicsTextItem):
                text_editable = focus_item.textInteractionFlags() & \
                    Qt.TextInteractionFlag.TextEditable
                if text_editable:
                    super().keyPressEvent(event)
                    event.accept()
            else:
                event.ignore()
            return
        super().keyPressEvent(event)


class DiagramSubWindow(DocSubWindow):
    @checked
    def __init__(
        self    : Self,
        parent  : MdiArea | None = None,
        binding : DocBinding | None = None,
    ) -> None:
        super().__init__(parent, binding)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

    def closeEvent(self : Self, closeEvent : QCloseEvent | None) -> None:  # noqa: N803
        if closeEvent is None:
            logger().warning("No close event")
            return
        super().closeEvent(closeEvent)
        widget = self.widget()
        if isinstance(widget, DiagramView):
            scene = widget.scene()
            if scene and scene.undo_stack:
                try:
                    scene.undo_stack.canUndoChanged.disconnect()
                    scene.undo_stack.canRedoChanged.disconnect()
                    scene.selectionChanged.disconnect()
                except TypeError: # workaround for Qt cleanup
                    pass
