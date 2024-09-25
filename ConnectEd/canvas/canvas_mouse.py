from PyQt6.QtCore import Qt, QRectF, QSizeF
from enum import Enum, auto

from common import logger
from prefs import prefs

from canvas_mouse.canvas_mouse_move                      import CanvasMouseMoveMixin
from canvas_mouse.canvas_mouse_left_click                import CanvasMouseLeftClickMixin
from canvas_mouse.canvas_mouse_left_click_alt            import CanvasMouseLeftClickAltMixin
from canvas_mouse.canvas_mouse_left_click_ctrl           import CanvasMouseLeftClickCtrlMixin
from canvas_mouse.canvas_mouse_left_click_ctrl_alt       import CanvasMouseLeftClickCtrlAltMixin
from canvas_mouse.canvas_mouse_left_click_ctrl_shift     import CanvasMouseLeftClickCtrlShiftMixin
from canvas_mouse.canvas_mouse_left_click_ctrl_shift_alt import CanvasMouseLeftClickCtrlShiftAltMixin
from canvas_mouse.canvas_mouse_left_click_shift          import CanvasMouseLeftClickShiftMixin
from canvas_mouse.canvas_mouse_left_click_shift_alt      import CanvasMouseLeftClickShiftAltMixin
from canvas_mouse.canvas_mouse_left_drag                 import CanvasMouseLeftDragMixin
from canvas_mouse.canvas_mouse_left_drag_alt             import CanvasMouseLeftDragAltMixin
from canvas_mouse.canvas_mouse_left_drag_ctrl            import CanvasMouseLeftDragCtrlMixin
from canvas_mouse.canvas_mouse_left_drag_ctrl_alt        import CanvasMouseLeftDragCtrlAltMixin
from canvas_mouse.canvas_mouse_left_drag_ctrl_shift      import CanvasMouseLeftDragCtrlShiftMixin
from canvas_mouse.canvas_mouse_left_drag_ctrl_shift_alt  import CanvasMouseLeftDragCtrlShiftAltMixin
from canvas_mouse.canvas_mouse_left_drag_shift           import CanvasMouseLeftDragShiftMixin
from canvas_mouse.canvas_mouse_left_drag_shift_alt       import CanvasMouseLeftDragShiftAltMixin
from canvas_mouse.canvas_mouse_mid_click                 import CanvasMouseMidClickMixin
from canvas_mouse.canvas_mouse_mid_click_alt             import CanvasMouseMidClickAltMixin
from canvas_mouse.canvas_mouse_mid_click_ctrl            import CanvasMouseMidClickCtrlMixin
from canvas_mouse.canvas_mouse_mid_click_ctrl_alt        import CanvasMouseMidClickCtrlAltMixin
from canvas_mouse.canvas_mouse_mid_click_ctrl_shift      import CanvasMouseMidClickCtrlShiftMixin
from canvas_mouse.canvas_mouse_mid_click_ctrl_shift_alt  import CanvasMouseMidClickCtrlShiftAltMixin
from canvas_mouse.canvas_mouse_mid_click_shift           import CanvasMouseMidClickShiftMixin
from canvas_mouse.canvas_mouse_mid_click_shift_alt       import CanvasMouseMidClickShiftAltMixin
from canvas_mouse.canvas_mouse_mid_drag                  import CanvasMouseMidDragMixin
from canvas_mouse.canvas_mouse_mid_drag_alt              import CanvasMouseMidDragAltMixin
from canvas_mouse.canvas_mouse_mid_drag_ctrl             import CanvasMouseMidDragCtrlMixin
from canvas_mouse.canvas_mouse_mid_drag_ctrl_alt         import CanvasMouseMidDragCtrlAltMixin
from canvas_mouse.canvas_mouse_mid_drag_ctrl_shift       import CanvasMouseMidDragCtrlShiftMixin
from canvas_mouse.canvas_mouse_mid_drag_ctrl_shift_alt   import CanvasMouseMidDragCtrlShiftAltMixin
from canvas_mouse.canvas_mouse_mid_drag_shift            import CanvasMouseMidDragShiftMixin
from canvas_mouse.canvas_mouse_mid_drag_shift_alt        import CanvasMouseMidDragShiftAltMixin
from canvas_mouse.canvas_mouse_wheel                     import CanvasMouseWheelMixin


class CanvasMouseMixin(
    CanvasMouseMoveMixin,
    CanvasMouseLeftClickMixin,
    CanvasMouseLeftClickAltMixin,
    CanvasMouseLeftClickCtrlMixin,
    CanvasMouseLeftClickCtrlAltMixin,
    CanvasMouseLeftClickCtrlShiftMixin,
    CanvasMouseLeftClickCtrlShiftAltMixin,
    CanvasMouseLeftClickShiftMixin,
    CanvasMouseLeftClickShiftAltMixin,
    CanvasMouseLeftDragMixin,
    CanvasMouseLeftDragAltMixin,
    CanvasMouseLeftDragCtrlMixin,
    CanvasMouseLeftDragCtrlAltMixin,
    CanvasMouseLeftDragCtrlShiftMixin,
    CanvasMouseLeftDragCtrlShiftAltMixin,
    CanvasMouseLeftDragShiftMixin,
    CanvasMouseLeftDragShiftAltMixin,
    CanvasMouseMidClickMixin,
    CanvasMouseMidClickAltMixin,
    CanvasMouseMidClickCtrlMixin,
    CanvasMouseMidClickCtrlAltMixin,
    CanvasMouseMidClickCtrlShiftMixin,
    CanvasMouseMidClickCtrlShiftAltMixin,
    CanvasMouseMidClickShiftMixin,
    CanvasMouseMidClickShiftAltMixin,
    CanvasMouseMidDragMixin,
    CanvasMouseMidDragAltMixin,
    CanvasMouseMidDragCtrlMixin,
    CanvasMouseMidDragCtrlAltMixin,
    CanvasMouseMidDragCtrlShiftMixin,
    CanvasMouseMidDragCtrlShiftAltMixin,
    CanvasMouseMidDragShiftMixin,
    CanvasMouseMidDragShiftAltMixin,
    CanvasMouseWheelMixin
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

    #-------------------------------------------------------------------------------
    # dispatch to correct method based on mouse button and modifiers

    def mouseClick(self, p):
        if self.mouseButton == self.MouseButton.LEFT:
            match self.mouseModifiers:
                case self.Modifiers.CTRL | self.Modifiers.SHIFT | self.Modifiers.ALT:
                    self.mouseLeftClickCtrlShiftAlt(p)
                case self.Modifiers.CTRL | self.Modifiers.SHIFT:
                    self.mouseLeftClickCtrlShift(p)
                case self.Modifiers.CTRL | self.Modifiers.ALT:
                    self.mouseLeftClickCtrlAlt(p)
                case self.Modifiers.SHIFT | self.Modifiers.ALT:
                    self.mouseLeftClickShiftAlt(p)
                case self.Modifiers.CTRL:
                    self.mouseLeftClickCtrl(p)
                case self.Modifiers.SHIFT:
                    self.mouseLeftClickShift(p)
                case self.Modifiers.ALT:
                    self.mouseLeftClickAlt(p)
                case self.Modifiers.NONE:
                    self.mouseLeftClick(p)
        elif self.mouseButton == self.MouseButton.MID:
            match self.mouseModifiers:
                case self.Modifiers.CTRL | self.Modifiers.SHIFT | self.Modifiers.ALT:
                    self.mouseMidClickCtrlShiftAlt(p)
                case self.Modifiers.CTRL | self.Modifiers.SHIFT:
                    self.mouseMidClickCtrlShift(p)
                case self.Modifiers.CTRL | self.Modifiers.ALT:
                    self.mouseMidClickCtrlAlt(p)
                case self.Modifiers.SHIFT | self.Modifiers.ALT:
                    self.mouseMidClickShiftAlt(p)
                case self.Modifiers.CTRL:
                    self.mouseMidClickCtrl(p)
                case self.Modifiers.SHIFT:
                    self.mouseMidClickShift(p)
                case self.Modifiers.ALT:
                    self.mouseMidClickAlt(p)
                case self.Modifiers.NONE:
                    self.mouseMidClick(p)

    def mouseDragStart(self, p):
        if self.mouseButton == self.MouseButton.LEFT:
            match self.mouseModifiers:
                case self.Modifiers.CTRL | self.Modifiers.SHIFT | self.Modifiers.ALT:
                    self.mouseLeftDragCtrlShiftAltStart(p)
                case self.Modifiers.CTRL | self.Modifiers.SHIFT:
                    self.mouseLeftDragCtrlShiftStart(p)
                case self.Modifiers.CTRL | self.Modifiers.ALT:
                    self.mouseLeftDragCtrlAltStart(p)
                case self.Modifiers.SHIFT | self.Modifiers.ALT:
                    self.mouseLeftDragShiftAltStart(p)
                case self.Modifiers.CTRL:
                    self.mouseLeftDragCtrlStart(p)
                case self.Modifiers.SHIFT:
                    self.mouseLeftDragShiftStart(p)
                case self.Modifiers.ALT:
                    self.mouseLeftDragAltStart(p)
                case self.Modifiers.NONE:
                    self.mouseLeftDragStart(p)
        elif self.mouseButton == self.MouseButton.MID:
            match self.mouseModifiers:
                case self.Modifiers.CTRL | self.Modifiers.SHIFT | self.Modifiers.ALT:
                    self.mouseMidDragCtrlShiftAltStart(p)
                case self.Modifiers.CTRL | self.Modifiers.SHIFT:
                    self.mouseMidDragCtrlShiftStart(p)
                case self.Modifiers.CTRL | self.Modifiers.ALT:
                    self.mouseMidDragCtrlAltStart(p)
                case self.Modifiers.SHIFT | self.Modifiers.ALT:
                    self.mouseMidDragShiftAltStart(p)
                case self.Modifiers.CTRL:
                    self.mouseMidDragCtrlStart(p)
                case self.Modifiers.SHIFT:
                    self.mouseMidDragShiftStart(p)
                case self.Modifiers.ALT:
                    self.mouseMidDragAltStart(p)
                case self.Modifiers.NONE:
                    self.mouseMidDragStart(p)

    def mouseDrag(self, p):
        if self.mouseButton == self.MouseButton.LEFT:
            match self.mouseModifiers:
                case self.Modifiers.CTRL | self.Modifiers.SHIFT | self.Modifiers.ALT:
                    self.mouseLeftDragCtrlShiftAlt(p)
                case self.Modifiers.CTRL | self.Modifiers.SHIFT:
                    self.mouseLeftDragCtrlShift(p)
                case self.Modifiers.CTRL | self.Modifiers.ALT:
                    self.mouseLeftDragCtrlAlt(p)
                case self.Modifiers.SHIFT | self.Modifiers.ALT:
                    self.mouseLeftDragShiftAlt(p)
                case self.Modifiers.CTRL:
                    self.mouseLeftDragCtrl(p)
                case self.Modifiers.SHIFT:
                    self.mouseLeftDragShift(p)
                case self.Modifiers.ALT:
                    self.mouseLeftDragAlt(p)
                case self.Modifiers.NONE:
                    self.mouseLeftDrag(p)
        elif self.mouseButton == self.MouseButton.MID:
            match self.mouseModifiers:
                case self.Modifiers.CTRL | self.Modifiers.SHIFT | self.Modifiers.ALT:
                    self.mouseMidDragCtrlShiftAlt(p)
                case self.Modifiers.CTRL | self.Modifiers.SHIFT:
                    self.mouseMidDragCtrlShift(p)
                case self.Modifiers.CTRL | self.Modifiers.ALT:
                    self.mouseMidDragCtrlAlt(p)
                case self.Modifiers.SHIFT | self.Modifiers.ALT:
                    self.mouseMidDragShiftAlt(p)
                case self.Modifiers.CTRL:
                    self.mouseMidDragCtrl(p)
                case self.Modifiers.SHIFT:
                    self.mouseMidDragShift(p)
                case self.Modifiers.ALT:
                    self.mouseMidDragAlt(p)
                case self.Modifiers.NONE:
                    self.mouseMidDrag(p)

    def mouseDragFinish(self, p2, p1):
        if self.mouseButton == self.MouseButton.LEFT:
            match self.mouseModifiers:
                case self.Modifiers.CTRL | self.Modifiers.SHIFT | self.Modifiers.ALT:
                    self.mouseLeftDragCtrlShiftAltFinish(p2, p1)
                case self.Modifiers.CTRL | self.Modifiers.SHIFT:
                    self.mouseLeftDragCtrlShiftFinish(p2, p1)
                case self.Modifiers.CTRL | self.Modifiers.ALT:
                    self.mouseLeftDragCtrlAltFinish(p2, p1)
                case self.Modifiers.SHIFT | self.Modifiers.ALT:
                    self.mouseLeftDragShiftAltFinish(p2, p1)
                case self.Modifiers.CTRL:
                    self.mouseLeftDragCtrlFinish(p2, p1)
                case self.Modifiers.SHIFT:
                    self.mouseLeftDragShiftFinish(p2, p1)
                case self.Modifiers.ALT:
                    self.mouseLeftDragAltFinish(p2, p1)
                case self.Modifiers.NONE:
                    self.mouseLeftDragFinish(p2, p1)
        elif self.mouseButton == self.MouseButton.MID:
            match self.mouseModifiers:
                case self.Modifiers.CTRL | self.Modifiers.SHIFT | self.Modifiers.ALT:
                    self.mouseMidDragCtrlShiftAltFinish(p2, p1)
                case self.Modifiers.CTRL | self.Modifiers.SHIFT:
                    self.mouseMidDragCtrlShiftFinish(p2, p1)
                case self.Modifiers.CTRL | self.Modifiers.ALT:
                    self.mouseMidDragCtrlAltFinish(p2, p1)
                case self.Modifiers.SHIFT | self.Modifiers.ALT:
                    self.mouseMidDragShiftAltFinish(p2, p1)
                case self.Modifiers.CTRL:
                    self.mouseMidDragCtrlFinish(p2, p1)
                case self.Modifiers.SHIFT:
                    self.mouseMidDragShiftFinish(p2, p1)
                case self.Modifiers.ALT:
                    self.mouseMidDragAltFinish(p2, p1)
                case self.Modifiers.NONE:
                    self.mouseMidDragFinish(p2, p1)

    #-------------------------------------------------------------------------------
    # mouse wheel

    def wheelEvent(self, event):
        match self.mouseModifiers:
            case self.Modifiers.CTRL | self.Modifiers.SHIFT | self.Modifiers.ALT:
                self.wheelCtrlShiftAlt(event)
            case self.Modifiers.CTRL | self.Modifiers.SHIFT:
                self.wheelCtrlShift(event)
            case self.Modifiers.CTRL | self.Modifiers.ALT:
                self.WheelCtrlAlt(event)
            case self.Modifiers.SHIFT | self.Modifiers.ALT:
                self.wheelShiftAlt(event)
            case self.Modifiers.CTRL:
                self.wheelCtrl(event)
            case self.Modifiers.SHIFT:
                self.WheelShift(event)
            case self.Modifiers.ALT:
                self.wheelAlt(event)
            case self.Modifiers.NONE:
                self.wheel(event)

    #-------------------------------------------------------------------------------

    def setMouseState(self, state):
        self.mouseState = state

    def dragMin(self, p1, p2):
        r = QRectF(p1, p2)
        return r.size().width()  > prefs().edit.drag.min.x or \
               r.size().height() > prefs().edit.drag.min.y

    #-------------------------------------------------------------------------------