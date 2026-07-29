from __future__ import annotations

from typing import Self

from .idle  import DiagramViewStateIdle

from ..host import asDiagramView

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
    DiagramViewStateEditMoveGrip,
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
    stateEditMoveGrip           : DiagramViewStateEditMoveGrip            # noqa N815
    stateEditMovePins           : DiagramViewStateEditMovePins            # noqa N815
    stateEditAdjustPolySeg      : DiagramViewStateEditAdjustPolySeg       # noqa N815
    stateEditAppearance         : DiagramViewStateEditAppearance          # noqa N815
    stateEditItemProperties     : DiagramViewStateEditItemProperties      # noqa N815
    stateEditDiagramProperties  : DiagramViewStateEditDiagramProperties   # noqa N815
    stateEditQuery              : DiagramViewStateEditQuery               # noqa N815
    stateEditText               : DiagramViewStateEditText                # noqa N815
    stateEditPort               : DiagramViewStateEditPort                # noqa N815
    stateEditBlockPin           : DiagramViewStateEditBlockPin            # noqa N815
    stateEditPropertyText       : DiagramViewStateEditPropertyText        # noqa N815
    statePlaceSymbolPin         : DiagramViewStatePlaceSymbolPin          # noqa N815
    statePlaceLine1             : DiagramViewStatePlaceLine1              # noqa N815
    statePlaceLine2             : DiagramViewStatePlaceLine2              # noqa N815
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
        host = asDiagramView(self)
        host.stateIdle                   = DiagramViewStateIdle                   (host)
        host.stateViewPan1               = DiagramViewStateViewPan1               (host)
        host.stateViewPan2               = DiagramViewStateViewPan2               (host)
        host.stateViewZoomArea1          = DiagramViewStateViewZoomArea1          (host)
        host.stateViewZoomArea2          = DiagramViewStateViewZoomArea2          (host)
        host.stateEditSelectArea1        = DiagramViewStateEditSelectArea1        (host)
        host.stateEditSelectArea2        = DiagramViewStateEditSelectArea2        (host)
        host.stateEditPaste              = DiagramViewStateEditPaste              (host)
        host.stateEditDuplicate          = DiagramViewStateEditDuplicate          (host)
        host.stateEditSlide              = DiagramViewStateEditSlide              (host)
        host.stateEditMove               = DiagramViewStateEditMove               (host)
        host.stateEditMoveGrip           = DiagramViewStateEditMoveGrip           (host)
        host.stateEditMovePins           = DiagramViewStateEditMovePins           (host)
        host.stateEditAdjustPolySeg      = DiagramViewStateEditAdjustPolySeg      (host)
        host.stateEditAppearance         = DiagramViewStateEditAppearance         (host)
        host.stateEditItemProperties     = DiagramViewStateEditItemProperties     (host)
        host.stateEditDiagramProperties  = DiagramViewStateEditDiagramProperties  (host)
        host.stateEditQuery              = DiagramViewStateEditQuery              (host)
        host.stateEditText               = DiagramViewStateEditText               (host)
        host.stateEditPort               = DiagramViewStateEditPort               (host)
        host.stateEditBlockPin           = DiagramViewStateEditBlockPin           (host)
        host.stateEditPropertyText       = DiagramViewStateEditPropertyText       (host)
        host.statePlaceSymbolPin         = DiagramViewStatePlaceSymbolPin         (host)
        host.statePlaceLine1             = DiagramViewStatePlaceLine1             (host)
        host.statePlaceLine2             = DiagramViewStatePlaceLine2             (host)
        host.statePlaceRectangle1        = DiagramViewStatePlaceRectangle1        (host)
        host.statePlaceRectangle2        = DiagramViewStatePlaceRectangle2        (host)
        host.statePlaceEllipse1          = DiagramViewStatePlaceEllipse1          (host)
        host.statePlaceEllipse2          = DiagramViewStatePlaceEllipse2          (host)
        host.statePlacePolyline1         = DiagramViewStatePlacePolyline1         (host)
        host.statePlacePolyline2         = DiagramViewStatePlacePolyline2         (host)
        host.statePlaceText              = DiagramViewStatePlaceText              (host)
        host.statePlacePort              = DiagramViewStatePlacePort              (host)
        host.statePlaceGate              = DiagramViewStatePlaceGate              (host)
        host.statePlaceBlock1            = DiagramViewStatePlaceBlock1            (host)
        host.statePlaceBlock2            = DiagramViewStatePlaceBlock2            (host)
        host.statePlaceBlockPin          = DiagramViewStatePlaceBlockPin          (host)
        host.statePlaceConn1             = DiagramViewStatePlaceConn1             (host)
        host.statePlaceConn2             = DiagramViewStatePlaceConn2             (host)
        host.statePlaceTap               = DiagramViewStatePlaceTap               (host)
        host.statePlaceNetLabel          = DiagramViewStatePlaceNetLabel          (host)
        host.statePlaceNetLabelOnSegment = DiagramViewStatePlaceNetLabelOnSegment (host)
