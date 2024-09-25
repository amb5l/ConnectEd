from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QWidget, QApplication

from common          import logger
from canvas_state    import CanvasStateMixin
from canvas_paint    import CanvasPaintMixin
from canvas_mouse    import CanvasMouseMixin
from canvas_keyboard import CanvasKeyboardMixin
from canvas_menu     import CanvasMenuMixin, CanvasMenu
from canvas_zoom_pan import CanvasZoomPanMixin
from canvas_private  import CanvasPrivateMixin


class Canvas(
    QWidget,
    CanvasStateMixin,     # edit state management
    CanvasPaintMixin,    # paintEvent
    CanvasMouseMixin,    # mouse events
    CanvasKeyboardMixin, # keyboard events
    CanvasMenuMixin,     # context menu
    CanvasZoomPanMixin,  # zoom and pan
    CanvasPrivateMixin   # private methods
):
    def __init__(self, diagram):
        super().__init__()

        self.diagram             = diagram                  # diagram instance
        self.clipboard           = QApplication.clipboard() # clipboard

        self.selectionClear()                           # selected diagram items

        self.zoom                = 1.0
        self.pan                 = QPointF(0.0, 0.0)
        self.alpha               = 255                  # alpha channel for diagram items
        self.initialResizeDone   = False

        self.state               = self.State.SELECT
        self.mouseState          = self.MouseState.IDLE
        self.MouseButton         = self.MouseButton.NONE
        self.mousePressModifiers = self.Modifiers.NONE  # modifiers at moment of mouse press
        self.currentPos          = QPointF()
        self.startPos            = QPointF()
      #  self.physicalPos         = QPoint(0, 0) # TODO initialize from current mouse position
        self.prevPos             = QPointF()

        self.contextMenu         = CanvasMenu(self, self.window().actions)

        logger.info('Canvas: initialising')
        self.setMouseTracking(True)
        self.window().statusBar.msg.setText('Ready')
        # uncomment to enable keypress events
        #self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        #self.setAutoFillBackground(True)
        # set background color
        # p = self.palette()
        # p.setColor(self.backgroundRole(), prefs().draw.theme.background)
        # self.setPalette(p)
