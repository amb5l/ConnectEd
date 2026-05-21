# Net labels

Implementation plan for floating `NetLabelItem` on diagram sheets. Replaces the
legacy model (labels parented to `FreeNodeItem`) with unparented text items whose
**origin handle** is the wire attachment hotspot.

## Design

### What changed from the earlier sketch

| Earlier idea | Current direction |
|--------------|-------------------|
| Structurally bound to `SegmentItem` (`_segment`, `_t`) | **Unparented** top-level item; no segment reference stored |
| Container + `PropertyTextItem` child | **Single item** — cousin of `PropertyTextItem`, not parent/child |
| Label follows segment on geometry change | Label **does not move** when the wire moves; touch is **recomputed** |
| Cleat/tether to segment handle | **Origin** (`RectHandleId`) is the hotspot; text offset like any `TextItem` |

### Participation rule

A label contributes to net name resolution **only if** its origin
(`getOriginHandle().scenePos()`) geometrically **touches** a segment — point on
the **finite** segment within tolerance. Moving the label or changing origin can
attach or detach without editing the wire.

### Selection rule

Selecting a **segment** finds coincident `NetLabelItem`s (origin touches that
segment) and **propagates selection** to them. No parent/child link to the
segment.

### Segment delete

Labels are **not** auto-deleted when a segment is removed. They may become
non-touching and drop out of resolution until the user repositions them.

```mermaid
flowchart TB
  NL[NetLabelItem unparented]
  NL -->|origin hot spot| TOUCH{touches segment?}
  TOUCH -->|yes| RESOLVE[Include in net naming]
  TOUCH -->|no| IGNORE[Ignore for resolution]
  SEG[SegmentItem selected]
  SEG -->|geometric query| NL
```

## Current state

- [`ConnectEd/widgets/graphics/items/net_label.py`](../ConnectEd/widgets/graphics/items/net_label.py) —
  stub `TextItem` subclass; `__init__` body is `pass` (broken).
- Legacy labels under [`FreeNodeItem`](../ConnectEd/widgets/graphics/items/node.py);
  netlist scans `node.childItems()` in
  [`netlist.py`](../ConnectEd/widgets/graphics/scenes/diagram/netlist.py) (lines
  ~107–110, ~367–369).
- Orphan free-node cleanup deletes child labels in
  [`conn.py`](../ConnectEd/widgets/graphics/scenes/diagram/api/conn.py).
- `editDelete` treats `NetLabelItem` like a property-text child (parent exception)
  in [`edit.py`](../ConnectEd/widgets/graphics/scenes/diagram/api/edit.py).
- `FreeNodeItem.fromXml` has a parent/child bug:
  `instance.setParentItem(child)` should be `child.setParentItem(instance)`.
- Theme: `NetLabel` quill already in diagram resources/settings.
- `NetLabelItem` is **not** registered in
  [`items/__init__.py`](../ConnectEd/widgets/graphics/items/__init__.py)
  `_item_classes` (top-level XML load/save will not work until registered).

## Target: `NetLabelItem`

**Base:** extend [`TextItem`](../ConnectEd/widgets/graphics/items/text.py) (transform,
rect handles, resize grips, appearance) — **not** `PropertiesMixin` +
`PropertyTextSpec`.

**Why not `PropertyTextItem`:** cleat/tether and `owner().properties` are for
labels bound to a parent item. Net labels are free-floating.

| Feature | Approach |
|---------|----------|
| Name + displayed text | `_name`, `_value`; `onTextChanged()` → `value` or `"<{_name}>"` |
| Properties | `InherentProperty` for **Name** and **Value** (MVP); optional **Visible** later |
| Padding | Include `TextItem._PROPERTIES_PADDING` in `_PROPERTIES` |
| Origin | `ItemRectHandlesMixin`; origin point = hotspot |
| Hot spot visibility | `_ORIGIN_GRIP_SHAPE = GripShape.STAR` on origin handle; shown when selected via `setGripsVisible` (same as other rect-handle text items). **No** custom `paint()` or extra resource. |
| Text body | `NetLabel` theme quill |
| Direct `text()` / `setText()` | Block like `PropertyTextItem`; edit via properties / dialogs |

**Do not use:** segment registry, cleat-to-segment, `_PROPERTY_TEXTS`,
`NetLabelTetherItem`.

### `__init__` (fill existing signature, do not rewrite)

Call `super().__init__(...)`, set `_name` / `_value`, `onTextChanged()`.
Default `_name` for net naming labels is `"Name"` (matches legacy
`child.name() == "Name"` checks).

Implement `settingsName() → "NetLabel"`.

Set `_ORIGIN_GRIP_SHAPE = GripShape.STAR` (class attribute). Do **not** override
`paint()` or clear `ItemHasNoContents` — `TextItem` renders via its child
renderer; the origin grip marks the hotspot when the item is selected.

## Netlist: touch geometry and resolution

Touch helpers live on [`Netlist`](../ConnectEd/widgets/graphics/scenes/diagram/netlist.py),
not in a separate items module. Views and items call `scene.netlist.*`.

**Staged rollout:** stage **2** adds only **placement snap** on `Netlist` (geometry
primitives + `snapToSegment`). Stage **3+** adds resolution, change handlers,
and the rest of the public API. `_notifyNetlist()` on `NetLabelItem` stays a
no-op until `onNetLabelChanged` lands in stage 3.

**Why not `items/net_label_touch.py`:** avoids a freestanding geometry module
that would pull `Netlist` / `DiagramScene` and segment graph concerns into
`items/`. Keeping touch tests beside `_resolveSubnet` keeps “does this label
name this net?” in one place.

**Do not** put touch logic on `NetLabelItem` — the item only notifies the
netlist when its geometry or value changes (effective from stage 3).

### Constants and primitives (module-level or `Netlist` private)

```python
_TOUCH_EPS = PITCH / 2   # core.defs

def _segmentSceneLine(seg: SegmentItem) -> QLineF
def _originScenePos(label: NetLabelItem) -> QPointF
def _segmentTouchesOrigin(seg, origin, eps=_TOUCH_EPS) -> bool
```

- Segment in scene coords: `seg.scenePos()` → `seg.mapToScene(seg.line().p2())`.
- Project origin onto segment; require parameter `t ∈ [0, 1]` and distance ≤ `eps`.
- **Stage 2:** implement primitives + `snapToSegment` only.
- **Stage 3+:** `_originScenePos` and `_segmentTouchesOrigin` also drive resolution
  and selection.

### Public `Netlist` methods

**Stage 2 (placement snap only):**

```python
def snapToSegment(self, scene_pos: QPointF) -> tuple[SegmentItem, QPointF] | None
```

**Stage 3+ (resolution and selection):**

```python
def netLabels(self) -> list[NetLabelItem]
def labelsTouchingSegment(self, seg: SegmentItem) -> list[NetLabelItem]
def labelsTouchingSubnet(self, nodes: set[NodeItem]) -> list[NetLabelItem]
def subnetsForLabel(self, label: NetLabelItem) -> set[Subnet]
def subnetsForSegment(self, seg: SegmentItem) -> set[Subnet]
def onNetLabelChanged(self, label: NetLabelItem) -> None
def onSegmentGeometryChanged(self, seg: SegmentItem) -> None
```

- `snapToSegment` — nearest segment + closest on-segment point within tolerance.
- `onNetLabelChanged` / `onSegmentGeometryChanged` — `_resolveSubnets(affected)`,
  then `self._scene.netlistChanged.emit()` (**stage 3+**).

### Resolution changes (stage 3+)

In `_resolveSubnet` / `nodeNameSuffixType`:

1. Remove `FreeNodeItem.childItems()` / `NetLabelItem` scans.
2. Collect name labels via `labelsTouchingSubnet(subnet.nodes)`; filter
   `label.name() == "Name"`; append `label.value()` to `label_names`.
3. Precedence unchanged (name labels over port names; conflicts → DRC later).

**On segment geometry change:** do not move labels; call `onSegmentGeometryChanged`.
**On label move / origin / value change:** `NetLabelItem` calls `onNetLabelChanged`.

Remove label deletion from orphan free-node cleanup in
[`conn.py`](../ConnectEd/widgets/graphics/scenes/diagram/api/conn.py).

## Selection: segment → coincident labels (stage 6)

Hook in [`DrawingView._selectClick`](../ConnectEd/widgets/graphics/views/drawing/private.py)
after selecting a `SegmentItem`:

1. If segment is selected, `labels = scene.netlist.labelsTouchingSegment(seg)`.
2. For each label, apply the same fresh / shift / ctrl policy as the segment
   click (`setSelected(True)` or toggle).

**Move/slide (MVP):** segment move does **not** move touching labels (no
structural bind). Optional later: move touching labels with selected segment.

## Scene API and commands (stage 2 add; stage 3 netlist hook)

### `DiagramScene.addNetLabel`

Add to [`diagram/api/add.py`](../ConnectEd/widgets/graphics/scenes/diagram/api/add.py):

```python
def addNetLabel(
    self,
    pos        : QPointF,
    name       : str = "Name",
    value      : str = "",
    origin     : RectHandleId = RectHandleId.CENTER,  # hotspot at placement point
    ...        # text layout kwargs aligned with NetLabelItem.__init__
    undoable   : bool = True,
) -> NetLabelItem
```

Behaviour:

1. Construct `NetLabelItem` with origin positioned so the hotspot lands on `pos`
   (placement interaction computes item `pos` from origin + align/pad).
2. Add via undo command (see below).
3. **Stage 2:** no netlist refresh on add/delete.
4. **Stage 3+:** call `netlist.onNetLabelChanged(label)` after add; symmetric refresh on undo.

### Undo command

Prefer a dedicated command in e.g.
[`diagram/cmd/net_label.py`](../ConnectEd/widgets/graphics/scenes/diagram/cmd/net_label.py)
(subclass `CmdDiagramSceneBase` or compose `CmdAdd`):

- **redo:** add item to scene, select it (**stage 3+:** `netlist.onNetLabelChanged`).
- **undo:** remove item (**stage 3+:** refresh netlist for formerly touched subnets).

Alternatively wrap `CmdAdd` and invoke netlist refresh in `addNetLabel` after
`cmdExec`; dedicated command keeps netlist side effects symmetric on undo.

### `editDelete`

In [`diagram/api/edit.py`](../ConnectEd/widgets/graphics/scenes/diagram/api/edit.py),
remove `NetLabelItem` from the property-text parent exception — treat as a normal
top-level item.

## XML (new format only, stage 2)

Top-level `<NetLabel>` element (via `ItemXmlMixin` + property attrs):

- Scene position (`X`, `Y`), text layout, `Origin`, **Name**, **Value**.
- **No** `SegmentID` / `T`.

Register `NetLabelItem` in
[`items/__init__.py`](../ConnectEd/widgets/graphics/items/__init__.py). Scene
[`toXml` / `fromXml`](../ConnectEd/widgets/graphics/scenes/diagram/__init__.py)
already serialises unparented `ItemXmlMixin` items.

Strip NetLabel child XML from
[`node.py`](../ConnectEd/widgets/graphics/items/node.py) (`toXml`, `fromXml`).

No migration for old FreeNode-embedded labels.

## Place menu and placement flow (stage 2)

Primary UX: **Place → Net Label** on diagram sheets (alongside Connection, Tap,
etc.). Secondary: segment context menu **Add Net Label** (same commit path).

### Menu bar

| File | Change |
|------|--------|
| [`menu_bar/actions.py`](../ConnectEd/widgets/window/menu_bar/actions.py) | `Action(..., "Net Label", "Place Net Label", shortcut TBD)` e.g. `placeNetLabel` |
| [`menu_bar/slots.py`](../ConnectEd/widgets/window/menu_bar/slots.py) | `@withCurrentWidget(DiagramView) def placeNetLabel(...): view.ui.placeNetLabel()` |
| [`menu_bar/__init__.py`](../ConnectEd/widgets/window/menu_bar/__init__.py) | In `updatePlaceMenu`, diagram branch: add `placeNetLabel` after `placeTap` (connectivity group) |

### View UI

[`views/diagram/ui/place.py`](../ConnectEd/widgets/graphics/views/diagram/ui/place.py):

```python
def placeNetLabel(self) -> None:
    self._view.state.go(self._view.statePlaceNetLabel)
```

### View state

[`views/diagram/state/__init__.py`](../ConnectEd/widgets/graphics/views/diagram/state/__init__.py):

- Declare and construct `statePlaceNetLabel`.

[`views/diagram/state/place.py`](../ConnectEd/widgets/graphics/views/diagram/state/place.py):

- `DiagramViewStatePlaceNetLabel` — status e.g. `"Place Net Label: pick a point on a wire"`.
- On click: `scene.netlist.snapToSegment(...)`; if hit, start
  `PlaceNetLabelInteraction`.
- If no segment at click, ignore or show status hint (no placement).

### Placement interaction

New [`PlaceNetLabelInteraction`](../ConnectEd/widgets/graphics/views/diagram/interaction/place.py)
(subclass `PlaceBase1PosInteraction` or `Interaction`):

- Preview `NetLabelItem` following cursor, snapped to wire under cursor.
- Hotspot (origin) stays on the segment; item `pos` derived from origin handle
  geometry (default origin `CENTER` or corner as chosen).
- **Commit:** `scene.addNetLabel(snap_pos, undoable=True)` — do not call
  `addItems` directly (netlist must refresh).
- **Cancel:** remove preview.
- Optional: open properties dialog for **Value** before or after first click
  (mirror `DrawingViewStatePlaceText` + `TextItemDialog` pattern; may use
  item properties dialog instead for MVP).

### Snap

Placement uses `scene.netlist.snapToSegment(scene_pos)` (same primitives as
resolution touch tests).

## Segment context menu (secondary, stage 2)

[`SegmentItem`](../ConnectEd/widgets/graphics/items/segment.py) currently mixes in
`ItemMenuMixin` but does not implement `ctxMenuItems` (right-click on segments
is broken). Implement `ctxMenuItems` for diagram scenes:

- **Add Net Label** — place at segment midpoint via `_segmentSceneLine` (or
  `snapToSegment` if menu gains click position later); calls `scene.addNetLabel(...)`.

## `NetLabelItem` UI on existing item

Override `ctxMenuItems` (cousin of `PropertyTextItem` / `TextItem`):

- **Properties...** → `editItemProperties` (edit **Name** / **Value**).
- **Appearance...** → `editAppearance`.
- Auto width/height actions as for text items.

**Origin hotspot:** `_ORIGIN_GRIP_SHAPE = GripShape.STAR` (already on
[`net_label.py`](../ConnectEd/widgets/graphics/items/net_label.py)). When
selected, the origin handle’s star grip (`MoveGripItem` via
[`grip.py`](../ConnectEd/widgets/graphics/items/grip.py) `origin_shape`) is
visible through the normal `setGripsVisible` path — no `paint()` override.

## TODO checklist

Work in order unless noted. Check off as completed.

### 1. `NetLabelItem` — `items/net_label.py`

Do this first. Item should be constructable before placement lands in §2.

- [x] Add `TextItem._PROPERTIES_PADDING` to `_PROPERTIES`.
- [x] Implement `__init__` body: `super().__init__(...)`, `_name`, `_value`, `onTextChanged()` (keep existing signature).
- [x] Implement `settingsName() → "NetLabel"`.
- [x] `_ORIGIN_GRIP_SHAPE = GripShape.STAR` for origin hotspot when selected (no custom `paint()`).
- [x] Block direct `text()` / `setText()` (raise like `PropertyTextItem`).
- [x] Wire `setName` / `setValue` to call `_notifyNetlist()` after `onTextChanged()`.
- [x] Override `onPositionChanged` — call super, then `_notifyNetlist()`.
- [x] Override `setOrigin` — call super, then `_notifyNetlist()`.
- [x] `_notifyNetlist()` — if scene is `DiagramScene`, call `scene.netlist.onNetLabelChanged(self)` (guard until §3 exists).
- [x] Override `ctxMenuItems` — Properties, Appearance, auto width/height (cousin of `PropertyTextItem`).

### 2. Place net labels

Goal: place, edit, save, and reload labels on wires. **No net naming yet**
(`_notifyNetlist` remains a no-op).

**Snap geometry on `Netlist` (placement subset only):**

- [ ] `_TOUCH_EPS = PITCH / 2`.
- [ ] `_segmentSceneLine(seg)` — scene-space finite segment from `scenePos()` + `line().p2()`.
- [ ] `_segmentTouchesOrigin(seg, origin, eps)` — project onto segment; require `t ∈ [0, 1]` and distance ≤ `eps` (needed by `snapToSegment`).
- [ ] `snapToSegment(scene_pos)` — nearest segment + closest on-segment point within tolerance.

**Scene API and undo — `scenes/diagram/`:**

- [ ] Add `diagram/cmd/net_label.py` with `CmdAddNetLabel` (or equivalent):
- [ ]   **redo:** add item, select (no netlist call yet).
- [ ]   **undo:** remove item.
- [ ] Add `DiagramSceneApiAddMixin.addNetLabel(...)` in `api/add.py`:
- [ ]   Build `NetLabelItem` kwargs (default `name="Name"`, `value=""`).
- [ ]   Position item so origin hotspot lands on `pos` (document chosen origin default).
- [ ]   `cmdExec` with `CmdAddNetLabel`.
- [ ] Export command from `cmd/` package if needed.

**Delete and XML:**

- [ ] `scenes/diagram/api/edit.py` — remove `NetLabelItem` from property-text parent delete exception.
- [ ] `items/__init__.py` — `registerClass(_item_classes, "NetLabelItem")`.
- [ ] Manual round-trip: save diagram with label, reload, verify `<NetLabel>` attrs.

**Place menu — window / view wiring:**

- [ ] `menu_bar/actions.py` — `placeNetLabel` action (label, tooltip, shortcut TBD).
- [ ] `menu_bar/slots.py` — `placeNetLabel(view)` → `view.ui.placeNetLabel()`.
- [ ] `menu_bar/__init__.py` — add to diagram branch of `updatePlaceMenu` (after `placeTap`).
- [ ] `views/diagram/ui/place.py` — `placeNetLabel()` → `state.go(statePlaceNetLabel)`.
- [ ] `views/diagram/state/__init__.py` — declare and construct `statePlaceNetLabel`.
- [ ] `views/diagram/state/place.py` — `DiagramViewStatePlaceNetLabel`:
- [ ]   Status string for status bar.
- [ ]   On click: `scene.netlist.snapToSegment(...)`; if none, stay in state (optional status hint).
- [ ]   On hit: start `PlaceNetLabelInteraction` at snapped point.

**Place interaction — `views/diagram/interaction/place.py`:**

- [ ] Add `PlaceNetLabelInteraction`:
- [ ]   Create preview `NetLabelItem` (not yet on undo stack).
- [ ]   `update(pos)` — `scene.netlist.snapToSegment(pos)`; move item so origin stays on segment.
- [ ]   `_commit` — `scene.addNetLabel(snap_pos, ..., undoable=True)`; remove preview if separate.
- [ ]   `_cancel` — remove preview from scene.
- [ ]   `ctxMenuItems` — Complete / Cancel (match other place interactions).
- [ ] (Optional) Open properties dialog for **Value** before interact (like Place Text).

**Segment context menu — `items/segment.py`:**

- [ ] Implement `ctxMenuItems(view)` for diagram scenes.
- [ ] Action **Add Net Label** — `scene.addNetLabel(midpoint)` via `_segmentSceneLine(...).pointAt(0.5)`.
- [ ] Guard: only when `isinstance(scene, DiagramScene)`.

**Stage 2 verification:**

- [ ] Place → Net Label on a wire; label appears with origin on segment.
- [ ] Set **Value** via Properties; displayed text updates (netlist unchanged).
- [ ] Undo/redo add/remove label.
- [ ] Save/load preserves top-level `<NetLabel>` elements.
- [ ] Segment context menu **Add Net Label** works.
- [ ] Right-click existing label: Properties / Appearance.

### 3. Netlist resolution — `scenes/diagram/netlist.py`

**Remaining touch / public API:**

- [ ] `_originScenePos(label)` — `label.getOriginHandle().scenePos()`.
- [ ] `netLabels()` — all top-level `NetLabelItem` in `self._scene`.
- [ ] `labelsTouchingSegment(seg)` — filter `netLabels()` by `_segmentTouchesOrigin`.
- [ ] `labelsTouchingSubnet(nodes)` — in-subnet segments only; dedupe labels.
- [ ] `subnetsForLabel(label)` — subnets of segments touched by label origin.
- [ ] `subnetsForSegment(seg)` — subnets of `node1` / `node2`.
- [ ] `onNetLabelChanged(label)` — `_resolveSubnets(subnetsForLabel(label))`, `netlistChanged.emit()`.
- [ ] `onSegmentGeometryChanged(seg)` — `_resolveSubnets(subnetsForSegment(seg))`, `netlistChanged.emit()`.

**Resolution (replace legacy scans):**

- [ ] Remove `FreeNodeItem` / `NetLabelItem` child scan from `nodeNameSuffixType`.
- [ ] In `_resolveSubnet`, replace per-node `childItems()` loop with `labelsTouchingSubnet(subnet.nodes)`.
- [ ] Keep filter `label.name() == "Name"`; append `label.value()` to `label_names`.
- [ ] Verify name-label precedence over port/pin names unchanged in existing resolution logic.

**Wire commands and item notifications:**

- [ ] `CmdAddNetLabel` redo/undo — call `onNetLabelChanged` (or equivalent refresh).
- [ ] Confirm `_notifyNetlist()` on `NetLabelItem` now drives resolution.

- [ ] (Optional) Unit tests for `_segmentTouchesOrigin` / `snapToSegment` edge cases.

### 4. Segment geometry hook — `items/segment.py`

- [ ] At end of `onGeometryChange`, if scene is `DiagramScene`, call `netlist.onSegmentGeometryChanged(self)`.

### 5. Legacy removal

- [ ] `items/node.py` — remove NetLabel child serialisation from `NodeItem.toXml`.
- [ ] `items/node.py` — remove NetLabel child deserialisation from `FreeNodeItem.fromXml`.
- [ ] `scenes/diagram/api/conn.py` — remove NetLabel deletion loop in orphan free-node cleanup.

### 6. Selection propagation — `views/drawing/private.py`

- [ ] After `_selectItem(items[0])` in `_selectClick`, if item is `SegmentItem` and selected:
- [ ]   Guard: scene is `DiagramScene`.
- [ ]   For each label in `scene.netlist.labelsTouchingSegment(seg)`, apply fresh / ctrl-toggle selection policy.
- [ ] Confirm shift-add-to-selection behaviour matches segment click (no accidental clear).

### 7. End-to-end verification

- [ ] Set **Value** via Properties; netlist browser / subnet name updates.
- [ ] Move label off wire; name drops from net resolution.
- [ ] Move label back onto wire; name reappears.
- [ ] Select segment; touching labels become selected.
- [ ] Delete segment; label remains but no longer names the net.
- [ ] Undo/redo add label restores/removes net name correctly.

### 8. Docs follow-up (post-implementation)

- [ ] Update [`CONNECTIVITY2.md`](CONNECTIVITY2.md) — floating label model (remove FreeNode parent wording).
- [ ] Tick “implement net labels” in [`NEXT.md`](NEXT.md) or add cross-link to this doc.

## Implementation order (summary)

1. §1 `NetLabelItem` — done.
2. §2 **Place net labels** — snap on `Netlist`, `addNetLabel`, XML, Place menu, interaction, segment menu; verify placement without net naming.
3. §3 **Netlist resolution** — remaining touch API, `_resolveSubnet`, wire `onNetLabelChanged` into item and commands.
4. §4 Segment geometry hook.
5. §5 Legacy removal (FreeNode child XML, conn cleanup).
6. §6 Selection propagation.
7. §7 End-to-end verification (net naming + selection).
8. §8 Docs follow-up.

## Out of scope (for now)

- Type / Visible / `_net_names` type codes.
- DRC for conflicts or floating labels not touching any segment.
- Old FreeNode XML migration.
- Auto-moving labels when segment slides.
- Properties spreadsheet columns for net labels.

## Related docs

- [`CONNECTIVITY2.md`](CONNECTIVITY2.md) — net naming overview (update when implemented).
- [`NEXT.md`](NEXT.md) — name-label precedence notes.
