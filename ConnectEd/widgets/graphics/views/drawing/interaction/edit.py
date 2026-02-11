from typing import Self
from math   import asin, degrees, copysign

from PyQt6.QtCore    import QPointF, QLineF
from PyQt6.QtWidgets import QGraphicsLineItem

from ......core.types import EdgeLoc
from ......core.xml   import paste

from ....items import clone

from ....items.block     import BlockItem
from ....items.block_pin import BlockPinItem
from ....items.polyline  import PolylineItem, PolySegItem

from . import MoveItemsMixin,      \
              AddRemoveItemsMixin, \
              ItemsInteraction,    \
              Interaction,         \
              ItemType

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...drawing import DrawingView


class EditPasteInteraction(
    MoveItemsMixin,       # update, _moveBy, _moveSave, _moveRestore
    AddRemoveItemsMixin,  # _addToScene, _removeFromScene
    ItemsInteraction      # _view, _scene, _items, valid
):
    def __init__(
        self : Self,
        view : "DrawingView",
        pos  : QPointF
    ) -> None:
        items, copy_pos = paste()
        if items:
            super().__init__(view, items)
            self._cpos = self._ipos = copy_pos or pos
            self._items = items
            self._moveSave()
            self._addToScene(select=True)
            self.update(pos)  # Move to initial position
        else:
            self._items = None

    def commit(self : Self, pos : QPointF) -> bool:
        self._moveRestore()  # restore initial positions
        self.update(pos)     # apply final offset
        # add pasted items to scene
        self._scene.addItems(self._items, undoable=True)
        return True

    def cancel(self : Self) -> None:
        self._removeFromScene()   # remove preview items


class EditDuplicateInteraction(EditPasteInteraction):
    """Very similar to paste, but items come from cloning."""

    def __init__(
        self  : Self,
        view  : "DrawingView",
        items : list[ItemType],  # items to duplicate
        pos   : QPointF          # duplication origin
    ) -> None:
        clone_items = clone(items)
        if clone_items:
            ItemsInteraction.__init__(self, view, clone_items)
            self._cpos = self._ipos = pos
            self._moveSave()
            self._addToScene(select=True)
        else:
            self._items = None


class EditMoveInteraction(
    MoveItemsMixin,    # update, _moveBy, _moveSave, _moveRestore
    ItemsInteraction,  # _view, _scene, _items, valid
):
    # instance attributes
    _slide  : bool  # true => retain connections, false => break connections

    def __init__(
        self  : Self,
        view  : "DrawingView",
        items : list[ItemType],
        pos   : QPointF,
        slide : bool = False
    ) -> None:
        items = items if isinstance(items, list) else [items]
        # Filter: keep only items that have no ancestor in the items list
        orphan_items = []
        item_set = set(items)
        for item in items:
            parent = item.parentItem()
            has_ancestor = False
            while parent is not None:
                if parent in item_set:
                    has_ancestor = True
                    break
                parent = parent.parentItem()
            if not has_ancestor:
                orphan_items.append(item)
        # Start interaction
        super().__init__(view, orphan_items)
        self._cpos  = self._ipos = pos
        self._slide = slide
        self._moveSave()  # record initial positions

    def commit(self : Self, pos : QPointF) -> bool:
        self._moveRestore()  # restore initial positions
        # apply final offset
        self._scene.editMove(self._items, pos - self._ipos, self._slide, undoable=True)
        return True

    def cancel(self : Self) -> None:
        self._moveRestore()  # restore initial positions


class EditMoveBlockPinsInteraction(Interaction):
    # instance attributes
    _parent : BlockItem
    _pins   : list[BlockPinItem]           # first item is primary pin
    _sloc   : dict[ItemType, EdgeLoc]  # stored locations of all pins

    def __init__(
        self   : Self,
        view   : "DrawingView",
        parent : BlockItem,
        pins   : list[BlockPinItem]
    ) -> None:
        super().__init__(view)
        self._parent = parent
        self._pins = pins
        self._storeLoc()

    def valid(self : Self) -> bool:
        return \
            self._parent is not None and \
            hasattr(self, "_pins") and \
            len(self._pins) > 0

    def update(self : Self, pos : QPointF, snap : QPointF | None = None) -> None:
        pos_snap = self._scene._snap(pos, snap) if snap else pos
        primary = self._pins[0]
        loc_old = primary.loc()
        loc_new = self._parent.pos2loc(pos)
        loc_new_snap = self._parent.pos2loc(pos_snap)
        offset = self._parent.locDelta(loc_old, loc_new_snap)
        snap_pressure = self._parent.locDelta(loc_new, loc_new_snap)
        corner = +1 if snap_pressure > 0 else -1 if snap_pressure < 0 else 0
        self._pins[0].setLoc(loc_new_snap)
        for pin in self._pins[1:]:
            pin.setLoc(self._parent.locOffset(pin.loc(), offset, corner))

    def commit(self : Self, pos : QPointF, snap : QPointF | None = None) -> bool:
        self._restoreLoc()
        self.update(pos, snap)
        if all(p.loc() == self._sloc[p] for p in self._pins):
            return True # no change so skip command push
        self._scene.editMoveBlockPins(
            self._parent,
            self._pins,
            {p: p.loc() for p in self._pins},
            self._sloc,
            undoable=True
        )
        return True

    def cancel(self : Self) -> None:
        self._restoreLoc()

    def _storeLoc(self : Self) -> None:
        self._sloc = {p: p.loc() for p in self._pins}

    def _restoreLoc(self : Self) -> None:
        for p in self._pins:
            p.setLoc(self._sloc[p])


class EditAdjustPolySegInteraction(Interaction):
    # instance attributes
    _polyline : PolylineItem           # parent polyline
    _seg      : PolySegItem            # target segment
    _before   : float | None       # initial sweep angle
    _guide1   : QGraphicsLineItem  # inline guide
    _guide2   : QGraphicsLineItem  # perpendicular guide

    def __init__(
        self     : Self,
        view     : "DrawingView",
        polyline : PolylineItem,
        seg      : PolySegItem,
        pos      : QPointF
    ) -> None:
        super().__init__(view)
        self._polyline = polyline
        self._seg = seg
        self._before = seg.sweep()
        self._showGuides()
        self.update(pos)

    def valid(self : Self) -> bool:
        return self._polyline is not None and self._seg is not None

    def update(self : Self, pos : QPointF) -> None:
        chord = self._guide1.line()  # chord line (p1 → p2)
        p1 = chord.p1()
        chord_vec = chord.p2() - p1  # vector along the chord
        chord_len = chord.length()
        if chord_len == 0:
            return
        pos_vec = pos - p1  # p1 -> pos
        # 2-D cross product gives a signed area → side test
        cross = chord_vec.x() * pos_vec.y() - chord_vec.y() * pos_vec.x()
        signed_sagitta = cross / chord_len  # >0 right, <0 left
        sagitta = abs(signed_sagitta)
        if sagitta < 1e-6:  # mouse on the chord
            return
        # radius of the circle that passes through the two endpoints
        radius = (sagitta ** 2 + (chord_len / 2) ** 2) / (2 * sagitta)
        # central angle in degrees (always the *smaller* angle, 0°-180°)
        minor_theta = 2 * degrees(asin((chord_len / 2) / radius))
        # Switch to major arc if on the far side
        theta = 360 - minor_theta if sagitta > radius else minor_theta
        # Apply the side sign – now sweep can be ±0° to ±360°
        sweep = copysign(theta, signed_sagitta)
        if abs(sweep) < 1.0:
            return
        # Update guides
        center = chord.center()
        perp_vec = QPointF(chord.dy() / 2, -chord.dx() / 2)  # CCW
        perp_line = QLineF(center, center + perp_vec)
        pos_line = QLineF(pos, pos + chord_vec)
        _, corner = perp_line.intersects(pos_line)
        self._guide2.setLine(QLineF(center, corner))
        self._guide3.setLine(QLineF(corner, pos))
        # done
        self._seg.setSweep(sweep)
        self._polyline.updatePath()

    def commit(self : Self, pos : QPointF) -> bool:
        self.update(pos)
        new_sweep = self._seg.sweep()
        # Restore original value before creating undo command
        self._seg.setSweep(self._before)
        # Now create command with before/after values
        self._scene.editPolySeg(self._seg, new_sweep, undoable=True)
        self._hideGuides()
        return True

    def complete(self : Self, pos : QPointF) -> None:
        self.commit(pos)

    def cancel(self : Self) -> None:
        self._seg.setSweep(self._before)
        self._polyline.updatePath()
        self._hideGuides()

    def _showGuides(self : Self) -> None:
        # inline fixed
        in_line = QLineF(self._seg.v1().scenePos(), self._seg.v2().scenePos())
        self._guide1 = self._scene.guide(0)
        self._guide1.setLine(in_line)
        self._guide1.setVisible(True)
        center = in_line.center()
        zero_length_line = QLineF(center, center)
        # 90 degree slider
        self._guide2 = self._scene.guide(1)
        self._guide2.setLine(zero_length_line)
        self._guide2.setVisible(True)
        # 0 degree slider
        self._guide3 = self._scene.guide(2)
        self._guide3.setLine(zero_length_line)
        self._guide3.setVisible(True)

    def _hideGuides(self : Self) -> None:
        self._guide1.setVisible(False)
        self._guide2.setVisible(False)
        self._guide3.setVisible(False)
