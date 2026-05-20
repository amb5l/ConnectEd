moveHandle : test with all pin types
implement net labels
test pin wire/bus width

app/local settings e.g. select color, grid color
scene settings, corresponding to scene resources => save/load XML

YAML setting defaults
updatePath mixin?
get rid of None direction?
(re)move RectItemHandleMixin etc
place port, drag name by handle => bug
pen mixin

more shared line/fill
  pins, ports
  _sel_line gone

onPathChange

pin width controlled by suffix
gate mirroring
add signal types to netlist, derived from ports and pins

unresolved/scalar/vector resolution for segments, taps

PlaceBaseInteraction._ITEM_TYPE => generic?
remove item suffix
get TapItem working
onGeometryChange review
DrawingViewUi review - diagram separation
use ItemTransformMixin for BlockItem - test mirroring, pin movement
USE MIRRORING FOR BLOCK PINS so anchored property positions stay sensible


use ItemTransformMixin everywhere
general purpose tether (for use with PropertyLabelItem)

# Completing Netlist Support

Netlist support is WIP.


Let's consider movement (not sliding which will stretch connections).
The interaction needs to clean up the selection set, removing parented items
to leave "primary" items (which may have children). The clean selection set may
include vertices and segments.

In preparation for the movement preview - the part of the interaction before
it is committed - segments will need to be detached from the vertices of
segments that are not part of the selection set, and from the entries of items that are
not part of the selection set.

(Special case: zero length segment connecting colocated entries. These will be
deleted. They are created/deleted as required as entries land on top of each
other or are separated.)

The interaction can then freely move the set of primary items around the scene
while the user decides where to drop them.

If the user cancels the interaction, any detachments need to be reversed.
I could implement symmetrical detach/attach methods but these are quite complex
operations and ensuring symmetry may be tricky. Or should I consider an
undo stack local to the interaction?

If the user commits the interaction, the items will need to be dropped into the
scene at the new position. I propose special handling of items that affect
connectivity.
1) entries on items will be postprocessed to ensure they connect to existing
   entries, vertices and segments at the new position;
2) getNode will be used to ensure the existence of a node at all vertex
   positions;
3) Segments will be redrawn so that - at the new position - vertices are
   created, entries are connected to, etc.

Consider and advise.











Consider a diagram with two disjointed connections. One is connected to a port
named "A" so is part of the "A" net. The other is connected to pins only so
has no net.

The user places an "A" label on the other. The two connections should now
be merged into net "A". How do we do this?

We could search through ports and labels with the name "A" and then consider
their connected nets.

Or we could maintain a dict of "namers"...

_namers : dict[str : list[PortItem | PropertyLabelItem]]

...objects that impart a name to their connection. And then we can look at the
"A" entry and consider the connected nets of its list of objects.
















A label may be used to apply a name to a connection (it is parented to a
free vertex and one is created if needed.)

Name labels take 3 forms:
- name[left:right] - a vector called "name" with a range from left to right,
  the range direction (a VHDL concern) being automatic (could be specified by
  using a unicode down arrow or up arrow in place of the colon).
- name[n] - scalar net which is member "n" of parent vector "name"
- name - scalar net

Q: Use of variables in expressions in ranges - how do we decide what range to
   use in the HDL signal declaration? And how do we decide what the "resolved"
   range should be in the Net instance?
A: if a variable is used anywhere in a range for a vector, that vector must
   have a "Range" label somewhere and that will be used for the HDL declaration.





Important: range and index suffixes are not processed until HDL export.


A bus may be drawn using multiple disjointed connections. Each may have a name
label with a different range. The range used in the HDL declaration of the bus
signal is determined by taking the min and max values of the left and right
of the ranges (where simple numbers are used) or from a range label if the
range contains variable expressions.





- when a net experiences connectivity/labelling changes, a name and type
  resolution process must run; the results are cached in the net instance's name
  and datatype attributes and propagated to all segments to update their
  appearance
- let's call the scalar/vector distinction the net "structure"
- attempts to resolve structure may fail e.g. because of no entries/labels
  or because of conflicts
- so we need a single Net class that can support and transition between 3
  structures: scalar, vector and unresolved
- scalar members of a vector net that are drawn on the diagram must exist in
  the netlist (along with information about their vertices and segments) so that
  they can receive appearance updates
- for net name resolution, name labels take precedence over port names
- unnamed nets are named automatically (from their ID)
- conflicting name labels are a DRC error

Q: should a Net instance store both vertices and segments?


# Variable Names

We need to decide a sensible set of rules for variable names that will work
with VHDL, Verilog and SystemVerilog - and impose that in DRC. If future
export formats require different rules, we deal with those later.


# Literal Support

We need to decide on a "native" format for (HDL-agnostic) literals, supporting
various data types. Consider values like "Z", "X".


# Expressions

We will need to translate native (HDL-agnositic) expressions from native to
the desired export format e.g. VHDL or Verilog.

This will involve
- defining native operators (ideally allowing both Verilog and VHDL style)
  and translating these correctly
- translating native literals

TODO: define a set of operators


# Constant Support

- It should be possible to declare named constants at diagram level, for use
  in expressions.
- Constant declarations should include a name, type and value (an expression).
- For example, declare a one character named constant to shorted a long
  generic/parameter name for improved diagram density.


# Expressions as Sources

- It should be possible to apply a Value label containing an expression to a
  port or pin to create a corresponding HDL assignment.
- Applying Value labels to nets carries the risk of being confused with names.
  Either forbid this (require the use of a buffer to drive a net from a value)
  or force a "Value=X" display style on the label.

Q: what to do about Value labels on nets?


# Generic/Parameter Support

Need to add generic/parameter support to diagrams. Although I could support
graphical objects/connections, I think there should be clear UI distinction.

Proposal:

1) Diagram Level
Implement a list of Parameter instances, each specifying a name, type and
optional default value. Provide a dialog to allow the list to be edited.
Implement a graphical object to display this information in a compact table.

2) Blocks and Symbols
Provide a Parameters property of kind Parameters. Display parameter assignments
in bulleted list that can be positioned as the user desires - usually below
the block/symbol. Allow parameters that are unassigned (left at default values)
to be included/excluded from the list.


# Bus Taps

Bus taps are not required to establish connectivity. A user can draw a labelled
bus connection then apply a label corresponding to a bus member to another
connection.

It might seem sensible to consider them in DRC - to check that the tapped
net exists in the bus - but the use of expressions in ranges would make this
impossible.