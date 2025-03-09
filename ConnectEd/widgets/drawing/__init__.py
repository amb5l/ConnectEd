"""
Drawing components for the ConnectEd application.

This module provides classes for creating and manipulating drawings,
including the main Drawing widget and DrawingSubWindow container.
"""

__all__ = [
    'Drawing',
    'DrawingSubWindow'
]

from types       import NoneType
from typing      import Optional, ClassVar

from PyQt6.QtCore    import Qt, QPointF, QRectF, QEvent, QTimer
from PyQt6.QtWidgets import QMdiArea, QMdiSubWindow, QWidget, \
                            QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt6.QtGui     import QPainter

from ...core     import TypedList, settings, Z_DRAWING
from ...elements import Sheet, Grid, SelectBox

from .private import DrawingPrivateMixin
from .events  import DrawingEventsMixin
from .api     import DrawingApiMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from ..symbol import Symbol
    from ..main_window import MainWindow


class Drawing(
    QGraphicsView,
    DrawingEventsMixin,
    DrawingPrivateMixin,
    DrawingApiMixin
):
    """Main drawing widget for the ConnectEd application.

    This class provides the core drawing functionality, including:
    - Element management (adding, removing, selecting)
    - View manipulation (zooming, panning)
    - Grid display and snapping
    - Event handling (mouse, keyboard, paint)
    """
    ELEMENT_TYPES : ClassVar[TypedList] = TypedList(NoneType)
    main_window   : 'MainWindow'
    scene         : QGraphicsScene
    name          : str
    sheet         : Sheet
    wip           : Optional[QGraphicsItem]
    symbols       : Optional[TypedList['Symbol']]
    sel_box       : SelectBox
    zoom          : float
    pan_prev      : Optional[QPointF]
    mouse         : 'Drawing.Mouse'
    grid          : Grid
    state         : 'Drawing.State'

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

        self.main_window = main_window
        self.scene       = QGraphicsScene()
        self.name        = 'Untitled'
        self.sheet       = Sheet(settings.defaults.sheet)
        self.wip         = None
        self.symbols     = None
        self.sel_box     = SelectBox()
        self.zoom        = 1.0
        self.pan_prev    = None
        self.mouse       = self.Mouse()
        self.grid        = Grid(self.sheet)
        self.state       = self.State.Idle

        self.setScene(self.scene)
        self.setSceneRect(self.sheet.boundingRect())
        self.scene.addItem(self.sheet)
        self.scene.addItem(self.grid)
        self.scene.addItem(self.sel_box)
        self.setMouseTracking(True)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setZ(Z_DRAWING)
        # uncomment to enable keypress events
        #self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def drawBackground(self, painter : QPainter, rect : QRectF) -> None:
        painter.setBrush(settings.theme.background)
        painter.fillRect(rect, settings.theme.background)

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
