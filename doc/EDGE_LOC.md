# Edge-located pin resize

Resizing a block or a symbol keeps every edge-located pin on its edge. A handle stops when the next step would push a pin past either corner.

`ItemEdgeLocChildMixin` is the pin (`BlockPinItem`, `SymbolPinItem`). `ItemEdgeLocParentMixin` is the rectangle it sits on. They stay separate classes in `edge_loc.py`. `setLoc` already requires the parent mixin. `moveHandleBy` stays `None`. The grip drag records the real scene movement on undo, and redo runs through the same clip.

## Location

Offset is a distance along the edge from the rectangle's top-left, in local coordinates.

| Edge | Offset runs | Anchor |
|---|---|---|
| Left, Right | down the height | top |
| Top, Bottom | across the width | left |

`loc2pos` places a left or top pin from the offset alone. A right or bottom pin also depends on the width or height, so a size change has to `setLoc` again or that pin stays at the old edge.

A pin stays planted in the scene until a corner reaches it. Dragging the right or bottom edge leaves offsets alone, and `setLoc` carries the pins on that edge. Dragging the left edge subtracts the applied movement from the offsets of the top and bottom pins. Dragging the top edge subtracts it from the offsets of the left and right pins. The local origin moves with the item, so an unchanged offset would slide every pin with that edge.

## Limits

Clip each axis before the rectangle changes. A corner handle can stop in one axis and still move in the other. The existing `PITCH` floor in `setPoints` remains.

- Right: new width is at least `PITCH` and at least the largest top or bottom offset.
- Left: movement is at most the smallest top or bottom offset.
- Bottom and top: the same, using the left and right offsets and the height.

After the clip, every offset is in `[0, length]` of its edge. The pin that stopped the handle sits on that corner.

Only `ItemEdgeLocChildMixin` children are rewritten or refreshed. Block labels, and the lines and text inside a symbol, stay at their local positions. Nets stay out of this path. `setLoc` moves the pin. Rubber-banding stays in the diagram interaction.

## Steps

1. Add the parent operations on `ItemEdgeLocParentMixin`.
   - Clip a handle delta against the pins and the current size.
   - Rewrite offsets for the top or left part of the delta that will actually be applied.
   - `setLoc` each edge-located child from its current edge and offset.
2. `BlockItem` already inherits the parent mixin. Override `moveHandleBy`: rewrite and clip, then call the rect implementation. `onGeometryChanged` refreshes the pins, which removes the TODO there. `setRect` already calls `onGeometryChanged`, so a Width or Height edit refreshes too. Those setters clip with the same floors, because they move no origin edge and must not shrink past a pin.
3. `SymbolBaseItem` inherits `ItemEdgeLocParentMixin`. A symbol pin's `setLoc` writes a position only when the parent is that mixin. The definition and the instance both parent pins, so both need it.
4. Route symbol rectangle changes through the same clip, origin rewrite, and refresh. `SymbolBaseItem.setWidth`, `setHeight`, and `setRect` assign the rect directly and do not notify geometry. `ItemRectHandlesMixin.moveHandleBy` requires `BaseRectangleMixin`, which the symbol body is not. The symbol override clips, applies the position and size change, and refreshes. Syncing an instance still copies the definition rect and clones the pins. The clone's `setLoc` lands once the instance is a parent.

## Test

`tests/unit/widgets/test_edge_loc.py` builds one block and drives every resize handle.

Create a `BlockItem` and parent a `BlockPinItem` on each of the four edges. Place each pin inset from both corners, so either end of the edge can reach it. Give the block a real size, several pitches on each side.

Then call `moveHandleBy` for each corner and each mid-edge handle: `Top Left`, `Top Center`, `Top Right`, `Middle Left`, `Middle Right`, `Bottom Left`, `Bottom Center`, `Bottom Right`. `Middle Center` moves the whole block and is not part of this test.

For each of those eight handles, move outward by more than one pitch, then inward by more than the distance from the moving edge to the nearest pin. After every call:

- Each pin's edge is unchanged.
- Its offset is within `[0, length]` of that edge.
- Its local position equals the parent's `loc2pos` of that location.
- An inward move that would pass a pin leaves that pin on the corner, and the rectangle no smaller than the pin on that axis.
- A pin whose edge did not move along the drag keeps its scene position. A pin on the edge that moved follows that edge.
