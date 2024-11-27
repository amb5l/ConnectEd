from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QWidget

from common            import logger
from .paint            import CanvasPaintMixin
from .zoom_pan         import CanvasZoomPanMixin

#from .canvas_state     import CanvasStateMixin
#from .canvas_paint     import CanvasPaintMixin
#from .canvas_keyboard  import CanvasKeyboardMixin
#from .canvas_menu      import CanvasMenuMixin, CanvasMenu
#from .canvas_zoom_pan  import CanvasZoomPanMixin
#from .canvas_selection import CanvasSelectionMixin
#from .canvas_private   import CanvasPrivateMixin
#
#from .canvas_mouse.canvas_mouse import CanvasMouseMixin


class Canvas(
    QWidget,
    CanvasPaintMixin,
    CanvasSlotsViewMixin
    #CanvasStateMixin,     # edit state management
    #CanvasMouseMixin,     # mouse events
    #CanvasKeyboardMixin,  # keyboard events
    #CanvasMenuMixin,      # context menu
    #CanvasSelectionMixin, # selection
    #CanvasPrivateMixin    # private methods
):
    def __init__(self, window, diagram):
        logger.debug('entry')
        super().__init__(window)
        self.diagram              = diagram
        self.zoom                 = 1.0
        self.pan                  = QPointF(0.0, 0.0)
        self.initialResizeDone    = False
        self.setMouseTracking(True)
        self.window().statusbar.msg.setText('Ready')
        # uncomment to enable keypress events
        #self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
