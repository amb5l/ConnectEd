Let's consider opening PropertiesDialog with a set of items that includes connections (segments and nodes).

But neither SegmentItem nor NodeItem has properties.

The scene builds subnets and nets from its segment and node population, and these have property analogs e.g name, suffix.  Later a type property may be added.

The idea is that the appearance of a segment is determined by the properties of its subnet/net. Vector/bus = thick, scalar/wire = narrow.

Should we align net properties with the main property system? I think not. Nets get properties from connected objects (e.g. port name => net name, tap => suffix), and net labels (which can impart a name, type).

I propose that segments are excluded from PropertiesDialog, and nets/subnets are included (using a bush to present their hierarchical relationship) but are read-only.

Consider the alternatives - including property system support for SegmentItem.

Advice please.