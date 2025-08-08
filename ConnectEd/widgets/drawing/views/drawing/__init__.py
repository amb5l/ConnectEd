from typing import Self, Optional
from math   import ceil

from PyQt6.QtCore    import Qt, QPoint, QPointF, QRectF, QEvent
from PyQt6.QtWidgets import QApplication, QMdiArea, QMdiSubWindow, \
                            QGraphicsView, QGraphicsTextItem
from PyQt6.QtGui     import QPainter, QPen, QCloseEvent, QKeyEvent

from ..... import hub

from ....marquee import Marquee

from ...scenes.drawing import DrawingScene

from ...scenes.api.interaction import Interaction

from ...items import ElementMixin

from .mouse     import DrawingViewMouseMixin
from .private   import DrawingViewPrivateMixin
from .api       import DrawingViewApiMixin
from .state     import DrawingViewStateMixin, DrawingViewStateBase
from .defs      import *


def getView(pos : QPoint):
    widget = QApplication.widgetAt(pos)
    while widget is not None and widget.parent() is not None:
        if isinstance(widget, DrawingView):
            break
        widget = widget.parent()
    return widget

class DrawingView(
    DrawingViewMouseMixin,
    QGraphicsView,
    DrawingViewApiMixin,
    DrawingViewStateMixin,
    DrawingViewPrivateMixin
):
    _shown      : bool = False
    _zoomed     : bool = False
    marquee     : Marquee
    layer       : DrawingViewLayer
    zoom        : float
    pan         : Optional[QPoint]
    grid        : DrawingViewGrid
    mouse       : DrawingViewMouse
    state       : DrawingViewStateBase
    interaction : Optional[Interaction]
    target      : Optional[ElementMixin]  # for context menus

    def __init__(self : Self, scene : DrawingScene) -> None:
        super().__init__(scene)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )
        self._shown    = False
        self._zoomed   = False
        self.marquee   = Marquee(self)
        self.layer     = DrawingViewLayer.Drawing
        self.zoom      = 1.0
        self.pan       = None
        self.grid      = DrawingViewGrid()
        self.mouse     = DrawingViewMouse()
        self.interaction = None

        self.setMouseTracking(True)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        # uncomment to enable keypress events
        #self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._setLayer(DrawingViewLayer.Drawing)

        self.initStates()
        self.state = self.stateIdle
        self.state.go(self.stateIdle)

    def showEvent(self : Self, event : QEvent) -> None:
        super().showEvent(event)
        self._shown = True
        self.viewZoomAll()

    def resizeEvent(self : Self, event : QEvent) -> None:
        super().resizeEvent(event)
        if self._shown and not self._zoomed:
            self._zoomed = True
            self.viewZoomAll()

    def drawForeground(self : Self, painter : QPainter, rect : QRectF) -> None:
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
            color = hub.settings.getTheme("grid/line")
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

    def keyPressEvent(self : Self, event : QKeyEvent) -> None:
        """Override default arrow key handling to prevent panning"""
        if event.key() in (
            Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down
        ):
            focus_item = self.scene().focusItem()
            if (isinstance(focus_item, QGraphicsTextItem) and
                focus_item.textInteractionFlags() & Qt.TextInteractionFlag.TextEditable):
                super().keyPressEvent(event)
                event.accept()
            else:
                event.ignore()
            return
        super().keyPressEvent(event)

class DrawingSubWindow(QMdiSubWindow):
    def __init__(
        self   : Self,
        parent : Optional[QMdiArea] = None
    ) -> None:
        if parent is None:
            parent = hub.main_window.mdi_area
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

    def closeEvent(self, event: QCloseEvent) -> None:
        if isinstance(self.widget(), DrawingView):
            scene = self.widget().scene()
            if scene and scene.undo_stack:
                try:
                    scene.undo_stack.canUndoChanged.disconnect()
                    scene.undo_stack.canRedoChanged.disconnect()
                    scene.selectionChanged.disconnect()
                except TypeError:
                    pass
        super().closeEvent(event)
