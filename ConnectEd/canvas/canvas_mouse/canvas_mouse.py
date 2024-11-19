from PyQt6.QtCore import Qt, QRectF, QSizeF
from enum import Enum, auto
from itertools import combinations
import importlib

from common import logger
from prefs import prefs

from .canvas_mouse_move       import CanvasMouseMoveMixin
from .canvas_mouse_wheel      import CanvasMouseWheelMixin
from .canvas_mouse_left_click import CanvasMouseLeftClickMixin


class CanvasMouseMixin(
    CanvasMouseMoveMixin,
    CanvasMouseWheelMixin,
    CanvasMouseLeftClickMixin
):
    class MouseState(Enum):
        IDLE  = auto()
        PRESS = auto()
        DRAG  = auto()

    class MouseButton(Enum):
        NONE  = Qt.MouseButton.NoButton
        LEFT  = Qt.MouseButton.LeftButton
        MID   = Qt.MouseButton.MiddleButton
        OTHER = Qt.MouseButton.RightButton

    #-------------------------------------------------------------------------------
    # process mouse press/move/release into click/move/drag

    def mousePressEvent(self, event):
        '''
        Process mouse press event: record essential details for a later decision
        on whether this is a click or a drag.
        '''
        if self.mouseState != self.MouseState.IDLE:
            logger.warning(
                'Canvas.mousePressEvent: unexpected mouseState:',
                str(self.mouseState)
            )
            return
        match event.button():
            case Qt.MouseButton.RightButton:
                return # ignore right button - it's used for the context menu
            case Qt.MouseButton.LeftButton | Qt.MouseButton.MiddleButton:
                self.mouseButton = event.button()
            case _:
                logger.warning('Canvas.mousePressEvent: unhandled button:', str(event.button()))
                self.mouseButton = self.MouseButton.OTHER
        self.mouseModifiers = self.getModifiers(event)
        self.mousePressCanvasPos = event.pos()
        self.mousePressDiagramPos = self.canvas2diagram(event.pos())
        self.setMouseState(self.MouseState.PRESS)
        return

    def mouseMoveEvent(self, event):
        '''
        Process mouse move event: if pressed, measure movement to decide whether
        drag threshold has been met.
        '''
        match self.mouseState:
            case self.MouseState.IDLE:
                self.mouseMove(self.canvas2diagram(event.pos()))
            case self.MouseState.PRESS:
                if self.dragMin(self.mousePressDiagramPos, self.canvas2diagram(event.pos())):
                    self.setMouseState(self.MouseState.DRAG)
                    self.mouseDragStart(self.mousePressDiagramPos)
                    self.mouseDrag(self.canvas2diagram(event.pos()))
            case self.MouseState.DRAG:
                self.mouseDrag(self.canvas2diagram(event.pos()))
            case _:
                logger.warning(
                    'Canvas.mouseMoveEvent: unexpected mouseState:',
                    str(self.mouseState)
                )

    def mouseReleaseEvent(self, event):
        '''
        Process mouse release event: complete click or drag.
        '''
        match self.mouseState:
            case self.MouseState.PRESS:
                self.mouseClick(self.mousePressDiagramPos)
            case self.MouseState.DRAG:
                self.mouseDragFinish(self.canvas2diagram(event.pos()))
            case _:
                logger.warning(
                    'Canvas.mouseReleaseEvent: unexpected mouseState:',
                    str(self.mouseState)
                )

    def mouseDoubleClickEvent(self, event):
        '''
        Process mouse double-click event.
        '''
        if self.mouseState != self.MouseState.IDLE:
            logger.warning(
                'Canvas.mouseDoubleClickEvent: unexpected mouseState:',
                str(self.mouseState)
            )
            return
        match event.button():
            case Qt.MouseButton.RightButton:
                return # ignore right button - it's used for the context menu
            case Qt.MouseButton.LeftButton | Qt.MouseButton.MiddleButton:
                self.mouseButton = event.button()
            case _:
                logger.warning('Canvas.mouseDoubleClickEvent: unhandled button:', str(event.button()))
                self.mouseButton = self.MouseButton.OTHER
        self.mouseModifiers = self.getModifiers(event)
        self.mousePressDiagramPos = self.canvas2diagram(event.pos())
        self.mouseDoubleClick(self.mousePressDiagramPos)
        return

    def wheelEvent(self, event):
        delta = event.angleDelta().y()/prefs.view.wheelStep
        self.mouseWheel(self, delta)

    #-------------------------------------------------------------------------------
    # dispatch to correct method based on mouse button and/or modifiers

    def mouseMethod(self, name, x):
        return lambda checked=False, x=name: getattr(self, x)(self, x)

    def mouseClick(self, p):
        methodName = 'mouse' + self.mouseButton.name.title() + 'Click' + \
            'Ctrl'  if self.mouseModifiers & self.Modifiers.CTRL  else '' + \
            'Shift' if self.mouseModifiers & self.Modifiers.SHIFT else '' + \
            'Alt'   if self.mouseModifiers & self.Modifiers.ALT   else ''
        self.mouseMethod(methodName, p)

    def mouseDragStart(self, p):
        methodName = 'mouse' + self.mouseButton.name.title() + 'Drag' + \
            'Ctrl'  if self.mouseModifiers & self.Modifiers.CTRL  else '' + \
            'Shift' if self.mouseModifiers & self.Modifiers.SHIFT else '' + \
            'Alt'   if self.mouseModifiers & self.Modifiers.ALT   else '' + \
            'Start'
        self.mouseMethod(methodName, p)

    def mouseDrag(self, p):
        methodName = 'mouse' + self.mouseButton.name.title() + 'Drag' + \
            'Ctrl'  if self.mouseModifiers & self.Modifiers.CTRL  else '' + \
            'Shift' if self.mouseModifiers & self.Modifiers.SHIFT else '' + \
            'Alt'   if self.mouseModifiers & self.Modifiers.ALT   else ''
        self.mouseMethod(methodName, p)

    def mouseDragFinish(self, p):
        methodName = 'mouse' + self.mouseButton.name.title() + 'Drag' + \
            'Ctrl'  if self.mouseModifiers & self.Modifiers.CTRL  else '' + \
            'Shift' if self.mouseModifiers & self.Modifiers.SHIFT else '' + \
            'Alt'   if self.mouseModifiers & self.Modifiers.ALT   else '' + \
            'Finish'
        self.mouseMethod(methodName, p)

    def mouseWheel(self, delta):
        methodName = 'mouse' + self.mouseButton.name.title() + 'Wheel' + \
            'Ctrl'  if self.mouseModifiers & self.Modifiers.CTRL  else '' + \
            'Shift' if self.mouseModifiers & self.Modifiers.SHIFT else '' + \
            'Alt'   if self.mouseModifiers & self.Modifiers.ALT   else ''
        self.mouseMethod(methodName, delta)

    #-------------------------------------------------------------------------------

    def setMouseState(self, state):
        self.mouseState = state

    def dragMin(self, p1, p2):
        r = QRectF(p1, p2)
        return r.size().width()  > prefs.edit.drag.min.x or \
               r.size().height() > prefs.edit.drag.min.y

    #-------------------------------------------------------------------------------
