from typing import Self

from PyQt6.QtWidgets import QGraphicsItem

from .....core.types import DataKind

from ...properties import InherentProperty, PropertiesMixin


class ItemMirrorMixin:
    # class attributes
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

    # instance attributes
    _mirror_h : bool
    _mirror_v : bool

    def initMirror(self : Self) -> None:
        self._mirror_h = False
        self._mirror_v = False

    def onMirrorChange(self : Self | PropertiesMixin) -> None:
        # rebuild local transform to include mirror scale
        if hasattr(self, "updateOrigin"):
            self.updateOrigin()
        # process self scene mirror change
        if hasattr(self, "onSceneMirrorChange"):
            self.onSceneMirrorChange()
        # propagate to children
        for child in self.childItems():
            if hasattr(child, "onSceneMirrorChange"):
                child.onSceneMirrorChange()
        # broadcast changes
        self.signalPropertyChanges(["MirrorH", "MirrorV"])

    def mirrorH(self : Self) -> bool:
        return self._mirror_h

    def setMirrorH(self : Self, mirror_h : bool) -> None:
        self._mirror_h = mirror_h
        self.onMirrorChange()

    def parentSceneMirrorH(self : Self | QGraphicsItem) -> bool:
        """Returns effective horizontal mirroring of the parent."""
        mirror_h = False
        item : "Self | QGraphicsItem | None" = self.parentItem()
        while item is not None:
            if hasattr(item, "mirrorH"):
                mirror_h = mirror_h ^ item.mirrorH()
            item = item.parentItem()
        return mirror_h

    def sceneMirrorH(self : Self | QGraphicsItem) -> bool:
        """Returns effective horizontal mirroring of this item."""
        return self.parentSceneMirrorH() ^ self.mirrorH()

    def mirrorV(self : Self) -> bool:
        return self._mirror_v

    def setMirrorV(self : Self, mirror_v : bool) -> None:
        self._mirror_v = mirror_v
        self.onMirrorChange()

    def parentSceneMirrorV(self : Self | QGraphicsItem) -> bool:
        """Returns effective vertical mirroring of the parent."""
        mirror_v = False
        item : "Self | QGraphicsItem | None" = self.parentItem()
        while item is not None:
            if hasattr(item, "mirrorV"):
                mirror_v = mirror_v ^ item.mirrorV()
            item = item.parentItem()
        return mirror_v

    def sceneMirrorV(self : Self | QGraphicsItem) -> bool:
        """Returns effective vertical mirroring of this item."""
        return self.parentSceneMirrorV() ^ self.mirrorV()
