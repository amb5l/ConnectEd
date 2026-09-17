# PropertiesDialog Plan

## Widget Hierarchy

- PropertiesDialog : QDialog
  - title...
    - single item: "(Item Type) Properties"
    - multi item, all same type: "(Item Type) Properties (N items)"
    - multi item, multi type: "Properties (N items)"
  - _layout : QVBoxLayout
    - _main_widget : PropertiesPerspectiveWidget | TabWidget
      - PropertiesPerspectiveWidget or TabWidget with PropertiesPerspectiveWidget tabs
      - tab per item type
    - _ok_cancel_layout : OkCancelLayout

- PropertiesPerspectiveWidget
  - _unsliced_widget: PropertiesUnslicedWidget
  - _sliced_widget: PropertiesSlicedWidget (disabled for single item)
  - _layout : QVBoxLayout
    - main widget is determined by _perspective_combo below
    - _control_layout
      - _perspective_combo: Unsliced or Sliced (determines active widget)
        - disabled for single item
      - _slice_combo: list of all property fields (kind/value/display...)
        - visible when _sliced_widget is active
      - _transpose_checkbox
      - stretch
      - _filter_button => PropertiesFilterDialog, filtering choices apply to both _unsliced_widget and _sliced_widget
      - references to UI elements passed to main widget instances

- PropertiesUnslicedWidget(TableView)
  - rows = unique item/property combinations (item may appear on multiple rows)
  - columns = property fields
    - item group: ID, type (hidden for single item)
    - property group: name, custom, kind, value, visible...
    - column heading context menu allows column hide/unhide, sort
  - cells show property field values
  - take over _transpose_checkbox when shown

- PropertiesSlicedWidget(TableView)
  - rows = items
  - columns = property names
    - column heading context menu allows column hide/unhide, sort, also supports PropertyColumnsDialog to control show/hide and ordering
  - cells show field chosen by _slice_combo (reference passed into ctor)
  - cell hover tip shows ALL fields
  - take over _transpose_checkbox when shown

- PropertiesFilterDialog
  - supports filtering of property names only
