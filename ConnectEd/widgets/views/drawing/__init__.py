__all__ = ['DrawingView', 'DrawingSubWindow']

from typing import Optional
from math   import ceil

from PyQt6.QtCore    import Qt, QPoint, QPointF, QRectF, QEvent
from PyQt6.QtWidgets import QMdiArea, QMdiSubWindow, QGraphicsView
from PyQt6.QtGui     import QPainter, QPen, QCloseEvent

from ....widgets.scenes  import DrawingScene
from ....widgets.marquee import Marquee

from .private import DrawingViewPrivateMixin, Layer
from .events  import DrawingViewEventsMixin
from .api     import DrawingViewApiMixin

from .... import hub


class DrawingSubWindow(QMdiSubWindow):
    def __init__(
        self   : 'DrawingSubWindow',
        parent : Optional[QMdiArea] = None
    ) -> None:
        if parent is None:
            parent = hub.main_window.mdi_area
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

    def closeEvent(self : 'DrawingSubWindow', event : QCloseEvent) -> None:
        hub.main_window.menu_bar.updateWindowMenu()

class DrawingView(
    QGraphicsView,
    DrawingViewPrivateMixin,
    DrawingViewEventsMixin,
    DrawingViewApiMixin
):
    _shown   : bool = False
    _zoomed  : bool = False
    marquee  : Marquee
    layer    : Layer
    zoom     : float
    grid     : 'DrawingView.Grid'
    prev_pos : Optional[QPointF | QPoint]
    mouse    : 'DrawingView.Mouse'
    state    : 'DrawingView.State'

    def __init__(self : 'DrawingView', scene : DrawingScene) -> None:
        super().__init__(scene)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )

        self._shown   = False
        self._zoomed  = False
        self.marquee  = Marquee(self)
        self.layer    = Layer.Drawing
        self.zoom     = 1.0
        self.grid     = self.Grid()
        self.prev_pos = None
        self.mouse    = self.Mouse()

        self._goState(self.State.Idle)

        self.setMouseTracking(True)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        # uncomment to enable keypress events
        #self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._setLayer(Layer.Drawing)

    def showEvent(self : 'DrawingView', event : QEvent) -> None:
        super().showEvent(event)
        self._shown = True
        self.viewZoomAll()

    def resizeEvent(self : 'DrawingView', event : QEvent) -> None:
        super().resizeEvent(event)
        if self._shown and not self._zoomed:
            self._zoomed = True
            self.viewZoomAll()

    def drawForeground(self, painter : QPainter, rect : QRectF) -> None:
        # draw grid
        def align(x : float, px : float) -> float:
            return px * int(x / px)
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
        color = hub.settings.theme.grid.line
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
