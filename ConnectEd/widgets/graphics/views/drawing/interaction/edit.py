from typing import Self
from math   import asin, degrees, copysign

from PyQt6.QtCore    import QPointF, QLineF
from PyQt6.QtWidgets import QGraphicsLineItem

from ......core.check import checked
from ......core.xml   import paste

from ....items import clone

from ....items.polyline  import PolylineItem, PolySegItem

from . import MoveItemsMixin,      \
              PreviewStateMixin,   \
              AddRemoveItemsMixin, \
              DrawingItemsInteraction,    \
              DrawingInteraction,         \
              ItemType

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...drawing import DrawingView


class EditPasteInteraction(
    MoveItemsMixin,       # update, _moveBy, _previewSave, _previewRestore
    AddRemoveItemsMixin,  # _addToScene, _removeFromScene
    DrawingItemsInteraction      # _view, _scene, _items, valid
):
    @checked
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
            self._previewSave()
            self._addToScene(select=True)
            self.update(pos)  # Move to initial position
        else:
            self._items = None

    def _commit(self : Self, pos : QPointF) -> bool:
        self._previewRestore()  # restore initial positions
        self.update(pos)     # apply final offset
        # add pasted items to scene
        self._scene.addItems(self._items, undoable=True)
        return True

    def _cancel(self : Self) -> None:
        self._removeFromScene()   # remove preview items


class EditDuplicateInteraction(EditPasteInteraction):
    """Very similar to paste, but items come from cloning."""

    @checked
    def __init__(
        self  : Self,
        view  : "DrawingView",
        items : list[ItemType],  # items to duplicate
        pos   : QPointF          # duplication origin
    ) -> None:
        clone_items = clone(items)
        if clone_items:
            DrawingItemsInteraction.__init__(self, view, clone_items)
            self._cpos = self._ipos = pos
            self._previewSave()
            self._addToScene(select=True)
        else:
            self._items = None


class EditMoveInteraction(
    MoveItemsMixin,    # update, _moveBy, _previewSave, _previewRestore
    DrawingItemsInteraction,  # _view, _scene, _items, valid
):
    # instance attributes
    _slide  : bool  # true => retain connections, false => break connections

    @checked
    def __init__(
        self  : Self,
        view  : "DrawingView",
        items : ItemType | list[ItemType],
        pos   : QPointF,
        slide : bool = False
    ) -> None:
        if not isinstance(items, list):
            items = [items]
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
        self._previewSave()  # record initial positions

    def _commit(self : Self, pos : QPointF) -> bool:
        self._previewRestore()  # restore initial positions
        # apply final offset
        self._scene.editMove(self._items, pos - self._ipos, self._slide, undoable=True)
        return True

    def _cancel(self : Self) -> None:
        self._previewRestore()  # restore initial positions


class EditAdjustPolySegInteraction(PreviewStateMixin, DrawingInteraction):
    # instance attributes
    _polyline : PolylineItem       # parent polyline
    _seg      : PolySegItem        # target segment
    _guide1   : QGraphicsLineItem  # inline guide
    _guide2   : QGraphicsLineItem  # perpendicular guide
    _guide3   : QGraphicsLineItem  # chord-direction guide

    @checked
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
        self._previewSave()
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

    def _commit(self : Self, pos : QPointF) -> bool:
        self.update(pos)
        new_sweep = self._seg.sweep()
        # Restore original value before creating undo command
        self._previewRestore()
        # Now create command with before/after values
        self._scene.editPolySeg(self._seg, new_sweep, undoable=True)
        self._hideGuides()
        return True

    def _complete(self : Self, pos : QPointF) -> None:
        self.commit(pos)

    def _cancel(self : Self) -> None:
        self._previewRestore()
        self._hideGuides()

    def _previewTargets(self : Self) -> list[PolySegItem]:
        return [self._seg]

    def _previewSaveTarget(self : Self, target : PolySegItem) -> float | None:
        return target.sweep()

    def _previewRestoreTarget(
        self   : Self,
        target : PolySegItem,
        state  : float | None
    ) -> None:
        target.setSweep(state)

    def _previewDidRestore(self : Self) -> None:
        self._polyline.updatePath()

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
