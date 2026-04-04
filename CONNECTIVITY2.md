# Connectivity (networkx approach)

## Data Model

Two parallel representations maintained in sync:

- **Graphics layer** -- `VertexItem` / `EntryItem` (`QGraphicsPathItem`) and
  `SegmentItem` (`QGraphicsLineItem`) live in the `QGraphicsScene`. They handle
  rendering, hit testing, and spatial queries.
- **Netlist layer** -- a single scene-level `nx.Graph` holds connectivity.
  Graph nodes are `VertexItem` instances. Graph edges carry `SegmentItem`
  instances as edge data. Each connected component of the graph is a net.
  The graph is the single source of truth for both connectivity and the
  vertex-to-segment relationships.

## Scene-Level State (`DrawingSceneConnMixin`)

- `_graph : nx.Graph` -- the netlist. Nodes are `VertexItem` instances. Edges
  carry `SegmentItem` instances as data (`segment` attribute). Each connected
  component is a net.

No `Net` class at runtime. No `_nets`, `_node_net`, or `_nodes` dicts. No
runtime vertex ID counter -- IDs are assigned transiently during serialization.

## Items

- **`VertexItem`** -- free-floating vertex. No persistent ID; vertices are
  identified by instance reference at runtime. No `_connections` list;
  connectivity is held by the graph. Connection count for appearance is
  obtained via `self.scene()._graph.degree(self)`.
  Appearance changes with connection state (unconnected / connected / junction).
- **`EntryItem`** -- `VertexItem` subclass parented to a pin (`PortPinMixin`).
  Junction threshold of 2 (vs 3 for free vertices). `settingsName()` returns
  `"Entry"` for distinct appearance.
- **`SegmentItem`** -- line between two `VertexItem`s. References `_vtx1` and
  `_vtx2` for geometry. Also stored as edge data in the graph.

## Key Operations

### Add edge (place segment between v1 and v2)

```python
self._graph.add_edge(vtx1, vtx2, segment=seg)
```

If vtx1 and vtx2 were in different components, this automatically merges the
nets. No manual merge logic needed.

### Remove edge (delete segment)

```python
self._graph.remove_edge(vtx1, vtx2)
```

Then check if the component split:

```python
if not nx.has_path(self._graph, vtx1, vtx2):
    # net has split into two separate nets
```

### Get segment between two vertices

```python
seg = self._graph.edges[vtx1, vtx2]["segment"]
```

### Get all segments connected to a vertex

```python
segs = [data["segment"] for _, _, data in self._graph.edges(vtx, data=True)]
```

### Get connection count (for appearance)

```python
n = self._graph.degree(vtx)
```

### Split edge (insert vertex into existing segment)

```python
seg = self._graph.edges[vtx1, vtx2]["segment"]
self._graph.remove_edge(vtx1, vtx2)
self._graph.add_edge(vtx1, new_vtx, segment=seg)   # reuse existing segment
self._graph.add_edge(new_vtx, vtx2, segment=seg2)   # new segment
```

### Unsplit edge (remove redundant vertex)

```python
self._graph.remove_edge(vtx, far1)
self._graph.remove_edge(vtx, far2)
self._graph.add_edge(far1, far2, segment=surviving_seg)
self._graph.remove_node(vtx)
```

### Get net for a vertex

```python
component = nx.node_connected_component(self._graph, vtx)
```

Returns the set of `VertexItem` instances forming the net.

### Get all nets

```python
nets = list(nx.connected_components(self._graph))
```

### Check if two vertices are on the same net

```python
same_net = nx.has_path(self._graph, vtx1, vtx2)
```

## Net Properties (name, etc.)

Net properties are stored as node attributes on a designated vertex in the
component -- specifically, the vertex that parents a `NetLabelItem`:

```python
self._graph.nodes[vtx]["net_name"] = "CLK"
```

To get a net's name, find any node in the component that has a `"net_name"`
attribute. Vertices without labels have no such attribute.

## Physical vs Logical Nets

The graph represents **physical** connectivity -- what is wired together with
segments. Each connected component is a physical net.

**Logical** nets can span multiple physical components when they share the same
net name. For example, two separate groups of wires both labelled "CLK" are
physically disconnected but logically one net. This is the standard schematic
convention for power rails, clocks, buses, etc.

The graph does not add virtual edges for name-based equivalence. Every graph
edge carries a `SegmentItem`; this invariant is preserved. Instead, the logical
netlist is derived on demand by grouping physical components by name:

```python
def logicalNets(self):
    named = {}
    unnamed = []
    for component in nx.connected_components(self._graph):
        name = self._componentNetName(component)
        if name:
            named.setdefault(name, set()).update(component)
        else:
            unnamed.append(component)
    return list(named.values()) + unnamed
```

### When the logical view is needed

- **Highlighting** (click a wire, highlight the whole logical net): computed on
  demand by grouping components by name. Fast enough for interactive use.
- **Netlist export** (HDL generation): batch operation, computed once.
- **DRC** (multiple drivers, floating nets, etc.): batch operation.
- **Real-time editing**: almost always uses physical connectivity (which
  segments and vertices are wired together). The graph answers this directly.

### Conflict detection

If the user assigns different names to two components and then connects them
with a segment, the resulting physical component has two names. This is a DRC
warning, not something the graph resolves automatically.

## Operations That Affect Connectivity

- **Place segment** (`addSegment`): get/create vertices at endpoints, create
  segment, add edge to graph, tidy.
- **Delete items**: remove segments and vertices, remove edges/nodes from graph.
  Check for net splits via `nx.has_path`.
- **Move items**: moving a port moves its entry; if an entry lands on or leaves
  a vertex, edges are added/removed in the graph.
- **Paste / duplicate**: items are added one at a time in a specific order so
  that connectivity can be resolved incrementally:
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
     existing vertices encountered, and update the graph accordingly.

## Undo/Redo Strategy

All connectivity mutations go through `QUndoCommand` subclasses grouped in
macros. Commands are atomic and deterministic. API methods contain the
conditional logic and dispatch commands within macros.

### Commands

Each command handles both graphics and graph updates. There is no conditional
logic in commands -- they are atomic and deterministic. The graph edge lifecycle
is tied to the segment lifecycle; they are the same operation.

- **`CmdAddVertex`** / **`CmdRemoveVertex`**: add/remove the `VertexItem` in
  the scene and add/remove the node in `_graph`.
- **`CmdAddSegment`**: creates a `SegmentItem`, sets its vertices, adds it to
  the scene, and adds the graph edge with the segment as data. Undo reverses
  all of it.

  ```python
  def redo(self):
      self._seg.setVtx1(self._vtx1)
      self._seg.setVtx2(self._vtx2)
      self._scene.addItem(self._seg)
      self._scene._graph.add_edge(self._vtx1, self._vtx2, segment=self._seg)

  def undo(self):
      self._scene._graph.remove_edge(self._vtx1, self._vtx2)
      self._seg.setVtx1(None)
      self._seg.setVtx2(None)
      self._scene.removeItem(self._seg)
  ```

- **`CmdRemoveSegment`**: the reverse of `CmdAddSegment`.
- **`CmdSplitSegment`**: removes one graph edge, adds two graph edges (with
  their respective segments), and splits the graphics segment.
- **`CmdUnsplitSegment`**: removes two graph edges, adds one graph edge (with
  the surviving segment), removes the redundant vertex node, and merges the
  graphics segments.
- **`CmdReattachSegment`**: updates graph edges and segment vertex references
  together.

No separate netlist commands. No `CmdMergeNets` or `CmdSplitNets`. Merging and
splitting are emergent from adding/removing edges. The invariant "graph edge
exists iff segment exists" is enforced by construction.

### API methods (orchestrators)

API methods (`addVertex`, `addSegment`, `unsplitSegment`, etc.) do spatial
queries, make decisions, and dispatch the appropriate sequence of commands
inside a macro. The macro makes the whole operation atomic for undo/redo.

## Serialization

Vertices have no persistent IDs. Transient `dict[int, VertexItem]` mappings
are built on the fly during save and load, and discarded afterwards.

### Save (toXml)

Enumerate all graph nodes and assign sequential integer IDs:

```python
vtx_to_id: dict[VertexItem, int] = {}
for i, vtx in enumerate(self._graph.nodes):
    vtx_to_id[vtx] = i
    # write <Vertex Id="i" X="..." Y="..."/>
```

Then iterate connected components. For each component, write a `<Net>` element
whose edges reference the transient IDs:

```python
for component in nx.connected_components(self._graph):
    subgraph = self._graph.subgraph(component)
    pairs = [f"{vtx_to_id[v1]},{vtx_to_id[v2]}"
             for v1, v2 in subgraph.edges()]
    # write <Net Edges="0,1 2,3 ..." Name="CLK"/>
```

Segments do not need independent serialization -- they are fully determined by
their endpoint vertices (which define position) and the graph edges (which
define connectivity). On load, segments are recreated from the graph edges.

### Load (fromXml)

Build the reverse mapping as vertices are deserialized:

```python
id_to_vtx: dict[int, VertexItem] = {}
# for each <Vertex> element:
vtx = VertexItem(pos)
id_to_vtx[vid] = vtx
self.addItem(vtx)
self._graph.add_node(vtx)
```

Then for each `<Net>` element, create segments and add edges to `_graph`:

```python
for pair in edges_str.split(" "):
    id1, id2 = pair.split(",")
    vtx1, vtx2 = id_to_vtx[int(id1)], id_to_vtx[int(id2)]
    seg = SegmentItem(vtx1, vtx2)
    self.addItem(seg)
    self._graph.add_edge(vtx1, vtx2, segment=seg)
```

Both dicts are local variables; nothing persists after serialization completes.

## Diagnostics

A `validateConnectivity()` method can verify graphics/netlist consistency:

- Every segment's vtx1/vtx2 has a corresponding edge in the graph.
- Every edge in the graph has a `segment` attribute referencing a `SegmentItem`.
- The edge's `segment` attribute matches the edge's endpoint nodes (i.e.
  `seg.vtx1()` and `seg.vtx2()` are the edge's nodes).
- Every `VertexItem` in the scene is a node in the graph.
- Every node in the graph is a `VertexItem` in the scene.
- `_graph.degree(vtx)` agrees with the vertex's visual connection state.

This is called after each macro during development (behind a debug flag).

## What Changes vs Current Approach

### Removed

- `Net` class (no runtime net objects)
- `NetEdge` named tuple
- `_nets: dict[int, Net]`
- `_node_net: dict[int, int]`
- `_nodes: dict[int, VertexItem]`
- `_id_net: Counter`
- `_id_vtx: Counter` (IDs assigned transiently during serialization instead)
- `VertexItem._id` (no persistent vertex ID)
- `VertexItem._connections: list[SegmentItem]` (replaced by graph adjacency)
- `VertexItem.attach()` / `VertexItem.detach()` (replaced by graph edge ops)
- `mergeNetEdgeNode`, `unSplitNetEdge` and related scene methods
- `CmdSplitNetEdge`, `CmdUnsplitNetEdge` and all separate netlist commands

### Added

- `networkx` dependency (pure Python, no numpy required for core operations)
- `_graph: nx.Graph` on scene
- Graph operations integrated into existing commands (`CmdAddSegment`, etc.)

### Unchanged

- All graphics items (`VertexItem`, `EntryItem`, `SegmentItem`)
- API method structure (macros of atomic commands)
- XML format (compatible)

## Implementation Plan

1. ~~Add `networkx` dependency.~~ **done**
2. ~~Add `_graph: nx.Graph` to `DrawingSceneConnMixin.initConn()`.~~ **done**
3. ~~Integrate graph operations into existing commands.~~ **done** --
   `CmdAddVertex`, `CmdRemoveVertex`, `CmdAddSegment`, `CmdRemoveSegment`,
   `CmdSplitSegment`, `CmdUnsplitSegment` all updated. `CmdReattachSegment`
   removed. Remaining: clean up stale references in `api/conn.py`
   (`CmdReattachSegment` import, `CmdSplitNetEdge`, `CmdUnsplitNetEdge`,
   `vtx.netId()`, `v1.id()`).
4. Remove `VertexItem._connections`, `attach()`, `detach()`. Replace
   connection count with `_graph.degree(vtx)`. Update `onScenePositionChange`
   and `onConnectionChange` in `vertex.py`. Remove `attach`/`detach` calls
   from `segment.py` `setVtx1`/`setVtx2`.
5. Remove `Net` class, `NetEdge`, old netlist commands, old scene dicts.
   Partially done (imports cleaned from `cmd/conn.py`). Still referenced in
   `api/conn.py`.
6. Remove `VertexItem._id`, `VertexItem.id()`, and `_id_vtx: Counter`.
   Update `CmdAddVertex` to not assign an ID. Serialization uses transient
   dicts only.
7. Update `toXml` / `fromXml` to use `nx.connected_components` on save and
   `_graph.add_edge` on load, with transient ID mappings.
8. Implement `validateConnectivity()` diagnostic.
9. Handle net properties (name) via node attributes and `NetLabelItem`.
