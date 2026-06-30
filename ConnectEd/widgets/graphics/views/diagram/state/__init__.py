from __future__ import annotations

from typing import Self

from .idle  import DiagramViewStateIdle

from .view  import (
    DiagramViewStateViewPan1,
    DiagramViewStateViewPan2,
    DiagramViewStateViewZoomArea1,
    DiagramViewStateViewZoomArea2
)
from .edit  import (
    DiagramViewStateEditSelectArea1,
    DiagramViewStateEditSelectArea2,
    DiagramViewStateEditPaste,
    DiagramViewStateEditDuplicate,
    DiagramViewStateEditSlide,
    DiagramViewStateEditMove,
    DiagramViewStateEditResize,
    DiagramViewStateEditMovePins,
    DiagramViewStateEditAdjustPolySeg,
    DiagramViewStateEditAppearance,
    DiagramViewStateEditItemProperties,
    DiagramViewStateEditDiagramProperties,
    DiagramViewStateEditQuery,
    DiagramViewStateEditText,
    DiagramViewStateEditPropertyText,
    DiagramViewStateEditPort,
    DiagramViewStateEditBlockPin
)
from .place import (
    DiagramViewStatePlaceSymbolPin,
    DiagramViewStatePlaceLine1,
    DiagramViewStatePlaceLine2,
    DiagramViewStatePlaceRectangle1,
    DiagramViewStatePlaceRectangle2,
    DiagramViewStatePlaceEllipse1,
    DiagramViewStatePlaceEllipse2,
    DiagramViewStatePlacePolyline1,
    DiagramViewStatePlacePolyline2,
    DiagramViewStatePlaceText,
    DiagramViewStatePlaceConn1,
    DiagramViewStatePlaceConn2,
    DiagramViewStatePlaceTap,
    DiagramViewStatePlaceNetLabel,
    DiagramViewStatePlaceNetLabelOnSegment,
    DiagramViewStatePlacePort,
    DiagramViewStatePlaceGate,
    DiagramViewStatePlaceBlock1,
    DiagramViewStatePlaceBlock2,
    DiagramViewStatePlaceBlockPin
)

class DiagramViewStateMixin:
    stateIdle                   : DiagramViewStateIdle                    # noqa N815
    stateViewPan1               : DiagramViewStateViewPan1                # noqa N815
    stateViewPan2               : DiagramViewStateViewPan2                # noqa N815
    stateViewZoomArea1          : DiagramViewStateViewZoomArea1           # noqa N815
    stateViewZoomArea2          : DiagramViewStateViewZoomArea2           # noqa N815
    stateEditSelectArea1        : DiagramViewStateEditSelectArea1         # noqa N815
    stateEditSelectArea2        : DiagramViewStateEditSelectArea2         # noqa N815
    stateEditPaste              : DiagramViewStateEditPaste               # noqa N815
    stateEditDuplicate          : DiagramViewStateEditDuplicate           # noqa N815
    stateEditSlide              : DiagramViewStateEditSlide               # noqa N815
    stateEditMove               : DiagramViewStateEditMove                # noqa N815
    stateEditResize             : DiagramViewStateEditResize              # noqa N815
    stateEditMovePins           : DiagramViewStateEditMovePins            # noqa N815
    stateEditAdjustPolySeg      : DiagramViewStateEditAdjustPolySeg       # noqa N815
    stateEditAppearance         : DiagramViewStateEditAppearance          # noqa N815
    stateEditItemProperties     : DiagramViewStateEditItemProperties      # noqa N815
    stateEditDrawingProperties  : DiagramViewStateEditDiagramProperties   # noqa N815
    stateEditQuery              : DiagramViewStateEditQuery               # noqa N815
    stateEditText               : DiagramViewStateEditText                # noqa N815
    stateEditPort               : DiagramViewStateEditPort                # noqa N815
    stateEditBlockPin           : DiagramViewStateEditBlockPin            # noqa N815
    stateEditPropertyText       : DiagramViewStateEditPropertyText        # noqa N815
    statePlaceSymbolPin         : DiagramViewStatePlaceSymbolPin          # noqa N815
    statePlaceRectangle1        : DiagramViewStatePlaceRectangle1         # noqa N815
    statePlaceRectangle2        : DiagramViewStatePlaceRectangle2         # noqa N815
    statePlaceEllipse1          : DiagramViewStatePlaceEllipse1           # noqa N815
    statePlaceEllipse2          : DiagramViewStatePlaceEllipse2           # noqa N815
    statePlacePolyline1         : DiagramViewStatePlacePolyline1          # noqa N815
    statePlacePolyline2         : DiagramViewStatePlacePolyline2          # noqa N815
    statePlaceText              : DiagramViewStatePlaceText               # noqa N815
    statePlaceConn1             : DiagramViewStatePlaceConn1              # noqa N815
    statePlaceConn2             : DiagramViewStatePlaceConn2              # noqa N815
    statePlaceTap               : DiagramViewStatePlaceTap                # noqa N815
    statePlaceNetLabel          : DiagramViewStatePlaceNetLabel           # noqa N815
    statePlaceNetLabelOnSegment : DiagramViewStatePlaceNetLabelOnSegment  # noqa N815
    statePlacePort              : DiagramViewStatePlacePort               # noqa N815
    statePlaceGate              : DiagramViewStatePlaceGate               # noqa N815
    statePlaceBlock1            : DiagramViewStatePlaceBlock1             # noqa N815
    statePlaceBlock2            : DiagramViewStatePlaceBlock2             # noqa N815
    statePlaceBlockPin          : DiagramViewStatePlaceBlockPin           # noqa N815

    def initStates(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.stateIdle                   = DiagramViewStateIdle                   (self)
        self.stateViewPan1               = DiagramViewStateViewPan1               (self)
        self.stateViewPan2               = DiagramViewStateViewPan2               (self)
        self.stateViewZoomArea1          = DiagramViewStateViewZoomArea1          (self)
        self.stateViewZoomArea2          = DiagramViewStateViewZoomArea2          (self)
        self.stateEditSelectArea1        = DiagramViewStateEditSelectArea1        (self)
        self.stateEditSelectArea2        = DiagramViewStateEditSelectArea2        (self)
        self.stateEditPaste              = DiagramViewStateEditPaste              (self)
        self.stateEditDuplicate          = DiagramViewStateEditDuplicate          (self)
        self.stateEditSlide              = DiagramViewStateEditSlide              (self)
        self.stateEditMove               = DiagramViewStateEditMove               (self)
        self.stateEditResize             = DiagramViewStateEditResize             (self)
        self.stateEditMovePins           = DiagramViewStateEditMovePins           (self)
        self.stateEditAdjustPolySeg      = DiagramViewStateEditAdjustPolySeg      (self)
        self.stateEditAppearance         = DiagramViewStateEditAppearance         (self)
        self.stateEditItemProperties     = DiagramViewStateEditItemProperties     (self)
        self.stateEditDiagramProperties  = DiagramViewStateEditDiagramProperties  (self)
        self.stateEditQuery              = DiagramViewStateEditQuery              (self)
        self.stateEditText               = DiagramViewStateEditText               (self)
        self.stateEditPort               = DiagramViewStateEditPort               (self)
        self.stateEditBlockPin           = DiagramViewStateEditBlockPin           (self)
        self.stateEditPropertyText       = DiagramViewStateEditPropertyText       (self)
        self.statePlaceSymbolPin         = DiagramViewStatePlaceSymbolPin         (self)
        self.statePlaceLine1             = DiagramViewStatePlaceLine1             (self)
        self.statePlaceLine2             = DiagramViewStatePlaceLine2             (self)
        self.statePlaceRectangle1        = DiagramViewStatePlaceRectangle1        (self)
        self.statePlaceRectangle2        = DiagramViewStatePlaceRectangle2        (self)
        self.statePlaceEllipse1          = DiagramViewStatePlaceEllipse1          (self)
        self.statePlaceEllipse2          = DiagramViewStatePlaceEllipse2          (self)
        self.statePlacePolyline1         = DiagramViewStatePlacePolyline1         (self)
        self.statePlacePolyline2         = DiagramViewStatePlacePolyline2         (self)
        self.statePlaceText              = DiagramViewStatePlaceText              (self)
        self.statePlacePort              = DiagramViewStatePlacePort              (self)
        self.statePlaceGate              = DiagramViewStatePlaceGate              (self)
        self.statePlaceBlock1            = DiagramViewStatePlaceBlock1            (self)
        self.statePlaceBlock2            = DiagramViewStatePlaceBlock2            (self)
        self.statePlaceBlockPin          = DiagramViewStatePlaceBlockPin          (self)
        self.statePlaceConn1             = DiagramViewStatePlaceConn1             (self)
        self.statePlaceConn2             = DiagramViewStatePlaceConn2             (self)
        self.statePlaceTap               = DiagramViewStatePlaceTap               (self)
        self.statePlaceNetLabel          = DiagramViewStatePlaceNetLabel          (self)
        self.statePlaceNetLabelOnSegment = DiagramViewStatePlaceNetLabelOnSegment (self)
