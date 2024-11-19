KEY

Shows colours, widths, line styles for wires and how they correspond to
wire types (c.w. VHDL types).


CONSTANT (Verilog parameter)



SYMBOL

The basic unit of a diagram. Can correspond to...
    child diagram
    HDL module e.g VHDL entity or component (interface can be checked)
    black box e.g. electronic component or FPGA vendor primitive
    HDL function - library or user defined
        one or more inputs, one output
        consider scalar and vector inputs and outputs




A symbol can contain
    pins
    decorations (graphics and text)
    attributes



PIN
A pin comprises
    external line (zero, short or long)
    attributes
        name
        number
        type


FUNCTION

Gates etc. For example, an AND gate can have an arbitrary number of inputs.
Inputs and the output may be active high or low. The translator receives the
name of the function, and a list of pins and connected wires. The translator can
signal its support (or lack of) so that the availability of the function can be
constrained when editing.

Configurations:|
    2-N scalars -> scalar
    scalar + vector -> scalar
    1-N scalars + vector -> scalar
    2-N vectors -> vectors

Think about vector inputs. A single one should result in a function of the
constituent scalars, with a scalar output. Multiple vector inputs should
result in a vector output. Mismatching vector widths on the input will result
in an error.


For VHDL, an AND gate might result in a concurrent signal assignment.


CONTEXTUAL ACTIONS

GUI actions (menu items, toolbar buttons, shortcut keys) can be
- permanently enabled e.g. File Open
- enabled depending on the diagram state
    - diagram existence (does one always exist? can multiples exist?)
    - item(s) selected, and their types
        - e.g block selected enables pin placement?

Diagram essentials are edited through menu actions. They can be selected and
their properties edited via the GUI also. E.g. the key, title block.

Diagram items need editing attributes
    - can be moved (everything?)
    - can be slid (blocks, wires)
    - can be rotated (everything ex title block?)

DIAGRAM PROPERTIES FOR VHDL
VHDL file path/name
entity name
architecture name

VHDL diagram types
entity/architecture
entity

CODE BLOCKS FOR VHDL
    function
    procedure
    diagram is parent:
        entity.library/package
        entity.generics
        entity.declarative
        architecture.library/package
        architecture.declarative.head e.g. constants
        architecture.declarative.tail e.g. attributes
        architecture.body.head (+ order number)
        architecture.body.tail
    block is parent:
        instance prefix
        instance suffix
        architecture declarative head or tail e.g. attributes

Wires

Wires are used to interconnect ports and the pins of blocks and symbols.
They can be scalar or vectors. Multidimensional vectors are supported.

Taps

A tap breaks out a specified range, which is displayed next to the tap symbol.

Name

Range
    A range indicates the range of a vector wire e.g. 1:2 or 7:0

ATTRIBUTES



WIRE ALIASES
A wire alias allows a wire to referred to by a different name (and range).
It causes a VHDL alias statement to be added to the architecture declarative region.
The alias type is derived from the wire.

BUFFER



WIRE PROPERTIES FOR VHDL
    name
    range
    type (relates to appearance, key) e.g. std_logic

BLOCK PROPERTIES FOR VHDL
type
    component with declaration
    component without declaration
    entity (e.g. work.myentity)

code relationship:
    generate
    compare
    none (not recommended)
primitive: yes or no
    you can't descend into a primitive, and no code will be generated from it
instance name = reference
generic map
for components: include declaration yes/no



Zoom Window

"Situation"
    - mouse state: idle, press,
    - edit mode: add xxx,
    - canvas state

Canvas mouse mode: click1 or click2
Depending on the situation, edits require
- a single point e.g. select item, place text
- a pair of points e.g. select by rectangle, place circle
- a series of single points e.g. polyline
A pair of points may be designated by either of
- a pair of clicks
- click - drag - release
We need to handle pairs of points designated by a drag in operations that require a series of single points.
So mouse handling needs to be oriented towards 1, 2 or N clicks.


For 2 or N clicks, there is a "work in progress" phase between clicks.
During this time the diagram object is gestating.
Mouse event handling => click events

We need a general mechanism for enabling and disabling actions. For example, cut and copy are disabled when no items are selected. Mirror is disabled when text items are selected.

We need to implement clipboard support. Do we need to serialize/unserialise diagram objects?

PDF support needed.

QTreeView to view prefs hierarchically. Double click on one to edit it?

Review shortcuts after adding Menu shortcuts e.g. ALT-F for File

Macro support?

Canvas flux situations:
- selection window
- zoom window
- draw new diagram item - block, wire etc
- resize item(s)
- select or move item(s)
- paste or ctrl-drag duplicate item(s)


press release
press move release

Clipboard
QByteArray -> QMimeData


A **click** is a press then release without moving the pointer - a small amount of movement is tolerated, but beyond this the operation will become a **drag**.
(The tolerance is specified by prefs().edit.drag.min)


wheel up   - zoom in
wheel down - zoom out
wheel click  - zoom full


left click -



VHDL specifics

A block can represent a component instance or an entity instance. It should
have a

A symbol can represent