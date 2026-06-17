from __future__ import annotations

from typing import Self, TypeAlias

from ...drawing.state import DrawingViewStateMixin

from .idle  import DiagramViewStateIdle

from .edit  import DiagramViewStateEditPort, \
                   DiagramViewStateEditBlockPin

from .place import DiagramViewStatePlaceConn1, \
                   DiagramViewStatePlaceConn2, \
                   DiagramViewStatePlaceTap, \
                   DiagramViewStatePlaceNetLabel, \
                   DiagramViewStatePlaceNetLabelOnSegment, \
                   DiagramViewStatePlacePort, \
                   DiagramViewStatePlaceGate, \
                   DiagramViewStatePlaceBlock1, \
                   DiagramViewStatePlaceBlock2, \
                   DiagramViewStatePlaceBlockPin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DiagramView
    from .base import DiagramViewStateBase
    MixinSelf: TypeAlias = Self | DiagramView
else:
    MixinSelf = Self


class DiagramViewStateMixin(DrawingViewStateMixin):
    state                       : DiagramViewStateBase                   # noqa N815
    stateEditPort               : DiagramViewStateEditPort                # noqa N815
    stateEditBlockPin           : DiagramViewStateEditBlockPin            # noqa N815
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

    def initStates(self : MixinSelf) -> None:
        DrawingViewStateMixin.initStates(self)
        self.stateIdle                   = DiagramViewStateIdle                   (self)
        self.stateEditPort               = DiagramViewStateEditPort               (self)
        self.stateEditBlockPin           = DiagramViewStateEditBlockPin           (self)
        self.statePlaceConn1             = DiagramViewStatePlaceConn1             (self)
        self.statePlaceConn2             = DiagramViewStatePlaceConn2             (self)
        self.statePlaceTap               = DiagramViewStatePlaceTap               (self)
        self.statePlaceNetLabel          = DiagramViewStatePlaceNetLabel          (self)
        self.statePlaceNetLabelOnSegment = DiagramViewStatePlaceNetLabelOnSegment (self)
        self.statePlacePort              = DiagramViewStatePlacePort              (self)
        self.statePlaceGate              = DiagramViewStatePlaceGate              (self)
        self.statePlaceBlock1            = DiagramViewStatePlaceBlock1            (self)
        self.statePlaceBlock2            = DiagramViewStatePlaceBlock2            (self)
        self.statePlaceBlockPin          = DiagramViewStatePlaceBlockPin          (self)
