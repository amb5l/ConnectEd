from typing      import Self, overload
from dataclasses import replace

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QTransform

from .....core.check import checked
from .....core.types import DataKind, HandleId

from ...properties import InherentProperty, PropertiesMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..handle import HandleItem
    from .handle  import ItemHandlesMixin


class ItemTransformMixin:
    """Combines previous position, rotation and mirror mixins."""

    # class attributes
    _ORIGIN : HandleId | None
    _PROPERTIES_POS = {
        "X" : InherentProperty(
            kind   = DataKind.FLOAT,
            worthy = lambda self: self.pos() != QPointF(0, 0),
            getter = lambda self: self.pos().x(),
            setter = lambda self, value: self.setX(value)
        ),
        "Y" : InherentProperty(
            kind   = DataKind.FLOAT,
            worthy = lambda self: self.pos() != QPointF(0, 0),
            getter = lambda self: self.pos().y(),
            setter = lambda self, value: self.setY(value)
        )
    }
    _PROPERTIES_ROTATE = {
        "Rotation" : InherentProperty(
            kind   = DataKind.FLOAT,
            worthy = lambda self: self.rotation() != 0,
            getter = lambda self: self.rotation(),
            setter = lambda self, value: self.setRotation(value)
        )
    }
    _PROPERTIES_MIRROR = {
        "MirrorH" : InherentProperty(
            kind   = DataKind.BOOL,
            worthy = lambda self: self.mirrorH(),
            getter = lambda self: self.mirrorH(),
            setter = lambda self, value: self.setMirrorH(value)
        ),
        "MirrorV" : InherentProperty(
            kind   = DataKind.BOOL,
            worthy = lambda self: self.mirrorV(),
            getter = lambda self: self.mirrorV(),
            setter = lambda self, value: self.setMirrorV(value)
        )
    }
    _PROPERTIES_NO_ORIGIN = \
        _PROPERTIES_POS | _PROPERTIES_ROTATE | _PROPERTIES_MIRROR
    _PROPERTIES_ORIGIN = InherentProperty(
        kind   = None,
        worthy = lambda self: self.origin() is not None,
        getter = lambda self: self.origin(),
        setter = lambda self, value: self.setOrigin(value)
    )
    _PROPERTIES_RECT_ORIGIN = {
        "Origin" : replace(_PROPERTIES_ORIGIN, kind=DataKind.RECT_HANDLE)
    }
    _PROPERTIES_LINE_ORIGIN = {
        "Origin" : replace(_PROPERTIES_ORIGIN, kind=DataKind.LINE_HANDLE)
    }
    _PROPERTIES_BLOCK_PIN_ORIGIN = {
        "Origin" : replace(_PROPERTIES_ORIGIN, kind=DataKind.BLOCK_PIN_HANDLE)
    }
    _PROPERTIES_SYMBOL_PIN_ORIGIN = {
        "Origin" : replace(_PROPERTIES_ORIGIN, kind=DataKind.SYMBOL_PIN_HANDLE)
    }

    # instance attributes
    _mirror_h : bool
    _mirror_v : bool

    @checked
    def initTransform(self : Self | QGraphicsItem) -> None:
        self._mirror_h = False
        self._mirror_v = False
        if hasattr(self, "_ORIGIN"):
            from .handle import ItemHandlesMixin
            if not isinstance(self, ItemHandlesMixin):
                raise TypeError("ItemTransformMixin requires ItemHandlesMixin")
            self.setOrigin(self._ORIGIN)

    @checked
    def onPositionChanged(
        self : Self | QGraphicsItem | PropertiesMixin,
        _pos : QPointF | None = None
    ) -> None:
        self.properties.signalChanges(["X", "Y"])

    @checked
    def onRotationChanged(self : Self | PropertiesMixin, _angle : float) -> None:
        # process self scene rotation changes
        if hasattr(self, "onSceneRotationChanged"):
            self.onSceneRotationChanged()
        # propagate to children
        for child in self.childItems():
            if hasattr(child, "onSceneRotationChanged"):
                child.onSceneRotationChanged()
        # broadcast change
        self.properties.signalChanges("Rotation")

    @checked
    def onMirrorChanged(self : Self | PropertiesMixin) -> None:
        # rebuild local transform to include mirror scale
        self.updateTransform()
        # process self scene mirror change
        if hasattr(self, "onSceneMirrorChanged"):
            self.onSceneMirrorChanged()
        # propagate to children
        for child in self.childItems():
            if hasattr(child, "onSceneMirrorChanged"):
                child.onSceneMirrorChanged()
        # broadcast changes
        self.properties.signalChanges(["MirrorH", "MirrorV"])

    @overload
    def moveBy(self : Self | QGraphicsItem, dx : float, dy : float) -> None:
        ...

    @overload
    def moveBy(self : Self | QGraphicsItem, d : QPointF) -> None:
        ...

    @checked
    def moveBy(
        self : Self | QGraphicsItem,
        dx_d : float | QPointF,
        dy   : float | None = None
    ) -> None:
        """Move item by scene offset, accounting for parent scene rotation."""
        dx = dx_d.x() if isinstance(dx_d, QPointF) else dx_d
        dy = dx_d.y() if isinstance(dx_d, QPointF) else dy
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
    def rotateCW(self : Self | QGraphicsItem) -> None:
        self.setRotation((self.rotation() + 90.0) % 360.0)

    @checked
    def rotateCCW(self : Self | QGraphicsItem) -> None:
        self.setRotation((self.rotation() - 90.0) % 360.0)

    @checked
    def parentSceneRotation(self : Self | QGraphicsItem) -> float:
        """Returns total effective rotation angle (degrees) of the parent."""
        angle = 0.0
        item = self.parentItem()
        while item is not None:
            angle += item.rotation()
            item = item.parentItem()
        return angle % 360.0

    @checked
    def sceneRotation(self : Self | QGraphicsItem) -> float:
        """Returns total effective rotation angle (degrees) of the item."""
        return (self.parentSceneRotation() + self.rotation()) % 360.0

    @checked
    def mirrorH(self : Self) -> bool:
        return getattr(self, "_mirror_h", False)

    @checked
    def setMirrorH(self : Self, mirror_h : bool) -> None:
        self._mirror_h = mirror_h
        self.onMirrorChanged()

    @checked
    def parentSceneMirrorH(self : Self | QGraphicsItem) -> bool:
        """Returns effective horizontal mirroring of the parent."""
        mirror_h = False
        item = self.parentItem()
        while item is not None:
            if isinstance(item, ItemTransformMixin):
                mirror_h ^= item.mirrorH()
            item = item.parentItem()
        return mirror_h

    @checked
    def sceneMirrorH(self : Self | QGraphicsItem) -> bool:
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
    def parentSceneMirrorV(self : Self | QGraphicsItem) -> bool:
        """Returns effective vertical mirroring of the parent."""
        mirror_v = False
        item : "Self | QGraphicsItem | None" = self.parentItem()
        while item is not None:
            if isinstance(item, ItemTransformMixin):
                mirror_v ^= item.mirrorV()
            item = item.parentItem()
        return mirror_v

    @checked
    def sceneMirrorV(self : Self | QGraphicsItem) -> bool:
        """Returns effective vertical mirroring of this item."""
        return self.parentSceneMirrorV() ^ self.mirrorV()

    @checked
    def origin(self : Self) -> HandleId | None:
        return getattr(self, "_origin", None)

    @checked
    def setOrigin(
        self : "Self | QGraphicsItem | ItemHandlesMixin | PropertiesMixin",
        id   : HandleId
    ) -> None:
        """Set origin handle without shifting the item in scene."""
        old_id   = self.origin()
        old_spos : QPointF | None = None
        if self.scene() is not None and old_id is not None and old_id != id \
        and hasattr(self, "_handles"):
            old_spos = self.getHandle(old_id).scenePos()
        self._origin = id
        self.updateTransform()
        if hasattr(self, "_handles"):
            for handle in self._handles.values():
                handle.grip().updatePath()
        self.onOriginChanged(old_id, id)
        if old_spos is not None and old_id is not None:
            actual = self.getHandle(old_id).scenePos()
            parent = self.parentItem()
            if parent is None:
                delta = old_spos - actual
                QGraphicsItem.moveBy(self, delta.x(), delta.y())
            else:
                pd = parent.mapFromScene(old_spos) - parent.mapFromScene(actual)
                QGraphicsItem.moveBy(self, pd.x(), pd.y())
        self.properties.signalChanges("Origin")

    def onOriginChanged(
        self : Self,
        _old : HandleId | None,
        _new : HandleId,
    ) -> None:
        """Hook after transform rebuild; override to refresh dependent layout."""
        return

    @checked
    def getOriginHandle(self : "Self | ItemHandlesMixin") -> "HandleItem":
        return self.getHandle(self._origin)

    @checked
    def updateTransform(self : "Self | QGraphicsItem | ItemHandlesMixin") -> None:
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
