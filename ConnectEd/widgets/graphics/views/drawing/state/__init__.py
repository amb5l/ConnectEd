from .base  import DrawingViewStateBase
from .view  import DrawingViewStateViewPan1,              \
                   DrawingViewStateViewPan2,              \
                   DrawingViewStateViewZoomArea1,         \
                   DrawingViewStateViewZoomArea2
from .edit  import DrawingViewStateEditSelectArea1,       \
                   DrawingViewStateEditSelectArea2,       \
                   DrawingViewStateEditPaste,             \
                   DrawingViewStateEditDuplicate,         \
                   DrawingViewStateEditSlide,             \
                   DrawingViewStateEditMove,              \
                   DrawingViewStateEditResize,            \
                   DrawingViewStateEditMovePins,          \
                   DrawingViewStateEditAdjustPolySeg,     \
                   DrawingViewStateEditAppearance,        \
                   DrawingViewStateEditItemProperties,    \
                   DrawingViewStateEditDrawingProperties, \
                   DrawingViewStateEditQuery,             \
                   DrawingViewStateEditText,              \
                   DrawingViewStateEditPropertyText
from .place import DrawingViewStatePlaceSymbolPin,        \
                   DrawingViewStatePlaceLine1,            \
                   DrawingViewStatePlaceLine2,            \
                   DrawingViewStatePlaceRectangle1,       \
                   DrawingViewStatePlaceRectangle2,       \
                   DrawingViewStatePlaceEllipse1,         \
                   DrawingViewStatePlaceEllipse2,         \
                   DrawingViewStatePlacePolyline1,        \
                   DrawingViewStatePlacePolyline2,        \
                   DrawingViewStatePlaceText

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


class DrawingViewStateMixin:
    state                      : DrawingViewStateBase                   # noqa N815
    stateViewPan1              : DrawingViewStateViewPan1               # noqa N815
    stateViewPan2              : DrawingViewStateViewPan2               # noqa N815
    stateViewZoomArea1         : DrawingViewStateViewZoomArea1          # noqa N815
    stateViewZoomArea2         : DrawingViewStateViewZoomArea2          # noqa N815
    stateEditSelectArea1       : DrawingViewStateEditSelectArea1        # noqa N815
    stateEditSelectArea2       : DrawingViewStateEditSelectArea2        # noqa N815
    stateEditPaste             : DrawingViewStateEditPaste              # noqa N815
    stateEditDuplicate         : DrawingViewStateEditDuplicate          # noqa N815
    stateEditSlide             : DrawingViewStateEditSlide              # noqa N815
    stateEditMove              : DrawingViewStateEditMove               # noqa N815
    stateEditResize            : DrawingViewStateEditResize             # noqa N815
    stateEditMovePins          : DrawingViewStateEditMovePins           # noqa N815
    stateEditAdjustPolySeg     : DrawingViewStateEditAdjustPolySeg      # noqa N815
    stateEditAppearance        : DrawingViewStateEditAppearance         # noqa N815
    stateEditItemProperties    : DrawingViewStateEditItemProperties     # noqa N815
    stateEditDrawingProperties : DrawingViewStateEditDrawingProperties  # noqa N815
    stateEditQuery             : DrawingViewStateEditQuery              # noqa N815
    stateEditText              : DrawingViewStateEditText               # noqa N815
    stateEditPropertyText      : DrawingViewStateEditPropertyText       # noqa N815
    statePlaceSymbolPin        : DrawingViewStatePlaceSymbolPin         # noqa N815
    statePlaceRectangle1       : DrawingViewStatePlaceRectangle1        # noqa N815
    statePlaceRectangle2       : DrawingViewStatePlaceRectangle2        # noqa N815
    statePlaceEllipse1         : DrawingViewStatePlaceEllipse1          # noqa N815
    statePlaceEllipse2         : DrawingViewStatePlaceEllipse2          # noqa N815
    statePlacePolyline1        : DrawingViewStatePlacePolyline1         # noqa N815
    statePlacePolyline2        : DrawingViewStatePlacePolyline2         # noqa N815
    statePlaceText             : DrawingViewStatePlaceText              # noqa N815

    def initStates(self : "DrawingView") -> None:
        self.stateViewPan1              = DrawingViewStateViewPan1              (self)
        self.stateViewPan2              = DrawingViewStateViewPan2              (self)
        self.stateViewZoomArea1         = DrawingViewStateViewZoomArea1         (self)
        self.stateViewZoomArea2         = DrawingViewStateViewZoomArea2         (self)
        self.stateEditSelectArea1       = DrawingViewStateEditSelectArea1       (self)
        self.stateEditSelectArea2       = DrawingViewStateEditSelectArea2       (self)
        self.stateEditPaste             = DrawingViewStateEditPaste             (self)
        self.stateEditDuplicate         = DrawingViewStateEditDuplicate         (self)
        self.stateEditSlide             = DrawingViewStateEditSlide             (self)
        self.stateEditMove              = DrawingViewStateEditMove              (self)
        self.stateEditResize            = DrawingViewStateEditResize            (self)
        self.stateEditMovePins          = DrawingViewStateEditMovePins          (self)
        self.stateEditAdjustPolySeg     = DrawingViewStateEditAdjustPolySeg     (self)
        self.stateEditAppearance        = DrawingViewStateEditAppearance        (self)
        self.stateEditItemProperties    = DrawingViewStateEditItemProperties    (self)
        self.stateEditDrawingProperties = DrawingViewStateEditDrawingProperties (self)
        self.stateEditQuery             = DrawingViewStateEditQuery             (self)
        self.stateEditText              = DrawingViewStateEditText              (self)
        self.stateEditPropertyText      = DrawingViewStateEditPropertyText      (self)
        self.statePlaceSymbolPin        = DrawingViewStatePlaceSymbolPin        (self)
        self.statePlaceLine1            = DrawingViewStatePlaceLine1            (self)
        self.statePlaceLine2            = DrawingViewStatePlaceLine2            (self)
        self.statePlaceRectangle1       = DrawingViewStatePlaceRectangle1       (self)
        self.statePlaceRectangle2       = DrawingViewStatePlaceRectangle2       (self)
        self.statePlaceEllipse1         = DrawingViewStatePlaceEllipse1         (self)
        self.statePlaceEllipse2         = DrawingViewStatePlaceEllipse2         (self)
        self.statePlacePolyline1        = DrawingViewStatePlacePolyline1        (self)
        self.statePlacePolyline2        = DrawingViewStatePlacePolyline2        (self)
        self.statePlaceText             = DrawingViewStatePlaceText             (self)
