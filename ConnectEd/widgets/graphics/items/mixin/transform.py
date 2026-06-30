from __future__ import annotations

from typing      import Self, TypeVar, Generic
from dataclasses import replace

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QTransform

from .....core.check import checked
from .....core.types import DataKind, HandleId

from ...properties import InherentProperty, PropertiesManager, PropertiesMixin

from ..protocols import OnSceneOrientationChangedProtocol


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..handle import HandleItem
    from .handle  import ItemHandlesMixin


class ItemTransformMixin:
    """Combines previous position, rotation and mirror mixins."""

    # class attributes
    _ORIGIN : HandleId  # undefined = no origin on this item
    _PROPERTIES_POS = {
        "X" : InherentProperty[QGraphicsItem](
            kind   = DataKind.FLOAT,
            worthy = lambda self: self.pos() != QPointF(0, 0),
            getter = lambda self: self.pos().x(),
            setter = lambda self, value: self.setX(value)
        ),
        "Y" : InherentProperty[QGraphicsItem](
            kind   = DataKind.FLOAT,
            worthy = lambda self: self.pos() != QPointF(0, 0),
            getter = lambda self: self.pos().y(),
            setter = lambda self, value: self.setY(value)
        )
    }
    _PROPERTIES_ROTATE = {
        "Rotation" : InherentProperty[QGraphicsItem](
            kind   = DataKind.FLOAT,
            worthy = lambda self: self.rotation() != 0,
            getter = lambda self: self.rotation(),
            setter = lambda self, value: self.setRotation(value)
        )
    }
    _PROPERTIES_MIRROR = {
        "MirrorH" : InherentProperty["ItemTransformMixin"](
            kind   = DataKind.BOOL,
            worthy = lambda self: self.mirrorH(),
            getter = lambda self: self.mirrorH(),
            setter = lambda self, value: self.setMirrorH(value)
        ),
        "MirrorV" : InherentProperty["ItemTransformMixin"](
            kind   = DataKind.BOOL,
            worthy = lambda self: self.mirrorV(),
            getter = lambda self: self.mirrorV(),
            setter = lambda self, value: self.setMirrorV(value)
        )
    }
    _PROPERTIES_NO_ORIGIN = \
        _PROPERTIES_POS | _PROPERTIES_ROTATE | _PROPERTIES_MIRROR
    _PROPERTY_ORIGIN = InherentProperty["ItemTransformMixin"](
        kind   = None,
        worthy = lambda self: self.hasOrigin(),
        getter = lambda self: self.origin(),
        setter = lambda self, value: self.setOrigin(value)
    )
    _PROPERTIES_RECT_ORIGIN = {
        "Origin" : replace(_PROPERTY_ORIGIN, kind=DataKind.RECT_HANDLE)
    }
    _PROPERTIES_LINE_ORIGIN = {
        "Origin" : replace(_PROPERTY_ORIGIN, kind=DataKind.LINE_HANDLE)
    }
    _PROPERTIES_BLOCK_PIN_ORIGIN = {
        "Origin" : replace(_PROPERTY_ORIGIN, kind=DataKind.BLOCK_PIN_HANDLE)
    }
    _PROPERTIES_SYMBOL_PIN_ORIGIN = {
        "Origin" : replace(_PROPERTY_ORIGIN, kind=DataKind.SYMBOL_PIN_HANDLE)
    }

    # instance attributes
    _origin    : HandleId
    _mirror_h  : bool
    _mirror_v  : bool

    # external instance attributes
    properties : PropertiesManager  # provided by PropertiesMixin

    @checked
    def initTransform(self : Self) -> None:
        self._mirror_h = False
        self._mirror_v = False
        if hasattr(self, "_ORIGIN"):
            self.setOrigin(self._ORIGIN)

    @checked
    def onPositionChanged(self : Self, _pos : QPointF | None = None) -> None:
        if isinstance(self, PropertiesMixin):
            self.properties.signalChanges(["X", "Y"])
        return

    @checked
    def onRotationChanged(self : Self, _angle : float) -> None:
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        # process self scene rotation changes
        if isinstance(self, OnSceneOrientationChangedProtocol):
            self.onSceneOrientationChanged()
        # propagate to children
        for child in self.childItems():
            if isinstance(child, OnSceneOrientationChangedProtocol):
                child.onSceneOrientationChanged()
        # broadcast change
        self.properties.signalChanges("Rotation")

    @checked
    def onMirrorChanged(self : Self) -> None:
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        # rebuild local transform to include mirror scale
        self.updateTransform()
        # process self scene mirror change
        if isinstance(self, OnSceneOrientationChangedProtocol):
            self.onSceneOrientationChanged()
        # propagate to children
        for child in self.childItems():
            if isinstance(child, OnSceneOrientationChangedProtocol):
                child.onSceneOrientationChanged()
        # broadcast changes
        self.properties.signalChanges(["MirrorH", "MirrorV"])

    @checked
    def moveBy(
        self : Self,
        dx   : float,
        dy   : float
    ) -> None:
        """Move item by scene offset, accounting for parent scene rotation."""
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        a = self.parentSceneRotation()
        match a:
            case 0   : QGraphicsItem.moveBy(self,  dx,  dy)
            case 90  : QGraphicsItem.moveBy(self,  dy, -dx)
            case 180 : QGraphicsItem.moveBy(self, -dx, -dy)
            case 270 : QGraphicsItem.moveBy(self, -dy,  dx)
            case _   :
                transform = QTransform().rotate(-a)
                rotated_offset = transform.map(QPointF(dx, dy))
                QGraphicsItem.moveBy(self, rotated_offset.x(), rotated_offset.y())

    @checked
    def rotateCW(self : Self) -> None:
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        self.setRotation((self.rotation() + 90.0) % 360.0)

    @checked
    def rotateCCW(self : Self) -> None:
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        self.setRotation((self.rotation() - 90.0) % 360.0)

    @checked
    def parentSceneRotation(self : Self) -> float:
        """Returns total effective rotation angle (degrees) of the parent."""
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        angle = 0.0
        item = self.parentItem()
        while item is not None:
            angle += item.rotation()
            item = item.parentItem()
        return angle % 360.0

    @checked
    def sceneRotation(self : Self) -> float:
        """Returns total effective rotation angle (degrees) of the item."""
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        return (self.parentSceneRotation() + self.rotation()) % 360.0

    @checked
    def mirrorH(self : Self) -> bool:
        return getattr(self, "_mirror_h", False)

    @checked
    def setMirrorH(self : Self, mirror_h : bool) -> None:
        self._mirror_h = mirror_h
        self.onMirrorChanged()

    @checked
    def parentSceneMirrorH(self : Self) -> bool:
        """Returns effective horizontal mirroring of the parent."""
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        mirror_h = False
        item = self.parentItem()
        while item is not None:
            if isinstance(item, ItemTransformMixin):
                mirror_h ^= item.mirrorH()
            item = item.parentItem()
        return mirror_h

    @checked
    def sceneMirrorH(self : Self) -> bool:
        """Returns effective horizontal mirroring of this item."""
        return self.parentSceneMirrorH() ^ self.mirrorH()

    @checked
    def mirrorV(self : Self) -> bool:
        return getattr(self, "_mirror_v", False)

    @checked
    def setMirrorV(self : Self, mirror_v : bool) -> None:
        self._mirror_v = mirror_v
        self.onMirrorChanged()

    @checked
    def parentSceneMirrorV(self : Self) -> bool:
        """Returns effective vertical mirroring of the parent."""
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        mirror_v = False
        item = self.parentItem()
        while item is not None:
            if isinstance(item, ItemTransformMixin):
                mirror_v ^= item.mirrorV()
            item = item.parentItem()
        return mirror_v

    @checked
    def sceneMirrorV(self : Self) -> bool:
        """Returns effective vertical mirroring of this item."""
        return self.parentSceneMirrorV() ^ self.mirrorV()

    @checked
    def hasOrigin(self : Self) -> bool:
        return hasattr(self, "_origin")

    @checked
    def origin(self : Self) -> HandleId:
        return self._origin

    @checked
    def setOrigin(self : Self, id : HandleId) -> None:
        """Set origin handle without shifting the item in scene."""
        from .handle import ItemHandlesMixin
        if not isinstance(self, QGraphicsItem) \
        or not isinstance(self, ItemHandlesMixin):
            raise TypeError("Bad host")
        if not isinstance(id, self.handleIdType()):
            raise TypeError("Bad handle ID type")
        old_id = None
        old_spos = None
        if self.hasOrigin():
            old_id = self._origin
            if self.scene() is not None and old_id != id:
                old_spos = self.getHandle(old_id).scenePos()
        self._origin = id
        self.updateTransform()
        for handle in self.handles().values():
            handle.grip().updatePath()
        self.onOriginChanged(old_id, id)
        if old_id is not None and old_spos is not None:
            actual = self.getHandle(old_id).scenePos()
            parent = self.parentItem()
            if parent is None:
                delta = old_spos - actual
                QGraphicsItem.moveBy(self, delta.x(), delta.y())
            else:
                parent_delta = \
                    parent.mapFromScene(old_spos) - parent.mapFromScene(actual)
                QGraphicsItem.moveBy(self, parent_delta.x(), parent_delta.y())
        self.properties.signalChanges("Origin")

    def onOriginChanged(
        self : Self,
        _old : HandleId | None,
        _new : HandleId,
    ) -> None:
        """Hook after transform rebuild; override to refresh dependent layout."""
        return

    @checked
    def getOriginHandle(self : Self | ItemHandlesMixin) -> HandleItem:
        from .handle import ItemHandlesMixin
        if not isinstance(self, ItemTransformMixin) \
        or not isinstance(self, ItemHandlesMixin):
            raise TypeError("Bad host")
        return self.getHandle(self._origin)

    @checked
    def updateTransform(self : Self | QGraphicsItem | ItemHandlesMixin) -> None:
        """
        Rebuild the item's local transform so that rotation and mirroring
        pivot around the same point:

        - If the item declares an `_ORIGIN` handle, the pivot is that
          handle's local position. The `setTransform` also shifts local
          coords so the handle lands at the item's Qt `pos()`.
        - Otherwise, the pivot is local (0, 0), matching Qt's default
          `transformOriginPoint`. The shift collapses to a no-op, so
          `setTransform` just carries the mirror scale.
        """
        from .handle import ItemHandlesMixin
        if not isinstance(self, QGraphicsItem)     \
        or not isinstance(self, ItemTransformMixin) \
        or not isinstance(self, ItemHandlesMixin):
            raise TypeError("Bad host")
        # pick pivot: origin handle position (if any), else local (0, 0)
        if getattr(self, "_ORIGIN", None) is not None \
        and getattr(self, "_origin", None) is not None \
        and hasattr(self, "_handles"):
            pivot = self._handles[self._origin].pos()
        elif hasattr(self, "_ORIGIN") and not hasattr(self, "_origin"):
            # still initialising - setOrigin() will call us again
            return
        else:
            pivot = QPointF(0, 0)
        # rotation / mirror pivot
        self.setTransformOriginPoint(pivot)
        # mirror scales, reflected around pivot in local coords
        sx = -1.0 if self.mirrorH() else 1.0
        sy = -1.0 if self.mirrorV() else 1.0
        # T(p) = (sx*(p - pivot).x, sy*(p - pivot).y); translate is a no-op
        # when pivot == (0, 0) - i.e. for origin-less items.
        transform = QTransform()
        transform.scale(sx, sy)
        transform.translate(-pivot.x(), -pivot.y())
        self.setTransform(transform)
