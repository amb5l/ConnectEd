# Scene / View Split

Goal: complete the clean separation of diagram-specific behavior from the
shared drawing base, while leaving `DrawingScene` / `DrawingView` as the home
for functionality that genuinely applies to all graphics editors.

## Current State

- `DrawingScene` is already the common scene base.
- `DiagramScene` already owns connectivity (`netlist`, conn APIs, diagram
  resources).
- `SymbolScene` already exists and does not implement connectivity.
- `DiagramView` already has a diagram-specific state mixin layered on top of
  the drawing view base.
- `SymbolView` still reuses `DrawingView` directly.

So the split is partly there already, but some diagram-specific logic still
leaks into the drawing layer.

## Key Correction

The state machine is a view concern, not a scene concern.

The old statement "the existing DrawingScene state machine belongs in
DiagramScene" is not quite right. The real split is:

- `DrawingViewStateMixin`: shared editor/view state machinery
- `DiagramViewStateMixin`: diagram-specific states layered on top
- future `SymbolViewStateMixin`: symbol-specific states layered on top

## What Should Stay In The Base

These belong in `DrawingScene` / `DrawingView` because they are editor-common:

- selection handling
- generic move / resize / rotate / duplicate / paste interactions
- generic item placement for unconstrained drawing items
- properties / appearance editing
- guides, grips, viewport state, marquee, zoom / pan
- base undo stack ownership

## What Must Move Out Of The Base

These should not live in the drawing base:

- connectivity-aware movement and detachment logic
- wire / connection placement
- block-pin movement semantics tied to diagram blocks
- netlist-aware delete / add / move behavior
- anything that assumes entries, vertices, segments, or nets exist

## Concrete Gaps To Close

### 1. Remove diagram-specific interaction imports from drawing states

`DrawingViewStateIdle` still imports and uses `EditMoveBlockPinsInteraction`
from the drawing interaction module, even though that interaction now belongs
to the diagram layer.

This is the clearest remaining leak from diagram behavior into the base view
state flow.

Action:
- stop `drawing/state/idle.py` from depending on diagram-only interactions
- dispatch block-pin move initiation from the diagram view/state layer instead

### 2. Split the view state hierarchy properly

`DiagramViewStateMixin` already exists and extends `DrawingViewStateMixin`.
That is the right shape.

`SymbolView` should follow the same pattern:
- create a `SymbolViewStateMixin`
- keep only symbol-relevant place/edit states
- avoid inheriting diagram assumptions via the generic idle/move path

### 3. Keep scene APIs aligned with the split

The API mixins should reflect the same boundary:

- `DrawingSceneApiMixin`: generic edit/add/property behavior
- `DiagramSceneApiMixin`: diagram add/conn/edit behavior
- `SymbolSceneApiMixin` if symbol-specific scene operations become non-trivial

At the moment, diagram APIs are still not fully separated from the drawing API
surface, and some diagram-specific edit behavior is not yet wired through the
diagram API mixin.

### 4. Define symbol-specific ownership explicitly

`SymbolScene` is not just "DiagramScene without connectivity".

It needs its own rules for:
- symbol pins
- symbol boundary / frame item ownership
- item placement constraints relative to the symbol boundary
- export / serialization expectations for symbols

Those rules should live in symbol-specific scene/view code, not in the drawing
base.

### 5. Keep item classes honest about scope

Some items are generic drawing items.
Some are diagram-only.
Some are symbol-only.

The split will stay messy unless code is explicit about which layer owns:
- `SegmentItem`, `VertexItem`, `EntryItem` => diagram
- symbol boundary item and related pin semantics => symbol
- line / rectangle / ellipse / text / polyline => drawing-generic

## Proposed End State

### Shared drawing layer

- `DrawingScene`
- `DrawingView`
- `DrawingSceneApiMixin`
- `DrawingViewStateMixin`
- generic interactions and item editing infrastructure

### Diagram layer

- `DiagramScene`
- `DiagramView`
- `DiagramSceneApiMixin`
- `DiagramViewStateMixin`
- connectivity-aware interactions, placement, and commands

### Symbol layer

- `SymbolScene`
- `SymbolView`
- `SymbolSceneApiMixin` when needed
- `SymbolViewStateMixin`
- symbol-specific placement/edit constraints and interactions

## Next Steps

1. Finish moving `EditMoveBlockPinsInteraction` ownership fully into the
   diagram layer by removing drawing-layer imports/call sites.
2. Introduce a `SymbolViewStateMixin` so symbol editing stops inheriting
   diagram-adjacent assumptions through drawing states.
3. Review `DrawingViewStateIdle` and related generic move/placement paths for
   diagram-only branches and move them behind diagram overrides.
4. Review scene API mixins so diagram edit behavior is exposed from the diagram
   API layer rather than borrowed implicitly from the drawing base.
5. Add the missing symbol boundary item and then place symbol-pin behavior
   under symbol-specific ownership.