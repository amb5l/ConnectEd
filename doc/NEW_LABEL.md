# New label model

Unite `PropertyTextItem` and `NetLabelItem` into one decorative `LabelItem`. A net name lives on a new `LabelNodeItem`, which is a `FreeNodeItem` that carries properties. The label is a view of one of those properties.

## LabelItem

`LabelItem` replaces `PropertyTextItem`. It stays decorative. It shows one property of its owner, and it never names a net by itself.

Rename the item, its tether, and the spec and edit types. The XML reader accepts both `PropertyText` and `Label`. The writer emits `Label`. Theme lookup keeps falling back to `PropertyText`.

Two parents, two move policies:

| Parent | Drag |
|---|---|
| `LabelNodeItem` | Drags the node. Incident segments rubber-band. |
| Any other owner (port, pin, block, gate, symbol) | Drags the label relative to its cleat. The tether stays. |

The lock on a label node is structural. Local position stays at the node origin. Origin and alignment are the only placement controls, with the current net-label defaults: bottom-left origin, middle alignment, height one pitch. There is no tether and no position grip. A press or drag on that label targets the node, the same way a fixed node forwards selection to its parent. A move filter alone is not enough, because the property dialog, paste, and XML can all call `setPos`.

A label on any other owner stays freely movable relative to its cleat. The parent type decides which policy applies.

## LabelNodeItem

`LabelNodeItem` subclasses `FreeNodeItem` and uses `PropertiesMixin`. It has an inherent `Name` property. Its `Name` text is a `LabelItem` child.

`isinstance(..., FreeNodeItem)` matches the subclass. Two sites must exclude a label node explicitly:

- `isRedundantNode`, and the cull at the end of `addSegment`, leave a label node in place. A degree-2 node in the middle of a straight wire is a legal named vertex.
- `connectFixedNode` does not absorb a coincident label node into a pin.

Every other `FreeNodeItem` branch in the move interaction stays. The node moves with its segment, a real corner still slides, and incident wires still rubber-band.

Junction drawing uses the free-node threshold of 3, so a degree-2 label on a straight wire draws no dot. A label node coincident with a pin draws no second dot.

### Coincidence with a fixed node

A pin is a `FixedNodeItem` parented to the pin, so the label cannot become that node. Both items remain. Link them with the zero-length segment already used for two fixed nodes at one point. They share a subnet. The pin keeps its own name, and the label node's `Name` joins the same resolution rules.

### Leaving a site

A normal drag rubber-bands: the vertex moves, the wires follow, and nothing is left behind. Alt-drag is the vacate. Alt already means "do not retain connections" (`slide = not alt` in the idle state).

At the abandoned site:

- Degree 2 and the two segments are aligned: unsplit. No leftover node.
- Any other site (end, corner, tee, cross): put a `FreeNodeItem` there and retarget the segments to it.

Leaving a coincident pin drops the zero-length link. The pin is already the vertex that stays, so no free node is inserted on top of it.

`isRedundantNode` stays false while the item is still a `LabelNodeItem`. The colinear cull runs only after that demotion.

## Netlist

`nodeNameSuffixType` reads `Name` from a `LabelNodeItem` directly. A property change on the node resolves the subnet.

Remove the spatial attachment of a net label:

- `labelsTouchingSegment`
- `subnetsForLabel`
- `onNetLabelChanged`
- `_deferNetLabels`
- `_segmentTouchesOrigin` and the touch epsilon

## Place menu

Placing a label stays a user action. The diagram Place menu keeps **Net Label** (`N`) and gains **Item Label** beside it. A symbol window gets **Item Label** only. Decorative **Text** stays as it is.

Both actions end in the successor of `PropertyTextItemDialog`. The net-label dialog, group box, and layout go away. The dialog title follows the owner: "Net Label" when the parent is a `LabelNodeItem`, "Item Label" otherwise.

For a net label, omit the cleat and position controls. `Name` stays the inherent property, and the value field is the net name. Origin, alignment, padding, and typography stay.

### Net Label

The click is the node position, snapped the way placement already snaps.

1. Drop a `LabelNodeItem` there and attach its locked `Name` label.
2. Join whatever is already at that point.
   - A segment through the point is split.
   - A plain `FreeNodeItem` is replaced by the label node, and its segments are retargeted.
   - A `FixedNodeItem` stays, linked by a zero-length segment.
   - A `LabelNodeItem` already there is reused, and the dialog edits its existing label.
   - Empty space leaves a degree-0 node.
3. Open the label dialog on that label.

Accept applies the dialog as one undo step with the drop. Cancel removes the node when this place created it, and leaves an existing node untouched.

The segment context command (`placeNetLabelOnSegment`) uses this same drop, at the snapped point on the wire.

### Item Label

The click picks an item that owns properties. The place adds a `LabelItem` on that item's default cleat, freely movable relative to the anchor, and opens the same dialog so the user can choose the property, the value, and the cleat. Cancel removes that new label. A click that hits no such item stays in the pick state.

## XML

Where a `Label` is written follows its parent.

| Parent | Where the `Label` is written |
|---|---|
| `LabelNode` | Nested inside that `LabelNode` element, and that element appears only in `Netlist` |
| Port, pin, block, gate, symbol | Nested on that owner in the diagram body |

`LabelNode` itself is not a diagram-level item. It appears only inside `Netlist`, as `FreeNode` does. Its child `Label` elements travel with it, so they appear in the netlist and nowhere else. A `Label` on any other owner stays in the diagram body and is absent from `Netlist`.

```xml
<Netlist>
  <LabelNode ID="26" X="470" Y="140" Name="rd_sel[4:0]">
    <Label Name="Name" Origin="Bottom Left" Pad_Left="2" Pad_Right="2"/>
  </LabelNode>
</Netlist>
```

`Name` on the node is the net name. `Name` on the child identifies which property the label shows, as `PropertyText` does today. The child has no local position. `LabelNodeItem.toXml` writes `ID`, `X`, `Y`, the node's properties, and then each child `Label`.

Segments are written already split at that point. Loading them creates a plain `FreeNode` there, because the netlist has not been read yet. The netlist handler then replaces that free node with a `LabelNodeItem`, applies `Name`, and builds the child `Label` elements from inside the `LabelNode` tag. The subnet's node list includes the new id.

A degree-0 `LabelNode` is created by its netlist element, because no segment produces a node. It is still a graph node, in a subnet of its own, so save finds it with the other netlist nodes and writes its child labels there. A `LabelNode` coincident with a fixed node is created at that position and linked with a zero-length segment. Its labels are still children of the `LabelNode` element in `Netlist`, not of the pin.

## `examples/jarv/jarv_core.sch.hdl.ce`

Edit this sheet by hand after the loader accepts the new elements. There is no general migrator.

Property texts stay nested on their owners in the diagram body. Rename the tag from `PropertyText` to `Label`. Attributes stay. Those labels do not become nodes, and they do not move into `Netlist`.

The six net labels each sit on a straight segment. Each becomes a `LabelNode` inside `Netlist`, with its `Label` nested in that element. The segment is written already split, and the new id is added to the subnet.

| Label | Point | Segment it splits | Subnet |
|---|---|---|---|
| `rs1_sel[4:0]` | (470, 120) | (460, 120)–(610, 120) | 2 |
| `rs2_sel[4:0]` | (470, 130) | (460, 130)–(610, 130) | 7 |
| `rd_sel[4:0]` | (470, 140) | (460, 140)–(610, 140) | 4 |
| `rd_we` | (470, 150) | (460, 150)–(610, 150) | 6 |
| `rs1_data[31:0]` | (820, 120) | (810, 120)–(920, 120) | 8 |
| `rs2_data[31:0]` | (820, 130) | (810, 130)–(920, 130) | 10 |

Reload the file afterwards. The netlist check stays silent: every subnet id matches, and the six names still resolve.

## Work order

1. Introduce `LabelItem` as the rename of `PropertyTextItem`. Read both XML tags. Write `Label`.
2. Introduce `LabelNodeItem` with `Name`, a locked child label, and the cull and absorb exclusions. Coincidence is a zero-length segment.
3. Point the netlist at the node's `Name`. Remove the spatial net-label path and the move deferral.
4. Rubber-band a normal drag. Alt-drag vacates, demoting to `FreeNodeItem` or unsplitting.
5. Add **Item Label** and retarget **Net Label** on the Place menu. Both open the label dialog. Remove `NetLabelItem` and its dialog.
6. Hand-edit `jarv_core.sch.hdl.ce` and load it.

## Out of scope

- Marquee selection review.
- The `@override` pass.
