__all__ = ["DrawingView", "DrawingSubWindow"]

from typing import Self, Optional
from enum   import Enum, auto
from math   import ceil, sqrt

from PyQt6.QtCore    import Qt, QPoint, QPointF, QRectF, QSizeF, QEvent
from PyQt6.QtWidgets import QMdiArea, QMdiSubWindow, \
                            QMenu, QGraphicsView, \
                            QGraphicsItem, QGraphicsTextItem
from PyQt6.QtGui     import QPainter, QPainterPath, QPen, QIcon, \
                            QCloseEvent, QEnterEvent, \
                            QKeyEvent, QMouseEvent, QWheelEvent, \
                            QAction, QCursor

from ...core import logger, LAYER_SHEET, LAYER_DRAWING

from ..scenes  import DrawingScene
from ..marquee import Marquee

from ..elements import Element, Grip, cmdSlide, cmdMove, cmdResize, \
                       Rectangle, cmdPlaceRectangle, \
                       Text, cmdPlaceText

from ... import hub


class DrawingViewLayer(Enum):
    Sheet   = LAYER_SHEET
    Drawing = LAYER_DRAWING

class DrawingViewGrid:
    display    : bool
    snap       : bool
    pitch      : QPointF
    dots       : bool
    alpha      : int
    min_pixels : int

    def __init__(self : Self) -> None:
        self.display    = hub.settings.defaults.grid.display
        self.snap       = hub.settings.defaults.grid.snap
        self.pitch      = hub.settings.defaults.grid.pitch
        self.dots       = hub.settings.defaults.grid.dots
        self.alpha      = hub.settings.defaults.grid.alpha
        self.min_pixels = hub.settings.defaults.grid.min_pixels

class DrawingViewPLPos:
    physical : Optional[QPoint] = None
    logical  : Optional[QPointF] = None

    def __init__(
        self     : Self,
        physical : Optional[QPoint] = None,
        logical  : Optional[QPointF] = None
    ) -> None:
        self.physical = physical
        self.logical  = logical

    def setPL(self : Self, physical: QPoint, logical: QPointF) -> None:
        self.physical = physical
        self.logical  = logical

class DrawingViewMousePress(DrawingViewPLPos):
    modifiers : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier

    def __init__(
        self      : Self,
        physical  : Optional[QPoint] = None,
        logical   : Optional[QPointF] = None,
        modifiers : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier
    ) -> None:
        super().__init__(physical, logical)
        self.modifiers = modifiers

class DrawingViewMouseRelease(DrawingViewPLPos):
    pass

class DrawingViewMouseButtonState(Enum):
    Idle     = auto()
    Pressed  = auto()
    Dragging = auto()

class DrawingViewMouseButton:
    press   : DrawingViewMousePress
    release : DrawingViewMouseRelease
    double  : DrawingViewMousePress
    state   : DrawingViewMouseButtonState

    def __init__(self : Self) -> None:
        self.press   = DrawingViewMousePress()
        self.release = DrawingViewMouseRelease()
        self.double  = DrawingViewMousePress()
        self.state   = DrawingViewMouseButtonState.Idle

class DrawingViewMouse:
    current : DrawingViewPLPos
    left    : DrawingViewMouseButton
    middle  : DrawingViewMouseButton

    def __init__(self : Self) -> None:
        self.current = DrawingViewPLPos()
        self.left    = DrawingViewMouseButton()
        self.middle  = DrawingViewMouseButton()

class DrawingViewState(Enum):
    Idle            = auto()
    ViewPan1        = auto()
    ViewPan2        = auto()
    ViewZoomWindow1 = auto()
    ViewZoomWindow2 = auto()
    SelectArea2     = auto()
    EditSlide1      = auto()
    EditSlide2      = auto()
    EditMove1       = auto()
    EditMove2       = auto()
    EditResize1     = auto()
    EditResize2     = auto()
    PlaceRectangle1 = auto()
    PlaceRectangle2 = auto()
    PlaceText1      = auto()
    PlaceText2      = auto()

DrawingViewStateTip = {
    DrawingViewState.Idle            : "Idle",
    DrawingViewState.ViewPan1        : "ViewPan1",
    DrawingViewState.ViewPan2        : "ViewPan2",
    DrawingViewState.ViewZoomWindow1 : "ViewZoomWindow1",
    DrawingViewState.ViewZoomWindow2 : "ViewZoomWindow2",
    DrawingViewState.SelectArea2     : "SelectArea2",
    DrawingViewState.EditSlide1      : "EditSlide1",
    DrawingViewState.EditSlide2      : "EditSlide2",
    DrawingViewState.EditMove1       : "EditMove1",
    DrawingViewState.EditMove2       : "EditMove2",
    DrawingViewState.EditResize1     : "EditResize1",
    DrawingViewState.EditResize2     : "EditResize2",
    DrawingViewState.PlaceRectangle1 : "PlaceRectangle1",
    DrawingViewState.PlaceRectangle2 : "PlaceRectangle2",
    DrawingViewState.PlaceText1      : "PlaceText1",
    DrawingViewState.PlaceText2      : "PlaceText2"
}

class DrawingViewWip:
    macro    : bool
    elements : Optional[list[QGraphicsItem]]
    pos0     : Optional[QPointF | QPoint]

    def __init__(self : Self) -> None:
        self.clear()

    def clear(self : Self) -> None:
        self.macro    = False
        self.elements = None
        self.pos0     = None

qkm = Qt.KeyboardModifier

class DrawingView(QGraphicsView):

    Layer            = DrawingViewLayer
    Grid             = DrawingViewGrid
    PLPos            = DrawingViewPLPos
    MousePress       = DrawingViewMousePress
    MouseRelease     = DrawingViewMouseRelease
    MouseButtonState = DrawingViewMouseButtonState
    MouseButton      = DrawingViewMouseButton
    Mouse            = DrawingViewMouse
    State            = DrawingViewState
    StateTip         = DrawingViewStateTip
    Wip              = DrawingViewWip

    _shown   : bool = False
    _zoomed  : bool = False
    marquee  : Marquee
    layer    : DrawingViewLayer
    zoom     : float
    grid     : "DrawingView.Grid"
    mouse    : "DrawingView.Mouse"
    state    : "DrawingView.State"
    wip      : "DrawingView.Wip"

    def __init__(self : Self, scene : DrawingScene) -> None:
        super().__init__(scene)
        scene.textEditingComplete.connect(self.placeTextFinalize)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )

        self._shown   = False
        self._zoomed  = False
        self.marquee  = Marquee(self)
        self.layer    = DrawingViewLayer.Drawing
        self.zoom     = 1.0
        self.grid     = self.Grid()
        self.mouse    = self.Mouse()
        self.wip      = self.Wip()

        self._goState(self.State.Idle)

        self.setMouseTracking(True)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        # uncomment to enable keypress events
        #self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._setLayer(DrawingViewLayer.Drawing)

    ############################################################################
    # display events

    def showEvent(self : Self, event : QEvent) -> None:
        super().showEvent(event)
        self._shown = True
        self.viewZoomAll()

    def resizeEvent(self : Self, event : QEvent) -> None:
        super().resizeEvent(event)
        if self._shown and not self._zoomed:
            self._zoomed = True
            self.viewZoomAll()

    def drawForeground(self : Self, painter : QPainter, rect : QRectF) -> None:
        # draw grid
        def align(x : float, px : float) -> float:
            return px * int(x / px)
        if self.grid.display:
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

    ############################################################################
    # key events

    def keyPressEvent(self : Self, event : QKeyEvent) -> None:
        """Override default arrow key handling to prevent panning"""
        if event.key() in (
            Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down
        ):
            focus_item = self.scene().focusItem()
            if (isinstance(focus_item, QGraphicsTextItem) and
                focus_item.textInteractionFlags() & Qt.TextInteractionFlag.TextEditable):
                super().keyPressEvent(event)
                event.accept()
            else:
                event.ignore()
            return
        super().keyPressEvent(event)

    ############################################################################
    # mouse events

    def enterEvent(self : Self, event : QEnterEvent) -> None:
        p = self.mapFromGlobal(QCursor.pos())
        l = self.mapToScene(p)
        self.mouse.current.setPL(p, l)
        hub.main_window.status_bar.xy.setText(
            str(int(round(l.x()))) + "," + str(int(round(l.y())))
        )

    def leaveEvent(self : Self, _ : QEvent) -> None:
        rect = self.viewport().rect()
        p = QPoint(rect.width() // 2, rect.height() // 2)
        l = self.mapToScene(p)
        self.mouse.current.setPL(p, l)
        hub.main_window.status_bar.xy.setText("-,-")

    def mouseMoveEvent(self : Self, event : QMouseEvent) -> None:
        p = event.pos(); l = self.mapToScene(p)
        self.mouse.current.setPL(p, l)
        hub.main_window.status_bar.xy.setText(
            str(int(round(l.x()))) + "," + str(int(round(l.y())))
        )
        match self.mouse.left.state:
            case self.MouseButtonState.Pressed:
                d = self._distance(self.mouse.left.press.physical, event.pos())
                if d >= hub.settings.prefs.mouse.drag:
                    self.mouse.left.state = self.MouseButtonState.Dragging
                    self.mouseLeftDragBegin()
                    return
            case self.MouseButtonState.Dragging:
                self.mouseLeftDragContinue()
                return
        match self.mouse.middle.state:
            case self.MouseButtonState.Pressed:
                d = self._distance(self.mouse.middle.press.physical, event.pos())
                if d >= hub.settings.prefs.mouse.drag:
                    self.mouse.middle.state = self.MouseButtonState.Dragging
                    self.mouseMiddleDragBegin()
                    return
            case self.MouseButtonState.Dragging:
                self.mouseMiddleDragContinue()
                return
        self.mouseMove()

    def mousePressEvent(self : Self, event : QMouseEvent) -> None:
        p = event.pos(); l = self.mapToScene(p)
        items = self.scene().items(
            l,
            Qt.ItemSelectionMode.IntersectsItemShape,
            Qt.SortOrder.DescendingOrder,
            self.viewportTransform()
        )
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.mouse.left.press.setPL(p, l)
            self.mouse.left.press.modifiers = self._getModifiers(event)
            self.mouse.left.state = self.MouseButtonState.Pressed
        if event.buttons() & Qt.MouseButton.MiddleButton:
            self.mouse.middle.press.setPL(p, l)
            self.mouse.middle.press.modifiers = self._getModifiers(event)
            self.mouse.middle.state = self.MouseButtonState.Pressed

    def mouseReleaseEvent(self : Self, event : QMouseEvent) -> None:
        p = event.pos(); l = self.mapToScene(p)
        if event.button() & Qt.MouseButton.LeftButton:
            self.mouse.left.release.setPL(p, l)
            match self.mouse.left.state:
                case self.MouseButtonState.Pressed:
                    self.mouseLeftClick()
                    self.mouse.left.state = self.MouseButtonState.Idle
                case self.MouseButtonState.Dragging:
                    self.mouseLeftDragEnd()
                    self.mouse.left.state = self.MouseButtonState.Idle
                case _:
                    logger.warning(f"Mouse left button released when idle")
        if event.button() & Qt.MouseButton.MiddleButton:
            self.mouse.middle.release.setPL(p, l)
            match self.mouse.middle.state:
                case self.MouseButtonState.Pressed:
                    self.mouseMiddleClick()
                    self.mouse.middle.state = self.MouseButtonState.Idle
                case self.MouseButtonState.Dragging:
                    self.mouseMiddleDragEnd()
                    self.mouse.middle.state = self.MouseButtonState.Idle
                case _:
                    logger.warning(f"Mouse middle button released when idle")

    def mouseDoubleClickEvent(self : Self, event : QMouseEvent) -> None:
        p = event.pos(); l = self.mapToScene(p)
        self.mouse.left.double.setPL(p, l)
        self.mouse.left.double.modifiers = self._getModifiers(event)
        if event.button() & Qt.MouseButton.LeftButton:
            self.mouseLeftDoubleClick()
        if event.button() & Qt.MouseButton.MiddleButton:
            self.mouseMiddleDoubleClick()

    def wheelEvent(self : Self, event : QWheelEvent) -> None:
        p = event.position().toPoint(); l = self.mapToScene(p)
        self.mouse.current.setPL(p, l)
        self.mouseWheel(
            event.angleDelta().y() / hub.settings.prefs.mouse.wheel,
            self._getModifiers(event)
        )

    ############################################################################
    # intermediate mouse methods

    def mouseLeftClick(self : Self) -> None:
        m = self.mouse.left.press.modifiers
        match self.state:
            case self.State.Idle:
                m = self.mouse.left.press.modifiers
                items = self._itemsAt(self.mouse.left.press.logical)
                for item in items:
                    if isinstance(item, Grip):
                        self.grip = item
                        break
                else:
                    self.grip = None
                if m == qkm.NoModifier and not self.grip:
                    self.scene().clearSelection()
                self._selectPoint(
                    self.mouse.current.logical,
                    m & qkm.ControlModifier,
                    m & qkm.AltModifier
                )
            case self.State.ViewPan1:
                self.wip.pos0 = self.mouse.left.release.physical
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self._goState(self.State.ViewPan2)
            case self.State.ViewPan2:
                delta = self.mouse.left.release.physical - self.wip.pos0
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() - delta.x()
                )
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() - delta.y()
                )
                self.wip.clear()
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self._goState(self.State.Idle)
            case self.State.ViewZoomWindow1:
                self.marquee.begin(self.mouse.left.release.physical)
                self._goState(self.State.ViewZoomWindow2)
            case self.State.ViewZoomWindow2:
                self.marquee.end(self.mouse.left.release.physical)
                self._zoomRect(self.marquee.rect())
                self._goState(self.State.Idle)
            case self.State.EditSlide1:
                self._selectPoint(
                    self.mouse.current.logical,
                    m == qkm.ControlModifier
                )
                self.slideBegin(
                    self._snap(self.mouse.left.release.logical)
                )
            case self.State.EditSlide2:
                self.slideComplete(
                    self._snap(self.mouse.left.release.logical)
                )
            case self.State.EditMove1:
                self._selectPoint(
                    self.mouse.current.logical,
                    m == qkm.ControlModifier
                )
                self.moveBegin(
                    self.scene().selectedItems(),
                    self._snap(self.mouse.left.release.logical)
                )
            case self.State.EditMove2:
                self.moveComplete(
                    self._snap(self.mouse.left.release.logical)
                )
            case self.State.PlaceRectangle1:
                self.placeRectangleBegin(
                    self._snap(self.mouse.left.release.logical)
                )
            case self.State.PlaceRectangle2:
                self.placeRectangleComplete(
                    self._snap(self.mouse.left.release.logical)
                )
            case self.State.PlaceText1:
                self.placeTextBegin(
                    self._snap(self.mouse.left.release.logical)
                )
            case self.State.PlaceText2:
                self.placeTextComplete(
                    self._snap(self.mouse.left.release.logical)
                )

    def mouseLeftDragBegin(self : Self) -> None:
        match self.state:
            case self.State.Idle:
                m = self.mouse.left.press.modifiers
                items = self._itemsAt(self.mouse.left.press.logical)
                for item in items:
                    if isinstance(item, Grip):
                        self.grip = item
                        break
                else:
                    self.grip = None
                if self.grip: # we"ve hit a grip
                    self.resizeBegin(
                        self.grip, self._snap(self.mouse.left.press.logical)
                    )
                else:
                    if not (m & (qkm.ControlModifier | qkm.ShiftModifier)):
                        self.scene().clearSelection()
                    self._selectPoint(
                        self.mouse.left.press.logical,
                        m & qkm.ControlModifier
                    )
                    items = self.scene().selectedItems()
                    if len(items): # slide/move
                        if m & qkm.AltModifier:
                            self.moveBegin(
                                items,
                                self._snap(self.mouse.left.press.logical)
                            )
                        else:
                            self.slideBegin(
                                items,
                                self._snap(self.mouse.left.press.logical)
                            )
                    else: # start marquee selection
                        self.marquee.begin(self.mouse.left.press.physical)
                        self._goState(self.State.SelectArea2)
            case self.State.ViewZoomWindow1:
                self.marquee.begin(self.mouse.left.press.physical)
                self._goState(self.State.ViewZoomWindow2)
            case self.State.PlaceRectangle1:
                self.placeRectangleBegin(
                    self._snap(self.mouse.left.press.logical)
                )

    def mouseLeftDragContinue(self : Self) -> None:
        match self.state:
            case self.State.SelectArea2:
                self.marquee.resize(self.mouse.current.physical)
            case self.State.ViewPan2:
                delta = self.mouse.current.physical - self.wip.pos0
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() - delta.x()
                )
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() - delta.y()
                )
                self.wip.pos0 = self.mouse.current.physical
            case self.State.ViewZoomWindow2:
                self.marquee.resize(self.mouse.current.physical)
            case self.State.EditSlide2:
                self.slideContinue(
                    self._snap(self.mouse.current.logical)
                )
            case self.State.EditMove2:
                self.moveContinue(
                    self._snap(self.mouse.current.logical)
                )
            case self.State.EditResize2:
                self.resizeContinue(self._snap(self.mouse.current.logical))
            case self.State.PlaceRectangle2:
                self.placeRectangleContinue(
                    self._snap(self.mouse.current.logical)
                )

    def mouseLeftDragEnd(self : Self) -> None:
        m = self.mouse.left.press.modifiers
        match self.state:
            case self.State.SelectArea2:
                self.marquee.end(self.mouse.left.release.physical)
                self._selectRect(
                    self.marquee.rect(),
                    m == qkm.ControlModifier
                )
                self._goState(self.State.Idle)
            case self.State.ViewZoomWindow2:
                self.marquee.end(self.mouse.left.release.physical)
                self._zoomRect(self.marquee.rect())
                self._goState(self.State.Idle)
            case self.State.EditSlide2:
                self.slideComplete(
                    self._snap(self.mouse.left.release.logical)
                )
            case self.State.EditMove2:
                self.moveComplete(
                    self._snap(self.mouse.left.release.logical)
                )
            case self.State.EditResize2:
                self.resizeComplete(self._snap(self.mouse.left.release.logical))
            case self.State.PlaceRectangle2:
                self.placeRectangleComplete(
                    self._snap(self.mouse.left.release.logical)
                )

    def mouseLeftDoubleClick(self : Self) -> None:
        pass

    def mouseMiddleClick(self : Self) -> None:
        pass

    def mouseMiddleDragBegin(self : Self) -> None:
        if self.state == self.State.Idle:
            match self.mouse.middle.press.modifiers:
                case Qt.KeyboardModifier.NoModifier:
                    self.wip.pos0 = self.mouse.current.physical
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
                    self._goState(self.State.ViewPan2)
                case Qt.KeyboardModifier.ControlModifier:
                    self.marquee.begin(self.mouse.middle.press.physical)
                    self._goState(self.State.ViewZoomWindow2)

    def mouseMiddleDragContinue(self : Self) -> None:
        match self.state:
            case self.State.ViewPan2:
                delta = self.mouse.current.physical - self.wip.pos0
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
                self.wip.pos0 = self.mouse.current.physical
            case self.State.ViewZoomWindow2:
                self.marquee.resize(self.mouse.current.physical)

    def mouseMiddleDragEnd(self : Self) -> None:
        match self.state:
            case self.State.ViewPan2:
                delta = self.mouse.current.physical - self.wip.pos0
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
                self.wip.clear()
                self.setCursor(Qt.CursorShape.ArrowCursor)
            case self.State.ViewZoomWindow2:
                self.marquee.end(self.mouse.middle.release.physical)
                self._zoomRect(self.marquee.rect())
                self._goState(self.State.Idle)

    def mouseMiddleDoubleClick(self : Self) -> None:
        pass

    def mouseMove(self : Self) -> None:
        match self.state:
            case self.State.ViewPan2:
                delta = self.mouse.current.physical - self.wip.pos0
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
                self.wip.pos0 = self.mouse.current.physical
            case self.State.ViewZoomWindow2:
                self.marquee.resize(self.mouse.current.physical)
            case self.State.EditSlide2:
                self.slideContinue(
                    self._snap(self.mouse.current.logical)
                )
            case self.State.EditMove2:
                self.moveContinue(
                    self._snap(self.mouse.current.logical)
                )
            case self.State.EditResize2:
                self.resizeContinue(
                    self._snap(self.mouse.current.logical)
                )
            case self.State.PlaceRectangle2:
                self.placeRectangleContinue(
                    self._snap(self.mouse.current.logical)
                )

    def mouseWheel(self : Self, n: int, modifiers: Qt.KeyboardModifier) -> None:
        match modifiers:
            case Qt.KeyboardModifier.NoModifier:      # pan up/down
                self.viewPanUp(n) if n >= 0 else self.viewPanDown(-n)
            case Qt.KeyboardModifier.ShiftModifier:   # pan left/right
                self.viewPanLeft(n) if n >= 0 else self.viewPanRight(-n)
            case Qt.KeyboardModifier.ControlModifier: # zoom in/out
                self.viewZoomIn(n) if n >= 0 else self.viewZoomOut(-n)

    ############################################################################
    # edit methods

    def editUndo(self : Self) -> None:
        self.scene().undo_stack.undo()

    def editRedo(self : Self) -> None:
        self.scene().undo_stack.redo()

    def editCancel(self : Self) -> None:
        scene : DrawingScene = self.scene()
        if self.wip.macro:
            scene.undo_stack.endMacro()
        scene.undo_stack.undo()
        self.wip.clear()
        self._goState(self.State.Idle)

    def editComplete(self : Self) -> None:
        match self.state:
            case self.State.PlaceRectangle2:
                self.placeRectangleComplete(
                    self._snap(self.mouse.current.logical)
                )

    def editCut(self : Self) -> None:
        print("TODO: editCut")

    def editCopy(self : Self) -> None:
        print("TODO: editCopy")

    def editPaste(self : Self) -> None:
        print("TODO: editPaste")

    def editDelete(self : Self) -> None:
        print("TODO: editDelete")

    def editSlide(self : Self) -> None:
        if self.scene().selectedItems():
            pos = self._snap(self._selectedItemsRect().center())
            self.slideBegin(self.scene().selectedItems(), pos)
        else:
            self._goState(self.State.EditSlide1)

    def editMove(self : Self) -> None:
        if self.scene().selectedItems():
            pos = self._snap(self._selectedItemsRect().center())
            self.moveBegin(self.scene().selectedItems(), pos)
        else:
            self._goState(self.State.EditMove1)

    ############################################################################
    # view methods

    def viewZoomAll(self : Self) -> None:
        rect = self._allItemsRect()
        if rect is None:
            self._zoomAbs(1)
        else:
            self._zoomRect(rect)

    def viewZoomWindow(self : Self) -> None:
        self._goState(self.State.ViewZoomWindow1)

    def viewZoomIn(self : Self, n : int = 1) -> None:
        self._zoomRelMouse((1 + hub.settings.prefs.display.zoom.step)**n)

    def viewZoomOut(self : Self, n : int = 1) -> None:
        self._zoomRelMouse((1 - hub.settings.prefs.display.zoom.step)**n)

    def viewPan(self : Self, n : int = 1) -> None:
        self._goState(self.State.ViewPan1)

    def viewPanLeft(self : Self, n : int = 1) -> None:
        self._pan(QPointF(hub.settings.prefs.display.pan.step * n, 0))

    def viewPanRight(self : Self, n : int = 1) -> None:
        self._pan(QPointF(-hub.settings.prefs.display.pan.step * n, 0))

    def viewPanUp(self : Self, n : int = 1) -> None:
        self._pan(QPointF(0, hub.settings.prefs.display.pan.step * n))

    def viewPanDown(self : Self, n : int = 1) -> None:
        self._pan(QPointF(0, -hub.settings.prefs.display.pan.step * n))

    def viewPrev(self : Self) -> None:
        pass

    def viewNext(self : Self) -> None:
        pass

    def viewGridDisplay(self : Self, checked : bool) -> None:
        self.grid.display = checked
        self.viewport().update()

    def viewGridSnap(self : Self, checked : bool) -> None:
        self.grid.snap = checked

    def viewGridSettings(self : Self) -> None:
        # TODO dialog required
        pass

    ############################################################################
    # place methods

    def placeRectangle(self : Self) -> None:
        self._goState(self.State.PlaceRectangle1)

    def placeRectangleCmd(
        self       : Self,
        size_or_p2 : QSizeF | QPointF,
        wip        : bool
    ) -> None:
        # TODO get default anchor and pen/brush/text spec from settings
        self.scene().undo_stack.push(cmdPlaceRectangle(
            scene      = self.scene(),
            element    = self.wip.elements[0],
            pos        = self.wip.pos0,
            size_or_p2 = size_or_p2,
            wip        = wip
        ))

    def placeRectangleBegin(self : Self, p1: QPointF) -> None:
        self.wip.elements = [Rectangle()]
        self.wip.pos0 = p1
        self.placeRectangleCmd(QSizeF(1,1), True)
        self._goState(self.State.PlaceRectangle2)

    def placeRectangleContinue(self : Self, p2: QPointF) -> None:
        self.placeRectangleCmd(p2, True)

    def placeRectangleComplete(self : Self, p2: QPointF) -> None:
        self.placeRectangleCmd(p2, False)
        self.wip.clear()
        self._goState(self.State.Idle)

    def placeText(self : Self) -> None:
        self._goState(self.State.PlaceText1)

    def placeTextCmd(self : Self, text : str, wip : bool) -> None:
        self.scene().undo_stack.push(cmdPlaceText(
            scene   = self.scene(),
            element = self.wip.elements[0],
            pos     = self.wip.pos0,
            text    = text,
            wip     = wip
        ))

    def placeTextBegin(self : Self, pos : QPointF) -> None:
        new_text = Text()
        self.wip.elements = [new_text]
        self.wip.pos0 = pos
        self.placeTextCmd("", True)
        new_text.setEditable(True)
        new_text.setFocus()
        self._goState(self.State.PlaceText2)

    def placeTextComplete(self : Self, pos : QPointF) -> None:
        self.wip.elements[0].clearFocus()

    def placeTextFinalize(self, text_item: Text):
        if text_item == self.wip.elements[0]:
            text = text_item.toPlainText().strip()
            if text:
                self.wip.elements[0].setEditable(False)
                self.placeTextCmd(text, False)
            else:
                self.scene().undo_stack.undo()
        else:
            logger.warning("placeTextFinalize: text_item != wip.elements[0]")
        self.wip.clear()
        self._goState(self.State.Idle)

    ############################################################################
    # slide methods
    # TODO: stretch connections

    def slideCmd(self  : Self, delta : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.undo_stack.push(cmdSlide(
            scene    = self.scene(),
            elements = self.wip.elements,
            delta    = delta
        ))

    def slideBegin(
        self     : Self,
        elements : list[Element],
        pos      : QPointF
    ) -> None:
        self.wip.macro = True
        self.wip.elements = elements
        self.wip.pos0 = pos
        scene : DrawingScene = self.scene()
        scene.undo_stack.beginMacro("Move")
        self._goState(self.State.EditMove2)

    def slideContinue(self : Self, pos : QPointF) -> None:
        self.slideCmd(pos - self.wip.pos0)
        self.wip.pos0 = pos

    def slideComplete(self : Self, pos : QPointF) -> None:
        self.slideCmd(pos - self.wip.pos0)
        self.wip.clear()
        scene : DrawingScene = self.scene()
        scene.undo_stack.endMacro()
        self._goState(self.State.Idle)

    ############################################################################
    # move methods

    def moveCmd(self  : Self, delta : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.undo_stack.push(cmdMove(
            scene    = self.scene(),
            elements = self.wip.elements,
            delta    = delta
        ))

    def moveBegin(
        self     : Self,
        elements : list[Element],
        pos      : QPointF
    ) -> None:
        self.wip.macro = True
        self.wip.elements = elements
        self.wip.pos0 = pos
        scene : DrawingScene = self.scene()
        scene.undo_stack.beginMacro("Move")
        self._goState(self.State.EditMove2)

    def moveContinue(self : Self, pos : QPointF) -> None:
        self.moveCmd(pos - self.wip.pos0)
        self.wip.pos0 = pos

    def moveComplete(self : Self, pos : QPointF) -> None:
        self.moveCmd(pos - self.wip.pos0)
        self.wip.clear()
        scene : DrawingScene = self.scene()
        scene.undo_stack.endMacro()
        self._goState(self.State.Idle)

    ############################################################################
    # resize methods

    def resizeCmd(self  : Self, delta : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.undo_stack.push(cmdResize(
            scene   = self.scene(),
            element = self.wip.elements[0],
            delta   = delta
        ))

    def resizeBegin(self : Self, grip : Grip, pos : QPointF) -> None:
        self.wip.macro = True
        self.wip.elements = [grip]
        self.wip.pos0 = pos
        scene : DrawingScene = self.scene()
        scene.undo_stack.beginMacro("Resize")
        self._goState(self.State.EditResize2)

    def resizeContinue(self : Self, pos : QPointF) -> None:
        self.resizeCmd(pos - self.wip.pos0)
        self.wip.pos0 = pos

    def resizeComplete(self : Self, pos : QPointF) -> None:
        self.resizeCmd(pos - self.wip.pos0)
        self.wip.clear()
        scene : DrawingScene = self.scene()
        scene.undo_stack.endMacro()
        self._goState(self.State.Idle)

    ############################################################################
    # private methods

    def _goState(self : Self, state : "DrawingView.State") -> None:
        self.state = state
        if hub.main_window is not None:
            hub.main_window.status_bar.tip.setText(self.StateTip[state])

    def _allItemsRect(self : Self) -> Optional[QRectF]:
        items_rect = None
        if hasattr(self.scene(), "paper_rect"):
            items_rect = self.scene().paper_rect()
        for item in self.scene().items():
            item_rect = item.mapToScene(item.boundingRect()).boundingRect()
            items_rect = item_rect if items_rect is None else \
                items_rect.united(item_rect)
        return items_rect

    def _selectedItemsRect(self : Self) -> Optional[QRectF]:
        items_rect = None
        for item in self.scene().selectedItems():
            item_rect = item.mapToScene(item.boundingRect()).boundingRect()
            items_rect = item_rect if items_rect is None else \
                items_rect.united(item_rect)
        return items_rect

    def _pan(self : Self, delta: QPointF) -> None:
        lrect = self.mapToScene(self.viewport().rect()).boundingRect()  # Scene coords
        pan = QPointF(lrect.width()  * delta.x(), lrect.height() * delta.y())
        transform = self.transform()
        pdelta = QPointF(transform.m11() * pan.x(), transform.m22() * pan.y())
        self.horizontalScrollBar().setValue(
            self.horizontalScrollBar().value() - int(pdelta.x())
        )
        self.verticalScrollBar().setValue(
            self.verticalScrollBar().value() - int(pdelta.y())
        )
        self.mouse.current.setPL(
            self.mapFromGlobal(QCursor.pos()),
            self.mapToScene(self.mouse.current.physical)
        )

    def _zoomAbs(self : Self, abs: float) -> None:
        abs = max(abs, hub.settings.prefs.display.zoom.limit.min)
        abs = min(abs, hub.settings.prefs.display.zoom.limit.max)
        self.zoom = abs
        self.resetTransform()
        self.scale(self.zoom, self.zoom)
        hub.main_window.status_bar.zoom.setText(
            "{:.2f}%".format(self.zoom * 100)
        )
        hub.main_window.actions.actionEnable(
            "viewZoomIn",  self.zoom < hub.settings.prefs.display.zoom.limit.max
        )
        hub.main_window.actions.actionEnable(
            "viewZoomOut", self.zoom > hub.settings.prefs.display.zoom.limit.min
        )

    def _zoomRel(self : Self, rel: float) -> None:
        self._zoomAbs(self.zoom * rel)

    def _zoomRelMouse(self : Self, rel: float) -> None:
        ppos_old = self.mouse.current.physical
        lpos_old = self.mouse.current.logical
        self._zoomRel(rel)
        ppos_new = self.mapFromScene(lpos_old)
        delta = ppos_new - ppos_old
        self.horizontalScrollBar().setValue(
            self.horizontalScrollBar().value() + delta.x()
        )
        self.verticalScrollBar().setValue(
            self.verticalScrollBar().value() + delta.y()
        )
        self.mouse.current.setPL(
            self.mapFromGlobal(QCursor.pos()),
            self.mapToScene(self.mouse.current.physical)
        )

    def _zoomRect(self : Self, rect : QRectF) -> None:
        factor = min(
            self.viewport().width()  / rect.width(),
            self.viewport().height() / rect.height()
            ) * (1 - hub.settings.prefs.display.zoom.padding)
        self._zoomAbs(factor)
        self.centerOn(rect.center())

    def _round2nearest(self : Self, x : float, n : float) -> float:
        return round(x / n) * n

    def _snap(self : Self, pos: QPointF) -> QPoint:
        return QPointF(
            self._round2nearest(pos.x(), self.grid.pitch.x()),
            self._round2nearest(pos.y(), self.grid.pitch.y())
        ) if self.grid.snap else pos

    def _distance(self : Self, cp1: QPoint, cp2: QPoint) -> int:
        return int(round(sqrt((cp1.x() - cp2.x())**2 + (cp1.y() - cp2.y())**2)))

    def _getModifiers(
        self  : Self,
        event : QMouseEvent
    ) -> Qt.KeyboardModifier:
        qkm = Qt.KeyboardModifier
        mask = qkm.ControlModifier | qkm.ShiftModifier | qkm.AltModifier
        return event.modifiers() & mask

    def _setLayer(self : Self, layer: "DrawingView.Layer") -> None:
        self.layer = layer
        for item in self.scene().items():
            item.setFlag(
                QGraphicsItem.GraphicsItemFlag.ItemIsSelectable,
                item.zValue() in layer.value
            )
            item.setSelected(False)

    def _itemsAt(self : Self, point: QPointF) -> list[QGraphicsItem]:
        items = self.scene().items(
            point,
            Qt.ItemSelectionMode.IntersectsItemShape,
            Qt.SortOrder.DescendingOrder,
            self.viewportTransform()
        )
        return [i for i in items if i.zValue() in self.layer.value]

    def _selectRect(
        self   : Self,
        rect   : QRectF,
        toggle : bool = False
    ) -> None:
        path = QPainterPath()
        path.addRect(rect)
        if toggle:
            items = self.scene().items(
                path,
                Qt.ItemSelectionMode.IntersectsItemShape,
                Qt.SortOrder.AscendingOrder,
                self.viewportTransform()
            )
            for item in items:
                item.setSelected(not item.isSelected())
        else:
            self.scene().setSelectionArea(
                path,
                Qt.ItemSelectionOperation.AddToSelection,
                Qt.ItemSelectionMode.IntersectsItemShape,
                self.transform()
            )
        for item in self.scene().selectedItems():
            if hasattr(item, "updateGripsVisibility"):
                item.updateGripsVisibility()

    def _selectPoint(
        self   : Self,
        point  : QPointF,
        toggle : bool = False,
        choice : bool = False
    ) -> None:
        items = self._itemsAt(point)
        if len(items) > 1 and choice: # multiple choice case
            init_sel = {item: item.isSelected() for item in items}
            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu::item {
                    padding: 2px 10px 2px 4px;  /* Reduce left padding */
                }
                QMenu::icon {
                    width: 0px;  /* Ensure no space for icons */
                }
            """)
            for item in items:
                text = f"{item.__class__.__name__}"
                action = QAction(text, self)
                action.setIcon(QIcon())
                action.setData(item)
                action.triggered.connect(
                    lambda checked, i=item, t=toggle, p=init_sel[item]:
                    self._selectItem(i, t, p)
                )
                menu.addAction(action)
            def _onHover(action):
                for item in items:
                    item.setSelected(init_sel[item])
                item = action.data() if action else None
                if item:
                    self._selectItem(item, toggle, init_sel[item])
            menu.hovered.connect(_onHover)
            menu.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            menu.setFocus()
            menu.exec(self.mapToGlobal(self.mapFromScene(point)))
        elif items: # single or top item case
            item = items[0]
            if toggle:
                item.setSelected(not item.isSelected())
            else:
                item.setSelected(True)
        for item in self.scene().selectedItems():
            if hasattr(item, "updateGripsVisibility"):
                item.updateGripsVisibility()

    def _selectItem(self : Self, item, toggle, prev=None):
        if prev is None:
            item.setSelected(not item.isSelected() if toggle else True)
        else:
            item.setSelected(not prev if toggle else True)

class DrawingSubWindow(QMdiSubWindow):
    def __init__(
        self   : Self,
        parent : Optional[QMdiArea] = None
    ) -> None:
        if parent is None:
            parent = hub.main_window.mdi_area
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

    def closeEvent(self, event: QCloseEvent) -> None:
        if isinstance(self.widget(), DrawingView):
            scene = self.widget().scene()
            if scene and scene.undo_stack:
                try:
                    scene.undo_stack.canUndoChanged.disconnect()
                    scene.undo_stack.canRedoChanged.disconnect()
                    scene.selectionChanged.disconnect()
                except TypeError:
                    pass
        hub.main_window.menu_bar.updateWindowMenu()
        super().closeEvent(event)
