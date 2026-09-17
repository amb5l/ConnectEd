- align consecutive declarations and assignments vertically
  (plenty of examples in codebase)
- put type declarations of class and instance attributes at top of class decl

- PropertiesDialog
  - FilterDialog (see below) narrows items and properties
  - _main_widget is TabWidget containing multiple PropertiesPerspectiveWidget instances (if tabbed) or direct reference to single PropertiesPerspectiveWidget (if untabbed)
  - PropertiesTableWidget
    - radio button group selects perspective
    - property centric
      - optional table title (details of single item if applicable)
      - table
        - row = unique property
        - columns
          - item related (ID, type name) (hidden for single item)
          - property fields (kind, value, display...)
        - cell = value of property field
        - tip = none
    - item centric
      - row = unique item
      - columns = property names
      - cell = value of property field chosen by "Show" combo (kind, value...)
      - tip = values of all property fields for hovered item/property
      - show combo defaults to "Value"
  - filter button shows FilterDialog
  - tabify/untabify button available if more than one item type; separates
  - filter and sort recipe may be saved with a name e.g. "hdl"

  - PropertiesFilterDialog
    - _main_widget is either tab widget or direct reference to single XXXFilterWidget
      - ItemTypesFilterWidget
        - appears if more than one item type
        - list of type names with checkboxes, on left
        - buttons for select all / deselect all, on right
        - dialog OK suppressed if no type is selected
      - PropertiesFilterWidget
        - item set is filtered by ItemFilterWidget if it exists else ItemTypesFilterWidget if it exists; when tab is shown it checks to see if this has changed and updates as required e.g. removes items whose type is filtered out
        - appears if more than one property across item set i.e. almost always but let's allow for the edge case of single item with single property
        - displays shuttle of names (included <-> excluded)
        - dialog OK suppressed if no properties included
    - getItems returns filtered items
    - getPropertyNames returns filtered property names




- PropertyTableWidget
  - QVerticalLayout
    - single Table or tab widget
    - TableView on top of TableModel
    - QHorizontalLayout
      - checkbox: Transpose
    - unify/tabify (tab per item type) if more than one item type in set

- TreeTableWidget
  - top level rows = items
    - 2nd level rows = properties

- multi-item table 1 (item centric)
  - row = unique item
  - column = property name
  - cell = selected by "Show" combo
  - tip = not shown values e.g. kind for value, value for kind, custom...
  - show combo picks property attribute (kind, value, display...)
  - filter button for item types and property names
  - unify/tabify (tabs = item types) if more than one item type

- multi-item table 2 (property centric)
  - row = unique property (item may repeat)
  - column = all property attributes (custom, kind, value, name)
  - filter button for item types and property names
  - unify/tabify (tabs = item types) if more than one item type

- single item is property centric view with item columns hidden


- multi item, all one class
  - use TableWidget

- multi item, multi classes
  - property centric
    - columns = item ID, item type, custom, kind, display...




- single item
  - dialog title = "<item name> Properties"
  - single TableWidget (no tabs)
    - rows = property, columns = fields e.g. kind, value, display, visible...
    - single arrangement, single axes option (rows = property, cols = fields)
  - OK/Cancel buttons
  - no view control radio buttons



- multiple items dialog
  - if all items the same class
    - dialog title = "<item name> Properties (N items)"
  - else
    - dialog title = "Properties (N items)"

    - single TableWidget (no tabs)
      - rows = property
      - columns = item ID, name, kind, value, display, visible...
  - multiple classes
    - tab per class
      - tab name = class name minus "Item"
      - table per tab
    - radio buttons = Unified (no tabs), Separate (tab per item class)
      - disabled if all items are of the same class

