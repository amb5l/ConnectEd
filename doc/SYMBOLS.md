Up to now, the idea for symbols has been to have...
- definition (boundary, pins and graphics) as items in a SymbolScene
- instances built on-demand from the scene content
- scene editing similar to diagrams

I propose a change.
- symbol definition and diagram instances are both items
- structure is: empty rectangle; border visible during symbol editing but otherwise invisible; pins are children and are located on border (EdgeLoc); graphics are children and must be within border
- definition is a master instance held in the symbols cache of a diagram
- diagram instances are clones of this

The challenge is propagating changes from the master to its clones as a result of the user editing it, or even replacing it with a different version from (e.g.) a library. If clones have a back reference to the named entry in the symbols cache, and the master has forward entries, we should be able to manage this.

Symbols will still be stored in libraries - containers (lists) of symbols and not much else apart from metadata for the corresponding HDL library.

This implies SymbolScene will be transient - created on demand for symbol editingonly. It could and perhaps should be a special purpose subclass of DiagramScene.

NOTE: edits/replacements of symbols need to be followed by connectivity refresh

Symbol serialisation:
When a whole diagram or part of it is serialised, any symbols must be serialised as definitions in a separate block. Note that pasting may cause collisions between pasted symbol definitions and pre-existing ones.

So although SymbolItem needs a toXml method this will be called during symbol definition serialisation only.