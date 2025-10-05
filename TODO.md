- MRU
- getTheme
- support defaults in PortPinText
- background netlist extraction
- check interactions that don't change anything don't push a cmd
- tackle onGeometryChange usage
- rotate ports during placement

- propagate property name change to texts
- property change propagation
- override setRotation to maintain ortho angles
- review OnPositionChange
- move hub import to top everywhere
- sort out editAppearance, editProperties in view/scene/cmd
- scene:
  editText, editPropertyText, editProperties, editAppearance

- what about moving PropertyTexts when their parents are or are not selected?
- settings propagation
- selection state propagation parent => child
- setters and getters, properties vs not, use of get prefix for getters
- assign origin is not undoable
- should KeyPoint be a QPointF subclass?
- ratsnest
- common menus for elements


appearance
  settings - default appearance
  direct appearance edit

text change
size change

position change


Cloning blocks leaves out pins
Move to BaseText for pin/port name
Port and other element rotation

Change
  pin = BlockPin(
to
  pin = scene.placeBlockPin
GroupElementMixin?
XML for block pins, ports?

Selection Behaviour
===================
- child elements e.g. property texts? sequential/incremental selection?
- add tolerance to all

Pins
===========
- clipping of BlockPinIndicator - will be fixed by tolerance (see above)

Properties System
=================
- after transpose, header sorting arrow is stale
- apply button with underlying command
- QUndoCommand based editing with local undo stack
- revert/revert all/cut/copy/paste
- context menu testing
- signal from cmdElement(s) -> PropertiesTabWidget to update all models
  in the event of drawing changes
- missing spreadsheet delegates
  - color

General
=======
- prepareGeometryChange throughout?
- separate state machines for diagram and symbol views, inheriting from drawing
- localisation (language translation)
- better window menu - submenu per design, with tile action?
- setter and getter names (esp getter)
- use of 'instance' as argument/variable name
- family -> font
- export to SVG, use diffsvg to compare with known good for regression testing

- review setPos/pos - use _local_pos to simplify/speed up pos()
- review itemChange to connect to KeyPointManager change signal

- use pyTooling - class variable type hints

- improve context menu handling for single vs multiple elements;
  consider adding title; handle properties and appearance automatically?

- view prev/next

Define a View State Class:
Create a DrawingViewState class to store zoom, h_scroll, and v_scroll.
Add this to DrawingView’s private classes in .\ConnectEd\widgets\drawing\views\drawing\__init__.py.

Add a Navigation Stack to DrawingView:
Add a view_history list and view_history_index to DrawingView.

Initialize them in DrawingView.__init__.
Implement methods to push a new state, navigate backward, and navigate forward.

Capture View State Changes:
Modify zoom and pan methods (_zoomAbs, _pan, etc.) to push new states after changes.
Avoid pushing states during transient operations (e.g., dragging in EditPaste or PlaceRectangle2).

Implement viewPrevious and viewNext:
Update viewPrevious and viewNext in DrawingViewViewMixin to navigate the stack and apply the corresponding state.
Update action enablement (viewPrevious, viewNext) based on the stack index.

Integrate with Actions:
Ensure the Actions class updates viewPrevious and viewNext enablement dynamically.
Connect the stack’s state changes to action enablement in DrawingView.





- fix diagram paper_size

- save explorer text zoom in settings
- asterisk for unsaved diagrams and libraries
- different color for top level containers
- explorer container <empty> status
- extend scripting test
- convert drawing scene to module, move commands into scene

- switch from design to diagram
- add settings to explorer (light, dark) ???
- save display preferences with diagram
- appearance: force system default, apply system or diagram default

- rich text v simple text
- cache settings in elements - new pen/brush/font management
- merge XML attributes and properties
- Add ElementWithGrips, ElementWithAnchor
- review QPointF vs x,y
- moveKeyPoint -> dx, dy
- move keypoint into parent
- text anchor editing
- grip shapes, context menu
- multi select context menu
- Mouse left button released when idle
- consolidate mouse event handling
- Liberation fonts: serif spacing
- remove unused methods
- sort out WIP
- explorer: multi item copy/paste
  - new design/library option in free space
  - expand on paste (e.g. to symbol cache)
- symbol editor scroll bars / extents
- get rid of raise errors, use logger
- improve paste destination tolerance in explorer
  - allow paste of designs, libraries when clicking in free space
  - allow paste of diagrams into designs
- explorer: modified indicator, full path tooltip
- autosave
- Window menu: check active window
- new widgets:
  - Add Symbol Explorer
- filter log view by level
- look at windowFilePath
- move some context menu logic into TreeView
- tidy up MDI subwindow top right button icons
- apply default path to new databases

