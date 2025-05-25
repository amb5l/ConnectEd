__all__ = ["DrawingView", "DrawingSubWindow"]

from typing import Self, Optional
from enum   import Enum, auto
from math   import ceil

from PyQt6.QtCore    import Qt, QPoint, QPointF, QRectF, QEvent
from PyQt6.QtWidgets import QMdiArea, QMdiSubWindow, \
                            QGraphicsView, QGraphicsItem, QGraphicsTextItem
from PyQt6.QtGui     import QPainter, QPen, QCloseEvent, QKeyEvent

from .....core import logger, paste, LAYER_SHEET, LAYER_DRAWING

from ....dialogs import AppearanceDialog
from ....marquee import Marquee

from ...scenes import DrawingScene
from ...items  import Element, TextBlock, cmdMove

from .mouse   import DrawingViewMouseMixin
from .private import DrawingViewPrivateMixin

from ..... import hub


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
        s = hub.settings.get("defaults/grid")
        self.display    = s.display
        self.snap       = s.snap
        self.pitch      = s.pitch
        self.dots       = s.dots
        self.alpha      = s.alpha
        self.min_pixels = s.min_pixels

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
    EditPaste       = auto()
    EditSlide1      = auto()
    EditSlide2      = auto()
    EditMove1       = auto()
    EditMove2       = auto()
    EditResize1     = auto()
    EditResize2     = auto()
    EditResize3     = auto()
    EditAppearance1 = auto()
    EditAppearance2 = auto()
    PlaceRectangle1 = auto()
    PlaceRectangle2 = auto()
    PlaceTextBlock1 = auto()
    PlaceTextBlock2 = auto()

DrawingViewStateTip = {
    DrawingViewState.Idle            : "Idle",
    DrawingViewState.ViewPan1        : "Pan: pick the first point",
    DrawingViewState.ViewPan2        : "Pan: pick the second point",
    DrawingViewState.ViewZoomWindow1 : "Zoom Window: pick the first point",
    DrawingViewState.ViewZoomWindow2 : "Zoom Window: pick the second point",
    DrawingViewState.SelectArea2     : "Select: complete the marquee selection",
    DrawingViewState.EditPaste       : "Paste: select the paste position",
    DrawingViewState.EditSlide1      : "Slide: select one or more items",
    DrawingViewState.EditSlide2      : "Slide: place the selected item(s) as required",
    DrawingViewState.EditMove1       : "Move: select one or more items",
    DrawingViewState.EditMove2       : "Move: place the selected item(s) as required",
    DrawingViewState.EditResize1     : "Resize: select a single resizeable item",
    DrawingViewState.EditResize2     : "Resize: select a grip to begin resizing",
    DrawingViewState.EditResize3     : "Resize: place the selected grip as required",
    DrawingViewState.EditAppearance1 : "Appearance: select one or more items",
    DrawingViewState.EditAppearance2 : "Appearance: specify changes",
    DrawingViewState.PlaceRectangle1 : "Place Rectangle: pick the first point",
    DrawingViewState.PlaceRectangle2 : "Place Rectangle: pick the second point",
    DrawingViewState.PlaceTextBlock1 : "Place Text Block: pick a position",
    DrawingViewState.PlaceTextBlock2 : "Place Text Block: enter the text"
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

class DrawingView(
    DrawingViewMouseMixin,
    QGraphicsView,
    DrawingViewPrivateMixin
):

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
        scene.textEditingComplete.connect(self.placeTextBlockFinalize)
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
            color = hub.settings.getTheme("grid/line")
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
        self.scene().clearSelection()
        self._goState(self.State.Idle)

    def editComplete(self : Self) -> None:
        # TODO seriously consider this
        match self.state:
            case self.State.PlaceRectangle2:
                self.placeRectangleComplete(
                    self._snap(self.mouse.current.logical)
                )

    def editCut(self : Self) -> None:
        print("TODO: editCut")

    def editCopy(self : Self) -> None:
        scene : DrawingScene = self.scene()
        scene.editCopy(self._snap(self.mouse.current.logical))

    def editPaste(self : Self) -> None:
        scene : DrawingScene = self.scene()
        self.wip.clear()
        items, copy_pos = paste()
        if not items:
            logger.warning("No valid data to paste")
            self._goState(self.State.Idle)
            return
        elements = [item for item in items if isinstance(item, Element)]
        if not elements:
            logger.warning("No valid elements to paste")
            self._goState(self.State.Idle)
            return
        # Clear key points for existing items
        scene.clearSelection()
        for item in scene.items():
            if isinstance(item, Element):
                item.setKPVisible(False)
        self.wip.elements = elements
        self.wip.pos0 = elements[0].pos() if copy_pos is None and elements else copy_pos or QPointF(0, 0)
        pos = self._snap(self.mouse.current.logical)
        offset = pos - self.wip.pos0
        # Block signals to batch initial setup
        scene.blockSignals(True)
        for element in elements:
            if element.scene() != scene:
                scene.addItem(element)
            element.setPos(element.pos() + offset)
            element.setSelected(True)
            element.setKPVisible(False)  # Explicitly hide keypoints
        scene.blockSignals(False)
        # Manually trigger selection changed to update key points
        scene.selectionChanged.emit()
        self.wip.macro = True
        scene.undo_stack.beginMacro("Paste Elements")
        self._goState(self.State.EditPaste)

    def editPasteContinue(self : Self) -> None:
        scene : DrawingScene = self.scene()
        if not self.wip.elements:
            logger.warning("editPasteContinue: No elements in wip, aborting")
            self._goState(self.State.Idle)
            return
        new_pos = self._snap(self.mouse.current.logical)
        mouse_delta = new_pos - self.wip.pos0
        # Block signals to avoid multiple selection updates
        scene.blockSignals(True)
        for element in self.wip.elements:
            if element.scene() == scene:
                element.setPos(element.pos() + mouse_delta)
                element.setSelected(True)  # Ensure elements remain selected
                element.setKPVisible(False)  # Explicitly hide keypoints
        scene.blockSignals(False)
        # Manually trigger selection changed to update key points
        scene.selectionChanged.emit()
        self.wip.pos0 = new_pos

    def editPasteComplete(self : Self) -> None:
        scene : DrawingScene = self.scene()
        if not self.wip.elements:
            logger.warning("editPasteComplete: No elements in wip, aborting")
            self._goState(self.State.Idle)
            return
        pos = self._snap(self.mouse.current.logical)
        offset = pos - self.wip.pos0
        for element in self.wip.elements:
            if element.scene() == scene:
                scene.removeItem(element)
                element.setPos(element.pos() - offset)
        scene.editPaste(pos, (self.wip.elements, self.wip.pos0))
        if self.wip.macro:
            scene.undo_stack.endMacro()
        self.wip.clear()
        self._goState(self.State.Idle)

    def editDelete(self : Self) -> None:
        print("TODO: DrawingView.editDelete")

    def editSlide(self : Self) -> None:
        if self.scene().selectedItems():
            pos = self._snap(self._selectedItemsRect().center())
            self.moveBegin(self.scene().selectedItems(), pos, True)
        else:
            self._goState(self.State.EditSlide1)

    def editMove(self : Self) -> None:
        if self.scene().selectedItems():
            pos = self._snap(self._selectedItemsRect().center())
            self.moveBegin(self.scene().selectedItems(), pos)
            self._goState(self.State.EditMove2)
        else:
            self._goState(self.State.EditMove1)

    def editResize(self : Self) -> None:
        if len(self.scene().selectedItems()) == 1:
            self._goState(self.State.EditResize2)
        else:
            self.scene().clearSelection()
            self._goState(self.State.EditResize1)

    def editAppearance(
        self : Self,
        elements : Element | list[Element] = []
    ) -> None:
        scene : DrawingScene = self.scene()
        if scene.selectedItems():
            elements = scene.selectedItems()
        elif not isinstance(elements, list):
            elements = [elements]
        if elements:
            self._goState(self.State.EditAppearance2)
            dialog = AppearanceDialog(elements)
            if dialog.exec():
                scene.editAppearance(
                    scene.selectedItems(),
                    dialog.getChoice()
                )
            self._goState(self.State.Idle)
        else:
            self._goState(self.State.EditAppearance1)

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
        self._zoomRelMouse((1 + hub.settings.get("display/zoom/step"))**n)

    def viewZoomOut(self : Self, n : int = 1) -> None:
        self._zoomRelMouse((1 - hub.settings.get("display/zoom/step"))**n)

    def viewPan(self : Self, n : int = 1) -> None:
        self._goState(self.State.ViewPan1)

    def viewPanLeft(self : Self, n : int = 1) -> None:
        self._pan(QPointF(hub.settings.get("display/pan/step") * n, 0))

    def viewPanRight(self : Self, n : int = 1) -> None:
        self._pan(QPointF(-hub.settings.get("display/pan/step") * n, 0))

    def viewPanUp(self : Self, n : int = 1) -> None:
        self._pan(QPointF(0, hub.settings.get("display/pan/step") * n))

    def viewPanDown(self : Self, n : int = 1) -> None:
        self._pan(QPointF(0, -hub.settings.get("display/pan/step") * n))

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

    def placeRectangleBegin(self : Self, p1: QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.clearSelection()
        self.wip.clear()
        element = scene.placeRectangle(p1)
        self.wip.elements = [element]
        self.wip.pos0 = p1
        self.wip.elements[0].setSelected(True) # explicitly select the rectangle
        self.wip.elements[0].setKPVisible(True) # ensure keypoints are visible
        self._goState(self.State.PlaceRectangle2)

    def placeRectangleContinue(self : Self, p2: QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeRectangle(self.wip.pos0, p2, inst=self.wip.elements[0])

    def placeRectangleComplete(self : Self, p2: QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.placeRectangle(self.wip.pos0, p2, inst=self.wip.elements[0])
        self.wip.clear()
        self._goState(self.State.Idle)

    def placeTextBlock(self : Self) -> None:
        self._goState(self.State.PlaceTextBlock1)

    def placeTextBlockBegin(self : Self, pos : QPointF) -> None:
        scene : DrawingScene = self.scene()
        scene.clearSelection()
        self.wip.clear()
        element = scene.placeTextBlock("", pos)
        element.setEditable(True)
        element.setFocus()
        self.wip.elements = [element]
        self.wip.pos0 = pos
        self._goState(self.State.PlaceTextBlock2)

    def placeTextBlockComplete(self : Self) -> None:
        self.wip.elements[0].clearFocus()

    def placeTextBlockFinalize(self, text_item: TextBlock):
        scene : DrawingScene = self.scene()
        if text_item == self.wip.elements[0]:
            text = text_item.toPlainText()
            if text:
                self.wip.elements[0].setEditable(False)
                self.wip.elements[0].update()
                scene.placeTextBlock(text, self.wip.pos0, inst=self.wip.elements[0])
            else: # cancel empty text
                self.scene().undo_stack.undo()
        else:
            logger.warning("placeTextBlockFinalize: text_item != wip.elements[0]")
        self.wip.clear()
        self._goState(self.State.Idle)

    ############################################################################
    # move methods

    def moveCmd(self  : Self, delta : QPointF, slide : bool = False) -> None:
        scene : DrawingScene = self.scene()
        scene.undo_stack.push(cmdMove(
            scene    = self.scene(),
            elements = self.wip.elements,
            delta    = delta,
            slide    = slide
        ))

    def moveBegin(
        self     : Self,
        elements : list[Element],
        pos      : QPointF,
        slide    : bool = False
    ) -> None:
        self.wip.macro = True
        self.wip.elements = elements
        self.wip.pos0 = pos
        scene : DrawingScene = self.scene()
        scene.undo_stack.beginMacro("Move")

    def moveContinue(self : Self, pos : QPointF, slide : bool = False) -> None:
        self.moveCmd(pos - self.wip.pos0, slide)
        self.wip.pos0 = pos

    def moveComplete(self : Self, pos : QPointF, slide : bool = False) -> None:
        self.moveCmd(pos - self.wip.pos0, slide)
        self.wip.clear()
        scene : DrawingScene = self.scene()
        scene.undo_stack.endMacro()

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
