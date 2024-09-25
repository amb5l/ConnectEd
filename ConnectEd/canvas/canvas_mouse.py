from PyQt6.QtCore import Qt, QRectF, QSizeF
from enum import Enum, auto

from common import logger
from prefs import prefs

from canvas_mouse.canvas_mouse_click import CanvasMouseClickMixin

# click or drag (e.g. select, select window, or move)


# 2 point operation

class CanvasMouseMixin(
    CanvasMouseClickMixin
):
    class MouseState(Enum):
        IDLE  = auto()
        PRESS = auto()
        DRAG  = auto()

    class MouseButton(Enum):
        NONE   = Qt.MouseButton.NoButton
        LEFT   = Qt.MouseButton.LeftButton
        MIDDLE = Qt.MouseButton.MiddleButton
        OTHER  = Qt.MouseButton.RightButton

    #-------------------------------------------------------------------------------
    # process mouse press/move/release into click/move/drag

    def mousePressEvent(self, event):
        '''
        Process mouse press event: record essential details for a later decision
        on whether this is a click or a drag.
        '''
        if self.mouseState != self.MouseState.IDLE:
            # reject press during press or drag
            logger.warning(
                "Canvas.mousePressEvent: unexpected mouseState:",
                str(self.mouseState)
            )
            return
        match event.button():
            case Qt.MouseButton.RightButton:
                pass # ignore right button - it's used for the context menu
            case Qt.MouseButton.LeftButton | Qt.MouseButton.MiddleButton:
                self.mouseButton = event.button()
            case _:
                logger.warning("Canvas.mousePressEvent: unhandled button:", str(event.button()))
                self.mouseButton = self.MouseButton.OTHER
        self.mouseModifiers = self.getModifiers(event)
        self.mousePressPos = self.canvas2diagram(event.pos())
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
                if self.dragMin(self.mousePressPos, self.canvas2diagram(event.pos())):
                    self.setMouseState(self.MouseState.DRAG)
                    self.mouseDragStart(self.mousePressPos)
                    self.mouseDrag(self.canvas2diagram(event.pos()))
            case self.MouseState.DRAG:
                self.mouseDrag(self.canvas2diagram(event.pos()))
            case _:
                logger.warning(
                    "Canvas.mouseMoveEvent: unexpected mouseState:",
                    str(self.mouseState)
                )

    def mouseReleaseEvent(self, event):
        '''
        Process mouse release event: complete click or drag.
        '''
        if event.button() != Qt.MouseButton.LeftButton:
            return
        match self.mouseState:
            case self.MouseState.PRESS:
                self.mouseClick(self.mousePressPos)
            case self.MouseState.DRAG:
                self.mouseDragFinish(
                    self.canvas2diagram(event.pos()),
                    self.mousePressPos
                )
            case _:
                logger.warning(
                    "Canvas.mouseReleaseEvent: unexpected mouseState:",
                    str(self.mouseState)
                )

    # movement with no button pressed
    def mouseMove(self, p):
        match self.state:
            case self.State.SELECT:
                pass
            case self.State.SELECT_WIN:
                self.selectionRect.setRect(self.saneRect(self.mousePressPos, p))
            case self.State.PLACE_BLOCK_0:
                pass
            case self.State.PLACE_BLOCK_1:
                self.diagram.newBlockResize(self.snap(p))

    def mouseDragStart(self, p):
        if (self.state == self.State.SELECT) \
        and (self.mouseModifiers & self.Modifiers.CTRL):
            pass
        else:
            self.selectionClear()
        match self.state:
            case self.State.SELECT:
                # click on background -> select area (new)
                # ctrl-click on background -> select area (incremental)
                # click on object(s) -> select and move it
                # ctrl-click on object(s) -> duplication
                items = self.diagram.select(p)
                if items:
                    self.selectionAdd(items)
                    if self.mouseModifiers & self.Modifiers.CTRL:
                        self.setState(self.State.DUPLICATE)
                    elif self.mouseModifiers & self.Modifiers.ALT:
                        self.setState(self.State.MOVE)
                    else:
                        self.setState(self.State.SLIDE)
                else:
                    self.setState(self.State.SELECT_AREA)
            case self.State.PLACE_BLOCK_0:
                self.setState(self.State.PLACE_BLOCK_1)


                if self.mouseModifiers & self.Modifiers.CTRL:
                    self.setState(self.State.DUPLICATE)
        pass

    def mouseDrag(self, p):
        match self.state:
            case self.State.SELECT_AREA:
                self.selectionRect = self.saneRect(self.mousePressPos, p)

    def mouseDragFinish(self, p2, p1):
        match self.state:
            case self.State.SELECT_AREA:
                self.selectionAdd(self.diagram.select(QRectF(p1, p2)))
                self.setState(self.State.SELECT)
            case self.State.DUPLICATE:
                # duplicate selected items at pos
                # back to select mode
                self.setState(self.State.SELECT)
            case self.State.MOVE:
                # move selected items to pos
                # back to select mode
                self.setState(self.State.SELECT)

    #-------------------------------------------------------------------------------
    # mouse wheel

    def wheelEvent(self, event):
        delta = event.angleDelta().y()/prefs().view.wheelStep
        if delta > 0:
            self.zoomIn(delta)
        elif delta < 0:
            self.zoomOut(-delta)

    #-------------------------------------------------------------------------------

    def setMouseState(self, state):
        self.mouseState = state

    def dragMin(self, p1, p2):
        r = QRectF(p1, p2)
        return r.size().width()  > prefs().edit.drag.min.x or \
               r.size().height() > prefs().edit.drag.min.y

    #-------------------------------------------------------------------------------