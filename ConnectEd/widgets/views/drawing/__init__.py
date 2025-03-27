__all__ = ['DrawingView', 'DrawingSubWindow']

from typing import Optional

from PyQt6.QtCore    import Qt, QPoint, QPointF, QRectF, QEvent, QTimer
from PyQt6.QtWidgets import QMdiArea, QMdiSubWindow, QGraphicsView
from PyQt6.QtGui     import QPainter

from ....widgets.scenes  import DrawingScene
from ....widgets.marquee import Marquee

from .private import DrawingViewPrivateMixin, Layer
from .events  import DrawingViewEventsMixin
from .api     import DrawingViewApiMixin

from .... import hub


class DrawingSubWindow(QMdiSubWindow):
    first_zoom_done : bool = False

    def __init__(self : 'DrawingSubWindow', parent : QMdiArea) -> None:
        super().__init__(parent)
        self.first_zoom_done = False

    def showEvent(self : 'DrawingSubWindow', event : QEvent) -> None:
        super().showEvent(event)
        if not self.first_zoom_done and isinstance(self.widget(), DrawingView):
            QTimer.singleShot(100, lambda: self.widget().viewZoomAll())
            self.first_zoom_done = True

class DrawingView(
    QGraphicsView,
    DrawingViewPrivateMixin,
    DrawingViewEventsMixin,
    DrawingViewApiMixin
):
    marquee  : Marquee
    layer    : Layer
    zoom     : float
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

        self.marquee  = Marquee(self)
        self.layer    = Layer.Drawing
        self.zoom     = 1.0
        self.prev_pos = None
        self.mouse    = self.Mouse()

        self._goState(self.State.Idle)

        self.setMouseTracking(True)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        # uncomment to enable keypress events
        #self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._setLayer(Layer.Drawing)

    def drawBackground(self, painter : QPainter, rect : QRectF) -> None:
        painter.fillRect(rect, hub.settings.theme.vacuum.fill)
