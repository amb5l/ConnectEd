Thoughts about the desired netlist browser widget. Implications for connectivity
management (DiagramScene netlist manager).

Connectivity comprises graphics (nodes and segments) and netlist management
(graph, subnets and nets).

The netlist browser will be a QTreeView subclass that shows nets, subnets and
nodes. It will allow users to zoom to a selected item.

Connectivity changes are serialised. A complex paste operation that makes
multiple connectivity changes happens piece-wise - a node or segment at a time.
We need to consider the implications of this for our netlist browser. We
should batch up connectivity changes rather than refreshing the QTreeView
for each node or segment.

Connectivity changes happen as a result of UI interactions or calls to scene
methods e.g. paste. Scene methods are the gatekeepers of scene mutation - or
that's the intention. In these we should - perhaps - call start and end
methods to create and process the batch changes.

Or perhaps the browser model should be rebuilt from scratch after each
connectivity change rather than changed incrementally - until we run into
a performance problem with this approach.
