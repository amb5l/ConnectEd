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