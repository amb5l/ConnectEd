"""
Drawing components for the ConnectEd application.

This module provides classes for creating and manipulating drawings,
including the main Drawing widget and DrawingSubWindow container.
"""

__all__ = [
    'Drawing',
    'DrawingSubWindow'
]

from typing import Optional

from PyQt6.QtCore    import Qt, QPoint, QPointF, QRectF, QEvent, QTimer
from PyQt6.QtWidgets import QWidget, QMdiArea, QMdiSubWindow, \
                            QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt6.QtGui     import QPainter

from ...core    import settings
from ...widgets import Extents, Grid

from .private import Layer, DrawingPrivateMixin
from .events  import DrawingEventsMixin
from .api     import DrawingApiMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from ..main_window import MainWindow


class Drawing(
    QGraphicsView,
    DrawingEventsMixin,
    DrawingPrivateMixin,
    DrawingApiMixin
):
    """Main drawing widget for the ConnectEd application.

    This class provides the core drawing functionality, including:
    - Item management (adding, removing, selecting)
    - View manipulation (zooming, panning)
    - Grid display and snapping
    - Event handling (mouse, keyboard, paint)
    """
    main_window : 'MainWindow'
    name        : str
    scene       : QGraphicsScene
    extents     : Extents
    grid        : Grid
    wip         : Optional[QGraphicsItem]
    wip_p1      : Optional[QPointF]       # 1st point created
    marquis     : 'Drawing.Marquis'
    layer       : Layer
    zoom        : float
    pan_prev    : Optional[QPointF]
    mouse       : 'Drawing.Mouse'
    state       : 'Drawing.State'

    def __init__(
        self        : 'Drawing',
        parent      : QWidget,
        main_window : 'MainWindow'
    ) -> None:
        """Initialize a Drawing widget.

        Args:
            parent: The parent widget
            main_window: The main application window
        """
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )

        self.main_window = main_window
        self.name        = 'Untitled'
        self.scene       = QGraphicsScene()
        self.extents     = Extents(settings.defaults.sheet)
        self.grid        = Grid(self.extents)
        self.wip         = None
        self.marquis     = self.Marquis(self)
        self.zoom        = 1.0
        self.pan_prev    = None
        self.mouse       = self.Mouse()
        self.point1      = None
        self.state       = self.State.Idle

        self.setScene(self.scene)
        self.scene.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)
        self.scene.addItem(self.extents)
        self.scene.addItem(self.grid)

        self.setMouseTracking(True)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        # uncomment to enable keypress events
        #self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._setLayer(Layer.Drawing)

    def drawBackground(self, painter : QPainter, rect : QRectF) -> None:
        painter.fillRect(rect, settings.theme.vacuum.fill)

    def setZ(self, z : int) -> None:
        """
        Make scene items with the supplied Z-value selectable.
        Make all other scene items non-selectable.
        """
        for item in self.scene.items():
            item.setFlag(
                QGraphicsItem.GraphicsItemFlag.ItemIsSelectable,
                item.zValue() == z
            )

class DrawingSubWindow(QMdiSubWindow):
    first_zoom_done : bool = False

    def __init__(
        self   : 'DrawingSubWindow',
        parent : QMdiArea
    ) -> None:
        super().__init__(parent)
        self.first_zoom_done = False

    def showEvent(
        self   : 'DrawingSubWindow',
        event  : QEvent
    ) -> None:
        super().showEvent(event)
        if not self.first_zoom_done and isinstance(self.widget(), Drawing):
            QTimer.singleShot(100, lambda: self.widget().viewZoomAll())
            self.first_zoom_done = True
