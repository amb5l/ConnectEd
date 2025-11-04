from PyQt6.QtCore import Qt

from .base  import DrawingViewStateBase
from .idle  import DrawingViewStateIdle
from .view  import DrawingViewStateViewPan1, \
                   DrawingViewStateViewPan2, \
                   DrawingViewStateViewZoomArea1, \
                   DrawingViewStateViewZoomArea2
from .edit  import DrawingViewStateEditSelectArea1, \
                   DrawingViewStateEditSelectArea2, \
                   DrawingViewStateEditPaste, \
                   DrawingViewStateEditDuplicate, \
                   DrawingViewStateEditSlide, \
                   DrawingViewStateEditMove, \
                   DrawingViewStateEditResize, \
                   DrawingViewStateEditMovePins, \
                   DrawingViewStateEditAdjustPolySeg, \
                   DrawingViewStateEditAppearance, \
                   DrawingViewStateEditProperties, \
                   DrawingViewStateEditQuery, \
                   DrawingViewStateEditPort, \
                   DrawingViewStateEditBlockPin, \
                   DrawingViewStateEditText, \
                   DrawingViewStateEditPropertyText
from .place import DrawingViewStatePlaceConn1, \
                   DrawingViewStatePlaceConn2, \
                   DrawingViewStatePlacePort, \
                   DrawingViewStatePlaceBlock1, \
                   DrawingViewStatePlaceBlock2, \
                   DrawingViewStatePlaceBlockPin, \
                   DrawingViewStatePlaceSymbolPin, \
                   DrawingViewStatePlaceLine1, \
                   DrawingViewStatePlaceLine2, \
                   DrawingViewStatePlaceRectangle1, \
                   DrawingViewStatePlaceRectangle2, \
                   DrawingViewStatePlaceEllipse1, \
                   DrawingViewStatePlaceEllipse2, \
                   DrawingViewStatePlacePolyline1, \
                   DrawingViewStatePlacePolyline2, \
                   DrawingViewStatePlaceText, \
                   DrawingViewStatePlaceTextBlock

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


class DrawingViewStateMixin:
    state                  : DrawingViewStateBase
    stateIdle              : DrawingViewStateIdle
    stateViewPan1          : DrawingViewStateViewPan1
    stateViewPan2          : DrawingViewStateViewPan2
    stateViewZoomArea1     : DrawingViewStateViewZoomArea1
    stateViewZoomArea2     : DrawingViewStateViewZoomArea2
    stateEditSelectArea1   : DrawingViewStateEditSelectArea1
    stateEditSelectArea2   : DrawingViewStateEditSelectArea2
    stateEditPaste         : DrawingViewStateEditPaste
    stateEditDuplicate     : DrawingViewStateEditDuplicate
    stateEditSlide         : DrawingViewStateEditSlide
    stateEditMove          : DrawingViewStateEditMove
    stateEditResize        : DrawingViewStateEditResize
    stateEditMovePins      : DrawingViewStateEditMovePins
    stateEditAdjustPolySeg : DrawingViewStateEditAdjustPolySeg
    stateEditAppearance    : DrawingViewStateEditAppearance
    stateEditProperties    : DrawingViewStateEditProperties
    stateEditQuery         : DrawingViewStateEditQuery
    stateEditPort          : DrawingViewStateEditPort
    stateEditBlockPin      : DrawingViewStateEditBlockPin
    stateEditText          : DrawingViewStateEditText
    stateEditPropertyText  : DrawingViewStateEditPropertyText
    statePlacePort         : DrawingViewStatePlacePort
    statePlaceBlock1       : DrawingViewStatePlaceBlock1
    statePlaceBlock2       : DrawingViewStatePlaceBlock2
    statePlaceBlockPin     : DrawingViewStatePlaceBlockPin
    statePlaceSymbolPin    : DrawingViewStatePlaceSymbolPin
    statePlaceRectangle1   : DrawingViewStatePlaceRectangle1
    statePlaceRectangle2   : DrawingViewStatePlaceRectangle2
    statePlaceEllipse1     : DrawingViewStatePlaceEllipse1
    statePlaceEllipse2     : DrawingViewStatePlaceEllipse2
    statePlacePolyline1    : DrawingViewStatePlacePolyline1
    statePlacePolyline2    : DrawingViewStatePlacePolyline2
    statePlaceText         : DrawingViewStatePlaceText
    statePlaceTextBlock    : DrawingViewStatePlaceTextBlock
    statePlaceConn1        : DrawingViewStatePlaceConn1
    statePlaceConn2        : DrawingViewStatePlaceConn2

    def initStates(self : "DrawingView") -> None:
        self.stateIdle              = DrawingViewStateIdle             (self)
        self.stateViewPan1          = DrawingViewStateViewPan1         (self)
        self.stateViewPan2          = DrawingViewStateViewPan2         (self)
        self.stateViewZoomArea1     = DrawingViewStateViewZoomArea1    (self)
        self.stateViewZoomArea2     = DrawingViewStateViewZoomArea2    (self)
        self.stateEditSelectArea1   = DrawingViewStateEditSelectArea1  (self)
        self.stateEditSelectArea2   = DrawingViewStateEditSelectArea2  (self)
        self.stateEditPaste         = DrawingViewStateEditPaste        (self)
        self.stateEditDuplicate     = DrawingViewStateEditDuplicate    (self)
        self.stateEditSlide         = DrawingViewStateEditSlide        (self)
        self.stateEditMove          = DrawingViewStateEditMove         (self)
        self.stateEditResize        = DrawingViewStateEditResize       (self)
        self.stateEditMovePins      = DrawingViewStateEditMovePins     (self)
        self.stateEditAdjustPolySeg = DrawingViewStateEditAdjustPolySeg (self)
        self.stateEditAppearance    = DrawingViewStateEditAppearance   (self)
        self.stateEditProperties    = DrawingViewStateEditProperties   (self)
        self.stateEditQuery         = DrawingViewStateEditQuery        (self)
        self.stateEditPort          = DrawingViewStateEditPort         (self)
        self.stateEditBlockPin      = DrawingViewStateEditBlockPin     (self)
        self.stateEditText          = DrawingViewStateEditText         (self)
        self.stateEditPropertyText  = DrawingViewStateEditPropertyText (self)
        self.statePlaceConn1        = DrawingViewStatePlaceConn1       (self)
        self.statePlaceConn2        = DrawingViewStatePlaceConn2       (self)
        self.statePlacePort         = DrawingViewStatePlacePort        (self)
        self.statePlaceBlock1       = DrawingViewStatePlaceBlock1      (self)
        self.statePlaceBlock2       = DrawingViewStatePlaceBlock2      (self)
        self.statePlaceBlockPin     = DrawingViewStatePlaceBlockPin    (self)
        self.statePlaceSymbolPin    = DrawingViewStatePlaceSymbolPin   (self)
        self.statePlaceLine1        = DrawingViewStatePlaceLine1       (self)
        self.statePlaceLine2        = DrawingViewStatePlaceLine2       (self)
        self.statePlaceRectangle1   = DrawingViewStatePlaceRectangle1  (self)
        self.statePlaceRectangle2   = DrawingViewStatePlaceRectangle2  (self)
        self.statePlaceEllipse1     = DrawingViewStatePlaceEllipse1    (self)
        self.statePlaceEllipse2     = DrawingViewStatePlaceEllipse2    (self)
        self.statePlacePolyline1    = DrawingViewStatePlacePolyline1   (self)
        self.statePlacePolyline2    = DrawingViewStatePlacePolyline2   (self)
        self.statePlaceText         = DrawingViewStatePlaceText        (self)
        self.statePlaceTextBlock    = DrawingViewStatePlaceTextBlock   (self)
