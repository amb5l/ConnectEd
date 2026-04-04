# Connectivity

## Data Model

Two parallel representations maintained in sync:

- **Graphics layer** -- `VertexItem` / `EntryItem` (`QGraphicsPathItem`) and
  `SegmentItem` (`QGraphicsLineItem`) live in the `QGraphicsScene`. They handle
  rendering, hit testing, and spatial queries.
- **Netlist layer** -- `Net` objects hold adjacency (`dict[int, set[int]]`)
  using integer vertex IDs only. No references to graphics objects.

## Scene-Level State (`DrawingSceneConnMixin`)

- `_id_net : Counter` -- monotonic net ID generator
- `_id_vtx : Counter` -- monotonic vertex ID generator
- `_nets : dict[int, Net]` -- net ID to `Net` instance
- `_nodes : dict[int, VertexItem]` -- vertex ID to `VertexItem` instance
- `_node_net : dict[int, int]` -- vertex ID to net ID (reverse lookup)

## Items

- **`VertexItem`** -- free-floating vertex with `_id: int`. Manages
  `_connections: list[SegmentItem]` for the graphics side. Appearance changes
  with connection state (unconnected / connected / junction).
- **`EntryItem`** -- `VertexItem` subclass parented to a pin (`PortPinMixin`).
  Junction threshold of 2 (vs 3 for free vertices). `settingsName()` returns
  `"Entry"` for distinct appearance.
- **`SegmentItem`** -- line between two `VertexItem`s. References `_vtx1` and
  `_vtx2`. Pure graphics; no net awareness.
- **`Net`** -- plain Python object. Stores `_id`, `_name`, `_adjacency`.
  Supports `addEdge`, `splitEdge`, `unSplitEdge`. Serializes edges as compact
  XML attribute.

## Operations That Affect Connectivity

- **Place segment** (`addSegment`): get/create vertices at endpoints, create
  segment, create/join nets, tidy.
- **Delete items**: remove segments and vertices, split or remove nets.
- **Move items**: moving a port moves its entry; if an entry lands on or leaves
  a vertex, nets may join or split.
- **Paste / duplicate**: new IDs generated for vertices and nets via counters.
  Items are added one at a time in a specific order so that connectivity can be
  resolved incrementally:
  1. **Pin-bearing items** (ports, blocks, symbols): add each item to the scene,
     then scan its pin entries against the existing scene. For each entry:
     - Entry hits an existing vertex -- merge the vertex into the entry.
     - Entry hits an existing segment -- split that segment at the entry.
     - Entry hits another pin entry -- create a zero-length segment between them.
       The joined entries change from unconnected to connected appearance,
       visually indicating the connection even though the segment has no length.
  2. **Free vertices**: add each vertex, creating or merging into existing
     vertices and entries at the same position.
  3. **Segments**: add each segment. Walk along its length, splitting at any
     existing vertices encountered, and update nets accordingly.

## Undo/Redo Strategy

All connectivity mutations go through `QUndoCommand` subclasses grouped in
macros:

- **Unified commands** handle both graphics and netlist for tightly coupled
  operations (e.g. `CmdSplitSegment` splits the graphics AND updates the net
  adjacency).
- **Netlist-only commands** for operations without a graphics counterpart
  (e.g. `CmdMergeNets` stores adjacency snapshots for undo).
- **Macros** compose commands atomically (e.g. `addSegment` wraps vertex
  creation, segment creation, and net updates in one macro).

For net merges, the command stores pre-merge adjacency snapshots
(`dict[int, set[int]]`) of both nets. Undo restores both snapshots and
re-separates the nets.

## Catching Connectivity Changes

Qt provides no semantic signal for "connectivity changed."
`QGraphicsScene.changed()` fires for any visual update and carries no
structural information. All connectivity-mutating actions flow through undo
commands, and those commands update both graphics and netlist atomically. The
commands are the catch-all -- no connectivity can change without going through
them.
