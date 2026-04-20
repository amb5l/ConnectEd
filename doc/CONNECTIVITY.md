Connectivity in ConnectEd


To export HDL from a scene it is necessary to extract a netlist, describing
connections between ports and pins. This could be done on demand, but
maintaining a live netlist during editing enables net highlighting and real time
DRC.

The DiagramScene class provides Netlist and Net classes, and methods for
editing nets.

A net has the following attributes:
- name
- type
- range

Net Resolution

Information about a net's name, type and (if a vector) its type can be gained
from...
- connected ports
- connected pins
- annotations


- build list of names
- check

1. Scalar or Vector
- 


Note that conflicting information needs to be highlighted to the user.