# Property and Property Text Editing UX

We need the following to be slick:

- edit properties of one or more items; edit values, add/delete properties
- add a property text (and optionally a property) to one or more items
- hide (make invisible) one or more property texts
- edit appearance / unhide one or more property texts
- add a named property to one or more items of the same type

## Properties

The properties system exposes scene and item parameters for persistance (serialisation) and editing UI purposes, and allows these parameters, and user created values, to be displayed on the diagram.

### Editing

- Right click single property owner item and choose "Properties..." from context menu. PropertiesDialog will show - no tabs, list view only.
- Select multiple property owner items and choose "Properties..." from context menu. PropertiesDialog will show - tab per item type if more than one; list view on each; grid view available if tab shows more than one item.
- Double click a PropertyTextItem or right click and choose "Edit..." from the context menu. Shows the PropertyTextItem dialog which allows both property and property text editing.

### Adding

PropertiesDialog includes "Add"/"New" button. Creates new uncommitted row.

### Deleting

PropertiesDialog includes "Delete"/"Remove" button (active when property row selected in list view, or cell/column selected in grid view.)

## Property Texts

Property texts are bound to properties by name, retrieving and displaying the corresponding value. They subscribe to value changes to remain in sync.

A property may have zero, one or many property texts.

### Adding

Any of the following:

- Right click a single property owner item and choose "Property Texts > Add..." from its context menu; PropertyTextDialog will show with "cleat" containing a default handle.

- Select a property owner to show its grips; right click a handle and choose "Property Texts > Add..." or "Add Property Text..." (the latter will show if no existing property texts are anchored to the handle). PropertyTextDialog will show (title "Add PropertyText (1 Item)") with "cleat" containing the chosen handle.

- Select one or more property owner items. If there is at lease one property name in common across the set of items, the context menu will allow addition of property texts; if there are existing property texts, the menu will allow both editing and adding, otherwise only adding. Choose the relevant context menu action and PropertyTextDialog will show, titled "Add Property Text (N Items)". If items share a handle set, the cleat combo will show it, defaulting to the first. Otherwise cleat will show asterisk (read only) to indicate "various". Note a new Name may be specified in which case Kind will support string or text (new custom property). Value will show asterisk (various) or a common value.

- In the PropertiesDialog grid view, select a one or more items under a single property heading and choose "Add Property Text...". This will show the PropertyTextDialog (title "Add Property Text (N Items)"); this will prefill the property name combo.

### Editing (including unhiding)

Any of the following:

- Double click a PropertyTextItem or right click and choose "Edit..." from the context menu. Shows PropertyTextItemDialog which allows both property and property text editing.

- Right click single property owner item and choose "Property Texts..." from context menu (not shown for PropertyTextItem). PropertyTextItemsDialog will show.

- Select one or more property owner items, choose "Property Texts > Edit..." from context menu (available only if 1 or more PTs exist). This will show either the PropertyTextDialog for 1 PT or PropertyTextItemsDialog for 2..N PTs.

- In the PropertiesDialog grid view, select a one or more items under a single property heading and choose "Property Texts > Edit..." (not available if no PTs). This will show either the PropertyTextDialog for 1 PT or PropertyTextItemsDialog for 2..N PTs.

- In the PropertiesDialog list view, select a single property and choose "Property Texts > Edit..." (not available if no PTs).

### Hiding (making invisible)
- select one or more PropertyTextItems (no other item types) then choose "Hide" from the context menu

### Deleting
- select one or more PropertyTextItems (and other item types if desired)
- either
  - press "Delete"
  - choose "Delete" from the Edit menu
  - choose "Delete" from the context menu

# Widgets

PropertyDialog
  - new property details (name, kind, value r/w if applicable)#
  - used for new and existing

PropertyTextItemDialog
  - property details (name combo, kind r/o, value r/w if applicable)
  - text appearance controls

PropertiesDialog
  - main widget = PropertiesItemTypeWidget or PropertiesItemTypeTabWidget
  - ok cancel layout

- PropertiesItemTypeTabWidget
  - QTabWidget subclass with no overrides at this time
  - intended to contain 2..N PropertiesItemTypeWidget tabs

- PropertiesItemTypeWidget
  - main widget is either...
    - PropertiesGridWidget
    - PropertiesBushWidget
    - PropertiesTreeWidget
    - PropertiesListWidget
  - control layout at bottom:
    - bush/tree/list/grid radio buttons
    - view specific controls
      - bush
        - show texts checkbox (default checked)
        - add property: adds to all or selected item
        - remove property: applies to selected item/property
        - 2D selection allowed over text fields if shown else over property fields; single cell or row otherwise
      - tree
        - show texts checkbox (default checked)
        - add property button: adds to all or selected item
        - remove property button: applies to selected item/property
        - 2D selection allowed over text fields if shown else over property fields; single cell or row otherwise
      - list: show texts
        - show texts checkbox (default checked)
          - property fields are read only if texts are shown, but underlying property may be edited via a form dialog by double-clicking them
        - add property button: adds to all or selected item
        - remove property button: applies to selected item/property
      - grid
        - add button - adds property to selected item or all (pops up form dialog)
        - remove button - removes property (selected cell or column)
        - rename - renames property (selected cell or column)
        - full 2D selection allowed
    - property Add/Remove buttons (follow active widget)
    - Filter button to enable property name filtering

PropertiesGridWidget
  - item per row
  - columns = (filtered) property names (union across all items)
    - inherent property names are italicised
  - cell = property value

PropertiesBushWidget
  - condensed tree (see below) with cells from the first child moved up to the parent so there are no empty rows

PropertiesTreeWidget
  - first level rows = items
  - second level rows = properties
  - third level rows = property texts

PropertiesListWidget
  - property per row
  - columns:
    - item ID (may be repeated; multiple properties per item)
    - property name (editable for custom)
    - property kind (editable for custom)
    - property value



# Misc

Polyline needs some work to expose its chain of segments as a property. Probably a semicolon separated list (x,y) and/or (x,y,arc). Does anything else? Such cases stand out because they need custom toXml/fromXml.
