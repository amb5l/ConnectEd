1) move back to widgets/graphics

Properties apply to scenes and items.

2) class Property

Property object


- single item:
  - column headings = name, type (kind), value, display, cleat, ...
  - row heading = property name

- multiple items:
  - tab per item type e.g. block, symbol, rectangle, line ...
  - each tab shows a table
  - mode: attribute
    - column headings = property name
    - row headings = item ID (UUID for name, simpler ID system later)
    - cell contents depends on "Attribute" combo:
      - value, type (kind), display, cleat...
  - mode: property
    - column headings = same as for single item case (all attributes of a property
    - row heading = item ID
    - cell contents depends on "Property" combo (property name)


- editing properties of single item
  - 2 tabs: "properties" and "property texts"
  - each tabs shows a table
  - properties table:
    - rows = property names
    - columns = kind, value
  - property texts table:
    - read only columns for property name, kind, value
  - dialog has pushbuttons for add and delete; applies to current tab

- PROPERTY FILTER!!!

- editing properties of multiple items
  - tab per item type e.g. block, symbol, rectangle, line ...
  - each tab shows a table
  - row headings are item UUID (later will switch to simpler ID system)
  - table has 3 modes: value, type (kind) and text
    - value mode: column headings = property
    - column per prp
    - value shows values with type and number of texts in tooltips
    - type shows kind with value and number of texts in tooltips
    - text shows property texts with read only columns for name, type, value
  - row = item ID (UUID until Drawing Unique ID is implemented)
  - column = property name
  - tables may be transposed
  - dialog controls apply to current tab and are remembered:
    - combo or radio buttons for kind and value (which is shown)
    - pushbuttons for add and delete

- dialog buttons:
  - OK, Cancel
  - Add, Delete (property or text depending on table display mode)
  - Transpose

- display hints: (accessibility)
  - text:
    - italic = read only e.g. inherent property name
    - bold = new or modified
    - strikethrough = deleted
  - background:
    - green = new
    - yellow = modified
    - red = deleted
    - diagonal hatching = non-existent
