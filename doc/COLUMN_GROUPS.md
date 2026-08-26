---
name: Table column groups
overview: Two-band horizontal headers on TableView — group labels from TableModel, painted and clickable in TableHeaderView. Empty groups keep today’s single header.
todos:
  - id: model-api
    content: TableModel stores per-column group names; clear groups on setHorizontalHeaderLabels
    status: completed
  - id: header-paint
    content: TableHeaderView — extra height, paint group band + leaf labels, hit-test group vs leaf
    status: completed
  - id: header-click
    content: Click group band selects that span’s columns without changing default cell selection mode
    status: completed
  - id: view-wire
    content: TableView installs TableHeaderView; reads groups from TableModel; no-op when groups is None/empty
    status: completed
  - id: properties-dialog
    content: PropertiesDialog uses TableModel + group labels (Property / Text)
    status: completed
isProject: false
---

# Table column groups

Optional second header band: **group** titles over contiguous leaf columns. Model owns per-column names; header paints runs and handles clicks. No extra model rows or columns. No span type — the header walks `horizontalHeaderGroupLabels()`.

## Design

```text
TableModel          metadata: leaf labels + optional per-column group names
       │
TableView           installs TableHeaderView; does not store groups
       │
TableHeaderView     paints two bands when groups present; click group → select span
```

- **No groups** (`_hgroups is None` or all blank): one header row, current look.
- **Groups**: taller header. Top band = group name over a run of equal names; bottom = leaf (`Name`, `Type`, …).
- Data `rowCount()` / `column()` unchanged.

### Model API

```text
setHorizontalHeaderLabels(labels)
  → leaf headers; _hgroups = None

setHorizontalHeaderGroupLabels([(group, leaf), ...])
  → one pair per column; length must match columnCount()
  → consecutive equal group names form one painted/clickable span

horizontalHeaderGroupLabels() -> list[str] | None
```

Rules:

- `None` / omitted groups → no group band.
- Empty string group name → ungrouped leaf (blank span, no click target).
- Adjacent same name → one span (not three “Property” cells conceptually).
- Do not put group titles in `headerData(DisplayRole)` for leaf columns.

Validate in debug/log if `len(pairs) != columnCount()`.

### Header (`TableHeaderView`)

`QHeaderView` has one section per **leaf** column. Extra height = group band + leaf band.

| Concern | Approach |
|---------|----------|
| Height | `sizeHint` includes group-band height when model has groups |
| Paint | `paintSection`: leaf text in lower half; group text once per span (clip to span’s x-range) |
| Resize | Group underline / vertical ticks at span boundaries |
| Click | `mousePressEvent`: y in group band → select columns `[start, start+count)`; y in leaf band → default section behaviour |
| Selection | Select those **columns’ cells** via the view’s `selectionModel`. Do **not** switch the view to `SelectColumns` permanently |
| Sections movable | Leave **off** while spans are name-run based |

### View (`TableView`)

- Require `TableModel` (same module).
- `setHorizontalHeader(TableHeaderView(Qt.Horizontal, self))`.
- Header reads groups from `model()` on paint / model-reset.

### First consumer — PropertiesDialog

```text
Property × 3   Name, Type, Value
Text     × n   Display + remaining _PT_COLS
```

Click **Property** → select Name/Type/Value; click **Text** → select display + PT columns.

## Out of scope

- Nested groups (only one group band).
- Vertical (row) groups.
- Spreadsheet / library `QTableView` (not `TableView`).
- Putting group names in data rows.
