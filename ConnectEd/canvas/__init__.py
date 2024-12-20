from PyQt6.QtCore    import Qt, QPointF
from PyQt6.QtWidgets import QWidget

from .private      import CanvasPrivateMixin
from .events.paint import CanvasEventsPaintMixin
from .api.view     import CanvasApiViewMixin
#from main_window   import MainWindow
from sub_window    import SubWindow
from diagram       import Diagram


class Canvas(
    QWidget,
    CanvasPrivateMixin,
    CanvasEventsPaintMixin,
    CanvasApiViewMixin
):
    def __init__(self : 'Canvas', main_window : 'MainWindow', sub_window : SubWindow, diagram : Diagram):
        super().__init__(sub_window)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.main_window = main_window
        self.sub_window  = sub_window
        self.diagram     = diagram
        self.zoom        = 1.0
        self.pan         = QPointF(0.0, 0.0)
        self.setMouseTracking(True)
        self.main_window.statusbar.msg.setText('Ready')
        # uncomment to enable keypress events
        #self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
